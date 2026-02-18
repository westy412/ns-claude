# [Project Name] - Implementation Progress

## Resumption Instructions

**If you are resuming this implementation in a new session, follow these steps:**

1. Read THIS file (`progress.md`) completely — it is your entry point
2. Read the spec file listed in "Spec Location" below
3. Check the **Current Phase** and **Next Chunk** below to know where to pick up
4. Read the **Execution Plan Snapshot** to understand the full build order without re-parsing the spec
5. Check **Stream Status** to understand what's done and what's in progress
6. Check **Open Questions / Blockers** for anything that needs resolution before continuing
7. If team mode was active: re-create the team, re-create remaining tasks from the Execution Plan Snapshot, and spawn teammates for streams that have remaining work
8. Begin work on the **Next Chunk**

---

## Status

**Current Phase:** [Phase N — Phase Name]
**Next Chunk:** [chunk-name] (stream: [stream-name])
**Execution Mode:** single-agent | team
**Last Updated:** YYYY-MM-DD
**Spec Location:** [path to /specs/[name].md]

---

## Execution Plan Snapshot

> Mirrors the spec's execution plan so a new session understands build order without re-parsing.

### Streams

| Stream | Responsibility | Owns | Skills |
|--------|---------------|------|--------|
| [stream-name] | [responsibility] | [file list] | [skills] |

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

- [ ] [file path]
- [ ] [file path]

---

## Implementation Notes

### Decisions Made
-

### Issues Encountered
-

### Deviations from Spec
-

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
