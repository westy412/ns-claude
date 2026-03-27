# Team Orchestration

> **When to read:** When setting up the verification team in Phase 1.

---

## Prerequisites

Before spawning the team:

1. **Spec folder identified** -- you have the path to `{workforce-root}/specs/YYYY-MM-DD-feature-name/`
2. **Spec file located** -- `{spec-folder}/spec.md` (general) or `{spec-folder}/spec/manifest.yaml` (agent)
3. **Progress file located** -- `{spec-folder}/progress.md`
4. **Both files read** -- you understand what was supposed to be built and what was built
5. **teammate-spawn skill loaded** -- invoke `Skill tool -> skill: "teammate-spawn"` before generating prompts

---

## Team Setup Sequence

### Step 1: Determine Scope

From the progress file, extract:
- **Completed files list** -- these are the files the code quality agent will review
- **Execution plan snapshot** -- this is what the completeness agent will verify against
- **Stream status** -- current state of all streams and chunks

From the spec, extract:
- **Requirements** -- what the spec compliance agent will verify
- **Acceptance criteria** -- what must be true
- **Architecture section** -- patterns and constraints to verify

### Step 2: Generate Teammate Prompts

Use the [verifier-teammate.md](../templates/verifier-teammate.md) template to generate 3 prompt files.

**Save location:** `{spec-folder}/teammate-prompts/`

Each prompt must include:
- The specific dimension and its checks (from [verification-dimensions.md](verification-dimensions.md))
- Paths to the spec and progress files
- The list of files to investigate (scoped per agent)
- Instructions to use `codebase-researcher` sub-agents
- The findings format to report back in

### Agent-Specific Scoping

| Agent | What files it needs to read | What it investigates |
|-------|---------------------------|---------------------|
| `spec-compliance-verifier` | Spec (requirements, acceptance criteria, architecture), progress file (deviations), all implemented files | Whether each requirement maps to working code |
| `completeness-verifier` | Spec (execution plan), progress file (stream status, completed files), file system | Whether all planned files and outputs exist |
| `code-quality-verifier` | Progress file (completed files list), all implemented source files | Code patterns, security, performance, maintainability |

### Step 3: Create Team and Tasks

```
1. TeamCreate: team name "verification-{spec-name}"

2. TaskCreate for each agent:
   - spec-compliance-verifier: "Verify all spec requirements and acceptance criteria are implemented"
   - completeness-verifier: "Verify all planned files, chunks, and phases exist and are populated"
   - code-quality-verifier: "Review implemented code for correctness, security, performance, maintainability, error handling"

3. Spawn all 3 agents in PARALLEL using the Agent tool:
   - Each agent reads its teammate prompt file
   - Each agent works independently
   - No dependencies between agents
```

### Step 4: Monitor

- Wait for all 3 agents to complete
- Each agent sends findings back via SendMessage to team-lead
- If an agent encounters an error (e.g., can't find files), it reports the error as a finding

### Step 5: Cleanup

After collecting all results:
1. Delete the team: `TeamDelete`
2. Remove teammate prompt files: `rm -rf {spec-folder}/teammate-prompts/`

---

## Agent Sub-Agent Delegation

Each verification agent should spawn `codebase-researcher` sub-agents for deep investigation. This keeps the verification agent's context clean and allows parallel investigation within each dimension.

**Pattern for spawning codebase-researcher:**

```
Agent tool:
  subagent_type: "codebase-researcher"
  prompt: "[Specific investigation task with file paths and what to look for]"
```

**Guidelines for sub-agent tasks:**
- Be specific about which files to examine
- Tell the sub-agent exactly what to look for
- Ask for file paths and line numbers in the response
- One sub-agent per focused investigation area (e.g., one for security review of API handlers, one for security review of auth middleware)
- Don't give a single sub-agent too many files -- split across multiple sub-agents if the file list is large

**Recommended sub-agent split for code-quality-verifier:**

| Sub-Agent | Focus |
|-----------|-------|
| Correctness researcher | Null handling, boundary conditions, logic errors |
| Security researcher | Injection, secrets, auth, XSS, data exposure |
| Performance researcher | N+1 queries, algorithms, memory leaks |
| Maintainability researcher | Duplication, complexity, naming, dependencies |
| Error handling researcher | Empty catches, unhandled promises, propagation |
| Type safety researcher | `any` types, runtime validation, assertions (TypeScript only) |

The code-quality-verifier spawns these in parallel, collects results, and synthesizes into its findings report.

---

## Communication Protocol

**Agents to team lead:**
- Each agent sends a single comprehensive findings message when complete
- Format: structured markdown following the findings format from [verification-dimensions.md](verification-dimensions.md)

**Team lead does NOT send instructions mid-investigation.** The teammate prompt file contains everything the agent needs.

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Spec file not found | Stop. Report error to user. Do not spawn team. |
| Progress file not found | Stop. Report error to user. Do not spawn team. |
| Agent can't find expected files | Agent reports as FAIL finding: "Expected file X does not exist" |
| Agent times out or errors | Team lead notes the dimension as INCOMPLETE in the report |
| Sub-agent returns no results | Agent flags the investigated area as INCONCLUSIVE |
