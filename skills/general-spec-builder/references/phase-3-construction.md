# Phase 3: Spec Construction

> **When to read:** After Phase 2 (Research) is complete. This phase walks through writing each section of the spec template, working WITH the user section by section.

---

## Core Approach

Work through each section WITH the user. Don't fill it out alone.

For each section:
1. **Draft** based on discovery doc + research findings
2. **Present** to user
3. **Get feedback** and refine
4. **Write** to the spec file
5. **Move** to next section

Use the spec template at `templates/spec.md` as the starting structure.

---

## Section: Meta

Simple metadata table. Fill from context gathered in Phase 1.

| Field | Guidance |
|-------|----------|
| **Type** | Determines which skills are needed. Values: `backend-api`, `frontend`, `agent-langgraph`, `agent-dspy`, `hybrid` |
| **Repo** | Repository name from discovery doc or user input |
| **Status** | Start as `draft`. Changes to `in-progress` when work begins, `complete` when done |
| **Created** | Today's date |

---

## Section: Overview

2-3 paragraphs maximum. Should answer:
- What are we building?
- Why are we building it?
- What's the context?

**Keep it concise.** The discovery doc has the full thinking; the spec is operational.

---

## Section: Skills

List skills the implementing agent should load before starting work. Populated from Phase 1 skill discovery.

```markdown
Load these skills before starting:
- backend-api
- cloudrun-deploy
```

**Note:** Some skills may not exist yet. List what SHOULD be loaded; the agent will skip missing ones.

---

## Section: Requirements

The "what" — what needs to be true when this work is complete.

- Transform from discovery doc's "Solution Overview" and "Scope"
- Be specific enough that acceptance can be verified
- Include both functional and non-functional requirements

**Ask the user:** "Here are the requirements I've extracted. Anything missing or wrong?"

---

## Section: Architecture

**Optional for simple work.** Include when:
- Key technical decisions must be followed
- Specific patterns must be used
- Constraints exist (performance, compatibility)
- Multiple components need to coordinate

Pull from:
- Discovery doc's "Key Decisions"
- Research findings (codebase patterns, reference projects)
- User input on preferences

### Work Type Variations

| Type | Architecture Should Include |
|------|----------------------------|
| `backend-api` | API contracts, database schema, auth approach, error handling patterns |
| `frontend` | Component hierarchy, state management, routing, styling conventions |
| `hybrid` | How agent interacts with other components, data flow, sequencing |

---

## Section: Reference Files

**Required section.** Lists all files that informed this spec.

Two sources:
1. **From Discovery** — Copy reference files from the discovery document
2. **From Spec Research** — Add files examined during Phase 2

```markdown
## Reference Files

**From Discovery:**
- `src/auth/handlers.py` — Existing auth patterns
- `docs/api-design.md` — API design guidelines

**From Spec Research:**
- `src/middleware/rate_limit.py` — Rate limiting implementation to follow
- `tests/auth/` — Existing auth test patterns
```

**Why this matters:** The implementing agent can quickly reference these files to understand patterns and conventions without re-discovering them.

---

## Section: Execution Plan

**This is the most important section.** It defines the contract between spec-builder and the implementation builder.

**Read `references/execution-plan-guide.md` for comprehensive guidance** on phases, chunks, streams, and communication.

At a high level, this section defines:
- **Work streams** — groups of related chunks assigned to the same agent
- **Phases** — sequential barriers; chunks within a phase run in parallel
- **Chunks** — individual units of work
- **Communication** — what agents share between streams

**Ask the user:** "Does this execution plan make sense? Are the phases and streams right?"

---

## Section: Acceptance Criteria

For the **whole spec**, not individual chunks. Must be verifiable — preferably with commands.

```markdown
- [ ] User can log in with email/password
- [ ] JWT tokens expire after 1 hour
- [ ] All tests pass: `pytest tests/auth/`
- [ ] Linting clean: `ruff check src/`
```

Pull from:
- Discovery doc's success criteria
- Requirements (inverted into verifiable checks)
- Standard quality gates (tests, linting, type checking)

---

## Section: Completion Promise

A unique string that signals the entire spec is complete. The `general-implementation-builder` outputs this after verifying all acceptance criteria pass.

**Format:** `<promise>[DESCRIPTIVE_NAME]_COMPLETE</promise>`

Examples:
- `<promise>AUTH_SYSTEM_COMPLETE</promise>`
- `<promise>USER_ONBOARDING_COMPLETE</promise>`

Must be unique within the project.

---

## Section: Notes

Initially empty or populated with key decisions from the discovery doc. Accumulates during work:
- Design decisions made
- Context discovered
- Trade-offs chosen

---

## Writing the Spec File

After all sections are drafted and user-approved:

1. Confirm the save location: "I'll save this to `/specs/[name].md`. Good?"
2. Write the spec file using the completed template
3. Update progress.md to reflect completed sections

---

## Phase Completion Checklist

Before moving to Phase 4 (or Phase 5 if no hybrid handoff needed):
- [ ] All sections drafted and user-reviewed
- [ ] Execution plan reviewed for completeness
- [ ] Spec file written to `/specs/[name].md`
- [ ] Progress.md updated with completed sections
