# Verification Report: [spec-name]

**Spec Folder:** [path to spec folder]
**Spec:** [spec.md | spec/manifest.yaml]
**Progress:** [progress.md]
**Run:** [NNN] (verification-NNN.md)
**Verified:** [date]
**Verdict:** PASS | WARNINGS ONLY | NEEDS FIXES

---

## Summary

| # | Dimension | Status | Blocking | Warnings | Details |
|---|-----------|--------|----------|----------|---------|
| 1 | Spec Compliance | | 0 | 0 | [link to section] |
| 2 | Completeness | | 0 | 0 | [link to section] |
| 3 | Code Quality | | 0 | 0 | [link to section] |

**Total blocking issues:** [count]
**Total warnings:** [count]

---

## 1. Spec Compliance

### Requirements

| # | Requirement | Status | Evidence |
|---|------------|--------|----------|
| | [requirement text] | PASS/WARN/FAIL | [file:line or explanation] |

### Acceptance Criteria

| # | Criterion | Status | Evidence |
|---|----------|--------|----------|
| | [criterion text] | PASS/WARN/FAIL | [file:line or explanation] |

### Architecture Compliance

| # | Decision/Constraint | Status | Evidence |
|---|-------------------|--------|----------|
| | [architectural decision from spec] | PASS/WARN/FAIL | [evidence] |

### Deviations from Spec

| # | Deviation | Documented? | Assessment |
|---|----------|-------------|------------|
| | [what differs from spec] | Yes/No | [reasonable / problematic] |

---

## 2. Completeness

### Execution Plan Coverage

| Phase | Chunk | Stream | Expected Status | Actual Status | Notes |
|-------|-------|--------|----------------|---------------|-------|
| | | | done | | |

### File Existence

| # | Expected File | Exists? | Non-Empty? | Status |
|---|--------------|---------|------------|--------|
| | [file path] | Yes/No | Yes/No/Stub | PASS/FAIL |

### Stubs and Placeholders

| # | Location | Type | Status |
|---|----------|------|--------|
| | [file:line] | TODO / empty function / NotImplemented | FAIL |

---

## 3. Code Quality

### 3a. Correctness

| # | Finding | Severity | Location | Issue | Fix |
|---|---------|----------|----------|-------|-----|
| | | Critical/High/Medium/Low | [file:line] | | |

### 3b. Security

| # | Finding | Severity | Location | Issue | Fix |
|---|---------|----------|----------|-------|-----|
| | | Critical/High/Medium/Low | [file:line] | | |

### 3c. Performance

| # | Finding | Severity | Location | Issue | Fix |
|---|---------|----------|----------|-------|-----|
| | | Critical/High/Medium/Low | [file:line] | | |

### 3d. Maintainability

| # | Finding | Severity | Location | Issue | Fix |
|---|---------|----------|----------|-------|-----|
| | | Critical/High/Medium/Low | [file:line] | | |

### 3e. Error Handling

| # | Finding | Severity | Location | Issue | Fix |
|---|---------|----------|----------|-------|-----|
| | | Critical/High/Medium/Low | [file:line] | | |

### 3f. Type Safety

| # | Finding | Severity | Location | Issue | Fix |
|---|---------|----------|----------|-------|-----|
| | | Critical/High/Medium/Low | [file:line] | | |

---

## Spec Traceability Matrix

> Maps every spec requirement to an implementation outcome. This section feeds the feedback flywheel -- review skills read it to detect recurring spec quality patterns.

### Requirements

| # | Spec Requirement | Outcome | Impl Location | Notes |
|---|-----------------|---------|---------------|-------|
| | [requirement text from spec] | CORRECT / INCORRECT / AMBIGUOUS / MISSING | [file:line or N/A] | [explanation] |

### Acceptance Criteria

| # | Criterion | Outcome | Impl Location | Notes |
|---|----------|---------|---------------|-------|
| | [criterion text from spec] | CORRECT / INCORRECT / AMBIGUOUS / MISSING | [file:line or N/A] | [explanation] |

### Ambiguity Detail

> Only populated for requirements/criteria with outcome = AMBIGUOUS. Each entry helps the spec builder avoid the same mistake next time.

| # | Requirement | Ambiguity Category | What Was Ambiguous | What the Agent Assumed | What Was Actually Needed |
|---|------------|-------------------|-------------------|----------------------|------------------------|
| | [requirement] | Vague requirement / Missing edge case / Implicit assumption / Conflicting requirements / Unspecified interface / Missing acceptance criterion | [the unclear part of the spec] | [what the implementation agent interpreted] | [what the correct interpretation should have been] |

### Outcome Summary

| Outcome | Count | % |
|---------|-------|---|
| CORRECT | | |
| INCORRECT | | |
| AMBIGUOUS | | |
| MISSING | | |
| **Total** | | 100% |

---

## Fix Priority

> Consolidated list of all FAIL findings, ordered by priority. Feed this section to the implementation builder.

| Priority | Dimension | Finding | Location | Fix Required |
|----------|-----------|---------|----------|-------------|
| 1 | | | [file:line] | |
| 2 | | | [file:line] | |
| 3 | | | [file:line] | |
