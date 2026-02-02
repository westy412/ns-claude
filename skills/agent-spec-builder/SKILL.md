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
3. **Incremental, top-down** — High-level first, then granular details
4. **Progress tracking** — Maintain progress document for handover between sessions
5. **User approval required** — Before handoff to agent-impl-builder
6. **Ask when unsure** — Never guess. If unclear about requirements, APIs, or approach, ask the user

---

## When to Ask for Feedback

**Always ask the user when:**
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
- Guess at API endpoints or authentication methods
- Assume tool implementations without verification
- Make design decisions without user input when multiple valid options exist
- Leave vague specifications that will cause impl-builder to guess

---

## Child Skills (MANDATORY)

**These skills are MANDATORY. You MUST invoke them using the Skill tool at the specified points.**

| Skill | When | What It Provides |
|-------|------|------------------|
| `agent-teams` | Phase 2 - Pattern Selection | Team patterns (pipeline, router, loop, fan-out), selection criteria |
| `individual-agents` | Phase 3 - Agent Types | Agent type definitions (LLM, Tool, Router, etc.), selection criteria |
| `prompt-engineering` | Phase 3 - Prompt Config | Prompt frameworks, roles, modifiers reference |
| `tools-and-utilities` | Section 6 - Tools & Utilities | Tool vs utility decision tree, design patterns |

**How to invoke:**
```
Skill tool → skill: "agent-teams"
```

**Why these are mandatory:**
- Without `agent-teams`: You'll choose wrong patterns or miss coordination options
- Without `individual-agents`: You'll misclassify agents or miss type-specific requirements
- Without `prompt-engineering`: Prompts will lack proper structure and role guidance
- Without `tools-and-utilities`: You'll confuse tools with utilities, miss organization patterns

**If you skip these skills, the spec will be incomplete and the impl-builder will fail.**

---

## Workflow Overview

```
Create Progress Doc → Discovery → High-Level Design → Agent Detail → Generate Spec
```

**Critical:** At each phase, update the progress document. This enables handover between sessions when context gets saturated.

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
   - Read `spec/manifest.yaml` for system overview
   - Read `spec/progress.md` to understand current state
   - Resume from there

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

**STOP. Use the Skill tool now: `skill: "tools-and-utilities"`**

This loads the tool vs utility decision framework and design patterns.

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

**STOP. Use the Skill tool now: `skill: "agent-teams"`**

This loads the pattern selection criteria. Work WITH the user to select the pattern based on their coordination needs:

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

**STOP. Use the Skill tool now:**
1. `skill: "individual-agents"` — for agent type selection
2. `skill: "prompt-engineering"` — for prompt configuration

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

---

## Tools vs Utilities

| Level | What | Examples |
|-------|------|----------|
| **Agent tools** | Individual agent capabilities | Search API, database query, code execution |
| **Team utilities** | Shared integrations at team level | Teams webhook, WhatsApp API, email service |

---

## Output of This Skill

A complete specification folder containing:
1. `progress.md` — Handover document with all decisions and progress
2. `agent-config.yaml` — Machine-readable configuration
3. `team.md` — Team overview and orchestration
4. `{agent}.md` files — Detailed spec for each agent

This feeds into the `agent-impl-builder` skill.

---

## Handover Protocol

When context gets saturated or session ends:

1. **Update progress.md** with current state
2. **Mark phase** (Discovery / High-Level Design / Agent Detail / Generate Spec)
3. **List open questions** that need resolution
4. **Define next steps** clearly

New session starts by reading `progress.md` to understand current state.

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
