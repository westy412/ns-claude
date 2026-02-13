# Phase 5: Execution Plan

Define HOW the spec should be implemented — what can be done in parallel, what's sequential, and how agents should communicate. This plan goes in two places: `manifest.yaml` (machine-readable) and `progress.md` (human-readable summary).

---

## Step 1: List Implementation Tasks

For each team (including nested), identify the files that need to be created:
- `team.py` (scaffold, then full implementation)
- `tools.py` (if agents use tools)
- `prompts.py` / `signatures.py` (depending on framework)
- `utils.py` (if needed)
- `.env.example`
- `main.py` (FastAPI wrapper)

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

**DSPy typical execution plan:**
```
Phase 1 — Signatures + Tools (parallel):
  Stream signatures: signatures.py (all signature classes with docstrings)
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
