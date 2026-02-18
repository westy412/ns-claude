---
name: general-spec-builder
description: Transform discovery documents into implementation specs. Handles backend APIs, frontend, features, and products. Routes pure agent work to agent-spec-builder; handles hybrid work (agent + API/frontend) by producing specs for non-agent components then handing off.
allowed-tools: Read, Glob, Grep, Task, AskUserQuestion, Write, Edit
---

# General Spec Builder Skill

## Purpose

Transform a discovery document (from the `discovery` skill) into a formal spec that can be executed by `general-implementation-builder`.

**Goal:** Produce a spec detailed enough for Claude to work through autonomously, with clear work breakdown, acceptance criteria, and completion promise.

**This skill handles:**
- Backend APIs
- Frontend features
- Products (multi-component)
- Features (general)
- Hybrid work (agent + API/frontend)

**This skill routes to `agent-spec-builder` for:**
- Pure agent systems (single agent or agent teams with no API/frontend components)

---

## Key Principles

1. **Spec-driven** — The spec IS the plan. Everything an agent needs is in the spec file
2. **Collaborative** — Work WITH the user section by section. Don't fill out alone
3. **Incremental write** — Write spec sections as they're approved, not all at the end
4. **Technology-agnostic** — The template works for any work type
5. **Skill-aware** — Discover and record which skills the implementing agent should load
6. **Progress tracking** — Maintain progress document for cross-session resumption

---

## Input

A discovery document from the `discovery` skill containing:
- Problem statement, solution overview, key decisions, constraints
- Scope (in/out/deferred), context, reference files, open questions

If no discovery document exists, suggest running the `discovery` skill first.

---

## Output

A single `/specs/[name].md` file following the spec template.

The spec contains: Meta, Overview, Skills, Requirements, Architecture, Reference Files, Execution Plan (with work streams, phases, chunks, communication), Acceptance Criteria, Completion Promise, and Notes.

---

## Workflow

### Phase Routing Table

| Phase | Purpose | Reference |
|-------|---------|-----------|
| **1** | Intake — locate discovery doc, identify work type, routing decision, skill discovery | `references/phase-1-intake.md` |
| **2** | Research — codebase patterns, reference projects, web research | `references/phase-2-research.md` |
| **3** | Construction — section-by-section spec writing with user | `references/phase-3-construction.md` |
| **4** | Handoff — hybrid work handoff to agent-spec-builder (skip if not hybrid) | `references/phase-4-handoff.md` |
| **5** | Review — validation gates, user confirmation, save | `references/phase-5-review.md` |

### Phase Quick Decision

```
Starting fresh?
├── New spec → Phase 1 (Intake) → references/phase-1-intake.md
└── Resuming → Read progress.md → jump to indicated phase

At Phase 1 complete:
├── Pure agent work? → Route to agent-spec-builder, exit
└── Else → Phase 2 (Research) → references/phase-2-research.md

At Phase 2 complete:
└── Phase 3 (Construction) → references/phase-3-construction.md
    └── For Execution Plan section → references/execution-plan-guide.md

At Phase 3 complete:
├── Hybrid work? → Phase 4 (Handoff) → references/phase-4-handoff.md
└── Non-hybrid? → Phase 5 (Review) → references/phase-5-review.md

At Phase 4 complete:
└── Phase 5 (Review) → references/phase-5-review.md
```

---

## Spec Structure

The spec template lives at `templates/spec.md`. Key sections:

| Section | Purpose |
|---------|---------|
| Meta | Type, repo, status, created date |
| Overview | What and why — 2-3 paragraphs |
| Skills | Skills the implementing agent should load |
| Requirements | What must be true when done |
| Architecture | Key decisions, patterns, constraints (optional for simple work) |
| Reference Files | Files consulted during discovery and spec creation |
| Execution Plan | Work streams, phases, chunks, communication |
| Acceptance Criteria | Verifiable checks for the whole spec |
| Completion Promise | Unique string signalling spec work is complete |
| Notes | Design decisions, context discovered |

---

## Execution Plan

The execution plan is the most important section. It defines the contract between spec-builder and implementation builder.

**Detailed guidance:** Read `references/execution-plan-guide.md`

**Two execution modes the plan enables:**

| Mode | When | How |
|------|------|-----|
| **Single-agent** | No parallel phases, or teams not warranted | One agent works through phases/chunks sequentially |
| **Team mode** | 2+ streams with parallel chunks | Lead spawns teammates per stream, phase barriers via task dependencies |

---

## Validation Gates (Phase 5)

Before finalizing, these 4 checks must pass:

1. **Stream ownership** — No two streams write to the same file
2. **Chunk sizing** — Not too granular (overhead), not too large (can't complete)
3. **Acceptance criteria verifiability** — Every criterion can be objectively verified
4. **Skill assignment** — Every chunk has skills listed if applicable

Details: `references/phase-5-review.md`

---

## Sub-Agent Delegation

Use sub-agents for research to keep your context clean:

| Sub-Agent | When to Use |
|-----------|-------------|
| `codebase-researcher` | Understanding existing patterns, finding conventions |
| `web-researcher` | API docs, best practices, library patterns |

Details: `references/sub-agent-delegation.md`

---

## Handover Protocol

For cross-session resumption, save all state to `progress.md`.

**When to trigger:** Context getting large, phase boundaries, user pauses.

Details: `references/handover-protocol.md`

---

## Templates

| Template | Purpose |
|----------|---------|
| `templates/spec.md` | The spec template — copy and fill |
| `templates/progress.md` | Progress tracking for cross-session resumption |

---

## Anti-Patterns

| Don't | Why |
|-------|-----|
| Copy the entire discovery doc into the spec | Spec is operational, not exploratory |
| Make execution plan chunks too granular | Each becomes a Linear issue; too many = overhead |
| Make execution plan chunks too large | Should be completable in reasonable time |
| Put everything in one phase | Maximize parallelism — if chunks are independent, separate phases |
| Two streams writing to the same file | Causes conflicts in parallel execution |
| Skip the Architecture section for complex work | Agent needs guidance on patterns |
| Write acceptance criteria that can't be verified | "Works well" is not verifiable |
| Finalize without user confirmation | Spec drives execution; must be right |
| Include progress updates in the spec | That goes in Linear issue comments |
| Include implementation decisions | That goes in Git commit messages |
| Put detailed phase guidance in SKILL.md | All detail belongs in reference files |

---

## References

| Reference | Purpose |
|-----------|---------|
| `references/phase-1-intake.md` | Intake, routing decision, skill discovery |
| `references/phase-2-research.md` | Codebase + web research patterns |
| `references/phase-3-construction.md` | Section-by-section spec writing guidance |
| `references/phase-4-handoff.md` | Hybrid work handoff to agent-spec-builder |
| `references/phase-5-review.md` | Review, validation gates, finalize |
| `references/execution-plan-guide.md` | Deep guide on phases, chunks, streams, communication |
| `references/handover-protocol.md` | Cross-session resumption |
| `references/sub-agent-delegation.md` | Research sub-agent patterns |

---

## Related Skills

- `discovery` — Produces the discovery document this skill consumes
- `agent-spec-builder` — Handles pure agent work and hybrid handoffs
- `general-implementation-builder` — Consumes the spec this skill produces
- `project-management` — Can help create Linear issues from Execution Plan
