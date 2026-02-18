# Streaming & Persistence

Durable execution with checkpointing and real-time output via streaming.

## The Problem

Long-running agents (research tasks, multi-step analysis) face two challenges:
1. **No visibility** — `invoke()` blocks until complete with no intermediate output
2. **No durability** — if the process crashes, all progress is lost

Checkpointing solves durability. Streaming solves visibility. Production agents need both.

## Streaming Modes

LangGraph provides 6 stream modes:

| Mode | What It Emits | Best For |
|------|---------------|----------|
| `values` | Full state after each step | Debugging, state inspection |
| `updates` | State deltas per step | Long-running agents, progress tracking |
| `messages` | Token-by-token LLM output | Chatbots, real-time UX |
| `tasks` | Task execution events | Monitoring sub-agent delegation |
| `checkpoints` | Checkpoint events | Persistence monitoring |
| `custom` | Custom events from nodes | Application-specific streaming |

## Streaming Examples

### Updates Mode (Recommended for Agents)

```python
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    checkpointer=checkpointer,
)

config = {"configurable": {"thread_id": "thread-123"}}

for event in agent.stream(
    {"messages": [{"role": "user", "content": "Research AI trends"}]},
    config=config,
    stream_mode="updates",
):
    # Each event is a dict of state updates from a single node
    print(event)
```

### Messages Mode (For Chatbots)

```python
for event in agent.stream(
    {"messages": [{"role": "user", "content": "Explain quantum computing"}]},
    config=config,
    stream_mode="messages",
):
    # Token-by-token streaming for real-time display
    if hasattr(event, 'content'):
        print(event.content, end="", flush=True)
```

### Async Streaming

```python
async for event in agent.astream(
    {"messages": [{"role": "user", "content": "Research competitors"}]},
    config=config,
    stream_mode="updates",
):
    await process_event(event)
```

## Checkpointing

Checkpointing saves computation state at intermediate stages. If the process crashes, it resumes from the last checkpoint — not from scratch.

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

## Persistence Architecture

```
                    ┌─────────────────┐
                    │  Checkpointer   │
                    │  (PostgresSaver) │
                    │                 │
                    │  Saves:         │
                    │  - Messages     │
                    │  - Tool calls   │
                    │  - Agent state  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        ┌─────┴─────┐ ┌─────┴─────┐ ┌─────┴─────┐
        │ Thread 1  │ │ Thread 2  │ │ Thread 3  │
        │ User A    │ │ User A    │ │ User B    │
        │ Session 1 │ │ Session 2 │ │ Session 1 │
        └───────────┘ └───────────┘ └───────────┘

                    ┌─────────────────┐
                    │     Store       │
                    │ (PostgresStore) │
                    │                 │
                    │  Saves:         │
                    │  - /memories/   │
                    │  - Cross-thread │
                    │  - Persistent   │
                    └─────────────────┘
```

**Checkpointer** = per-thread conversation state (messages, tool calls)
**Store** = cross-thread persistent data (memories, preferences)

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

Checkpoints can be resumed on any machine, an arbitrary amount of time after they were saved — they don't rely on keeping a process running.

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

# Stream for visibility
config = {"configurable": {"thread_id": f"user-{user_id}"}}

for event in agent.stream(
    {"messages": [{"role": "user", "content": user_message}]},
    config=config,
    stream_mode="updates",
):
    send_to_client(event)
```

## Anti-Patterns

```python
# WRONG: MemorySaver in production
from langgraph.checkpoint.memory import MemorySaver
agent = create_deep_agent(checkpointer=MemorySaver())
# Data lost on restart! Use SqliteSaver or PostgresSaver

# WRONG: No thread_id
result = agent.invoke({"messages": [...]})
# No persistence, no multi-turn conversation

# WRONG: Using invoke() for long-running tasks
result = agent.invoke(...)  # Blocks with no visibility
# Use stream() with stream_mode="updates"

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
- [ ] Streaming used for long-running agent tasks
- [ ] `stream_mode="updates"` for agents, `"messages"` for chatbots
- [ ] Store configured for cross-thread memory needs
- [ ] MemorySaver never used in production
- [ ] Checkpointer present when using `interrupt_on` (HITL)
