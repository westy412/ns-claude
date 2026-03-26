# Progress Tracking & Cross-Session Resumption

> **Context:** This reference covers maintaining progress.md for task tracking and how to resume implementation across sessions. Read this when starting a new session or needing to understand progress tracking mechanics.

---

## Locating the Progress Document

The progress document lives in the feature folder, shared by all skills.

### Location

Progress is ALWAYS at `{feature-folder}/progress.md` — the feature folder is the parent directory of the spec file.

Examples:
- Spec: `~/content-workforce/specs/2026-03-26-content-engine/spec.md` → Progress: `~/content-workforce/specs/2026-03-26-content-engine/progress.md`
- Spec: `~/inbound-workforce/specs/2026-03-26-auth-system/spec.md` → Progress: `~/inbound-workforce/specs/2026-03-26-auth-system/progress.md`

### Locate or Populate (Phase 0)

1. Derive the feature folder from the spec path (parent directory of `spec.md`)
2. **If `progress.md` EXISTS:** Read it. Check for `## Implementation` section.
   - If `## Implementation` exists → you're resuming, skip to execution
   - If `## Implementation` is missing → append the Implementation section from `templates/progress.md`
3. **If `progress.md` DOES NOT exist:** Create from `templates/progress.md`, populate all sections

### Populating the Implementation Section

From the parsed spec, populate:

**Execution Plan Snapshot** — for each phase:

```markdown
#### Phase 1 — [Phase Name]

| Chunk | Stream | Status | Commit | Notes |
|-------|--------|--------|--------|-------|
| [chunk-name] | [stream] | pending | | |
```

For Phase 2+, add the Blocked By column:

```markdown
#### Phase 2 — [Phase Name]

| Chunk | Stream | Status | Blocked By | Commit | Notes |
|-------|--------|--------|------------|--------|-------|
| [chunk-name] | [stream] | pending | Phase 1 | | |
```

**Stream Status** — for each stream:

```markdown
#### [Stream Name]

**Owns:** [file list from spec]
**Skills:** [skills from spec]

| Phase | Chunk | Status | Key Output |
|-------|-------|--------|------------|
| 1 | [chunk-name] | pending | |
| 2 | [chunk-name] | pending | |
```

**Also update:**
- Meta → Status: `implementation`
- Artifacts table → add entries for existing files
- Pipeline History → add row for implementation start
- Next Action → clear any previous handoff, note implementation is in progress

---

## Updating Progress

Update the feature folder's `progress.md` at these moments:

| Event | What to Update |
|-------|----------------|
| Starting a chunk | Chunk status: `pending` → `in_progress` |
| Completing a chunk | Chunk status: `in_progress` → `done`, add Commit hash, add Key Output |
| Phase boundary | Current Phase, Next Chunk |
| Encountering a blocker | Add to Open Questions / Blockers |
| Making a design decision | Add to Implementation Notes → Decisions Made |
| Deviating from spec | Add to Implementation Notes → Deviations from Spec |
| Completing a file | Add to Completed Files with commit hash |
| Starting a session | Add Session Log entry |
| Ending a session | Update Session Log with summary |
| All phases complete | Update Next Action with handoff to `/general-implementation-verifier` |

**CRITICAL: Update the feature folder's `progress.md` BEFORE ending a session.** The next session depends on it.

---

## Cross-Session Resumption

When starting a NEW session on an existing implementation:

1. **Read the feature folder's `progress.md`** — check the `## Implementation` section for resumption instructions
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

---

## Commit Tracking

When a chunk is completed, record the commit hash in the Execution Plan Snapshot:

```markdown
| setup-database | backend | done | abc1234 | Schema + migrations |
```

Also update the Completed Files list:

```markdown
- [x] src/db/schema.py — commit: abc1234
- [x] src/db/migrations/001.py — commit: abc1234
```

This creates traceability from spec requirements → chunks → commits, which the verification skill uses to trace what was built and when.
