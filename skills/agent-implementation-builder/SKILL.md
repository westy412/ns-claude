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

| Skill | Invoke At | What It Provides |
|-------|-----------|------------------|
| `agent-teams` | Phase 1 (Team Scaffold) | Team orchestration patterns, graph structure examples |
| `tools-and-utilities` | Phase 2 (Tools) | Tool implementation patterns, utility organization |
| `individual-agents` | Phase 3 (Agent Implementations) | Agent implementation patterns per type |
| `prompt-engineering` | Phase 4 (Prompts) | Invoked by prompt-creator sub-agent (LangGraph only) |

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

DSPy uses signature docstrings AS the prompts. There is NO separate prompts.py file.

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
        ├── signatures.py    # DSPy Signatures (prompts are in docstrings)
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
        │   ├── tools.py
        │   └── utils.py
        └── parallel-research/
            ├── team.py
            ├── signatures.py
            ├── tools.py
            └── utils.py
```

**File Placement Rules for DSPy:**

| File | What Goes Here | Required? |
|------|----------------|-----------|
| `signatures.py` | All DSPy Signature classes with rich docstrings | YES (always for DSPy) |
| `models.py` | Pydantic BaseModel classes for complex nested outputs | If needed |
| `team.py` | dspy.Module class with Predict/ChainOfThought instances | YES |
| `tools.py` | Tool functions returning dicts (NOT @tool decorated) | If agents use tools |
| `utils.py` | Singleton LM factories, formatters, retry wrapper | YES (formatters needed between stages) |
| `prompts.py` | ❌ **DO NOT CREATE** for DSPy | NO |

**Why no prompts.py for DSPy:**
DSPy Signatures use their docstrings as prompts. The docstring is compiled directly into the LLM call. Creating separate prompts.py creates confusion about which prompt is actually used.

**Where prompts live in DSPy:**
```python
# signatures.py

class MyAgentSignature(dspy.Signature):
    """
    ← THIS DOCSTRING IS THE PROMPT

    === YOUR ROLE IN THE WORKFLOW ===
    You are the [role] agent in a [pattern] pipeline.

    === YOUR TASK ===
    [Detailed task description]

    === QUALITY STANDARDS ===
    - Standard 1
    - Standard 2

    === CONSTRAINTS ===
    - Never do X
    - Always do Y
    """

    input_field: str = dspy.InputField(desc="What this input contains")
    output_field: str = dspy.OutputField(desc="What to return")
```

**Signature Organization:**
- **Small teams (1-5 agents):** All signatures in team's `signatures.py`
- **Large teams (6+ agents):** Consider grouping by role or stage within signatures.py, use comments as section headers
- **Nested teams:** Each sub-team has its own `signatures.py`; shared signatures can go in root-level `models.py` if reused

---

## Workflow

### Phase 0: Parse Spec and Initialize Project

**Step 1:** Read `spec/manifest.yaml` — this is your entry point.

The manifest provides:
1. **System type** — single-agent, agent-team, or nested-teams
2. **Hierarchy** — visual structure of teams and agents
3. **File list** — all spec files to read
4. **Implementation order** — suggested sequence

**Step 2:** Read `agent-config.yaml` for detailed configuration, including:
- Framework being used (langgraph, dspy)
- Agent types
- Tool requirements

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

Fill in placeholder functions with actual implementations.

For each agent:
1. Read agent spec (e.g., `creator.md`)
2. Read pattern reference from `agent-config.yaml → agent → reference`
   - e.g., `agent-patterns/individual-agents/langgraph/text-agent.md`
3. Generate implementation following the pattern

### Phase 4: Prompts/Signatures

**Note:** For LangGraph, the `prompt-engineering` skill is loaded by prompt-creator sub-agents in their own context windows, NOT by the main agent. Do not invoke `prompt-engineering` directly — it would waste main-agent context. The sub-agent spawn template (below) handles this. For DSPy, write signature docstrings directly without sub-agents.

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

#### DSPy: signatures.py

**CRITICAL: DSPy does NOT use prompts.py. Prompts ARE signature docstrings.**

**Strategy:** Write signatures.py directly. Do NOT spawn prompt-creator sub-agents.

**Step 1: Create signatures.py with all DSPy Signature classes**

```python
# signatures.py

import dspy
from typing import Literal, Union

class CreatorSignature(dspy.Signature):
    """
    ← THIS DOCSTRING IS THE PROMPT - Write comprehensive instructions here

    === YOUR ROLE IN THE WORKFLOW ===
    You are the Creator agent in a loop pattern. You generate initial content
    that the Critic will review. You will see the Critic's feedback in your
    conversation history when called for iteration.

    === YOUR TASK ===
    Generate creative content based on the input theme and any previous feedback.

    [... Full prompt content goes here ...]

    === QUALITY STANDARDS ===
    - Be specific and actionable
    - Incorporate critic feedback when available

    === CONSTRAINTS ===
    - Never ignore feedback
    - Always improve on previous iteration
    """

    # Inputs
    theme: str = dspy.InputField(desc="Content theme to write about")
    history: dspy.History = dspy.InputField(desc="Conversation history with critic feedback")

    # Outputs
    content: str = dspy.OutputField(desc="Generated content")


class CriticSignature(dspy.Signature):
    """
    ← THIS DOCSTRING IS THE PROMPT

    === YOUR ROLE IN THE WORKFLOW ===
    You are the Critic agent. Review content created by the Creator and provide
    structured feedback. If content passes your criteria, approve it. Otherwise,
    suggest specific improvements.

    [... Full prompt content goes here ...]
    """

    content: str = dspy.InputField(desc="Content to review")
    criteria: str = dspy.InputField(desc="Quality criteria")

    feedback: str = dspy.OutputField(desc="Specific improvement suggestions")
    passed: bool = dspy.OutputField(desc="True if content meets criteria")
    score: int = dspy.OutputField(desc="Quality score 0-100")
```

**Step 2: Write rich docstrings**

For each signature:
1. Read the agent spec (e.g., `agents/creator.md`)
2. Extract: Purpose, Key Tasks, Inputs, Outputs, Behavioral Requirements
3. Write a comprehensive docstring following DSPy conventions:
   - Start with workflow context (which stage, what comes before/after)
   - Describe the specific task
   - Include quality standards and rubrics
   - List constraints and anti-patterns
   - For enum fields, list valid values IN THE DOCSTRING
4. Use XML-style section headers for clarity: `=== SECTION NAME ===`

**Do NOT:**
- ❌ Create prompts.py for DSPy projects
- ❌ Spawn prompt-creator sub-agents for DSPy
- ❌ Put prompts anywhere except signature docstrings
- ❌ Use brief docstrings like "Extract data" - they must be comprehensive

**Why this matters:**
DSPy compiles signature docstrings directly into LLM prompts. A weak docstring = weak outputs. The docstring is the ONLY place to provide instructions to the agent. There is no separate prompt file.

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

## Task Dependencies

**When an execution plan exists in manifest.yaml**, use the phases and chunk dependencies from the plan instead of these default chains. The execution plan provides project-specific dependencies that override these defaults.

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
signatures.py (write signature docstrings directly - NO prompt-creator sub-agents)
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

For each unique work stream in the execution plan, spawn a teammate using the Task tool with `team_name` parameter.

**Critical: The spawn prompt IS the teammate's entire context.** Teammates do NOT inherit the lead's conversation history. Include everything they need:

```
Task tool:
  team_name: [project-name]
  name: [stream-name]
  subagent_type: general-purpose  (or prompt-creator for prompts stream)
  prompt: [see Teammate Spawn Prompt Template below]
```

### Step 4: Monitor Phase Execution

- Teammates check TaskList for available (unblocked) tasks in their stream
- All chunks in a phase execute in parallel across teammates
- When a teammate completes a chunk, it marks the task complete and checks for next work
- Phase barriers are enforced via `blockedBy` — Phase 2 tasks unblock when all Phase 1 tasks complete
- The lead monitors progress via TaskList and handles any issues

### Step 5: Handle Inter-Agent Communication

The `communication` section of the execution plan defines what needs to be shared:

- After a phase completes, teammates send relevant information to downstream streams via `SendMessage`
- Example: tools stream sends function signatures to scaffold stream after Phase 1
- The lead can relay information between teammates if direct messaging isn't sufficient

### Step 6: Finalization

After all phases complete:
1. Lead validates all files exist and are internally consistent
2. Run tests if defined in acceptance criteria
3. Shutdown teammates via `SendMessage(shutdown_request)`
4. Clean up team via `TeamDelete`

### Teammate Spawn Prompt Template

When spawning a teammate, provide this context:

```
"You are a teammate working on [project-name].

YOUR WORK STREAM: [stream-name]
YOUR RESPONSIBILITY: [stream responsibility from execution plan]
YOUR FILES: You own and may edit these files ONLY:
  [file list from stream.owns]
DO NOT edit files outside your ownership — message the owning stream instead.

SKILLS TO LOAD: Before starting work, use the Skill tool to load:
  [list from stream.skills, e.g.:]
  - skill: "agent-teams"
  - skill: "individual-agents"

SPEC LOCATION: [path to spec/ directory]
FRAMEWORK: [langgraph or dspy]
FRAMEWORK CHEATSHEET: [path to frameworks/[framework]/CHEATSHEET.md]
  READ THIS BEFORE WRITING ANY CODE.

WORKFLOW:
1. Load your required skills (above)
2. Read the framework cheatsheet
3. Check TaskList for available (unblocked) tasks in your stream
4. Claim a task with TaskUpdate (set status to in_progress)
5. Read the relevant spec files for context
6. Implement the chunk
7. Mark task completed with TaskUpdate
8. Check TaskList for next available task
9. If a task requires info from another stream, use SendMessage to request it

COMMUNICATION:
  [Include relevant communication patterns from execution plan, e.g.:]
  - After completing Phase 1 tools: Send function signatures to 'scaffold' stream
  - After completing Phase 2 agents: Send state schema to 'prompts' stream"
```

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

1. **signatures.py** — All DSPy Signature classes with comprehensive docstrings (prompts are HERE)
2. **tools.py** — Tool functions returning dicts (if needed)
3. **utils.py** — Singleton LM factories, formatters, retry wrapper (REQUIRED)
4. **models.py** — Pydantic models for complex nested outputs (if needed)
5. **team.py** — dspy.Module with Predict/ChainOfThought instances
6. **main.py** — FastAPI wrapper (root level only)

**Key DSPy differences:**
- signatures.py is created FIRST and contains all prompts as docstrings
- NO prompts.py file
- NO prompt-creator sub-agents
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
