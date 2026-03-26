# langchain-mcp-adapters -- Tools Reference

How MCP tools are loaded, converted to LangChain `BaseTool` objects, and how to work with structured and multimodal content they return.

## Loading Tools

There are two ways to load MCP tools as LangChain tools: via the `MultiServerMCPClient` convenience method, or via the standalone `load_mcp_tools()` function.

---

### client.get_tools()

The simplest approach. Call `get_tools()` on a `MultiServerMCPClient` instance to retrieve all tools from every connected server as a flat list of `BaseTool` objects.

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

async with MultiServerMCPClient(
    {
        "math": {
            "transport": "stdio",
            "command": "python",
            "args": ["-m", "math_server"],
        },
        "weather": {
            "transport": "sse",
            "url": "http://localhost:8000/sse",
        },
    }
) as client:
    tools = await client.get_tools()
    # tools is list[BaseTool] -- all tools from both servers
```

When using `MultiServerMCPClient` as an async context manager, calling `get_tools()` is the standard path. The client manages sessions internally and returns combined tools from all configured servers.

---

### load_mcp_tools()

The standalone function for cases where you need direct control over the session or connection. Located in `langchain_mcp_adapters.tools`.

```python
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "math": {
        "transport": "stdio",
        "command": "python",
        "args": ["-m", "math_server"],
    },
})

async with client.session("math") as session:
    tools = await load_mcp_tools(session)
```

#### Function Signature

```python
async def load_mcp_tools(
    session: ClientSession | None,
    *,
    connection: Connection | None = None,
    callbacks: Callbacks | None = None,
    tool_interceptors: list[ToolCallInterceptor] | None = None,
    server_name: str | None = None,
    tool_name_prefix: bool = False,
) -> list[BaseTool]
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session` | `ClientSession \| None` | required | An active MCP client session. If `None`, `connection` must be provided instead. |
| `connection` | `Connection \| None` | `None` | Connection configuration used to create a new session when `session` is `None`. A new session is created for each tool call in this mode. |
| `callbacks` | `Callbacks \| None` | `None` | Optional LangChain callbacks for handling notifications and events during tool execution. |
| `tool_interceptors` | `list[ToolCallInterceptor] \| None` | `None` | Interceptors that wrap tool call execution. See the Interceptors reference for details. |
| `server_name` | `str \| None` | `None` | Identifies which server these tools belong to. Used for prefixing when `tool_name_prefix=True`. |
| `tool_name_prefix` | `bool` | `False` | When `True` and `server_name` is provided, prepends the server name to each tool name (e.g., `"weather_search"` instead of `"search"`). |

#### Returns

`list[BaseTool]` — LangChain `StructuredTool` objects. Each tool carries MCP annotations in its `metadata` dict.

#### Raises

`ValueError` — If both `session` and `connection` are `None`.

#### Using connection instead of session

When you pass `connection` instead of `session`, a new MCP session is created on each tool invocation. This is useful for stateless transports but adds overhead for persistent connections.

```python
from langchain_mcp_adapters.tools import load_mcp_tools

tools = await load_mcp_tools(
    session=None,
    connection={
        "transport": "sse",
        "url": "http://localhost:8000/sse",
    },
    server_name="weather",
)
```

---

### MCP-to-LangChain Conversion

Under the hood, both loading methods call `convert_mcp_tool_to_langchain_tool()` for each tool discovered on the server. The conversion maps:

| MCP Tool Field | LangChain BaseTool Field |
|----------------|--------------------------|
| `tool.name` | `name` (optionally prefixed with `server_name_`) |
| `tool.description` | `description` |
| `tool.inputSchema` | `args_schema` |
| `tool.annotations` | `metadata["annotations"]` |

The resulting tool uses `response_format="content_and_artifact"`, which means tool results are returned as a `ToolMessage` containing both the text content and an optional `artifact` field for structured data.

---

## Structured Content

MCP tools can return `structuredContent` alongside text in their `CallToolResult`. The adapter wraps this in an `MCPToolArtifact` and attaches it to the `ToolMessage.artifact` field.

### MCPToolArtifact

```python
from typing import Any
from typing_extensions import TypedDict

class MCPToolArtifact(TypedDict):
    structured_content: dict[str, Any]
```

| Field | Type | Description |
|-------|------|-------------|
| `structured_content` | `dict[str, Any]` | The structured content from the MCP tool, corresponding to the `structuredContent` field in `CallToolResult`. |

### Reading Structured Content from Agent Output

After invoking an agent, inspect the `ToolMessage` objects in the response for artifacts:

```python
from langchain_core.messages import ToolMessage

result = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "Query the database for active users"}]}
)

for message in result["messages"]:
    if isinstance(message, ToolMessage) and message.artifact:
        structured = message.artifact["structured_content"]
        print(f"Got structured data: {structured}")
```

### Surfacing Structured Content via an Interceptor

By default the LLM only sees the text portion of a tool result. To make structured content visible to the model, use an interceptor that appends it to the text content:

```python
import json
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from mcp.types import TextContent

async def append_structured_content(request: MCPToolCallRequest, handler):
    """Make structuredContent visible to the model by appending it as text."""
    result = await handler(request)
    if result.structuredContent:
        result.content.append(
            TextContent(type="text", text=json.dumps(result.structuredContent))
        )
    return result

async with MultiServerMCPClient(
    {
        "db": {
            "transport": "stdio",
            "command": "python",
            "args": ["-m", "db_server"],
        },
    },
    tool_interceptors=[append_structured_content],
) as client:
    tools = await client.get_tools()
```

---

## Multimodal Content

MCP tools can return mixed content types — text, images, resource links, and embedded resources. The adapter converts each MCP content block into the corresponding LangChain content block type.

### Content Type Mapping

| MCP Content Type | LangChain Block | Notes |
|------------------|-----------------|-------|
| `TextContent` | `TextContentBlock` | Plain text |
| `ImageContent` | `ImageContentBlock` | Base64-encoded image with MIME type |
| `ResourceLink` (image MIME) | `ImageContentBlock` | Image referenced by URI |
| `ResourceLink` (other MIME) | `FileContentBlock` | Non-image file referenced by URI |
| `EmbeddedResource` (text) | `TextContentBlock` | Inline text resource |
| `EmbeddedResource` (blob, image) | `ImageContentBlock` | Inline base64 image |
| `EmbeddedResource` (blob, other) | `FileContentBlock` | Inline base64 file |
| `AudioContent` | — | **Not yet supported.** Raises `NotImplementedError`. |

### Accessing Multimodal Results

Tool results that contain multiple content types are accessible through the `content` field (raw provider format) and the `content_blocks` property (standardized LangChain format):

```python
result = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "Generate a chart of monthly sales"}]}
)

for message in result["messages"]:
    if message.type == "tool":
        for block in message.content_blocks:
            if block["type"] == "text":
                print(f"Text: {block['text']}")
            elif block["type"] == "image":
                mime = block.get("mime_type", "unknown")
                if "url" in block:
                    print(f"Image URL ({mime}): {block['url']}")
                elif "base64" in block:
                    print(f"Image base64 ({mime}): {block['base64'][:60]}...")
            elif block["type"] == "file":
                print(f"File: {block.get('url') or 'base64 blob'}")
```

### Return Type

Internally the adapter uses the union type for converted tool results:

```python
ToolMessageContentBlock = TextContentBlock | ImageContentBlock | FileContentBlock
```

A single tool call can return a list containing any mix of these block types.

---

## Tool Name Prefixing

When connecting to multiple MCP servers, tool names can collide. For example, two servers might each expose a tool named `search`. The `tool_name_prefix` option resolves this by prepending the server name to each tool name.

### With MultiServerMCPClient

Pass `tool_name_prefix=True` in the server configuration:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

async with MultiServerMCPClient(
    {
        "weather": {
            "transport": "stdio",
            "command": "python",
            "args": ["-m", "weather_server"],
            "tool_name_prefix": True,
        },
        "news": {
            "transport": "stdio",
            "command": "python",
            "args": ["-m", "news_server"],
            "tool_name_prefix": True,
        },
    }
) as client:
    tools = await client.get_tools()
    # If both servers expose "search", you get:
    #   "weather_search" and "news_search"
```

### With load_mcp_tools()

Pass both `server_name` and `tool_name_prefix=True`:

```python
from langchain_mcp_adapters.tools import load_mcp_tools

tools = await load_mcp_tools(
    session=my_session,
    server_name="weather",
    tool_name_prefix=True,
)
# Tool originally named "search" becomes "weather_search"
```

The prefix is applied as `f"{server_name}_{tool.name}"`. If `server_name` is `None`, setting `tool_name_prefix=True` has no effect.

---

## Tool Execution Patterns

### Default Stateless Execution

By default, each tool invocation creates a fresh MCP session, executes the tool, and cleans up. This is the behavior when you pass a `connection` configuration instead of a persistent `session` to `load_mcp_tools()`.

```python
from langchain_mcp_adapters.tools import load_mcp_tools

# Each tool call creates a new session
tools = await load_mcp_tools(
    session=None,
    connection={
        "transport": "sse",
        "url": "http://localhost:8000/sse",
    },
)
```

This works well for stateless servers but adds overhead for each invocation.

### Stateful Sessions

For servers that maintain context across tool calls (e.g., database connections, user sessions), create a persistent session using a context manager:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "db": {
        "transport": "stdio",
        "command": "python",
        "args": ["-m", "database_server"],
    },
})

async with client.session("db") as session:
    tools = await load_mcp_tools(session)
    # All tool calls within this block share the same session
    result = await agent.ainvoke({"messages": [...]})
```

---

## Best Practices

1. **Use persistent sessions for stateful servers** — If your MCP server maintains state (database connections, user context), always load tools within a session context manager to ensure tool calls share the same session.

2. **Use interceptors to access runtime context** — Tool interceptors allow you to inject user IDs, state, or other runtime context during tool execution. See the Interceptors reference for details.

3. **Handle structured content explicitly** — If you need machine-parseable data from tool results, access the `artifact` field on `ToolMessage` objects rather than parsing text output.

4. **Create persistent sessions for better performance** — For servers using persistent transports (stdio, SSE), reusing sessions is more efficient than creating a new session per tool call.

5. **Access multimodal content via content_blocks** — Use the `content_blocks` property for provider-agnostic handling of mixed content types (text, images, files).

6. **Use tool name prefixing to avoid collisions** — When connecting to multiple servers that might expose tools with the same name, enable `tool_name_prefix=True` to namespace tool names by server.

---

## Documentation Links

- [LangChain MCP Tools Documentation](https://docs.langchain.com/oss/python/langchain/mcp) - Official guide covering MCP tools integration, loading, structured content, and multimodal handling
- [langchain_mcp_adapters API Reference](https://reference.langchain.com/python/langchain_mcp_adapters/) - API documentation for load_mcp_tools, MCPToolArtifact, and related classes
