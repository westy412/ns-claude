---
name: general-impl-builder
description: Transform general specifications into production code. Takes general-spec-builder output and drives implementation through team mode or single-agent execution. Use when you have a complete spec and are ready to implement.
allowed-tools: Read, Glob, Grep, Task, Write, Edit, Bash, Skill
---

# General Implementation Builder Skill

## Purpose

An implementation skill that transforms `/specs/[name].md` files produced by `general-spec-builder` into production code. Technology-agnostic — all domain knowledge comes from skills listed in the spec.

**Goal:** Autonomous code generation from general specifications.

---

## When to Use This Skill

Use this skill when:
- You have a complete spec from `general-spec-builder`
- Ready to implement production code from the spec
- The work is NOT a pure agent system (for pure agents, use `agent-implementation-builder`)

**Skip this skill when:**
- Still gathering requirements (use `discovery` first)
- Still defining the spec (use `general-spec-builder` first)
- Building a pure agent system (use `agent-spec-builder` + `agent-implementation-builder`)
- Only modifying existing code without a spec

---

## Key Principles

1. **Spec-driven** — All implementation decisions come from the spec. The spec's execution plan defines phases, chunks, and streams.
2. **Parallel where possible** — Use team mode for multi-stream work. Maximize parallelism across independent chunks.
3. **Skill loading from spec** — No hardcoded technology mappings. Skills are listed in the spec's Skills section and per-chunk in the execution plan.
4. **Context-conscious** — Load skills one at a time, just-in-time. Persist progress before loading new skills.
5. **Ask when unsure** — Never guess. If the spec is unclear, information is missing, or multiple approaches are valid, ask the user.
6. **Fix propagation — sweep the codebase** — When applying a pattern fix, search ALL instances of the same pattern and fix them all. Don't just fix the one that broke.

---

## When to Ask for Feedback

**Always ask the user when:**
- Spec is missing required information
- Multiple implementation approaches are valid
- You encounter errors or unexpected behavior
- Spec seems incomplete or contradictory
- You're about to make an assumption not in the spec

**Never:**
- Invent APIs or endpoints not in the spec
- Guess at authentication methods or integrations
- Proceed with implementation when critical information is missing

---

## Input

A spec file produced by `general-spec-builder`:

```
{repo-root}/specs/[name].md
```

The spec contains: Meta, Overview, Skills, Requirements, Architecture, Reference Files, Execution Plan (Work Streams, Phases, Chunks, Communication), Acceptance Criteria, and Completion Promise.

For the full spec format, see the `general-spec-builder` skill's spec template.

---

## Output

Whatever the spec defines — this skill is technology-agnostic. The spec's type (backend-api, frontend, agent-*, etc.) determines the output structure. Skills listed in the spec provide the implementation patterns.

---

## Workflow

### Phase Routing Table

| Step | What | Reference |
|------|------|-----------|
| Parse Spec | Read and parse `/specs/[name].md` | `references/spec-parsing.md` |
| Initialize | Phase 0 setup, create progress.md, determine execution mode | `references/workflow.md` |
| Team Mode | Parallel execution with teammates (2+ streams) | `references/team-mode.md` |
| Single-Agent Mode | Sequential execution (1 stream or simple specs) | `references/single-agent-mode.md` |
| Completion | Verify acceptance criteria, output completion promise | `references/workflow.md` |

### Phase 0: Parse Spec and Initialize (Fixed)

1. Read the spec file
2. Parse all sections (see `references/spec-parsing.md`)
3. Load top-level skills from the Skills section (one at a time)
4. Determine execution mode
5. Initialize project (if needed)
6. Create progress.md from template
7. Update spec status to `in-progress`
8. Proceed to team mode or single-agent mode

Full details: `references/workflow.md`

### Spec-Driven Phases (From Execution Plan)

After Phase 0, all phases come from the spec. The builder follows whatever phases and chunks the spec defines. No fixed phase structure beyond Phase 0.

---

## Execution Mode Decision Tree

```
Does the execution plan have 2+ streams in any phase?
├── Yes → TEAM MODE (read references/team-mode.md)
│   Use teammate-spawn skill to generate prompt files
│   Each stream gets its own teammate
│
└── No → SINGLE-AGENT MODE (read references/single-agent-mode.md)
    Work through phases sequentially, chunk by chunk
```

**Decision inputs:**
- Count distinct streams across all chunks
- If 2+ streams exist in the same phase → team mode
- If only 1 stream, or no streams defined → single-agent mode
- If execution plan missing entirely → single-agent mode

---

## Delegation Strategy

```
General Implementation Builder (team lead)
├── Spawns TEAMMATES (via TeamCreate + Task tool with team_name)
│   └── Teammates can spawn SUB-AGENTS for:
│       ├── codebase-researcher → Explore patterns, find implementations
│       └── web-researcher → Read API docs, external documentation
```

| Situation | Method | Reference |
|-----------|--------|-----------|
| Parallel work streams | Teammates | `references/team-mode.md` |
| Codebase research | Sub-agent (codebase-researcher) | `references/sub-agents.md` |
| API doc research | Sub-agent (web-researcher) | `references/sub-agents.md` |

Full details: `references/sub-agents.md`

---

## Progress Tracking

**Create `progress.md` BEFORE starting implementation (Phase 0).**

| Topic | Reference |
|-------|-----------|
| Progress document format | `references/progress-tracking.md` |
| Cross-session resumption | `references/progress-tracking.md` |
| Progress template | `templates/progress.md` |

---

## Feedback Loop

When you receive feedback about generated code, record the pattern in progress.md to prevent the same mistake across chunks and sessions.

Full process: `references/feedback-loop.md`

**Mandatory triggers:**
- User says generated code is wrong
- A pattern was used incorrectly
- Code doesn't follow project conventions
- Debugging reveals a systematic issue

---

## Templates

- `templates/progress.md` — Progress tracking template for cross-session resumption

---

## References

- `references/spec-parsing.md` — How to parse the markdown spec into actionable work
- `references/workflow.md` — Core workflow: Phase 0, spec-driven phases, completion
- `references/team-mode.md` — Team mode execution with parallel streams
- `references/single-agent-mode.md` — Sequential execution for simple specs
- `references/sub-agents.md` — Delegation strategy for research sub-agents
- `references/progress-tracking.md` — Progress tracking and cross-session resumption
- `references/feedback-loop.md` — Learning from mistakes and recording patterns
