---
name: langchain-deep-agents
description: Comprehensive guide for building agents with the LangChain Deep Agents SDK. Use when creating, customizing, or debugging LangChain Deep Agents -- covers create_deep_agent, subagents, memory, backends, skills, sandboxes, middleware, and human-in-the-loop.
metadata:
  tags: langchain, deep-agents, langgraph, agent, subagent, memory, skills, sandbox
---

# LangChain Deep Agents SDK

> **Invoke with:** `/deep-agents` | **Keywords:** deep agents, langchain, langgraph, create_deep_agent, subagent, memory, backend, skills, sandbox, middleware

A comprehensive guide for building, customizing, and debugging agents with the LangChain Deep Agents SDK. Use this skill when you need to:
- Create a new deep agent from scratch
- Add subagents, memory, skills, or sandboxes
- Configure middleware or human-in-the-loop
- Troubleshoot context management or agent behavior

---

## Purpose

This skill provides reference material for the LangChain Deep Agents SDK (`deepagents` package), an opinionated agent harness built on LangGraph with built-in planning, file systems, subagent spawning, and context management.

## Reference Files

Choose the appropriate reference based on your task:

| Task | Reference File | Description |
|------|----------------|-------------|
| **Create an agent** | [getting-started.md](./references/getting-started.md) | Installation, full `create_deep_agent` API, models, tools, system prompts, invocation patterns, quickstart |
| **Add subagents** | [subagents.md](./references/subagents.md) | SubAgent dict, CompiledSubAgent, general-purpose subagent, design patterns, skills inheritance, streaming |
| **Configure memory & backends** | [memory-and-backends.md](./references/memory-and-backends.md) | StateBackend, FilesystemBackend, StoreBackend, CompositeBackend, FileData, LangSmith, long-term memory |
| **Add skills** | [skills-system.md](./references/skills-system.md) | SKILL.md format, progressive disclosure, backend-specific usage, subagent skills, skills vs tools |
| **Use sandboxes** | [sandboxes.md](./references/sandboxes.md) | Modal, Runloop, Daytona -- isolated code execution environments |
| **Configure middleware** | [middleware.md](./references/middleware.md) | Middleware protocol, default stack, custom middleware, `@wrap_tool_call`, execution flow |
| **Human-in-the-loop** | [human-in-the-loop.md](./references/human-in-the-loop.md) | `interrupt_on`, decisions, resume with `Command`, subagent overrides, `interrupt()` |
| **Planning & todos** | [planning-and-todos.md](./references/planning-and-todos.md) | `write_todos` tool, task decomposition, adaptive planning |
| **Streaming** | [streaming.md](./references/streaming.md) | 6 stream modes, real-time events, subagent streaming, async streaming |
| **Persistence** | [persistence.md](./references/persistence.md) | Checkpointers, thread management, crash recovery, SqliteSaver vs PostgresSaver |
| **File organization** | [file-organization.md](./references/file-organization.md) | Project structure, module layout, YAML configs |
| **Architecture patterns** | [architecture-patterns.md](./references/architecture-patterns.md) | Single agent, research agent, content builder, hybrid memory, approval pipeline |

> **Maintenance Note**: If any patterns in the reference files are found to be incorrect during implementation, update the corresponding reference file with the correct pattern.

---

## Core Concepts

### What is LangChain Deep Agents?

LangChain Deep Agents is an **agent harness** -- the same core tool-calling loop as other agent frameworks, but with built-in tools and capabilities for complex, multi-step tasks. It is built on top of LangChain's core building blocks and uses the LangGraph runtime.

### Four Pillars

| Pillar | Built-in Tool | Purpose |
|--------|--------------|---------|
| **Planning** | `write_todos` | Task decomposition and progress tracking |
| **File System** | `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep` | Context management via virtual filesystem |
| **Subagents** | `task` | Delegate work with isolated context windows |
| **Context Management** | `SummarizationMiddleware` | Auto-compression when conversations grow long |

### When to Use LangChain Deep Agents vs Alternatives

| Scenario | Use |
|----------|-----|
| Complex, multi-step tasks requiring planning | **LangChain Deep Agents** |
| Large context management via file systems | **LangChain Deep Agents** |
| Delegation to specialized subagents | **LangChain Deep Agents** |
| Simple agent with a few tools | `create_agent` (LangChain) |
| Custom graph logic with fine-grained control | LangGraph directly |

---

## Quick Reference

### create_deep_agent Signature

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

### Minimal Agent

```python
from deepagents import create_deep_agent

agent = create_deep_agent()
result = agent.invoke({"messages": [{"role": "user", "content": "Research quantum computing"}]})
print(result["messages"][-1].content)
```

### Agent with Custom Tools and Subagents

```python
agent = create_deep_agent(
    model="openai:gpt-5.2",
    tools=[internet_search],
    system_prompt="You are a research assistant.",
    subagents=[{
        "name": "researcher",
        "description": "Conducts in-depth web research",
        "system_prompt": "Search thoroughly and return concise summaries.",
        "tools": [internet_search],
    }]
)
```

### Agent with Long-Term Memory

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    store=InMemoryStore(),
    backend=lambda rt: CompositeBackend(
        default=StateBackend(rt),
        routes={"/memories/": StoreBackend(rt)}
    ),
    checkpointer=MemorySaver(),
    system_prompt="Save user preferences to /memories/preferences.txt"
)
```

---

## Built-in Tools

| Tool | Category | Purpose |
|------|----------|---------|
| `write_todos` | Planning | Task decomposition |
| `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep` | File System | Context management |
| `execute` | Shell | Run commands (sandboxed) |
| `task` | Orchestration | Spawn subagents |

---

## Default Middleware Stack

| Middleware | Purpose |
|-----------|---------|
| `TodoListMiddleware` | Task planning |
| `FilesystemMiddleware` | File operations |
| `SubAgentMiddleware` | Subagent coordination |
| `SummarizationMiddleware` | Context compression |
| `AnthropicPromptCachingMiddleware` | Token efficiency |
| `PatchToolCallsMiddleware` | Interrupted tool call fixes |

---

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

---

## Documentation Links

- **Docs**: https://docs.langchain.com/oss/python/deepagents/overview
- **GitHub**: https://github.com/langchain-ai/deepagents
- **API Reference**: https://reference.langchain.com/python/deepagents/
- **JS/TS**: https://github.com/langchain-ai/deepagentsjs
- **CLI**: https://docs.langchain.com/oss/python/deepagents/cli

## Related Skills

- **dspy**: DSPy framework patterns for declarative agent design
- **agent-spec-builder**: Design complete agent systems with framework-agnostic specs
- **agent-implementation-builder**: Build full agent teams from specifications
