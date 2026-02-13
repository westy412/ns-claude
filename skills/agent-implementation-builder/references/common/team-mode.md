# Team Mode Execution & Orchestration

> **Context:** This reference covers team mode — using Claude Code agent teams to execute implementation chunks in parallel. Read this when Step 4.5 in Phase 0 determined TEAM MODE (execution plan has parallel chunks across multiple streams).

---

## When to Use Team Mode

Use team mode when the execution plan has **parallel chunks across multiple streams** in any phase.

**Example from manifest.yaml:**
```yaml
execution-plan:
  phases:
    - phase: 1
      chunks:
        - name: data-models
          stream: models          # ← Different streams
        - name: tools
          stream: tools           # ← can work in parallel
        - name: research-signatures
          stream: signatures      # ← across Phase 1
```

If chunks share the same stream → single-agent mode (sequential).
If chunks span different streams → team mode (parallel).

*Important: IF YOU ARE USING TEAM MODE MAKE SURE TO LOAD IN THE agent-impl-teammate-spawn skill*

---

## Team Mode Workflow

### Step 1: Create Team and Task List

```
TeamCreate: team_name="[project]-impl", description="..."
```

For each chunk in execution plan, create a task:
```
TaskCreate:
  subject: "Phase N: [chunk.name] — [chunk.description summary]"
  description: "[chunk.description] + spec files + skills required + communication needs"
  activeForm: "Implementing [chunk.name]"
```

Set phase dependencies via TaskUpdate:
- Phase 1 tasks: no blockedBy
- Phase 2 tasks: blockedBy = [all Phase 1 task IDs]
- Phase 3 tasks: blockedBy = [all Phase 2 task IDs]

---

### Step 2: Map Streams to Skills (MANDATORY)

For each stream in execution plan, use this mapping:

| Stream Type | Required Skills | Load When |
|-------------|----------------|-----------|
| **models** | (none — derive from specs) | N/A |
| **tools** | tools-and-utilities | Phase 1 before writing tools |
| **signatures** | prompt-engineering, individual-agents | Phase 1 before writing signatures |
| **research** | agent-teams, individual-agents | Phase 2 before modules |
| **ideation** | agent-teams, individual-agents | Phase 2 before modules |
| **scaffold** | agent-teams | Phase 3+ before orchestration |
| **scaffold/root** | owns root pipeline, FastAPI wrapper | agent-teams |

**How to detect stream type:** Read `stream.owns` file list. Match file patterns to table above.

**Example:**
```yaml
streams:
  - name: research
    owns: [src/research/]  # ← Owns team modules
```
→ Stream type: team/orchestration → Skills: agent-teams

If execution plan lists `stream.skills`, use those. Otherwise, use this default table.

**CRITICAL:** Skills are NOT optional. Every stream that writes agent code MUST load the corresponding skills.
**IMPORTANT:** Do NOT spawn teammates without determining their required skills.

---

### Step 3: Generate Teammate Prompt Files

For each stream with work, use the `agent-impl-teammate-spawn` skill to generate a structured prompt file:

```
Skill tool -> skill: "agent-impl-teammate-spawn"
```

This skill reads your manifest.yaml and agent-config.yaml to generate a prompt file for each stream at:
```
{project-path}/teammate-prompts/{team-name}/{stream-name}.md
```

Each generated file includes the exact skills to load, how to load them, tasks to work on, validation checklists, and communication requirements. Follow the skill's step-by-step instructions to generate one file per stream.

---

### Step 4: Spawn Teammates with Minimal Prompts

After generating all prompt files, spawn each teammate with a minimal prompt pointing to their file:

```
Task tool:
  team_name: [project-name]
  name: [stream-name]
  subagent_type: general-purpose
  model: opus (for complex streams like research/ideation)
  prompt: |
    You are teammate [stream-name] on team [project-name].

    Read your full instructions at:
      [project-path]/teammate-prompts/[team-name]/[stream-name].md

    Follow ALL steps in order. DO NOT skip Step 1 (Load Required Skills).
    After loading skills, confirm to team-lead via SendMessage.
```

---

### Step 5: Verify Skill Loading (MANDATORY — DO NOT SKIP)

This is the enforcement mechanism. Without this step, teammates will skip skill loading and produce broken code. This has been proven: in NS-1158, 4/5 teammates skipped skills and produced incorrect implementations.

After spawning all teammates:

1. Wait for the first message from each teammate
2. The message MUST confirm skill loading with the specific skill names (e.g., "Skills loaded: agent-teams, individual-agents")
3. If the first message is about anything other than skill loading — the teammate skipped Step 1. Send them back:
   > "STOP. You must load your required skills before doing any work. Go back to Step 1 in your prompt file. Use the Skill tool to load each skill listed there. Confirm to me when done."
4. Do NOT assign tasks, do NOT allow work to begin, do NOT respond to implementation questions until skills are confirmed
5. If a teammate claims a task without confirming skills — revoke it immediately and enforce loading

**Enforcement rule:** If a teammate completes a file without confirming skill loading,
assume it's wrong and request skill-guided review before accepting the work.

---

### Step 6: Monitor Phase Execution

- Teammates check TaskList for available (unblocked) tasks in their stream
- All chunks in a phase execute in parallel across teammates
- When a teammate completes a chunk, it marks the task complete and checks for next work
- Phase barriers are enforced via `blockedBy` — Phase 2 tasks unblock when all Phase 1 tasks complete
- The lead monitors progress via TaskList and handles any issues

---

### Step 7: Handle Inter-Agent Communication

The `communication` section of the execution plan defines what needs to be shared:

- After a phase completes, teammates send relevant information to downstream streams via `SendMessage`
- Example: tools stream sends function signatures to scaffold stream after Phase 1
- The lead can relay information between teammates if direct messaging isn't sufficient

---

### Step 8: Finalization

After all phases complete:
1. Lead validates all files exist and are internally consistent
2. Run tests if defined in acceptance criteria
3. Shutdown teammates via `SendMessage(shutdown_request)`
4. Clean up team via `TeamDelete`
5. Clean up teammate prompt files:
   ```bash
   rm -rf {project-path}/teammate-prompts/{team-name}/
   rmdir {project-path}/teammate-prompts/ 2>/dev/null
   ```

---

## Stream Communication Protocol

Teammates must communicate when:
1. Completing a chunk that produces data needed by other streams
2. Encountering a missing input that should come from another stream
3. Discovering a spec/implementation mismatch affecting multiple streams

**When to send:**
Check `execution-plan.communication` in manifest.yaml:

```yaml
communication:
  - from: tools
    to: [research, ideation]
    after: phase-1
    what: Tool function signatures
```

After completing the trigger event (phase-1 for tools stream), send via:
```
SendMessage:
  type: message
  recipient: [target-stream-name]
  content: [what to send]
  summary: "Phase 1 tools complete: function signatures available"
```

**What to send:** Function signatures, interface contracts, model schemas, breaking changes.

**Team Lead Responsibilities:**
- Monitor SendMessage traffic
- Verify communication plan is followed
- Relay messages if direct teammate-to-teammate fails

---

## Team Lead Progress Management

As team lead, you MUST:

**1. Create progress.md BEFORE spawning teammates**
- Use template from templates/progress.md
- Populate Execution Plan Snapshot with all chunks
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
- When a chunk completes, check execution-plan.communication
- If communication required, verify SendMessage was sent
- If not sent, prompt the teammate

**5. Validate before proceeding to next phase**
- All Phase N tasks must be "completed" before Phase N+1 starts
- Check that all communication happened
- Spot-check 1-2 files for import validity

---

## Task Dependencies in Team Mode

**When an execution plan exists in manifest.yaml**, the execution plan is the SOLE source of truth for phasing. The plan defines:
- **Phases** — ordered stages that execute sequentially (Phase 2 waits for Phase 1 to complete)
- **Chunks** — units of work within a phase that can run in parallel across agent team teammates
- **Streams** — work streams that own specific files; each teammate maps to a stream

All default file-type phasing (Scaffold → Tools → Agents → Prompts → Utils) is IGNORED when an execution plan exists. Do NOT reference these defaults in progress tracking, task creation, or teammate spawn prompts. Use the execution plan's phase names and chunk names instead.
