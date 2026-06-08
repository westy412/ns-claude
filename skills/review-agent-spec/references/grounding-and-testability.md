# Grounding & Testability

> **When to read:** At consolidation (Step 4), the review **lead** runs these two checks directly
> against the spec — not delegated to the 3 dimension agents. They turn the spec from "internally
> consistent" into "anchored in reality and liftable into tests." Findings feed the Grounding &
> Testability section and two new verdict dimensions.

---

## Reality-Grounding (FAIL unanchored I/O)

Every data contract / I/O shape must be anchored to a **real, probed source** — an actual API spec,
DB schema, real example payload, or existing code — not an imagined shape.

- For each input/output model or integration contract: does the spec cite where the real shape came from?
- **Unanchored I/O → FAIL.** A guessed contract is the single biggest source of "reality differs from
  the spec" failures downstream.
- **Scale / volume present** where it matters → WARN if a load-bearing scale assumption is missing.
- **Known-Risks present** (non-empty, or explicit "none identified") → WARN if absent.

## Test-Derivability (FAIL un-testable Requirements)

The spec is the source of the test suite. For **each Requirement (by ID):** can a **concrete test case**
be lifted directly from it — a specific input and expected output/behavior?

- A Requirement from which no concrete test can be derived is under-specified → **FAIL** it (it will be
  verified by nobody downstream).
- A good seed names: the trigger/input, the expected output/assertion, and the edge/failure case.

## Emit the Test-Seed file

Write the liftable cases to **`reviews/review-NNN-testseed.md`** — one block per Requirement ID
(input → expected-output → edge cases). This is the artifact Stage-7 typed-testing consumes; emitting
it here is what makes "the spec is the source of tests" real, not aspirational.

## Spec-defect loopback

If either check shows the **spec itself** is wrong/under-specified (not merely reviewer uncertainty),
that's a spec defect: it loops **back into the spec** via the spec-builder, never patched downstream.
See `autonomy-and-escalation.md`.
