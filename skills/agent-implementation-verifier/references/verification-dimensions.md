# Verification Dimensions

> **When to read:** When generating teammate prompts in Phase 1. Each section defines what one verification agent checks.

Each dimension is assigned to one agent. The agent spawns `codebase-researcher` sub-agents to investigate specific areas, then synthesizes findings into structured results.

---

## Dimension 1: Spec Compliance

**Agent:** `spec-compliance-verifier`
**Purpose:** Verify every agent spec requirement is implemented correctly -- agent types, model configs, prompt configurations, and I/O signatures all match.

### What to Check

**Agent Type Compliance:**
- Read `agent-config.yaml` for each agent's declared type
- LangGraph types: `text-agent`, `message-agent`, `structured-output-agent`, `text-tool-agent`, `message-tool-agent`, `structured-output-tool-agent`
- DSPy types: `basic-agent`, `reasoning-agent`, `conversational-agent`, `tool-agent`
- Verify the implementation matches the declared type (e.g., DSPy `tool-agent` uses `ChainOfThought`/`Predict` + `ToolCalls` for single/predictable tools, or `ReAct` only for multi-step dynamic tool chains)
- Flag mismatches as FAIL

**Model Configuration Compliance:**
- Read `agent-config.yaml` for each agent's model settings (provider, name, reasoning, temperature)
- Verify the implementation uses the correct model provider and name
- DSPy: check singleton LM factories match the model tier (Flash vs Pro)
- LangGraph: check model tier is correct
- If `model.reasoning: true`, verify extended thinking / chain-of-thought is enabled
- Flag mismatches as FAIL

**Prompt Configuration Compliance:**
- Read `agent-config.yaml` for each agent's prompt config (framework, role, modifiers)
- Verify prompt content aligns with the declared role (e.g., `Researcher` role prompt should focus on investigation)
- Verify modifiers are reflected (e.g., `tools` modifier → prompt references tool usage; `structured-output` → prompt references output format)
- Flag missing modifier implementations as WARN

**I/O Signature Compliance:**
- Read each `{agent}.md` spec file for declared Inputs and Outputs
- Verify all spec inputs have corresponding implementation parameters:
  - DSPy: `InputField` declarations in signatures
  - LangGraph: `State` TypedDict fields
- Verify all spec outputs have corresponding implementation outputs:
  - DSPy: `OutputField` declarations
  - LangGraph: State return fields
- Flag missing I/O fields as FAIL

**Team Pattern Compliance:**
- Read `agent-config.yaml -> team.pattern`
- Verify `team.py` implements the correct pattern (pipeline, router, fan-in-fan-out, loop)
- For nested teams: verify parent orchestration matches the hierarchy in `manifest.yaml`
- Flag pattern mismatches as FAIL

**Cross-Agent Data Flow:**
- For each agent whose output feeds another agent's input (per spec):
  - Verify output field names/types match input field names/types
  - Verify the data is actually passed (not dropped between agents)
- Flag broken data flow as FAIL

### Findings Format

```
### [Agent name / Config entry]
- **Status:** PASS | WARN | FAIL
- **Spec says:** [what agent-config.yaml or agent spec declares]
- **Implementation has:** [what the code actually does]
- **Location:** [file:line]
- **Issue:** [if WARN/FAIL: what's wrong]
- **Fix:** [if WARN/FAIL: what needs to change]
```

---

## Dimension 2: Completeness

**Agent:** `completeness-verifier`
**Purpose:** Verify all framework-specific files exist, all phases produced their outputs, and nothing is missing or stubbed.

### What to Check

**Framework File Layout:**
- Determine framework from `agent-config.yaml`
- Check the expected file structure exists:

DSPy expected layout:
```
project/
  pyproject.toml, .env.example, main.py
  src/
    {team_name}/
      team.py, signatures.py, utils.py (REQUIRED)
      prompts/{agent_name}.md (one per agent)
      tools.py (if agents have tools)
      models.py (if needed)
```

LangGraph expected layout:
```
project/
  pyproject.toml, .env.example, main.py
  src/
    {team_name}/
      team.py, prompts.py
      tools.py (if agents have tools)
      utils.py (if needed)
```

- Flag missing required files as FAIL
- Flag missing optional files as WARN (with note on whether spec requires them)

**Execution Plan Coverage:**
- Read `manifest.yaml -> execution-plan` for all phases and chunks
- Read progress file for chunk statuses
- For each chunk marked `done`: verify expected output exists
- For chunks marked `pending`/`in_progress`: flag as FAIL
- For chunks marked `blocked`/`skipped`: flag as WARN

**Phase Output Verification:**
- Phase 0: pyproject.toml, src/ directory, progress.md exist
- Phase 1: team.py exists with orchestration logic
- Phase 2: tools.py exists (if spec defines tools)
- Phase 3: Agent functions are implemented (not just placeholders)
- Phase 4: Prompts exist (DSPy: prompts/*.md + signatures.py; LangGraph: prompts.py)
- Phase 5: utils.py exists (DSPy: REQUIRED; LangGraph: if needed)
- Phase 6: .env.example exists with required variables
- Phase 7: main.py exists with FastAPI endpoints

**Stub Detection:**
- TODO comments, placeholder functions, `pass` bodies, `NotImplementedError`
- DSPy: empty signature docstrings are EXPECTED (they're loaded from markdown), don't flag these
- Functions that exist but only contain imports and empty bodies
- Flag stubs as FAIL with specific location

**Nested Team Completeness:**
- For nested teams: verify each sub-team directory has its own complete file set
- Verify the parent team.py orchestrates all sub-teams

### Findings Format

```
### [File / Phase / Chunk]
- **Status:** PASS | WARN | FAIL
- **Expected:** [what the spec/framework requires]
- **Actual:** [what exists on disk]
- **Issue:** [if WARN/FAIL: what's missing]
- **Fix:** [if WARN/FAIL: what needs to be created]
```

---

## Dimension 3: Framework Compliance

**Agent:** `framework-compliance-verifier`
**Purpose:** Verify the implementation follows the correct framework patterns and avoids known anti-patterns. This dimension is framework-specific -- load the appropriate reference file.

The team lead includes the correct framework checks in this agent's prompt:
- DSPy → content from [framework-checks-dspy.md](framework-checks-dspy.md)
- LangGraph → content from [framework-checks-langgraph.md](framework-checks-langgraph.md)

### What to Check (Common)

**Team Orchestration Fidelity:**
- Does `team.py` implement the declared team pattern correctly?
- For nested teams: are sub-teams standalone modules (no factory functions)?
- Does the orchestration flow match the spec's team.md description?

**Communication Contract Fulfillment:**
- For each communication entry in the execution plan:
  - Does the sending agent's implementation produce the described data?
  - Does the receiving agent's implementation consume it?
  - Are field names/types compatible?

**Shared Infrastructure (Nested Teams):**
- Shared infrastructure (models, utils, services) lives at parent level
- Signatures and prompts are NOT shared between sibling teams
- Each sub-team has its own complete agent implementations

**See framework-specific reference files for the detailed checks.**

### Findings Format

```
### [Pattern / Anti-Pattern name]
- **Status:** PASS | WARN | FAIL
- **Category:** Pattern Compliance | Anti-Pattern Violation | Data Flow | Orchestration
- **Location:** [file:line]
- **Issue:** [what's wrong]
- **Evidence:** [code snippet or pattern found]
- **Fix:** [what needs to change]
```

---

## Dimension 4: Code Quality

**Agent:** `code-quality-verifier`
**Purpose:** Review the implemented code for correctness, security, performance, maintainability, and error handling.

This dimension is identical to the general-implementation-verifier's code quality dimension. The scope is all files created or modified as part of this implementation (from progress file's Completed Files section).

### What to Check

**4a. Correctness** -- Null handling, boundary conditions, boolean logic, unreachable code, type mismatches
**4b. Security** -- Injection, hardcoded secrets, auth flaws, XSS, sensitive data exposure, insecure config
**4c. Performance** -- N+1 queries, inefficient algorithms, memory leaks, unnecessary computation
**4d. Maintainability** -- Code duplication, function length, nesting, magic numbers, circular dependencies
**4e. Error Handling** -- Empty catches, unhandled promises, missing propagation, missing context

### Agent-Specific Quality Additions

Beyond the general checks, also verify:
- **Tool functions return dicts** (DSPy requirement) -- not Pydantic models or raw values
- **Async patterns** -- DSPy `aforward()` uses `await agent.acall()` with `call_with_retry`
- **Environment variable handling** -- sensitive config loaded from env vars, not hardcoded
- **FastAPI endpoint correctness** -- request/response schemas match spec inputs/outputs, proper error status codes

### Findings Format

```
### [Sub-dimension]: [Brief description]
- **Status:** PASS | WARN | FAIL
- **Severity:** Critical | High | Medium | Low
- **Location:** [file:line]
- **Issue:** [what's wrong]
- **Evidence:** [code snippet or pattern found]
- **Fix:** [what needs to change]
```

---

## Future Dimension: Test Verification (Not Yet Active)

**Agent:** `test-verifier` (placeholder -- do not spawn)
