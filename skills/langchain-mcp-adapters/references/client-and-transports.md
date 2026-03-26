# langchain-mcp-adapters -- Client & Transport Configuration Reference

## MultiServerMCPClient

The central class for managing connections to one or more MCP servers. It handles session lifecycle and exposes LangChain-compatible tools, prompts, and resources from all connected servers.

### Constructor

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    connections: dict[str, Connection] | None = None,
    *,
    callbacks: Callbacks | None = None,
    tool_interceptors: list[ToolCallInterceptor] | None = None,
    tool_name_prefix: bool = False,
)
```

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `connections` | `dict[str, Connection] \| None` | `None` | Maps server names (arbitrary strings) to connection configurations. Each value is a `StdioConnection`, `SSEConnection`, `StreamableHttpConnection`, or `WebsocketConnection` TypedDict. |
| `callbacks` | `Callbacks \| None` | `None` | Notification and event handlers forwarded to the underlying MCP `ClientSession`. |
| `tool_interceptors` | `list[ToolCallInterceptor] \| None` | `None` | Interceptors that can modify tool call requests and responses before they reach the server. |
| `tool_name_prefix` | `bool` | `False` | When `True`, each tool name is prefixed with its server name and an underscore (e.g., a tool named `search` on server `weather` becomes `weather_search`). Useful for avoiding name collisions across servers. |

### Key Methods

**`get_tools`** -- loads LangChain `BaseTool` instances from connected servers.

```python
async def get_tools(self, *, server_name: str | None = None) -> list[BaseTool]
```

When called without `server_name`, tools from all servers are loaded concurrently via `asyncio.gather`. When called with a specific server name, only that server's tools are returned. A new MCP `ClientSession` is created for each tool invocation at call time.

**`session`** -- opens a managed `ClientSession` to a named server.

```python
@asynccontextmanager
async def session(
    self,
    server_name: str,
    *,
    auto_initialize: bool = True,
) -> AsyncIterator[ClientSession]
```

Raises `ValueError` if `server_name` is not present in the connections dict. When `auto_initialize` is `True` (the default), `session.initialize()` is called automatically.

**`get_prompt`** -- retrieves a prompt template from a specific server.

```python
async def get_prompt(
    self,
    server_name: str,
    prompt_name: str,
    *,
    arguments: dict[str, Any] | None = None,
) -> list[HumanMessage | AIMessage]
```

**`get_resources`** -- retrieves resources (files, data blobs) from servers.

```python
async def get_resources(
    self,
    server_name: str | None = None,
    *,
    uris: str | list[str] | None = None,
) -> list[Blob]
```

When `uris` is `None`, only static resources are returned (dynamic resources are not loaded).

---

## Connection Union Type

All connection configurations are defined as TypedDicts and combined into a single union:

```python
Connection = StdioConnection | SSEConnection | StreamableHttpConnection | WebsocketConnection
```

Every connection TypedDict requires a `transport` literal field that identifies which transport to use. The rest of the fields vary by type.

---

## StdioConnection

Launches the MCP server as a local subprocess and communicates over stdin/stdout. Inherently stateful -- the subprocess persists for the lifetime of the client connection.

> **Deployment note:** stdio transport was designed for applications running on a user's machine. Evaluate whether a remote transport (HTTP, SSE, WebSocket) is more appropriate before using stdio in a web server context.

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `transport` | `Literal["stdio"]` | Yes | -- | Must be `"stdio"`. |
| `command` | `str` | Yes | -- | Executable to run (e.g., `"python"`, `"node"`, `"npx"`). |
| `args` | `list[str]` | Yes | -- | Command-line arguments passed to the executable. |
| `env` | `dict[str, str] \| None` | No | `None` | Environment variables for the subprocess. When `None`, a subset of the parent process environment is inherited. |
| `cwd` | `str \| Path \| None` | No | `None` | Working directory for the subprocess. |
| `encoding` | `str` | No | `"utf-8"` | Text encoding for messages sent to/from the server. |
| `encoding_error_handler` | `Literal["strict", "ignore", "replace"]` | No | `"strict"` | How encoding/decoding errors are handled. `"strict"` raises on error. |
| `session_kwargs` | `dict[str, Any] \| None` | No | `None` | Extra keyword arguments forwarded to the MCP `ClientSession` constructor. |

### Example

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "math": {
            "transport": "stdio",
            "command": "python",
            "args": ["./servers/math_server.py"],
            "env": {"PYTHONPATH": "/opt/custom/lib"},
            "cwd": "/opt/servers",
        }
    }
)
tools = await client.get_tools()
```

---

## SSEConnection

Connects to an MCP server over Server-Sent Events. Supports custom headers and authentication. Note that SSE has been deprecated in the MCP specification in favor of Streamable HTTP, but it remains supported for backward compatibility.

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `transport` | `Literal["sse"]` | Yes | -- | Must be `"sse"`. |
| `url` | `str` | Yes | -- | Full URL of the SSE endpoint. |
| `headers` | `dict[str, Any] \| None` | No | `None` | HTTP headers sent with every request (e.g., authorization tokens, tracing headers). |
| `timeout` | `float` | No | `5` | HTTP request timeout in seconds. Increase for slow-responding servers. |
| `sse_read_timeout` | `float` | No | `300` (5 min) | Maximum seconds to wait for a new SSE event before disconnecting. |
| `session_kwargs` | `dict[str, Any] \| None` | No | `None` | Extra keyword arguments forwarded to the MCP `ClientSession`. |
| `httpx_client_factory` | `McpHttpClientFactory \| None` | No | `None` | Custom factory for creating the underlying `httpx.AsyncClient`. See the Headers & Authentication section. |
| `auth` | `httpx.Auth` | No | -- | Authentication handler passed to the `httpx.AsyncClient`. Supports any `httpx.Auth` subclass including OAuth flows. |

### Example

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "legacy_server": {
            "transport": "sse",
            "url": "https://my-mcp-server.example.com/sse",
            "headers": {"Authorization": "Bearer sk-abc123"},
            "timeout": 10,
            "sse_read_timeout": 600,
        }
    }
)
tools = await client.get_tools()
```

---

## StreamableHttpConnection

The recommended remote transport. Communicates over standard HTTP with optional SSE streaming for long-running responses. Supports headers, authentication, and custom HTTP client configuration.

The `transport` literal accepts both `"streamable_http"` and the shorthand `"http"` -- they are interchangeable.

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `transport` | `Literal["streamable_http"]` | Yes | -- | Must be `"streamable_http"` (or `"http"` as an alias). |
| `url` | `str` | Yes | -- | Full URL of the HTTP endpoint (e.g., `"http://localhost:3000/mcp"`). |
| `headers` | `dict[str, Any] \| None` | No | `None` | HTTP headers sent with every request. |
| `timeout` | `timedelta` | No | `timedelta(seconds=30)` | HTTP request timeout. Note: this is a `timedelta`, not a float. |
| `sse_read_timeout` | `timedelta` | No | `timedelta(seconds=300)` | Maximum wait time for a new SSE event before disconnecting. All other HTTP operations use `timeout`. |
| `terminate_on_close` | `bool` | No | -- | Whether to send a termination signal when the session closes. |
| `session_kwargs` | `dict[str, Any] \| None` | No | `None` | Extra keyword arguments forwarded to the MCP `ClientSession`. |
| `httpx_client_factory` | `McpHttpClientFactory \| None` | No | `None` | Custom factory for creating the underlying `httpx.AsyncClient`. |
| `auth` | `httpx.Auth` | No | -- | Authentication handler passed to the `httpx.AsyncClient`. |

### Example -- Basic

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "weather": {
            "transport": "http",
            "url": "http://localhost:8000/mcp",
        }
    }
)
tools = await client.get_tools()
```

### Example -- With Headers and Timeout

```python
from datetime import timedelta
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "weather": {
            "transport": "streamable_http",
            "url": "https://api.example.com/mcp",
            "headers": {
                "Authorization": "Bearer YOUR_TOKEN",
                "X-Request-ID": "trace-abc-123",
            },
            "timeout": timedelta(seconds=60),
            "sse_read_timeout": timedelta(minutes=10),
        }
    }
)
tools = await client.get_tools()
```

---

## WebsocketConnection

Connects to an MCP server over WebSocket. Minimal configuration -- only requires a URL. Does not support headers or authentication fields directly; use `session_kwargs` if the underlying WebSocket library supports them.

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `transport` | `Literal["websocket"]` | Yes | -- | Must be `"websocket"`. |
| `url` | `str` | Yes | -- | WebSocket endpoint URL (e.g., `"ws://localhost:8080"` or `"wss://example.com/ws"`). |
| `session_kwargs` | `dict[str, Any] \| None` | No | `None` | Extra keyword arguments forwarded to the MCP `ClientSession`. |

### Example

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "realtime": {
            "transport": "websocket",
            "url": "ws://localhost:8080",
        }
    }
)
tools = await client.get_tools()
```

---

## Headers & Authentication

Headers and authentication are supported on `SSEConnection` and `StreamableHttpConnection`. They are not available on `StdioConnection` (no HTTP layer) or `WebsocketConnection`.

### Static Headers

Pass a `headers` dict to include HTTP headers with every request. Common use cases: bearer tokens, API keys, tracing/correlation IDs.

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "api_server": {
            "transport": "http",
            "url": "https://api.example.com/mcp",
            "headers": {
                "Authorization": "Bearer sk-live-abc123",
                "X-Trace-ID": "req-456",
            },
        }
    }
)
```

### httpx.Auth Integration

For dynamic authentication (OAuth2, token refresh, custom flows), pass an `httpx.Auth` instance via the `auth` field. This is forwarded directly to the underlying `httpx.AsyncClient`.

```python
import httpx
from langchain_mcp_adapters.client import MultiServerMCPClient


class TokenRefreshAuth(httpx.Auth):
    """Custom auth that refreshes an expired bearer token."""

    def __init__(self, token_url: str, client_id: str, client_secret: str):
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self._token: str | None = None

    def auth_flow(self, request: httpx.Request):
        if self._token is None:
            self._token = self._fetch_token()
        request.headers["Authorization"] = f"Bearer {self._token}"
        yield request

    def _fetch_token(self) -> str:
        resp = httpx.post(
            self.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )
        resp.raise_for_status()
        return resp.json()["access_token"]


auth = TokenRefreshAuth(
    token_url="https://auth.example.com/token",
    client_id="my-client",
    client_secret="my-secret",
)

client = MultiServerMCPClient(
    {
        "secured_server": {
            "transport": "http",
            "url": "https://api.example.com/mcp",
            "auth": auth,
        }
    }
)
tools = await client.get_tools()
```

### McpHttpClientFactory Protocol

For full control over the HTTP client (custom TLS, proxies, connection pooling), provide a callable that returns an `httpx.AsyncClient`:

```python
import httpx
from langchain_mcp_adapters.client import MultiServerMCPClient


def custom_httpx_factory(
    headers: dict[str, str] | None = None,
    timeout: httpx.Timeout | None = None,
    auth: httpx.Auth | None = None,
) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        headers=headers,
        timeout=timeout,
        auth=auth,
        verify="/path/to/custom-ca-bundle.pem",
        proxy="http://corporate-proxy:8080",
    )


client = MultiServerMCPClient(
    {
        "internal_server": {
            "transport": "http",
            "url": "https://internal.corp.example.com/mcp",
            "httpx_client_factory": custom_httpx_factory,
        }
    }
)
```

---

## Multi-Server Setup

`MultiServerMCPClient` accepts any number of servers in the connections dict. Each server operates independently with its own transport, credentials, and session lifecycle. Tools from all servers are merged into a single list by `get_tools()`.

### Mixed-Transport Example

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "math": {
            "transport": "stdio",
            "command": "python",
            "args": ["./servers/math_server.py"],
        },
        "weather": {
            "transport": "http",
            "url": "http://localhost:8000/mcp",
            "headers": {"Authorization": "Bearer weather-token"},
        },
        "legacy_data": {
            "transport": "sse",
            "url": "https://data.example.com/sse",
            "timeout": 15,
        },
        "realtime_feed": {
            "transport": "websocket",
            "url": "ws://localhost:9000",
        },
    }
)

# Load all tools from every server concurrently
all_tools = await client.get_tools()

# Or load tools from a single server
math_tools = await client.get_tools(server_name="math")
```

### Using tool_name_prefix to Avoid Collisions

When multiple servers expose tools with the same name (e.g., both expose a `search` tool), enable `tool_name_prefix` to disambiguate:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "web": {
            "transport": "http",
            "url": "http://localhost:8001/mcp",
        },
        "docs": {
            "transport": "http",
            "url": "http://localhost:8002/mcp",
        },
    },
    tool_name_prefix=True,
)

tools = await client.get_tools()
# Without prefix: ["search", "search"]  -- collision
# With prefix:    ["web_search", "docs_search"]  -- unique
```

### Explicit Session for Direct MCP SDK Access

When you need to work with the raw MCP `ClientSession` (for example, to call protocol methods not wrapped by the adapter), use the `session` context manager:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

client = MultiServerMCPClient(
    {
        "math": {
            "transport": "stdio",
            "command": "python",
            "args": ["./servers/math_server.py"],
        }
    }
)

async with client.session("math") as session:
    # session is an initialized mcp.ClientSession
    tools = await load_mcp_tools(session)
    resources = await session.list_resources()
```

### Integration with LangGraph

A common pattern is wiring `MultiServerMCPClient` tools into a LangGraph `StateGraph`:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

model = init_chat_model("openai:gpt-4.1")

client = MultiServerMCPClient(
    {
        "math": {
            "transport": "stdio",
            "command": "python",
            "args": ["./servers/math_server.py"],
        },
        "weather": {
            "transport": "http",
            "url": "http://localhost:8000/mcp",
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
graph = builder.compile()

result = await graph.ainvoke(
    {"messages": [{"role": "user", "content": "What is (3 + 5) x 12?"}]}
)
```

### Direct Python MCP SDK (Without MultiServerMCPClient)

For single-server use cases or when you need lower-level control, you can bypass `MultiServerMCPClient` and use the Python MCP SDK directly:

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from langchain_mcp_adapters.tools import load_mcp_tools

async with streamablehttp_client("http://localhost:3000/mcp") as (read, write, _):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await load_mcp_tools(session)
```

---

## Transport Comparison

| Transport | Literal Value | Stateful | Headers | Auth | Typical Use Case |
|-----------|---------------|----------|---------|------|------------------|
| Stdio | `"stdio"` | Yes (subprocess) | No | No | Local tools, CLI wrappers, development |
| Streamable HTTP | `"streamable_http"` or `"http"` | No (by default) | Yes | Yes (`httpx.Auth`) | Remote services, production APIs |
| SSE | `"sse"` | Varies | Yes | Yes (`httpx.Auth`) | Legacy servers (deprecated in MCP spec) |
| WebSocket | `"websocket"` | Yes (persistent) | No | No | Real-time bidirectional communication |

---

## Transport Selection Guidelines

### Use HTTP Transport When:
- Connecting to remote services
- Need authentication/authorization
- Require custom headers (tracing, API keys)
- Want to deploy servers independently
- Building production APIs

### Use stdio Transport When:
- Running local tools
- Need simple setup for development
- Want subprocess isolation
- Working with command-line utilities
- Building user-facing desktop applications

**Important:** stdio transport was designed primarily for applications running on a user's machine. Evaluate whether a remote transport (HTTP, SSE, WebSocket) is more appropriate before using stdio in a web server context.

---

## Setting Up MCP Servers

### FastMCP with HTTP Transport

```python
from fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    return f"It's sunny in {location}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

Run with: `python weather_server.py --port 8000`

### FastMCP with stdio Transport

```python
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

Run with: `python math_server.py`

---

## Default Constants

These defaults are defined in `langchain_mcp_adapters.sessions`:

| Constant | Value | Applies To |
|----------|-------|------------|
| `DEFAULT_ENCODING` | `"utf-8"` | StdioConnection |
| `DEFAULT_ENCODING_ERROR_HANDLER` | `"strict"` | StdioConnection |
| `DEFAULT_HTTP_TIMEOUT` | `5` (seconds) | SSEConnection |
| `DEFAULT_SSE_READ_TIMEOUT` | `300` (seconds / 5 min) | SSEConnection |
| `DEFAULT_STREAMABLE_HTTP_TIMEOUT` | `timedelta(seconds=30)` | StreamableHttpConnection |
| `DEFAULT_STREAMABLE_HTTP_SSE_READ_TIMEOUT` | `timedelta(seconds=300)` | StreamableHttpConnection |

---

## Documentation Links

### Official Documentation
- **GitHub Repository**: [langchain-ai/langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
  - Multiple MCP Servers configuration
  - Streamable HTTP transport setup
  - Runtime headers and authentication examples
- **LangChain Python Docs**: [MCP Integration Guide](https://docs.langchain.com/oss/python/langchain/mcp)
  - Transport selection and configuration
  - FastMCP server setup
  - Integration patterns
- **API Reference**: [langchain_mcp_adapters](https://reference.langchain.com/python/langchain_mcp_adapters/)
  - `MultiServerMCPClient` class reference
  - Connection type specifications
  - Complete parameter documentation

### Related Resources
- **MCP Specification**: Model Context Protocol official docs
- **FastMCP**: Framework for building MCP servers in Python
- **httpx Documentation**: For custom authentication and HTTP client configuration
