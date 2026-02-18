# Middleware

Composable hooks for context engineering — the core architectural pattern in Deep Agents.

## The Core Principle

Middleware intercepts the agent loop, giving surgical control over what happens before, during, and after model calls. Think Express.js or Django middleware, but for AI agents. Every Deep Agent feature (planning, filesystem, sub-agents) is implemented as middleware.

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

## Default Middleware Stack

`create_deep_agent()` automatically attaches this stack in order:

| Order | Middleware | Purpose |
|-------|-----------|---------|
| 1 | TodoListMiddleware | Establish todo state, inject `write_todos` tool |
| 2 | FilesystemMiddleware | Establish file state, inject fs tools |
| 3 | SubAgentMiddleware | Inject `task` tool for delegation |
| 4 | SummarizationMiddleware | Compress conversation when tokens approach limit |
| 5 | AnthropicPromptCachingMiddleware | Optimize token usage for Anthropic models |
| 6 | PatchToolCallsMiddleware | Fix interrupted tool call history |

Conditionally added:
| Middleware | Condition |
|-----------|-----------|
| SkillsMiddleware | When `skills` argument provided |
| HumanInTheLoopMiddleware | When `interrupt_on` argument provided |

**Stack order matters.** PlanningMiddleware must come first to establish todo state. FilesystemMiddleware depends on backend being configured. SubAgentMiddleware depends on the model.

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

## Writing Custom Middleware

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

## Key Middleware Deep Dives

### TodoListMiddleware

Provides the `write_todos` tool for structured task decomposition. Automatically injects system prompt guidance on when to use todos.

**Critical constraint:** `write_todos` is enforced to be called at most once per model turn (replaces entire todo list, parallel calls create ambiguity).

```python
from deepagents.middleware.todolist import TodoListMiddleware

# Included by default, but can be customized:
agent = create_deep_agent(
    middleware=[
        TodoListMiddleware(
            system_prompt="Always create a detailed plan before starting work."
        ),
    ],
)
```

### FilesystemMiddleware

Provides four tools: `ls`, `read_file`, `write_file`, `search_files`. Backend determines storage behavior.

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

### LLMToolSelectorMiddleware

Uses an LLM to filter tools before the main model call. Essential when an agent has many tools — reduces token usage and improves focus.

```python
from deepagents.middleware.tool_selector import LLMToolSelectorMiddleware

agent = create_deep_agent(
    tools=[tool1, tool2, ..., tool30],
    middleware=[
        LLMToolSelectorMiddleware(
            model="anthropic:claude-haiku-4-5-20251001",  # Fast, cheap selector
        ),
    ],
)
```

## Middleware Execution Flow

```
User Message
    │
    ▼
before_agent(state)     ← Runs once: populate state
    │
    ▼
┌─── Agent Loop ───────────────────────┐
│                                       │
│  wrap_model_call(call_model, state)   │
│       │                               │
│       ▼                               │
│  Model generates response             │
│       │                               │
│       ▼                               │
│  Tool execution (if tool calls)       │
│       │                               │
│       ▼                               │
│  Loop continues until done            │
└───────────────────────────────────────┘
    │
    ▼
Final Response
```

## Middleware for Sub-Agents

Sub-agents automatically receive a default middleware stack:
- TodoListMiddleware
- FilesystemMiddleware
- SummarizationMiddleware

Plus any custom middleware specified in the subagent definition.

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
        TodoListMiddleware(...),      # Should come first
    ],
)

# WRONG: Duplicating default middleware
agent = create_deep_agent(
    middleware=[
        TodoListMiddleware(),  # Already included by default!
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
