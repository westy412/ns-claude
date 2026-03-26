# langchain-mcp-adapters -- Session Management Reference

How `MultiServerMCPClient` manages MCP server sessions, and when to control session lifecycle explicitly.

---

## Default Stateless Behavior

`MultiServerMCPClient` is stateless by default. When you call `get_tools()` and then invoke those tools, each tool invocation spins up a fresh `ClientSession`, executes the call, and tears the session down. No state carries over between tool calls.

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "math": {
            "transport": "stdio",
            "command": "uvx",
            "args": ["mcp-server-math"],
        }
    }
)

# get_tools() does NOT open a persistent session.
# Each tool invocation will create and destroy its own session.
tools = await client.get_tools()

# First tool call: creates session -> executes -> closes session
result_1 = await tools[0].ainvoke({"a": 2, "b": 3})

# Second tool call: creates a completely new session
result_2 = await tools[1].ainvoke({"a": 10, "b": 4})
```

This is the right default for most use cases because:

- It avoids resource leaks from forgotten open sessions.
- It works naturally with servers that treat each request independently.
- You do not need to manage async context managers or worry about cleanup.

The tradeoff is overhead: every tool call pays the cost of opening and initializing a new session. For servers that are purely functional (compute something, return a result), this overhead is negligible.

---

## Stateful Sessions

Some MCP servers maintain state across calls. A database server might track an open transaction. A file-system server might maintain a working directory. A conversation-aware server might accumulate context. In these cases, you need one session that stays alive across multiple operations.

The `session()` method on `MultiServerMCPClient` provides this through an async context manager.

### Method Signature

```python
@asynccontextmanager
async def session(
    self,
    server_name: str,
    *,
    auto_initialize: bool = True,
) -> AsyncIterator[ClientSession]:
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `server_name` | `str` | required | The key identifying the server in the client's connection dictionary |
| `auto_initialize` | `bool` | `True` | Whether to call `session.initialize()` automatically on entry |

**Raises:** `ValueError` if `server_name` does not match any key in the connections dictionary.

**Yields:** An initialized `ClientSession` that persists until the context manager exits.

---

## Explicit Session Management

### Basic Pattern

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

client = MultiServerMCPClient(
    {
        "db": {
            "transport": "stdio",
            "command": "uvx",
            "args": ["mcp-server-sqlite", "--db-path", "app.db"],
        }
    }
)

async with client.session("db") as session:
    # All tool calls within this block share the same session.
    tools = await load_mcp_tools(session)

    # These calls happen on the SAME session -- server-side state persists.
    await tools[0].ainvoke({"query": "BEGIN TRANSACTION"})
    await tools[0].ainvoke({"query": "INSERT INTO users (name) VALUES ('Ada')"})
    await tools[0].ainvoke({"query": "COMMIT"})
# Session is closed here automatically.
```

### Loading Resources and Prompts in a Session

Resources and prompts also accept an explicit session, so you can load everything from a single persistent connection:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.resources import load_mcp_resources
from langchain_mcp_adapters.prompts import load_mcp_prompt

client = MultiServerMCPClient(
    {
        "project": {
            "transport": "stdio",
            "command": "uvx",
            "args": ["mcp-server-project"],
        }
    }
)

async with client.session("project") as session:
    tools = await load_mcp_tools(session)
    blobs = await load_mcp_resources(session, uris=["file:///README.md"])
    messages = await load_mcp_prompt(
        session,
        "code_review",
        arguments={"language": "python", "focus": "security"},
    )
```

### Using a Session with a LangChain Agent

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

client = MultiServerMCPClient(
    {
        "workspace": {
            "transport": "stdio",
            "command": "uvx",
            "args": ["mcp-server-workspace"],
        }
    }
)

async with client.session("workspace") as session:
    tools = await load_mcp_tools(session)
    agent = create_react_agent(
        "anthropic:claude-sonnet-4-20250514",
        tools,
    )
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Summarize the project status"}]}
    )
```

The agent's entire execution — including all intermediate tool calls it decides to make — runs against the same session, so the server can track context across the conversation.

### Controlling Initialization with auto_initialize

By default, `session()` calls `session.initialize()` on your behalf before yielding. If you need to defer initialization or handle it yourself:

```python
async with client.session("math", auto_initialize=False) as session:
    # Session is connected but NOT initialized yet.
    # You might inspect transport details or set up callbacks first.
    await session.initialize()
    tools = await load_mcp_tools(session)
```

In practice, leaving `auto_initialize=True` (the default) is almost always what you want. The `False` option exists for advanced scenarios like custom initialization sequences or diagnostic inspection before the handshake completes.

### The Old Context Manager Pattern is Removed

Earlier versions of `langchain-mcp-adapters` allowed using `MultiServerMCPClient` itself as a context manager:

```python
# This no longer works -- raises NotImplementedError
async with MultiServerMCPClient({...}) as client:
    tools = client.get_tools()
```

The `__aenter__` and `__aexit__` methods now raise `NotImplementedError`. Use `client.session("server_name")` instead for explicit session control, or call `client.get_tools()` directly for the default stateless behavior.

---

## When to Use Stateful Sessions

### Use stateless (default) when:

- The server is purely functional (math, formatting, data lookup).
- Each tool call is independent and self-contained.
- You want simplicity and do not want to manage session lifecycle.
- You are calling tools from multiple servers and do not need cross-call state on any of them.

### Use stateful sessions when:

- The server tracks transactions (database servers with BEGIN/COMMIT).
- The server maintains a working directory or cursor position.
- The server accumulates context across calls (conversation memory, incremental builds).
- You need to load tools, resources, and prompts from one consistent connection.
- You want to avoid per-call session overhead in a tight loop of many tool invocations.

### Decision summary

| Scenario | Approach | Why |
|----------|----------|-----|
| Stateless compute (math, hashing) | `get_tools()` | No cross-call state needed |
| Database transactions | `client.session("db")` | Transaction must span multiple calls |
| File system operations | `client.session("fs")` | Working directory context matters |
| Agent with many rapid tool calls | `client.session("server")` | Reduces session setup overhead |
| Multiple independent servers | `get_tools()` | Simpler, no lifecycle management |
| Loading tools + resources + prompts together | `client.session("server")` | Single consistent connection |

### stdio Transport Note

The `stdio` transport is inherently stateful at the process level — the subprocess persists for the lifetime of the client. However, without an explicit `client.session()` call, `MultiServerMCPClient` still creates a new `ClientSession` per tool invocation even over stdio. Use `client.session()` if you need the MCP protocol session (not just the subprocess) to persist across calls.

---

## Documentation Links

- [MCP Adapters Documentation - Stateful Sessions](https://docs.langchain.com/oss/python/langchain/mcp)
- [API Reference - MultiServerMCPClient.session()](https://reference.langchain.com/python/langchain_mcp_adapters/)
