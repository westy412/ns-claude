# Review Output Template

Save to `{vault}/private/reviews/review-NNN.md`. Fill the machine-readable header completely — downstream tooling parses it.

---

```markdown
# Extraction Review NNN — [scope, e.g. candidate-profile + 6 sub-components]

```yaml
review_verdict:
  overall: PASS | WARN | FAIL
  grounding: PASS | WARN | FAIL
  assumption_audit: PASS | WARN | FAIL
  integrity: PASS | WARN | FAIL
  counts: { fail: N, warn: N, needs_user: N, session_confirmed: N }
  reviewed_docs: [paths]
  source_transcripts: [paths]
  run_mode: post-extraction | standalone
  date: YYYY-MM-DD
```

## 1. Grounding (grounding-tracer)

[Traceability summary table, defect table, quote verification — verbatim from the agent, deduplicated]

**Dimension verdict:** PASS | WARN | FAIL

## 2. Assumption Audit (assumption-auditor)

[Findings table, status audit, register audit — deduplicated]

**Dimension verdict:** PASS | WARN | FAIL

## 3. Integrity (integrity-checker)

[Per-check tables and summary]

**Dimension verdict:** PASS | WARN | FAIL

## 4. Consolidated Findings

One row per unique defect after root-cause dedupe:

| # | Severity | Dimension | Doc § | Finding | Disposition |
|---|----------|-----------|-------|---------|-------------|
| 1 | FAIL | grounding | [doc §] | [issue] | will fix (how) / session-confirmed (add marker) / needs you → Qn |

## 5. Questions for the User

Numbered Qn list — every `needs you` finding as a specific, answerable question.

## 6. Fixes Applied

Filled after fixes: finding # → edit made → doc. (Re-run note if a dimension was re-reviewed.)
```

---

Rules:

- Every agent finding appears in its section — consolidation dedupes, never drops
- Dedupe by root cause: discussion-not-decision → assumption; absent → grounding; wrong value → integrity
- `session_confirmed` count only in post-extraction mode; standalone runs escalate those to `needs_user`
