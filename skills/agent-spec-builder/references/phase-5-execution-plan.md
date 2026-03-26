# Phase 5: Execution Plan

Define HOW the spec should be implemented — what can be done in parallel, what's sequential, and how agents should communicate. This plan goes in two places: `manifest.yaml` (machine-readable) and `progress.md` (human-readable summary).

---

## Step 1: List Implementation Tasks

For each team (including nested), identify the files that need to be created:
- `team.py` (dspy.Module orchestration — DSPy) or `team.py` (StateGraph — LangGraph)
- `tools.py` (if agents use tools)
- `signatures.py` + `prompts/*.md` (DSPy) or `prompts.py` (LangGraph)
- `utils.py` (REQUIRED for DSPy — singleton LM, formatters; optional for LangGraph)
- `models.py` (if complex Pydantic outputs needed)
- `.env.example`
- `main.py` (FastAPI wrapper — root level only)

**DSPy file placement:** Each team directory sits directly under `src/` (e.g., `src/content_draft/team.py`). Do NOT use wrapper directories like `src/programs/` or `src/routes/`. See `agent-implementation-builder/references/dspy/file-organization.md` for the full reference.

## Step 2: Group into Phases

Analyze dependencies to determine what can run in parallel:

**LangGraph typical execution plan:**
```
Phase 1 — Scaffold + Foundation (parallel):
  Stream scaffold: team.py scaffold (orchestration + placeholders)
  Stream tools: tools.py (tool definitions)
  Skills: scaffold → [agent-teams, individual-agents], tools → [tools-and-utilities]

Phase 2 — Agent Implementation (parallel):
  Stream scaffold: Fill in agent implementation functions in team.py
  (If agents are independent, each can be a separate chunk)
  Skills: [individual-agents]

Phase 3 — Prompts (parallel):
  Stream prompts: One chunk per agent prompt (sub-agents can work in parallel)
  Skills: [prompt-engineering]

Phase 4 — Finalization (parallel):
  Stream scaffold: utils.py, .env.example, main.py
```

**DSPy typical execution plan (single/nested team):**
```
Phase 1 — Signatures + Tools (parallel):
  Stream signatures: signatures.py (all signature classes with empty docstrings)
  Stream tools: tools.py (tool functions)
  Skills: signatures → [prompt-engineering], tools → [tools-and-utilities]

Phase 2 — Utilities + Models (parallel):
  Stream scaffold: utils.py (singleton LM, formatters)
  Stream scaffold: models.py (Pydantic models if needed)

Phase 3 — Team Module:
  Stream scaffold: team.py (dspy.Module — needs everything above)
  Skills: [agent-teams, individual-agents]

Phase 4 — Finalization (parallel):
  Stream scaffold: .env.example, main.py
```

**DSPy multi-team service execution plan:**
```
Phase 1 — Foundation (parallel):
  Stream foundation: shared infrastructure (models/, utils/, services/, config.py)
  Stream prompts: extract/create prompt .md files for all teams
  Skills: foundation → [], prompts → [prompt-engineering]

Phase 2 — Team Implementation (parallel, one chunk per team):
  Stream team-X: src/team_x/ — team.py + signatures.py + prompts/*.md
  Stream team-Y: src/team_y/ — team.py + signatures.py + prompts/*.md
  Skills: each team stream → [individual-agents, prompt-engineering]

Phase 3 — Endpoints & Integration:
  Stream endpoints: main.py + src/schemas.py (endpoint handlers + request/response schemas)
  Skills: []
```

**DSPy path rules (MUST follow file-organization reference):**
- Team directories go directly under `src/` — e.g., `src/content_draft/`, NOT `src/programs/content_draft/`
- NO wrapper directories: no `src/programs/`, no `src/routes/`
- Orchestration file is `team.py` in every team directory, NOT `program.py`
- Endpoint handlers go in `main.py`, NOT in `src/routes/`
- Stream `owns` paths must match: `src/{snake_case_team_name}/`

## Step 3: Define Work Streams

Group related chunks so the same agent handles them across phases:

| Stream | Typical Responsibility | Skills |
|--------|----------------------|--------|
| scaffold | Orchestration logic, utilities, service wrapper | agent-teams, individual-agents |
| tools | Tool implementation from spec documentation | tools-and-utilities |
| prompts/signatures | Agent prompt/signature creation | prompt-engineering |

**MANDATORY: Every stream MUST have a `skills` field** in manifest.yaml, even if the list is empty (`skills: []`). This tells the impl-builder which skills to load for that stream's work. Omitting the field causes the impl-builder to guess, leading to incorrect skill loading or missing context.

## Step 4: Define Communication

What information needs to flow between streams:

| From | To | When | What |
|------|----|------|------|
| tools | scaffold | After Phase 1 | Tool function signatures and return types |
| scaffold | prompts | After Phase 2 | Agent function structures and state schemas |

## Step 5: Write to manifest.yaml

Populate the `execution-plan` section using the template format:
- `streams:` — work stream definitions with skills
- `phases:` — phase definitions with chunks
- `communication:` — inter-stream communication needs

## Step 6: Validate Paths (DSPy Only)

**BLOCKING — do not finalize the execution plan until all checks pass.**

For DSPy projects, verify all generated `owns` paths and chunk descriptions against the file-organization reference (`agent-implementation-builder/references/dspy/file-organization.md`):

| Check | Rule | Bad Example | Good Example |
|-------|------|-------------|--------------|
| No `programs/` wrapper | Teams go directly under `src/` | `src/programs/content_draft/` | `src/content_draft/` |
| No `routes/` wrapper | Endpoints go in `main.py` | `src/routes/` | `main.py` |
| Correct orchestration file | DSPy uses `team.py` | `program.py` | `team.py` |
| Snake_case directories | Python packages must be importable | `src/content-draft/` | `src/content_draft/` |
| Prompt file location | Prompts are in `prompts/*.md` inside team dir | `src/programs/*/prompts/` | `src/{team}/prompts/` |

**If any path uses `programs/`, `routes/`, or `program.py`**, fix it before proceeding. These wrapper directories violate DSPy principle #6 ("No separate routes/ or programs/ wrapper directories") and principle #7 ("Sub-teams sit directly under src/").
