# Ambiguity Analysis: General Spec

> Evaluate every requirement for interpretive ambiguity from the perspective of an autonomous software development agent. Produce actionable clarification questions.

---

## Why This Matters

Autonomous implementation agents cannot ask clarifying questions during execution. Every ambiguity becomes a guess, and guesses become bugs or rework. The goal is to ensure every requirement in the spec has exactly one reasonable interpretation.

**The test:** "If I gave this requirement to 5 different senior engineers with no additional context, would they all build the same thing?"

---

## Ambiguity Categories

Analyze every requirement, acceptance criterion, and architectural constraint against these six categories.

### Category 1: Multiple Interpretations

The requirement text could be read two or more ways, each producing a different implementation.

**Detection signals:**
- Vague nouns: "the data", "the response", "the output" — which data? what format?
- Unqualified adjectives: "fast", "secure", "scalable", "clean" — by what measure?
- Implied behavior: "handle errors" — log? retry? return error response? all three?
- Ambiguous pronouns: "it should update" — update what? how? when?
- Passive voice hiding the actor: "the record is updated" — by whom? triggered by what?

**For each finding, produce:**

| Requirement | Ambiguity | Possible Interpretations | Clarification Question |
|------------|-----------|-------------------------|----------------------|
| [text] | [what's ambiguous] | (A) ... (B) ... (C) ... | [specific question] |

### Category 2: Undefined Edge Cases

The requirement defines the happy path but not what happens at boundaries or under failure.

**Detection signals:**
- No error handling specified for operations that can fail (API calls, DB writes, file I/O)
- No behavior defined for empty inputs, null values, missing fields
- No boundary conditions (max length, min value, overflow)
- No timeout or retry semantics for external calls
- No behavior for concurrent operations on shared state

**For each finding, produce a specific "What happens when..." question:**
- "What happens when the external API returns a 500?"
- "What happens when the input list is empty?"
- "What happens when two requests update the same record simultaneously?"

### Category 3: Implicit Assumptions

The spec assumes something without stating it. The implementation agent may not share these assumptions.

**Detection signals:**
- References to "standard" or "typical" behavior without definition
- Assumptions about data format, schema, or quality not stated
- Assumptions about infrastructure (single instance vs. distributed, cloud provider)
- Assumptions about user behavior or input patterns
- Assumptions about ordering, timing, or sequence of operations
- Assumptions about authentication, authorization, or permissions model

**For each finding, state the assumption and ask whether it's correct:**
- "This assumes all users are authenticated. Is that correct, or should unauthenticated access be handled?"
- "This assumes the database supports transactions. Should the spec state this requirement?"

### Category 4: Vague Scope Boundaries

It's unclear where this feature's responsibility starts and ends.

**Detection signals:**
- Open-ended phrases: "and other similar...", "etc.", "as needed"
- Requirements that could expand infinitely: "support all formats", "handle any input"
- Unclear integration boundaries: "integrate with the API" — which endpoints? what auth?
- Missing explicit scope-out for obvious adjacent concerns
- "Future-proof" language without concrete boundaries

**For each finding, ask what's in and what's out:**
- "The spec says 'support common file formats'. Which formats specifically? Should the spec enumerate them?"
- "'Integrate with the notification service' — which notification types? Email only, or also SMS/push?"

### Category 5: Contradictory Requirements

Two or more requirements conflict with each other. Both cannot be true simultaneously.

**Detection signals:**
- Performance vs. correctness trade-offs not resolved
- Security vs. usability contradictions (e.g., "seamless login" + "require MFA")
- Scope-in items that conflict with stated constraints
- Acceptance criteria that cannot all be true simultaneously
- Requirements in different sections that specify different behavior for the same scenario

**For each finding, state both requirements and the contradiction:**
- "Requirement 3 says 'responses under 200ms' but Requirement 7 says 'validate against external service on every request'. These likely conflict — which takes priority?"

### Category 6: Missing "What Happens When" Scenarios

Operational scenarios that the spec doesn't address.

**Detection signals:**
- No failure mode discussion for the system as a whole
- No degraded-mode behavior (what works when a dependency is down?)
- No rollback or recovery process for failed operations
- No monitoring or observability requirements
- First-time setup vs. steady-state not distinguished
- No migration path from current state to new state

**For each finding, identify the scenario and ask how it should be handled:**
- "What happens if the migration fails halfway? Is there a rollback strategy?"
- "How should the system behave when the cache is cold (first request after deploy)?"

---

## How to Analyze

For each requirement in the spec (from Requirements, Acceptance Criteria, and Architecture sections):

1. **Read the requirement in isolation** — without the context of surrounding text
2. **Apply the "5 senior engineers" test** — would they all build the same thing?
3. **If no** — identify which category the ambiguity falls into
4. **Write the specific clarification question** that would resolve it
5. **Rate severity:**
   - **HIGH** — different interpretations lead to fundamentally different implementations
   - **MEDIUM** — different interpretations lead to different behavior in edge cases
   - **LOW** — different interpretations lead to cosmetic or minor differences

**Cross-reference with source tracing:** If the discovery document answers a question that the spec leaves ambiguous, that is a source tracing gap (the answer exists but wasn't carried into the spec), NOT an ambiguity finding. Do not double-count.

---

## Output Format

### Ambiguity Summary

| Severity | Count |
|----------|-------|
| HIGH | [n] |
| MEDIUM | [n] |
| LOW | [n] |

### Findings

| # | Spec Section | Requirement | Category | Severity | Ambiguity | Clarification Question |
|---|-------------|------------|----------|----------|-----------|----------------------|
| 1 | [section] | [requirement text] | [1-6] | HIGH/MED/LOW | [what's ambiguous] | [specific question] |

---

## Scoring

- **FAIL** if any HIGH severity ambiguity exists
- **WARN** if MEDIUM severity ambiguities exist
- **PASS** if only LOW severity or none
