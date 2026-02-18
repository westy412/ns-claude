# Team Mode Execution & Orchestration

> **Context:** This reference covers team mode — using Claude Code agent teams to execute implementation chunks in parallel. Read this when Phase 0's execution mode decision determined TEAM MODE (2+ streams in any phase).

---

## When to Use Team Mode

Use team mode when the spec's execution plan has **2+ distinct streams** in any phase, meaning chunks can run in parallel.

**Example from spec:**
```markdown
### Work Streams

| Stream | Responsibility | Owns | Skills |
|--------|---------------|------|--------|
| data | Database models | src/models/ | backend-api |
| api | API endpoints | src/api/ | backend-api |

### Phase 1: Foundation

| Chunk | Stream | Outcome | Depends On |
|-------|--------|---------|------------|
| User model | data | Database tables exist | — |
| Auth utilities | data | JWT helpers work | — |
```

If all chunks share the same stream → single-agent mode (sequential).
If chunks span different streams → team mode (parallel).

---

## Team Mode Workflow

### Step 1: Create Team and Task List

```
TeamCreate: team_name="[spec-name]-impl", description="Implementing [spec title]"
```

For each chunk in the execution plan, create a task:

```
TaskCreate:
  subject: "Phase N: [chunk-name] — [outcome summary]"
  description: "[full chunk details including outcome, sub-tasks, skills, stream]"
  activeForm: "Implementing [chunk-name]"
```

Set phase dependencies via TaskUpdate:
- Phase 1 tasks: no blockedBy
- Phase 2 tasks: blockedBy = [all Phase 1 task IDs]
- Phase 3 tasks: blockedBy = [all Phase 2 task IDs]
- If a chunk has a specific `Depends On` (e.g., "Phase 1 + specific-chunk"), set those exact dependencies

---

### Step 2: Map Streams to Skills from the Spec

**Unlike agent-implementation-builder, there is NO hardcoded stream-to-skill mapping.** All skill assignments come from the spec:

1. Read the Work Streams table → each stream has a `Skills` column
2. Read each chunk's details → chunks may list additional or overriding skills
3. The stream-level skills are the default; chunk-level skills augment or override

**Example:**
```markdown
| Stream | Responsibility | Owns | Skills |
|--------|---------------|------|--------|
| data | Database models | src/models/ | backend-api |
| api | API endpoints | src/api/ | backend-api, authentication |
```

Stream `api` needs skills: `backend-api` and `authentication`.

**If a stream has no skills listed:** The teammate proceeds without loading domain skills. This is valid for streams doing simple file operations, configurations, or work that doesn't need specialized patterns.

**CRITICAL:** Skills are loaded by teammates, NOT the lead agent. The lead's job is to pass the right skill list to each teammate via the prompt file.

---

### Step 3: Generate Teammate Prompt Files

For each stream with work, use the `teammate-spawn` skill to generate a structured prompt file.

```
Skill tool -> skill: "teammate-spawn"
```

For each stream, gather the context needed for the prompt file:

| Field | Source |
|-------|--------|
| Teammate name | Stream name from Work Streams table |
| Team name | Your TeamCreate team_name |
| Role/responsibility | `Responsibility` column from Work Streams table |
| Skills to load | `Skills` column from Work Streams table |
| Files they own | `Owns` column from Work Streams table |
| Tasks | Chunks assigned to this stream (filtered from all phases) |
| Communication outbound | Communication table rows where `From == this stream` |
| Communication inbound | Communication table rows where `To == this stream` |
| Reference files | Spec's Reference Files section (relevant subset) |

**Generate one prompt file per stream at:**
```
{repo-path}/teammate-prompts/{team-name}/{stream-name}.md
```

Follow the teammate-spawn skill's step-by-step instructions. The generated prompt file should include:

1. **Skills to load** (if any) with exact Skill tool invocation syntax
2. **Role and file ownership** from the spec's Work Streams table
3. **Tasks** — the chunks this stream handles, organized by phase
4. **Communication requirements** — what to send/expect from other streams
5. **Validation checklist** — how to verify work before marking complete

**Key difference from agent-impl-teammate-spawn:** There is no framework cheatsheet to read, no manifest.yaml to parse, no agent-config.yaml. All context comes from the markdown spec and is injected into the prompt file.

---

### Step 4: Spawn Teammates with Minimal Prompts

After generating all prompt files, spawn each teammate:

```
Task tool:
  team_name: [team-name]
  name: [stream-name]
  subagent_type: general-purpose
  model: opus (for complex streams) or sonnet (for simpler streams)
  prompt: |
    You are teammate [stream-name] on team [team-name].

    Read your full instructions at:
      [repo-path]/teammate-prompts/[team-name]/[stream-name].md

    Follow ALL steps in order. Start by reading the file completely.
```

If the teammate has skills to load, add to the prompt:
```
    DO NOT skip loading your required skills.
    After loading skills, confirm to team-lead via SendMessage.
```

---

### Step 5: Verify Skill Loading (If Skills Specified)

If any teammate's prompt includes skills to load:

1. Wait for the first message from each teammate with skills
2. The message should confirm skill loading with specific skill names
3. If the first message is about something else — the teammate skipped skill loading:
   > "STOP. You must load your required skills before doing any work. Go back to your prompt file and load each skill listed there. Confirm to me when done."
4. Do NOT allow work to begin until skills are confirmed

**If a teammate has no skills listed,** they can proceed directly to their tasks. No confirmation needed.

---

### Step 6: Monitor Phase Execution

- Teammates check TaskList for available (unblocked) tasks in their stream
- All chunks in a phase execute in parallel across teammates
- When a teammate completes a chunk, it marks the task complete and checks for next work
- Phase barriers are enforced via `blockedBy` — Phase 2 tasks unblock when all Phase 1 tasks complete
- The lead monitors progress via TaskList and handles issues

**Lead responsibilities during execution:**
1. Monitor TaskList after each teammate message
2. Check for newly unblocked tasks
3. If a teammate is idle and tasks are available, assign them
4. Handle questions or blockers from teammates
5. Update progress.md after each phase completes

---

### Step 7: Handle Inter-Stream Communication

The spec's Communication table defines what needs to be shared between streams.

**When a phase completes and communication is required:**
1. Check the Communication table for rows triggered by this phase
2. Verify the source teammate sent the required data
3. If not sent, prompt the teammate

**Communication mechanism:**
```
SendMessage:
  type: message
  recipient: [target-stream-name]
  content: [what to send — schemas, signatures, endpoints, etc.]
  summary: "[brief summary]"
```

**What to communicate:** Function signatures, model schemas, API endpoints, interface contracts — anything a downstream stream needs to use upstream work.

**Team lead responsibilities:**
- Monitor that communication happens per the Communication table
- Relay messages if direct teammate-to-teammate messaging fails
- Verify downstream teammates received the data they need

---

### Step 8: Finalization

After all phases complete:

1. **Validate completeness** — Check that all chunks are marked done in TaskList
2. **Verify acceptance criteria** — Run test commands, check behavioral criteria
3. **Fix issues** — If any criterion fails, assign fix work to the appropriate teammate
4. **Shutdown teammates** — Send shutdown requests via `SendMessage(shutdown_request)`
5. **Clean up team** — `TeamDelete`
6. **Clean up prompt files:**
   ```bash
   rm -rf {repo-path}/teammate-prompts/{team-name}/
   rmdir {repo-path}/teammate-prompts/ 2>/dev/null
   ```
7. **Output completion promise** — Only after ALL acceptance criteria pass
8. **Update spec status** — `Status: in-progress` → `Status: complete`

---

## Team Lead Progress Management

As team lead, you MUST:

**1. Create progress.md BEFORE spawning teammates**
- Use template from `templates/progress.md`
- Populate Execution Plan Snapshot with all chunks from the spec
- Set initial status: all "pending"

**2. Update progress.md after each phase completes**
- Mark completed chunks as "done"
- Update "Current Phase" and "Next Chunk"
- Add session log entry

**3. Monitor TaskList after each teammate message**
```
TaskList → check for newly unblocked tasks → assign to idle teammates
```

**4. Enforce cross-stream communication**
- When a chunk completes, check the Communication table
- If communication required, verify SendMessage was sent
- If not sent, prompt the teammate

**5. Validate before proceeding to next phase**
- All Phase N tasks must be "completed" before Phase N+1 starts
- Check that all communication happened
- Spot-check 1-2 files for correctness

---

## Task Dependencies in Team Mode

The spec's execution plan is the SOLE source of truth for phasing:
- **Phases** — ordered stages that execute sequentially
- **Chunks** — units of work within a phase that can run in parallel
- **Streams** — work streams that own specific files; each teammate maps to a stream

All task ordering comes from the spec. Do NOT impose your own phasing.
