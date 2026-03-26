# langchain-mcp-adapters -- Tool Interceptors Reference

Tool interceptors are async middleware functions that wrap MCP tool execution. They provide runtime context access, request/response modification, and agent state control. Each interceptor follows a handler callback pattern: receive a request, optionally modify it, call the next handler, and optionally modify the result.

## Overview

An interceptor is any async callable matching the `ToolCallInterceptor` protocol. It receives two arguments: the incoming `MCPToolCallRequest` and a `handler` callback representing the next step in the chain (either another interceptor or the actual tool execution). The interceptor can inspect or modify the request before calling the handler, inspect or modify the result afterward, skip the handler entirely (short-circuit), or call the handler multiple times (retry).

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

async def my_interceptor(request, handler):
    # Pre-processing: inspect or modify request
    # ...

    result = await handler(request)

    # Post-processing: inspect or modify result
    # ...
    return result

client = MultiServerMCPClient(
    {
        "weather": {
            "url": "http://localhost:8080/mcp",
            "transport": "streamable_http",
        }
    },
    tool_interceptors=[my_interceptor],
)
```

---

## Basic Interceptors

### The ToolCallInterceptor Protocol

Every interceptor must satisfy this protocol signature:

```python
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from typing import Callable, Awaitable

async def interceptor(
    request: MCPToolCallRequest,
    handler: Callable[[MCPToolCallRequest], Awaitable],
) -> any:  # Returns MCPToolCallResult (ToolMessage or Command)
    ...
```

The `handler` parameter is the next callable in the interceptor chain. When called, it either invokes the next interceptor or executes the underlying MCP tool if no interceptors remain.

Key properties of the handler:

- **Can be called multiple times** -- enables retry logic.
- **Can be skipped entirely** -- enables caching or short-circuit responses.
- **Can be wrapped in error handling** -- enables fallback behavior.
- **Each handler call is independent** -- no shared mutable state between invocations.

### Minimal Pass-Through Interceptor

The simplest interceptor does nothing but forward the request:

```python
async def passthrough_interceptor(request, handler):
    return await handler(request)
```

### Logging Interceptor

```python
import logging

logger = logging.getLogger("mcp.tools")

async def logging_interceptor(request, handler):
    logger.info(
        "Tool call: %s | server: %s | args: %s",
        request.name,
        request.server_name,
        request.args,
    )
    result = await handler(request)
    logger.info("Tool result: %s | %s", request.name, result)
    return result
```

---

## Runtime Context

The `request.runtime` object exposes four fields that give interceptors access to the broader agent environment.

### runtime.context -- Configuration Values

Read-only configuration injected at agent construction time. Use this for API keys, user identifiers, and other values that remain stable across the session.

```python
async def auth_from_context(request, handler):
    user_id = request.runtime.context.user_id
    api_key = request.runtime.context.api_key

    modified = request.override(
        args={**request.args, "user_id": user_id},
        headers={"Authorization": f"Bearer {api_key}"},
    )
    return await handler(modified)
```

### runtime.store -- Long-Term Memory

Access to the LangGraph Store for persistent, cross-session data such as user preferences or cached results.

```python
async def preference_interceptor(request, handler):
    store = request.runtime.store
    user_id = request.runtime.context.user_id

    prefs = store.get(("preferences",), user_id)
    if prefs and prefs.value.get("language"):
        modified = request.override(
            args={**request.args, "language": prefs.value["language"]},
        )
        return await handler(modified)

    return await handler(request)
```

### runtime.state -- Conversation State

Access to the current agent state dictionary. This is the mutable state that persists within the current conversation turn or graph execution.

```python
async def check_auth_state(request, handler):
    is_authenticated = request.runtime.state.get("authenticated", False)

    if request.name in ("delete_record", "update_record") and not is_authenticated:
        from langchain_core.messages import ToolMessage
        return ToolMessage(
            content="Error: authentication required for this operation.",
            tool_call_id=request.runtime.tool_call_id,
        )

    return await handler(request)
```

### runtime.tool_call_id -- Message Correlation

The unique identifier for the current tool call. Required when constructing `ToolMessage` responses manually (for example, when short-circuiting without calling the handler).

```python
from langchain_core.messages import ToolMessage

async def rate_limit_interceptor(request, handler):
    if is_rate_limited(request.name):
        return ToolMessage(
            content=f"Tool '{request.name}' is temporarily rate limited. Try again shortly.",
            tool_call_id=request.runtime.tool_call_id,
        )
    return await handler(request)
```

---

## Modifying Requests

Use `request.override()` to produce a new, immutable request with modified fields. The original request is never mutated.

### Signature

```python
modified_request = request.override(
    args=...,       # dict -- replacement tool arguments
    headers=...,    # dict -- replacement or additional HTTP headers
)
```

### Injecting Arguments

```python
async def inject_tenant(request, handler):
    tenant_id = request.runtime.context.tenant_id
    modified = request.override(
        args={**request.args, "tenant_id": tenant_id},
    )
    return await handler(modified)
```

### Setting Headers

```python
async def dynamic_auth_headers(request, handler):
    token = await get_token_for_server(request.server_name)
    modified = request.override(
        headers={"Authorization": f"Bearer {token}"},
    )
    return await handler(modified)
```

### Sanitizing Arguments

```python
async def sanitize_inputs(request, handler):
    cleaned_args = {
        k: sanitize(v) if isinstance(v, str) else v
        for k, v in request.args.items()
    }
    return await handler(request.override(args=cleaned_args))
```

---

## Modifying Responses

Interceptors can transform, replace, or augment the result returned by the handler.

### Transforming Tool Output

```python
async def redact_pii(request, handler):
    result = await handler(request)

    if isinstance(result, ToolMessage):
        redacted_content = pii_redactor.redact(result.content)
        return ToolMessage(
            content=redacted_content,
            tool_call_id=result.tool_call_id,
        )

    return result
```

### Replacing Output on Error

```python
from langchain_core.messages import ToolMessage

async def graceful_error_interceptor(request, handler):
    try:
        return await handler(request)
    except TimeoutError:
        return ToolMessage(
            content=f"Tool '{request.name}' timed out. The remote server may be unavailable.",
            tool_call_id=request.runtime.tool_call_id,
        )
    except ConnectionError:
        return ToolMessage(
            content="Connection failed. Please check the MCP server status.",
            tool_call_id=request.runtime.tool_call_id,
        )
```

### Enriching Output

```python
import time

async def timing_interceptor(request, handler):
    start = time.perf_counter()
    result = await handler(request)
    elapsed = time.perf_counter() - start

    if isinstance(result, ToolMessage):
        enriched = f"{result.content}\n\n[Execution time: {elapsed:.2f}s]"
        return ToolMessage(
            content=enriched,
            tool_call_id=result.tool_call_id,
        )
    return result
```

---

## State Updates with Command

Return a `Command` object instead of a plain result to update agent state or redirect graph execution flow. This integrates with LangGraph's state management.

### Command Fields

| Field | Type | Purpose |
|-------|------|---------|
| `update` | `dict` | Merge these key-value pairs into the agent state. Must include the tool result in `messages` so the agent receives it. |
| `goto` | `str` | Transition to a named node in the graph. Use `"__end__"` to terminate execution. |

### Updating State After a Tool Call

```python
from langgraph.types import Command

async def track_order_status(request, handler):
    result = await handler(request)

    if request.name == "submit_order":
        return Command(
            update={
                "messages": [result],
                "order_submitted": True,
                "task_status": "completed",
            },
        )

    return result
```

### Redirecting Graph Flow

```python
from langgraph.types import Command

async def route_on_completion(request, handler):
    result = await handler(request)

    if request.name == "finalize_report":
        return Command(
            update={"messages": [result]},
            goto="summary_agent",
        )

    if request.name == "cancel_task":
        return Command(
            update={
                "messages": [result],
                "cancelled": True,
            },
            goto="__end__",
        )

    return result
```

### Conditional State Transition

```python
from langgraph.types import Command

async def escalation_interceptor(request, handler):
    result = await handler(request)

    if request.name == "analyze_ticket":
        content = result.content if hasattr(result, "content") else str(result)

        if "critical" in content.lower():
            return Command(
                update={
                    "messages": [result],
                    "severity": "critical",
                },
                goto="escalation_agent",
            )

    return result
```

---

## Composition Order

Interceptors compose in **onion order**: the first interceptor in the list is the outermost layer, and the last interceptor is the innermost layer (closest to the actual tool execution).

```
tool_interceptors = [outer, middle, inner]

Execution flow:

outer (pre-processing)
  -> middle (pre-processing)
       -> inner (pre-processing)
            -> MCP tool execution
       <- inner (post-processing)
  <- middle (post-processing)
<- outer (post-processing)
```

### Implications

- **Pre-processing** runs top-to-bottom (first interceptor runs first).
- **Post-processing** runs bottom-to-top (last interceptor returns first, outermost interceptor returns last).
- An outer interceptor can short-circuit the entire chain by not calling `handler`.
- An inner interceptor sees any modifications made by outer interceptors.

### Example: Layered Composition

```python
async def auth_interceptor(request, handler):
    """Outermost: inject auth before anything else."""
    token = await get_auth_token()
    modified = request.override(
        headers={"Authorization": f"Bearer {token}"},
    )
    return await handler(modified)

async def cache_interceptor(request, handler):
    """Middle: return cached result if available, skip inner layers."""
    cache_key = f"{request.name}:{hash(str(request.args))}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached  # Short-circuits: inner interceptor and tool never run.

    result = await handler(request)
    cache.set(cache_key, result, ttl=300)
    return result

async def error_interceptor(request, handler):
    """Innermost: catch tool errors, closest to actual execution."""
    try:
        return await handler(request)
    except Exception as e:
        return ToolMessage(
            content=f"Tool error: {e}",
            tool_call_id=request.runtime.tool_call_id,
        )

# Registration order determines nesting
client = MultiServerMCPClient(
    {"service": {"url": "http://localhost:8080/mcp", "transport": "streamable_http"}},
    tool_interceptors=[auth_interceptor, cache_interceptor, error_interceptor],
)
```

In this configuration:

1. `auth_interceptor` runs first, injecting headers.
2. `cache_interceptor` checks the cache. On a cache hit, `error_interceptor` and the tool never execute.
3. `error_interceptor` catches exceptions from the tool itself if no cache hit occurred.

---

## Practical Examples

### Caching with TTL

```python
import time
from langchain_core.messages import ToolMessage

_cache: dict[str, tuple[float, MCPToolCallResult]] = {}
CACHE_TTL = 120  # seconds

async def caching_interceptor(request, handler):
    # Only cache read-only tools
    if request.name not in ("search", "get_weather", "lookup_user"):
        return await handler(request)

    cache_key = f"{request.name}:{repr(sorted(request.args.items()))}"
    now = time.time()

    if cache_key in _cache:
        cached_at, cached_result = _cache[cache_key]
        if now - cached_at < CACHE_TTL:
            return cached_result

    result = await handler(request)
    _cache[cache_key] = (now, result)
    return result
```

### Retry with Exponential Backoff

```python
import asyncio
from langchain_core.messages import ToolMessage

async def retry_interceptor(request, handler):
    max_retries = 3
    last_error = None

    for attempt in range(max_retries):
        try:
            return await handler(request)
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                delay = 1.0 * (2 ** attempt)  # 1s, 2s, 4s
                await asyncio.sleep(delay)

    return ToolMessage(
        content=f"Tool '{request.name}' failed after {max_retries} attempts: {last_error}",
        tool_call_id=request.runtime.tool_call_id,
    )
```

### Conditional Tool Blocking

```python
from langchain_core.messages import ToolMessage

SENSITIVE_TOOLS = {"delete_file", "drop_table", "send_email"}

async def permission_gate(request, handler):
    if request.name in SENSITIVE_TOOLS:
        role = request.runtime.state.get("user_role", "viewer")
        if role not in ("admin", "editor"):
            return ToolMessage(
                content=f"Permission denied: '{request.name}' requires admin or editor role.",
                tool_call_id=request.runtime.tool_call_id,
            )
    return await handler(request)
```

### Per-Server Header Injection

```python
SERVER_TOKENS = {
    "github": "ghp_xxxxxxxxxxxx",
    "jira": "jira_token_yyyy",
    "slack": "xoxb-zzzzzzzzzz",
}

async def per_server_auth(request, handler):
    token = SERVER_TOKENS.get(request.server_name)
    if token:
        modified = request.override(
            headers={"Authorization": f"Bearer {token}"},
        )
        return await handler(modified)
    return await handler(request)
```

### Audit Trail

```python
import datetime
from langgraph.types import Command

async def audit_trail_interceptor(request, handler):
    result = await handler(request)

    audit_entry = {
        "tool": request.name,
        "server": request.server_name,
        "args": request.args,
        "user": request.runtime.context.user_id,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    existing_log = request.runtime.state.get("audit_log", [])

    return Command(
        update={
            "messages": [result],
            "audit_log": existing_log + [audit_entry],
        },
    )
```

### Full Multi-Interceptor Registration

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "github": {
            "url": "http://localhost:3001/mcp",
            "transport": "streamable_http",
        },
        "database": {
            "url": "http://localhost:3002/mcp",
            "transport": "streamable_http",
        },
    },
    tool_interceptors=[
        logging_interceptor,      # Outermost: log everything
        per_server_auth,          # Inject server-specific tokens
        permission_gate,          # Block unauthorized calls
        caching_interceptor,      # Return cached results when available
        retry_interceptor,        # Innermost: retry on transient failures
    ],
)

tools = await client.get_tools()
```

---

## Anti-Patterns

```python
# WRONG: Mutating the request directly instead of using override()
async def bad_mutate(request, handler):
    request.args["extra"] = "value"  # Do not mutate; use request.override()
    return await handler(request)

# WRONG: Forgetting to return the result
async def bad_swallow(request, handler):
    await handler(request)
    # Missing: return statement -- agent receives None

# WRONG: Returning Command without including messages
async def bad_command(request, handler):
    result = await handler(request)
    return Command(
        update={"status": "done"},  # Missing "messages": [result]
        goto="next_node",
    )

# WRONG: Blocking the event loop with synchronous I/O
async def bad_blocking(request, handler):
    import requests
    resp = requests.get("https://api.example.com/check")  # Use aiohttp or httpx instead
    return await handler(request)
```

---

## Documentation Links

- [LangChain MCP Documentation - Tool Interceptors](https://docs.langchain.com/oss/python/langchain/mcp)
- [LangChain MCP Adapters API Reference](https://reference.langchain.com/python/langchain_mcp_adapters/)
