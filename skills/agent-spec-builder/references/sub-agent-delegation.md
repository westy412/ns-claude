# Sub-Agent Delegation

Detailed guidance for spawning advisor and writer sub-agents during Phase 3 (Agent Detail). Sub-agents run in their own context windows via the Task tool, auto-load their skills, and return structured proposals for user validation. This is distinct from agent teams — these are lightweight delegates for focused analysis/writing tasks.

> **Generate every delegate prompt as a file via the generic `teammate-spawn` skill** (reviewable, and it enforces skill loading) — not an inline prompt. Teammates skim long inline prompts and skip loading their skills, then write wrong patterns. The spawn *mechanics* below are platform-specific; the prompt *content* and the rules in this section are not.

## Advisors vs Writers — rigor by fabrication risk

- **Advisors** (`agent-type-advisor`, `prompt-config-advisor`) propose *bounded choices* (a type from a fixed set, a role from 8, modifiers from a list) and every proposal is **user-validated** before anything is written. Low fabrication surface, human-checked immediately. → file-based prompt + required skill loading + roster/purpose context. **No** per-field gate — they run *before* the detail exists; they help produce it.
- **Writers** (`team-spec-writer`, `agent-spec-writer`) generate *substantive free-form detail* (behaviors, I/O, examples) into long files where a fabrication hides easily. → full complete-context handoff + the Pre-Writer Completeness Gate + the anti-fabrication rule below.

## Pre-Writer Completeness Gate (BLOCKING)

A writer fills missing detail by *fabricating* plausible-but-wrong content the end review may miss. So before spawning ANY writer for an agent, assert that agent's full detail is present in `progress.md` — this is exactly the per-agent checklist in `templates/progress.md` → "Agent Progress":

Purpose (all 6) · Framework & Role (+reasoning) · LLM Config · Modifiers · Inputs/Outputs · Context Flow (up+down) · Domain Context · Behavioral Requirements · ≥1 Example (in→out)

**Any blank → STOP. Do not spawn.** Capture the missing detail (ask the user, or pull from the discovery doc), record it in `progress.md`, then spawn. No empty field crosses the seam — an empty field is the fabrication trigger.

## Anti-Fabrication Rule (every writer prompt includes this verbatim)

> Write only from the provided files (`progress.md`, discovery, templates). Do NOT invent detail. If a required field is missing or ambiguous, do NOT guess — stop and report the gap to team lead (e.g. "BLOCKED: missing Inputs/Outputs for agent X"). A wrong-but-coherent spec is worse than a flagged gap.

Parent-relay backstop: if the gate misses something, the writer returns a structured BLOCKED result instead of fabricating; the lead resolves and re-spawns. No live peer-to-peer messaging is assumed — the writer reports at the end, the lead relays. This keeps the flow portable across both platforms.

---

## Available Sub-Agents

| Sub-Agent | What It Does | Auto-Loads | When to Use | Model |
|-----------|-------------|------------|-------------|-------|
| `agent-type-advisor` | Analyzes agents, proposes types with reasoning | `individual-agents` | Phase 3a — agent type analysis | Opus |
| `prompt-config-advisor` | Analyzes agents, proposes prompt configs with reasoning | `prompt-engineering` | Phase 3b — prompt config analysis (AFTER types validated) | Opus |
| `team-spec-writer` | Writes team.md and agent-config.yaml with agent placeholders | `agent-teams` | Phase 3c — team spec writing (AFTER all decisions validated) | Opus |
| `agent-spec-writer` | Writes complete agent spec files from validated decisions | `individual-agents`, `prompt-engineering` | Phase 3d — agent spec writing (fills in placeholders from team-spec-writer) | Opus |

## Phase 3 Execution Flow

1. **Spawn agent-type-advisor** for all agents → returns proposals → present table to user → user validates → save to progress.md
2. **Spawn prompt-config-advisor** (can batch large teams) → returns proposals → present table to user → user validates → save to progress.md
3. **Spawn team-spec-writer** → writes team.md, agent-config.yaml, and agent placeholder files → confirms completion
4. **Spawn agent-spec-writer** (5-6 in parallel per batch) → fills in agent spec files → confirms completion

## How Sub-Agents Work

1. You spawn the sub-agent via the Task tool with `subagent_type` set to the agent name
2. The sub-agent auto-loads its skill (in its own context — costs you nothing)
3. It reads reference files it needs (template, progress.md, type reference files)
4. It returns structured proposals/output back to you
5. You present the proposals to the user for validation
6. You write the validated decisions to spec files and progress.md

## Before Spawning Advisors

**CRITICAL: Before spawning any advisor sub-agents, ensure progress.md is completely up to date with:**
1. All Phase 1 discovery findings captured
2. Phase 2 results: team pattern selected, flow diagram, agent roster with purposes and key tasks
3. All decisions made with reasoning
4. Tool needs identified (even if tools aren't fully specified yet)
5. Any constraints or requirements that will inform type/prompt selection

The advisors will read progress.md as their authoritative source. If progress.md is incomplete, their proposals will be incomplete.

---

## Step 1: Spawn agent-type-advisor (all agents)

**When:** After Phase 2 is complete and progress.md is updated with the agent roster.

**Example spawn:**

```
Task tool → subagent_type: "agent-type-advisor"
Prompt:
"Analyze these agents and propose types for each one.

## Team Context
- Team pattern: [pipeline/router/loop/fan-in-fan-out]
- Framework: [dspy/langgraph]
- Team purpose: [what the team does overall]

## Agent Roster
[For EACH agent, provide:]

### [Agent Name]
- Purpose: [what this agent does]
- Key tasks: [specific things it does]
- Receives input from: [upstream agent or trigger]
- Sends output to: [downstream agent or final output]

## Reference Files
- Progress file: [path to spec-folder/progress.md at spec folder root] — PRIMARY SOURCE for all decisions and context
- Discovery document: [path to discovery file] — ALWAYS include if it exists for full problem context
- Agent template: ~/.claude/skills/agent-spec-builder/templates/agent.md

## Instructions
Read the progress file FIRST for all decisions and project context.
Read the discovery document for full problem context and requirements (always include if available).
Read the agent template to understand the spec structure your proposals will feed into.
Use the individual-agents skill (auto-loaded) to apply type selection criteria.
Return proposals for each agent with reasoning, LLM config recommendations, and capability flags."
```

**After it returns:**
1. Review the proposals yourself for obvious issues
2. **Run Model Tier Validation:** Cross-check each agent's proposed model tier against its role (see Post-Generation Validation Check 4 in `references/phase-4-generate-spec.md`). Flag contradictions before presenting to user.
3. **Present to the user in table format** (the advisor returns a summary table - show it):
   ```
   | Agent | Proposed Type | Tools | Multi-turn | Reasoning | Structured Output | Confidence |
   |-------|--------------|-------|------------|-----------|-------------------|------------|
   | [agent data from advisor's summary table]
   ```
4. Ask the user: "Here are the proposed agent types based on the individual-agents skill criteria. Do you agree with these selections, or would you like to adjust any?"
5. If user requests changes, capture both the original proposal AND the user's decision with reasoning
6. Write validated types, LLM configs, and capability flags to progress.md
7. Update agent spec files with the frontmatter (type, framework, reference) and LLM Configuration sections
8. THEN proceed to Step 2

---

## Step 2: Spawn prompt-config-advisor (can batch)

**When:** AFTER agent types are validated and saved to progress.md.

**Batching strategy for large teams:**
- **Small teams (1-5 agents):** One advisor for all agents
- **Medium teams (6-12 agents):** One advisor for all agents or split by role (e.g., research agents vs synthesis agents)
- **Large teams (13+ agents):** Split into batches of 5-8 agents. Spawn multiple advisors IN PARALLEL (one message with multiple Task tool uses), each handling a batch.

**Example spawn (single batch):**

```
Task tool → subagent_type: "prompt-config-advisor"
Prompt:
"Analyze these agents and propose prompt configurations for each one.

## Team Context
- Team pattern: [pipeline/router/loop/fan-in-fan-out]
- Framework: [dspy/langgraph]
- Team purpose: [what the team does overall]

## Agent Details (WITH VALIDATED TYPES)
[For EACH agent, provide:]

### [Agent Name]
- Purpose: [what this agent does]
- Key tasks: [specific things it does]
- Type (validated): [type from agent-type-advisor]
- Capability flags (from type analysis):
  - Needs tools: [yes/no]
  - Needs multi-turn: [yes/no]
  - Needs reasoning: [yes/no]
  - Needs structured output: [yes/no]
  - Needs memory: [yes/no]

## Reference Files
- Progress file: [path to spec-folder/progress.md at spec folder root] — PRIMARY SOURCE for validated agent types and all decisions
- Discovery document: [path to discovery file] — ALWAYS include if it exists for full problem context
- Agent template: ~/.claude/skills/agent-spec-builder/templates/agent.md

## Instructions
Read the progress file FIRST for validated agent types, capability flags, and all decisions.
Read the discovery document for full problem context and requirements (always include if available).
Read the agent template to understand the spec structure your proposals will feed into.
Use the prompt-engineering skill (auto-loaded) to apply framework, role, and modifier selection criteria.
Use the capability flags from the type analysis as strong signals for framework and modifier selection.
Return proposals for each agent with reasoning for framework, role, and modifier choices."
```

**For large teams spawning multiple advisors in parallel:**

Send one message with multiple Task tool uses. Example for a 16-agent team:

```
# Batch 1: Agents 1-8
Task tool → subagent_type: "prompt-config-advisor"
Prompt: [include agents 1-8 with their types and capability flags]

# Batch 2: Agents 9-16 (IN THE SAME MESSAGE)
Task tool → subagent_type: "prompt-config-advisor"
Prompt: [include agents 9-16 with their types and capability flags]
```

Both advisors run in parallel, each analyzing their batch. Merge the results when they return.

**After it returns:**
1. Review the proposals yourself for obvious issues
2. **Present to the user in table format** (the advisor returns a summary table - show it):
   ```
   | Agent | Framework | Role | Modifiers | Confidence |
   |-------|-----------|------|-----------|------------|
   | [agent data from advisor's summary table]
   ```
3. Ask the user: "Here are the proposed prompt configurations based on the prompt-engineering skill criteria. Do you agree with these selections, or would you like to adjust any?"
4. If user requests changes, capture both the original proposal AND the user's decision with reasoning
5. Write validated prompt configs to progress.md
6. THEN proceed to Step 3

---

## Step 3: Spawn team-spec-writer

**When:** AFTER both type and prompt config are validated and saved to progress.md.

**Example spawn:**

```
Task tool → subagent_type: "team-spec-writer"
Prompt:
"Write the team spec files for [team-name].

## Validated Decisions
- Pattern: [pipeline/router/loop/fan-in-fan-out]
- Framework: [langgraph/dspy]
- Pattern reference: [path to agent-teams/[framework]/[pattern].md]

## Agent Roster (with validated types and prompt configs)
[For EACH agent:]

### [Agent Name]
- Type: [validated type]
- Framework: [framework]
- Type reference: [path to individual-agents reference]
- Prompt framework: [single-turn/conversational]
- Prompt role: [role]
- Prompt modifiers: [list]
- LLM provider: [provider]
- LLM model: [model]
- Reasoning: [yes/no]
- Temperature: [value]
- Purpose: [brief description]
- Key tasks: [list]
- Receives input from: [upstream]
- Sends output to: [downstream]

## Reference Files
- Progress file: [path to spec-folder/progress.md at spec folder root]
- Discovery document: [path if exists]
- Team template: ~/.claude/skills/agent-spec-builder/templates/team.md
- Agent-config template: ~/.claude/skills/agent-spec-builder/templates/agent-config.yaml
- Output directory: [path to spec/[team-name]/]

## Instructions
Read all reference files.
Write team.md and agent-config.yaml following templates exactly.
Create agents/ directory with placeholder files (frontmatter only + TODO comment).
Use validated decisions - do not re-decide.
Pull orchestration details from the pattern reference file.
Confirm completion when done."
```

**After it returns:**
1. Verify team.md and agent-config.yaml were created
2. Verify agent placeholder files exist
3. Update progress.md to mark team spec as complete
4. THEN proceed to Step 4

---

## Step 4: Spawn agent-spec-writer (can parallelize)

**When:** AFTER team-spec-writer has created the structure.

**Batching strategy:**
- **1-3 agents:** One spec-writer for all
- **4-8 agents:** Spawn 2-3 spec-writers in parallel, each handling 2-3 agents
- **9+ agents:** Spawn 5-6 spec-writers in parallel (batch 1), then next batch after completion

**Example spawn (single agent):**

```
Task tool → subagent_type: "agent-spec-writer"
Prompt:
"Write the complete agent spec file for [agent-name].

## Validated Decisions (from user validation)
- Type: [type]
- Framework: [langgraph/dspy]
- Reference: [path to individual-agents reference file]
- Prompt framework: [single-turn/conversational]
- Prompt role: [role]
- Prompt modifiers: [list]
- LLM provider: [provider]
- LLM model: [model]
- Reasoning: [yes/no]
- Temperature: [value]

## Capability Flags (from type analysis)
- Needs tools: [yes/no - if yes, which tools from progress.md Tool Implementation Details]
- Needs multi-turn: [yes/no]
- Needs reasoning: [yes/no - if yes, technique]
- Needs structured output: [yes/no]
- Needs memory: [yes/no - if yes, what kind]

## Agent Purpose (from roster)
- Purpose: [what this agent does]
- Key tasks: [list]
- Receives input from: [upstream]
- Sends output to: [downstream]

## Reference Files
- Progress file: [path to spec-folder/progress.md at spec folder root]
- Discovery document: [path if exists]
- Output path: [path to write spec/[team-name]/agents/agent-name.md]

## Instructions
Read all reference files.
Write the complete agent spec following templates/agent.md exactly.
Use validated decisions - do not re-decide.
Pull purpose, context, behavioral requirements, and examples from progress.md and discovery doc.
For tools: use the Tool Implementation Details section from progress.md.
Confirm completion when done."
```

**For multiple agents in parallel:**

Send one message with multiple Task tool uses:

```
# Agent 1
Task tool → subagent_type: "agent-spec-writer"
Prompt: [agent 1 details]

# Agent 2 (IN THE SAME MESSAGE)
Task tool → subagent_type: "agent-spec-writer"
Prompt: [agent 2 details]

# ... up to 5-6 agents per batch
```

**After they return:**
1. Verify all spec files were created
2. Spot-check one or two files for template compliance
3. Update progress.md to mark agent specs as complete
4. Proceed to next phase (finalize manifest, execution plan)

---

## Key Rules for Spawning Sub-Agents

1. **Give it the progress.md path** — contains all validated decisions and project context
2. **Give it the discovery document path** — if it exists, always include for full problem context
3. **Give it all validated decisions** — type, prompt config, LLM config, capability flags
4. **Give it enough agent detail** — purpose, key tasks, upstream/downstream connections
5. **Give it the output path** — where to write the spec file
6. **Sub-agents cannot talk to the user** — they write files and confirm completion
