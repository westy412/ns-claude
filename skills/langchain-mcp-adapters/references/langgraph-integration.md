# langchain-mcp-adapters -- LangGraph Integration Reference

## Using create_agent

The `create_agent` function (formerly `create_react_agent`) builds a prebuilt ReAct agent that can invoke MCP tools. It accepts a model identifier string and a list of tools loaded from MCP servers.

### Single Server with stdio

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["./math_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_agent("openai:gpt-4.1", tools)
            result = await agent.ainvoke(
                {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
            )
            print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### Multiple Servers with MultiServerMCPClient

`MultiServerMCPClient` manages connections to many MCP servers at once. Each server entry declares its transport type (`stdio`, `http`, or `sse`) and transport-specific parameters.

```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

async def main():
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["./math_server.py"],
                "transport": "stdio",
            },
            "weather": {
                "url": "http://localhost:8000/mcp",
                "transport": "http",
            },
        }
    )
    tools = await client.get_tools()
    agent = create_agent("openai:gpt-4.1", tools)

    math_result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
    )
    weather_result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
    )
    print(math_result)
    print(weather_result)

if __name__ == "__main__":
    asyncio.run(main())
```

### HTTP Transport with Authentication Headers

Pass `headers` for HTTP or SSE transports to include authentication tokens or custom headers on every request to that server.

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

client = MultiServerMCPClient(
    {
        "weather": {
            "transport": "http",
            "url": "http://localhost:8000/mcp",
            "headers": {
                "Authorization": "Bearer YOUR_TOKEN",
                "X-Custom-Header": "custom-value",
            },
        },
    }
)
tools = await client.get_tools()
agent = create_agent("openai:gpt-4.1", tools)
```

### Stateless vs Stateful Sessions

By default `MultiServerMCPClient` is stateless -- each tool invocation opens a new MCP `ClientSession`. When the server needs to maintain state across calls (for example, a scratchpad or a multi-step workflow), use the explicit session context manager and load tools within it:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent

client = MultiServerMCPClient(
    {
        "stateful_server": {
            "command": "python",
            "args": ["./stateful_server.py"],
            "transport": "stdio",
        },
    }
)

async with client.session("stateful_server") as session:
    tools = await load_mcp_tools(session)
    agent = create_agent("openai:gpt-4.1", tools)
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Run multi-step task"}]}
    )
```

## StateGraph with ToolNode

For full control over agent behavior, wire MCP tools into a LangGraph `StateGraph` manually. The `ToolNode` prebuilt node executes tool calls emitted by the model, and `tools_condition` routes to either the tool node or the end of the graph depending on whether the model requested a tool call.

```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

async def main():
    model = init_chat_model("openai:gpt-4.1")

    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["./math_server.py"],
                "transport": "stdio",
            },
            "weather": {
                "url": "http://localhost:8000/mcp",
                "transport": "http",
            },
        }
    )
    tools = await client.get_tools()

    def call_model(state: MessagesState):
        model_with_tools = model.bind_tools(tools)
        response = model_with_tools.invoke(state["messages"])
        return {"messages": response}

    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", tools_condition)
    builder.add_edge("tools", "call_model")

    graph = builder.compile()

    result = await graph.ainvoke(
        {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### Key components

- **`MessagesState`** -- Built-in state schema with a `messages` list. Sufficient for most chat agents.
- **`ToolNode(tools)`** -- Wraps the loaded MCP tools so the graph can execute them. Pass the same list returned by `client.get_tools()` or `load_mcp_tools(session)`.
- **`tools_condition`** -- Conditional edge function that checks whether the model's last message contains tool calls. Routes to the `"tools"` node if yes, otherwise routes to `END`.
- **`model.bind_tools(tools)`** -- Binds tool schemas to the model so it can produce properly formatted tool-call messages.

### Custom State and Additional Edges

You can extend `MessagesState` with extra fields and add more nodes for pre/post-processing, human-in-the-loop checks, or multi-agent handoffs:

```python
from typing import Annotated
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

class AgentState(MessagesState):
    task_status: str

def post_process(state: AgentState):
    last_msg = state["messages"][-1]
    return {"task_status": "done" if "DONE" in last_msg.content else "in_progress"}

builder = StateGraph(AgentState)
builder.add_node("call_model", call_model)
builder.add_node("tools", ToolNode(tools))
builder.add_node("post_process", post_process)

builder.add_edge(START, "call_model")
builder.add_conditional_edges("call_model", tools_condition)
builder.add_edge("tools", "call_model")
builder.add_edge("call_model", "post_process")  # after final answer
builder.add_edge("post_process", END)

graph = builder.compile()
```

## LangGraph API Server

To deploy an MCP-powered agent as a LangGraph API Server, define a graph factory function and reference it in `langgraph.json`.

### Graph Factory (graph.py)

The factory function is an async callable that returns a compiled graph or agent. The server calls it once at startup.

```python
# graph.py
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

async def make_graph():
    client = MultiServerMCPClient(
        {
            "weather": {
                "url": "http://localhost:8000/mcp",
                "transport": "http",
            },
            "math": {
                "command": "python",
                "args": ["./math_server.py"],
                "transport": "stdio",
            },
        }
    )
    tools = await client.get_tools()
    agent = create_agent("openai:gpt-4.1", tools)
    return agent
```

> **Note:** `stdio` transport spawns a subprocess, which works on user machines but may not be suitable for all server deployment environments. Prefer `http` (streamable HTTP) or `sse` transports when deploying to production servers.

### Configuration File (langgraph.json)

Place this file at the project root alongside `graph.py`. The `graphs` mapping points each named graph to a `module:callable` path.

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./graph.py:make_graph"
  }
}
```

- **`dependencies`** -- A list of paths or package references the server should install. `"."` installs the current directory as a package (expects a `pyproject.toml`).
- **`graphs`** -- A mapping of graph names to their factory functions. The format is `"<path>:<function_name>"`. The function must be async and return a compiled graph or agent.

### StateGraph Factory Variant

If you need a custom StateGraph instead of the prebuilt agent:

```python
# graph.py
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

async def make_graph():
    model = init_chat_model("openai:gpt-4.1")

    client = MultiServerMCPClient(
        {
            "weather": {
                "url": "http://localhost:8000/mcp",
                "transport": "http",
            },
        }
    )
    tools = await client.get_tools()

    def call_model(state: MessagesState):
        return {"messages": model.bind_tools(tools).invoke(state["messages"])}

    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", tools_condition)
    builder.add_edge("tools", "call_model")

    return builder.compile()
```

### Running the Server

```bash
pip install langgraph-cli
langgraph dev
```

This starts the LangGraph API Server locally, reading `langgraph.json` from the current directory. The agent is accessible at `http://localhost:8123`.

## Creating Custom Servers (FastMCP)

FastMCP provides a decorator-based API for creating MCP tool servers. These servers expose tools that `langchain-mcp-adapters` can load and use.

### Installation

```bash
pip install "mcp[cli]"
# or for the standalone FastMCP package:
pip install fastmcp
```

### Stdio Server

Stdio transport communicates over standard input/output. The client spawns the server as a subprocess. Best suited for local development and single-user scenarios.

```python
# math_server.py
from fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Connect from the client side:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "math": {
            "command": "python",
            "args": ["./math_server.py"],
            "transport": "stdio",
        },
    }
)
tools = await client.get_tools()
```

### HTTP (Streamable HTTP) Server

HTTP transport runs a persistent HTTP server. Supports multiple concurrent clients and is suitable for remote/production deployments.

```python
# weather_server.py
from fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get the current weather for a given location."""
    # Replace with a real weather API call
    return f"It's sunny in {location}"

@mcp.tool()
async def get_forecast(location: str, days: int = 3) -> str:
    """Get a weather forecast for a given location."""
    return f"{days}-day forecast for {location}: sunny, cloudy, rain"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")  # Default port 8000, path /mcp
```

Start the server, then connect:

```bash
python weather_server.py
```

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "weather": {
            "url": "http://localhost:8000/mcp",
            "transport": "http",
        },
    }
)
tools = await client.get_tools()
```

### Direct Streamable HTTP Client Connection

For low-level control without `MultiServerMCPClient`, use the streamable HTTP client directly:

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from langchain_mcp_adapters.tools import load_mcp_tools

async with streamablehttp_client("http://localhost:8000/mcp") as (read, write, _):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await load_mcp_tools(session)
        # Use tools with any agent or graph
```

### Server with Elicitation

Servers can request additional input from the client during tool execution using the elicitation protocol. This requires an `on_elicitation` callback on the client side.

```python
# profile_server.py
from pydantic import BaseModel
from mcp.server.fastmcp import Context, FastMCP

server = FastMCP("Profile")

class UserDetails(BaseModel):
    email: str
    age: int

@server.tool()
async def create_profile(name: str, ctx: Context) -> str:
    """Create a user profile, requesting details via elicitation."""
    result = await ctx.elicit(
        message=f"Please provide details for {name}'s profile:",
        schema=UserDetails,
    )
    if result.action == "accept" and result.data:
        return f"Created profile for {name}: email={result.data.email}, age={result.data.age}"
    if result.action == "decline":
        return f"User declined. Created minimal profile for {name}."
    return "Profile creation cancelled."

if __name__ == "__main__":
    server.run(transport="streamable-http")
```

Handle elicitation on the client side:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext
from mcp.shared.context import RequestContext
from mcp.types import ElicitRequestParams, ElicitResult

async def on_elicitation(
    mcp_context: RequestContext,
    params: ElicitRequestParams,
    context: CallbackContext,
) -> ElicitResult:
    """Respond to elicitation requests from the server."""
    return ElicitResult(
        action="accept",
        content={"email": "user@example.com", "age": 30},
    )

client = MultiServerMCPClient(
    {
        "profile": {
            "url": "http://localhost:8000/mcp",
            "transport": "http",
        },
    },
    callbacks=Callbacks(on_elicitation=on_elicitation),
)
tools = await client.get_tools()
```

## Complete Agent Examples

### End-to-End: Custom Server + create_agent

A self-contained example that creates a FastMCP server and an agent that uses it.

**Server (tools_server.py):**

```python
from fastmcp import FastMCP

mcp = FastMCP("Tools")

@mcp.tool()
def search_docs(query: str) -> str:
    """Search internal documentation."""
    return f"Found 3 results for '{query}': [doc1, doc2, doc3]"

@mcp.tool()
def create_ticket(title: str, description: str, priority: str = "medium") -> str:
    """Create a support ticket."""
    return f"Ticket created: '{title}' (priority={priority})"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

**Agent (agent.py):**

```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

async def main():
    client = MultiServerMCPClient(
        {
            "tools": {
                "url": "http://localhost:8000/mcp",
                "transport": "http",
            },
        }
    )
    tools = await client.get_tools()
    agent = create_agent("openai:gpt-4.1", tools)

    result = await agent.ainvoke(
        {"messages": [
            {"role": "user", "content": "Search docs for 'auth errors' then create a high priority ticket about it"}
        ]}
    )
    for msg in result["messages"]:
        print(f"{msg.type}: {msg.content}")

if __name__ == "__main__":
    asyncio.run(main())
```

### End-to-End: Multi-Server StateGraph with Interceptors

Combines multiple servers, a custom StateGraph, and a tool interceptor for runtime context injection.

```python
import asyncio
from dataclasses import dataclass
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

@dataclass
class UserContext:
    user_id: str

async def inject_user(request: MCPToolCallRequest, handler):
    """Inject user_id into every tool call."""
    runtime = request.runtime
    user_id = runtime.context.user_id
    modified = request.override(args={**request.args, "user_id": user_id})
    return await handler(modified)

async def main():
    model = init_chat_model("openai:gpt-4.1")

    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["./math_server.py"],
                "transport": "stdio",
            },
            "weather": {
                "url": "http://localhost:8000/mcp",
                "transport": "http",
            },
        },
        tool_interceptors=[inject_user],
    )
    tools = await client.get_tools()

    def call_model(state: MessagesState):
        return {"messages": model.bind_tools(tools).invoke(state["messages"])}

    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", tools_condition)
    builder.add_edge("tools", "call_model")
    graph = builder.compile()

    result = await graph.ainvoke(
        {"messages": [{"role": "user", "content": "what is the weather in NYC?"}]},
        config={"configurable": {"context": UserContext(user_id="user_42")}},
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### End-to-End: LangGraph API Server Deployment

**Project layout:**

```
my-agent/
  graph.py
  math_server.py
  langgraph.json
  pyproject.toml
```

**graph.py:**

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

async def make_graph():
    client = MultiServerMCPClient(
        {
            "math": {
                "url": "http://math-service:8000/mcp",
                "transport": "http",
            },
        }
    )
    tools = await client.get_tools()
    return create_agent("openai:gpt-4.1", tools)
```

**langgraph.json:**

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./graph.py:make_graph"
  }
}
```

**Run locally:**

```bash
# Start MCP server in one terminal
python math_server.py

# Start LangGraph API Server in another terminal
pip install langgraph-cli
langgraph dev
```

The agent is served at `http://localhost:8123` and can be called via the LangGraph SDK or REST API.

## Transport Reference

| Transport | Config Key | Required Fields | Use Case |
|-----------|-----------|----------------|----------|
| `stdio` | `"transport": "stdio"` | `command`, `args` | Local dev, single-user, subprocess-based |
| `http` | `"transport": "http"` | `url` | Remote servers, production, multi-client |
| `sse` | `"transport": "sse"` | `url` | Legacy server-sent events connections |

All HTTP-based transports (`http`, `sse`) accept an optional `headers` dict for authentication and custom headers.

## Key Imports

```python
# Client and tool loading
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

# Agent creation (prebuilt ReAct agent)
from langchain.agents import create_agent

# Model initialization
from langchain.chat_models import init_chat_model

# LangGraph graph construction
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

# Interceptors and callbacks
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext

# MCP server creation
from fastmcp import FastMCP

# Low-level MCP client (for direct connections)
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client
```

---

## Documentation Links

- [langchain-mcp-adapters GitHub Repository](https://github.com/langchain-ai/langchain-mcp-adapters) - Official repository with examples for using MCP tools with LangGraph StateGraph and LangGraph API Server
- [LangChain MCP Documentation](https://docs.langchain.com/oss/python/langchain/mcp) - Official documentation covering custom MCP servers with FastMCP and integration patterns
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/) - LangGraph framework documentation for building stateful agent workflows
- [FastMCP](https://github.com/jlowin/fastmcp) - Decorator-based library for creating custom MCP tool servers
