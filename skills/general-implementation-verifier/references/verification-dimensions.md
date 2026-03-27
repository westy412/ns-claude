# Verification Dimensions

> **When to read:** When generating teammate prompts in Phase 1. Each section defines what one verification agent checks.

Each dimension is assigned to one agent. The agent spawns `codebase-researcher` sub-agents to investigate specific areas, then synthesizes findings into structured results.

---

## Dimension 1: Spec Compliance

**Agent:** `spec-compliance-verifier`
**Purpose:** Verify every requirement and acceptance criterion from the spec is implemented correctly.

### What to Check

**Requirements Traceability:**
- Read the spec's `## Requirements` section
- For each requirement, trace it to specific code that implements it
- Flag requirements with no corresponding implementation as FAIL
- Flag requirements that are partially implemented as WARN

**Acceptance Criteria:**
- Read the spec's `## Acceptance Criteria` section
- For each criterion, determine if it can be verified from the code
- Criteria with executable commands (e.g., `All tests pass: npm test`) -- note but do not execute (test verification is a future dimension)
- Criteria that are verifiable by reading code -- verify them
- Flag unmet criteria as FAIL

**Architecture Compliance:**
- Read the spec's `## Architecture` section (if present)
- Verify key architectural decisions are reflected in the code
- Check that specified patterns are followed (e.g., "use repository pattern" -- verify repositories exist)
- Check that specified constraints are respected (e.g., "no direct DB access from handlers")

**Deviations:**
- Read the progress file's `## Deviations from Spec` section
- For each documented deviation, assess if it's reasonable or problematic
- Undocumented deviations (code differs from spec with no explanation) are FAIL
- Documented deviations with rationale are WARN (flag for human review)

### How to Investigate

Spawn `codebase-researcher` sub-agents for:
- Tracing a specific requirement to code: "Find the implementation of [requirement]. Check [files from execution plan]."
- Verifying an architectural pattern: "Check if [pattern] is followed in [directory]. Look for violations."
- Checking a specific acceptance criterion: "Verify that [criterion] is met by examining [relevant files]."

### Findings Format

For each check, report:
```
### [Requirement/Criterion ID or text]
- **Status:** PASS | WARN | FAIL
- **Evidence:** [What code was found / not found, with file paths and line numbers]
- **Issue:** [If WARN/FAIL: what's wrong]
- **Fix:** [If WARN/FAIL: what needs to change]
```

---

## Dimension 2: Completeness

**Agent:** `completeness-verifier`
**Purpose:** Verify all planned files, chunks, and phases from the execution plan exist and are populated.

### What to Check

**Execution Plan Coverage:**
- Read the spec's `## Execution Plan` section (all phases, all chunks)
- Read the progress file's `## Execution Plan Snapshot` and `## Stream Status`
- For each chunk marked `done` in progress: verify the expected output actually exists
- For chunks marked `pending` or `in_progress`: flag as FAIL (implementation incomplete)
- For chunks marked `blocked` or `skipped`: flag as WARN with the documented reason

**File Existence:**
- Read the progress file's `## Completed Files` section
- For each file listed: verify it exists on disk
- For each file listed: verify it is non-empty and contains meaningful content (not just boilerplate/stubs)
- Check the spec's execution plan for files that should exist but aren't listed in progress

**Stream Completeness:**
- For each work stream defined in the spec:
  - Verify all phases for that stream have been completed
  - Check that the stream's owned files all exist
  - Verify key outputs mentioned in chunk outcomes are present

**Progress File Accuracy:**
- Compare progress file claims against reality:
  - Files marked complete actually exist and are populated
  - Phase statuses match what's in the codebase
  - No orphaned files (files that exist but aren't tracked in progress)

**Stub Detection:**
- Look for TODO comments, placeholder functions, or empty implementations
- Functions that throw "not implemented" errors
- Files that exist but only contain imports and empty class/function shells
- Flag stubs as FAIL with the specific location

### How to Investigate

Spawn `codebase-researcher` sub-agents for:
- Checking a set of files: "Verify these files exist and are non-empty: [file list]. Report any that are missing or contain only stubs."
- Verifying a chunk's output: "The execution plan says [chunk] should produce [outcome]. Check if this exists in [files/directories]."
- Finding stubs: "Search [directories] for TODO comments, NotImplementedError, placeholder functions, or empty implementations."

### Findings Format

For each check, report:
```
### [Chunk/File/Stream name]
- **Status:** PASS | WARN | FAIL
- **Expected:** [What the spec/progress file says should exist]
- **Actual:** [What actually exists]
- **Issue:** [If WARN/FAIL: what's missing or incomplete]
- **Fix:** [If WARN/FAIL: what needs to be created or completed]
```

---

## Dimension 3: Code Quality

**Agent:** `code-quality-verifier`
**Purpose:** Review the implemented code for correctness, security, performance, maintainability, and error handling.

### Scope

Only review files that were created or modified as part of this implementation. Use the progress file's `## Completed Files` section and git history to determine scope.

### What to Check

**3a. Correctness**

| Check | Severity | What to look for |
|-------|----------|-----------------|
| Null/undefined handling | Error | Chaining on nullable returns without guards; `array.find()` used without undefined check |
| Boundary conditions | Error | Division by zero; empty collection access; off-by-one in loops |
| Boolean logic | Error | Inverted conditions; wrong operator (`&&` vs `||`); De Morgan violations |
| Unreachable code | Warning | Code after unconditional return/throw; conditions always true/false |
| Type mismatches | Error | Wrong type passed to function; implicit coercions that change behavior |

**3b. Security**

| Check | Severity | What to look for |
|-------|----------|-----------------|
| Injection vulnerabilities | Critical | SQL string concatenation; unsanitized template rendering; OS command injection |
| Hardcoded secrets | Critical | API keys, tokens, passwords in source; high-entropy strings in code |
| Auth/authz flaws | Critical | Missing authorization checks; IDOR (resource access without ownership verification) |
| XSS | High | `innerHTML` with user content; `dangerouslySetInnerHTML` without sanitization |
| Sensitive data exposure | High | Passwords/tokens in logs; PII in API responses unnecessarily |
| Insecure configuration | Medium | `DEBUG=true` in production config; `CORS *` with credentials; TLS verification disabled |

**3c. Performance**

| Check | Severity | What to look for |
|-------|----------|-----------------|
| N+1 queries | Error | Database query inside a loop; ORM lazy loading in iteration |
| Inefficient algorithms | Warning | Nested loops where a Map/Set lookup would work; repeated `Array.find()` in loops |
| Memory leaks | Error | Event listeners without cleanup; intervals not cleared; growing caches with no eviction |
| Unnecessary computation | Warning | Sorting same array multiple times; recalculating values that could be cached |
| Bundle concerns | Info | Importing entire libraries when only one function needed |

**3d. Maintainability**

| Check | Severity | What to look for |
|-------|----------|-----------------|
| Code duplication | Warning | Near-identical logic blocks (>6 lines) copied across files |
| Function length | Warning | Functions >40 lines doing multiple distinct operations |
| Excessive nesting | Warning | >3 levels of nesting; complex guard clauses that should be early returns |
| Magic numbers/strings | Warning | Inline numeric/string literals without named constants |
| Naming quality | Info | Single-letter vars outside loops; generic names (`data`, `info`, `handler`) |
| Circular dependencies | Error | Module A imports B imports A |

**3e. Error Handling**

| Check | Severity | What to look for |
|-------|----------|-----------------|
| Silent error swallowing | Critical | Empty catch blocks; catch that only logs without re-throwing or handling |
| Unhandled promises | Error | Async calls without await and without .catch(); fire-and-forget patterns |
| Missing error propagation | Error | Function returns null on failure instead of throwing; error converted to boolean |
| Missing error context | Warning | `logger.error('failed')` without the error object; no correlation/request ID |
| Catch-all without discrimination | Warning | Catching all exceptions identically rather than handling specific error types |

**3f. Type Safety (TypeScript projects)**

| Check | Severity | What to look for |
|-------|----------|-----------------|
| `any` on public APIs | Critical | Exported functions with `any` params or return types |
| Missing runtime validation | Error | External data (API response, user input) cast to a type without Zod/schema validation |
| Non-null assertion abuse | Warning | `value!` without preceding null guard |
| Type assertion overuse | Warning | `as Type` casts instead of type guards; double assertions `as unknown as X` |

### How to Investigate

Spawn `codebase-researcher` sub-agents per quality sub-dimension:
- "Review [files] for security issues: injection, hardcoded secrets, auth flaws, XSS. Report findings with file paths and line numbers."
- "Check [files] for correctness: null handling, boundary conditions, boolean logic, unreachable code."
- "Analyze [files] for performance: N+1 queries, inefficient algorithms, memory leaks."
- "Review [files] for maintainability: duplication, function length, nesting, magic numbers."
- "Check [files] for error handling: empty catches, unhandled promises, missing propagation."

Group files by area (e.g., all API handlers together, all data layer together) to give each sub-agent focused context.

### Findings Format

For each finding, report:
```
### [Sub-dimension]: [Brief description]
- **Status:** PASS | WARN | FAIL
- **Severity:** Critical | High | Medium | Low
- **Location:** [file:line]
- **Issue:** [What's wrong]
- **Evidence:** [Code snippet or pattern found]
- **Fix:** [What needs to change]
```

Group findings by sub-dimension (3a through 3f). Within each group, order by severity (Critical first).

---

## Future Dimension: Test Verification (Not Yet Active)

**Agent:** `test-verifier` (placeholder -- do not spawn)

When testing infrastructure is in place, this agent will check:
- Test files exist for implemented modules
- Tests cover critical paths (happy path + error paths)
- Test commands from acceptance criteria pass
- No tests that only verify mocks (over-mocking)
- No flaky patterns (shared mutable state, real timers, real network calls)
