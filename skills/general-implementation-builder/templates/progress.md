# [Feature Name]

## Meta

| Field | Value |
|-------|-------|
| **Workforce** | [content-workforce / inbound-workforce / outbound-workforce] |
| **Feature Folder** | [full path to specs/YYYY-MM-DD-feature-name/] |
| **Status** | brainstorm / discovery / spec-building / spec-review / implementation / verification / complete |
| **Linear Issue** | [URL or "None"] |
| **Created** | YYYY-MM-DD |
| **Last Updated** | YYYY-MM-DD |

## Next Action

> **What the next agent should do. This is the handoff message.**
>
> Read the spec at `spec.md` and the discovery document at `discovery.md` in this folder.
> Load skills: [list]
> Invoke: `/[skill-name]`

---

## Artifacts

| File | Status | Created By | Date |
|------|--------|-----------|------|
| brainstorm.md | complete / n/a | /brainstorm | |
| discovery.md | complete / n/a | /discovery | |
| spec.md OR spec/ | complete / n/a | /general-spec-builder OR /agent-spec-builder | |
| reviews/review-NNN.md | complete / n/a | /review-general-spec OR /review-agent-spec | |
| feedback/verification-NNN.md | pending / complete / n/a | /general-implementation-verifier | |

---

## Pipeline History

| Step | Skill | Date | Result | Notes |
|------|-------|------|--------|-------|
| | | | | |

---

## Brainstorm

**Completed:** [date or "N/A — discovery was entry point"]

[Brief: what was brainstormed, which idea was selected, link to idea card if applicable]

---

## Discovery

**Completed:** [date]
**Key decisions:** [numbered list]
**Constraints:** [list]
**Scope in:** [list]
**Scope out:** [list]
**Open questions resolved in spec:** [list]

---

## Spec Builder

**Completed:** [date]
**Spec type:** general / agent
**Work type:** backend-api / frontend / hybrid / agent-langgraph / agent-dspy

### Research Findings

**Codebase patterns:**
[Summary of relevant patterns in the target repo]

**Conventions to follow:**
[List]

### User Q&A

| Question | Answer |
|----------|--------|
| | |

---

## Review

**Completed:** [date]
**Skill:** /review-general-spec or /review-agent-spec
**Result:** PASS / WARN / FAIL
**Blocking issues found:** [count]
**Warnings found:** [count]
**Issues fixed:** [list what was changed]
**Review file:** reviews/review-NNN.md

---

## Implementation

**Status:** pending / in-progress / complete
**Execution Mode:** single-agent / team
**Current Phase:** [Phase N — Phase Name]
**Next Chunk:** [chunk-name] (stream: [stream-name])
**Target Repo(s):** [repo path(s)]

### Resumption Instructions

[For a new session: what to do first, which phase to resume, what's done, what's next. Must be specific enough that a cold-start session can continue without re-reading the entire spec.]

### Execution Plan Snapshot

> Mirrors the spec's execution plan so a new session understands build order without re-parsing.

#### Streams

| Stream | Responsibility | Owns | Skills |
|--------|---------------|------|--------|
| [stream-name] | [responsibility] | [file list] | [skills] |

#### Phase 1 — [Phase Name]

| Chunk | Stream | Status | Commit | Notes |
|-------|--------|--------|--------|-------|
| [chunk-name] | [stream] | pending | | |

#### Phase 2 — [Phase Name]

| Chunk | Stream | Status | Blocked By | Commit | Notes |
|-------|--------|--------|------------|--------|-------|
| [chunk-name] | [stream] | pending | Phase 1 | | |

**Chunk status values:** pending | in_progress | done | blocked | skipped

### Stream Status

#### [Stream Name]

**Owns:** [file list]
**Skills:** [skills to load]

| Phase | Chunk | Status | Key Output |
|-------|-------|--------|------------|
| 1 | [chunk-name] | pending | |

### Completed Files

- [ ] [file path] — commit: [hash]
- [ ] [file path] — commit: [hash]

### Implementation Notes

#### Decisions Made
-

#### Issues Encountered
-

#### Deviations from Spec
-

### Session Log

| Date | Phase | Summary | Key Decisions |
|------|-------|---------|---------------|
| | | | |

---

## Verification

**Status:** pending / in-progress / complete
**Report:** feedback/verification-NNN.md
**Result:** [PASS / WARNINGS ONLY / NEEDS FIXES]

---

## Open Questions / Blockers

> Items that need resolution. Tag with HUMAN_NEEDED if waiting on user input.

| # | Question / Blocker | Raised By | Status | Resolution |
|---|-------------------|-----------|--------|------------|
| | | | open / resolved | |
