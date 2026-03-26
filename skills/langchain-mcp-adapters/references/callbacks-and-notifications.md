# langchain-mcp-adapters -- Callbacks & Notifications Reference

How to handle progress notifications, logging, and elicitation requests from MCP servers using the `Callbacks` dataclass.

## Callbacks Overview

The `Callbacks` dataclass provides handlers for server-to-client notifications and interactive requests. Pass it to `MultiServerMCPClient` or `load_mcp_tools` to receive events during tool execution.

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.callbacks import Callbacks

callbacks = Callbacks(
    on_progress=my_progress_handler,
    on_logging_message=my_logging_handler,
    on_elicitation=my_elicitation_handler,
)

client = MultiServerMCPClient(
    {"server": {"transport": "http", "url": "http://localhost:8000/mcp"}},
    callbacks=callbacks,
)
```

### Callbacks Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `on_progress` | `Callable \| None` | `None` | Handler for progress update notifications. |
| `on_logging_message` | `Callable \| None` | `None` | Handler for server log messages. |
| `on_elicitation` | `Callable \| None` | `None` | Handler for interactive input requests from the server. |

### CallbackContext

Every callback handler receives a `CallbackContext` object providing metadata about the current operation:

```python
from langchain_mcp_adapters.callbacks import CallbackContext
```

| Field | Type | Description |
|-------|------|-------------|
| `server_name` | `str` | Name of the MCP server that sent the notification. |
| `tool_name` | `str \| None` | Name of the tool being executed (if applicable). |

### Passing Callbacks to load_mcp_tools

Callbacks can also be passed directly to the standalone `load_mcp_tools` function:

```python
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.callbacks import Callbacks

tools = await load_mcp_tools(
    session=None,
    connection=my_connection,
    callbacks=Callbacks(on_progress=my_handler),
)
```

---

## Progress Notifications

MCP servers can report progress during long-running tool operations. The `on_progress` handler receives updates with current progress, optional total, and an optional message.

### Handler Signature

```python
async def on_progress(
    progress: float,
    total: float | None,
    message: str | None,
    context: CallbackContext,
) -> None:
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `progress` | `float` | Current progress value (interpretation depends on server). |
| `total` | `float \| None` | Total expected value. `None` if unknown (indeterminate progress). |
| `message` | `str \| None` | Optional human-readable status message. |
| `context` | `CallbackContext` | Server and tool metadata. |

### Client Example

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext

async def on_progress(
    progress: float,
    total: float | None,
    message: str | None,
    context: CallbackContext,
) -> None:
    if total is not None:
        percent = (progress / total) * 100
        print(f"[{context.server_name}] {percent:.1f}% - {message or ''}")
    else:
        print(f"[{context.server_name}] Progress: {progress} - {message or ''}")

client = MultiServerMCPClient(
    {"processor": {"transport": "http", "url": "http://localhost:8000/mcp"}},
    callbacks=Callbacks(on_progress=on_progress),
)
tools = await client.get_tools()
```

### Server-Side Progress Reporting

Servers report progress using the context object:

```python
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("Processor")

@mcp.tool()
async def process_files(file_count: int, ctx: Context) -> str:
    """Process multiple files with progress reporting."""
    for i in range(file_count):
        await ctx.report_progress(i + 1, file_count, f"Processing file {i + 1}")
    return f"Processed {file_count} files"
```

---

## Logging

MCP servers can send log messages at various severity levels. The `on_logging_message` handler receives these as structured notifications.

### Handler Signature

```python
from mcp.types import LoggingMessageNotificationParams

async def on_logging_message(
    params: LoggingMessageNotificationParams,
    context: CallbackContext,
) -> None:
```

### LoggingMessageNotificationParams Fields

| Field | Type | Description |
|-------|------|-------------|
| `level` | `str` | Log level (see table below). |
| `logger` | `str \| None` | Logger name from the server. |
| `data` | `Any` | Log message content (string or structured data). |

### Log Levels (RFC 5424)

| Level | Severity | Description |
|-------|----------|-------------|
| `"emergency"` | 0 | System is unusable |
| `"alert"` | 1 | Action must be taken immediately |
| `"critical"` | 2 | Critical conditions |
| `"error"` | 3 | Error conditions |
| `"warning"` | 4 | Warning conditions |
| `"notice"` | 5 | Normal but significant conditions |
| `"info"` | 6 | Informational messages |
| `"debug"` | 7 | Debug-level messages |

### Client Example

Bridge MCP log messages to Python's `logging` module:

```python
import logging
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext
from mcp.types import LoggingMessageNotificationParams

logger = logging.getLogger("mcp")

MCP_TO_PYTHON_LEVEL = {
    "emergency": logging.CRITICAL,
    "alert": logging.CRITICAL,
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "notice": logging.INFO,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}

async def on_logging_message(
    params: LoggingMessageNotificationParams,
    context: CallbackContext,
) -> None:
    level = MCP_TO_PYTHON_LEVEL.get(params.level, logging.INFO)
    logger.log(
        level,
        "[%s] %s: %s",
        context.server_name,
        params.logger or "default",
        params.data,
    )

client = MultiServerMCPClient(
    {"service": {"transport": "http", "url": "http://localhost:8000/mcp"}},
    callbacks=Callbacks(on_logging_message=on_logging_message),
)
```

### Server-Side Logging

Servers send log messages using the context object:

```python
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("Service")

@mcp.tool()
async def process_data(query: str, ctx: Context) -> str:
    """Process data with logging."""
    await ctx.log("info", f"Processing query: {query}")
    # ... processing ...
    await ctx.log("debug", f"Query completed in 0.5s")
    return "Done"
```

---

## Elicitation

Elicitation allows MCP servers to request additional input from the client during tool execution. The server pauses, sends a structured request with a Pydantic schema, and waits for the client to respond.

### Server Setup

Servers use `ctx.elicit()` with a Pydantic model to request structured input:

```python
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP, Context

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
        return f"Created profile: {name}, email={result.data.email}, age={result.data.age}"
    if result.action == "decline":
        return f"User declined. Created minimal profile for {name}."
    return "Profile creation cancelled."

if __name__ == "__main__":
    server.run(transport="http")
```

### Multi-Step Elicitation

Servers can elicit multiple times within a single tool call:

```python
class ShippingAddress(BaseModel):
    street: str
    city: str
    zip_code: str

class PaymentMethod(BaseModel):
    card_type: str
    last_four: str

@server.tool()
async def checkout(ctx: Context) -> str:
    """Multi-step checkout with elicitation."""
    address = await ctx.elicit(
        message="Enter shipping address:",
        schema=ShippingAddress,
    )
    if address.action != "accept":
        return "Checkout cancelled at address step."

    payment = await ctx.elicit(
        message="Enter payment details:",
        schema=PaymentMethod,
    )
    if payment.action != "accept":
        return "Checkout cancelled at payment step."

    return f"Order placed to {address.data.city} with card ending {payment.data.last_four}"
```

### Client Setup

The client provides an `on_elicitation` callback that receives the request and returns an `ElicitResult`:

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
    """Handle elicitation requests from the server."""
    return ElicitResult(
        action="accept",
        content={"email": "user@example.com", "age": 30},
    )

client = MultiServerMCPClient(
    {"profile": {"transport": "http", "url": "http://localhost:8000/mcp"}},
    callbacks=Callbacks(on_elicitation=on_elicitation),
)
tools = await client.get_tools()
```

### Handler Signature

```python
async def on_elicitation(
    mcp_context: RequestContext,
    params: ElicitRequestParams,
    context: CallbackContext,
) -> ElicitResult:
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `mcp_context` | `RequestContext` | MCP protocol context for the request. |
| `params` | `ElicitRequestParams` | Contains `message` (str) and `requestedSchema` (JSON Schema). |
| `context` | `CallbackContext` | Server and tool metadata. |

### Response Actions

The `ElicitResult` supports three actions:

| Action | Description | `content` field |
|--------|-------------|-----------------|
| `"accept"` | Accept and provide the requested data. | Dict matching the requested schema. |
| `"decline"` | Decline to provide data (server can use fallback logic). | Optional — usually omitted. |
| `"cancel"` | Cancel the entire tool operation. | Optional — usually omitted. |

```python
# Accept with data
ElicitResult(action="accept", content={"email": "user@example.com", "age": 30})

# Decline (server decides what to do)
ElicitResult(action="decline")

# Cancel the operation entirely
ElicitResult(action="cancel")
```

### Interactive Elicitation Example

A client that prompts the user interactively in the terminal:

```python
import json

async def interactive_elicitation(
    mcp_context: RequestContext,
    params: ElicitRequestParams,
    context: CallbackContext,
) -> ElicitResult:
    """Prompt the user in the terminal for elicitation data."""
    print(f"\n[{context.server_name}] Server requests input:")
    print(f"  Message: {params.message}")
    print(f"  Schema: {json.dumps(params.requestedSchema, indent=2)}")

    response = input("Provide data as JSON (or 'decline'/'cancel'): ").strip()

    if response == "decline":
        return ElicitResult(action="decline")
    if response == "cancel":
        return ElicitResult(action="cancel")

    try:
        data = json.loads(response)
        return ElicitResult(action="accept", content=data)
    except json.JSONDecodeError:
        print("Invalid JSON. Declining.")
        return ElicitResult(action="decline")
```

---

## Quick Template

A complete example combining all three callback types:

```python
import logging
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext
from mcp.types import LoggingMessageNotificationParams, ElicitRequestParams, ElicitResult
from mcp.shared.context import RequestContext

logger = logging.getLogger("mcp")

async def on_progress(progress, total, message, context):
    pct = f"{(progress/total*100):.0f}%" if total else f"{progress}"
    print(f"[{context.server_name}] {pct} {message or ''}")

async def on_logging_message(params, context):
    logger.info("[%s] %s: %s", context.server_name, params.level, params.data)

async def on_elicitation(mcp_context, params, context):
    # Auto-decline all elicitation requests
    return ElicitResult(action="decline")

client = MultiServerMCPClient(
    {
        "service": {
            "transport": "http",
            "url": "http://localhost:8000/mcp",
        },
    },
    callbacks=Callbacks(
        on_progress=on_progress,
        on_logging_message=on_logging_message,
        on_elicitation=on_elicitation,
    ),
)
tools = await client.get_tools()
```

---

## Import Reference

```python
# Callbacks and context
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext

# MCP types for logging and elicitation
from mcp.types import LoggingMessageNotificationParams
from mcp.types import ElicitRequestParams, ElicitResult
from mcp.shared.context import RequestContext
```

---

## Documentation Links

- **MCP Integration Guide**: [https://docs.langchain.com/oss/python/langchain/mcp](https://docs.langchain.com/oss/python/langchain/mcp)
  - Progress notifications, logging, and elicitation sections
- **API Reference**: [https://reference.langchain.com/python/langchain_mcp_adapters/](https://reference.langchain.com/python/langchain_mcp_adapters/)
  - Callbacks dataclass and CallbackContext documentation
