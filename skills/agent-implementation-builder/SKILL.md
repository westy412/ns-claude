---
name: agent-impl-builder
description: Transform agent specifications into production code. Takes agent-spec-builder output and generates team orchestration, agents, prompts, and tools. Use when you have a complete specification and are ready to implement.
allowed-tools: Read, Glob, Grep, Task, Write, Edit, Bash
---

# Agent Implementation Builder Skill

## Purpose

An implementation skill that transforms agent specifications into production code. Takes the output from agent-spec-builder and generates working code with proper structure.

**Goal:** Autonomous code generation from specifications.

---

## When to Use This Skill

Use this skill when:
- You have a complete specification from agent-spec-builder
- Ready to generate production code
- Implementing an agent or agent team from scratch

**Skip this skill when:**
- Still gathering requirements (use agent-spec-builder instead)
- Only modifying prompts (use prompt-engineering directly)
- Debugging existing agents (use agent-debugger when available)

---

## Key Principles

1. **Spec-driven** — All implementation decisions come from the spec
2. **Task-based execution** — Break spec into discrete tasks with dependencies
3. **Parallel where possible** — Spawn sub-agents for independent work (e.g., prompts)
4. **Reference-guided** — Use pattern references from agent-config.yaml
5. **Only create what's needed** — Don't generate empty files
6. **Framework cheat sheets first** — Read framework rules before writing code
7. **Ask when unsure** — Never guess. If spec is unclear or documentation is missing, ask the user
8. **Context-conscious loading** — Load child skills one at a time, only at the phase that needs them. The framework cheatsheet is the only reference to load upfront (Phase 0). All other skills are loaded just-in-time per phase. Persist progress to progress.md before each new skill load.
9. **Specs describe behavior, skills describe implementation** — Specs say WHAT should happen — behavior descriptions, data flow, acceptance criteria. Skills say HOW to implement it — framework patterns, code conventions, anti-patterns. If a spec includes code/pseudo-code that conflicts with a skill rule, follow the skill. Specs are not authoritative on implementation details. Schemas (data structures, API contracts) in specs are valid references; code examples are not.
10. **Fix propagation — sweep the codebase** — When applying a pattern fix (e.g., fixing model validation, adding retry logic), search ALL instances of the same pattern in the codebase, not just the failing one. Process: 1) Fix the triggering instance, 2) Search for all instances of the same pattern (`grep -r "class.*BaseModel" src/` for models, grep for function signatures, etc.), 3) Apply the same fix to ALL qualifying instances, 4) Document the sweep scope in the commit message. Incomplete fixes cause recurring bugs.
11. **Model-consumer lockstep** — When modifying a Pydantic model (adding/removing/renaming fields), you MUST update ALL consumers in the same commit. Process: 1) Change the model, 2) grep for all usages of the class name AND field names being changed across the codebase, 3) Update every consumer (formatters, serializers, downstream agents), 4) Commit model + all consumer changes together. Never commit a model change without updating its consumers.

---

## When to Ask for Feedback

**Always ask the user when:**
- Spec is missing required information (especially tool documentation links)
- API documentation doesn't match what spec describes
- Multiple implementation approaches are valid
- You encounter errors or unexpected behavior
- Spec seems incomplete or contradictory
- You're about to make an assumption not in the spec

**How to ask:**
> "The spec for [tool] doesn't include a documentation link. What API/library should I use?"
> "I found two ways to implement [feature]: [A] or [B]. Which do you prefer?"
> "The API documentation shows [X] but the spec says [Y]. Which is correct?"
> "I'm not confident about [specific implementation detail]. Can you clarify?"

**Never:**
- Invent APIs or endpoints not in the spec
- Guess at authentication methods
- Create placeholder tools that don't work (like "API integration required")
- Proceed with implementation when critical information is missing

---

## Framework Cheat Sheets

**CRITICAL: Read the framework cheat sheet BEFORE writing any code.**

Cheat sheets contain critical rules, patterns, and anti-patterns for each framework. They prevent common mistakes that are hard to debug.

| Framework | Cheat Sheet Location |
|-----------|---------------------|
| LangGraph | `frameworks/langgraph/CHEATSHEET.md` |
| DSPy | `frameworks/dspy/CHEATSHEET.md` |

**What cheat sheets contain:**
- **Critical Rules** — Things you MUST do / MUST NOT do
- **Common Patterns** — Quick reference for key patterns
- **Anti-patterns** — What NOT to do with examples of wrong code

**Example critical rule (LangGraph):**
> ToolNode MUST be added to the graph as a separate node. NEVER create ToolNode inside agent functions or manually invoke it.

**When to read:**
1. At the start of implementation (Phase 0)
2. Before implementing any tool-using agents
3. When combining patterns (e.g., router + tools)

---

## Child Skills (Just-in-Time Loading)

**CONTEXT BUDGET RULE: Only invoke ONE child skill at a time, and ONLY when you reach the phase that needs it.** The only upfront reading is the framework cheatsheet (Phase 0, Step 3). Everything else is loaded just-in-time.

### Who Loads Which Skills

| Skill | Loaded By | When | Why |
|-------|-----------|------|-----|
| **Framework cheatsheet** | Main agent | Phase 0, Step 3 | Critical rules for all code generation |
| **agent-teams** | Teammates (research, ideation, scaffold streams) | Before writing team modules | Team-specific orchestration patterns |
| **individual-agents** | Teammates (research, ideation, signatures streams) | Before writing agent code | Agent type patterns |
| **tools-and-utilities** | Teammates (tools stream) | Before writing tool functions | Tool design patterns |
| **prompt-engineering** | Teammates (signatures stream, DSPy) OR prompt-creator sub-agents (LangGraph) | Before writing prompts/signatures | Prompt structure patterns |

**CRITICAL: Main agent does NOT load child skills.** Loading all skills would consume
~10K+ lines of context, leaving no room for spec files or code generation. Instead:
- Main agent loads framework cheatsheet once (Phase 0)
- Teammates load their specific child skills just-in-time when needed
- This distributes context load across teammate contexts

**In team mode:** Each teammate gets its own context window. Skills loaded by a teammate
do NOT consume the main agent's context.

*Important: iIF YOU ARE USING TEAM MODE MAKE SURE TO LOAD IN THE agent-impl-teammate-spawn skill*


| Skill | Invoke At | What It Provides |
|-------|-----------|------------------|
| `agent-teams` | Phase 1 (Team Scaffold) | Team orchestration patterns, graph structure examples |
| `tools-and-utilities` | Phase 2 (Tools) | Tool implementation patterns, utility organization |
| `individual-agents` | Phase 3 (Agent Implementations) | Agent implementation patterns per type |
| `prompt-engineering` | Phase 4 (Prompts) | Loaded by teammates writing prompts (LangGraph: `prompts.py`, DSPy: `prompts/*.md` files) |

**How to invoke (one at a time):**
```
Skill tool → skill: "agent-teams"
```

**Loading rules:**
1. Phase 0: Read ONLY the framework cheatsheet. DO NOT invoke any child skills yet.
2. At each subsequent phase, invoke the ONE skill needed for that phase.
3. Before invoking a new child skill, update progress.md with all completed work.
4. After completing a phase, update progress.md before proceeding.
5. If context is large after completing a phase, consider a session handover before loading the next skill.
6. For Phase 4 (LangGraph): `prompt-engineering` is loaded by prompt-creator sub-agents in their own context, NOT by the main agent.

**Why just-in-time:** Each child skill loads hundreds to thousands of lines. Loading all four upfront alongside the framework cheatsheet and spec files will exhaust the context window, leaving no room for actual code generation.

---

## Input

Spec folder from agent-spec-builder:

**Single agent:**
```
project-name/
└── spec/
    ├── manifest.yaml        # ENTRY POINT - read this first
    ├── progress.md          # Design decisions and context
    ├── agent-config.yaml    # Machine-readable configuration
    └── my-agent.md          # Agent spec
```

**Single team:**
```
project-name/
└── spec/
    ├── manifest.yaml        # ENTRY POINT - read this first
    ├── progress.md
    └── content-review-loop/ # Team folder (self-contained)
        ├── team.md
        ├── agent-config.yaml # This team's config
        └── agents/
            ├── creator.md
            └── critic.md
```

**Nested teams:**
```
project-name/
└── spec/
    ├── manifest.yaml        # ENTRY POINT - hierarchy + file list
    ├── progress.md
    └── research-pipeline/   # Root team folder
        ├── team.md
        ├── agent-config.yaml # Root team config
        ├── content-refinement/
        │   ├── team.md
        │   ├── agent-config.yaml # Sub-team config
        │   └── agents/
        │       ├── creator.md
        │       └── critic.md
        └── parallel-research/
            ├── team.md
            ├── agent-config.yaml # Sub-team config
            └── agents/
                ├── researcher-a.md
                └── merger.md
```

**manifest.yaml provides:**
- System type (single-agent, agent-team, nested-teams)
- Hierarchy visualization
- Complete file list
- Parallel groups for implementation (sub-teams can run in parallel)

---

## Output

Production code - mirrors spec structure, each team folder is self-contained:

**Single agent:**
```
project-name/
├── pyproject.toml           # Project config + dependencies (managed by uv)
├── uv.lock                  # Lockfile (managed by uv)
├── .env.example             # Required environment variables
└── src/
    ├── agent.py             # Agent implementation
    ├── prompts.py           # Agent prompt
    └── tools.py             # Tools (if needed)
```

**Single team:**
```
project-name/
├── pyproject.toml           # Project config + dependencies (managed by uv)
├── uv.lock                  # Lockfile (managed by uv)
├── .env.example             # Required environment variables
└── src/
    └── content-review-loop/
        ├── team.py          # Orchestration + agents
        ├── prompts.py       # Agent prompts
        ├── tools.py         # Tool definitions (if needed)
        └── utils.py         # Utilities (if needed)
```

**Nested teams:**
```
project-name/
├── pyproject.toml           # Project config + dependencies (managed by uv)
├── uv.lock                  # Lockfile (managed by uv)
├── .env.example             # Required environment variables
└── src/
    └── research-pipeline/
        ├── team.py          # Top-level orchestration
        ├── content-refinement/
        │   ├── team.py
        │   ├── prompts.py
        │   ├── tools.py
        │   └── utils.py
        └── parallel-research/
            ├── team.py
            ├── prompts.py
            ├── tools.py
            └── utils.py
```

**Only create files if the team needs them.**

---

## Framework-Specific File Organization

### LangGraph File Organization

LangGraph follows the structure shown above:
- `team.py` - Orchestration + agent nodes
- `prompts.py` - Separate prompt strings for each agent
- `tools.py` - Tool definitions (if needed)
- `utils.py` - Utilities (if needed)

### DSPy File Organization

**CRITICAL: DSPy has DIFFERENT file organization than LangGraph.**

DSPy uses a two-file pattern: Signature classes in `signatures.py` have **empty docstrings**, and rich prompt content lives in co-located `prompts/{agent_name}.md` files that get loaded into `Signature.__doc__` at import time.

**Single team:**
```
project-name/
├── pyproject.toml
├── uv.lock
├── .env.example
├── main.py                  # FastAPI service wrapper
└── src/
    └── content-review-loop/
        ├── team.py          # Orchestration module
        ├── signatures.py    # DSPy Signatures (empty docstrings)
        ├── prompts/
        │   ├── creator.md   # Rich prompt content loaded at runtime
        │   └── critic.md
        ├── models.py        # Pydantic models (if needed for complex outputs)
        ├── tools.py         # Tool definitions (if needed)
        └── utils.py         # Utilities + formatters (if needed)
```

**Nested teams:**
```
project-name/
├── pyproject.toml
├── uv.lock
├── .env.example
├── main.py                  # FastAPI service wrapper
└── src/
    └── research-pipeline/
        ├── team.py          # Top-level orchestration
        ├── models.py        # Shared Pydantic models (optional)
        ├── utils.py         # Shared utilities + formatters
        ├── content-refinement/
        │   ├── team.py
        │   ├── signatures.py
        │   ├── prompts/
        │   │   ├── creator.md
        │   │   └── critic.md
        │   ├── tools.py
        │   └── utils.py
        └── parallel-research/
            ├── team.py
            ├── signatures.py
            ├── prompts/
            │   ├── researcher.md
            │   └── merger.md
            ├── tools.py
            └── utils.py
```

**File Placement Rules for DSPy:**

| File | What Goes Here | Required? |
|------|----------------|-----------|
| `signatures.py` | DSPy Signature classes with empty docstrings + `_load_prompt()` helper | YES (always for DSPy) |
| `prompts/*.md` | Rich prompt content (XML-tagged sections) loaded via `__doc__` at import | YES (one per agent) |
| `models.py` | Pydantic BaseModel classes for complex nested outputs | If needed |
| `team.py` | dspy.Module class with Predict/ChainOfThought instances | YES |
| `tools.py` | Tool functions returning dicts (NOT @tool decorated) | If agents use tools |
| `utils.py` | Singleton LM factories, formatters, retry wrapper | YES (formatters needed between stages) |
| `prompts.py` | ❌ **DO NOT CREATE** for DSPy | NO |

**How prompts work in DSPy (two-file pattern):**

```python
# signatures.py — typed interface with empty docstrings

import dspy
from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent / "prompts"

def _load_prompt(filename: str) -> str:
    """Load prompt content from a co-located markdown file."""
    return (_PROMPTS_DIR / filename).read_text()


class MyAgentSignature(dspy.Signature):
    """"""  # Empty — loaded from prompts/my_agent.md

    input_field: str = dspy.InputField(desc="What this input contains")
    output_field: str = dspy.OutputField(desc="What to return")


# Load at import time — DSPy reads __doc__ when Predict/ChainOfThought is instantiated
MyAgentSignature.__doc__ = _load_prompt("my_agent.md")
```

**Why separate .md files (not inline docstrings):**
- Prompts are editable without touching Python code — prompt engineers iterate on `.md` files without modifying typed interfaces
- Version control clarity — prompt changes vs I/O contract changes show up as separate diffs
- prompt-engineering skill applies directly — XML-tagged sections, role guidance, and quality standards from the skill work naturally with `.md` files
- DSPy optimization compatible — GEPA/MIPROv2 see `__doc__` as a normal string

**Structured Output — Critical Rule:**
When generating DSPy signatures, NEVER use `str` output fields with JSON parsing instructions.
- Use typed fields: `bool`, `int`, `float`, `list[str]`, `dict[str, Any]`, `Literal[...]`
- Use Pydantic `BaseModel` for complex nested outputs, `RootModel[List[...]]` for lists of objects
- Define Pydantic models in `models.py`, import them in `signatures.py`
- Access results: `result.field_name` for typed fields, `result.field_name.model_dump()` for Pydantic models
- See `frameworks/dspy/CHEATSHEET.md` Critical Rules §7 for full guidance and examples

**Signature Organization:**
- **Small teams (1-5 agents):** All signatures in team's `signatures.py`
- **Large teams (6+ agents):** Consider grouping by role or stage within signatures.py, use comments as section headers
- **Nested teams:** Each sub-team has its own `signatures.py` + `prompts/` directory; shared signatures can go in root-level `models.py` if reused

---

## Workflow

### Phase 0: Parse Spec and Initialize Project

**Step 1:** Read `spec/manifest.yaml` — this is your entry point.

The manifest provides:
1. **System type** — single-agent, agent-team, or nested-teams
2. **Hierarchy** — visual structure of teams and agents
3. **File list** — all spec files to read
4. **Implementation order** — suggested sequence

**Step 2:** Read the ROOT `agent-config.yaml` for detailed configuration, including:
- Framework being used (langgraph, dspy)
- Agent types
- Tool requirements
- **`sub-teams` key** — if present, note child folders. Each child folder has its own `agent-config.yaml`. Read sub-team configs only when you reach that sub-team's implementation chunk.

**Nested agent-config.yaml structure:** agent-config.yaml files mirror the directory structure — one per team folder at every level. The root config lists sub-teams with `folder` references. Each sub-team's config is self-contained with its own agents, pattern, and notes.

```yaml
# Root agent-config.yaml
team:
  name: research-phase
  sub-teams:
    - name: linkedin-keyword
      folder: linkedin-keyword/    # Has its own agent-config.yaml
    - name: analytics-team
      folder: analytics-team/      # Has its own agent-config.yaml
  agents:
    - agent:
        name: signal-blender       # Direct member of this team
```

**Step 3: READ THE FRAMEWORK CHEAT SHEET.**

Based on the framework in agent-config.yaml, read the corresponding cheat sheet:
- LangGraph → `frameworks/langgraph/CHEATSHEET.md`
- DSPy → `frameworks/dspy/CHEATSHEET.md`

**This step is CRITICAL.** The cheat sheet contains rules that prevent common implementation mistakes.

**Step 4:** Read individual spec files as needed.

**Step 4.5: Determine execution mode.**

Read the `execution-plan` section from manifest.yaml:

- **IF** the execution plan has phases with 2+ parallel chunks across different streams:
  → Use **TEAM MODE** (see "Team Mode Orchestration" section below)
*Important: iIF YOU ARE USING TEAM MODE MAKE SURE TO LOAD IN THE agent-impl-teammate-spawn skill*

- **IF** the execution plan is purely sequential, missing, or all chunks are in one stream:
  → Use **SINGLE-AGENT MODE** (current workflow — proceed to Phase 1)

Team mode uses Claude Code agent teams to execute chunks in parallel. Each work stream gets its own teammate agent with independent context. Single-agent mode works through phases sequentially as before.

**Step 5: Initialize project with uv.**

```bash
# Navigate to project directory
cd [project-name]

# Initialize uv project (if not already initialized)
uv init

# Create src directory structure
mkdir -p src/[team-name]
```

**Step 6: Add core dependencies.**

Read dependencies from `team.md` → Dependencies section and add them:

```bash
# Core framework dependencies
uv add langgraph langchain-anthropic

# Tool dependencies (from spec)
uv add httpx beautifulsoup4 youtube-transcript-api
```

**Add dependencies as you identify them from the spec.** Don't wait until the end.

**Step 7: CREATE the progress document.**

This is CRITICAL. Create `progress.md` in the project root BEFORE starting implementation.

1. **Read the template:** `agent-patterns/agent-implementation-builder/templates/progress.md`
2. **Create progress.md** in project root
3. **Populate with ALL tasks** derived from the spec:

For each team (including nested), add these tasks:
- Create team.py scaffold
- Create tools.py (if team has tool-using agents)
- Implement each agent (one task per agent, named)
- Create prompts (one task per agent, named)
- Create utils.py (if needed)
- Create .env.example

**Example progress.md content:**

```markdown
# YouTube Summarizer - Implementation Progress

## Status

**Current Phase:** Phase 0 - Setup
**Last Updated:** 2025-01-10
**Spec Location:** spec/

---

## Tasks

| Task | Status | Dependencies | Assigned To | Notes |
|------|--------|--------------|-------------|-------|
| team.py scaffold | pending | - | agent-impl-builder | |
| tools.py | pending | scaffold | agent-impl-builder | youtube-transcript-api |
| Implement fetcher | pending | tools.py | agent-impl-builder | |
| Implement summarizer | pending | tools.py | agent-impl-builder | |
| Prompt: fetcher | pending | fetcher impl | prompt-creator | |
| Prompt: summarizer | pending | summarizer impl | prompt-creator | |
| .env.example | pending | - | agent-impl-builder | |

**Status values:** pending | in_progress | done | blocked | skipped
```

4. **Update progress.md as you work** — mark tasks in_progress when starting, done when complete

**The progress document is your task list.** Refer to it before each phase to know what to do next.

### Phase 1: Team Scaffold

**When you reach this phase:** Invoke `skill: "agent-teams"` to load team pattern implementation guides.

**Before invoking:** Ensure progress.md reflects Phase 0 completion (project initialized, dependencies added, framework cheatsheet read).
**After completing this phase:** Update progress.md with scaffold status before proceeding to Phase 2.

Create team.py with:
- Orchestration logic based on pattern (pipeline, router, fan-in-fan-out, loop)
- Placeholder functions for each agent

When creating team.py scaffold, include BOTH methods:

- [ ] `forward()` — synchronous, no retry, for DSPy optimization
- [ ] `aforward()` — async, with retry wrapper, for production
- [ ] Validation: `raise ValueError` if `shared_lm` is None

```python
# team.py scaffold example

async def creator(state: State) -> State:
    """Creator agent - generates initial content."""
    pass

async def critic(state: State) -> State:
    """Critic agent - reviews and provides feedback."""
    pass

# Orchestration logic here...
```

**Reference:** Use pattern file from `agent-config.yaml → team → reference`
- e.g., `agent-patterns/agent-teams/langgraph/loop.md`

### Phase 2: Tools

**When you reach this phase:** Invoke `skill: "tools-and-utilities"` to load tool implementation patterns.

**Before invoking:** Ensure progress.md reflects Phase 1 completion (team scaffold created).
**After completing this phase:** Update progress.md with tools status before proceeding to Phase 3.

Create tools.py with tool definitions from agent specs.

**Critical:** The spec provides documentation links. You MUST read the actual API/SDK documentation to create working tools.

For each agent that has tools:

1. **Read agent spec** (e.g., `creator.md`)
2. **Extract tool definitions** from Modifiers → Tools section
3. **For each tool, based on implementation type:**

**MCP Server:**
- Configure MCP server connection
- Use the specified tool name

**Existing API:**
- Read the documentation URL from spec
- Use `WebFetch` or `web-researcher` sub-agent to get:
  - Exact endpoint signatures
  - Request/response schemas
  - Error codes
- Create tool using `httpx` or appropriate HTTP client

**SDK/Library:**
- Read the documentation URL from spec
- Use `WebFetch` or `web-researcher` sub-agent to get:
  - Exact method signatures
  - Return types
  - Exception types
- Create tool using the specified library

**Custom Function:**
- Follow the algorithm/pseudocode in spec
- Implement the described logic

4. **Generate tool functions** with proper:
   - Type hints (from API docs)
   - Docstrings (describe what tool does)
   - Error handling (from error codes in docs/spec)
   - Return format (JSON string for LangGraph tools)

**If documentation link is missing or unclear, ASK the user before guessing.**

**Only create tools.py if at least one agent uses tools.**

### Phase 3: Agent Implementations

**When you reach this phase:** Invoke `skill: "individual-agents"` to load agent type implementation guides.

**Before invoking:** Ensure progress.md reflects Phase 2 completion (tools created).
**After completing this phase:** Update progress.md with agent implementation status before proceeding to Phase 4.

### Input/Output Validation Protocol (MANDATORY)

Before implementing ANY signature, follow this protocol:

**Step 1: Extract from Spec**
Read the agent's spec file (agents/[name].md). Create two lists:

INPUTS CHECKLIST:
  [ ] input_field_1 (type: str, required: yes)
  [ ] input_field_2 (type: dict, required: no, default: None)
  [ ] ...

OUTPUTS CHECKLIST:
  [ ] output_field_1 (type: ResearchFindingList)
  [ ] output_field_2 (type: bool)
  [ ] ...

**Step 2: Trace Upstream Data**
For each input that comes from another component:
1. Identify the upstream component (which module produces this?)
2. Read that component's output spec
3. Verify field names match EXACTLY
4. If mismatch, flag for team lead

Example:
```
Input: research_documents (from Research Phase)
Upstream: ResearchPhase.aforward() output
Trace: Does ResearchPhase return a field called "research_documents"?
  ✓ Yes → src/research/team.py:233 returns ResearchPhaseOutput with 4 doc fields
  ✗ No → Message team-lead: "Research phase output schema mismatch"
```

**Step 3: Implement Signature**
Create the signature with ALL inputs and outputs from your checklists.

**Step 4: Cross-Check**
Before moving on:
  [ ] Every spec input has a corresponding InputField
  [ ] Every spec output has a corresponding OutputField
  [ ] All OutputFields use typed models (NO str+JSON)
  [ ] Optional inputs use default=None + optionality in desc
  [ ] Model tier assignment matches spec (Flash vs Pro)

**If ANY checkbox is unchecked, DO NOT PROCEED. Fix first.**

---

Fill in placeholder functions with actual implementations.

For each agent:
1. Read agent spec (e.g., `creator.md`)
2. Read pattern reference from `agent-config.yaml → agent → reference`
   - e.g., `agent-patterns/individual-agents/langgraph/text-agent.md`
3. Generate implementation following the pattern

### Phase 4: Prompts/Signatures

**Note:** The `prompt-engineering` skill is loaded by **teammates** writing prompts, NOT by the main agent. Do not invoke `prompt-engineering` directly — it would waste main-agent context. For LangGraph, teammates edit `prompts.py` directly. For DSPy, teammates write `prompts/{agent_name}.md` files that get loaded into signature docstrings at runtime.

**Framework-specific approaches:**

#### LangGraph: prompts.py

**Strategy:** Create scaffold first, then sub-agents edit directly. This keeps prompts out of main agent context.

**Step 1: Create prompts.py scaffold**

```python
# prompts.py - Generated scaffold

CREATOR_PROMPT = """
# TODO: Generated by prompt-creator sub-agent
"""

CRITIC_PROMPT = """
# TODO: Generated by prompt-creator sub-agent
"""
```

**Step 2: Spawn prompt-creator sub-agents to EDIT the file directly**

For each agent, spawn `prompt-creator` sub-agent with:
- Path to prompts.py file
- Which prompt variable to update (e.g., `CREATOR_PROMPT`)
- Agent spec file path (e.g., `agents/creator.md`)
- Prompt config from `agent-config.yaml → agent → prompt`

The sub-agent:
1. Reads the agent spec
2. Invokes `prompt-engineering` skill internally
3. **Edits prompts.py directly** (uses Edit tool to update the placeholder)
4. Does NOT return the prompt to main agent

**Parallel execution:** If 6 agents, spawn 6 prompt-creator agents simultaneously. Each edits a different variable in the same file.

**Why this approach:**
- Prompts don't flow through main agent context
- Sub-agents work directly on the file
- Main agent just waits for completion
- Cleaner context management

#### DSPy: signatures.py + prompts/*.md

**CRITICAL: DSPy uses a two-file pattern. Signatures have empty docstrings; prompts live in separate `.md` files.**

**Strategy:** Create `signatures.py` with empty docstrings and `_load_prompt()` helper, then create `prompts/{agent_name}.md` files with rich XML-tagged prompt content. Teammates load the `prompt-engineering` skill when writing the `.md` files.

**Step 1: Create signatures.py with empty docstrings + prompt loader**

```python
# signatures.py

import dspy
from pathlib import Path
from typing import Literal, Union

_PROMPTS_DIR = Path(__file__).parent / "prompts"

def _load_prompt(filename: str) -> str:
    """Load prompt content from a co-located markdown file."""
    return (_PROMPTS_DIR / filename).read_text()


class CreatorSignature(dspy.Signature):
    """"""  # Empty — loaded from prompts/creator.md

    # Inputs
    theme: str = dspy.InputField(desc="Content theme to write about")
    previous_feedback: str = dspy.InputField(
        desc="Optional feedback from prior iteration. If not provided, this is the first attempt.",
        default=None
    )

    # Outputs
    content: str = dspy.OutputField(desc="Generated content")


class CriticSignature(dspy.Signature):
    """"""  # Empty — loaded from prompts/critic.md

    content: str = dspy.InputField(desc="Content to review")
    criteria: str = dspy.InputField(desc="Quality criteria")

    feedback: str = dspy.OutputField(desc="Specific improvement suggestions")
    passed: bool = dspy.OutputField(desc="True if content meets criteria")
    score: int = dspy.OutputField(desc="Quality score 0-100")


# Load rich prompt content from markdown at module import time.
# DSPy reads __doc__ when Predict/ChainOfThought is instantiated.
CreatorSignature.__doc__ = _load_prompt("creator.md")
CriticSignature.__doc__ = _load_prompt("critic.md")
```

**Step 2: Create prompts/*.md files with XML-tagged content**

For each agent, create a `prompts/{agent_name}.md` file using XML tags:

```xml
<!-- prompts/creator.md -->

<who_you_are>
You are a creative content generator in a quality-retry loop.
You produce initial content that a Critic will evaluate.
</who_you_are>

<context>
Workflow:
- Stage 1: YOU (Creator) — Generate content based on theme
- Stage 2: Critic — Evaluate and provide feedback
- Repeat: You receive feedback and improve

When previous_feedback is provided, you are on a retry iteration.
Incorporate the feedback to improve your output.
</context>

<task>
1. Read the theme and any previous feedback
2. Generate creative content that addresses the theme
3. If feedback is present, specifically address each point raised
4. Ensure output meets quality standards below
</task>

<quality_standards>
- Be specific and actionable, not generic
- Incorporate all critic feedback when available
- Each iteration must show measurable improvement
</quality_standards>

<anti_patterns>
- Do NOT ignore previous feedback
- Do NOT repeat the same content across iterations
- Do NOT produce generic filler content
</anti_patterns>

<important_notes>
- If no previous_feedback is provided, this is the first attempt
- Always improve on previous iteration when feedback exists
</important_notes>
```

**DSPy Prompt-Writing File Traversal:**

When writing DSPy `prompts/*.md` files, teammates should read these reference files in order:

| Order | File | Purpose |
|-------|------|---------|
| 1 | `agent-implementation-builder/frameworks/dspy/CHEATSHEET.md` | Signature patterns and DSPy-specific rules |
| 2 | `prompt-engineering/references/targets/dspy.md` | DSPy-specific sections to keep/skip/add |
| 3 | `prompt-engineering/references/frameworks/single-turn.md` | XML section structure template |
| 4 | `prompt-engineering/references/roles/{role}.md` | Role-specific section guidance |
| 5 | `prompt-engineering/references/modifiers/{applicable}.md` | Modifier adaptations for DSPy |
| 6 | `prompt-engineering/references/guidelines/prompt-writing.md` | Quality checklist |

**Do NOT:**
- ❌ Create `prompts.py` for DSPy projects
- ❌ Write inline docstring prompts — use `prompts/*.md` files loaded via `__doc__`
- ❌ Use `=== SECTION ===` headers — use XML tags (`<who_you_are>`, `<task>`, etc.)
- ❌ Use brief docstrings like "Extract data" — prompts must be 20+ lines of substantive content

**Why this matters:**
DSPy reads `Signature.__doc__` when `Predict`/`ChainOfThought` is instantiated. The `_load_prompt()` helper reads `.md` files at import time and assigns them to `__doc__`. This gives you the best of both worlds: typed Python interfaces in `signatures.py` and rich, maintainable prompt content in `.md` files that benefit from the full prompt-engineering skill guidelines.

### Phase 5: Utilities

Create utils.py if shared utilities are needed.

Only create if:
- Multiple agents share common logic
- Team needs helper functions

### Phase 6: Environment Setup

Generate environment configuration file.

**Note:** Dependencies are already added via `uv add` in Phase 0. The `pyproject.toml` is managed by uv.

**Generate `.env.example`:**

```bash
# Required API keys
ANTHROPIC_API_KEY=your_key_here  # LLM provider
YOUTUBE_API_KEY=your_key_here    # For YouTube metadata (optional)

# Optional configuration
LOG_LEVEL=INFO
```

**Include comments** explaining what each variable is for and how to obtain it.

**Read from:** `team.md` → Dependencies → Environment Variables section

### Phase 7: FastAPI Service Wrapper

**CRITICAL: Every agent system needs a FastAPI wrapper for deployment.**

Agent modules are pure DSPy/LangGraph code. The FastAPI layer provides:
- HTTP endpoints for agent invocation
- Request validation
- Error handling and status codes
- Async execution
- Health checks

**Create main.py in project root:**

```python
"""
FastAPI service wrapper for [System Name].

Provides HTTP endpoints for agent invocation with request validation,
error handling, and async execution.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.[team_name].team import [TeamClass]
from src.[team_name].utils import get_shared_lm  # For DSPy
# OR for LangGraph:
# from src.[team_name].team import create_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# Request/Response Models
# =============================================================================

class [SystemName]Request(BaseModel):
    """Request model for [system] endpoint."""
    # Define request fields based on team.py aforward() parameters
    input_field: str
    config: dict = {}


class [SystemName]Response(BaseModel):
    """Response model for [system] endpoint."""
    # Define response fields based on team.py return Prediction
    output_field: str
    timings: dict = {}
    error: str | None = None


# =============================================================================
# Lifespan Management
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize shared resources on startup, cleanup on shutdown.

    For DSPy: Initialize singleton LM
    For LangGraph: Initialize graph, checkpointer, etc.
    """
    # Startup
    logger.info("[Startup] Initializing [System Name]...")

    # DSPy: Initialize singleton LM
    from src.[team_name].utils import get_shared_lm
    app.state.shared_lm = get_shared_lm()
    app.state.pipeline = [TeamClass](shared_lm=app.state.shared_lm)

    # OR for LangGraph:
    # app.state.graph = create_graph()

    logger.info("[Startup] [System Name] ready")

    yield

    # Shutdown
    logger.info("[Shutdown] Cleaning up resources...")


# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title="[System Name] API",
    description="[Brief description of what this system does]",
    version="1.0.0",
    lifespan=lifespan,
)


# =============================================================================
# Health Check
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy", "service": "[system-name]"}


# =============================================================================
# Main Endpoint
# =============================================================================

@app.post("/[endpoint-name]", response_model=[SystemName]Response)
async def run_[system_name](request: [SystemName]Request) -> [SystemName]Response:
    """
    Execute the [system name] pipeline.

    Args:
        request: Input data and configuration.

    Returns:
        Processed output with timings and error status.

    Raises:
        HTTPException: 500 if pipeline execution fails.
    """
    try:
        logger.info("[API] Received request for [system name]")

        # Execute pipeline
        result = await app.state.pipeline.aforward(
            input_field=request.input_field,
            config=request.config,
        )

        # Check for pipeline-level errors
        if hasattr(result, 'error') and result.error:
            logger.error("[API] Pipeline failed: %s", result.error)
            raise HTTPException(
                status_code=500,
                detail=f"Pipeline execution failed: {result.error}"
            )

        logger.info("[API] Request completed. Timings: %s", result.timings)

        return [SystemName]Response(
            output_field=result.output_field,
            timings=result.timings,
            error=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("[API] Unexpected error")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# =============================================================================
# Run Server (Development)
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
```

**Customize based on spec:**

1. **Read team.md** → Inputs/Outputs sections
2. **Define Request model** with fields matching `aforward()` parameters
3. **Define Response model** with fields matching the return Prediction
4. **Name the endpoint** based on the system purpose (e.g., `/generate-ideas`, `/summarize`, `/analyze`)
5. **Add uvicorn dependency:** `uv add fastapi uvicorn[standard]`

**Additional endpoints to consider:**

For systems with status callbacks or multi-step flows:
```python
@app.post("/[system-name]/start")
async def start_generation(request: StartRequest):
    """Start async job, return job_id for status polling."""
    # Queue job with background task
    pass

@app.get("/[system-name]/status/{job_id}")
async def get_status(job_id: str):
    """Check job status."""
    # Return status + partial results if available
    pass
```

**Only create if spec mentions async job patterns or status callbacks.**

---

## Team Mode Execution

*Important: iIF YOU ARE USING TEAM MODE MAKE SURE TO LOAD IN THE agent-impl-teammate-spawn skill*

### When to Use Team Mode

Use team mode when the execution plan has **parallel chunks across multiple streams** in any phase.

**Example from manifest.yaml:**
```yaml
execution-plan:
  phases:
    - phase: 1
      chunks:
        - name: data-models
          stream: models          # ← Different streams
        - name: tools
          stream: tools           # ← can work in parallel
        - name: research-signatures
          stream: signatures      # ← across Phase 1
```

If chunks share the same stream → single-agent mode (sequential).
If chunks span different streams → team mode (parallel).

---

### Team Mode Workflow

#### Step 1: Create Team and Task List

```
TeamCreate: team_name="[project]-impl", description="..."
```

For each chunk in execution plan, create a task:
```
TaskCreate:
  subject: "Phase N: [chunk.name] — [chunk.description summary]"
  description: "[chunk.description] + spec files + skills required + communication needs"
  activeForm: "Implementing [chunk.name]"
```

Set phase dependencies via TaskUpdate:
- Phase 1 tasks: no blockedBy
- Phase 2 tasks: blockedBy = [all Phase 1 task IDs]
- Phase 3 tasks: blockedBy = [all Phase 2 task IDs]

---

#### Step 2: Map Streams to Skills (MANDATORY)

For each stream in execution plan, use this mapping:

| Stream Type | Required Skills | Load When |
|-------------|----------------|-----------|
| **models** | (none — derive from specs) | N/A |
| **tools** | tools-and-utilities | Phase 1 before writing tools |
| **signatures** | prompt-engineering, individual-agents | Phase 1 before writing signatures |
| **research** | agent-teams, individual-agents | Phase 2 before modules |
| **ideation** | agent-teams, individual-agents | Phase 2 before modules |
| **scaffold** | agent-teams | Phase 3+ before orchestration |

If execution plan lists `stream.skills`, use those. Otherwise, use this default table.

**⚠️ CRITICAL:** Skills are NOT optional. Every stream that writes agent code MUST load the corresponding skills.

---

#### Step 3: Generate Teammate Prompt Files

For each stream with work, use the `agent-impl-teammate-spawn` skill to generate a structured prompt file:

```
Skill tool -> skill: "agent-impl-teammate-spawn"
```

This skill reads your manifest.yaml and agent-config.yaml to generate a prompt file for each stream at:
```
{project-path}/teammate-prompts/{team-name}/{stream-name}.md
```

Each generated file includes the exact skills to load, how to load them, tasks to work on, validation checklists, and communication requirements. Follow the skill's step-by-step instructions to generate one file per stream.

---

#### Step 4: Spawn Teammates with Minimal Prompts

After generating all prompt files, spawn each teammate with a minimal prompt pointing to their file:

```
Task tool:
  team_name: [project-name]
  name: [stream-name]
  subagent_type: general-purpose
  model: opus (for complex streams like research/ideation)
  prompt: |
    You are teammate [stream-name] on team [project-name].

    Read your full instructions at:
      [project-path]/teammate-prompts/[team-name]/[stream-name].md

    Follow ALL steps in order. DO NOT skip Step 1 (Load Required Skills).
    After loading skills, confirm to team-lead via SendMessage.
```

---

#### Step 5: Verify Skill Loading (MANDATORY — DO NOT SKIP)

This is the enforcement mechanism. Without this step, teammates will skip skill loading and produce broken code. This has been proven: in NS-1158, 4/5 teammates skipped skills and produced incorrect implementations.

After spawning all teammates:

1. Wait for the first message from each teammate
2. The message MUST confirm skill loading with the specific skill names (e.g., "Skills loaded: agent-teams, individual-agents")
3. If the first message is about anything other than skill loading — the teammate skipped Step 1. Send them back:
   > "STOP. You must load your required skills before doing any work. Go back to Step 1 in your prompt file. Use the Skill tool to load each skill listed there. Confirm to me when done."
4. Do NOT assign tasks, do NOT allow work to begin, do NOT respond to implementation questions until skills are confirmed
5. If a teammate claims a task without confirming skills — revoke it immediately and enforce loading
| **scaffold/root** | owns root pipeline, FastAPI wrapper | agent-teams |

**How to detect stream type:** Read `stream.owns` file list. Match file patterns to table above.

**Example:**
```yaml
streams:
  - name: research
    owns: [src/research/]  # ← Owns team modules
```
→ Stream type: team/orchestration → Skills: agent-teams

**⚠️ IMPORTANT:** Do NOT spawn teammates without determining their required skills.

### Stream Communication Protocol

Teammates must communicate when:
1. Completing a chunk that produces data needed by other streams
2. Encountering a missing input that should come from another stream
3. Discovering a spec/implementation mismatch affecting multiple streams

**When to send:**
Check `execution-plan.communication` in manifest.yaml:

```yaml
communication:
  - from: tools
    to: [research, ideation]
    after: phase-1
    what: Tool function signatures
```

After completing the trigger event (phase-1 for tools stream), send via:
```
SendMessage:
  type: message
  recipient: [target-stream-name]
  content: [what to send]
  summary: "Phase 1 tools complete: function signatures available"
```

**What to send:** Function signatures, interface contracts, model schemas, breaking changes.

**Team Lead Responsibilities:**
- Monitor SendMessage traffic
- Verify communication plan is followed
- Relay messages if direct teammate-to-teammate fails

### Team Lead Progress Management (Team Mode)

As team lead, you MUST:

**1. Create progress.md BEFORE spawning teammates**
- Use template from templates/progress.md
- Populate Execution Plan Snapshot with all chunks
- Set initial status: all "pending"

**2. Update progress.md after each phase completes**
- Mark completed chunks as "done"
- Update "Current Phase" and "Next Chunk"
- Add session log entry

**3. Monitor TaskList after each teammate message**
```
TaskList → check for newly unblocked tasks → assign to idle teammates
```

**4. Enforce cross-stream communication**
- When a chunk completes, check execution-plan.communication
- If communication required, verify SendMessage was sent
- If not sent, prompt the teammate

**5. Validate before proceeding to next phase**
- All Phase N tasks must be "completed" before Phase N+1 starts
- Check that all communication happened
- Spot-check 1-2 files for import validity

---

## Task Dependencies

**When an execution plan exists in manifest.yaml**, the execution plan is the SOLE source of truth for phasing. The plan defines:
- **Phases** — ordered stages that execute sequentially (Phase 2 waits for Phase 1 to complete)
- **Chunks** — units of work within a phase that can run in parallel across agent team teammates
- **Streams** — work streams that own specific files; each teammate maps to a stream

All default file-type phasing below is IGNORED when an execution plan exists. Do NOT reference these defaults (Scaffold → Tools → Agents → Prompts → Utils) in progress tracking, task creation, or teammate spawn prompts. Use the execution plan's phase names and chunk names instead.

**Default LangGraph dependencies (when no execution plan):**
```
team.py scaffold
       ↓
    tools.py
       ↓
agent implementations (can be parallel per agent if tools complete)
       ↓
   prompts.py (parallel - all prompts at once)
       ↓
    utils.py (as needed)
       ↓
  .env.example
       ↓
    main.py (FastAPI wrapper)
```

**Default DSPy dependencies (when no execution plan):**
```
signatures.py + prompts/*.md (empty docstrings + separate .md prompt files)
       ↓
    tools.py (if needed)
       ↓
    utils.py (singleton LM, formatters, retry wrapper)
       ↓
    models.py (Pydantic models if needed for complex outputs)
       ↓
    team.py (dspy.Module with Predict instances)
       ↓
  .env.example
       ↓
    main.py (FastAPI wrapper)
```

---

## Navigating References

The agent-config.yaml provides paths to pattern references:

```yaml
team:
  name: content-review-loop
  pattern: loop
  framework: langgraph
  reference: agent-patterns/agent-teams/langgraph/loop.md  # ← Use this

  agents:
    - agent:
        name: creator
        type: text-agent
        framework: langgraph
        reference: agent-patterns/individual-agents/langgraph/text-agent.md  # ← Use this
        prompt:
          framework: single-turn
          role: creative-generator
          modifiers: [memory]
```

When implementing:
1. Read the reference file for the pattern/structure
2. Read the spec file (team.md, agent.md) for the specific requirements
3. Combine: pattern structure + spec requirements = implementation

---

## Sub-Agent Strategy

### Single-Agent Mode

| Task | Sub-Agent | Notes |
|------|-----------|-------|
| Team scaffold | None | agent-impl-builder does directly |
| Tools | None | agent-impl-builder does directly |
| Agent implementations | None | agent-impl-builder does directly |
| Prompts | `prompt-creator` | One per agent, run in parallel, edits file directly |
| Utils | None | agent-impl-builder does directly |

### Team Mode

| Task | Method | Notes |
|------|--------|-------|
| Quick focused work (single file) | Task tool sub-agent | No coordination needed, fires and forgets |
| Parallel phased work | Agent team teammate | One per work stream, execution plan has parallel chunks |
| Prompt generation | prompt-creator sub-agent OR team prompts stream | Sub-agent if few prompts; teammate stream if many |

**When to use which:**
- Use **Task sub-agents** for isolated, quick tasks within a single file
- Use **Agent team teammates** when the execution plan defines parallel work streams
- Team mode teammates maintain context across phases within their stream

**Prompt-creator invocation:**

When spawning prompt-creator sub-agents, provide these EXPLICIT instructions:

```
Task tool with subagent_type='prompt-creator'

PROMPT FOR SUB-AGENT:
"You are creating a prompt for the [AGENT_NAME] agent.

STEP 1: INVOKE THE PROMPT-ENGINEERING SKILL
You MUST use the Skill tool to invoke: skill: "prompt-engineering"
This loads the prompt engineering reference files. Do not skip this step.

STEP 2: READ THE REFERENCE FILES
After invoking the skill, read these files:
- agent-patterns/prompt-engineering/frameworks/[framework].md
- agent-patterns/prompt-engineering/roles/[role].md
- agent-patterns/prompt-engineering/modifiers/[each modifier].md

STEP 3: READ THE AGENT SPEC
Read the agent spec file: [path to agents/agent-name.md]
Extract: Purpose, Key Tasks, Inputs, Outputs, Behavioral Requirements, Examples

STEP 4: WRITE THE PROMPT
Using the reference files and agent spec, write the prompt.
Use XML tags to structure sections: <role>, <task>, <context>, <constraints>, <output_format>

STEP 5: EDIT THE FILE DIRECTLY
Use the Edit tool to update [prompts.py path]
Replace the placeholder for [VARIABLE_NAME] with your generated prompt.
Do NOT return the prompt content - edit the file directly.

Prompt config:
- Framework: [single-turn | conversational]
- Role: [role name]
- Modifiers: [list of modifiers]
"
```

**CRITICAL: The sub-agent MUST:**
1. Use Skill tool to invoke `prompt-engineering` skill FIRST
2. Read the framework reference file
3. Read the role reference file
4. Read modifier reference files (if any)
5. Read the agent spec
6. THEN write the prompt following the patterns in the reference files

**XML Tags in Prompts:**
All prompts MUST use XML tags to structure sections. This improves model comprehension.

```python
CREATOR_PROMPT = """
<role>
You are a content creator...
</role>

<context>
Background information...
</context>

<task>
Your task is to...
</task>

<constraints>
- Constraint 1
- Constraint 2
</constraints>

<output_format>
Return your response as...
</output_format>
"""
```

---

## Progress Tracking

Maintain a task list throughout implementation:

```markdown
# [Project Name] - Implementation Progress

## Status

**Current Phase:** Scaffold | Tools | Agents | Prompts | Utils
**Last Updated:** YYYY-MM-DD

## Tasks

| Task | Status | Dependencies | Notes |
|------|--------|--------------|-------|
| team.py scaffold | done | - | |
| tools.py | done | scaffold | |
| Implement creator | done | tools.py | |
| Implement critic | in_progress | tools.py | |
| Prompt: creator | pending | creator impl | |
| Prompt: critic | pending | critic impl | |
| utils.py | pending | - | May not be needed |

## Completed Files

- [x] team.py (scaffold)
- [ ] team.py (full)
- [ ] tools.py
- [ ] prompts.py
- [ ] utils.py

## Notes

[Implementation decisions, issues encountered, etc.]
```

---

## Handling Nested Teams

For nested teams, use the **execution plan** from manifest.yaml to determine phasing.

If no execution plan exists, process depth-first with parallelization:

1. Read `manifest.yaml` for the execution plan (or fall back to hierarchy)
2. Sub-teams at the same level can be implemented in parallel
3. Parent team waits for all sub-teams to complete
4. Top-level team.py imports and orchestrates sub-teams

**Each sub-team folder is self-contained** - has its own `agent-config.yaml`, can be processed independently.

```
Phase 1 (can run simultaneously):
├── Implement content-refinement/ (complete team)
└── Implement parallel-research/ (complete team)

Phase 2 (after Phase 1 completes):
└── Implement research-pipeline/ top-level (orchestrates sub-teams)
```

In **team mode**, each sub-team can be assigned to a different work stream's teammate. In **single-agent mode**, spawn Task sub-agents for parallel sub-team work.

---

## Cross-Session Resumption

Implementation of large systems (10+ agents, nested teams) will span multiple sessions. The `progress.md` file is the mechanism for cross-session continuity.

**How to resume from progress.md:**

1. Read `progress.md` — it contains resumption instructions at the top
2. Check **Current Phase** and **Next Chunk** to know where to pick up
3. Read the **Execution Plan Snapshot** to understand the full build order without re-parsing manifest.yaml
4. Check **Stream Status** for per-stream progress
5. Check **Open Questions / Blockers** for anything needing resolution
6. Read the framework cheatsheet (path is in progress.md Status section)
7. If team mode: re-create the team via `TeamCreate`, create remaining tasks from the Execution Plan Snapshot (only uncompleted chunks), and spawn teammates for streams with remaining work
8. Continue from the **Next Chunk**

**Keeping progress.md current:**

- Update **Current Phase** and **Next Chunk** whenever you move to a new chunk
- Update chunk status in the **Execution Plan Snapshot** (pending → in_progress → done)
- Update **Stream Status** after each chunk completion
- Add entries to **Session Log** at the start and end of each session
- Add blockers to **Open Questions / Blockers** immediately when encountered
- Update progress.md BEFORE ending a session — the next session depends on it

---

## Template-to-Instances — BLOCKING REQUIREMENT

⚠️ **CRITICAL: This is NOT optional. Factory functions are FORBIDDEN for template instances.**

When multiple sub-teams share the same structure but differ in configuration (e.g., 5 search loops each targeting a different platform), generate each instance as a **standalone, self-contained module**.

**Pattern recognition:** A generic template spec is referenced by multiple sub-teams. Each sub-team has its own folder with its own `team.md` and `agent-config.yaml`, but the structure (agents, flow, pattern) is identical — only the configuration values differ (API keys, actor names, platform-specific parameters).

❌ **WRONG — Factory Functions (DO NOT DO THIS):**
```python
# src/research/research_loop.py
class ResearchLoop(dspy.Module):
    def __init__(self, search_tools, search_instructions, ...):
        # Generic implementation
        pass

def create_linkedin_keyword_loop(flash_lm):
    return ResearchLoop(
        search_tools=[search_linkedin_keyword],
        search_instructions=_LINKEDIN_KEYWORD_SEARCH_INSTRUCTIONS,
        ...
    )

def create_x_trending_loop(flash_lm):
    return ResearchLoop(...)
```

**Why this is wrong:**
- Violates isolation — changing one instance risks breaking others
- Makes debugging harder — error could be in generic class or instance config
- Prevents independent evolution — instances can't diverge over time
- LLM maintaining one instance must understand all instances

✅ **CORRECT — Self-Contained Modules:**
```
src/research/
├── linkedin_keyword/
│   ├── team.py          # LinkedInKeywordLoop(dspy.Module)
│   ├── signatures.py    # LinkedInKeywordSearchSignature, LinkedInKeywordAnalysisSignature
│   └── __init__.py
├── x_trending/
│   ├── team.py          # XTrendingLoop(dspy.Module)
│   ├── signatures.py    # XTrendingSearchSignature, XTrendingAnalysisSignature
│   └── __init__.py
```

Each instance is FULLY self-contained:
- Own directory
- Own team.py with instance-specific implementation
- Own signatures.py with platform-specific prompts baked into docstrings
- Own __init__.py
- Zero imports from sibling instances
- Can be understood and modified without reading siblings

**If you find yourself writing factory functions, STOP. Generate separate modules instead.**

**Generation rules:**

1. Each instance gets its own directory with its own `team.py`, `signatures.py`, agent files — the full set
2. **No shared imports between sibling instances** — each module is fully self-contained
3. If one instance breaks, fixing it should never risk breaking siblings
4. Each module must be understandable in isolation without cross-referencing the template or siblings

**Efficient generation approach:**

1. Read the first instance's spec fully and generate its complete module
2. For subsequent instances, diff against the first: note what changes (actor config, platform name, model parameters) and what stays the same (structure, flow, pattern)
3. Generate each subsequent instance as a standalone copy with its specific values substituted
4. Do NOT create a shared base class or parameterized factory — the duplication is intentional for maintainability

**Why duplication over abstraction:** An LLM maintaining `linkedin-keyword` should read one self-contained module, change it, and not risk breaking `x-trending`. Each instance can diverge independently over time without refactoring shared code.

---

## 3-Level Nesting

For systems with 3+ levels of nesting (root pipeline → phase teams → sub-teams), understand the import and orchestration chain:

**Example: 3-level hierarchy**

```
root pipeline.py                          # Level 1 — imports phase team modules
├── research_team/team.py                 # Level 2 — imports sub-team modules
│   ├── linkedin_keyword/team.py          # Level 3 — contains its own agents
│   ├── x_trending/team.py               # Level 3
│   ├── analytics_team/team.py           # Level 3
│   └── ...
└── ideation_team/team.py                # Level 2 — contains its own agents
```

**Import chain:** `root.forward() → phase_team.forward() → sub_team.forward() → agent.forward()`

```python
# Level 1: root pipeline.py
from src.research_team.team import ResearchPhase
from src.ideation_team.team import IdeationPipeline

class RootPipeline(dspy.Module):
    def __init__(self):
        self.research = ResearchPhase()
        self.ideation = IdeationPipeline()

    async def aforward(self, **inputs):
        research_output = await self.research.aforward(**inputs)
        return await self.ideation.aforward(research=research_output, **inputs)
```

```python
# Level 2: research_team/team.py (fan-in-fan-out orchestrating sub-teams)
from src.research_team.linkedin_keyword.team import LinkedInKeywordLoop
from src.research_team.x_trending.team import XTrendingLoop
from src.research_team.analytics_team.team import AnalyticsTeam

class ResearchPhase(dspy.Module):
    def __init__(self):
        self.linkedin_keyword = LinkedInKeywordLoop()
        self.x_trending = XTrendingLoop()
        self.analytics = AnalyticsTeam()
        # ... more sub-teams

    async def aforward(self, **inputs):
        results = await asyncio.gather(
            self.linkedin_keyword.aforward(**inputs),
            self.x_trending.aforward(**inputs),
            self.analytics.aforward(**inputs),
            return_exceptions=True,
        )
        # Synthesize results...
```

```python
# Level 3: research_team/linkedin_keyword/team.py (loop with its own agents)
class LinkedInKeywordLoop(dspy.Module):
    def __init__(self):
        self.search = dspy.ReAct(SearchSignature, tools=[apify_search])
        self.analysis = dspy.Predict(AnalysisSignature)

    async def aforward(self, **inputs):
        for i in range(max_iterations):
            search_result = await self.search.aforward(**inputs)
            analysis = await self.analysis.aforward(data=search_result)
            if analysis.satisfied:
                break
        return analysis
```

**Mixed-pattern guidance:**

When a parent team orchestrates children that use different patterns (e.g., fan-in-fan-out parent with loop children AND fan-in-fan-out children):

- The parent's `team.py` uses `asyncio.gather()` to run all sub-teams in parallel
- Each sub-team internally uses its own pattern (loops iterate, fan-out teams parallelize)
- The parent does NOT need to know the internal pattern of its children — it only calls `sub_team.aforward()` and receives the output
- Each sub-team is a self-contained `dspy.Module` that hides its internal orchestration

---

## Team Mode Orchestration

When the execution plan (from manifest.yaml) contains parallel phases with multiple work streams, use Claude Code agent teams to execute chunks in parallel.

**This section only applies when Step 4.5 in Phase 0 determined TEAM MODE.**

### Step 1: Create the Team

```
Use TeamCreate to set up the team:
- team_name: project name (e.g., "youtube-summarizer")
- description: Brief description of the implementation work
```

### Step 2: Create ALL Tasks Upfront

Read the execution plan and create one `TaskCreate` per chunk:

```
For each phase in execution-plan.phases:
  For each chunk in phase.chunks:
    TaskCreate:
      subject: chunk.name
      description: chunk.description + stream info + skills to load
      activeForm: "Implementing [chunk.name]"

Then set dependencies:
  - Tasks in Phase 1: no blockedBy
  - Tasks in Phase 2: blockedBy = [all Phase 1 task IDs]
  - Tasks in Phase N: blockedBy = [all Phase N-1 task IDs]
  - Chunk-level deps: add specific task IDs to blockedBy as needed
```

### Step 3: Spawn Teammates from Work Streams

For each unique work stream in the execution plan, use the `agent-impl-teammate-spawn` skill to generate prompt files, then spawn teammates with minimal prompts pointing to those files.

```
Skill tool -> skill: "agent-impl-teammate-spawn"
```

Follow the skill's step-by-step instructions. It will:
1. Read manifest.yaml and agent-config.yaml
2. Generate a prompt file per stream at `{project}/teammate-prompts/{team}/{stream}.md`
3. Each file includes the exact skills to load, how to load them, tasks, validation checklists

Then spawn each teammate:

```
Task tool:
  team_name: [project-name]
  name: [stream-name]
  subagent_type: general-purpose  (or prompt-creator for prompts stream)
  prompt: |
    You are teammate [stream-name] on team [project-name].

    Read your full instructions at:
      [project-path]/teammate-prompts/[team-name]/[stream-name].md

    Follow ALL steps in order. DO NOT skip Step 1 (Load Required Skills).
    After loading skills, confirm to team-lead via SendMessage.
```

### Step 4: Verify Skill Loading (MANDATORY — DO NOT SKIP)

This is the enforcement mechanism. Without this step, teammates will skip skill loading and produce broken code. This has been proven: in NS-1158, 4/5 teammates skipped skills and produced incorrect implementations.

After spawning all teammates:

1. Wait for the first message from each teammate
2. The message MUST confirm skill loading with the specific skill names (e.g., "Skills loaded: agent-teams, individual-agents")
3. If the first message is about anything other than skill loading — the teammate skipped Step 1. Send them back:
   > "STOP. You must load your required skills before doing any work. Go back to Step 1 in your prompt file. Use the Skill tool to load each skill listed there. Confirm to me when done."
4. Do NOT assign tasks, do NOT allow work to begin, do NOT respond to implementation questions until skills are confirmed
5. If a teammate claims a task without confirming skills — revoke it immediately and enforce loading

**Enforcement rule:** If a teammate completes a file without confirming skill loading,
assume it's wrong and request skill-guided review before accepting the work.

### Step 5: Monitor Phase Execution

- Teammates check TaskList for available (unblocked) tasks in their stream
- All chunks in a phase execute in parallel across teammates
- When a teammate completes a chunk, it marks the task complete and checks for next work
- Phase barriers are enforced via `blockedBy` — Phase 2 tasks unblock when all Phase 1 tasks complete
- The lead monitors progress via TaskList and handles any issues

### Step 6: Handle Inter-Agent Communication

The `communication` section of the execution plan defines what needs to be shared:

- After a phase completes, teammates send relevant information to downstream streams via `SendMessage`
- Example: tools stream sends function signatures to scaffold stream after Phase 1
- The lead can relay information between teammates if direct messaging isn't sufficient

### Step 7: Finalization

After all phases complete:
1. Lead validates all files exist and are internally consistent
2. Run tests if defined in acceptance criteria
3. Shutdown teammates via `SendMessage(shutdown_request)`
4. Clean up team via `TeamDelete`
5. Clean up teammate prompt files:
   ```bash
   rm -rf {project-path}/teammate-prompts/{team-name}/
   rmdir {project-path}/teammate-prompts/ 2>/dev/null
   ```

### Teammate Spawn Prompt Generation

Teammate prompts are generated by the `agent-impl-teammate-spawn` skill (see Step 3 above). The skill produces structured prompt files from manifest.yaml data. Do NOT write teammate prompts inline — always use the skill to generate them as files.

---

## File Generation Order

**LangGraph (per team including nested):**

1. **team.py scaffold** — Orchestration structure + placeholder agents
2. **tools.py** — Tool definitions (if needed)
3. **team.py full** — Fill in agent implementations
4. **prompts.py** — All prompts (parallel generation via prompt-creator sub-agents)
5. **utils.py** — Shared utilities (if needed)
6. **main.py** — FastAPI wrapper (root level only)

**DSPy (per team including nested):**

1. **signatures.py + prompts/*.md** — Signature classes (empty docstrings) + co-located prompt .md files loaded via `__doc__`
2. **tools.py** — Tool functions returning dicts (if needed)
3. **utils.py** — Singleton LM factories, formatters, retry wrapper (REQUIRED)
4. **models.py** — Pydantic models for complex nested outputs (if needed)
5. **team.py** — dspy.Module with Predict/ChainOfThought instances
6. **main.py** — FastAPI wrapper (root level only)

**Key DSPy differences:**
- signatures.py has empty docstrings; rich prompts are in `prompts/{agent_name}.md` files
- prompts/*.md files use XML tags (`<who_you_are>`, `<task>`, etc.) and are loaded at import time via `__doc__` reassignment
- NO prompts.py file — use `prompts/` directory with `.md` files instead
- prompt-engineering skill IS used for DSPy (teammates load it when writing `.md` prompt files)
- utils.py is REQUIRED (not optional) — must have singleton LM + formatters
- models.py only for complex Pydantic outputs, NOT for signatures

---

## Templates

Progress tracking template: `templates/progress.md`

---

## Feedback Loop: Updating Cheat Sheets

**When you receive feedback about generated code, update the cheat sheet to prevent the same mistake.**

This creates a learning loop where the cheat sheets evolve based on real-world implementation issues.

### When to Update

Update the cheat sheet when you receive feedback that:
- Points out an incorrect pattern you used
- Identifies a framework anti-pattern
- Highlights a rule you didn't follow
- Reveals a common mistake

### How to Update

1. **Identify the framework** — Which cheat sheet needs updating?
   - `frameworks/langgraph/CHEATSHEET.md`
   - `frameworks/dspy/CHEATSHEET.md`

2. **Categorize the feedback:**
   - **Critical Rule** — Add to "Critical Rules" section
   - **Anti-pattern** — Add to "Anti-Patterns" section with wrong code example
   - **Pattern clarification** — Add to relevant pattern section

3. **Format the update:**

**For anti-patterns:**
```markdown
### DO NOT: [Description of mistake]

```python
# WRONG
[Code that was incorrectly generated]
```

**Why:** [Explanation of why this is wrong]

**Correct approach:**
```python
# CORRECT
[How it should be done]
```
```

**For critical rules:**
```markdown
### [Number]. [Rule Name]

**CORRECT:**
```python
[Correct code]
```

**WRONG - DO NOT DO THIS:**
```python
[Wrong code]
```

**Why:** [Explanation]
```

4. **Edit the cheat sheet** using the Edit tool.

### Example

**Feedback received:**
> "The ToolNode is being created inside the agent function instead of being added to the graph."

**Action taken:**
1. Open `frameworks/langgraph/CHEATSHEET.md`
2. Add to Anti-Patterns section:

```markdown
### DO NOT: Create ToolNode inside agent functions

```python
# WRONG
async def agent(state):
    if response.tool_calls:
        tool_node = ToolNode(tools)  # WRONG - created inside function
        result = await tool_node.ainvoke(...)  # WRONG - manual invocation
```

**Why:** ToolNode is designed to be a graph node. Creating it inside functions bypasses LangGraph's execution model.
```

### Mandatory Update Triggers

**Always update the cheat sheet when:**
- [ ] User explicitly says the generated code is wrong
- [ ] A pattern was used incorrectly
- [ ] The code doesn't follow framework best practices
- [ ] A debugging session reveals a systematic issue

**Do not wait for multiple occurrences.** Add to the cheat sheet on first feedback to prevent repetition.

---

## References

- `frameworks/` — Framework cheat sheets (read first!)
- `agent-teams/` — Team pattern implementations
- `individual-agents/` — Agent type implementations
- `prompt-engineering/` — Prompt frameworks, roles, modifiers
- `agent-spec-builder/` — Specification format and structure
