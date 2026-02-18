# Persistence

Durable state storage for resumption, multi-turn conversations, and crash recovery.

## The Problem

Without persistence, if the process crashes during a long-running agent task, all progress is lost. Checkpointing saves computation state at intermediate stages so execution can resume from the last checkpoint -- not from scratch.

---

## Checkpointing

### Development: SqliteSaver

```python
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("agent.db")

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    checkpointer=checkpointer,
)
```

### Production: PostgresSaver

```python
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@host:5432/agents"
)

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    checkpointer=checkpointer,
)
```

### Why Checkpointers Matter

| Feature | Without Checkpointer | With Checkpointer |
|---------|---------------------|-------------------|
| Multi-turn conversations | Lost between requests | Preserved |
| Crash recovery | Start over | Resume from checkpoint |
| Human-in-the-loop | Not possible | Pause and resume |
| Time-travel debugging | Not possible | Replay from any point |

---

## Thread Management

Every invocation needs a `thread_id` to maintain conversation state:

```python
config = {"configurable": {"thread_id": "user-123-session-456"}}

# Turn 1
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Research AI startups"}]},
    config=config,
)

# Turn 2 (same thread - conversation continues)
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Focus on healthcare AI"}]},
    config=config,
)
```

**Thread ID design:**
- Use meaningful IDs: `user-{user_id}-session-{session_id}`
- New conversations get new thread IDs
- Same thread ID = continued conversation

---

## Persistence Architecture

```
                    +------------------+
                    |  Checkpointer    |
                    |  (PostgresSaver) |
                    |                  |
                    |  Saves:          |
                    |  - Messages      |
                    |  - Tool calls    |
                    |  - Agent state   |
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
        +-----+-----+ +-----+-----+ +-----+-----+
        | Thread 1  | | Thread 2  | | Thread 3  |
        | User A    | | User A    | | User B    |
        | Session 1 | | Session 2 | | Session 1 |
        +-----------+ +-----------+ +-----------+

                    +------------------+
                    |     Store        |
                    | (PostgresStore)  |
                    |                  |
                    |  Saves:          |
                    |  - /memories/    |
                    |  - Cross-thread  |
                    |  - Persistent    |
                    +------------------+
```

**Checkpointer** = per-thread conversation state (messages, tool calls)
**Store** = cross-thread persistent data (memories, preferences)

---

## Crash Recovery

```python
# Process crashes during a long research task...

# When the process restarts, just invoke with the same thread_id:
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Continue where you left off"}]},
    config={"configurable": {"thread_id": "thread-123"}},
)
# Agent sees full conversation history from checkpoint and continues
```

Checkpoints can be resumed on any machine, an arbitrary amount of time after they were saved -- they don't rely on keeping a process running.

---

## Production Setup

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

# Production-grade persistence
checkpointer = PostgresSaver.from_conn_string("postgresql://...")
store = PostgresStore.from_conn_string("postgresql://...")

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    checkpointer=checkpointer,
    store=store,
    backend=lambda rt: CompositeBackend(
        default=StateBackend(rt),
        routes={"/memories/": StoreBackend(rt)},
    ),
)
```

---

## Checkpointer Selection Guide

| Checkpointer | Persistence | Use Case |
|--------------|-------------|----------|
| `MemorySaver` | None (lost on restart) | Tests only, **never production** |
| `SqliteSaver` | Local file | Development, single-machine |
| `PostgresSaver` | Durable database | Production, multi-machine |

---

## Anti-Patterns

```python
# WRONG: MemorySaver in production
from langgraph.checkpoint.memory import MemorySaver
agent = create_deep_agent(checkpointer=MemorySaver())
# Data lost on restart! Use SqliteSaver or PostgresSaver

# WRONG: No thread_id
result = agent.invoke({"messages": [...]})
# No persistence, no multi-turn conversation

# WRONG: Same thread_id for different users
config = {"configurable": {"thread_id": "main"}}  # All users share state!

# WRONG: No checkpointer with HITL
agent = create_deep_agent(
    interrupt_on={"delete_file": True},
    # Missing checkpointer - can't pause and resume!
)
```

## Checklist

- [ ] Checkpointer configured (SqliteSaver for dev, PostgresSaver for prod)
- [ ] Thread IDs are meaningful and unique per conversation
- [ ] Store configured for cross-thread memory needs
- [ ] MemorySaver never used in production
- [ ] Checkpointer present when using `interrupt_on` (HITL)
