# Report Format

> **When to read:** When consolidating results from all verification agents into the final report (Phase 3).

---

## Severity Levels

Three status values, consistent with the `review-spec` skill:

| Status | Meaning | Blocking? |
|--------|---------|-----------|
| **PASS** | Requirement met, no issues found | No |
| **WARN** | Non-blocking issue flagged for attention | No |
| **FAIL** | Blocking issue, must be fixed before proceeding | Yes |

### Within Code Quality, findings also carry a severity:

| Severity | When to use |
|----------|-------------|
| **Critical** | Security vulnerabilities, data loss risk, silent failures in critical paths |
| **High** | Auth flaws, XSS, significant correctness errors |
| **Medium** | Performance issues in hot paths, maintainability concerns |
| **Low** | Style issues, minor naming concerns, informational findings |

### Mapping Severity to Status

| Severity | Maps to Status |
|----------|---------------|
| Critical | FAIL |
| High | FAIL |
| Medium | WARN |
| Low | WARN (or omit if trivial) |

---

## Overall Verdict

Determined by aggregating all findings:

| Condition | Verdict |
|-----------|---------|
| All dimensions PASS, no FAILs, no WARNs | **PASS** |
| No FAILs, but some WARNs exist | **WARNINGS ONLY** |
| Any FAIL in any dimension | **NEEDS FIXES** |

---

## Consolidation Rules

When merging findings from the 3 agents:

1. **Preserve attribution** -- each finding keeps its dimension label (Spec Compliance / Completeness / Code Quality)
2. **Deduplicate** -- if two agents flag the same file/issue, merge into one finding and note both dimensions flagged it
3. **Order by severity** -- within each dimension, FAILs first, then WARNs, then PASSes
4. **Count separately** -- the summary table shows blocking issues and warnings per dimension
5. **Cross-reference** -- if a completeness FAIL (file missing) explains a spec compliance FAIL (requirement unmet), link them

---

## Actionability Requirements

Every WARN or FAIL finding MUST include:

1. **What's wrong** -- specific, not vague ("Missing null check on user.profile" not "error handling could be better")
2. **Where** -- file path and line number (or file path and function name if line isn't precise)
3. **What needs to change** -- concrete fix description ("Add null guard before accessing user.profile.name" not "improve error handling")

Findings without all three are incomplete and should be revised before including in the report.

---

## Report Sections

The consolidated report follows the template at [verification-report.md](../templates/verification-report.md). Key sections:

### 1. Summary Table
One row per dimension. Shows PASS/WARN/FAIL status, count of blocking issues, count of warnings.

### 2. Spec Compliance Findings
All findings from the spec-compliance-verifier agent. Organized by:
- Requirements (one entry per requirement from the spec)
- Acceptance Criteria (one entry per criterion)
- Architecture Compliance (if spec has architecture section)
- Deviations (documented and undocumented)

### 3. Completeness Findings
All findings from the completeness-verifier agent. Organized by:
- Execution Plan Coverage (phase/chunk status)
- File Existence (per-file check)
- Stub Detection (TODOs, placeholders, empty implementations)

### 4. Code Quality Findings
All findings from the code-quality-verifier agent. Organized by sub-dimension:
- Correctness
- Security
- Performance
- Maintainability
- Error Handling
- Type Safety

### 5. Spec Traceability Matrix
Maps every requirement and acceptance criterion from the spec to an implementation outcome. This is the core of the feedback flywheel -- it tells the review skills what kinds of spec issues caused implementation failures.

**Outcome classifications:**

| Outcome | Meaning | Blame |
|---------|---------|-------|
| **CORRECT** | Spec was clear, implementation matches | Neither -- working as intended |
| **INCORRECT** | Spec was clear, implementation doesn't match | Implementation bug -- the agent built it wrong |
| **AMBIGUOUS** | Spec was unclear or ambiguous, causing wrong implementation | Spec quality issue -- the spec builder needs to improve |
| **MISSING** | Requirement not implemented at all | Implementation gap -- the agent skipped it |

**Why this matters:** Over time, review skills can read past `feedback/verification-*.md` files and detect recurring AMBIGUOUS patterns. If the same ambiguity type keeps causing failures (e.g., "spec says 'handle errors appropriately' without specifying error types"), the review skill can flag it pre-implementation in future specs.

**Ambiguity sub-categories** (when outcome is AMBIGUOUS, classify further):

| Category | Example |
|----------|---------|
| **Vague requirement** | "Handle errors appropriately" -- no specifics on which errors or how |
| **Missing edge case** | "Support pagination" -- doesn't specify behavior for empty results or invalid page numbers |
| **Implicit assumption** | "Use the existing auth" -- doesn't specify which auth mechanism or where it's configured |
| **Conflicting requirements** | Requirement A says "return 404" but Requirement B says "return empty array" for missing resources |
| **Unspecified interface** | "Expose an API endpoint" -- no method, path, request/response format |
| **Missing acceptance criterion** | Requirement exists but no way to verify it was implemented correctly |

### 6. Fix Priority
A consolidated, prioritized list of all FAIL findings across dimensions. Ordered by:
1. Critical security issues
2. Missing implementations (spec compliance FAILs)
3. Missing files (completeness FAILs)
4. High-severity code quality issues
5. Everything else

This section is what the implementation builder should consume when fixing issues.
