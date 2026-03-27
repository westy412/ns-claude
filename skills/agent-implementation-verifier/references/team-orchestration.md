# Team Orchestration

> **When to read:** When setting up the verification team in Phase 1.

---

## Prerequisites

Before spawning the team:

1. **Spec folder identified** -- you have the path to `{workforce-root}/specs/YYYY-MM-DD-feature-name/`
2. **Manifest located** -- `{spec-folder}/spec/manifest.yaml`
3. **Agent-config located** -- `{spec-folder}/spec/{team}/agent-config.yaml`
4. **Framework determined** -- DSPy or LangGraph (from agent-config.yaml)
5. **Progress file located** -- `{spec-folder}/progress.md`
6. **All files read** -- you understand the system hierarchy, agents, and what was built
7. **teammate-spawn skill loaded** -- invoke `Skill tool -> skill: "teammate-spawn"`

---

## Team Setup Sequence

### Step 1: Determine Scope

From the spec, extract:
- **System hierarchy** (from manifest.yaml) -- teams, sub-teams, agents
- **Agent configurations** (from agent-config.yaml) -- types, frameworks, models, prompt configs
- **Agent specs** (from {agent}.md files) -- I/O signatures, behavioral requirements
- **Execution plan** (from manifest.yaml) -- phases, chunks, communication contracts
- **Framework** -- DSPy or LangGraph

From the progress file, extract:
- **Completed files list** -- what exists on disk
- **Stream status** -- what was built per stream
- **Deviations** -- documented divergences from spec

### Step 2: Load Framework Checks

Based on the framework:
- **DSPy:** Read [framework-checks-dspy.md](framework-checks-dspy.md)
- **LangGraph:** Read [framework-checks-langgraph.md](framework-checks-langgraph.md)

This content will be included in the framework-compliance-verifier's teammate prompt.

### Step 3: Generate Teammate Prompts

Use the [verifier-teammate.md](../templates/verifier-teammate.md) template to generate 4 prompt files.

**Save location:** `{spec-folder}/teammate-prompts/`

### Agent-Specific Scoping

| Agent | What it reads | What it investigates |
|-------|--------------|---------------------|
| `spec-compliance-verifier` | manifest.yaml, agent-config.yaml, all agent spec .md files, implemented code | Agent types, models, prompts, I/O, team pattern, data flow match spec |
| `completeness-verifier` | manifest.yaml execution plan, progress.md, framework file layout rules, filesystem | All expected files exist, all phases complete, no stubs |
| `framework-compliance-verifier` | agent-config.yaml (framework), framework checks reference, all implemented source files | Framework patterns followed, anti-patterns absent, orchestration correct |
| `code-quality-verifier` | progress.md (completed files), all implemented source files | Correctness, security, performance, maintainability, error handling |

### Step 4: Create Team and Tasks

```
1. TeamCreate: team name "verification-{spec-name}"

2. TaskCreate for each agent:
   - spec-compliance-verifier: "Verify all agent types, model configs, prompt configs, I/O signatures, and team patterns match the spec"
   - completeness-verifier: "Verify all framework-specific files exist, all phases produced outputs, no stubs remain"
   - framework-compliance-verifier: "Verify [DSPy|LangGraph] framework patterns are followed and anti-patterns are absent"
   - code-quality-verifier: "Review implemented code for correctness, security, performance, maintainability, error handling"

3. Spawn all 4 agents in PARALLEL using the Agent tool
```

### Step 5: Monitor

- Wait for all 4 agents to complete
- Each agent sends findings back via SendMessage to team-lead
- If an agent encounters an error, it reports the error as a finding

### Step 6: Cleanup

After collecting all results:
1. Delete the team: `TeamDelete`
2. Remove teammate prompt files: `rm -rf {spec-folder}/teammate-prompts/`

---

## Agent Sub-Agent Delegation

Each verification agent should spawn `codebase-researcher` sub-agents for deep investigation.

**Recommended sub-agent split for framework-compliance-verifier:**

| Sub-Agent | Focus |
|-----------|-------|
| Pattern researcher | Two-file prompt pattern (DSPy) or prompts.py pattern (LangGraph) |
| Orchestration researcher | team.py structure, graph/module composition, team pattern |
| Data flow researcher | I/O field tracing across agents, State/Signature field matching |
| Anti-pattern researcher | Known bad patterns from the framework checks reference |

**Recommended sub-agent split for spec-compliance-verifier:**

| Sub-Agent | Focus |
|-----------|-------|
| Agent type researcher | Compare each agent's declared type to its implementation |
| Model config researcher | Verify model assignments, tiers, temperatures |
| I/O signature researcher | Trace all InputField/OutputField or State fields against spec |
| Prompt config researcher | Verify prompt roles and modifiers match agent-config.yaml |

---

## Communication Protocol

Same as general verifier: agents send a single comprehensive findings message when complete. Team lead does NOT send instructions mid-investigation.

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Manifest not found | Stop. Report error to user. Do not spawn team. |
| Progress file not found | Stop. Report error to user. Do not spawn team. |
| Agent-config.yaml not found | Stop. Report error to user. Do not spawn team. |
| Framework not recognized | Stop. Report error. Only `dspy` and `langgraph` are supported. |
| Agent can't find expected files | Agent reports as FAIL finding |
| Agent times out | Team lead notes the dimension as INCOMPLETE |
