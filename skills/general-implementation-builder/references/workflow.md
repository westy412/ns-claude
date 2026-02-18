# Workflow

> **Context:** This reference covers the core workflow from spec to completion. Phase 0 is fixed. All subsequent phases come from the spec's execution plan. Read this at the start of every implementation session.

---

## Phase 0: Parse Spec and Initialize

Phase 0 is the only fixed phase. It prepares everything for spec-driven execution.

### Step 1: Read the Spec File

Read the spec at the path provided by the user (typically `/specs/[name].md`).

If no path provided, ask: "Which spec should I implement? Provide the path to the spec file."

### Step 2: Parse the Spec

Follow `references/spec-parsing.md` to extract:
- Meta (type, repo, status)
- Skills (top-level skills to load)
- Execution Plan (streams, phases, chunks, communication)
- Acceptance Criteria
- Completion Promise

If the spec's Status is `complete`, inform the user and stop.
If the spec's Status is `draft`, warn the user before proceeding.

### Step 3: Load Top-Level Skills

From the spec's Skills section, load skills one at a time using the Skill tool:

```
Skill tool -> skill: "[skill-name]"
```

These are top-level skills for the lead agent. Chunk-level and stream-level skills are loaded by teammates (team mode) or just-in-time (single-agent mode).

**Context budget rule:** Only load ONE skill at a time. If the spec lists multiple skills, load the most relevant one first. Load others as needed during execution.

### Step 4: Determine Execution Mode

```
Does the execution plan have 2+ streams in any phase?
├── Yes → TEAM MODE
│   Read: references/team-mode.md
│   Use: teammate-spawn skill to generate prompt files
│
└── No → SINGLE-AGENT MODE
    Read: references/single-agent-mode.md
    Execute phases sequentially
```

**Decision inputs:**
- Count distinct streams across all chunks
- If 2+ streams exist in the same phase, chunks can run in parallel → team mode
- If only 1 stream, or all chunks are sequential → single-agent mode
- If execution plan is missing entirely → single-agent mode

### Step 5: Initialize Project

Navigate to the target repository:

```bash
cd [repo-path]
```

Verify the repo exists. If not, ask the user.

If the spec requires project initialization (new project, dependencies, etc.), handle it based on the spec's requirements and architecture section. This is technology-agnostic — the spec and its skills define what initialization looks like.

### Step 6: Create Progress Document

Create `progress.md` in the project root using `templates/progress.md`.

1. Read the template
2. Populate with data from the parsed spec:
   - All streams from Work Streams table
   - All phases and chunks from Execution Plan
   - Spec file path
   - Execution mode (team or single-agent)
3. Write to `{repo-root}/progress.md`

This file is the single source of truth for cross-session resumption.

### Step 7: Update Spec Status

Update the spec's Meta table: `Status: draft` → `Status: in-progress`

### Step 8: Proceed to Execution

- **Team mode:** Read `references/team-mode.md` and follow its workflow
- **Single-agent mode:** Read `references/single-agent-mode.md` and follow its workflow

---

## Spec-Driven Phases

After Phase 0, all phases come directly from the spec's execution plan. The builder does NOT define its own phases — it follows whatever the spec prescribes.

**Phase execution rules:**
1. Phases execute **sequentially** — Phase 2 starts only after ALL Phase 1 chunks complete
2. Chunks within a phase execute **in parallel** (team mode) or **sequentially** (single-agent mode)
3. Each chunk maps to a task in the task list
4. Update progress.md after each chunk completion
5. Follow the Communication table for inter-stream data sharing

**What drives each chunk:**
- The chunk's outcome statement defines success
- The chunk's sub-tasks define the work items
- The chunk's skills define what patterns to follow
- The chunk's stream defines file ownership

---

## Completion

After all phases complete:

### Step 1: Verify Acceptance Criteria

Read the spec's Acceptance Criteria section. For each criterion:

1. If it includes a command (e.g., `pytest tests/`), run it
2. If it's a behavioral check, verify the implementation matches
3. Mark each criterion as pass/fail

**If any criterion fails:** Fix the issue before proceeding. If you can't fix it, report to the user.

### Step 2: Output Completion Promise

Only when ALL acceptance criteria pass:

1. Output the completion promise string from the spec (wrapped in `<promise>` tags)
2. Update the spec's Meta table: `Status: in-progress` → `Status: complete`
3. Update progress.md: set all chunks to `done`, add final session log entry

### Step 3: Clean Up (Team Mode Only)

If team mode was used:
1. Shutdown all teammates via `SendMessage(shutdown_request)`
2. Delete the team via `TeamDelete`
3. Clean up teammate prompt files:
   ```bash
   rm -rf {repo-path}/teammate-prompts/{team-name}/
   rmdir {repo-path}/teammate-prompts/ 2>/dev/null
   ```

---

## Cross-Session Resumption

If you're starting a NEW session on an existing implementation:

1. Read `progress.md` — it contains resumption instructions at the top
2. Check **Current Phase** and **Next Chunk** to know where to pick up
3. Read the **Execution Plan Snapshot** to understand build order
4. Check **Stream Status** for per-stream progress
5. Check **Open Questions / Blockers** for unresolved items
6. Skip completed chunks (marked `done`)
7. If team mode: re-create team, create remaining tasks, spawn teammates for streams with remaining work
8. Continue from the **Next Chunk**

Full details: `references/progress-tracking.md`
