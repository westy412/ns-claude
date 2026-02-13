# Workflow Phases (Framework-Agnostic)

> **Context:** This reference covers Phases 0-3 and 5-7 of the implementation workflow. These phases are framework-agnostic. For Phase 4 (Prompts/Signatures), see the framework-specific references: `references/dspy/implementation-phases.md` or `references/langgraph/implementation-phases.md`.

---

## Phase 0: Parse Spec and Initialize Project

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
  → Use **TEAM MODE** (see `references/common/team-mode.md`)
  *Important: IF YOU ARE USING TEAM MODE MAKE SURE TO LOAD IN THE agent-impl-teammate-spawn skill*

- **IF** the execution plan is purely sequential, missing, or all chunks are in one stream:
  → Use **SINGLE-AGENT MODE** (proceed to Phase 1)

Team mode uses Claude Code agent teams to execute chunks in parallel. Each work stream gets its own teammate agent with independent context. Single-agent mode works through phases sequentially.

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

---

## Phase 1: Team Scaffold

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

---

## Phase 2: Tools

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

---

## Phase 3: Agent Implementations

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

---

## Phase 5: Utilities

Create utils.py if shared utilities are needed.

Only create if:
- Multiple agents share common logic
- Team needs helper functions

---

## Phase 6: Environment Setup

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

---

## Phase 7: FastAPI Service Wrapper

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
