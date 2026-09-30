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

### Step 6: Locate or Populate Progress Document

The progress document lives in the feature folder, shared by all skills working on this feature.

**IMPORTANT:** All skills read and write ONE `progress.md` at `{feature-folder}/progress.md`. The implementation builder writes to the `## Implementation` section.

1. Derive the feature folder from the spec path (parent directory of `spec.md`)
2. Check if `{feature-folder}/progress.md` EXISTS
3. **If YES:** Read it completely. Check if it has an `## Implementation` section.
   - If the Implementation section exists → you're resuming, skip to Step 8
   - If the Implementation section is missing → append it from `templates/progress.md` (only the Implementation section onwards)
4. **If NO:** Create from `templates/progress.md` — populate all sections
5. Populate the Implementation section with data from the parsed spec:
   - All streams from Work Streams table
   - All phases and chunks from Execution Plan
   - Spec file path
   - Execution mode (team or single-agent)
6. Update the Artifacts table with what exists in the feature folder
7. Update Pipeline History with a new row for implementation start

This file is the single source of truth for the entire feature lifecycle.

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
4. Update the feature folder's `progress.md` (Implementation section) after each chunk completion
5. Follow the Communication table for inter-stream data sharing
6. At each phase boundary, run the **per-phase review** (`references/per-phase-review.md`) before starting the next phase (`execute → review → fix`); a final **big review** runs at Completion

**What drives each chunk:**
- The chunk's outcome statement defines success
- The chunk's sub-tasks define the work items
- The chunk's skills define what patterns to follow
- The chunk's stream defines file ownership

---

## Completion

After all phases complete, run the **Completion sequence**, in this fixed order on every build:
`big review → verifier → typed testing → acceptance-criteria table → completion state`

### Step 1: Big Review

Run the aggregate review across the whole change (`references/per-phase-review.md` → The big review)
for the cross-phase issues a per-phase review cannot see. Resolve findings via the autonomy rule.

### Step 2: Verify (static)

On a clean big review, invoke the `general-implementation-verifier` skill on the spec folder. It
writes `feedback/verification-NNN.md`: a PASS / WARN / FAIL verdict per criterion and a traceability
matrix. The verifier reports; it does not fix.

- The verifier runs on every build. It is not optional, and not a choice you offer the user.
- Each FAIL and WARN runs the autonomy rule and becomes a Drift Log row. Invoke the verifier again
  if the fixes were substantial.
- Team mode: release the build team first (Execution below); apply fixes yourself or through a
  focused sub-agent.

### Step 3: Live Validation

With no open verifier FAIL, hand off to typed testing — see `references/testing-handoff.md`. Its
`testing_verdict` is the live gate.

### Step 4: Acceptance-Criteria Table

Write the table into the Implementation section of `progress.md`, one row per acceptance criterion
in the spec: `# | Criterion | Evidence | Verdict | Owner | Re-check condition`.

- Draw each verdict from recorded evidence — a `testing_verdict` row, the verifier's matrix, or a
  command you run now. Only PASS closes a row; "met" without re-checkable evidence is not PASS.
- A FAIL row runs the autonomy rule: fix and re-check before Step 5, else escalate.
- Each PARTIAL, UNTESTED, or deferred row needs an owner and a re-check condition. A row marked
  "deferred by design" must cite the spec line that allows the deferral.

### Step 5: Completion State

- **Every row PASS:** output the completion promise string from the spec (wrapped in `<promise>`
  tags). Set the spec Meta `Status: complete` and the progress Status to `complete`. Mark all chunks
  `done` and add a final Session Log entry.
- **Any row not PASS:** do not output the completion promise. Set the spec Meta
  `Status: builder-complete` and the progress Status to `builder-complete`. Add one Open Questions /
  Blockers row per open criterion, with its owner and re-check condition. No deploy or promotion
  step runs until each open row passes, or until the user records a waiver that names the rows.

### Execution (Claude Code)

- **Release the build team before Step 2** (team mode only). A lead runs one team at a time, and
  the verifier creates its own team. Send `SendMessage(shutdown_request)` to each teammate, then
  `TeamDelete`, then remove the prompt files:
   ```bash
   rm -rf {repo-path}/teammate-prompts/{team-name}/
   rmdir {repo-path}/teammate-prompts/ 2>/dev/null
   ```
- **Invoke the verifier** via the `Skill` tool → `skill: "general-implementation-verifier"` with the
  spec-folder path.

---

## Cross-Session Resumption

If you're starting a NEW session on an existing implementation:

1. Read the feature folder's `progress.md` — check the `## Implementation` section for resumption instructions
2. Check **Current Phase** and **Next Chunk** to know where to pick up
3. Read the **Execution Plan Snapshot** to understand build order
4. Check **Stream Status** for per-stream progress
5. Check **Open Questions / Blockers** for unresolved items
6. Skip completed chunks (marked `done`)
7. If team mode: re-create team, create remaining tasks, spawn teammates for streams with remaining work
8. Continue from the **Next Chunk**

Full details: `references/progress-tracking.md`
