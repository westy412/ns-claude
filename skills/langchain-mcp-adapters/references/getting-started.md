# langchain-mcp-adapters -- Getting Started Reference

## Installation

### Core Package

```bash
pip install langchain-mcp-adapters
# or
uv add langchain-mcp-adapters
```

### With Agent Dependencies

To build agents that use MCP tools, install the agent framework and an LLM provider:

```bash
pip install langchain-mcp-adapters langgraph "langchain[openai]"
```

Or with Anthropic models:

```bash
pip install langchain-mcp-adapters langgraph langchain-anthropic
```

### MCP Server Authoring

To write your own MCP servers, install FastMCP:

```bash
pip install fastmcp
```

### Environment Variables

| Variable | When Needed |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI models (e.g., `openai:gpt-4.1`) |
| `ANTHROPIC_API_KEY` | Anthropic models (e.g., `anthropic:claude-sonnet-4-5-20250929`) |
| `GOOGLE_API_KEY` | Google GenAI models |

Set the key for your chosen provider before running agents:

```bash
export OPENAI_API_KEY=<your_key>
# or
export ANTHROPIC_API_KEY=<your_key>
```

---

## Core Imports

```python
# Client for connecting to one or more MCP servers
from langchain_mcp_adapters.client import MultiServerMCPClient

# Load tools from a raw MCP session
from langchain_mcp_adapters.tools import load_mcp_tools

# Load resources exposed by an MCP server
from langchain_mcp_adapters.resources import load_mcp_resources

# Load prompt templates from an MCP server
from langchain_mcp_adapters.prompts import load_mcp_prompt

# Create a LangChain ReAct agent
from langchain.agents import create_agent

# Low-level MCP session and transport clients
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client
```

---

## Quick Start

The fastest path from zero to a working MCP-powered agent:

```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

async def main():
    client = MultiServerMCPClient({
        "math": {
            "transport": "stdio",
            "command": "python",
            "args": ["/absolute/path/to/math_server.py"],
        },
    })

    tools = await client.get_tools()
    agent = create_agent("openai:gpt-4.1", tools)

    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
    )
    print(response["messages"][-1].content)

asyncio.run(main())
```

---

## Writing an MCP Server

### stdio Server

A stdio server communicates over standard input/output. Best for local tools running on the same machine as the client.

```python
# math_server.py
from fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

The client spawns stdio servers automatically -- you do not start them manually in production. For manual testing:

```bash
python math_server.py
```

### HTTP Server

An HTTP server listens on a network port. Best for remote or shared services.

```python
# weather_server.py
from fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"It's sunny in {location}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

Start the HTTP server before connecting a client:

```bash
python weather_server.py
```

By default this listens on port 8000 at the `/mcp` endpoint.

### Transport Comparison

| Transport | Protocol | When to Use | Client Spawns Process |
|-----------|----------|-------------|----------------------|
| `stdio` | stdin/stdout | Local tools on the same machine | Yes |
| `http` | Streamable HTTP | Remote services, shared deployments | No (start separately) |
| `sse` | Server-Sent Events | Legacy HTTP-based servers | No (start separately) |

---

## Connecting a Client

### MultiServerMCPClient

`MultiServerMCPClient` is the primary way to connect to one or more MCP servers. It manages transport lifecycles and exposes tools as LangChain `BaseTool` instances.

#### Single stdio Server

```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

async def main():
    client = MultiServerMCPClient({
        "math": {
            "transport": "stdio",
            "command": "python",
            "args": ["/absolute/path/to/math_server.py"],
        },
    })
    tools = await client.get_tools()
    print([t.name for t in tools])

asyncio.run(main())
```

#### Single HTTP Server

```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

async def main():
    client = MultiServerMCPClient({
        "weather": {
            "transport": "http",
            "url": "http://localhost:8000/mcp",
        },
    })
    tools = await client.get_tools()
    print([t.name for t in tools])

asyncio.run(main())
```

#### Multiple Servers (Mixed Transports)

```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

async def main():
    client = MultiServerMCPClient({
        "math": {
            "transport": "stdio",
            "command": "python",
            "args": ["/absolute/path/to/math_server.py"],
        },
        "weather": {
            "transport": "http",
            "url": "http://localhost:8000/mcp",
        },
    })
    tools = await client.get_tools()
    # tools list contains tools from both servers
    print([t.name for t in tools])

asyncio.run(main())
```

### Server Configuration Parameters

#### stdio Transport

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `transport` | `str` | Yes | Must be `"stdio"` |
| `command` | `str` | Yes | Executable to run (e.g., `"python"`, `"node"`) |
| `args` | `list[str]` | Yes | Arguments passed to the command (use absolute paths) |

#### HTTP / Streamable HTTP Transport

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `transport` | `str` | Yes | `"http"` or `"streamable_http"` |
| `url` | `str` | Yes | Full URL to the MCP endpoint (e.g., `"http://localhost:8000/mcp"`) |
| `headers` | `dict[str, str]` | No | Custom HTTP headers (e.g., auth tokens) |

#### SSE Transport

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `transport` | `str` | Yes | Must be `"sse"` |
| `url` | `str` | Yes | Full URL to the SSE endpoint |
| `headers` | `dict[str, str]` | No | Custom HTTP headers |

### Authentication Headers

Pass authorization headers for HTTP and SSE transports:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "my_service": {
        "transport": "http",
        "url": "http://localhost:8000/mcp",
        "headers": {
            "Authorization": "Bearer YOUR_TOKEN",
            "X-Custom-Header": "custom-value",
        },
    },
})
```

### Low-Level Session Access

For direct access to an MCP `ClientSession` (e.g., to load resources or prompts), use the `session` context manager. This opens an explicit, stateful session with the named server.

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

client = MultiServerMCPClient({
    "math": {
        "transport": "stdio",
        "command": "python",
        "args": ["/absolute/path/to/math_server.py"],
    },
})

async with client.session("math") as session:
    tools = await load_mcp_tools(session)
    # use tools within this session scope
```

> **Note:** By default, `get_tools()` is stateless -- each tool invocation creates a fresh session. Use `client.session(...)` when you need a persistent connection across multiple calls.

---

## Low-Level Client Usage (Without MultiServerMCPClient)

You can bypass `MultiServerMCPClient` and work directly with MCP transport clients. This gives full control over session lifecycle.

### stdio Transport

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["/absolute/path/to/math_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)

            agent = create_agent("openai:gpt-4.1", tools)
            response = await agent.ainvoke(
                {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
            )
            print(response["messages"][-1].content)

asyncio.run(main())
```

### Streamable HTTP Transport

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent

async def main():
    async with streamablehttp_client("http://localhost:3000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)

            agent = create_agent("openai:gpt-4.1", tools)
            response = await agent.ainvoke(
                {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
            )
            print(response["messages"][-1].content)

asyncio.run(main())
```

---

## Creating Your First Agent

### Using `create_agent`

`create_agent` from `langchain.agents` builds a prebuilt ReAct agent from a model string and a list of tools. It handles LLM initialization, tool binding, and the agent loop internally.

```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

async def main():
    client = MultiServerMCPClient({
        "math": {
            "transport": "stdio",
            "command": "python",
            "args": ["/absolute/path/to/math_server.py"],
        },
        "weather": {
            "transport": "http",
            "url": "http://localhost:8000/mcp",
        },
    })

    tools = await client.get_tools()

    # Pass a model string in "provider:model" format
    agent = create_agent("openai:gpt-4.1", tools)

    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
    )
    print(math_response["messages"][-1].content)

    weather_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
    )
    print(weather_response["messages"][-1].content)

asyncio.run(main())
```

### Using LangGraph StateGraph (Custom Agent Loop)

For full control over the agent loop, use LangGraph's `StateGraph` directly. This lets you define custom routing logic, add nodes, and control the execution flow.

```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

async def main():
    model = init_chat_model("openai:gpt-4.1")

    client = MultiServerMCPClient({
        "math": {
            "transport": "stdio",
            "command": "python",
            "args": ["/absolute/path/to/math_server.py"],
        },
        "weather": {
            "transport": "http",
            "url": "http://localhost:8000/mcp",
        },
    })

    tools = await client.get_tools()

    def call_model(state: MessagesState):
        response = model.bind_tools(tools).invoke(state["messages"])
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
    print(result["messages"][-1].content)

asyncio.run(main())
```

### Model String Format

The `create_agent` function and `init_chat_model` accept model identifiers in `provider:model` format:

| Model String | Provider |
|-------------|----------|
| `"openai:gpt-4.1"` | OpenAI |
| `"anthropic:claude-sonnet-4-5-20250929"` | Anthropic |
| `"google_genai:gemini-2.5-flash"` | Google Generative AI |
| `"azure_openai:gpt-4.1"` | Azure OpenAI |

---

## Common Patterns

### asyncio.run Entry Point

All langchain-mcp-adapters APIs are async. Wrap your code in an async function and call it with `asyncio.run`:

```python
import asyncio

async def main():
    # all MCP client and agent code here
    pass

asyncio.run(main())
```

### Absolute Paths for stdio

Always use absolute paths in the `args` list for stdio servers. Relative paths resolve from the working directory of the spawned process, which may differ from your project root:

```python
# Correct
"args": ["/home/user/project/math_server.py"]

# Risky -- depends on working directory
"args": ["./math_server.py"]
```

### Creating the Agent Once

Avoid recreating the client and agent on every request. Create them once and reuse:

```python
# Good: create once
client = MultiServerMCPClient({...})
tools = await client.get_tools()
agent = create_agent("openai:gpt-4.1", tools)

# Reuse across multiple invocations
response1 = await agent.ainvoke({"messages": [...]})
response2 = await agent.ainvoke({"messages": [...]})
```

### Choosing a Transport

- **stdio** -- Use for local development, CLI tools, and single-user environments. The client spawns and manages the server process.
- **HTTP (streamable)** -- Use for shared or remote services, multi-user environments, and production deployments. You start the server independently.
- **SSE** -- Legacy HTTP transport. Use only when connecting to servers that do not support streamable HTTP.

---

## Documentation Links

- [langchain-mcp-adapters GitHub](https://github.com/langchain-ai/langchain-mcp-adapters) - Official repository with installation and quickstart
- [LangChain MCP Integration](https://docs.langchain.com/oss/python/langchain/mcp) - Official LangChain documentation for MCP adapters
- [FastMCP Documentation](https://github.com/jlowin/fastmcp) - Library for building MCP servers
