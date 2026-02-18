# Architecture Patterns Reference

Common agent architectures built with Deep Agents SDK.

## Available Patterns

| Pattern | Complexity | Use Case | Key Features |
|---------|-----------|----------|--------------|
| Single Agent | Simple | General tasks, Q&A | Tools + planning |
| Research Agent | Moderate | Deep research, reports | Search tools + filesystem |
| Content Builder | Complex | Multi-format content | Multiple sub-agents |
| Hybrid Memory Agent | Complex | Long-running assistants | Persistent memory + ephemeral working |
| Approval Pipeline | Moderate | Sensitive operations | HITL on destructive actions |

## Pattern Overviews

### Single Agent (Simple Tool Loop)

```
User -> Agent -> [Tool Calls] -> Response
              +- write_todos
              +- read_file / write_file
              +- custom_tools
```

The simplest pattern. One agent with tools, planning, and filesystem access.

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[search_web, calculate],
    system_prompt="You are a helpful assistant.",
)
```

**Best for:** General Q&A, simple tasks, prototyping.

### Research Agent (Search + File Write)

```
User -> Agent -> [Plan] -> [Search x N] -> [Write Notes] -> [Write Report] -> Response
```

Agent plans research, executes searches, writes findings to filesystem, produces structured output.

```python
from deepagents import create_deep_agent
from langchain.tools import tool

@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    return tavily_search(query)

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[search_web],
    system_prompt=(
        "You are an expert researcher. For every research task:\n"
        "1. Create a plan with write_todos\n"
        "2. Search for information using search_web\n"
        "3. Write detailed notes to the filesystem\n"
        "4. Produce a polished report\n"
        "Always cite your sources."
    ),
)
```

**Best for:** Deep research, report generation, competitive analysis.

### Content Builder (Multi-Subagent Pipeline)

```
User -> Coordinator -> task(researcher) -> task(writer) -> task(designer) -> Response
           |              |                  |               |
           |         Searches web      Reads notes     Creates assets
           |         Writes notes      Writes draft    Writes images
           |
           +- Orchestrates pipeline, reviews output
```

Main agent coordinates specialized sub-agents that each handle one phase.

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    subagents=[
        {
            "name": "researcher",
            "description": "Researches topics thoroughly",
            "system_prompt": "Search, evaluate sources, write notes.",
            "tools": [search_web, scrape_url],
        },
        {
            "name": "writer",
            "description": "Writes polished content from notes",
            "system_prompt": "Read notes, produce structured reports.",
            "tools": [],
        },
        {
            "name": "reviewer",
            "description": "Reviews content for quality and accuracy",
            "system_prompt": "Check facts, grammar, structure. Provide feedback.",
            "tools": [],
        },
    ],
    system_prompt=(
        "You are a content production coordinator.\n"
        "1. Delegate research to the researcher\n"
        "2. Delegate writing to the writer\n"
        "3. Delegate review to the reviewer\n"
        "4. Present final content to the user"
    ),
)
```

**Best for:** Blog posts, reports, multi-format content creation.

### Hybrid Memory Agent (Persistent + Ephemeral)

```
User -> Agent -> Check /memories/ -> Plan -> Execute -> Save findings to /memories/
                    |                                       |
                    +-- Cross-thread persistent -------------+
                    |
               Working files (ephemeral, thread-local)
```

Combines ephemeral working files with persistent memory for long-running assistants.

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    checkpointer=PostgresSaver.from_conn_string("postgresql://..."),
    store=PostgresStore.from_conn_string("postgresql://..."),
    backend=lambda rt: CompositeBackend(
        default=StateBackend(rt),
        routes={"/memories/": StoreBackend(rt)},
    ),
    memory=["/memories/"],
    system_prompt=(
        "You are a persistent assistant. At the start of each conversation:\n"
        "1. Check /memories/ for relevant context\n"
        "2. Use working files for intermediate work\n"
        "3. Save important findings to /memories/ for future reference"
    ),
)
```

**Best for:** Personal assistants, long-running projects, learning agents.

### Approval Pipeline (HITL)

```
User -> Agent -> Plan -> [Auto: read, search] -> [HITL: write, send, delete] -> Response
                                                      |
                                                Human approves/rejects
```

Combines autonomous execution for safe operations with human approval for sensitive ones.

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.postgres import PostgresSaver

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[read_file, write_file, send_email, delete_file, search_web],
    checkpointer=PostgresSaver.from_conn_string("postgresql://..."),
    interrupt_on={
        "write_file": True,
        "send_email": {"allowed_decisions": ["approve", "edit", "reject"]},
        "delete_file": {"allowed_decisions": ["approve", "reject"]},
        # read_file and search_web auto-execute
    },
)
```

**Best for:** Enterprise workflows, regulated environments, external communications.

## Pattern Selection Guide

```
What is your primary use case?
+-- Simple Q&A or task completion
|   +-- Single Agent
+-- Research and report writing
|   +-- Short research (5 min)
|   |   +-- Research Agent (single agent + search)
|   +-- Deep research (30+ min)
|       +-- Content Builder (researcher + writer sub-agents)
+-- Long-running assistant with memory
|   +-- Hybrid Memory Agent
+-- Sensitive operations requiring approval
|   +-- Approval Pipeline
+-- Complex multi-phase workflow
    +-- Content Builder (customize sub-agents per phase)
```

## Pattern Combinations

Patterns can be combined:

```
Hybrid Memory + Content Builder + Approval Pipeline
    |
    +-- Persistent memory across sessions
    +-- Specialized sub-agents for each phase
    +-- HITL approval for external communications
```

## Common Configurations

| Use Case | Pattern | Model | Sub-Agents | Backend |
|----------|---------|-------|------------|---------|
| Chatbot | Single Agent | Sonnet | None | StateBackend |
| Research tool | Research Agent | Sonnet | None | StateBackend |
| Content pipeline | Content Builder | Sonnet (main) + Haiku (bulk) | 2-4 | StateBackend |
| Personal assistant | Hybrid Memory | Sonnet | 1-2 | CompositeBackend |
| Enterprise workflow | Approval Pipeline | Sonnet | 1-3 | CompositeBackend |

## See Also

- [Middleware](middleware.md) - Middleware that powers each pattern
- [Subagents](subagents.md) - Sub-agent delegation patterns
- [Memory and Backends](memory-and-backends.md) - Storage configuration for each pattern
- [Streaming](streaming.md) - Real-time event output during execution
- [Persistence](persistence.md) - Checkpointers and durable state storage
