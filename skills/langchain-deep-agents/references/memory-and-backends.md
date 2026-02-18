# Memory and Backends

Deep agent tools operate on virtual file systems. Every agent has a backend that determines where files are stored and how long they persist.

---

## Backend Overview

| Backend | Persistence | Scope | Primary Use |
|---------|-------------|-------|-------------|
| `StateBackend` | Ephemeral | Single thread | Default; scratch work |
| `FilesystemBackend` | Local disk | Machine-wide | Direct local file access |
| `StoreBackend` | Cross-thread | All threads (via Store) | Long-term memory |
| `CompositeBackend` | Mixed | Configurable per path | Short-term + long-term combined |

---

## StateBackend (Default)

Ephemeral filesystem in LangGraph state. Persists only for a single thread.

```python
agent = create_deep_agent()

# Equivalent:
from deepagents.backends import StateBackend
agent = create_deep_agent(backend=(lambda rt: StateBackend(rt)))
```

---

## FilesystemBackend

Direct read/write access to the local filesystem. Use with caution.

```python
from deepagents.backends import FilesystemBackend
agent = create_deep_agent(backend=FilesystemBackend(root_dir=".", virtual_mode=True))
```

- `virtual_mode=True`: Sandboxes paths — blocks `..`, `~`, and absolute paths outside `root_dir`; prevents symlink traversal
- `virtual_mode=False` (default): **No security even with `root_dir` set**
- **Always use `virtual_mode=True`** and scope `root_dir` tightly

> **Security warnings:** FilesystemBackend grants direct read/write access. Agents can read secrets (API keys, `.env` files). Combined with network tools, this enables SSRF/exfiltration. Modifications are permanent. Appropriate for local dev CLIs and CI/CD pipelines. **Not appropriate for web servers or HTTP APIs.** Use Human-in-the-Loop middleware and sandbox backends for production.

---

## StoreBackend

Long-term storage persisted across threads.

```python
from langgraph.store.memory import InMemoryStore
from deepagents.backends import StoreBackend
agent = create_deep_agent(backend=(lambda rt: StoreBackend(rt)), store=InMemoryStore())
```

On LangSmith Deployment, omit `store` -- the platform provides one.

---

## CompositeBackend

Routes paths to different backends. Recommended for agents needing both scratch space and persistent memory.

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

composite_backend = lambda rt: CompositeBackend(
    default=StateBackend(rt),
    routes={"/memories/": StoreBackend(rt)}
)
agent = create_deep_agent(backend=composite_backend, store=InMemoryStore())
```

**Path routing:** `/memories/` prefix routes to StoreBackend. Everything else goes to StateBackend. Longer prefixes override shorter ones. CompositeBackend strips the route prefix before storing (`/memories/preferences.txt` stored as `/preferences.txt`). Query operations (`ls`, `glob`, `grep`) aggregate results across backends and preserve original prefixed paths.

---

## Memory Parameter

The `memory` parameter on `create_deep_agent` specifies virtual file paths (typically AGENTS.md files) that provide persistent context to the agent. How you populate those files depends on the backend:

**StateBackend** — pass files at invoke time:
```python
from deepagents.backends.utils import create_file_data

agent = create_deep_agent(
    memory=["/AGENTS.md"],
    checkpointer=MemorySaver(),
)

result = agent.invoke(
    {
        "messages": [{"role": "user", "content": "..."}],
        "files": {"/AGENTS.md": create_file_data(agents_md)},
    },
    config={"configurable": {"thread_id": "123456"}},
)
```

**StoreBackend** — pre-populate the store:
```python
store = InMemoryStore()
store.put(
    namespace=("filesystem",),
    key="/AGENTS.md",
    value=create_file_data(agents_md)
)

agent = create_deep_agent(
    backend=(lambda rt: StoreBackend(rt)),
    store=store,
    memory=["/AGENTS.md"]
)
```

**FilesystemBackend** — point to a local file:
```python
agent = create_deep_agent(
    backend=FilesystemBackend(root_dir="/path/to/project"),
    memory=["./AGENTS.md"],
    checkpointer=MemorySaver(),
)
```

---

## Long-Term Memory Setup

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()

def make_backend(runtime):
    return CompositeBackend(
        default=StateBackend(runtime),
        routes={"/memories/": StoreBackend(runtime)}
    )

agent = create_deep_agent(
    store=InMemoryStore(),
    backend=make_backend,
    checkpointer=checkpointer
)
```

---

## Cross-Thread Persistence

```python
import uuid

# Thread 1: save preferences
config1 = {"configurable": {"thread_id": str(uuid.uuid4())}}
agent.invoke(
    {"messages": [{"role": "user", "content": "Save my preferences to /memories/preferences.txt"}]},
    config=config1
)

# Thread 2: read preferences (different thread)
config2 = {"configurable": {"thread_id": str(uuid.uuid4())}}
agent.invoke(
    {"messages": [{"role": "user", "content": "What are my preferences?"}]},
    config=config2
)
```

---

## Accessing Memories Externally (LangSmith)

StoreBackend uses namespace `(assistant_id, "filesystem")`. Keys do **not** include the `/memories/` prefix due to CompositeBackend's route-stripping behavior.

```python
from langgraph_sdk import get_client
client = get_client(url="<DEPLOYMENT_URL>")

# Read
item = await client.store.get_item((assistant_id, "filesystem"), "/preferences.txt")

# Write
await client.store.put_item((assistant_id, "filesystem"), "/preferences.txt", {
    "content": ["line 1", "line 2"],
    "created_at": "2024-01-15T10:30:00Z",
    "modified_at": "2024-01-15T10:30:00Z"
})

# Search
items = await client.store.search_items((assistant_id, "filesystem"))
```

---

## FileData Schema

```python
{"content": ["line 1", "line 2"], "created_at": "...", "modified_at": "..."}

# Helper:
from deepagents.backends.utils import create_file_data
file_data = create_file_data("Hello\nWorld")
```

---

## Store Implementations

| Store | Persistence | Use Case |
|-------|-------------|----------|
| `InMemoryStore` | None (lost on restart) | Development |
| `PostgresStore` | Durable | Production |

```python
# Development
from langgraph.store.memory import InMemoryStore
store = InMemoryStore()

# Production
from langgraph.store.postgres import PostgresStore
store_ctx = PostgresStore.from_conn_string(os.environ["DATABASE_URL"])
store = store_ctx.__enter__()
store.setup()
```

---

## Use Cases

| Pattern | Memory Path | Description |
|---------|-------------|-------------|
| User preferences | `/memories/user_preferences.txt` | Settings across sessions |
| Self-improving instructions | `/memories/instructions.txt` | Agent updates own instructions |
| Knowledge base | `/memories/knowledge/` | Accumulated knowledge |
| Research projects | `/memories/research/` | State across sessions |

---

## Best Practices

- Use descriptive paths: `/memories/research/topic_a/sources.txt`
- Document memory structure in the system prompt
- Prune old data periodically
- `InMemoryStore` for dev, `PostgresStore` for production
- Omit `store` on LangSmith Deployment

---

## Documentation Links

- [Backends overview](https://docs.langchain.com/oss/python/deepagents/backends)
- [Long-term memory guide](https://docs.langchain.com/oss/python/deepagents/long-term-memory)
- [Customization guide](https://docs.langchain.com/oss/python/deepagents/customization)
- [Store API reference](https://docs.langchain.com/oss/python/deepagents/store-api)
