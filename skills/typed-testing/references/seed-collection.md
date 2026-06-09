# Seed Collection (Phase 1)

> **Context:** The upstream skills already emitted the test seed — the spec-builders (Test
> Sources / Examples + Edge Cases), tools-and-utilities (Example I/O + Errors), and the spec
> review (testseed file). This phase lifts that seed into one **test manifest**. Lift, don't
> re-derive — and never invent a test the spec doesn't ground.

---

## The five seed sources

Collect from the spec folder, in this order:

| # | Source | Where | Shape |
|---|--------|-------|-------|
| 1 | **Spec Test Sources** (general track) | `spec.md` → `## Test Sources` | `WE#` rows (Requirement, Input/Trigger, Expected Output) + `EC#` rows (Requirement, Condition, Expected Handling) |
| 2 | **Per-agent Examples + Edge Cases** (agent track) | each agent file → `## Examples` (input → expected output blocks) + `### Edge Cases` table (Case, How to Handle) | worked examples + failure-mode rows per agent |
| 3 | **Tool Example I/O + error cases** | each tool definition → `Example I/O` table (`T#` rows: Input, Expected Output) + `Errors` table (Error, Trigger, Expected Return) | the tool test suite |
| 4 | **Acceptance Criteria** | `spec.md` → `## Acceptance Criteria` | verifiable criteria, incl. literal test/lint commands |
| 5 | **Review test-seeds** | `reviews/review-NNN-testseed.md` (latest) | one block per Requirement ID (input → expected output → edge cases) |

## Dedup rule

The review testseed (source 5) was derived *from* the spec — it overlaps sources 1–3 by design.
Where a Requirement is covered by both, **the spec's own tables are canonical** (they survived
review and any later spec patches); use the review testseed to fill Requirements the spec tables
miss. Never run the same assertion twice under two IDs.

## Build the test manifest

One row per liftable test:

| Manifest ID | Source | Requirement | Lane | Input / Trigger | Expected |
|-------------|--------|-------------|------|-----------------|----------|
| M1 | WE1 / EC3 / T2 / AC4 / RS-R2 | R1 | code / agent-tools / agent-reasoning | concrete input | exact expected output / handling |

- **Manifest ID** is the run-local handle the lanes and report use.
- **Source** traces back to the seed row (so a failing test points at its spec line).
- **Lane** is assigned in Phase 2 (routing) — leave blank here if unclear, route next.
- Inputs/expecteds are copied **verbatim** from the seed — concrete, runnable values. If a seed
  row is too vague to run (placeholder text survived the upstream gates), treat it as a missing
  seed (below), not as something to flesh out yourself.

## Coverage check

Every spec Requirement must map to **≥ 1 manifest row** (the upstream review asserted
derivability; this confirms it survived the build). For any Requirement with no liftable seed:

- That is a **spec-quality gap** — run the autonomy rule (`autonomy-and-escalation.md` doctrine):
  resolvable from stated intent (discovery doc / spec / conversation) → derive the test from that
  material and **write the seed back into the spec** (never test-only); a genuine gap → escalate
  one concise question, or log a Known-Risk and record the Requirement as UNTESTED.
- **Do not invent tests the spec doesn't ground** — an invented expectation tests your guess,
  not the contract.

## Output of this phase

The completed manifest (kept in working context; it is reproduced in the report). Proceed to
Phase 2 routing with every row carrying a lane.
