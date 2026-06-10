---
description: Self-evolution retro (Layer 4) — registers completed runs and sweeps un-analysed ones, reading per-stage telemetry (Drift Logs, review_verdicts, verifier matrices, testing_verdicts, escalation records) across every skill and session of each run. Emits one consolidated run report per run plus pattern-gated skill-change proposals for skill-updater. Use when the user declares a run complete (register) or wants to run the process retro (sweep).
argument-hint: "[register <spec-folder-path> | retro]"
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, Task, Skill
---

> **Invoke with:** `/dev-evolution-retro register {spec-folder-path}` or `/dev-evolution-retro retro` | **Keywords:** run retro, process retro, register run, run complete, skill evolution, friction analysis

The feedback architecture's third tier consumer. Every upstream stage writes per-stage telemetry
into the spec folder (tier 1); this skill consolidates it per run (tier 2) and aggregates across
runs (tier 3) — root-causing every friction point toward **"what skill change would have
prevented this?"** and emitting pattern-gated proposals that `skill-updater` applies behind its
propose-gate. The loop's unit is the **run** (discovery → spec → review → build → verify →
typed-testing), not the session — a run spans sessions, so all state is file-based.

**Input:** `register` — a spec-folder path the user declares complete; `retro` — nothing (the
registry is the queue)
**Output:** `register` — a new registry row; `retro` — one `{spec-folder}/feedback/retro-NNN.md`
per swept run + proposals recorded in the registry + surfaced to the user

## When to Use This Skill

Use this skill when:
- The user declares a run complete end-to-end (`register` mode)
- `handover` or `typed-testing` surfaces "retro owed" and the user confirms registration
- The user wants the process retro run (`retro` mode) — sweeps ALL un-analysed registry rows
- The user asks where recurring process friction is coming from

**Skip this skill when:**
- The run is not complete — telemetry is still accumulating (the registry row would be premature;
  **never declare a run complete yourself** — only the user does)
- You want to review or test an artifact (use the verifier / `typed-testing` skills)
- You want to apply a skill change (use `skill-updater` — this skill only proposes)

## Modes

```
/dev-evolution-retro …
├── register {spec-folder-path} → confirm with the user, append a registry row
│        (references/registry.md — never auto-declare; prompt-only when routed here by
│         handover/typed-testing)
└── retro → sweep every registry row without retro-done
         (phases below — team mode by default, solo fallback)
```

## Reference Files

Load these just-in-time per phase — one at a time:

| Topic | Reference File | When to Load |
|-------|---------------|--------------|
| Registry contract | [registry.md](references/registry.md) | `register` mode, and `retro` Phase 0 (locating the queue) |
| Telemetry collection | [telemetry-collection.md](references/telemetry-collection.md) | Phase 1 — what to read in each spec folder |
| Team mode (dimensions) | [team-mode.md](references/team-mode.md) | Phase 2 — spawning the dimension analyzers |
| Root-causing | [root-causing.md](references/root-causing.md) | Phase 2/3 — the attribution doctrine every analyzer applies |
| Pattern gate | [pattern-gate.md](references/pattern-gate.md) | Phase 4 — cross-run aggregation + proposal rules |
| Autonomy & escalation | [autonomy-and-escalation.md](references/autonomy-and-escalation.md) | When a retro finding itself needs a fix-or-escalate call (shared doctrine — cite, don't restate) |

**Templates:**

| Template | Purpose |
|----------|---------|
| [run-report.md](templates/run-report.md) | Per-run consolidated report (`feedback/retro-NNN.md`) with machine-readable `retro_verdict` header |
| [registry.md](templates/registry.md) | Initial registry file (created once at the user's chosen high-level path) |

## Key Principles

1. **Only the user declares a run complete.** `handover` / `typed-testing` may prompt
   "register this run?" — they never auto-declare, and neither do you.
2. **Failures attribute to skills, never to the user.** "The user didn't provide enough
   information" is a discovery/spec-builder probing failure. Blame flows to the **earliest skill
   that should have caught it** (see [root-causing.md](references/root-causing.md)).
3. **No copied state.** Telemetry and run reports stay in the spec folder; the registry is
   pointers + status flags only. Cross-run aggregation works by reading prior run reports
   *through* the registry.
4. **Pattern-gated, not per-blip.** A skill-change proposal fires only when the same skill fails
   the same failure-class across **N=2 runs**. One run is noise. A single severe finding may be
   *flagged* — flags are not proposals.
5. **Propose, never apply.** Proposals are structured `skill-updater` feedback rows; the human
   approves and `skill-updater` applies behind its propose-gate. This skill never edits another
   skill.
6. **Spec folders must survive until retro'd.** Never prune a spec folder referenced by a
   registry row without `retro-done` — its telemetry is the only copy.
7. **The retro runs in its own session.** It reads across every skill and session of a run;
   don't bolt it onto the end of a depleted build/test session.

## Retro Phases

| Phase | What happens | Reference |
|-------|--------------|-----------|
| 0 | Locate the registry, list rows without `retro-done` — the sweep set | [registry.md](references/registry.md) |
| 1 | Per swept run, build the telemetry manifest (what exists, what's missing) | [telemetry-collection.md](references/telemetry-collection.md) |
| 2 | Fan out dimension analyzers across ALL swept runs (team mode) | [team-mode.md](references/team-mode.md) |
| 3 | Consolidate — one `feedback/retro-NNN.md` per run from the dimension findings | [run-report.md](templates/run-report.md) |
| 4 | Cross-run pattern gate → proposals; update registry rows to `retro-done` | [pattern-gate.md](references/pattern-gate.md) |

### Phase 0: Preconditions

1. Ask the user for the registry path if not already known from the conversation; it lives in a
   high-level folder of their choosing (see [registry.md](references/registry.md)). If no
   registry exists yet, there is nothing to sweep — offer `register` mode instead.
2. The sweep set = every row whose status is not `retro-done`. Confirm the set with the user
   before spawning analyzers (cheap to confirm, expensive to re-run).
3. Verify each swept spec folder still exists. A missing folder is a **lost-telemetry incident**:
   record it in the registry row, report it, and continue with the rest.

### Phase 4: Completion

1. Write each run's `feedback/retro-NNN.md` (next NNN in the `retro-*` sequence) — fill the
   `retro_verdict` header.
2. Run the pattern gate across this sweep + all prior run reports reachable through the registry
   ([pattern-gate.md](references/pattern-gate.md)). Record proposals and flags in the registry's
   `## Proposals` section.
3. Flip each swept registry row to `retro-done` with its report path.
4. Surface to the user: per-run report paths, proposals fired (with evidence runs), flags raised.
   For each approved proposal, hand off to `skill-updater` (Skill tool) with the structured
   feedback row.

## Sub-Agent Delegation

| Need | How |
|------|-----|
| Dimension analyzers (Phase 2) | Generate file-based briefs via the `teammate-spawn` skill (research profile), then spawn via the Task tool — wiring in [team-mode.md](references/team-mode.md) |
| Applying an approved proposal | Invoke `skill-updater` via the Skill tool — never edit a skill directly |
