---
# Machine-readable verdict — downstream consumers (handover, retro) parse this header.
testing_verdict:
  overall: PASS              # PASS | FAIL (any FAIL row = FAIL; UNTESTED alone doesn't fail the run)
  rows_total: 0
  rows_pass: 0
  rows_fail: 0
  rows_untested: 0
  requirements_untested: []  # Requirement IDs with no passing or failing row
  lanes:
    code: PASS               # PASS | FAIL | N/A | UNTESTED
    agent_tools: PASS
    agent_reasoning: PASS
  type_conformance: PASS     # PASS | FAIL | N/A (non-agent specs)
  spec_path: [path]
  tested: [YYYY-MM-DD HH:MM]
---

# Live Testing Report: [spec-name]

| Field | Value |
|-------|-------|
| **Tested** | [YYYY-MM-DD HH:MM] |
| **Run #** | [NNN] (testing-NNN.md) |
| **Spec Folder** | [path] |
| **Static gate** | [feedback/verification-NNN.md verdict | clean big review per progress.md | user override (Known-Risk)] |
| **Seed sources** | [spec Test Sources | agent Examples/Edge Cases | tool Example I/O | Acceptance Criteria | reviews/review-NNN-testseed.md] |

---

## Test Manifest & Results

| Manifest ID | Source | Requirement | Lane | Input / Trigger | Expected | Observed | Verdict |
|-------------|--------|-------------|------|-----------------|----------|----------|---------|
| M1 | [WE1] | [R1] | [code] | [input] | [expected] | [observed, trimmed] | PASS/FAIL/UNTESTED |

## Acceptance-Criteria Commands

| Command (verbatim) | Exit / Result | Verdict |
|--------------------|---------------|---------|
| [`test command`] | [exit 0 / failing output trimmed] | PASS/FAIL/UNTESTED |

## Type Conformance (agent specs — delete for non-agent specs)

| Agent | Declared Type | Live contract observed | Verdict |
|-------|---------------|------------------------|---------|
| [name] | [LLM/Tool/Router/Retriever/Subgraph/HiL] | [e.g. tool calls present in trace] | PASS/FAIL |

## UNTESTED Rows

| Manifest ID | Requirement | Reason | Re-runnable when |
|-------------|-------------|--------|------------------|
| [M#] | [R#] | [no credentials / external cost / environment down / missing seed] | [what unblocks it] |

## Failures & Routing

One block per FAIL:

### [M#] — [one-line finding]

- **Expected vs observed:** [the substance gap]
- **Diagnosis:** implementation defect | spec expected-output wrong | ambiguous
- **Branch (autonomy rule):** A — routed to builder fix | A — spec corrected via spec-builder | B — escalated
- **Routed to:** [builder fix list / spec-defect note in progress.md / user question + answer]

## Outcome

- **Verdict:** [overall]
- **progress.md updated:** [live testing done — owed-record cleared | live testing failed — owed-record stays]
- **Re-run needed:** [none | failed rows M#… after fixes land → testing-NNN+1]
