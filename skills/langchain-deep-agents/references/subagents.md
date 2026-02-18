# Subagents Reference

Subagents solve the context bloat problem. When agents use tools with large outputs, the context window fills up. Subagents isolate this detailed work in a separate context window -- the main agent receives only the final result.

---

## When to Use Subagents

| Situation | Use? | Why |
|-----------|------|-----|
| Multi-step tasks cluttering main context | Yes | Isolates detailed work |
| Specialized domain needing custom instructions/tools | Yes | Dedicated system prompt and toolset |
| Task requiring a different model | Yes | Override model per subagent |
| Main agent should focus on high-level coordination | Yes | Keeps orchestrator context clean |
| Simple, single-step task | No | Overhead outweighs benefit |
| Intermediate context must be maintained in parent | No | Subagent context is isolated |

---

## SubAgent (Dictionary-Based)

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Unique identifier |
| `description` | `str` | What this subagent does (agent uses this to decide when to delegate) |
| `system_prompt` | `str` | Instructions for the subagent |
| `tools` | `list[Callable]` | Tools the subagent can use |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `model` | `str \| BaseChatModel` | Override the main agent's model |
| `middleware` | `list[Middleware]` | Additional middleware |
| `interrupt_on` | `dict[str, bool]` | HITL for specific tools |
| `skills` | `list[str]` | Skills source paths (custom subagents do NOT inherit main agent skills) |
| `response_format` | `type[BaseModel]` | Pydantic model for structured output (data captured but not auto-returned to parent) |

### Example

```python
research_subagent = {
    "name": "research-agent",
    "description": "Used to research more in depth questions",
    "system_prompt": "You are a great researcher",
    "tools": [internet_search],
    "model": "openai:gpt-4.1",  # Optional override
}

agent = create_deep_agent(
    model="claude-sonnet-4-5-20250929",
    subagents=[research_subagent]
)
```

---

## CompiledSubAgent

For complex workflows, wrap a pre-built LangGraph graph as a subagent.

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Unique identifier |
| `description` | `str` | What this subagent does |
| `runnable` | `Runnable` | Compiled LangGraph graph (must have `"messages"` state key) |

```python
from deepagents import create_deep_agent, CompiledSubAgent
from langchain.agents import create_agent

custom_graph = create_agent(
    model=your_model,
    tools=specialized_tools,
    prompt="You are a specialized agent for data analysis..."
)

custom_subagent = CompiledSubAgent(
    name="data-analyzer",
    description="Specialized agent for complex data analysis tasks",
    runnable=custom_graph
)

agent = create_deep_agent(
    model="claude-sonnet-4-5-20250929",
    subagents=[custom_subagent]
)
```

---

## General-Purpose Subagent

Always available without configuration. Shares the main agent's system prompt, tools, model, and skills.

```python
# Invoked via task tool at runtime
task(name="general-purpose", task="Research quantum computing trends")
```

Ideal for context isolation without specialized behavior.

---

## Skills Inheritance

| Subagent Type | Inherits Skills? | How to Configure |
|---------------|-----------------|------------------|
| General-purpose | Yes, automatically | No config needed |
| Custom (dict) | No, must be explicit | Use `skills` parameter |
| CompiledSubAgent | No, self-contained | Skills managed within graph |

Skill state is fully isolated in both directions.

```python
research_subagent = {
    "name": "researcher",
    "description": "Research assistant with specialized skills",
    "system_prompt": "You are a researcher.",
    "tools": [web_search],
    "skills": ["/skills/research/", "/skills/web-search/"],
}

agent = create_deep_agent(
    model="claude-sonnet-4-5-20250929",
    skills=["/skills/main/"],  # Main + GP subagent get these
    subagents=[research_subagent],  # Gets only its own skills
)
```

---

## Streaming

Use `lc_agent_name` in event metadata to differentiate agents:

```python
agent = create_deep_agent(
    model="claude-sonnet-4-5-20250929",
    subagents=[research_subagent],
    name="main-agent"
)
# event.metadata["lc_agent_name"] -> "main-agent" or "research-agent"
```

---

## Structured Output

Subagents support structured output via `response_format`. The structured data is captured and validated but **not** automatically returned to the parent -- include it in the `ToolMessage`.

---

## Multiple Specialized Subagents Pattern

```python
research_subagent = {
    "name": "researcher",
    "description": "Researches topics using web search. Use for up-to-date information.",
    "system_prompt": "Search multiple sources, cross-reference, return concise summary with citations.",
    "tools": [web_search, scrape_page],
    "model": "openai:gpt-4.1",
}

analyst_subagent = {
    "name": "data-analyst",
    "description": "Analyzes datasets. Use when user provides data or asks for quantitative analysis.",
    "system_prompt": "Load data, compute statistics, generate charts, return key findings.",
    "tools": [python_repl, file_reader],
}

writer_subagent = {
    "name": "writer",
    "description": "Writes polished content. Use after research/analysis for final documents.",
    "system_prompt": "Produce clear, well-structured documents from research and analysis.",
    "tools": [file_writer],
}

agent = create_deep_agent(
    model="claude-sonnet-4-5-20250929",
    subagents=[research_subagent, analyst_subagent, writer_subagent],
)
```

---

## Best Practices

- **Descriptions**: Be specific ("Analyzes CSV data and produces charts" not "Does analysis")
- **System prompts**: Include tool usage guidance and output format requirements
- **Tools**: Minimize per subagent -- only what's needed
- **Models**: Cheaper models for simple tasks, stronger for complex reasoning
- **Return values**: Subagents should return concise results to avoid defeating context isolation

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Subagent not called | Make description more specific |
| Wrong subagent selected | Make descriptions more distinct |
| Context still bloated | Ensure main agent delegates rather than duplicates |
| Skills missing in custom subagent | Add `skills` parameter with explicit paths |
| CompiledSubAgent not working | Call `.compile()` and verify `messages` state key |

---

## Documentation Links

- [Subagents Guide](https://docs.langchain.com/oss/python/deepagents/subagents) — Full subagents documentation including SubAgent dict, CompiledSubAgent, general-purpose subagent, and skills inheritance
- [Subagents API Reference](https://docs.langchain.com/oss/python/deepagents/api/subagents) — API reference for SubAgent, CompiledSubAgent, and SubAgentMiddleware
- [Streaming Docs](https://docs.langchain.com/oss/python/deepagents/streaming) — Streaming events and `lc_agent_name` metadata for differentiating agent output
