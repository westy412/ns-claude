# Telemetry Collection

> **When to read:** Phase 1 — building the per-run telemetry manifest before spawning analyzers.

Every upstream stage writes file-based telemetry into the spec folder (tier 1 of the feedback
architecture) precisely so this skill can read it later, across sessions. Phase 1 inventories
what each swept run actually has — the manifest tells the dimension analyzers where to look and
records what's *missing* (a telemetry gap is itself a finding).

---

## What to read, per spec folder

| Source | File(s) | What it carries |
|--------|---------|-----------------|
| Drift Log / Spec-Feedback Ledger | `progress.md` → "Drift Log / Spec-Feedback Ledger" table | One row per spec-vs-reality drift: Phase · Finding · Class (`code-bug`/`spec-bug`) · Resolution · Spec amended? · Escalated? (Branch A/B) · Front-load failure? |
| Builder escalation records | `progress.md` (Drift Log `Escalated? yes` rows + Phase-0 gate rows) | Where the human was interrupted mid-build; Phase-0 rows = builds started on specs that weren't ready |
| Review verdicts | `reviews/review-NNN.md` → `review_verdict` header (all NNN) | PASS/WARN/FAIL per review round; FAIL count = how many rounds the spec needed; ambiguity findings |
| Review test-seed | `reviews/review-NNN-testseed.md` | What the review derived as testable — gaps here are spec-emitter failures |
| Verifier reports | `feedback/verification-NNN.md` → Spec Traceability Matrix | Per-requirement CORRECT / INCORRECT (impl-bug) / MISSING / AMBIGUOUS (spec-quality) + Routing column |
| Live testing | `feedback/testing-NNN.md` → `testing_verdict` header + manifest rows | PASS/FAIL/UNTESTED per seed row; FAILs that static gates missed; UNTESTED = seed/environment gaps |
| Mid-build spec amendments | Drift Log `Spec amended? yes` rows + spec git history if available | Every one is a front-load failure by definition |
| Decisions split | `progress.md` Decisions Made (Branch A vs Branch B), handover captures if present | Autonomous fixes vs escalations — the autonomy-dial signal |
| Spec-stage escalation records | *(when present)* | Discovery/spec-builder/review-stage escalations. **Known gap:** the spec-stage skills carry the escalation doctrine but do not yet write structured records (backlog #48). Read conversation-adjacent artefacts (spec folder notes, session captures) when they exist; otherwise record "spec-stage telemetry absent" in the manifest — absence is a finding, not a blocker. |

---

## The manifest

Per swept run, produce a short manifest (in your working notes or the team brief — it does not
need its own file):

```
Run: {registry row}
Spec folder: {path}
Present: [drift-log (N rows), review-001..003, verification-001, testing-001, ...]
Missing: [e.g. no testing-NNN (live testing never ran), no spec-stage escalation records (#48)]
Notable: [e.g. 2 front-load-failure rows, review FAILed twice, 1 Branch-B escalation]
```

Rules:

- **Read headers first, bodies on demand.** `review_verdict` / `testing_verdict` headers and the
  Drift Log table are designed to be parsed cheaply; analyzers load full bodies only for rows
  they're attributing.
- **Missing telemetry is a finding.** A run with no Drift Log rows and three mid-build spec
  commits didn't have a clean build — it has a capture failure. Attribute it to the skill that
  should have written the record.
- **Never reconstruct telemetry from memory or guesswork.** If it isn't in a file, it's absent.
