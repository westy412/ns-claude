# Middleware

Composable hooks for context engineering -- the core architectural pattern in Deep Agents.

## The Core Principle

Middleware intercepts the agent loop, giving surgical control over what happens before, during, and after model calls. Think Express.js or Django middleware, but for AI agents. Every Deep Agent feature (planning, filesystem, sub-agents) is implemented as middleware.

---

## The Protocol

Every middleware implements `AgentMiddleware` with two hooks:

```python
class AgentMiddleware:
    def before_agent(self, state: dict) -> dict:
        """
        Runs ONCE at initialization.
        Use to populate state (e.g., inject filesystem content, load todos).
        """
        return state

    def wrap_model_call(self, call_model: Callable, state: dict) -> Any:
        """
        Intercepts EVERY LLM invocation.
        Use to modify prompts, filter tools, or post-process responses.
        """
        return call_model(state)
```

Each middleware also operates through three mechanisms:

1. **Extending the state schema** -- adds new keys and data structures
2. **Adding new tools** -- injects tools into the agent's toolkit
3. **Modifying the model request** -- amends the system prompt

---

## Default Middleware Stack (Verified: deepagents 0.4.1)

`create_deep_agent()` automatically attaches this stack in order:

| Order | Middleware | Module | Purpose |
|-------|-----------|--------|---------|
| 1 | FilesystemMiddleware | `deepagents.middleware.filesystem` | Establish file state, inject fs tools |
| 2 | SubAgentMiddleware | `deepagents.middleware.subagents` | Inject `task` tool for delegation |
| 3 | SummarizationMiddleware | `deepagents.middleware.summarization` | Compress conversation when tokens approach limit |
| 4 | MemoryMiddleware | `deepagents.middleware.memory` | Memory file management |
| 5 | PatchToolCallsMiddleware | `deepagents.middleware.patch_tool_calls` | Fix interrupted tool call history |

## Conditional Middleware

| Middleware | Module | Activated By | Purpose |
|-----------|--------|-------------|---------|
| SkillsMiddleware | `deepagents.middleware.skills` | `skills` argument | Progressive skill loading |

> **Note**: The following middleware do **NOT exist** in deepagents 0.4.x:
> - ~~`TodoListMiddleware`~~ (`deepagents.middleware.todolist` does not exist)
> - ~~`HumanInTheLoopMiddleware`~~ (`deepagents.middleware.hitl` does not exist)
> - ~~`LLMToolSelectorMiddleware`~~ (`deepagents.middleware.tool_selector` does not exist)

**Stack order matters.** FilesystemMiddleware depends on backend being configured. SubAgentMiddleware depends on the model.

---

## Adding Custom Middleware

```python
from deepagents import create_deep_agent

# Custom middleware is added AFTER the default stack
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    middleware=[
        MyCustomMiddleware(),
        AnotherMiddleware(),
    ],
)
```

---

## Writing Custom Middleware (AgentMiddleware Class)

```python
from langchain.agents import AgentMiddleware

class LoggingMiddleware(AgentMiddleware):
    """Log every model call for observability."""

    def before_agent(self, state: dict) -> dict:
        """Initialize logging context."""
        print(f"Agent started with {len(state.get('messages', []))} messages")
        return state

    def wrap_model_call(self, call_model, state):
        """Wrap each LLM invocation with timing."""
        import time
        start = time.time()
        result = call_model(state)
        elapsed = time.time() - start
        print(f"Model call took {elapsed:.2f}s")
        return result
```

## Writing Custom Middleware (@wrap_tool_call Decorator)

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

### Custom Middleware Patterns

- **Logging**: Capture tool names, arguments, results
- **Validation**: Reject tool calls that violate constraints
- **Transformation**: Modify tool arguments or results
- **Rate limiting**: Throttle by tracking invocation counts
- **Error handling**: Wrap `handler(request)` in try/except

---

## Key Middleware Deep Dives

### FilesystemMiddleware

Provides tools: `ls`, `read_file`, `write_file`, `search_files`. Backend determines storage behavior.

```python
from deepagents.middleware.filesystem import FilesystemMiddleware

agent = create_deep_agent(
    middleware=[
        FilesystemMiddleware(
            backend=None,  # Defaults to StateBackend (ephemeral)
            system_prompt="Write to the filesystem when producing reports.",
            custom_tool_descriptions={
                "ls": "Use ls to discover available files.",
                "read_file": "Use read_file to examine file contents.",
            },
        ),
    ],
)
```

### SummarizationMiddleware

Monitors message token counts and automatically summarizes older messages when a threshold is reached. Preserves recent messages and keeps AI/Tool message pairs together.

Three compression techniques, applied in order of priority:

| Technique | Trigger | What Happens |
|-----------|---------|-------------|
| Tool result offloading | Single result > **20,000 tokens** | Oversized result saved to filesystem; replaced with file path reference and preview of first 10 lines |
| Tool input offloading | Context at **85%** of model's window | Older write/edit tool call arguments truncated; replaced with pointer to file on disk |
| Summarization | **85% threshold** AND offloading yields insufficient space | LLM generates structured summary (session intent, artifacts created, next steps); full conversation written to filesystem as canonical record |

```python
from deepagents.middleware.summarization import SummarizationMiddleware

agent = create_deep_agent(
    middleware=[
        SummarizationMiddleware(
            message_threshold=50,  # Summarize when exceeding this count
        ),
    ],
)
```

---

## Middleware Execution Flow

```
User Message
    |
    v
before_agent(state)     <- Runs once: populate state
    |
    v
+--- Agent Loop -----------------------+
|                                       |
|  wrap_model_call(call_model, state)   |
|       |                               |
|       v                               |
|  Model generates response             |
|       |                               |
|       v                               |
|  Tool execution (if tool calls)       |
|       |                               |
|       v                               |
|  Loop continues until done            |
+---------------------------------------+
    |
    v
Final Response
```

## Detailed Execution Order (deepagents 0.4.1)

```
1. PatchToolCallsMiddleware.before_agent()    <- Fix history
2. FilesystemMiddleware.before_agent()        <- Load filesystem state
3. SubAgentMiddleware.before_agent()          <- Configure subagents
4. MemoryMiddleware.before_agent()            <- Load memory files
5. [SkillsMiddleware.before_agent()]          <- Load skill index (if enabled)
6. SummarizationMiddleware.before_agent()     <- Check token limits
    |
    v
Agent Loop:
    7. [Custom middleware].wrap()              <- Your extensions
    |
    v
Model Call -> Tool Execution -> Loop
```

---

## Middleware for Sub-Agents

Sub-agents automatically receive a default middleware stack:
- FilesystemMiddleware
- SummarizationMiddleware
- MemoryMiddleware

Plus any custom middleware specified in the subagent definition.

---

## Middleware Types Quick Reference

### Default (Auto-Attached)

| Middleware | Tools Provided | Hook Used |
|-----------|---------------|-----------|
| FilesystemMiddleware | `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep` | `before_agent` + `wrap_model_call` |
| SubAgentMiddleware | `task` | `wrap_model_call` |
| SummarizationMiddleware | -- | `wrap_model_call` |
| MemoryMiddleware | -- | `before_agent` |
| PatchToolCallsMiddleware | -- | `before_agent` |

### Conditional (Auto-Added When Configured)

| Middleware | Purpose | When Added |
|-----------|---------|------------|
| SkillsMiddleware | Progressive skill loading | When `skills` argument provided |

### Quick Selection Guide

```
Does the agent need domain expertise?
+-- YES -> Use skills parameter (auto-adds SkillsMiddleware)
+-- NO -> Default stack is sufficient

Does the agent need custom behavior?
+-- YES -> Write custom AgentMiddleware class or @wrap_tool_call
+-- NO -> Default stack is sufficient
```

---

## Anti-Patterns

```python
# WRONG: Middleware that modifies state without returning it
class BadMiddleware(AgentMiddleware):
    def before_agent(self, state):
        state["custom_key"] = "value"
        # Missing: return state

# WRONG: Heavy computation in wrap_model_call
class SlowMiddleware(AgentMiddleware):
    def wrap_model_call(self, call_model, state):
        expensive_operation()  # Runs on EVERY model call
        return call_model(state)

# WRONG: Ignoring middleware order
agent = create_deep_agent(
    middleware=[
        SubAgentMiddleware(...),     # Depends on model
        FilesystemMiddleware(...),    # Should come before SubAgent
    ],
)

# WRONG: Duplicating default middleware
agent = create_deep_agent(
    middleware=[
        FilesystemMiddleware(),  # Already included by default!
    ],
)
```

## Checklist

- [ ] Custom middleware placed after default stack
- [ ] `before_agent` returns modified state
- [ ] `wrap_model_call` calls `call_model(state)` (don't swallow the call)
- [ ] Heavy operations cached, not repeated every model call
- [ ] Middleware order respects dependency chain
- [ ] Default middleware not duplicated

---

## Documentation Links

- [Deep Agents Customization (Middleware)](https://docs.langchain.com/oss/python/deepagents/customization) -- Default stack, conditional middleware, custom middleware with `@wrap_tool_call`
- [Context Management for Deep Agents (Blog)](https://blog.langchain.com/context-management-for-deepagents/) -- Compression techniques, token thresholds, testing strategies
