# Progress Tracking & Cross-Session Resumption

> **Context:** This reference covers maintaining progress.md for task tracking and how to resume implementation across sessions. Read this when starting a new session or needing to understand progress tracking mechanics.

---

## Creating Progress Document

Create `progress.md` during Phase 0, BEFORE starting any implementation work.

### Steps:

1. **Read the template:** `templates/progress.md`
2. **Populate from the parsed spec:**
   - All streams from the Work Streams table
   - All phases and chunks from the Execution Plan
   - Spec file path
   - Execution mode (team or single-agent)
3. **Write to:** `{repo-root}/progress.md`

### Populating the Execution Plan Snapshot:

For each phase in the spec, create a table:

```markdown
#### Phase 1 — [Phase Name]

| Chunk | Stream | Status | Notes |
|-------|--------|--------|-------|
| [chunk-name] | [stream] | pending | |
```

For Phase 2+, add the Blocked By column:

```markdown
#### Phase 2 — [Phase Name]

| Chunk | Stream | Status | Blocked By | Notes |
|-------|--------|--------|------------|-------|
| [chunk-name] | [stream] | pending | Phase 1 | |
```

### Populating Stream Status:

For each stream, list its chunks across all phases:

```markdown
### [Stream Name]

**Owns:** [file list from spec]
**Skills:** [skills from spec]

| Phase | Chunk | Status | Key Output |
|-------|-------|--------|------------|
| 1 | [chunk-name] | pending | |
| 2 | [chunk-name] | pending | |
```

---

## Updating Progress

Update progress.md at these moments:

| Event | What to Update |
|-------|----------------|
| Starting a chunk | Chunk status: `pending` → `in_progress` |
| Completing a chunk | Chunk status: `in_progress` → `done`, add Key Output |
| Phase boundary | Current Phase, Next Chunk |
| Encountering a blocker | Add to Open Questions / Blockers |
| Making a design decision | Add to Implementation Notes → Decisions Made |
| Deviating from spec | Add to Implementation Notes → Deviations from Spec |
| Starting a session | Add Session Log entry |
| Ending a session | Update Session Log with summary |

**CRITICAL: Update progress.md BEFORE ending a session.** The next session depends on it.

---

## Cross-Session Resumption

When starting a NEW session on an existing implementation:

1. **Read progress.md** — it contains resumption instructions at the top
2. **Check Current Phase and Next Chunk** to know where to pick up
3. **Read the Execution Plan Snapshot** to understand the full build order without re-parsing the spec
4. **Check Stream Status** for per-stream progress
5. **Check Open Questions / Blockers** for anything needing resolution
6. **Skip completed chunks** — only work on pending/in_progress items
7. **If team mode:** Re-create team via `TeamCreate`, create remaining tasks from the Execution Plan Snapshot (only uncompleted chunks), spawn teammates for streams with remaining work
8. **Continue from the Next Chunk**

### Re-creating Team Mode After Resumption

If the previous session used team mode:

1. `TeamCreate` with the same team name
2. Create tasks ONLY for uncompleted chunks (skip `done` chunks)
3. Set phase dependencies (blockedBy) based on remaining work
4. Spawn teammates only for streams that have remaining chunks
5. Continue monitoring as normal

---

## Chunk Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Not started |
| `in_progress` | Currently being worked on |
| `done` | Completed successfully |
| `blocked` | Cannot proceed — see Open Questions / Blockers |
| `skipped` | Intentionally skipped (e.g., not needed) |
