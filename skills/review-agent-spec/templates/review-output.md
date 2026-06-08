---
# Machine-readable verdict — the implementation-builder reads this header and refuses to start on FAIL.
review_verdict:
  overall: PASS              # PASS | WARN | FAIL (= worst dimension)
  blocking_count: 0
  warning_count: 0
  dimensions:
    structural: PASS         # PASS | WARN | FAIL
    source_tracing: PASS
    ambiguity: PASS
    reality_grounding: PASS
    test_derivability: PASS
  spec_path: [path]
  reviewed: [YYYY-MM-DD HH:MM]
---

# Agent Spec Review: [system-name]

| Field | Value |
|-------|-------|
| **Reviewed** | [YYYY-MM-DD HH:MM] |
| **Review #** | [NNN] |
| **Spec Type** | Agent |
| **System Type** | [single-agent / agent-team / nested-teams] |
| **Spec Path** | [path] |
| **Discovery Path** | [path] |
| **Other Sources** | [brainstorm path, research path, or "None"] |

---

## 1. Structural Checks

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Required root files | PASS/WARN/FAIL | |
| 2 | Manifest structure | PASS/WARN/FAIL | |
| 3 | Team folder completeness | PASS/WARN/FAIL | |
| 4 | Manifest-to-files sync | PASS/WARN/FAIL | |
| 5 | I/O consistency | PASS/WARN/FAIL | |
| 6 | Data flow map | PASS/WARN/FAIL | |
| 7 | Stream ownership | PASS/WARN/FAIL | |
| 8 | Chunk spec-file mapping | PASS/WARN/FAIL | |
| 9 | Stream skills assignment | PASS/WARN/FAIL | |
| 10 | Phase dependencies | PASS/WARN/FAIL | |
| 11 | Agent spec completeness | PASS/WARN/FAIL | |
| 12 | Model tier appropriateness | PASS/WARN/FAIL | |
| 13 | Anti-patterns | PASS/WARN/FAIL | |
| 14 | DSPy path validation | PASS/WARN/FAIL/N/A | |
| 15 | Instance parity | PASS/WARN/FAIL/N/A | |

**Structural Verdict:** PASS/WARN/FAIL
**Blocking:** [n] | **Warnings:** [n]

---

## 2. Source Material Tracing

### Coverage Summary

| Source | Total Items | Covered | Partial | Missing | Coverage % |
|--------|------------|---------|---------|---------|------------|
| Discovery | | | | | |
| Brainstorm | | | | | |
| Research | | | | | |
| **Total** | | | | | |

### Traceability Matrix

| # | Source | Item Summary | Found? | Spec File(s) | Fidelity |
|---|--------|-------------|--------|-------------|----------|
| | | | | | |

### Requirement-to-Agent Mapping

| Requirement | Responsible Agent(s) | Captured? | Notes |
|-------------|---------------------|-----------|-------|
| | | | |

### Coverage Gaps

| # | Importance | Source Item | Source Location | Why It Matters | Suggested Addition |
|---|-----------|-------------|-----------------|----------------|-------------------|
| | | | | | |

### Misinterpretations

| # | Source Item | Source Says | Spec Says | Impact | Suggested Fix |
|---|------------|-------------|-----------|--------|---------------|
| | | | | | |

**Source Tracing Verdict:** PASS/WARN/FAIL
**Blocking:** [n] | **Warnings:** [n]

---

## 3. Ambiguity Analysis

### Ambiguity Summary

| Severity | Count |
|----------|-------|
| HIGH | [n] |
| MEDIUM | [n] |
| LOW | [n] |

### Findings

| # | Spec File | Requirement | Category | Severity | Ambiguity | Clarification Question |
|---|----------|------------|----------|----------|-----------|----------------------|
| | | | | | | |

**Ambiguity Verdict:** PASS/WARN/FAIL
**Blocking:** [n] | **Warnings:** [n]

---

## Grounding & Testability

> Lead-run at consolidation (see `references/grounding-and-testability.md`). Reality-grounding (FAIL
> unanchored I/O) + scale/known-risk; test-derivability (FAIL un-testable Requirements). Liftable test
> cases are emitted separately to `review-NNN-testseed.md`.

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Data contracts cite a real probed source (no unanchored I/O) | PASS/WARN/FAIL | |
| 2 | Scale / volume assumptions present where load-bearing | PASS/WARN/FAIL | |
| 3 | Known-Risks section present | PASS/WARN/FAIL | |
| 4 | Every Requirement yields a concrete test case | PASS/WARN/FAIL | |

**Reality-Grounding Verdict:** PASS/WARN/FAIL  ·  **Test-Derivability Verdict:** PASS/WARN/FAIL
**Blocking:** [n] | **Warnings:** [n]

---

## 4. Overall Summary

| Dimension | Verdict | Blocking | Warnings |
|-----------|---------|----------|----------|
| Structural Checks | PASS/WARN/FAIL | [n] | [n] |
| Source Tracing | PASS/WARN/FAIL | [n] | [n] |
| Ambiguity Analysis | PASS/WARN/FAIL | [n] | [n] |
| Reality Grounding | PASS/WARN/FAIL | [n] | [n] |
| Test Derivability | PASS/WARN/FAIL | [n] | [n] |
| **Overall** | **PASS/WARN/FAIL** | **[total]** | **[total]** |

### Blocking Issues (must fix before implementation)

1. [issue description + fix suggestion]

### Warnings (recommended fixes)

1. [issue description + fix suggestion]
