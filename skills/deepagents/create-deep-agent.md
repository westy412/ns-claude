# create_deep_agent()

The single entry point for building deep agents. Returns a compiled LangGraph graph.

## The Core Principle

`create_deep_agent()` is a factory function that assembles a middleware stack, wires up tools, backends, and sub-agents, and returns a `CompiledStateGraph`. You configure everything through its parameters rather than manually building LangGraph graphs.

## Full Signature

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model: str | BaseChatModel | None = None,
    tools: Sequence[BaseTool | Callable | dict] | None = None,
    *,
    system_prompt: str | SystemMessage | None = None,
    middleware: Sequence[AgentMiddleware] = (),
    subagents: list[SubAgent | CompiledSubAgent] | None = None,
    skills: list[str] | None = None,
    memory: list[str] | None = None,
    response_format: ResponseFormat | None = None,
    context_schema: type[Any] | None = None,
    checkpointer: Checkpointer | None = None,
    store: BaseStore | None = None,
    backend: BackendProtocol | BackendFactory | None = None,
    interrupt_on: dict[str, bool | InterruptOnConfig] | None = None,
    debug: bool = False,
    name: str | None = None,
    cache: BaseCache | None = None,
) -> CompiledStateGraph
```

## Parameter Guide

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `model` | `str \| BaseChatModel` | `claude-sonnet-4` | LLM to use (must support tool calling) |
| `tools` | `Sequence[...]` | `[]` | Custom tools added to built-in tools |
| `system_prompt` | `str \| SystemMessage` | `None` | Prepended to BASE_AGENT_PROMPT |
| `middleware` | `Sequence[AgentMiddleware]` | `()` | Custom middleware added after defaults |
| `subagents` | `list[SubAgent \| CompiledSubAgent]` | `None` | Specialized agents for delegation |
| `skills` | `list[str]` | `None` | Filesystem paths to skill directories |
| `memory` | `list[str]` | `None` | Filesystem paths to memory files |
| `checkpointer` | `Checkpointer` | `None` | State persistence (required for HITL) |
| `store` | `BaseStore` | `None` | Cross-thread persistent storage |
| `backend` | `BackendProtocol \| BackendFactory` | `StateBackend` | Filesystem operation backend |
| `interrupt_on` | `dict[str, ...]` | `None` | Per-tool HITL approval config |
| `debug` | `bool` | `False` | Enable debug logging |
| `name` | `str` | `None` | Agent name for observability |

## Minimal Example

```python
from deepagents import create_deep_agent

# Simplest possible agent - uses claude-sonnet-4 by default
agent = create_deep_agent()

result = agent.invoke({
    "messages": [{"role": "user", "content": "Research LangGraph and write a summary"}]
})
```

## Production Example

```python
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.checkpoint.postgres import PostgresSaver

@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    # Implementation here
    return "search results..."

agent = create_deep_agent(
    model=init_chat_model("anthropic:claude-sonnet-4-20250514"),
    tools=[search_web],
    system_prompt=(
        "You are an expert research assistant. "
        "Always write findings to the filesystem and create a structured report."
    ),
    checkpointer=PostgresSaver.from_conn_string("postgresql://..."),
    name="research-agent",
    debug=False,
)
```

## Model Selection

```python
# Provider:model format (recommended)
agent = create_deep_agent(model="anthropic:claude-sonnet-4-20250514")
agent = create_deep_agent(model="openai:gpt-4o")
agent = create_deep_agent(model="google:gemini-2.5-flash")

# Pre-configured model object
from langchain.chat_models import init_chat_model
model = init_chat_model("openai:gpt-4o", temperature=0)
agent = create_deep_agent(model=model)

# Default: claude-sonnet-4-20250514 (when model=None)
agent = create_deep_agent()
```

**Critical:** Deep agents require an LLM that supports tool calling. Models without tool-calling support will fail.

## System Prompt Design

The `system_prompt` parameter is **prepended** to a built-in `BASE_AGENT_PROMPT` that contains detailed guidance on using built-in tools (todos, filesystem, subagents).

```python
# GOOD: Focus on domain-specific behavior
agent = create_deep_agent(
    system_prompt=(
        "You are a financial research analyst. "
        "When researching companies, always check SEC filings first. "
        "Write structured reports with sections: Overview, Financials, Risks."
    ),
)

# BAD: Duplicating built-in instructions
agent = create_deep_agent(
    system_prompt=(
        "You have access to a filesystem. Use write_file to save files. "
        "You can create todos with write_todos..."  # Already in BASE_AGENT_PROMPT
    ),
)
```

## Invocation Patterns

```python
# Synchronous
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Analyze this dataset"}]},
    config={"configurable": {"thread_id": "thread-123"}}
)

# Streaming (recommended for long-running tasks)
for event in agent.stream(
    {"messages": [{"role": "user", "content": "Write a research report"}]},
    config={"configurable": {"thread_id": "thread-123"}},
    stream_mode="updates",
):
    print(event)

# Async
result = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "Research competitors"}]},
    config={"configurable": {"thread_id": "thread-123"}}
)
```

## Async Variant

```python
from deepagents import async_create_deep_agent

# Identical to create_deep_agent but passes is_async=True
# Affects SubAgentMiddleware tool execution and subagent invocation
agent = await async_create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[search_web],
)
```

## Default Middleware Stack

When you call `create_deep_agent()`, the following middleware is automatically attached:

1. **TodoListMiddleware** - Planning and task tracking
2. **FilesystemMiddleware** - File read/write/ls/search operations
3. **SubAgentMiddleware** - Sub-agent delegation via `task` tool
4. **SummarizationMiddleware** - Context compression for long conversations
5. **AnthropicPromptCachingMiddleware** - Token optimization (Anthropic models)
6. **PatchToolCallsMiddleware** - Fixes interrupted tool call history

Conditionally added:
- **SkillsMiddleware** - When `skills` argument is provided
- **HumanInTheLoopMiddleware** - When `interrupt_on` argument is provided

## Anti-Patterns

```python
# WRONG: No thread_id in config
result = agent.invoke({"messages": [...]})  # No persistence across turns

# WRONG: Recreating agent per request
def handle_request(message):
    agent = create_deep_agent(...)  # Expensive! Create once, reuse
    return agent.invoke({"messages": [message]})

# WRONG: Using invoke for long-running tasks
result = agent.invoke(...)  # Blocks until complete, no visibility

# CORRECT: Stream for long tasks
for event in agent.stream(..., stream_mode="updates"):
    process(event)

# WRONG: Mixing sync and async
agent = create_deep_agent(...)  # Sync agent
await agent.ainvoke(...)  # May cause issues with SubAgentMiddleware

# CORRECT: Use async_create_deep_agent for async contexts
agent = await async_create_deep_agent(...)
await agent.ainvoke(...)
```

## Checklist

- [ ] Model explicitly specified (don't rely on default)
- [ ] `system_prompt` focuses on domain behavior, not tool instructions
- [ ] `checkpointer` configured for production (SqliteSaver/PostgresSaver)
- [ ] `thread_id` passed in config for every invocation
- [ ] Streaming used for long-running agent tasks
- [ ] `async_create_deep_agent` used in async contexts
- [ ] Agent created once and reused across requests
