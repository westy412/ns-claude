# langchain-mcp-adapters -- Resources & Prompts Reference

How to load MCP resources as LangChain Blob objects and MCP prompts as LangChain messages.

## Resources

MCP servers can expose data (files, database records, API responses) as resources. The adapter converts these into LangChain `Blob` objects.

### get_resources (Client Method)

The convenience method on `MultiServerMCPClient` for loading resources.

```python
async def get_resources(
    self,
    server_name: str | None = None,
    *,
    uris: str | list[str] | None = None,
) -> list[Blob]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `server_name` | `str \| None` | `None` | Server to load resources from. If `None`, loads from all servers. |
| `uris` | `str \| list[str] \| None` | `None` | Specific resource URIs to fetch. If `None`, loads all static resources (dynamic resources are skipped). |

> **Important:** When `uris` is `None`, dynamic resources (template-based URIs) are NOT loaded. You must provide explicit URIs to fetch dynamic resources.

#### Load All Static Resources from a Server

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "files": {
        "transport": "stdio",
        "command": "python",
        "args": ["./file_server.py"],
    },
})

blobs = await client.get_resources("files")
for blob in blobs:
    print(f"URI: {blob.metadata['uri']}, MIME: {blob.mimetype}")
    print(blob.as_string())
```

#### Load Specific Resources by URI

```python
blobs = await client.get_resources(
    "files",
    uris=["file:///path/to/readme.md", "file:///path/to/config.json"],
)
```

#### Load from All Servers

```python
# Loads static resources from every connected server
all_blobs = await client.get_resources()
```

---

### load_mcp_resources (Standalone Function)

For use with an explicit `ClientSession` when you need direct session control.

```python
from langchain_mcp_adapters.resources import load_mcp_resources

async def load_mcp_resources(
    session: ClientSession,
    *,
    uris: str | list[str] | None = None,
) -> list[Blob]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session` | `ClientSession` | required | An active, initialized MCP client session. |
| `uris` | `str \| list[str] \| None` | `None` | Specific resource URIs to fetch. If `None`, loads all static resources. |

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.resources import load_mcp_resources

client = MultiServerMCPClient({
    "files": {
        "transport": "stdio",
        "command": "python",
        "args": ["./file_server.py"],
    },
})

async with client.session("files") as session:
    # Load all static resources
    blobs = await load_mcp_resources(session)

    # Load specific resources
    blobs = await load_mcp_resources(
        session,
        uris=["file:///path/to/file.txt"],
    )
```

---

### Blob Objects

Resources are returned as LangChain `Blob` objects. Key fields and methods:

| Field/Method | Type | Description |
|-------------|------|-------------|
| `data` | `bytes \| str \| None` | The raw content (text or binary). |
| `mimetype` | `str \| None` | MIME type (e.g., `"text/plain"`, `"application/json"`). |
| `encoding` | `str` | Text encoding (default `"utf-8"`). |
| `path` | `str \| None` | Original path if applicable. |
| `metadata` | `dict` | Contains `uri` key with the MCP resource URI. |
| `as_string()` | `str` | Returns content decoded as text. |
| `as_bytes()` | `bytes` | Returns raw bytes. |
| `as_bytes_io()` | `BytesIO` | Returns a BytesIO stream. |

```python
for blob in blobs:
    # Access metadata
    uri = blob.metadata["uri"]
    mime = blob.mimetype

    # Read content
    text_content = blob.as_string()
    raw_bytes = blob.as_bytes()

    # Stream content
    stream = blob.as_bytes_io()
```

### Static vs Dynamic Resources

MCP servers expose two kinds of resources:

| Type | Description | `uris=None` behavior |
|------|-------------|---------------------|
| **Static** | Fixed URIs (e.g., `file:///config.json`) | Loaded automatically |
| **Dynamic** | Template URIs (e.g., `user://{user_id}/profile`) | **NOT loaded** -- must provide resolved URIs |

To fetch dynamic resources, resolve the template URI first and pass it explicitly:

```python
# Dynamic resource -- must provide the resolved URI
blobs = await client.get_resources(
    "users",
    uris=["user://42/profile"],
)
```

---

## Prompts

MCP servers can expose reusable prompt templates. The adapter converts these into LangChain message objects (`HumanMessage` or `AIMessage`).

### get_prompt (Client Method)

```python
async def get_prompt(
    self,
    server_name: str,
    prompt_name: str,
    *,
    arguments: dict[str, Any] | None = None,
) -> list[HumanMessage | AIMessage]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `server_name` | `str` | required | The server exposing the prompt. |
| `prompt_name` | `str` | required | Name of the prompt template. |
| `arguments` | `dict[str, Any] \| None` | `None` | Arguments to pass to the prompt template. |

#### Basic Usage

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "assistant": {
        "transport": "http",
        "url": "http://localhost:8000/mcp",
    },
})

# Load a prompt without arguments
messages = await client.get_prompt("assistant", "summarize")

# Load a prompt with arguments
messages = await client.get_prompt(
    "assistant",
    "code_review",
    arguments={"language": "python", "focus": "security"},
)
```

---

### load_mcp_prompt (Standalone Function)

For use with an explicit `ClientSession`.

```python
from langchain_mcp_adapters.prompts import load_mcp_prompt

async def load_mcp_prompt(
    session: ClientSession,
    name: str,
    *,
    arguments: dict[str, Any] | None = None,
) -> list[HumanMessage | AIMessage]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `session` | `ClientSession` | required | An active, initialized MCP client session. |
| `name` | `str` | required | Name of the prompt template. |
| `arguments` | `dict[str, Any] \| None` | `None` | Arguments to pass to the prompt template. |

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.prompts import load_mcp_prompt

client = MultiServerMCPClient({
    "assistant": {
        "transport": "http",
        "url": "http://localhost:8000/mcp",
    },
})

async with client.session("assistant") as session:
    messages = await load_mcp_prompt(
        session,
        "code_review",
        arguments={"language": "python", "focus": "security"},
    )
```

---

### Message Type Mapping

MCP prompt messages are converted to LangChain message types:

| MCP Role | LangChain Message Type |
|----------|----------------------|
| `"user"` | `HumanMessage` |
| `"assistant"` | `AIMessage` |

### Using Prompts in Chains

Prompt messages can be combined with user input and passed to an LLM:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

client = MultiServerMCPClient({
    "assistant": {
        "transport": "http",
        "url": "http://localhost:8000/mcp",
    },
})

model = init_chat_model("openai:gpt-4.1")

# Load a system/context prompt from the server
prompt_messages = await client.get_prompt(
    "assistant",
    "code_review",
    arguments={"language": "python", "focus": "security"},
)

# Append user input
all_messages = prompt_messages + [
    HumanMessage(content="Review this function:\n\ndef login(user, pw):\n    return db.query(f'SELECT * FROM users WHERE name={user} AND pass={pw}')")
]

# Send to model
response = await model.ainvoke(all_messages)
print(response.content)
```

---

## Import Reference

```python
# Client method (resources and prompts via MultiServerMCPClient)
from langchain_mcp_adapters.client import MultiServerMCPClient

# Standalone functions for explicit session usage
from langchain_mcp_adapters.resources import load_mcp_resources
from langchain_mcp_adapters.prompts import load_mcp_prompt

# Message types returned by prompt loading
from langchain_core.messages import HumanMessage, AIMessage

# Blob type returned by resource loading
from langchain_core.document_loaders import Blob
```

---

## Best Practices

### Session Management
Use explicit sessions (`client.session()`) when you need stateful interactions or lifecycle control. The standalone functions (`load_mcp_resources`, `load_mcp_prompt`) require an active session, while the client methods (`get_resources`, `get_prompt`) handle session management automatically.

### URI Filtering
Specify the `uris` parameter to load only the resources you need. This is more efficient than loading all resources and filtering afterward. For dynamic resources, you must provide explicit URIs.

### Error Handling
Wrap resource and prompt loading in try-except blocks for production use. Both `load_mcp_resources` and the client methods can raise `RuntimeError` if fetching fails.

```python
try:
    blobs = await client.get_resources("server_name", uris=["file:///config.json"])
except RuntimeError as e:
    print(f"Failed to load resources: {e}")
```

### Template Arguments
Validate that prompt arguments match the server's expected schema. Providing incorrect or missing arguments may cause the prompt loading to fail or produce unexpected results.

```python
# Ensure arguments match the prompt template's schema
messages = await client.get_prompt(
    "assistant",
    "code_review",
    arguments={"language": "python", "focus": "security"},  # Must match template
)
```

---

## Documentation Links

- [LangChain MCP Integration Guide](https://docs.langchain.com/oss/python/langchain/mcp) - Official guide covering resources and prompts
- [langchain-mcp-adapters API Reference](https://reference.langchain.com/python/langchain_mcp_adapters/) - Complete API documentation
