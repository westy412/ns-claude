# File Organization

How to structure Deep Agents projects, skills, and sub-agent definitions.

## Project Directory Structure

```
my-agent/
├── agent.py              # create_deep_agent() entry point
├── tools.py              # Custom tool definitions
├── subagents.py          # Sub-agent configurations
├── middleware.py          # Custom middleware (if any)
├── config.py             # Model, backend, and environment config
├── skills/               # Skill directories (loaded via skills parameter)
│   ├── research/
│   │   └── SKILL.md
│   └── writing/
│       └── SKILL.md
└── requirements.txt      # Dependencies
```

## Key Rules

### 1. Agent Creation in agent.py

```python
# agent.py - Entry point for agent creation

from deepagents import create_deep_agent
from .tools import search_web, scrape_url
from .subagents import RESEARCH_SUBAGENT, WRITER_SUBAGENT
from .config import get_model, get_checkpointer, get_backend

def create_agent():
    """Create and return the production agent."""
    return create_deep_agent(
        model=get_model(),
        tools=[search_web, scrape_url],
        subagents=[RESEARCH_SUBAGENT, WRITER_SUBAGENT],
        system_prompt=(
            "You are a research coordinator. "
            "Delegate research tasks to specialized sub-agents."
        ),
        checkpointer=get_checkpointer(),
        backend=get_backend(),
        name="research-coordinator",
    )
```

### 2. Tool Definitions in tools.py

```python
# tools.py - All custom tool definitions

from langchain.tools import tool

@tool
def search_web(query: str) -> str:
    """Search the web for information on a topic."""
    # Implementation
    return results

@tool
def scrape_url(url: str) -> str:
    """Scrape and extract content from a URL."""
    # Implementation
    return content
```

### 3. Sub-Agent Configs in subagents.py

```python
# subagents.py - Sub-agent definitions

RESEARCH_SUBAGENT = {
    "name": "researcher",
    "description": "Conducts thorough web research on a topic",
    "system_prompt": (
        "You are an expert researcher. Search thoroughly, "
        "read multiple sources, and write detailed notes."
    ),
    "tools": [],  # Tools injected from tools.py at agent creation
    "model": "anthropic:claude-sonnet-4-20250514",
}

WRITER_SUBAGENT = {
    "name": "writer",
    "description": "Writes polished reports from research notes",
    "system_prompt": (
        "You are a professional writer. Read research notes "
        "and produce polished, well-structured reports."
    ),
    "tools": [],
    "model": "anthropic:claude-sonnet-4-20250514",
}
```

### 4. Configuration in config.py

```python
# config.py - Environment and model configuration

import os
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.postgres import PostgresSaver
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

def get_model():
    """Get configured LLM."""
    model_name = os.getenv("MODEL_NAME", "anthropic:claude-sonnet-4-20250514")
    return init_chat_model(model_name)

def get_checkpointer():
    """Get production checkpointer."""
    conn_string = os.getenv("DATABASE_URL")
    if conn_string:
        return PostgresSaver.from_conn_string(conn_string)
    # Fallback for development
    from langgraph.checkpoint.sqlite import SqliteSaver
    return SqliteSaver.from_conn_string("agent.db")

def get_backend():
    """Get configured backend factory."""
    return lambda rt: CompositeBackend(
        default=StateBackend(rt),
        routes={"/memories/": StoreBackend(rt)},
    )
```

### 5. Skills in skills/ Directory

Skills are loaded by path and contain instructions for the agent:

```
skills/
├── research/
│   ├── SKILL.md          # Main instructions
│   ├── templates/        # Report templates
│   │   └── report.md
│   └── examples/         # Example outputs
│       └── sample-report.md
└── writing/
    └── SKILL.md
```

```python
# Loading skills
agent = create_deep_agent(
    backend=FilesystemBackend(root_dir="/app"),
    skills=["skills/research", "skills/writing"],
)
```

Skills are **progressively disclosed** — only loaded when the agent determines they're relevant to the current task. This reduces token usage at startup.

### 6. NO Separate Prompt Files

Deep Agents handle prompts through two mechanisms:
- `system_prompt` parameter in `create_deep_agent()`
- `BASE_AGENT_PROMPT` injected automatically by middleware

Creating separate prompt files adds confusion:

```python
# WRONG: Separate prompts.py
# prompts.py
AGENT_PROMPT = """You are a research agent..."""  # Where does this go?

# CORRECT: Inline in agent.py or subagents.py
agent = create_deep_agent(
    system_prompt="You are a research agent...",  # Clear ownership
)
```

## YAML Sub-Agent Configuration

For complex projects, externalize sub-agent configs to YAML:

```yaml
# subagents.yaml
- name: researcher
  description: Conducts thorough web research
  system_prompt: |
    You are an expert researcher.
    Always cite sources and write notes to the filesystem.
  model: anthropic:claude-sonnet-4-20250514

- name: writer
  description: Writes polished content from notes
  system_prompt: |
    You are a professional technical writer.
    Read notes from the filesystem and produce polished reports.
  model: anthropic:claude-sonnet-4-20250514
```

```python
# subagents.py
import yaml

def load_subagents(path="subagents.yaml"):
    """Load sub-agent configs from YAML."""
    with open(path) as f:
        return yaml.safe_load(f)
```

## File Placement Summary

| File | Purpose | Required? |
|------|---------|-----------|
| agent.py | `create_deep_agent()` entry point | Yes |
| tools.py | Custom tool definitions | If tools needed |
| subagents.py | Sub-agent configurations | If sub-agents used |
| middleware.py | Custom middleware classes | If custom middleware |
| config.py | Environment and model config | Recommended |
| skills/ | Skill instruction directories | Optional |
| prompts.py | Separate prompt storage | NO - don't create |

## Anti-Patterns

```python
# WRONG: All code in one file
# agent.py with 500 lines: tools, subagents, middleware, config, prompts
# Split into focused modules

# WRONG: Hardcoded models and connection strings
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",  # Should be in config
    checkpointer=PostgresSaver.from_conn_string("postgresql://user:pass@host/db"),
)

# WRONG: Tools defined inside create_deep_agent call
agent = create_deep_agent(
    tools=[
        lambda x: "result",  # Anonymous, untestable, no docstring
    ],
)

# WRONG: Sub-agent configs scattered across files
# Keep all sub-agent definitions in subagents.py for discoverability
```

## Checklist

- [ ] Agent creation isolated in agent.py
- [ ] Tools in tools.py with proper docstrings
- [ ] Sub-agent configs in subagents.py (or YAML)
- [ ] Environment config in config.py (not hardcoded)
- [ ] Skills in dedicated directories with SKILL.md
- [ ] No separate prompts.py file
- [ ] Dependencies in requirements.txt
