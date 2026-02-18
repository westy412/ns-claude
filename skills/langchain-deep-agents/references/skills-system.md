# Skills System

Skills are reusable agent capabilities providing specialized workflows and domain knowledge. Each skill is a directory containing a `SKILL.md` file with instructions and metadata, plus optional scripts, docs, and templates.

---

## How Skills Work (Progressive Disclosure)

1. **Startup** -- Agent reads only YAML frontmatter of each `SKILL.md` (name + description)
2. **Match** -- When a prompt arrives, agent checks skill descriptions against the task
3. **Read** -- If match found, agent reads the full `SKILL.md`
4. **Execute** -- Agent follows instructions and accesses supporting files

**Key insight:** Skills reduce startup token cost. Instead of loading 10,000 tokens of instructions upfront, the agent only loads what it needs when it needs it.

---

## SKILL.md Format

```yaml
---
name: langgraph-docs
description: Use this skill for requests related to LangGraph
license: MIT  # optional
compatibility: Requires internet access  # optional
metadata:  # optional
  author: langchain
  version: "1.0"
allowed-tools: fetch_url  # optional
---
# langgraph-docs

## Overview
This skill explains how to...

## Instructions
### 1. Fetch the Documentation Index
### 2. Select Relevant Documentation
### 3. Fetch Selected Documentation
### 4. Provide Accurate Guidance
```

**Constraints:** `description` truncated to 1024 chars. `SKILL.md` must be under 10 MB.

---

## Directory Structure

```
skills/
├── langgraph-docs/
│   └── SKILL.md
├── research/
│   ├── SKILL.md           # Main instructions (required)
│   ├── templates/         # Optional: report templates
│   │   └── report.md
│   └── examples/          # Optional: example outputs
│       └── sample.md
└── arxiv_search/
    ├── SKILL.md
    └── arxiv_search.py
```

---

## Usage with StateBackend (Default)

```python
from urllib.request import urlopen
from deepagents import create_deep_agent
from deepagents.backends.utils import create_file_data
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
skill_url = "https://raw.githubusercontent.com/langchain-ai/deepagents/refs/heads/main/libs/cli/examples/skills/langgraph-docs/SKILL.md"
with urlopen(skill_url) as response:
    skill_content = response.read().decode('utf-8')

skills_files = {"/skills/langgraph-docs/SKILL.md": create_file_data(skill_content)}

agent = create_deep_agent(skills=["./skills/"], checkpointer=checkpointer)
result = agent.invoke(
    {
        "messages": [{"role": "user", "content": "What is langgraph?"}],
        "files": skills_files  # Seed StateBackend's in-state filesystem
    },
    config={"configurable": {"thread_id": "12345"}}
)
```

## Usage with StoreBackend

```python
from deepagents import create_deep_agent
from deepagents.backends import StoreBackend
from deepagents.backends.utils import create_file_data
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
store.put(namespace=("filesystem",), key="/skills/langgraph-docs/SKILL.md",
    value=create_file_data(skill_content))

agent = create_deep_agent(
    backend=(lambda rt: StoreBackend(rt)), store=store, skills=["/skills/"]
)
```

## Usage with FilesystemBackend

```python
from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend

agent = create_deep_agent(
    backend=FilesystemBackend(root_dir="/Users/user/{project}"),
    skills=["/Users/user/{project}/skills/"],
)
```

---

## Source Precedence

Later sources override earlier ones (last wins):

```python
# If both contain "web-search", /skills/project/ wins
agent = create_deep_agent(skills=["/skills/user/", "/skills/project/"])
```

---

## Skills and Subagents

| Subagent Type | Inherits Skills? |
|---------------|-----------------|
| General-purpose | Yes, automatically |
| Custom subagent | No, use `skills` parameter |

Skill state is fully isolated in both directions.

---

## Skills vs Memory (AGENTS.md)

| | Skills | Memory (AGENTS.md) |
|---|---|---|
| **Purpose** | On-demand capabilities | Persistent context, always loaded |
| **Loading** | Progressive disclosure | Always injected into system prompt |
| **Format** | `SKILL.md` in directories | `AGENTS.md` files |
| **Layering** | Last wins | Combined |
| **Use when** | Instructions are task-specific | Context is always relevant |

---

## Skills vs Tools vs Sub-Agents

| Concept | What It Provides | When to Use |
|---------|-----------------|-------------|
| **Tool** | A function the agent can call | Specific actions (search, write, calculate) |
| **Skill** | Instructions and procedures | Domain expertise, methodology, templates |
| **Sub-Agent** | An isolated agent with its own context | Context isolation, specialization |

Skills define **procedures**; sub-agents **execute** complex multi-step work. Your sub-agents can use skills to effectively manage their context windows.

---

## When to Use Skills vs Tools

| Use **Skills** when | Use **Tools** when |
|---|---|
| Context is large (reduces system prompt tokens) | Agent lacks filesystem access |
| Bundling multiple capabilities together | Simple, atomic operations |
| Need additional context beyond tool descriptions | |
| Agent has filesystem access | |

---

## Agent Visibility

A "Skills System" section is automatically injected into the agent's system prompt at startup, showing each skill's name, description, and path. The agent uses this to perform the Match -> Read -> Execute workflow based on skill descriptions.

**Best practice:** Write clear, specific descriptions in your `SKILL.md` frontmatter -- matching decisions rely solely on descriptions.

---

## Path Specifications

- Use **forward slashes** for all skill paths (including on Windows)
- Paths are relative to the backend's root
- StateBackend: virtual filesystem keys must start with `/`
- FilesystemBackend: paths can be absolute or relative to `root_dir`

---

## Anti-Patterns

```python
# WRONG: Loading all skills upfront in system_prompt
agent = create_deep_agent(
    system_prompt=open("skills/research/SKILL.md").read() +
                  open("skills/writing/SKILL.md").read() +
                  open("skills/analysis/SKILL.md").read(),
    # Massive upfront context cost! Use skills parameter instead
)

# WRONG: Skills without filesystem access
agent = create_deep_agent(
    skills=["skills/research"],
    # Default StateBackend - skill files may not be accessible
)
```

## Checklist

- [ ] Skills defined with clear SKILL.md files
- [ ] Skills loaded via `skills` parameter (not system_prompt)
- [ ] Skills directories accessible on the configured backend
- [ ] Clear, specific descriptions in SKILL.md frontmatter

---

## Documentation Links

- [Skills Overview](https://docs.langchain.com/oss/python/deepagents/skills) -- Official Deep Agents skills system documentation
- [Agent Skills Specification](https://agentskills.io/specification) -- The specification that skills follow
- [Using Skills with Deep Agents](https://blog.langchain.com/using-skills-with-deep-agents/) -- Blog post covering practical usage patterns
