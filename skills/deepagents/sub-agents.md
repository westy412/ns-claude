# Sub-Agents

Delegate to specialized agents for context isolation and focused task execution.

## The Problem

A single agent handling everything accumulates tool call results, search outputs, and intermediate data in its context window. After 10 web searches, the main agent's context is bloated with irrelevant results, degrading performance on subsequent tasks.

Sub-agents solve this by executing tasks in **isolated context windows**, returning only a summary to the parent agent.

## When to Use Sub-Agents

| Scenario | Use Sub-Agent? |
|----------|----------------|
| Simple tool call (weather, calculation) | No |
| Multiple sequential tool calls (same domain) | Maybe |
| Research requiring 5+ web searches | Yes |
| Task requiring specialized tools | Yes |
| Long-running analysis that bloats context | Yes |
| Parallel independent tasks | Yes |

## Three Ways to Define Sub-Agents

### 1. Inline Dictionary (Simplest)

```python
from deepagents import create_deep_agent

research_subagent = {
    "name": "research-agent",
    "description": "Used to research in-depth questions",
    "system_prompt": "You are a great researcher. Always cite sources.",
    "tools": [search_web],
    "model": "openai:gpt-4o",  # Optional: override main agent model
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

```python
from deepagents.middleware.subagents import SubAgentMiddleware
from deepagents import CompiledSubAgent

# Your custom LangGraph graph
weather_graph = create_weather_graph()

weather_subagent = CompiledSubAgent(
    name="weather",
    description="Handles all weather-related queries.",
    runnable=weather_graph,
)

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    subagents=[weather_subagent],
)
```

## Built-In General-Purpose Sub-Agent

Every deep agent automatically has access to a **general-purpose subagent** that mirrors the main agent's capabilities (same system prompt, tools, and model). This is perfect for context isolation without specialized behavior.

```
Main Agent: "I need to do 10 web searches, but I don't want to bloat my context."
    │
    ▼
General-Purpose Subagent: Performs all 10 searches in its own context
    │
    ▼
Returns: Summary of findings only (context stays clean)
```

## Sub-Agent Invocation (task tool)

The main agent delegates to sub-agents using the `task` tool:

```
Main Agent receives user query
    │
    ▼
Main Agent calls task(name="research-agent", instructions="Research X")
    │
    ▼
research-agent runs in isolated context with its own tools
    │
    ▼
research-agent returns summary to Main Agent
    │
    ▼
Main Agent continues with clean context
```

## Default Middleware for Sub-Agents

When using `create_deep_agent`, sub-agents automatically receive:

1. **TodoListMiddleware** - Sub-agents can plan their own work
2. **FilesystemMiddleware** - Sub-agents can read/write files
3. **SummarizationMiddleware** - Long sub-agent conversations get compressed

Plus any custom middleware specified in the subagent definition.

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

### Specialized Tool Agents

```python
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    subagents=[
        {
            "name": "data-analyst",
            "description": "Analyzes data using Python and SQL",
            "system_prompt": "You are a data analyst. Write and execute code.",
            "tools": [python_repl, sql_query],
        },
        {
            "name": "api-integrator",
            "description": "Interacts with external APIs",
            "system_prompt": "You manage API integrations.",
            "tools": [http_get, http_post],
        },
    ],
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

## Concurrent Sub-Agent Execution

The main agent can launch multiple sub-agents concurrently by making multiple tool calls in a single turn:

```
Main Agent:
  - task(name="researcher", instructions="Research topic A")
  - task(name="researcher", instructions="Research topic B")
  - task(name="researcher", instructions="Research topic C")

All three run in parallel → results combined
```

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

## Checklist

- [ ] Each sub-agent has a clear, specific `description`
- [ ] `system_prompt` provides domain-specific guidance
- [ ] Tools scoped to what the sub-agent needs (not everything)
- [ ] Model chosen based on task complexity (Haiku for bulk, Sonnet for synthesis)
- [ ] General-purpose subagent used for simple context isolation
- [ ] CompiledSubAgent used for complex custom workflows
- [ ] Sub-agents not used for trivial tasks (use tools directly)
