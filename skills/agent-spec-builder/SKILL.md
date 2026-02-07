---
name: agent-spec-builder
description: Design agent systems through collaborative discovery and produce specifications for implementation. Acts as a design consultant - brainstorms with users, asks questions, and produces specs detailed enough for agent-impl-builder to work autonomously. Use when starting a new agent or agent team project.
allowed-tools: Read, Glob, Grep, Task, AskUserQuestion
---

# Agent Spec Builder Skill

## Purpose

A design consultant skill that helps users design agent systems through collaborative discovery. The spec is an output from consulting, brainstorming, and planning with the user - not a form to fill out.

**Goal:** Produce specifications detailed enough for agent-impl-builder to work autonomously.

---

## When to Use This Skill

Use this skill when:
- Starting a new agent or agent team project
- User needs help thinking through an agent system design
- Capturing requirements before implementation

**Skip this skill when:**
- Implementing an existing specification (use agent-impl-builder instead)
- Only modifying prompts (use prompt-engineering directly)

---

## Key Principles

1. **Design consultant, not form-filler** — Brainstorm with user, ask questions, help them think through their system
2. **First question: Single agent or agent team?** — Not everything needs a multi-agent system
3. **Always ask framework preference** — NEVER assume LangGraph or DSPy. Even if existing code uses one framework, the user may want to use the other for the new system. Ask explicitly.
4. **Incremental, top-down** — High-level first, then granular details
5. **Progress tracking** — Maintain progress document for handover between sessions
6. **User approval required** — Before handoff to agent-impl-builder
7. **Ask when unsure** — Never guess. If unclear about requirements, APIs, or approach, ask the user
8. **Context-conscious loading** — Load child skills one at a time, only at the phase that needs them. Never invoke multiple skills preemptively. Persist all decisions to progress.md before moving to the next phase so a new session can resume without re-reading everything.

---

## When to Ask for Feedback

**Always ask the user when:**
- **Framework choice (LangGraph vs DSPy)** — NEVER default based on existing codebase. Always ask explicitly, even if other agents in the repo use a specific framework.
- Unsure which API/library to use for a tool
- Multiple valid approaches exist (present options)
- Requirements are ambiguous
- You need to make assumptions
- Tool documentation is unclear or missing
- You're not confident about a design decision

**How to ask:**
> "I'm not sure about [specific thing]. Could you clarify [specific question]?"
> "I found multiple options for [tool/approach]. Which would you prefer: [Option A] or [Option B]?"
> "The documentation for [API] doesn't specify [detail]. Do you know how this works?"

**Never:**
- **Assume framework choice** — Do not default to LangGraph or DSPy based on existing codebase patterns. Always ask.
- Guess at API endpoints or authentication methods
- Assume tool implementations without verification
- Make design decisions without user input when multiple valid options exist
- Leave vague specifications that will cause impl-builder to guess

---

## Child Skills (Just-in-Time Loading)

**CONTEXT BUDGET RULE: Only invoke ONE child skill at a time, and ONLY when you reach the phase that needs it.** Loading all skills upfront will exhaust the context window and cause session failure.

| Skill | Invoke At | What It Provides |
|-------|-----------|------------------|
| `tools-and-utilities` | Phase 1, Section 6 (Tools) | Tool vs utility decision tree, design patterns |
| `agent-teams` | Phase 2 (Pattern Selection) | Team patterns (pipeline, router, loop, fan-out), selection criteria |
| `individual-agents` | Phase 3 (Agent Types) | Agent type definitions (LLM, Tool, Router, etc.), selection criteria |
| `prompt-engineering` | Phase 3 (Prompt Config) | Prompt frameworks, roles, modifiers reference |

**How to invoke (one at a time):**
```
Skill tool → skill: "agent-teams"
```

**Loading rules:**
1. DO NOT invoke any child skill until you reach the phase that requires it
2. Before invoking a child skill, update progress.md with ALL decisions made so far
3. After completing the phase that used a child skill, update progress.md with all new decisions before proceeding
4. If context is getting large, trigger the Handover Protocol BEFORE loading the next skill

**Why just-in-time:** Each child skill loads substantial reference material (hundreds to thousands of lines). Loading all four at once consumes ~15,000+ lines of context, leaving insufficient room for the actual design work and user conversation.

---

## Sub-Agents for Delegation

Child skills load into YOUR context window. Sub-agents run in their OWN context window and auto-load their own skills. Use sub-agents to offload analysis that requires skill knowledge without consuming your context budget.

### Available Sub-Agents

| Sub-Agent | What It Does | Auto-Loads | When to Use | Model |
|-----------|-------------|------------|-------------|-------|
| `agent-type-advisor` | Analyzes agents, proposes types with reasoning | `individual-agents` | Phase 3a — agent type analysis | Opus |
| `prompt-config-advisor` | Analyzes agents, proposes prompt configs with reasoning | `prompt-engineering` | Phase 3b — prompt config analysis (AFTER types validated) | Opus |
| `team-spec-writer` | Writes team.md and agent-config.yaml with agent placeholders | `agent-teams` | Phase 3c — team spec writing (AFTER all decisions validated) | Opus |
| `agent-spec-writer` | Writes complete agent spec files from validated decisions | `individual-agents`, `prompt-engineering` | Phase 3d — agent spec writing (fills in placeholders from team-spec-writer) | Opus |

**Phase 3 execution flow:**
1. **Spawn agent-type-advisor** for all agents → returns proposals → present table to user → user validates → save to progress.md
2. **Spawn prompt-config-advisor** (can batch large teams) → returns proposals → present table to user → user validates → save to progress.md
3. **Spawn team-spec-writer** → writes team.md, agent-config.yaml, and agent placeholder files → confirms completion
4. **Spawn agent-spec-writer** (5-6 in parallel per batch) → fills in agent spec files → confirms completion

**Batching strategy for agent-spec-writer:**
- **1-3 agents:** One spec-writer for all
- **4-8 agents:** One spec-writer per 2-3 agents (spawn multiple in parallel)
- **9+ agents:** One spec-writer per agent (spawn up to 5-6 in parallel per batch, then next batch)

All advisors run sequentially (type → prompt config). Then team-spec-writer creates structure. Then agent-spec-writers fill in details (can run in parallel).

### How Sub-Agents Work

1. You spawn the sub-agent via the Task tool with `subagent_type` set to the agent name
2. The sub-agent auto-loads its skill (in its own context — costs you nothing)
3. It reads reference files it needs (template, progress.md, type reference files)
4. It returns structured proposals/output back to you
5. You present the proposals to the user for validation
6. You write the validated decisions to spec files and progress.md

### Before Spawning Advisors

**CRITICAL: Before spawning any advisor sub-agents, ensure progress.md is completely up to date with:**
1. All Phase 1 discovery findings captured
2. Phase 2 results: team pattern selected, flow diagram, agent roster with purposes and key tasks
3. All decisions made with reasoning
4. Tool needs identified (even if tools aren't fully specified yet)
5. Any constraints or requirements that will inform type/prompt selection

The advisors will read progress.md as their authoritative source. If progress.md is incomplete, their proposals will be incomplete.

### Step 1: Spawn agent-type-advisor (all agents)

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
- Progress file: [path to spec/progress.md] — PRIMARY SOURCE for all decisions and context
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
2. **Present to the user in table format** (the advisor returns a summary table - show it):
   ```
   | Agent | Proposed Type | Tools | Multi-turn | Reasoning | Structured Output | Confidence |
   |-------|--------------|-------|------------|-----------|-------------------|------------|
   | [agent data from advisor's summary table]
   ```
3. Ask the user: "Here are the proposed agent types based on the individual-agents skill criteria. Do you agree with these selections, or would you like to adjust any?"
4. If user requests changes, capture both the original proposal AND the user's decision with reasoning
5. Write validated types, LLM configs, and capability flags to progress.md
6. Update agent spec files with the frontmatter (type, framework, reference) and LLM Configuration sections
7. THEN proceed to Step 2

### Step 2: Spawn prompt-config-advisor (can batch)

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
- Progress file: [path to spec/progress.md] — PRIMARY SOURCE for validated agent types and all decisions
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

### Step 3: Spawn team-spec-writer

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
- Progress file: [path to spec/progress.md]
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

### Step 4: Spawn agent-spec-writer (can parallelize)

**When:** AFTER both type and prompt config are validated and saved to progress.md.

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
- Progress file: [path to spec/progress.md]
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

**Key rules for spawning sub-agents:**
1. **Give it the progress.md path** — contains all validated decisions and project context
2. **Give it the discovery document path** — if it exists, always include for full problem context
3. **Give it all validated decisions** — type, prompt config, LLM config, capability flags
4. **Give it enough agent detail** — purpose, key tasks, upstream/downstream connections
5. **Give it the output path** — where to write the spec file
6. **Sub-agents cannot talk to the user** — they write files and confirm completion

---

## Workflow Overview

```
Setup → Discovery → High-Level Design → Agent Detail (per agent) → Finalize Spec → Execution Plan
```

**Incremental write pattern:** At each phase, the cycle is:
1. **Load** the skill needed for this phase (one at a time)
2. **Discuss** with the user — present options, ask questions, get decisions
3. **Write** the spec output for this phase (don't accumulate — write it NOW)
4. **Save** everything to progress.md — decisions, reasoning, thoughts, context
5. **Advance** to the next phase (or handover if context is getting large)

**Critical rule:** Write spec files at each phase, not all at the end. By the time you finish a phase, the corresponding spec sections should exist on disk. Progress.md must capture enough detail (including reasoning and thought process) that a new session can resume without re-discussing anything.

---

## Phase 0: Setup

**First actions:**

1. **Ask the user:**
   - "Are you creating a new project folder, or adding a spec to an existing project?"

2. **If creating new project:**
   - Ask: "What should the project folder be called?"
   - Create: `[project-name]/spec/`
   - Initialize `manifest.yaml` and `progress.md` from templates

3. **If existing project:**
   - Ask: "What's the path to the existing project folder?"
   - Create: `[project-path]/spec/`
   - Initialize `manifest.yaml` and `progress.md` from templates

4. **If resuming work:**
   - Read `spec/progress.md` FIRST — this is the authoritative state document
   - Review: Current Phase, Decisions Made, Discovery Substance, Open Questions, Next Steps
   - Read `spec/manifest.yaml` only if progress.md references spec files that exist
   - DO NOT re-read discovery documents, handover messages, or other source material already summarized in progress.md
   - DO NOT invoke any child skills until you reach a phase that needs them
   - Resume from the exact point described in "Next Steps" and "Resumption Instructions"
   - If progress.md indicates a phase is partially complete, read only the specific child skill needed for that phase

**Do not proceed until the project folder and spec directory are confirmed.**

**Directory structure:**
```
project-name/
└── spec/
    ├── manifest.yaml      # Entry point - read this first
    ├── progress.md        # Handover tracking
    └── [team-name]/       # Team folder (self-contained)
        ├── team.md
        ├── agent-config.yaml
        └── agents/
            └── [agent].md
```

The progress document tracks:
- Current phase
- Decisions made (with rationale)
- Discovery findings
- Design overview
- Per-agent progress
- Open questions
- Next steps

**Update this document throughout the process.**

---

## Phase 1: Discovery

**Purpose:** Understand the problem thoroughly before designing.

Cover these 8 areas:

### 1. Problem & Purpose
- What problem does this solve?
- Why does this need an agent (vs traditional code)?
- What does success look like?

### 2. Current State & Constraints
- What exists today?
- Technical constraints (APIs, latency, cost)?
- Organizational constraints (compliance, approvals)?

### 3. Interaction Mode

| Mode | Description | Implications |
|------|-------------|--------------|
| **User-facing** | Human interacts directly | Conversational tone, handle ambiguity, explain reasoning |
| **Autonomous** | Receives request, processes, returns result | Structured I/O, clear error handling, logging |
| **Agent-facing** | Called by another agent/team | Strict schemas, predictable behavior, fast responses |

### 4. Journey Mapping
- User journey (if user-facing)
- Agent journey (decision points, branches)
- System flow (data flow, integrations)

### 5. Inputs & Outputs
- What triggers this agent/team?
- What does it produce?
- Format requirements?

### 6. Integrations & Tools

**When you reach this section:** Invoke `skill: "tools-and-utilities"` to load the tool vs utility decision framework.

**Before invoking:** Ensure progress.md is updated with all Discovery findings from Sections 1-5.
**After completing this section:** Update progress.md with all tool decisions, implementation approaches, and dependency information before proceeding to Phase 2.

**Purpose:** Capture enough detail about each tool that the implementation builder can create working code WITHOUT guessing.

**Critical principle:** The impl-builder should NEVER have to invent an API or library. The spec must provide:
- Exact API/library to use
- Link to documentation
- Authentication details
- Example requests/responses

---

#### Step 1: Identify What Tools Are Needed

Ask the user:
- What external data does this agent need to fetch?
- What actions does this agent need to take?
- What systems does it need to integrate with?

---

#### Step 2: For Each Tool, Determine Implementation Approach

| Implementation | When to Use | Key Question |
|----------------|-------------|--------------|
| **MCP Server** | Functionality already exists as MCP server | "Is there an MCP server for this?" |
| **Existing API** | Third-party API available | "What API provides this data/action?" |
| **SDK/Library** | Python library available | "Is there a Python package for this?" |
| **Custom Function** | No existing solution | "What logic needs to be built?" |

---

#### Step 3: Get or Research the Specific Implementation

**Ask the user first:**
> "Do you know what API or library we should use for [tool purpose]?"

**If user knows:** Capture the details (see format below).

**If user doesn't know:** Use web-researcher to find options.

```
Task tool → subagent_type: "web-researcher"
Prompt: "I need to [tool purpose]. Research the best options:
1. Are there any MCP servers that provide this?
2. What APIs are available? (include: base URL, auth method, pricing)
3. What Python libraries can do this? (include: package name, GitHub stars, last updated)
Provide pros/cons for each option with links to documentation."
```

**Present options to user:**
> "I found these options for [tool purpose]:
> 1. **[Option A]** - [pros/cons] - [doc link]
> 2. **[Option B]** - [pros/cons] - [doc link]
> Which would you like to use?"

---

#### Step 4: Capture Full Implementation Details

**For MCP Server:**
- Server name (e.g., `@anthropic/mcp-server-github`)
- Tool name within server
- How to configure (env vars, config file)
- Link to MCP server documentation

**For Existing API:**
- Documentation URL (REQUIRED)
- Base URL
- Endpoint path and HTTP method
- Authentication method (API key, OAuth, none)
- How to obtain credentials
- Rate limits
- Request format with example
- Response format with example
- Error codes and handling
- Pagination (if applicable)

**For SDK/Library:**
- Package name (`pip install X`)
- Documentation URL (REQUIRED)
- Version constraints (if any)
- Import statement
- Key method(s) to use with signatures
- Example usage code
- Common errors and handling

**For Custom Function:**
- What it needs to do (detailed description)
- Input/output format
- Dependencies (packages, other tools)
- Algorithm or pseudocode
- Edge cases to handle

---

#### Step 5: Validate Understanding

Before moving on, confirm with user:
> "For the [tool name] tool, I'll specify:
> - Implementation: [type]
> - Using: [API/library name]
> - Documentation: [link]
> - Auth: [method]
> Does this look correct?"

---

#### Tool Discovery Questions Summary

| Question | Purpose |
|----------|---------|
| What external data/actions are needed? | Identify tool needs |
| Do you know what API/library to use? | Get user input first |
| Should I research options? | Trigger web-researcher |
| Which option do you prefer? | User selects approach |
| How do you authenticate? | Capture auth details |
| Do you have API keys already? | Understand setup needs |

**If unsure about any tool details, ASK the user or RESEARCH before proceeding. Never leave tool specifications vague.**

---

#### Step 6: Aggregate Dependencies

After specifying all tools, compile the project-level dependencies:

**Python Packages:**
- Collect all packages from tool specs
- Include framework packages (langgraph, langchain-anthropic, etc.)
- Note version constraints if specified in docs

**Environment Variables:**
- List all API keys and secrets needed
- Include instructions for obtaining each (signup URL, dashboard location)
- Note which tool/agent requires each variable

**External Services:**
- What services need to be running/available?
- MCP servers that need to be configured
- Databases, message queues, etc.

**Questions to ask:**
> "Do you already have API keys for [service], or do you need to set those up?"
> "Are there any other services this needs to connect to that we haven't discussed?"

**Record in team.md** under the Dependencies section.

### 7. Complexity & Reliability
- Expected volume/scale?
- Error tolerance?
- Retry/fallback needs?

### 8. LLM Configuration
- Same model for all agents, or different per agent?
- Provider preferences (Anthropic, OpenAI, Google, local)?
- Reasoning models needed? (for complex decision-making)
- Cost constraints? (affects model choice)
- Latency requirements? (smaller models for speed)
- Any compliance requirements? (data residency, no external APIs)

| Consideration | Questions to Ask |
|---------------|------------------|
| **Uniformity** | All agents same model, or specialized per task? |
| **Provider** | Anthropic, OpenAI, Google, local/self-hosted? |
| **Reasoning** | Need chain-of-thought? Extended thinking? |
| **Cost** | Budget constraints? Token limits? |
| **Latency** | Real-time needs? Async acceptable? |
| **Compliance** | Data privacy? On-prem requirements? |

**After Discovery:** Update progress document with findings.

---

## Phase 2: High-Level Design

**Purpose:** Evaluate discovered problem, map rough outline.

### First Decision: Single Agent or Agent Team?

```
Can one agent with tools handle this?
├── YES → Single agent (multiple tools + long system prompt)
└── NO → Agent team
    └── Can one team handle this?
        ├── YES → Single team
        └── NO → Nested teams (teams of teams)
```

**Single agent signals:**
- One clear responsibility
- Tools can handle all external needs
- No complex coordination needed

**Agent team signals:**
- Multiple distinct responsibilities
- Different specialists needed
- Complex coordination/handoffs

### Detail Level by Scope

| Building | Details to Capture |
|----------|-------------------|
| Single agent | Role + inputs + outputs |
| Agent team | Role + inputs + outputs + names of potential agents |
| Agent system (teams of teams) | Overall output + what each team does + agents within |

### Pattern Selection

**When you reach this phase:** Invoke `skill: "agent-teams"` to load the pattern selection criteria.

**Before invoking:** Ensure progress.md has complete Discovery findings (all 8 areas) and the single-agent-vs-team decision.
**After completing pattern selection:** Update progress.md with the chosen pattern, rationale, agents identified, and flow diagram before proceeding to Phase 3.

Work WITH the user to select the pattern based on their coordination needs:

| Pattern | Key Signal |
|---------|------------|
| **Pipeline** | Sequential stages, each depends on previous |
| **Router** | Dynamic dispatch based on input |
| **Fan-in-fan-out** | Parallel independent work, then aggregation |
| **Loop** | Iterative refinement with feedback |

### Output Format

- **Terminal:** ASCII art diagram only
- **File:** Both Mermaid AND ASCII art

### Nested Systems Approach

1. Start high level (overall system purpose, outputs)
2. Go more granular (what does each team do?)
3. Work back up (fill in agents within teams)
4. Can be iterative / somewhat simultaneous

**After High-Level Design:** Update progress document with design overview and agents identified.

---

## Phase 3: Agent Detail

**When you reach this phase, load skills ONE AT A TIME:**

1. First, invoke `skill: "individual-agents"` — for agent type selection
   - Use this to determine types for all agents
   - Update progress.md with agent type decisions and rationale
   - Then proceed to prompt configuration for each agent

2. Then, invoke `skill: "prompt-engineering"` — for prompt configuration
   - Use this for framework, role, and modifier selection per agent
   - Update progress.md with prompt config decisions per agent

**Before invoking either skill:** Ensure progress.md has complete Phase 2 results (pattern, agents identified, flow diagram).

**Context check:** If context is becoming large after individual-agents, consider triggering a session handover BEFORE loading prompt-engineering. Progress.md should have enough state for a new session to load prompt-engineering fresh.

**Purpose:** Capture enough detail per agent for autonomous implementation.

**Key principle:** Teams are orchestration logic. Agents do the actual work. Agent specs must be detailed.

For each agent, capture:

### Purpose (6 items)

| Section | What to Capture |
|---------|-----------------|
| **Goal** | What outcome this agent achieves |
| **Approach** | How it achieves that outcome (high-level method) |
| **Primary Responsibility** | One sentence summary of core job |
| **Key Tasks** | Bulleted list of specific things it does |
| **Success Criteria** | What good output looks like (measurable) |
| **Scope Boundaries** | What this agent does NOT do |

### Framework & Role

Use the `prompt-engineering` skill (invoked above) for selection criteria.

**Framework:** Single-Turn vs Conversational
- Single-Turn: Discrete task, all info upfront, no dialogue
- Conversational: Multi-turn, context across turns, ongoing dialogue

**Role:** One of 8 roles
- Researcher, Critic-Reviewer, Router-Classifier, Creative-Generator
- Planner-Strategist, Summarizer-Synthesizer, Conversational-Assistant, Transformer-Formatter

Include reasoning for each choice.

### LLM Configuration

For each agent, determine the model configuration:

| Setting | Options | Considerations |
|---------|---------|----------------|
| **Provider** | anthropic / openai / google / local | API access, cost, compliance |
| **Model** | claude-3-5-sonnet, gpt-4-turbo, etc. | Capability vs cost tradeoff |
| **Reasoning** | Yes / No | Does this agent need extended thinking? |
| **Temperature** | 0.0 - 1.0 | Lower for consistency, higher for creativity |

**Questions to ask:**
> "Should this agent use a smaller/faster model, or does it need the most capable one?"
> "Does this agent need reasoning capabilities (chain-of-thought, extended thinking)?"
> "Any cost constraints that affect model choice?"

**Default recommendations:**
- **Critic/Reviewer agents:** Higher capability model (needs nuanced judgment)
- **Router/Classifier agents:** Smaller/faster model (simple classification)
- **Creative agents:** May benefit from higher temperature
- **Structured output agents:** Lower temperature for consistency

**Record in agent spec** under LLM Configuration section with reasoning for each choice.

### Modifiers

| Modifier | What to Capture |
|----------|-----------------|
| **Tools** | Each tool: name, purpose, parameters, when to use, response format, error handling |
| **Structured Output** | Schema: field names, types, required/optional, example |
| **Memory** | None / Conversation History / Session State - what persists |
| **Reasoning** | None / CoT / CoV / Step-Back / ToT - which technique, why |

### Inputs & Outputs

For each input/output:
- Name
- Description
- Format
- Source (inputs) / Consumed by (outputs)

### Context Flow

Make explicit: Output of Agent A = Input of Agent B.

- **Upstream:** What agent sends data, what data, what format
- **Downstream:** What agent receives data, what data, what format

### Domain Context

- **Business Context:** What system/product this is part of
- **User Context:** Who interacts (if applicable)
- **Constraints:** Hard rules, compliance, limitations

### Behavioral Requirements

- **Key Behaviors:** Specific behaviors required
- **Edge Cases:** What could go wrong, how to handle
- **What NOT to do:** Explicit constraints

### Examples

At least one example showing:
- Sample input
- Expected output

### When to Split an Agent

Watch for signals that one agent is doing too much:
- Too many responsibilities
- Complex decision trees
- Multiple distinct outputs

Help user recognize when to split into multiple agents.

**After each agent:** Update progress document with agent progress checklist.

---

## Phase 4: Generate Spec

**Purpose:** Produce the specification files.

### Spec Folder Structure

**Single agent:**
```
project-name/
└── spec/
    ├── manifest.yaml        # Entry point for impl-builder
    ├── progress.md          # Handover document
    ├── agent-config.yaml    # Machine-readable config
    └── my-agent.md          # Agent spec
```

**Single team:**
```
project-name/
└── spec/
    ├── manifest.yaml        # Entry point for impl-builder
    ├── progress.md          # Handover document
    └── content-review-loop/
        ├── team.md          # Team overview
        ├── agent-config.yaml # This team's config
        └── agents/
            ├── creator.md   # Agent spec
            └── critic.md    # Agent spec
```

**Nested teams:**
```
project-name/
└── spec/
    ├── manifest.yaml        # Entry point for impl-builder
    ├── progress.md          # Handover document
    └── research-pipeline/   # Root team folder
        ├── team.md
        ├── agent-config.yaml # Root team config (references sub-teams)
        ├── content-refinement/
        │   ├── team.md
        │   ├── agent-config.yaml # Sub-team config
        │   └── agents/
        │       ├── creator.md
        │       └── critic.md
        └── parallel-research/
            ├── team.md
            ├── agent-config.yaml # Sub-team config
            └── agents/
                ├── researcher-a.md
                └── merger.md
```

**Key points:**
- Each team folder is self-contained with its own agent-config.yaml
- Agent specs live in `agents/` subdirectory within each team
- Sub-teams can be processed in parallel by impl-builder
- Use descriptive team names (not stage-1, stage-2)

### Files to Generate

**Root level (spec/):**

| File | Template | Purpose |
|------|----------|---------|
| `manifest.yaml` | `templates/manifest.yaml` | Entry point - hierarchy overview, file list |
| `progress.md` | `templates/progress.md` | Handover between sessions |

**Per team folder:**

| File | Template | Purpose |
|------|----------|---------|
| `team.md` | `templates/team.md` | Team overview and orchestration |
| `agent-config.yaml` | `templates/agent-config.yaml` | This team's configuration |
| `agents/{agent}.md` | `templates/agent.md` | Detailed spec for each agent |

**Critical:**
- `manifest.yaml` must be kept in sync with the spec structure
- Each team folder is self-contained with its own `agent-config.yaml`
- Agent specs go in `agents/` subdirectory within each team folder
- Sub-teams have their own folder with their own config
- After generating these files, proceed to **Phase 5: Execution Plan** to define implementation phasing

---

## Tools vs Utilities

| Level | What | Examples |
|-------|------|----------|
| **Agent tools** | Individual agent capabilities | Search API, database query, code execution |
| **Team utilities** | Shared integrations at team level | Teams webhook, WhatsApp API, email service |

---

## Phase 5: Execution Plan

**Purpose:** Define HOW the spec should be implemented — what can be done in parallel, what's sequential, and how agents should communicate.

After generating all spec files (Phase 4), produce an execution plan. This plan goes in **two places:**
1. **manifest.yaml** — Machine-readable `execution-plan` section (see template)
2. **progress.md** — Human-readable execution plan summary

### Step 1: List Implementation Tasks

For each team (including nested), identify the files that need to be created:
- `team.py` (scaffold, then full implementation)
- `tools.py` (if agents use tools)
- `prompts.py` / `signatures.py` (depending on framework)
- `utils.py` (if needed)
- `.env.example`
- `main.py` (FastAPI wrapper)

### Step 2: Group into Phases

Analyze dependencies to determine what can run in parallel:

**LangGraph typical execution plan:**
```
Phase 1 — Scaffold + Foundation (parallel):
  Stream scaffold: team.py scaffold (orchestration + placeholders)
  Stream tools: tools.py (tool definitions)
  Skills: scaffold → [agent-teams, individual-agents], tools → [tools-and-utilities]

Phase 2 — Agent Implementation (parallel):
  Stream scaffold: Fill in agent implementation functions in team.py
  (If agents are independent, each can be a separate chunk)
  Skills: [individual-agents]

Phase 3 — Prompts (parallel):
  Stream prompts: One chunk per agent prompt (sub-agents can work in parallel)
  Skills: [prompt-engineering]

Phase 4 — Finalization (parallel):
  Stream scaffold: utils.py, .env.example, main.py
```

**DSPy typical execution plan:**
```
Phase 1 — Signatures + Tools (parallel):
  Stream signatures: signatures.py (all signature classes with docstrings)
  Stream tools: tools.py (tool functions)
  Skills: signatures → [prompt-engineering], tools → [tools-and-utilities]

Phase 2 — Utilities + Models (parallel):
  Stream scaffold: utils.py (singleton LM, formatters)
  Stream scaffold: models.py (Pydantic models if needed)

Phase 3 — Team Module:
  Stream scaffold: team.py (dspy.Module — needs everything above)
  Skills: [agent-teams, individual-agents]

Phase 4 — Finalization (parallel):
  Stream scaffold: .env.example, main.py
```

### Step 3: Define Work Streams

Group related chunks so the same agent handles them across phases:

| Stream | Typical Responsibility | Skills |
|--------|----------------------|--------|
| scaffold | Orchestration logic, utilities, service wrapper | agent-teams, individual-agents |
| tools | Tool implementation from spec documentation | tools-and-utilities |
| prompts/signatures | Agent prompt/signature creation | prompt-engineering |

### Step 4: Define Communication

What information needs to flow between streams:

| From | To | When | What |
|------|----|------|------|
| tools | scaffold | After Phase 1 | Tool function signatures and return types |
| scaffold | prompts | After Phase 2 | Agent function structures and state schemas |

### Step 5: Write to manifest.yaml

Populate the `execution-plan` section using the template format:
- `streams:` — work stream definitions with skills
- `phases:` — phase definitions with chunks
- `communication:` — inter-stream communication needs

---

## Output of This Skill

A complete specification folder containing:
1. `progress.md` — Handover document with all decisions and progress
2. `agent-config.yaml` — Machine-readable configuration
3. `team.md` — Team overview and orchestration
4. `{agent}.md` files — Detailed spec for each agent
5. `manifest.yaml` — System hierarchy + **execution plan** for implementation

This feeds into the `agent-impl-builder` skill.

---

## Handover Protocol

When context is getting large, a session is ending, or before loading a new child skill when context is already substantial:

### Mandatory Steps

1. **Update progress.md** with ALL state needed for a cold-start resume:
   - Current phase and exact position within the phase
   - Every decision made, with rationale (not just the choice)
   - Discovery substance — key facts, constraints, and requirements (not just labels)
   - User Q&A — capture important questions asked and user's answers
   - Tool decisions — exact API/library chosen, auth method, documentation links
   - Agent details — types, roles, prompt configs decided so far
   - Flow diagram (ASCII) if one was produced
   - Open questions that still need resolution
   - Exact next steps (which phase, which section, which agent)
   - Which child skill to load next (and ONLY that one)

2. **Verify self-sufficiency:** A new session reading ONLY progress.md (without the original discovery document, handover message, or user conversation) must be able to:
   - Understand the full project context
   - Know every decision made and why
   - Resume work at the exact right point
   - Know which child skill to load next (and ONLY that one)

3. **Tell the user:** "I've saved all progress to progress.md. A new session can resume by invoking the agent-spec-builder skill — it will read progress.md and continue from [exact next step]."

### When to Trigger Handover

- Before loading a child skill when context already contains another loaded child skill
- When you notice responses becoming degraded or truncated
- At natural phase boundaries (end of Discovery, end of High-Level Design, etc.)
- When the user indicates they want to pause

---

## Templates

All templates are in `templates/` folder:

| Template | Purpose |
|----------|---------|
| `templates/manifest.yaml` | Entry point for impl-builder (hierarchy + file list) |
| `templates/progress.md` | Progress and handover tracking |
| `templates/agent-config.yaml` | Configuration file with examples |
| `templates/team.md` | Team specification |
| `templates/agent.md` | Individual agent specification |

---

## References

- `agent-teams/SKILL.md` — Team pattern selection criteria
- `individual-agents/SKILL.md` — Agent type selection criteria
- `prompt-engineering/SKILL.md` — Prompt configuration (framework, role, modifiers)
