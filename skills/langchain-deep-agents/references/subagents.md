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
| Research requiring 5+ web searches | Yes | Context isolation for large outputs |
| Parallel independent tasks | Yes | Concurrent execution |
| Simple, single-step task | No | Overhead outweighs benefit |
| Intermediate context must be maintained in parent | No | Subagent context is isolated |

---

## Three Ways to Define Subagents

### 1. Inline Dictionary (Simplest)

#### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Unique identifier |
| `description` | `str` | What this subagent does (agent uses this to decide when to delegate) |
| `system_prompt` | `str` | Instructions for the subagent |
| `tools` | `list[Callable]` | Tools the subagent can use |

#### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `model` | `str \| BaseChatModel` | Override the main agent's model |
| `middleware` | `list[Middleware]` | Additional middleware |
| `interrupt_on` | `dict[str, bool]` | HITL for specific tools |
| `skills` | `list[str]` | Skills source paths (custom subagents do NOT inherit main agent skills) |
| `response_format` | `type[BaseModel]` | Pydantic model for structured output (data captured but not auto-returned to parent) |

```python
from deepagents import create_deep_agent

research_subagent = {
    "name": "research-agent",
    "description": "Used to research in-depth questions",
    "system_prompt": "You are a great researcher. Always cite sources.",
    "tools": [search_web],
    "model": "openai:gpt-4.1",  # Optional: override main agent model
}

writer_subagent = {
    "name": "writer-agent",
    "description": "Used to write polished content from research notes",
    "system_prompt": "You are a professional technical writer.",
    "tools": [],
    "model": "anthropic:claude-sonnet-4-20250514",
}

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    subagents=[research_subagent, writer_subagent],
)
```

### 2. SubAgentMiddleware (Lower-Level Control)

```python
from langchain.tools import tool
from langchain.agents import create_agent
from deepagents.middleware.subagents import SubAgentMiddleware

@tool
def get_weather(city: str) -> str:
    """Get the weather in a city."""
    return f"The weather in {city} is sunny."

agent = create_agent(
    model="anthropic:claude-sonnet-4-20250514",
    middleware=[
        SubAgentMiddleware(
            default_model="anthropic:claude-sonnet-4-20250514",
            default_tools=[],
            subagents=[
                {
                    "name": "weather",
                    "description": "Gets weather information for cities.",
                    "system_prompt": "Use the get_weather tool to get weather data.",
                    "tools": [get_weather],
                    "model": "openai:gpt-4.1",  # Different model per subagent
                    "middleware": [],  # Custom middleware stack
                }
            ],
        )
    ],
)
```

### 3. CompiledSubAgent (Pre-Built LangGraph)

For complex workflows that need their own graph structure:

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
    runnable=custom_graph,
)

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    subagents=[custom_subagent],
)
```

---

## General-Purpose Subagent

Always available without configuration. Shares the main agent's system prompt, tools, model, and skills.

```python
# Invoked via task tool at runtime
task(name="general-purpose", task="Research quantum computing trends")
```

Ideal for context isolation without specialized behavior:

```
Main Agent: "I need to do 10 web searches, but I don't want to bloat my context."
    |
    v
General-Purpose Subagent: Performs all 10 searches in its own context
    |
    v
Returns: Summary of findings only (context stays clean)
```

---

## Sub-Agent Invocation (task tool)

The main agent delegates to sub-agents using the `task` tool:

```
Main Agent receives user query
    |
    v
Main Agent calls task(name="research-agent", instructions="Research X")
    |
    v
research-agent runs in isolated context with its own tools
    |
    v
research-agent returns summary to Main Agent
    |
    v
Main Agent continues with clean context
```

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

## Default Middleware for Sub-Agents

When using `create_deep_agent`, sub-agents automatically receive:

1. **TodoListMiddleware** - Sub-agents can plan their own work
2. **FilesystemMiddleware** - Sub-agents can read/write files
3. **SummarizationMiddleware** - Long sub-agent conversations get compressed

Plus any custom middleware specified in the subagent definition.

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

## Concurrent Sub-Agent Execution

The main agent can launch multiple sub-agents concurrently by making multiple tool calls in a single turn:

```
Main Agent:
  - task(name="researcher", instructions="Research topic A")
  - task(name="researcher", instructions="Research topic B")
  - task(name="researcher", instructions="Research topic C")

All three run in parallel -> results combined
```

---

## Sub-Agent Design Patterns

### Research + Writer Pipeline

```python
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[],  # Main agent orchestrates, doesn't need tools
    subagents=[
        {
            "name": "researcher",
            "description": "Conducts thorough web research on a topic",
            "system_prompt": (
                "You are an expert researcher. Search thoroughly, "
                "read multiple sources, and write detailed notes to the filesystem."
            ),
            "tools": [search_web, scrape_url],
            "model": "anthropic:claude-sonnet-4-20250514",
        },
        {
            "name": "writer",
            "description": "Writes polished reports from research notes",
            "system_prompt": (
                "You are a professional writer. Read research notes from the "
                "filesystem and produce a polished, well-structured report."
            ),
            "tools": [],
            "model": "anthropic:claude-sonnet-4-20250514",
        },
    ],
    system_prompt=(
        "You are a research coordinator. For any research task:\n"
        "1. Delegate research to the researcher subagent\n"
        "2. Then delegate report writing to the writer subagent\n"
        "3. Review the final report and present to the user"
    ),
)
```

### Cost-Optimized Delegation

```python
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",  # Main: smart orchestrator
    subagents=[
        {
            "name": "bulk-processor",
            "description": "Processes large batches of simple tasks",
            "system_prompt": "Process each item in the batch efficiently.",
            "tools": [process_item],
            "model": "anthropic:claude-haiku-4-5-20251001",  # Cheap for bulk work
        },
        {
            "name": "quality-reviewer",
            "description": "Reviews and validates complex outputs",
            "system_prompt": "Carefully review the output for quality.",
            "tools": [],
            "model": "anthropic:claude-sonnet-4-20250514",  # Smart for review
        },
    ],
)
```

---

## Anti-Patterns

```python
# WRONG: Sub-agent for simple tasks
subagents=[
    {
        "name": "calculator",
        "description": "Adds two numbers",  # Too simple, just use a tool
        "tools": [add_numbers],
    }
]

# WRONG: Sub-agent with no description
subagents=[
    {
        "name": "helper",
        "description": "",  # Main agent can't decide when to delegate
    }
]

# WRONG: Sub-agent duplicating main agent's capabilities
agent = create_deep_agent(
    tools=[search_web],  # Main agent has search
    subagents=[
        {
            "name": "searcher",
            "tools": [search_web],  # Redundant! Use general-purpose subagent
        }
    ],
)

# WRONG: No system_prompt for specialized subagent
subagents=[
    {
        "name": "researcher",
        "description": "Researches topics",
        "system_prompt": "",  # No guidance, subagent won't know how to behave
        "tools": [search_web],
    }
]
```

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

## Best Practices

- **Descriptions**: Be specific ("Analyzes CSV data and produces charts" not "Does analysis")
- **System prompts**: Include tool usage guidance and output format requirements
- **Tools**: Minimize per subagent -- only what's needed
- **Models**: Cheaper models for simple tasks, stronger for complex reasoning
- **Return values**: Subagents should return concise results to avoid defeating context isolation

---

## Checklist

- [ ] Each sub-agent has a clear, specific `description`
- [ ] `system_prompt` provides domain-specific guidance
- [ ] Tools scoped to what the sub-agent needs (not everything)
- [ ] Model chosen based on task complexity (Haiku for bulk, Sonnet for synthesis)
- [ ] General-purpose subagent used for simple context isolation
- [ ] CompiledSubAgent used for complex custom workflows
- [ ] Sub-agents not used for trivial tasks (use tools directly)

---

## Documentation Links

- [Subagents Guide](https://docs.langchain.com/oss/python/deepagents/subagents) -- Full subagents documentation
- [Subagents API Reference](https://docs.langchain.com/oss/python/deepagents/api/subagents) -- API reference for SubAgent, CompiledSubAgent, and SubAgentMiddleware
- [Streaming Docs](https://docs.langchain.com/oss/python/deepagents/streaming) -- Streaming events and `lc_agent_name` metadata
