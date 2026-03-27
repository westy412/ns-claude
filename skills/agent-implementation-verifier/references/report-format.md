# Report Format

> **When to read:** When consolidating results from all verification agents into the final report (Phase 3).

This is the agent-implementation-verifier variant. It follows the same structure as the general-implementation-verifier's report format but adds agent-specific dimensions.

---

## Severity Levels

Three status values, consistent across all verification skills:

| Status | Meaning | Blocking? |
|--------|---------|-----------|
| **PASS** | Requirement met, no issues found | No |
| **WARN** | Non-blocking issue flagged for attention | No |
| **FAIL** | Blocking issue, must be fixed before proceeding | Yes |

### Within Code Quality and Framework Compliance, findings also carry a severity:

| Severity | When to use |
|----------|-------------|
| **Critical** | Security vulnerabilities, broken data flow, wrong agent types |
| **High** | Missing framework patterns, broken orchestration, I/O mismatches |
| **Medium** | Performance issues, maintainability concerns, missing async patterns |
| **Low** | Style issues, minor naming concerns |

### Mapping Severity to Status

| Severity | Maps to Status |
|----------|---------------|
| Critical | FAIL |
| High | FAIL |
| Medium | WARN |
| Low | WARN (or omit if trivial) |

---

## Overall Verdict

| Condition | Verdict |
|-----------|---------|
| All dimensions PASS, no FAILs, no WARNs | **PASS** |
| No FAILs, but some WARNs exist | **WARNINGS ONLY** |
| Any FAIL in any dimension | **NEEDS FIXES** |

---

## Consolidation Rules

When merging findings from the 4 agents:

1. **Preserve attribution** -- each finding keeps its dimension label
2. **Deduplicate** -- if two agents flag the same file/issue, merge into one finding
3. **Order by severity** -- FAILs first, then WARNs, then PASSes
4. **Count separately** -- the summary table shows blocking issues and warnings per dimension
5. **Cross-reference** -- if a framework FAIL explains a spec compliance FAIL, link them

---

## Actionability Requirements

Every WARN or FAIL finding MUST include:

1. **What's wrong** -- specific description
2. **Where** -- file path and line number
3. **What needs to change** -- concrete fix description

---

## Report Sections

### 1. Summary Table
One row per dimension (4 rows). PASS/WARN/FAIL status, blocking count, warning count.

### 2. Spec Compliance Findings
Agent types, model configs, prompt configs, I/O signatures, team pattern, data flow.

### 3. Completeness Findings
File layout, phase outputs, execution plan coverage, stub detection.

### 4. Framework Compliance Findings
Framework-specific patterns and anti-patterns, team orchestration, communication contracts.

### 5. Code Quality Findings
Correctness, security, performance, maintainability, error handling.

### 6. Spec Traceability Matrix
Maps every agent spec requirement to an implementation outcome.

**Outcome classifications:**

| Outcome | Meaning | Blame |
|---------|---------|-------|
| **CORRECT** | Spec was clear, implementation matches | Neither |
| **INCORRECT** | Spec was clear, implementation doesn't match | Implementation bug |
| **AMBIGUOUS** | Spec was unclear, caused wrong implementation | Spec quality issue |
| **MISSING** | Requirement not implemented at all | Implementation gap |

**Agent-specific ambiguity sub-categories:**

| Category | Example |
|----------|---------|
| **Vague agent type** | "Use an appropriate agent type" without specifying which |
| **Missing I/O fields** | Input/output section incomplete, agent had to guess field names |
| **Unclear data flow** | "Passes data to the next agent" without specifying which fields |
| **Framework assumption** | Spec references a pattern that doesn't exist in the declared framework |
| **Conflicting configs** | agent-config.yaml says one thing, agent.md spec says another |
| **Unspecified model tier** | No model assignment, agent had to pick a default |

### 7. Fix Priority
Consolidated, prioritized list of all FAIL findings.
