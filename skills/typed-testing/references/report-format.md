# Report Format & Failure Routing (Phase 4)

> **Context:** The run is recorded in `{spec-folder}/feedback/testing-NNN.md` (its own `testing-*`
> sequence, next NNN; sibling to the verifier's `verification-NNN.md`). The report is per-stage
> telemetry — it stays in the spec folder so it travels across sessions and the run retro can
> consume it. Use `templates/testing-report.md`.

---

## The `testing_verdict` header

Machine-readable, at the top of the report (the typed-testing twin of the review's
`review_verdict` — downstream consumers parse it, humans skim it):

```yaml
---
testing_verdict:
  overall: PASS              # PASS | FAIL (any FAIL row = FAIL; UNTESTED rows alone don't fail the run)
  rows_total: 0
  rows_pass: 0
  rows_fail: 0
  rows_untested: 0
  requirements_untested: []  # Requirement IDs with NO passing or failing row (coverage gaps)
  lanes:
    code: PASS               # PASS | FAIL | N/A | UNTESTED
    agent_tools: PASS
    agent_reasoning: PASS
  type_conformance: PASS     # PASS | FAIL | N/A (non-agent specs)
  spec_path: [path]
  tested: [YYYY-MM-DD HH:MM]
---
```

## Report body

Per the template: the test manifest with verdicts (every row: source seed ID, Requirement, lane,
input, expected, observed, verdict), the per-agent type-conformance table (agent specs), the
UNTESTED rows with reasons, and the failure findings with routing.

UNTESTED is honest signal, not noise: every UNTESTED row carries the reason (no credentials /
external cost / environment down / missing seed) so the gap is visible, owned, and re-runnable.

## Failure routing — the autonomy rule applied to live failures

Every FAIL runs the fix-or-escalate decision (`autonomy-and-escalation.md` doctrine — cite it,
don't restate it). The live-testing question: **which side is wrong, the artifact or the seed?**

| Diagnosis | Branch | Route |
|-----------|--------|-------|
| Artifact diverges from what the spec/seed establishes | **A** (auto-fix) | Implementation defect → route to the implementation-builder (re-enter with the finding; trivial fixes may be applied directly), then **re-run the failed rows** as a new `testing-NNN` run |
| The seed's expected output is itself wrong (the spec mis-modelled reality — the live run proves it) | **A** (resolvable from intent) / **B** | If discovery/spec intent settles what it *should* be: correct **the spec** and re-derive the row — **never patch the test or the expectation in place to make it pass**. Spec-defect loopback: the correction lands in the spec via the spec-builder, then the row re-runs |
| Genuinely ambiguous which side is wrong | **B** (escalate) | One concise question to the user (comms standard in the doctrine); on "proceed", log a Known-Risk |

Findings are recorded in the report **and** the routing destination (builder fix list /
spec-defect note in `progress.md`) — a finding that lives only in the report dies in the report.

## Closing the loop

- **Overall PASS:** update `progress.md` — live testing **done**, report path, date — clearing
  the "live testing owed" record the builder/verifier left. List any UNTESTED rows there as open
  known gaps.
- **Overall FAIL:** `progress.md` records live testing **failed** (report path + the routed
  findings). The owed-record stays until a re-run passes.
- Re-runs after fixes: new report (next NNN), re-running at minimum the failed rows + any rows
  touching changed files. Prior reports are never edited — the sequence is the history.
