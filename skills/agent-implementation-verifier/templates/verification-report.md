# Verification Report: [spec-name]

**Spec Folder:** [path to spec folder]
**Manifest:** [spec/manifest.yaml]
**Framework:** [DSPy | LangGraph]
**System Type:** [single-agent | agent-team | nested-teams]
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
| 3 | Framework Compliance | | 0 | 0 | [link to section] |
| 4 | Code Quality | | 0 | 0 | [link to section] |

**Total blocking issues:** [count]
**Total warnings:** [count]

---

## 1. Spec Compliance

### Agent Type Compliance

| # | Agent | Spec Type | Impl Type | Status | Location |
|---|-------|-----------|-----------|--------|----------|
| | [agent name] | [from agent-config.yaml] | [what's implemented] | PASS/FAIL | [file:line] |

### Model Configuration

| # | Agent | Spec Model | Impl Model | Status | Location |
|---|-------|-----------|------------|--------|----------|
| | [agent name] | [provider/name/tier] | [what's implemented] | PASS/FAIL | [file:line] |

### Prompt Configuration

| # | Agent | Spec Role | Spec Modifiers | Impl Matches? | Status |
|---|-------|-----------|---------------|---------------|--------|
| | [agent name] | [role] | [modifiers] | Yes/No | PASS/WARN/FAIL |

### I/O Signature Compliance

| # | Agent | Spec I/O | Impl I/O | Status | Location |
|---|-------|---------|---------|--------|----------|
| | [agent] | [inputs/outputs from spec] | [InputField/OutputField or State fields] | PASS/FAIL | [file:line] |

### Team Pattern

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| | Team pattern matches spec | PASS/FAIL | [team.py implements pipeline/router/etc.] |
| | Nested team hierarchy correct | PASS/FAIL/N/A | [evidence] |

### Cross-Agent Data Flow

| # | From Agent | To Agent | Data | Status | Issue |
|---|-----------|----------|------|--------|-------|
| | [agent A] | [agent B] | [field names] | PASS/FAIL | [if broken: what's wrong] |

---

## 2. Completeness

### Framework File Layout

| # | Expected File | Exists? | Non-Empty? | Status |
|---|--------------|---------|------------|--------|
| | [file path per framework layout] | Yes/No | Yes/No/Stub | PASS/FAIL |

### Phase Output Verification

| Phase | Expected Output | Exists? | Status | Notes |
|-------|----------------|---------|--------|-------|
| 0 | pyproject.toml, src/, progress.md | | | |
| 1 | team.py with orchestration | | | |
| 2 | tools.py (if needed) | | | |
| 3 | Agent implementations | | | |
| 4 | Prompts/Signatures | | | |
| 5 | utils.py | | | |
| 6 | .env.example | | | |
| 7 | main.py (FastAPI) | | | |

### Execution Plan Coverage

| Phase | Chunk | Stream | Expected Status | Actual Status | Notes |
|-------|-------|--------|----------------|---------------|-------|
| | | | done | | |

### Stubs and Placeholders

| # | Location | Type | Status |
|---|----------|------|--------|
| | [file:line] | TODO / empty function / pass body | FAIL |

---

## 3. Framework Compliance

### Pattern Compliance ([DSPy | LangGraph])

| # | Pattern | Status | Location | Issue | Fix |
|---|---------|--------|----------|-------|-----|
| | [pattern name from framework checks] | PASS/FAIL | [file:line] | | |

### Anti-Pattern Detection

| # | Anti-Pattern | Detected? | Location | Severity |
|---|-------------|-----------|----------|----------|
| | [anti-pattern from framework checks] | Yes/No | [file:line] | FAIL/WARN |

### Team Orchestration

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| | [orchestration fidelity check] | PASS/FAIL | [evidence] |

### Communication Contracts

| # | From | To | Data | Fulfilled? | Status |
|---|------|----|------|-----------|--------|
| | [stream/agent] | [stream/agent] | [what should be sent] | Yes/No | PASS/FAIL |

---

## 4. Code Quality

### 4a. Correctness

| # | Finding | Severity | Location | Issue | Fix |
|---|---------|----------|----------|-------|-----|
| | | Critical/High/Medium/Low | [file:line] | | |

### 4b. Security

| # | Finding | Severity | Location | Issue | Fix |
|---|---------|----------|----------|-------|-----|
| | | Critical/High/Medium/Low | [file:line] | | |

### 4c. Performance

| # | Finding | Severity | Location | Issue | Fix |
|---|---------|----------|----------|-------|-----|
| | | Critical/High/Medium/Low | [file:line] | | |

### 4d. Maintainability

| # | Finding | Severity | Location | Issue | Fix |
|---|---------|----------|----------|-------|-----|
| | | Critical/High/Medium/Low | [file:line] | | |

### 4e. Error Handling

| # | Finding | Severity | Location | Issue | Fix |
|---|---------|----------|----------|-------|-----|
| | | Critical/High/Medium/Low | [file:line] | | |

---

## Spec Traceability Matrix

> Maps every agent spec requirement to an implementation outcome.

### Per-Agent Traceability

| # | Agent | Requirement | Outcome | Impl Location | Notes |
|---|-------|------------|---------|---------------|-------|
| | [agent name] | [requirement from agent spec] | CORRECT / INCORRECT / AMBIGUOUS / MISSING | [file:line] | |

### Acceptance Criteria

| # | Criterion | Outcome | Impl Location | Notes |
|---|----------|---------|---------------|-------|
| | [from overview.md or manifest] | CORRECT / INCORRECT / AMBIGUOUS / MISSING | [file:line] | |

### Ambiguity Detail

| # | Agent/Requirement | Ambiguity Category | What Was Ambiguous | What Agent Assumed | What Was Needed |
|---|------------------|-------------------|-------------------|-------------------|-----------------|
| | | Vague agent type / Missing I/O fields / Unclear data flow / Framework assumption / Conflicting configs / Unspecified model tier | | | |

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
