# Backends

Pluggable storage for filesystem operations and memory persistence.

## The Problem

Agents need to read and write files, but the storage requirements differ dramatically between development (ephemeral, in-memory) and production (persistent, secure, sandboxed). Without proper backend configuration, agents either lose all work between sessions or gain dangerous filesystem access.

## Four Backend Types

| Backend | Storage | Persistence | Security | Use Case |
|---------|---------|-------------|----------|----------|
| **StateBackend** | LangGraph state | Ephemeral (thread-local) | Safe | Development, simple tasks |
| **StoreBackend** | LangGraph BaseStore | Cross-thread persistent | Safe | Production memory, user preferences |
| **FilesystemBackend** | Real disk | Permanent | Risky | CLI tools, sandboxed environments |
| **CompositeBackend** | Routes to others | Mixed | Depends on config | Hybrid: ephemeral working files + persistent memory |

## StateBackend (Default)

Ephemeral, in-memory storage. Files exist only for the duration of a single thread.

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

**When to use:** Production systems where agents need to remember information across conversations. When deploying to LangSmith Deployment, a store is automatically provisioned.

## FilesystemBackend (Real Disk)

Direct filesystem access. Files are read/written to the actual disk.

```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

# ALWAYS use virtual_mode=True in production
agent = create_deep_agent(
    backend=FilesystemBackend(
        root_dir="/app/workspace",
        virtual_mode=True,  # CRITICAL: blocks ../, ~, absolute paths outside root
    ),
)
```

**Security warning:** `virtual_mode=False` (the default) provides **no security** even with `root_dir` set. Agents can read API keys, credentials, `.env` files, and make permanent, irreversible file modifications.

**When to use:** CLI tools, sandboxed containers (Docker, Modal, Runloop, Daytona). Never in web servers or HTTP APIs without sandboxing.

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

**Routing rules:**
- Files prefixed with `/memories/` go to StoreBackend (persistent, cross-thread)
- All other files go to StateBackend (ephemeral, thread-local)
- Longer prefixes win: `/memories/projects/` can override `/memories/`

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

## Production Pattern: Hybrid Memory

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
    system_prompt=(
        "Save important findings to /memories/ for future reference. "
        "Use working files (no prefix) for intermediate drafts."
    ),
)
```

## Security Checklist

| Environment | Recommended Backend | Safeguards |
|-------------|-------------------|------------|
| Development | StateBackend | None needed (ephemeral) |
| Web Server / API | StateBackend or StoreBackend | Never use FilesystemBackend |
| CLI Tool | FilesystemBackend + `virtual_mode=True` | Restrict `root_dir` |
| Sandbox (Docker, Modal) | FilesystemBackend | Container isolation |
| Production | CompositeBackend | HITL middleware for writes |

## Anti-Patterns

```python
# WRONG: FilesystemBackend without virtual_mode
backend = FilesystemBackend(root_dir="/app")  # Agent can escape root_dir!

# WRONG: FilesystemBackend in web server
# Agents can read secrets, modify system files
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

# WRONG: Assuming StateBackend persists across threads
# Thread 1: agent writes report.md
# Thread 2: agent tries to read report.md → File not found!
```

## Decision Flow

```
What environment are you in?
├── Development/Testing
│   └── StateBackend (default, no config needed)
├── Production Web API
│   ├── Need cross-thread memory?
│   │   ├── YES → CompositeBackend (State + Store)
│   │   └── NO → StateBackend
│   └── NEVER use FilesystemBackend
├── CLI Tool
│   └── FilesystemBackend(root_dir=".", virtual_mode=True)
└── Sandboxed Container
    └── FilesystemBackend (container provides isolation)
```

## Checklist

- [ ] Backend explicitly chosen (don't rely on default for production)
- [ ] `virtual_mode=True` on any FilesystemBackend
- [ ] PostgresStore for production StoreBackend (not InMemoryStore)
- [ ] CompositeBackend route prefixes planned with clear separation
- [ ] HITL middleware enabled for write operations in sensitive environments
- [ ] No FilesystemBackend in web servers or HTTP APIs
