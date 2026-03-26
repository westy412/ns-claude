# Review: General Spec

> Review checklist for specs produced by `general-spec-builder`. The spec is a single `.md` file at `/specs/[name].md`.

---

## Structural Checks

### Check 1: Required Sections Present

Every general spec MUST contain these sections. Mark FAIL if missing.

| Section | Required | What to look for |
|---------|----------|------------------|
| Meta | Yes | Table with Type, Repo, Status, Created |
| Overview | Yes | 2-3 paragraphs explaining what and why |
| Skills | Yes | List of skills for the implementing agent |
| Requirements | Yes | What must be true when done |
| Architecture | Conditional | Required for complex work (multi-component, new patterns). Optional for simple single-file changes |
| Reference Files | Yes | Files from discovery + spec research |
| Execution Plan | Yes | Work streams, phases, chunks, communication |
| Acceptance Criteria | Yes | Verifiable checks |
| Completion Promise | Yes | `<promise>` tag with unique string |
| Notes | Optional | Design decisions, context |

### Check 2: Meta Table Completeness

| Field | Valid Values | Check |
|-------|-------------|-------|
| Type | backend-api, frontend, agent-langgraph, agent-dspy, hybrid | Must be one of these |
| Repo | Non-empty | Must name the target repo |
| Status | draft, in-progress, complete | Must be set |
| Created | Date string | Must be present |

---

## Execution Plan Checks

### Check 3: Stream Ownership — No File Conflicts

For every file/directory listed in Work Streams `Owns` column:
1. List which stream owns it
2. FAIL if any file appears in multiple streams

Two agents editing the same file in parallel causes merge conflicts.

### Check 4: Chunk Sizing

Review each chunk in the execution plan:

**FAIL if too granular:**
- Single-file chunks that take < 1 hour
- More than 10 chunks for a medium feature
- Individual function-level chunks

**FAIL if too large:**
- Chunks spanning multiple unrelated concerns
- Chunks with > 10 sub-tasks
- Chunks that would take > 8 hours of focused work

**PASS if right-sized:**
- 2-8 hours of focused work per chunk
- 5-8 chunks typical for a medium feature
- Each chunk has a clear, independently verifiable outcome

### Check 5: Phase Dependencies

Verify the phase structure makes sense:
- Chunks in the same phase should be truly independent (parallelizable)
- Later phases should depend on earlier ones
- No circular dependencies

---

## Quality Checks

### Check 6: Acceptance Criteria Verifiability

For each criterion, ask: "Can this be objectively verified?"

**FAIL if:**
- Subjective language: "works well", "is clean", "is fast", "is good"
- Unquantified: "performs quickly" without a target metric
- Untestable: no command, API call, or clear observation to verify

**PASS if:**
- Binary (pass/fail)
- Testable (with a command, API call, or observation)
- Specific (not vague qualitative statements)

### Check 7: Skill Assignment

Every chunk in the execution plan must have a `Skills:` field:
- FAIL if any chunk is missing the skills field entirely
- WARN if a chunk involves technology-specific work but lists no skills
- PASS if `Skills: —` for pure config/documentation chunks

### Check 8: Overview Quality

- FAIL if the Overview section is just a copy of the discovery doc
- FAIL if it exceeds 3 paragraphs (operational, not exploratory)
- WARN if it doesn't explain both WHAT and WHY

### Check 9: Requirements Specificity

- FAIL if requirements are vague ("support user authentication" without specifying method)
- WARN if requirements duplicate acceptance criteria (they should complement, not repeat)
- PASS if requirements state what must be true when done, not how to get there

### Check 10: Reference Files Exist

For each file listed in Reference Files:
- WARN if the file path doesn't exist on disk (may indicate stale references)
- PASS if files exist or are clearly external references

---

## Anti-Pattern Checks

### Check 11: Spec Anti-Patterns

| Anti-Pattern | Detection | Status |
|-------------|-----------|--------|
| Discovery doc copy-pasted into spec | Overview > 3 paragraphs, exploratory language | FAIL |
| Implementation details in spec | Code examples, pseudo-code, specific function names | WARN |
| Vague acceptance criteria | Subjective language in criteria | FAIL |
| No communication defined for multi-stream | Multiple streams but empty Communication section | WARN |
| Progress updates in spec | References to "we decided" or session-specific context | WARN |

---

## Summary Template

After running all checks, present:

```
## Spec Review: [name]

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Required sections | | |
| 2 | Meta completeness | | |
| 3 | Stream ownership | | |
| 4 | Chunk sizing | | |
| 5 | Phase dependencies | | |
| 6 | Acceptance criteria verifiability | | |
| 7 | Skill assignment | | |
| 8 | Overview quality | | |
| 9 | Requirements specificity | | |
| 10 | Reference files exist | | |
| 11 | Anti-patterns | | |

**Blocking issues:** [count]
**Warnings:** [count]
```
