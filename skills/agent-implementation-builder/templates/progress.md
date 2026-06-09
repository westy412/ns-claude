# [Project Name] - Implementation Progress

## Resumption Instructions

**If you are resuming this implementation in a new session, follow these steps:**

1. Read THIS file (`progress.md`) completely — it is your entry point
2. Read the spec's `manifest.yaml` for system structure and execution plan
3. Read the framework cheatsheet listed in "Framework" below
4. Check the **Current Phase** and **Next Chunk** below to know where to pick up
5. Read the **Stream Status** section to understand what's done and what's in progress
6. Check **Open Questions / Blockers** for anything that needs resolution before continuing
7. If team mode was active: re-create the team, re-create remaining tasks from the Execution Plan Snapshot, and spawn teammates for streams that have remaining work
8. Begin work on the **Next Chunk**

---

## Status

**Current Phase:** [Phase N — Phase Name]
**Next Chunk:** [chunk-name] (stream: [stream-name])
**Execution Mode:** single-agent | team
**Framework:** [langgraph | dspy]
**Framework Cheatsheet:** [path to frameworks/[framework]/CHEATSHEET.md]
**Last Updated:** YYYY-MM-DD
**Spec Location:** [path to spec folder]

---

## Execution Plan Snapshot

> Mirrors the manifest.yaml execution plan so a new session understands build order without re-parsing.

### Streams

| Stream | Responsibility | Owns |
|--------|---------------|------|
| [stream-name] | [responsibility] | [file list] |

### Phases

#### Phase 1 — [Phase Name]

| Chunk | Stream | Status | Notes |
|-------|--------|--------|-------|
| [chunk-name] | [stream] | pending | |

#### Phase 2 — [Phase Name]

| Chunk | Stream | Status | Blocked By | Notes |
|-------|--------|--------|------------|-------|
| [chunk-name] | [stream] | pending | Phase 1 | |

#### Phase N — [Phase Name]

| Chunk | Stream | Status | Blocked By | Notes |
|-------|--------|--------|------------|-------|
| [chunk-name] | [stream] | pending | Phase N-1 | |

**Chunk status values:** pending | in_progress | done | blocked | skipped

---

## Stream Status

> Per-stream progress. Each stream tracks which phases/chunks are complete.

### [Stream Name]

**Owns:** [file list]
**Skills:** [skills to load]

| Phase | Chunk | Status | Key Output |
|-------|-------|--------|------------|
| 1 | [chunk-name] | pending | |
| 2 | [chunk-name] | pending | |

### [Stream Name 2]

**Owns:** [file list]
**Skills:** [skills to load]

| Phase | Chunk | Status | Key Output |
|-------|-------|--------|------------|
| 1 | [chunk-name] | pending | |

---

## Completed Files

### Top-Level
- [ ] [file]

### [Sub-Team / Module Name]
- [ ] [file]

---

## Reference Files Used

| Component | Reference Path |
|-----------|----------------|
| Team pattern | |
| [Agent-1] type | |

---

## Implementation Notes

### Decisions Made
-

### Issues Encountered
-

### Drift Log / Spec-Feedback Ledger

> One row per drift finding — anywhere built reality and the spec disagreed (per-phase review
> finding, I/O mismatch, verifier flag, user correction). Layer-4 telemetry: the run retro reads
> this table to root-cause process failures.

| Phase | Finding | Class | Resolution | Spec amended? | Escalated? | Front-load failure? |
|-------|---------|-------|------------|---------------|------------|---------------------|
| | | code-bug / spec-bug | | yes (where) / no | no (Branch A) / yes (Branch B) | yes / no |

**Class:** `code-bug` = code diverged from a correct spec. `spec-bug` = the spec was wrong
(spec-defect loopback — amend the spec, never code-only). **Front-load failure?** = yes when
discovery/spec should have caught it — every mid-build spec amendment is one.

---

## Open Questions / Blockers

> Items that need resolution. Tag with HUMAN_NEEDED if waiting on user input.

| # | Question / Blocker | Status | Resolution |
|---|-------------------|--------|------------|
| | | open / resolved | |

---

## Session Log

| Date | Phase | Summary | Key Decisions |
|------|-------|---------|---------------|
| | | | |
