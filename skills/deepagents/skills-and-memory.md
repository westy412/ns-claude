# Skills & Memory

Progressive disclosure of capabilities and cross-thread persistent memory.

## Skills

Skills provide agents with domain expertise, templates, and procedures without bloating the initial context window. They are **progressively disclosed** — only loaded when the agent determines they're relevant.

### How Skills Work

```
Agent receives user query
    │
    ▼
Agent examines available skills (names + descriptions only)
    │
    ▼
Agent determines "research" skill is relevant
    │
    ▼
Agent loads research/SKILL.md into context
    │
    ▼
Agent follows skill instructions for the task
```

**Key insight:** Skills reduce startup token cost. Instead of loading 10,000 tokens of instructions upfront, the agent only loads what it needs when it needs it.

### Defining Skills

Skills are directories on the filesystem containing at minimum a `SKILL.md` file:

```
skills/
├── research/
│   ├── SKILL.md           # Main instructions (required)
│   ├── templates/         # Optional: report templates
│   │   └── report.md
│   └── examples/          # Optional: example outputs
│       └── sample.md
├── data-analysis/
│   └── SKILL.md
└── content-writing/
    └── SKILL.md
```

### SKILL.md Structure

```markdown
# Research Skill

Expert research methodology for thorough topic investigation.

## When to Use
- User asks for research on a topic
- User needs a comprehensive report
- Task requires synthesizing multiple sources

## Procedure
1. Break the topic into 3-5 research questions
2. Search for each question using the search tool
3. Read and evaluate source quality
4. Synthesize findings into structured notes
5. Write a polished report with citations

## Quality Standards
- Minimum 5 unique sources per topic
- All claims must cite a source
- Include counterarguments where relevant

## Output Format
Write research notes to /research-notes/ and final report to /reports/
```

### Loading Skills

```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

# Skills must be accessible via the backend
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    backend=FilesystemBackend(root_dir="/app", virtual_mode=True),
    skills=["skills/research", "skills/data-analysis"],
)
```

**Requirement:** The skill directories must exist on the backend filesystem. If using `StateBackend` (default), you must write the skill files to state before creating the agent.

### Skills vs Tools vs Sub-Agents

| Concept | What It Provides | When to Use |
|---------|-----------------|-------------|
| **Tool** | A function the agent can call | Specific actions (search, write, calculate) |
| **Skill** | Instructions and procedures | Domain expertise, methodology, templates |
| **Sub-Agent** | An isolated agent with its own context | Context isolation, specialization |

Skills define **procedures**; sub-agents **execute** complex multi-step work. Your sub-agents can use skills to effectively manage their context windows.

## Memory

Memory enables agents to persist information across conversations (threads). While checkpointers save conversation state per-thread, memory provides **cross-thread** persistence.

### Memory Architecture

```
Thread 1 (Mon): Agent learns user prefers concise reports
    │
    ▼
Agent writes to /memories/user-preferences.md
    │
    ▼
StoreBackend persists this file
    │
    ▼
Thread 2 (Wed): New conversation, new thread_id
    │
    ▼
Agent reads /memories/user-preferences.md
    │
    ▼
Agent automatically uses concise report format
```

### Setting Up Memory

Memory uses the filesystem backend with persistent storage routes:

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.postgres import PostgresStore

store = PostgresStore.from_conn_string("postgresql://...")

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    store=store,
    backend=lambda rt: CompositeBackend(
        default=StateBackend(rt),
        routes={"/memories/": StoreBackend(rt)},
    ),
    memory=["/memories/"],  # Tell agent about memory locations
    system_prompt=(
        "Save important user preferences and learned information to /memories/. "
        "Check /memories/ at the start of each conversation for context."
    ),
)
```

### Memory Patterns

#### User Preferences

```
# /memories/user-preferences.md
- Prefers concise reports (2-3 pages max)
- Primary interest: healthcare AI startups
- Preferred format: bullet points for findings, prose for analysis
- Timezone: US Pacific
```

#### Knowledge Base

```
# /memories/company-research/acme-corp.md
## Acme Corp
- Industry: B2B SaaS
- Founded: 2019
- Last researched: 2026-01-15
- Key finding: Expanding into healthcare vertical
```

#### Project Context

```
# /memories/projects/q1-report.md
## Q1 Report Progress
- Sections completed: Executive Summary, Market Analysis
- Sections remaining: Competitor Analysis, Recommendations
- Last updated: 2026-01-20
- Key decision: Focus on top 5 competitors only
```

### Memory vs Checkpointer

| Feature | Checkpointer | Memory (Store) |
|---------|-------------|----------------|
| Scope | Per-thread | Cross-thread |
| Content | Messages, tool calls, state | Files, notes, preferences |
| Purpose | Conversation continuity | Long-term knowledge |
| Persistence | Thread lifetime | Indefinite |

Both are needed for a fully persistent agent. Use the checkpointer for conversation state and memory for learned knowledge.

## Pre-Loading Skills and Memory

If using `StateBackend` (default), skills and memory files must be written to state before the agent accesses them. With `FilesystemBackend` or `StoreBackend`, files persist naturally.

```python
# For StateBackend: pre-load skill files
# This is handled automatically when skills parameter is provided
# and the backend has access to the files

# For FilesystemBackend: skills are on disk
agent = create_deep_agent(
    backend=FilesystemBackend(root_dir="/app", virtual_mode=True),
    skills=["skills/research"],
    memory=["/app/memories/"],
)
```

## Anti-Patterns

```python
# WRONG: Loading all skills upfront in system_prompt
agent = create_deep_agent(
    system_prompt=open("skills/research/SKILL.md").read() +
                  open("skills/writing/SKILL.md").read() +
                  open("skills/analysis/SKILL.md").read(),
    # Massive upfront context cost! Use skills parameter instead
)

# WRONG: Memory without persistent backend
agent = create_deep_agent(
    backend=lambda rt: StateBackend(rt),  # Ephemeral!
    memory=["/memories/"],
    # Memory files lost after thread ends
)

# WRONG: No system prompt guidance for memory
agent = create_deep_agent(
    backend=lambda rt: CompositeBackend(
        default=StateBackend(rt),
        routes={"/memories/": StoreBackend(rt)},
    ),
    # Agent doesn't know to check /memories/ or what to save
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
- [ ] Memory backed by StoreBackend or persistent storage
- [ ] System prompt guides agent on memory read/write patterns
- [ ] CompositeBackend routes `/memories/` to persistent storage
- [ ] Skills directories accessible on the configured backend
- [ ] Memory vs checkpointer distinction understood and both configured
