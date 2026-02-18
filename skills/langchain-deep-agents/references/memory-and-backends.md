# Memory and Backends

Deep agent tools operate on virtual file systems. Every agent has a backend that determines where files are stored and how long they persist.

---

## Backend Overview

| Backend | Storage | Persistence | Security | Use Case |
|---------|---------|-------------|----------|----------|
| **StateBackend** | LangGraph state | Ephemeral (thread-local) | Safe | Default; development, simple tasks |
| **FilesystemBackend** | Real disk | Permanent | Risky | CLI tools, sandboxed environments |
| **StoreBackend** | LangGraph BaseStore | Cross-thread persistent | Safe | Long-term memory, user preferences |
| **CompositeBackend** | Routes to others | Mixed | Depends on config | Short-term + long-term combined |

---

## StateBackend (Default)

Ephemeral filesystem in LangGraph state. Persists only for a single thread.

```python
from deepagents import create_deep_agent

# StateBackend is the default - no configuration needed
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
)

# Explicit configuration (equivalent to default)
from deepagents.backends import StateBackend

agent = create_deep_agent(
    backend=lambda rt: StateBackend(rt),
)
```

**When to use:** Development, testing, short-lived tasks where file persistence is unnecessary.

---

## FilesystemBackend

Direct read/write access to the local filesystem. Use with caution.

```python
from deepagents.backends import FilesystemBackend

agent = create_deep_agent(
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
)
```

- `virtual_mode=True`: Sandboxes paths -- blocks `..`, `~`, and absolute paths outside `root_dir`; prevents symlink traversal
- `virtual_mode=False` (default): **No security even with `root_dir` set**
- **Always use `virtual_mode=True`** and scope `root_dir` tightly

> **Security warnings:** FilesystemBackend grants direct read/write access. Agents can read secrets (API keys, `.env` files). Combined with network tools, this enables SSRF/exfiltration. Modifications are permanent. Appropriate for local dev CLIs and CI/CD pipelines. **Not appropriate for web servers or HTTP APIs.** Use Human-in-the-Loop middleware and sandbox backends for production.

**When to use:** CLI tools, sandboxed containers (Docker, Modal, Runloop, Daytona). Never in web servers or HTTP APIs without sandboxing.

---

## StoreBackend (Persistent)

Cross-thread persistent storage using LangGraph's BaseStore. Files survive across different threads and sessions.

```python
from deepagents import create_deep_agent
from deepagents.backends import StoreBackend
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()  # Use PostgresStore in production

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    store=store,
    backend=lambda rt: StoreBackend(rt),
)
```

On LangSmith Deployment, omit `store` -- the platform provides one.

**When to use:** Production systems where agents need to remember information across conversations.

---

## CompositeBackend (Hybrid)

Routes different path prefixes to different backends. The production pattern for combining ephemeral working files with persistent memory.

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()  # Use PostgresStore in production

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    store=store,
    backend=lambda rt: CompositeBackend(
        default=StateBackend(rt),           # Working files: ephemeral
        routes={"/memories/": StoreBackend(rt)}  # Memory files: persistent
    ),
)
```

**Path routing:**
- Files prefixed with `/memories/` go to StoreBackend (persistent, cross-thread)
- All other files go to StateBackend (ephemeral, thread-local)
- Longer prefixes win: `/memories/projects/` can override `/memories/`
- CompositeBackend strips the route prefix before storing (`/memories/preferences.txt` stored as `/preferences.txt`)
- Query operations (`ls`, `glob`, `grep`) aggregate results across backends and preserve original prefixed paths

---

## Backend Factory Pattern

Backends that need runtime access (StateBackend, StoreBackend) use a factory callable:

```python
# Factory: receives ToolRuntime at agent initialization
backend=lambda rt: StateBackend(rt)

# Instance: doesn't need runtime (FilesystemBackend)
backend=FilesystemBackend(root_dir="/workspace")
```

You can pass either:
- A `BackendProtocol` instance (e.g., `FilesystemBackend(...)`)
- A `BackendFactory` callable: `Callable[[ToolRuntime], BackendProtocol]`

---

## Memory Parameter

The `memory` parameter on `create_deep_agent` specifies virtual file paths (typically AGENTS.md files) that provide persistent context to the agent. How you populate those files depends on the backend:

**StateBackend** -- pass files at invoke time:
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

**StoreBackend** -- pre-populate the store:
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

**FilesystemBackend** -- point to a local file:
```python
agent = create_deep_agent(
    backend=FilesystemBackend(root_dir="/path/to/project"),
    memory=["./AGENTS.md"],
    checkpointer=MemorySaver(),
)
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

## Long-Term Memory Setup

Memory enables agents to persist information across conversations (threads). While checkpointers save conversation state per-thread, memory provides **cross-thread** persistence.

### Memory Architecture

```
Thread 1 (Mon): Agent learns user prefers concise reports
    |
    v
Agent writes to /memories/user-preferences.md
    |
    v
StoreBackend persists this file
    |
    v
Thread 2 (Wed): New conversation, new thread_id
    |
    v
Agent reads /memories/user-preferences.md
    |
    v
Agent automatically uses concise report format
```

### Production Memory Setup

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

# Production-grade persistent storage
checkpointer = PostgresSaver.from_conn_string("postgresql://...")
store = PostgresStore.from_conn_string("postgresql://...")

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    checkpointer=checkpointer,
    store=store,
    backend=lambda rt: CompositeBackend(
        default=StateBackend(rt),
        routes={
            "/memories/": StoreBackend(rt),         # User preferences, knowledge
            "/memories/projects/": StoreBackend(rt), # Per-project persistent data
        }
    ),
    memory=["/memories/"],  # Tell agent about memory locations
    system_prompt=(
        "Save important findings to /memories/ for future reference. "
        "Use working files (no prefix) for intermediate drafts. "
        "Check /memories/ at the start of each conversation for context."
    ),
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

## Memory vs Checkpointer

| Feature | Checkpointer | Memory (Store) |
|---------|-------------|----------------|
| Scope | Per-thread | Cross-thread |
| Content | Messages, tool calls, state | Files, notes, preferences |
| Purpose | Conversation continuity | Long-term knowledge |
| Persistence | Thread lifetime | Indefinite |

Both are needed for a fully persistent agent. Use the checkpointer for conversation state and memory for learned knowledge.

---

## Security Checklist

| Environment | Recommended Backend | Safeguards |
|-------------|-------------------|------------|
| Development | StateBackend | None needed (ephemeral) |
| Web Server / API | StateBackend or StoreBackend | Never use FilesystemBackend |
| CLI Tool | FilesystemBackend + `virtual_mode=True` | Restrict `root_dir` |
| Sandbox (Docker, Modal) | FilesystemBackend | Container isolation |
| Production | CompositeBackend | HITL middleware for writes |

---

## Decision Flow

```
What environment are you in?
+-- Development/Testing
|   +-- StateBackend (default, no config needed)
+-- Production Web API
|   +-- Need cross-thread memory?
|   |   +-- YES -> CompositeBackend (State + Store)
|   |   +-- NO -> StateBackend
|   +-- NEVER use FilesystemBackend
+-- CLI Tool
|   +-- FilesystemBackend(root_dir=".", virtual_mode=True)
+-- Sandboxed Container
    +-- FilesystemBackend (container provides isolation)
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

## Anti-Patterns

```python
# WRONG: FilesystemBackend without virtual_mode
backend = FilesystemBackend(root_dir="/app")  # Agent can escape root_dir!

# WRONG: FilesystemBackend in web server
agent = create_deep_agent(
    backend=FilesystemBackend(root_dir="/"),
)

# WRONG: InMemoryStore in production
from langgraph.store.memory import InMemoryStore
store = InMemoryStore()  # Data lost on restart! Use PostgresStore

# WRONG: No route prefix planning in CompositeBackend
backend = CompositeBackend(
    default=StateBackend(rt),
    routes={"/": StoreBackend(rt)}  # Everything persists, defeats purpose
)

# WRONG: Memory without persistent backend
agent = create_deep_agent(
    backend=lambda rt: StateBackend(rt),  # Ephemeral!
    memory=["/memories/"],
    # Memory files lost after thread ends
)

# WRONG: No system prompt guidance for memory
agent = create_deep_agent(
    backend=lambda rt: CompositeBackend(
        default=StateBackend(rt),
        routes={"/memories/": StoreBackend(rt)},
    ),
    # Agent doesn't know to check /memories/ or what to save
)
```

## Checklist

- [ ] Backend explicitly chosen (don't rely on default for production)
- [ ] `virtual_mode=True` on any FilesystemBackend
- [ ] PostgresStore for production StoreBackend (not InMemoryStore)
- [ ] CompositeBackend route prefixes planned with clear separation
- [ ] HITL middleware enabled for write operations in sensitive environments
- [ ] No FilesystemBackend in web servers or HTTP APIs
- [ ] System prompt guides agent on memory read/write patterns
- [ ] Memory backed by StoreBackend or persistent storage
- [ ] Memory vs checkpointer distinction understood and both configured

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
