# Human-in-the-Loop

Per-tool approval workflows using `interrupt_on` and LangGraph's interrupt capabilities.

## The Problem

Some agent actions are irreversible (deleting files, sending emails, making API calls). Without human approval, agents can take destructive actions autonomously. HITL lets you configure which tools require human confirmation before execution.

## Prerequisites

HITL **requires a checkpointer** to persist agent state between the interrupt and resume. Without a checkpointer, the agent can't pause and wait for approval.

```python
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("agent.db")
```

---

## Basic Setup

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.sqlite import SqliteSaver

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[get_weather, send_email, delete_file],
    checkpointer=SqliteSaver.from_conn_string("agent.db"),
    interrupt_on={
        "send_email": True,          # Full approve/edit/reject
        "delete_file": True,          # Full approve/edit/reject
        "get_weather": False,         # No interrupt (auto-execute)
    },
)
```

---

## interrupt_on Configuration

### Simple Boolean

```python
interrupt_on={
    "send_email": True,   # Pause with all decisions available (approve, edit, reject)
    "get_weather": False,  # Auto-execute, no pause
}
```

### Detailed InterruptOnConfig

```python
interrupt_on={
    "send_email": {
        "allowed_decisions": ["approve", "edit", "reject"],
    },
    "delete_file": {
        "allowed_decisions": ["approve", "reject"],  # No editing allowed
    },
}
```

### Decision Types

| Decision | Effect |
|----------|--------|
| `"approve"` | Execute the tool with the original arguments |
| `"edit"` | Modify tool arguments before execution |
| `"reject"` | Skip executing this tool call entirely |

---

## Execution Flow

```
Agent decides to call send_email(to="user@example.com", body="...")
    |
    v
HumanInTheLoopMiddleware detects send_email is in interrupt_on
    |
    v
Agent PAUSES (state saved to checkpointer)
    |
    v
Application presents tool call to human for review
    |
    v
Human decides: approve / edit / reject
    |
    v
Application resumes agent with decision
    |
    v
Agent continues (executes tool or handles rejection)
```

---

## Resuming After Interrupt

Use `Command(resume=...)` to resume after an interrupt:

```python
from langgraph.types import Command

config = {"configurable": {"thread_id": "task-123"}}

# Initial invocation
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Send a report to team@company.com"}]},
    config=config,
)

# Check if agent is waiting for approval
if result.get("action_requests"):
    for request in result["action_requests"]:
        print(f"Tool: {request['tool']}")
        print(f"Args: {request['args']}")

        # Get human decision
        decision = get_human_decision(request)  # Your UI logic

    # Resume with decision using Command
    result = agent.invoke(
        Command(resume={"decisions": [{"type": "approve"}]}),
        config=config,  # MUST use same thread_id
    )
```

---

## Streaming with HITL

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
for event in agent.stream(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config,
    stream_mode="updates",
):
    print(event)
```

---

## Common Patterns

### Sensitive Write Operations

```python
agent = create_deep_agent(
    tools=[read_file, write_file, delete_file, search_files],
    checkpointer=checkpointer,
    interrupt_on={
        "write_file": True,     # Approve before writing
        "delete_file": True,     # Approve before deleting
        "read_file": False,      # Auto-execute reads
        "search_files": False,   # Auto-execute searches
    },
)
```

### External Communication

```python
agent = create_deep_agent(
    tools=[draft_email, send_email, search_web, create_ticket],
    checkpointer=checkpointer,
    interrupt_on={
        "send_email": {
            "allowed_decisions": ["approve", "edit", "reject"],
        },
        "create_ticket": {
            "allowed_decisions": ["approve", "edit", "reject"],
        },
        # search_web and draft_email auto-execute
    },
)
```

### Sub-Agent Approval

```python
agent = create_deep_agent(
    subagents=[researcher, writer],
    checkpointer=checkpointer,
    interrupt_on={
        "task": True,  # Approve before delegating to any sub-agent
    },
)
```

---

## Subagent Interrupts

Subagents can have their own `interrupt_on` config that **overrides** the parent:

```python
agent = create_deep_agent(
    interrupt_on={"delete_file": True},
    subagents=[{
        "name": "file-manager",
        "tools": [delete_file, read_file],
        "interrupt_on": {
            "delete_file": True,
            "read_file": True,  # Override: gate reads in this subagent
        }
    }],
    checkpointer=checkpointer
)
```

---

## Using interrupt() Directly

Tools can call `interrupt()` directly from within tool code for custom approval flows:

```python
from langgraph.types import interrupt

@tool
def request_approval(action: str) -> str:
    approval = interrupt({"type": "approval_request", "action": action})
    return "APPROVED" if approval.get("approved") else "REJECTED"
```

---

## Multiple Tool Calls in One Turn

When the agent makes multiple tool calls in a single turn, all interrupts are **batched** into a single interrupt -- provide one decision per action in order:

```python
# Agent wants to:
#   1. send_email(to="alice@co.com", ...)
#   2. send_email(to="bob@co.com", ...)
#   3. delete_file(path="/old-report.md")

# Resume with decisions in matching order:
result = agent.invoke(
    Command(resume={"decisions": [
        {"type": "approve"},      # Approve email to Alice
        {"type": "edit", "args": {"to": "bob-new@co.com"}},  # Edit Bob's email
        {"type": "reject"},       # Reject file deletion
    ]}),
    config=config,
)
```

---

## What to Gate

Gate tools with **irreversible side effects**: file deletion, sending messages, database writes, financial transactions. Read-only tools generally don't need gates.

---

## Anti-Patterns

```python
# WRONG: HITL without checkpointer
agent = create_deep_agent(
    interrupt_on={"send_email": True},
    # Missing checkpointer! Agent can't pause and resume
)

# WRONG: Interrupting on every tool
interrupt_on={
    "read_file": True,
    "search_files": True,
    "write_todos": True,  # Interrupting planning is annoying
    "ls": True,
}
# Only interrupt on irreversible or sensitive actions

# WRONG: Different thread_id on resume
# Invoke:
result = agent.invoke(messages, config={"configurable": {"thread_id": "t1"}})
# Resume with DIFFERENT thread_id:
result = agent.invoke(Command(resume=decisions), config={"configurable": {"thread_id": "t2"}})
# Agent starts fresh, doesn't find the paused state!

# WRONG: Decisions list order mismatch
# action_requests: [send_email, delete_file]
# decisions: [delete decision, email decision]  # Wrong order!
```

## Checklist

- [ ] Checkpointer configured (required for HITL)
- [ ] Only irreversible/sensitive tools in `interrupt_on`
- [ ] Same `thread_id` used for invoke and resume
- [ ] Decisions list matches `action_requests` order
- [ ] UI implemented to present tool calls for human review
- [ ] Read-only tools excluded from interrupts (auto-execute)
- [ ] Sub-agent delegation (`task` tool) considered for interrupts
- [ ] `Command(resume=...)` used for resuming after interrupt

---

## Documentation Links

- [Deep Agents Human-in-the-Loop](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop) -- `interrupt_on` config, decision types, subagent interrupts, `interrupt()` primitive
- [Deep Agents Customization (Middleware)](https://docs.langchain.com/oss/python/deepagents/customization) -- Default stack, conditional middleware
