# Deep Agents Skill

Guide for working with LangChain's Deep Agents SDK using production-tested patterns and conventions.

## When to Use

- Creating deep agents with `create_deep_agent()`
- Configuring middleware stacks for context engineering
- Setting up backends for filesystem and memory persistence
- Designing sub-agent delegation patterns
- Implementing human-in-the-loop workflows
- Building production-grade agent systems on LangGraph

## Quick Start

1. **Agent creation**: See [create-deep-agent.md](create-deep-agent.md)
2. **Middleware setup**: See [middleware.md](middleware.md)
3. **Critical patterns**: [backends.md](backends.md), [sub-agents.md](sub-agents.md), [planning-and-todos.md](planning-and-todos.md)

## Core Patterns

| Pattern | File | One-Line Summary |
|---------|------|------------------|
| Agent Creation | [create-deep-agent.md](create-deep-agent.md) | `create_deep_agent()` is the single entry point - returns a compiled LangGraph |
| Middleware | [middleware.md](middleware.md) | Composable hooks for context engineering before/during model calls |
| Backends | [backends.md](backends.md) | StateBackend for ephemeral, CompositeBackend for hybrid persistence |
| Sub-Agents | [sub-agents.md](sub-agents.md) | Delegate to specialized agents for context isolation |
| Planning & Todos | [planning-and-todos.md](planning-and-todos.md) | Built-in `write_todos` tool for structured task decomposition |
| File Organization | [file-organization.md](file-organization.md) | Skills, subagents, and middleware in dedicated modules |
| Streaming & Persistence | [streaming-and-persistence.md](streaming-and-persistence.md) | Checkpointers for durable execution + 6 stream modes |
| Human-in-the-Loop | [human-in-the-loop.md](human-in-the-loop.md) | `interrupt_on` for per-tool approval workflows |
| Skills & Memory | [skills-and-memory.md](skills-and-memory.md) | Progressive disclosure of capabilities + cross-thread memory |

## Anti-Patterns (Quick Reference)

```python
# WRONG: Not passing a model - relies on default silently
agent = create_deep_agent()  # Uses claude-sonnet-4 by default, be explicit

# WRONG: Creating agents without a checkpointer in production
agent = create_deep_agent(model="anthropic:claude-sonnet-4-20250514")
# Missing checkpointer - no persistence, no HITL support

# WRONG: Overloading the main agent instead of delegating
agent = create_deep_agent(
    tools=[tool1, tool2, ..., tool50],  # Too many tools, context bloat
)
# Use sub-agents for context isolation instead

# WRONG: Using FilesystemBackend without virtual_mode in production
from deepagents.backends import FilesystemBackend
backend = FilesystemBackend(root_dir="/")  # Full filesystem access, no security

# WRONG: Putting all logic in system_prompt instead of middleware
agent = create_deep_agent(
    system_prompt="<5000 words of instructions>"  # Use middleware for context engineering
)

# WRONG: Using MemorySaver in production
from langgraph.checkpoint.memory import MemorySaver
agent = create_deep_agent(checkpointer=MemorySaver())  # In-memory only, use SqliteSaver/PostgresSaver
```

## Common Imports

```python
# Deep Agents Core
from deepagents import create_deep_agent, async_create_deep_agent

# Model Initialization
from langchain.chat_models import init_chat_model

# Middleware
from deepagents.middleware.subagents import SubAgentMiddleware
from deepagents.middleware.filesystem import FilesystemMiddleware
from deepagents.middleware.todolist import TodoListMiddleware
from deepagents.middleware.summarization import SummarizationMiddleware
from deepagents.middleware.hitl import HumanInTheLoopMiddleware
from deepagents.middleware.tool_selector import LLMToolSelectorMiddleware

# Backends
from deepagents.backends import (
    StateBackend,
    StoreBackend,
    FilesystemBackend,
    CompositeBackend,
)

# Sub-Agents
from deepagents import CompiledSubAgent

# LangGraph Runtime
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.memory import InMemoryStore

# Tools
from langchain.tools import tool

# Async
import asyncio
```

## References

### Middleware Types
See [references/middleware-types.md](references/middleware-types.md) for links to:
- TodoListMiddleware (Planning)
- FilesystemMiddleware (File Operations)
- SubAgentMiddleware (Delegation)
- SummarizationMiddleware (Context Compression)
- HumanInTheLoopMiddleware (Approval Workflows)
- LLMToolSelectorMiddleware (Tool Filtering)
- AnthropicPromptCachingMiddleware (Token Optimization)

### Architecture Patterns
See [references/architecture-patterns.md](references/architecture-patterns.md) for links to:
- Single Agent (Simple Tool Loop)
- Research Agent (Search + File Write)
- Content Builder (Multi-Subagent Pipeline)
- Hybrid Memory Agent (Ephemeral + Persistent)

## Related Skills

- **dspy**: DSPy framework patterns for declarative agent design
- **agent-spec-builder**: Design complete agent systems with framework-agnostic specs
- **agent-implementation-builder**: Build full agent teams from specifications
