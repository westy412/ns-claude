---
name: handover
description: "Create a comprehensive session handover. Use when George asks for handover, handoff, end-of-session context, or wants state persisted before a new session."
argument-hint: '[linear-issue-id-or-instructions]'
---

# Handover Procedure

You are preparing a handover for yourself or the next session.

## Philosophy

State lives in Git and Linear, not in session documents. The handover:

1. Ensures state is persisted to the right places.
2. Creates a comprehensive message giving the next session full context to resume without re-asking questions or re-reading entire specs.

The next session will read reality from the spec, Linear, and git. The handover message bridges the gap between raw state and understanding. Decisions, rationale, user preferences, and gotchas do not live in git diffs.

Do not aim for brevity. Aim for completeness. Scale the handover to match the session. A 2-hour session with 8 tasks should not be compressed into 3 bullets.

## Step 1: Handle Invocation Details

Analyze any handover details the user provided with the request first. This determines what to persist and how.

If the user provided a Linear issue ID, such as `NS-123` or `TEAM-456`:

- Fetch the issue using available Linear tools, app connectors, or MCP tools.
- Treat this as the issue being worked on.
- Include its details throughout the handover.
- If Linear tooling is unavailable, say so briefly and continue with git and local context.

If the user provided custom instructions instead of a Linear issue ID:

- Prioritize those instructions.
- Explicitly address the requested points in the handover.

If the user provided no extra details, or said `NONE`:

- Check whether there is an obvious Linear issue from the conversation.
- If none is obvious, proceed without Linear context.

## Step 2: Persist State

Before creating the handover message, ensure state is properly persisted.

### Update Linear Issue

Only do this if Linear was used this session or a Linear issue was explicitly supplied.

1. Check off completed tasks in the issue description.
2. Add a progress comment summarizing what was done this session.
3. Update issue state if needed, for example moving to `In Review` if a PR was created.

Use the available Linear tools, app connectors, or MCP tools. If they are unavailable, include that limitation in the handover.

### Commit Work

If there are uncommitted changes:

1. Only commit files worked on in this session. Use `git add <specific-files>`.
2. Do not include unrelated user changes.
3. Use this commit format:

```text
NS-XXX: <action-verb> <what>

WHAT:
- <change 1>
- <change 2>

WHY: <rationale>

Linear: <issue-url>
```

Reference the Linear issue ID if one exists.

### Update Progress File

Only do this if a `progress.md` file exists for an in-flight skill workflow, such as `general-spec-builder` or `general-implementation-builder`.

1. Update it with current state, decisions made, and the exact resumption point.
2. Confirm the Drift Log / Spec-Feedback Ledger and escalation records are current — the handover's Pipeline State section reads from them.
3. Commit it with the other changes.

### Update Spec

If a Linear issue or phase was completed:

1. Check off the work breakdown item in the spec.
2. Commit the spec update.

## Step 3: Create Handover Message

Output the following in chat. Do not save it to a file.

```markdown
## Session Handover

### Context
- **Repo**: [repo name]
- **Branch**: [branch name]
- **Spec**: [path to spec file] (omit if none)
- **Linear**: [NS-XXX: Title] (omit if none used)
- **Progress file**: [path] (omit if none exists)

### Pipeline State (v4)
[Only include when a spec-folder workflow is in flight. Snapshot the three feedback layers:]
- **Layer 2 — review loop**: [latest reviews/review-NNN.md verdict (PASS/WARN/FAIL) +
  per-phase review position — which phase, clean or open findings]
- **Layer 3 — test/verification**: [latest feedback/verification-NNN.md result; latest
  feedback/testing-NNN.md testing_verdict; note "live testing owed" if typed-testing deferred]
- **Layer 4 — retro**: [retro owed? yes/no — yes when the run is ending without a process
  retro; point at the accumulated telemetry: progress.md Drift Log, escalation records]

### What Was Done
[Comprehensive account of every meaningful task completed this session.
Each bullet: action taken, file/location affected, outcome.
Do not compress. If 8 things were done, list 8 things.]

### Git State
[Branch status: clean/dirty, ahead/behind remote, stashed work]

### Commits
[`git log --oneline` for this session's commits only, with Linear issues noted:]
- `a1b2c3d NS-XXX: Description`
- `e4f5g6h Description (no issue)`
[If Linear issues were worked on but not in commit messages:]
- **Linear issues touched**: NS-XXX, NS-YYY

### Decisions Made
[Every non-obvious decision made this session, full rationale each. Split by how it was
resolved — this split is Layer-4 telemetry:]

**Autonomous fixes (Branch A — resolved from stated intent):**
- **[Decision]**: [Options, chosen, rejected and why; spec amended? where]

**Escalations (Branch B — the user was brought in):**
- **[Decision]**: [What was asked, what the user chose, what that settles going forward]

### Next Task
[The most important section. Be comprehensive.

Describe exactly what needs to happen next:
- The specific work to be done, with file paths and line numbers where useful
- Why this is the next task
- Decisions already made that affect the approach
- User preferences or constraints expressed during this session
- Edge cases or gotchas discovered that the next session needs
- Where this sits in the larger flow if applicable

Give enough context to start immediately without re-asking questions.]

### Blockers / Open Questions
[Only include if they exist. Questions needing human input.]

### Skills Needed for Next Session
[Only include if a skill is needed to continue. State which skill, where in its flow you are, and what phase or step to resume from.
Example: `general-implementation-builder - Phase 2 of 4 complete. Resume from Phase 3 (API route construction).`]

### How to Resume
1. Read: [most important file, such as spec, progress.md, or key source file]
2. Check: [git log or Linear, whichever has freshest state]
3. Start from: [exact file:line or phase/step]
```

## Key Principles

1. Do not create session documents. State lives in Git and Linear.
2. Commit before handover when the user expects persisted state.
3. Update Linear before handover when Linear was part of the work.
4. Scale to the session. A big session gets a big handover.
5. Decisions are the hardest thing to reconstruct. Git shows what changed, not why or what was rejected.
6. The `Next Task` section carries forward context. Include decisions, preferences, and gotchas that affect it.
7. List skills only if they are needed next. Do not list skills merely because they were used.
8. Carry the v4 pipeline state. Review/test/verification position and retro-owed must survive the session boundary — the loop's unit is the run, not the session.

**Execution (Claude Code):** the invocation detail arrives as the skill argument (`$ARGUMENTS`); Linear via the Linear MCP tools; the model may auto-invoke this skill when a session is wrapping up.
