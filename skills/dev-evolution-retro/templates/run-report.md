# Machine-readable header — downstream consumers (next sweep's pattern gate, handover) parse this.
retro_verdict:
  run: [registry row name]
  spec_path: [path]
  analysed: [YYYY-MM-DD]
  findings_total: 0
  by_class:                  # counts per failure-class
    front-load-failure: 0
    code-bug: 0
    spec-bug: 0
    gate-miss: 0
    escalation-misfire: 0
    capture-failure: 0
  skills_implicated: []      # attributed skills, deduped
  proposals_contributed: 0   # findings that entered a fired proposal this sweep
  flags_contributed: 0
  dimensions_no_signal: []   # dimensions with nothing to read (recorded, not skipped)
---

# Run Retro Report: [run name]

| Field | Value |
|-------|-------|
| **Analysed** | [YYYY-MM-DD] |
| **Report #** | [NNN] (retro-NNN.md) |
| **Spec folder** | [path] |
| **Telemetry present** | [from the Phase-1 manifest: drift-log (N rows), review-001..NNN, verification-NNN, testing-NNN, …] |
| **Telemetry missing** | [e.g. no spec-stage escalation records (#48); none] |
| **Mode** | [team (4 dimensions) | solo] |

---

## Run shape

[3-6 lines: what this run built, how many sessions/skills it crossed, headline numbers — review
rounds to PASS, drift rows, escalations, testing verdict. The reader should grasp the run
without opening the spec folder.]

## Findings

[All consolidated findings, the root-causing format verbatim — grouped by failure-class:]

- finding: [one sentence, citing the telemetry row/file]
  run: [this run]
  evidence: [file:line / Drift Log row / verdict header field]
  failure-class: [class]
  skill: [earliest skill that should have caught it]
  also-implicated: [downstream skills]
  prevention: [the specific skill change that would have prevented this]
  severity: [low | medium | high]

## The system working

[Correct escalations, clean spec-defect loopbacks, per-phase catches — baseline calibration,
never proposals (root-causing Rule 4). Brief bullets.]

## Cross-run notes

[Analyzer observations naming this run alongside others in the sweep — feeds the pattern gate;
the gate's outcome lives in the registry's Proposals section, not here.]
