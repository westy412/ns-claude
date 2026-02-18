# Middleware Architecture and Human-in-the-Loop

---

## Default Middleware Stack

| Middleware | Purpose |
|-----------|---------|
| `TodoListMiddleware` | Task planning and tracking |
| `FilesystemMiddleware` | File system operations |
| `SubAgentMiddleware` | Spawns and coordinates subagents |
| `SummarizationMiddleware` | Condenses message history when conversations get long |
| `AnthropicPromptCachingMiddleware` | Reduces redundant token processing for Anthropic models |
| `PatchToolCallsMiddleware` | Fixes interrupted/cancelled tool calls |

## Conditional Middleware

| Middleware | Activated By | Purpose |
|-----------|-------------|---------|
| `MemoryMiddleware` | `memory` argument | Persistent memory across sessions |
| `SkillsMiddleware` | `skills` argument | Loads skill definitions |
| `HumanInTheLoopMiddleware` | `interrupt_on` argument | Pauses for human approval |

---

## How Middleware Works

Each middleware operates through three mechanisms:

1. **Extending the state schema** -- adds new keys and data structures
2. **Adding new tools** -- injects tools into the agent's toolkit
3. **Modifying the model request** -- amends the system prompt

---

## Custom Middleware

```python
from langchain.tools import tool
from langchain.agents.middleware import wrap_tool_call
from deepagents import create_deep_agent

@tool
def get_weather(city: str) -> str:
    """Get the weather in a city."""
    return f"The weather in {city} is sunny."

call_count = [0]

@wrap_tool_call
def log_tool_calls(request, handler):
    """Intercept and log every tool call."""
    call_count[0] += 1
    tool_name = request.name if hasattr(request, 'name') else str(request)
    print(f"[Middleware] Tool call #{call_count[0]}: {tool_name}")
    print(f"[Middleware] Arguments: {request.args if hasattr(request, 'args') else 'N/A'}")
    result = handler(request)
    print(f"[Middleware] Tool call #{call_count[0]} completed")
    return result

agent = create_deep_agent(tools=[get_weather], middleware=[log_tool_calls])
```

### Patterns

- **Logging**: Capture tool names, arguments, results
- **Validation**: Reject tool calls that violate constraints
- **Transformation**: Modify tool arguments or results
- **Rate limiting**: Throttle by tracking invocation counts
- **Error handling**: Wrap `handler(request)` in try/except

---

## Human-in-the-Loop

Configure approval gates for sensitive tools. Requires a **checkpointer** and **thread ID**.

### interrupt_on Options

| Value | Behavior |
|-------|----------|
| `True` | Pause with all decisions available (approve, edit, reject) |
| `False` | No interrupts for this tool |
| `{"allowed_decisions": [...]}` | Pause with specific decisions only |

### Decision Types

| Decision | Effect |
|----------|--------|
| `"approve"` | Execute the tool with the original arguments |
| `"edit"` | Modify tool arguments before execution |
| `"reject"` | Skip executing this tool call entirely |

```python
from langchain.tools import tool
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

@tool
def delete_file(path: str) -> str:
    """Delete a file at the given path."""
    return f"Deleted {path}"

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    return f"Email sent to {to}"

checkpointer = MemorySaver()

agent = create_deep_agent(
    model="claude-sonnet-4-5-20250929",
    tools=[delete_file, send_email],
    interrupt_on={
        "delete_file": True,                                        # All decisions: approve, edit, reject
        "send_email": {"allowed_decisions": ["approve", "reject"]}, # No editing allowed
    },
    checkpointer=checkpointer  # REQUIRED for HITL
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Clean up old files and notify the team"}]},
    config={"configurable": {"thread_id": "task-123"}}
)
```

### How It Works

1. Agent plans a tool call matching an `interrupt_on` entry
2. Execution pauses, pending call persisted via checkpointer
3. Human reviews and provides decision (approve, reject, or edit)
4. Agent resumes via `Command(resume={"decisions": decisions})` with the same `thread_id`

When multiple gated tools are called at once, all interrupts are **batched** into a single interrupt -- provide one decision per action in order.

### Resuming After Interrupt

```python
from langgraph.types import Command

# After collecting human decision(s)
result = agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config={"configurable": {"thread_id": "task-123"}}  # Same thread_id
)
```

### Subagent Interrupts

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

Tools can also call `interrupt()` directly from within tool code for custom approval flows:

```python
from langgraph.types import interrupt

@tool
def request_approval(action: str) -> str:
    approval = interrupt({"type": "approval_request", "action": action})
    return "APPROVED" if approval.get("approved") else "REJECTED"
```

### What to Gate

Gate tools with **irreversible side effects**: file deletion, sending messages, database writes, financial transactions. Read-only tools generally don't need gates.

---

## Context Management (SummarizationMiddleware)

Three compression techniques, applied in order of priority:

| Technique | Trigger | What Happens |
|-----------|---------|-------------|
| Tool result offloading | Single result > **20,000 tokens** | Oversized result saved to filesystem; replaced with file path reference and preview of first 10 lines |
| Tool input offloading | Context at **85%** of model's window | Older write/edit tool call arguments truncated; replaced with pointer to file on disk |
| Summarization | **85% threshold** AND offloading yields insufficient space | LLM generates structured summary (session intent, artifacts created, next steps); full conversation written to filesystem as canonical record |

---

## Documentation Links

- [Deep Agents Customization (Middleware)](https://docs.langchain.com/oss/python/deepagents/customization) -- Default stack, conditional middleware, custom middleware with `@wrap_tool_call`
- [Deep Agents Human-in-the-Loop](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop) -- `interrupt_on` config, decision types, subagent interrupts, `interrupt()` primitive
- [Context Management for Deep Agents (Blog)](https://blog.langchain.com/context-management-for-deepagents/) -- Compression techniques, token thresholds, testing strategies
