---
description: Live-validation stage (Layer 3) — runs a built artifact against its spec-derived test seed. Routes by artifact type (code → run/endpoints/browser; agent tools → input→assert-output; agent reasoning → evals/LLM-judge + live type-conformance). Use after a verifier static PASS or a builder clean big review hands off a spec folder.
argument-hint: "[spec-folder-path]"
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, Task, Skill
---

> **Invoke with:** `/typed-testing {spec-folder-path}` | **Keywords:** typed testing, live testing, live validation, run the tests, test the implementation, feature-correctness

Runs a completed implementation against its **spec-derived test seed** — the worked examples, edge
cases, tool example-I/O, acceptance criteria, and review test-seeds the upstream skills emitted.
Every static gate upstream (spec review, per-phase review, verifier) proves *code-correctness*;
this stage proves **feature-correctness** by executing the real artifact and comparing observed
behaviour to what the spec promised. *Code-correctness ≠ feature-correctness* — nothing upstream
can verify the latter; this is the terminal gate.

**Input:** Path to a spec folder (`{workforce-root}/specs/YYYY-MM-DD-feature-name/`)
**Output:** `{spec-folder}/feedback/testing-NNN.md` — live test report with PASS/FAIL/UNTESTED per
seed row, plus a machine-readable `testing_verdict` header

## When to Use This Skill

Use this skill when:
- An implementation verifier returned a static **PASS** and handed off (`-> typed-testing {spec-folder-path}`)
- A builder's clean **big review** handed off (the `testing-handoff.md` seam)
- `progress.md` records **live testing is owed** for a static-complete build
- You want to re-run live tests after fixing failures from a previous run

**Skip this skill when:**
- The build is not static-complete (run the builder / verifier first — this stage assumes a clean static gate)
- You only need a static review of code against the spec (use the `*-implementation-verifier` skills)
- You are reviewing the spec itself (use `review-general-spec` / `review-agent-spec`)

## Reference Files

Load these just-in-time per phase — one at a time:

| Topic | Reference File | When to Load |
|-------|---------------|--------------|
| Seed collection | [seed-collection.md](references/seed-collection.md) | Phase 1 — lifting the test seed from the spec folder |
| Code lane | [lane-code.md](references/lane-code.md) | Phase 3 — seed rows routed to the code lane |
| Agent-tools lane | [lane-agent-tools.md](references/lane-agent-tools.md) | Phase 3 — seed rows routed to the tool lane |
| Agent-reasoning lane | [lane-agent-reasoning.md](references/lane-agent-reasoning.md) | Phase 3 — seed rows routed to the reasoning lane (incl. live type-conformance) |
| Report format | [report-format.md](references/report-format.md) | Phase 4 — writing the report + routing failures |
| Autonomy & escalation | [autonomy-and-escalation.md](references/autonomy-and-escalation.md) | When a failure/gap needs the fix-or-escalate decision (shared doctrine — cite, don't restate) |

**Templates:**

| Template | Purpose |
|----------|---------|
| [testing-report.md](templates/testing-report.md) | Output report structure (`feedback/testing-NNN.md`) |

## Key Principles

1. **The spec is the source of tests.** Lift every test from the emitted seed — never invent a
   test the spec doesn't ground. A requirement with no liftable seed is a spec-quality gap, not a
   license to improvise (run the autonomy rule).
2. **Run the real artifact.** Real environment, real commands, real calls. Never simulate a pass:
   a row that cannot be run live is recorded **UNTESTED** with the reason — an honest gap beats a
   fake green.
3. **Route by artifact type.** One spec usually mixes types — route each seed row to its lane
   (code / agent-tools / agent-reasoning), don't force one method onto everything.
4. **Failures run the autonomy rule** (`references/autonomy-and-escalation.md` — the shared
   doctrine, cited not restated): artifact diverges from spec → fix-side (Branch A); the spec's
   expected output is itself wrong → spec-defect loopback (never patch the test to pass).
5. **Live type-conformance complements the static check.** The agent verifier already confirms
   declared agent types match the spec (static). This stage proves the *running* agent behaves
   per its declared type's contract (live). Two layers, not duplication.
6. **Telemetry stays in the spec folder.** The report is per-stage telemetry (three-tier feedback
   architecture, tier 1) — it travels with the spec folder across sessions for the retro to consume.

## Phases

| Phase | What happens | Reference |
|-------|--------------|-----------|
| 0 | Preconditions — static gate confirmed, seed present | (below) |
| 1 | Collect the seed → test manifest | [seed-collection.md](references/seed-collection.md) |
| 2 | Route each manifest row by artifact type | (routing tree below) |
| 3 | Execute lanes — run the artifact, record observed vs expected | lane files |
| 4 | Report, route failures, clear live-testing-owed | [report-format.md](references/report-format.md) |

### Phase 0: Preconditions

1. Resolve the spec folder from the argument / handoff. Read `spec.md` (or `spec/manifest.yaml`)
   and `progress.md`.
2. Confirm the static gate: the latest `feedback/verification-NNN.md` is a static PASS, **or**
   `progress.md` records a clean big review with live testing owed. If neither — stop and route
   back to the builder/verifier; this stage does not substitute for the static gates. The user can
   explicitly override (log as a Known-Risk in the report).
3. Locate the seed sources (Phase 1 lifts them): spec Test Sources / per-agent Examples + Edge
   Cases, tool Example I/O + Errors tables, Acceptance Criteria, `reviews/review-NNN-testseed.md`.

### Phase 2: Artifact-type routing

Route each manifest row — not the whole spec — by what the row exercises:

```
seed row exercises…
├── code — feature, app, endpoint, CLI, UI, library
│      → lane-code.md (run it: commands, endpoints, browser; AC commands verbatim)
├── an agent tool / utility — deterministic function with a defined I/O contract
│      → lane-agent-tools.md (call with input, assert output; trigger errors, assert error return)
└── agent reasoning — LLM behaviour: prompts, routing, generation, selection
       → lane-agent-reasoning.md (evals / LLM-judge vs expected output + live type-conformance)
```

Mixed artifacts are normal: an agent system's tools take the tool lane, its reasoning takes the
reasoning lane, and any service/UI shell around it takes the code lane.

### Phase 4: Completion

1. Write `feedback/testing-NNN.md` (next NNN in the `testing-*` sequence) from the template —
   fill the `testing_verdict` header.
2. **All PASS (no FAILs):** update `progress.md` — live testing **done** (report path), clearing
   the "live testing owed" record. UNTESTED rows stay listed as known gaps.
   If the user confirms this completes the run end-to-end, offer to register it with
   `dev-evolution-retro` (register mode) — prompt-only; the user declares run-complete, never you.
3. **Any FAIL:** route per [report-format.md](references/report-format.md) — fix-side or
   spec-defect loopback — then re-run the failed rows as a new `testing-NNN` run after fixes land.
4. Report the verdict and the report path to the user / calling skill.

## Sub-Agent Delegation

| Need | How |
|------|-----|
| LLM-judge for reasoning-lane rows | Spawn a fresh-context judge sub-agent via the Task tool (`subagent_type: "general-purpose"`) — judge prompt in [lane-agent-reasoning.md](references/lane-agent-reasoning.md) |
| Driving the app / confirming a change end-to-end (code lane) | Invoke the built-in `run` / `verify` skills via the Skill tool — see [lane-code.md](references/lane-code.md) |
