# Middleware Types Reference

All available middleware in the Deep Agents SDK.

## Default Middleware (Auto-Attached)

| Middleware | Purpose | Hook Used |
|-----------|---------|-----------|
| **TodoListMiddleware** | Task planning and progress tracking | `before_agent` + `wrap_model_call` |
| **FilesystemMiddleware** | File read/write/ls/search operations | `before_agent` + `wrap_model_call` |
| **SubAgentMiddleware** | Sub-agent delegation via `task` tool | `wrap_model_call` |
| **SummarizationMiddleware** | Context compression for long conversations | `wrap_model_call` |
| **AnthropicPromptCachingMiddleware** | Token optimization for Anthropic models | `wrap_model_call` |
| **PatchToolCallsMiddleware** | Fix interrupted tool call history | `before_agent` |

## Conditional Middleware

| Middleware | Trigger | Purpose |
|-----------|---------|---------|
| **SkillsMiddleware** | `skills` argument provided | Progressive skill loading |
| **HumanInTheLoopMiddleware** | `interrupt_on` argument provided | Per-tool approval workflows |

## Optional Middleware

| Middleware | Purpose | When to Use |
|-----------|---------|-------------|
| **LLMToolSelectorMiddleware** | Filters tools before main model call | Agent has 10+ tools |

## Quick Selection Guide

```
Does the agent have many tools (10+)?
├── YES → Add LLMToolSelectorMiddleware
└── NO → Default stack is sufficient

Does the agent need human approval for some actions?
├── YES → Use interrupt_on parameter (auto-adds HumanInTheLoopMiddleware)
└── NO → Default stack is sufficient

Does the agent need domain expertise?
├── YES → Use skills parameter (auto-adds SkillsMiddleware)
└── NO → Default stack is sufficient

Does the agent need custom behavior?
├── YES → Write custom AgentMiddleware class
└── NO → Default stack is sufficient
```

## Middleware Details

### TodoListMiddleware
- **Tools provided:** `write_todos`
- **State populated:** Todo list state
- **Constraint:** `write_todos` called at most once per model turn
- **System prompt:** Injects guidance on when to use planning
- **Documentation:** [planning-and-todos.md](../planning-and-todos.md)

### FilesystemMiddleware
- **Tools provided:** `ls`, `read_file`, `write_file`, `search_files`
- **State populated:** Filesystem state from backend
- **Configuration:** Backend, custom system prompt, custom tool descriptions
- **Documentation:** [backends.md](../backends.md)

### SubAgentMiddleware
- **Tools provided:** `task`
- **Configuration:** Default model, default tools, subagent definitions
- **Feature:** Sub-agents receive their own default middleware stack
- **Documentation:** [sub-agents.md](../sub-agents.md)

### SummarizationMiddleware
- **Trigger:** Message token count exceeds threshold
- **Behavior:** Summarizes older messages, preserves recent ones
- **Configuration:** `message_threshold` parameter
- **Smart behavior:** Keeps AI/Tool message pairs together during summarization

### AnthropicPromptCachingMiddleware
- **Purpose:** Reduces redundant token processing for Anthropic models
- **Configuration:** Automatic, no user configuration needed
- **Scope:** Only active when using Anthropic models

### PatchToolCallsMiddleware
- **Purpose:** Fixes message history when tool calls are interrupted or cancelled
- **Behavior:** Ensures tool call / tool result pairs are consistent
- **Configuration:** Automatic, no user configuration needed

### LLMToolSelectorMiddleware
- **Purpose:** Uses a fast LLM to pre-filter relevant tools
- **Configuration:** Selector model (recommend Haiku for speed/cost)
- **When to use:** Agent has 10+ tools and token usage is a concern

### HumanInTheLoopMiddleware
- **Purpose:** Pauses agent for human approval on configured tools
- **Requires:** Checkpointer for state persistence
- **Configuration:** Per-tool interrupt behavior via `interrupt_on`
- **Documentation:** [human-in-the-loop.md](../human-in-the-loop.md)

### SkillsMiddleware
- **Purpose:** Progressive loading of skill files
- **Configuration:** Skill directory paths via `skills` parameter
- **Requires:** Backend with access to skill files
- **Documentation:** [skills-and-memory.md](../skills-and-memory.md)

## Middleware Execution Order

```
1. PatchToolCallsMiddleware.before_agent()    ← Fix history
2. TodoListMiddleware.before_agent()          ← Load todos
3. FilesystemMiddleware.before_agent()        ← Load filesystem state
4. SubAgentMiddleware.before_agent()          ← Configure subagents
5. [SkillsMiddleware.before_agent()]          ← Load skill index (if enabled)
6. SummarizationMiddleware.before_agent()     ← Check token limits
    │
    ▼
Agent Loop:
    7. LLMToolSelectorMiddleware.wrap()       ← Filter tools (if enabled)
    8. AnthropicPromptCachingMiddleware.wrap() ← Optimize tokens
    9. [Custom middleware].wrap()              ← Your extensions
   10. [HumanInTheLoopMiddleware].wrap()      ← Intercept tool calls (if enabled)
    │
    ▼
Model Call → Tool Execution → Loop
```

## See Also

- [Middleware Patterns](../middleware.md) - Writing and configuring middleware
- [Architecture Patterns](architecture-patterns.md) - How middleware enables agent patterns
