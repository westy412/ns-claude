# Single-Agent Mode

> **Context:** This reference covers single-agent execution — working through phases and chunks sequentially without spawning teammates. Read this when Phase 0's execution mode decision determined SINGLE-AGENT MODE (single stream, sequential chunks, or simple specs).

---

## When to Use Single-Agent Mode

Single-agent mode applies when:
- The execution plan has only **one stream** across all phases
- All chunks are **sequential** (no parallel work possible)
- The execution plan is **missing** entirely (treat spec as one big chunk)
- The spec is simple enough that team coordination overhead isn't warranted

---

## Workflow

### Step 1: Load Skills

From the spec's Skills section and chunk-level skill listings, load skills just-in-time:

- At Phase 0: Load top-level skills from the Skills section
- At each subsequent phase: Load chunk-level skills before starting that chunk
- **Context budget:** Only load ONE skill at a time. If a new skill is needed, persist progress to progress.md first

### Step 2: Work Through Phases Sequentially

For each phase in the execution plan:

1. Read the phase's chunks
2. For each chunk (in order):
   a. Load any chunk-specific skills not already loaded
   b. Read relevant reference files and spec details
   c. Execute the sub-tasks
   d. Verify the chunk's outcome is met
   e. Update progress.md — mark chunk as `done`
3. After all chunks in the phase complete, move to the next phase

### Step 3: Handle Dependencies

Since everything is sequential, dependencies are naturally satisfied:
- Phase 2 chunks only start after all Phase 1 chunks complete
- Within a phase, process chunks in the order listed

If a chunk has a specific `Depends On` referencing another chunk, verify that chunk is done before proceeding.

---

## Progress Tracking

Update progress.md after each chunk:

1. Mark the completed chunk as `done` in the Execution Plan Snapshot
2. Update "Current Phase" and "Next Chunk"
3. Add notes about any decisions made or issues encountered

This ensures cross-session resumption works — a new session reads progress.md and picks up where the last one left off.

---

## Sub-Agent Delegation

Even in single-agent mode, use sub-agents to keep your context clean:

| Situation | Sub-Agent | Why |
|-----------|-----------|-----|
| Understanding existing codebase patterns | `codebase-researcher` | Returns summary, doesn't pollute context |
| Reading API/SDK documentation | `web-researcher` | Large docs stay out of your context |
| Exploring unfamiliar code areas | `codebase-researcher` | Focused research, clean results |

See `references/sub-agents.md` for invocation patterns.

**When NOT to use sub-agents:**
- Simple file reads you need in context anyway
- Small, focused lookups (grep for a function name)
- When you already have the information from a previous step

---

## When to Consider Switching to Team Mode

If during execution you discover:
- A phase has chunks that could genuinely run in parallel
- The work is taking too long sequentially
- Multiple distinct areas of the codebase need simultaneous changes

Ask the user: "This spec has potential for parallel execution. Should I switch to team mode for the remaining phases?"
