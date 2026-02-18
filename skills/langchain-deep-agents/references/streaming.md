# Streaming

Real-time event output during agent execution.

## The Problem

`invoke()` blocks until the agent completes with no intermediate output. For long-running tasks (research, multi-step analysis), users have no visibility into progress. Streaming solves this by emitting events as the agent works.

---

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

---

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

---

## Streaming with Subagents

Use `lc_agent_name` in event metadata to differentiate which agent emitted an event:

```python
agent = create_deep_agent(
    model="claude-sonnet-4-5-20250929",
    subagents=[research_subagent],
    name="main-agent"
)

for event in agent.stream(input, config=config, stream_mode="updates"):
    agent_name = event.metadata.get("lc_agent_name", "unknown")
    # agent_name -> "main-agent" or "research-agent"
    print(f"[{agent_name}] {event}")
```

---

## Streaming with HITL

When streaming encounters an interrupt, handle it and resume:

```python
config = {"configurable": {"thread_id": "thread-123"}}

for event in agent.stream(
    {"messages": [{"role": "user", "content": "Delete old reports"}]},
    config=config,
    stream_mode="updates",
):
    if "action_requests" in event:
        # Agent is paused, waiting for approval
        for request in event["action_requests"]:
            decision = await get_human_approval(request)
        break

# Resume after approval
from langgraph.types import Command

for event in agent.stream(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config,
    stream_mode="updates",
):
    print(event)
```

---

## Production Streaming Setup

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string("postgresql://...")

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    checkpointer=checkpointer,
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

---

## Mode Selection Guide

```
What is your use case?
+-- Agent performing multi-step tasks
|   +-- stream_mode="updates" (state deltas per step)
+-- Chatbot / conversational UI
|   +-- stream_mode="messages" (token-by-token)
+-- Debugging agent behavior
|   +-- stream_mode="values" (full state snapshots)
+-- Monitoring sub-agent delegation
|   +-- stream_mode="tasks" (task execution events)
+-- Custom application events
    +-- stream_mode="custom" (emit from nodes)
```

---

## Anti-Patterns

```python
# WRONG: Using invoke() for long-running tasks
result = agent.invoke(...)  # Blocks with no visibility
# Use stream() with stream_mode="updates"

# WRONG: Not handling HITL interrupts in stream
for event in agent.stream(...):
    print(event)  # Will stop at interrupt with no handling
# Check for "action_requests" and resume with Command

# WRONG: Ignoring stream_mode selection
for event in agent.stream(...):  # Default mode may not suit your needs
    ...
# Explicitly choose the mode that matches your use case
```

## Checklist

- [ ] Streaming used for long-running agent tasks (not invoke)
- [ ] `stream_mode="updates"` for agents, `"messages"` for chatbots
- [ ] `lc_agent_name` used to differentiate subagent events
- [ ] HITL interrupts handled in stream loop
- [ ] Async streaming (`astream`) used in async contexts
