# Ambiguity Analysis: Agent Spec

> Evaluate every requirement for interpretive ambiguity from the perspective of an autonomous implementation agent. Includes 6 general categories plus 3 agent-specific categories. Produce actionable clarification questions.

---

## Why This Matters

Autonomous implementation agents cannot ask clarifying questions during execution. Agent specs are especially prone to ambiguity because they describe distributed behavior across multiple components — agent boundaries, tool contracts, and orchestration logic all create additional surfaces where assumptions can diverge.

**The test:** "If I gave this spec to 5 different senior engineers with no additional context, would they all build the same agent system?"

---

## General Ambiguity Categories (1-6)

### Category 1: Multiple Interpretations

The requirement text could produce different implementations.

**Detection signals:**
- Vague nouns: "the data", "the response" — which data? what format?
- Unqualified adjectives: "fast", "accurate", "reliable" — by what measure?
- Implied behavior: "process the input" — transform? validate? both?
- Ambiguous pronouns in multi-agent context: "it should handle" — which agent?

**Produce:** requirement, ambiguity, possible interpretations (A/B/C), clarification question.

### Category 2: Undefined Edge Cases

Happy path defined but boundaries and failures unaddressed.

**Detection signals:**
- No error handling for API calls, LLM calls, tool invocations
- No behavior for empty/null/malformed inputs to agents
- No timeout semantics for LLM calls or tool executions
- No behavior for agents that produce low-confidence outputs

**Produce:** specific "What happens when..." questions.

### Category 3: Implicit Assumptions

Unstated assumptions about the system.

**Detection signals:**
- Assumptions about LLM capabilities (model can "understand" without specifying how)
- Assumptions about data availability or quality
- Assumptions about execution environment
- Assumptions about ordering or concurrency

**Produce:** state the assumption, ask whether it's correct.

### Category 4: Vague Scope Boundaries

Unclear where responsibilities start and end.

**Detection signals:**
- Open-ended phrases: "and similar...", "etc."
- "Handle any type of..." without enumeration
- Unclear integration boundaries

**Produce:** ask what's in scope and what's out.

### Category 5: Contradictory Requirements

Requirements that conflict with each other.

**Detection signals:**
- Agent A's output schema conflicts with Agent B's input schema
- Performance requirements conflict with thoroughness requirements
- Scope contradictions between team.md and agent specs

**Produce:** state both requirements and the contradiction.

### Category 6: Missing "What Happens When" Scenarios

Unaddressed operational scenarios.

**Detection signals:**
- No system-level failure mode discussion
- No degraded-mode behavior
- No rollback/recovery for failed pipeline runs

**Produce:** identify scenario, ask how it should be handled.

---

## Agent-Specific Ambiguity Categories (7-9)

### Category 7: Agent Boundary Ambiguity

It's unclear which agent is responsible for a specific behavior.

**Detection signals:**
- A requirement that could belong to multiple agents
- Overlapping agent purposes or responsibilities
- Handoff points between agents not precisely defined
- Shared state or resources without clear ownership
- "The system should..." without specifying which agent

**For each finding, produce:**

| Requirement | Agent A Could Own It | Agent B Could Own It | Clarification Question |
|------------|---------------------|---------------------|----------------------|
| [text] | [why A] | [why B] | "Which agent is responsible for [behavior]?" |

### Category 8: Tool Behavior Ambiguity

A tool's behavior, inputs, outputs, or error modes are not fully defined.

**Detection signals:**
- Tool listed without input/output format specification
- Tool error modes not defined (what does the agent do when a tool fails?)
- Tool retry behavior not specified
- Tool invocation conditions ambiguous ("call when needed" — when specifically?)
- Tool output interpretation not defined (what does the agent do with the result?)

**For each finding, produce:**

| Tool | Agent | Ambiguity | Clarification Question |
|------|-------|-----------|----------------------|
| [tool name] | [agent] | [what's unclear] | [specific question] |

### Category 9: Orchestration Ambiguity

The flow between agents — sequencing, parallelism, retries, failure handling — is unclear.

**Detection signals:**
- Retry semantics not defined (how many times? backoff strategy? what triggers retry?)
- Failure cascade undefined (what happens downstream when an agent fails?)
- Parallel execution assumptions not stated (are these agents truly independent?)
- State management between agents unclear (who maintains shared state? how is it passed?)
- Loop termination conditions vague ("iterate until good enough" — what's the threshold?)
- Human-in-the-loop triggers undefined (when does the system escalate to a human?)

**For each finding, produce:**

| Flow Point | Agents Involved | Ambiguity | Clarification Question |
|-----------|----------------|-----------|----------------------|
| [handoff/branch/loop] | [agent names] | [what's unclear] | [specific question] |

---

## How to Analyze

For each requirement across all spec files (overview.md, team.md, agents/*.md, manifest.yaml):

1. **Read the requirement in isolation**
2. **Apply the "5 senior engineers" test**
3. **If no** — identify the category (1-9)
4. **Write the specific clarification question**
5. **Rate severity:**
   - **HIGH** — different interpretations lead to fundamentally different agent systems
   - **MEDIUM** — different interpretations lead to different behavior in edge cases
   - **LOW** — different interpretations lead to cosmetic or minor differences

**Cross-reference with source tracing:** If the discovery document answers a question the spec leaves ambiguous, that is a source tracing gap, NOT an ambiguity finding.

---

## Output Format

### Ambiguity Summary

| Severity | Count |
|----------|-------|
| HIGH | [n] |
| MEDIUM | [n] |
| LOW | [n] |

### Findings

| # | Spec File | Requirement | Category | Severity | Ambiguity | Clarification Question |
|---|----------|------------|----------|----------|-----------|----------------------|
| 1 | [file] | [text] | [1-9] | HIGH/MED/LOW | [what's ambiguous] | [specific question] |

---

## Scoring

- **FAIL** if any HIGH severity ambiguity exists
- **WARN** if MEDIUM severity ambiguities exist
- **PASS** if only LOW severity or none
