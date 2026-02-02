---
name: agent-impl-builder
description: Transform agent specifications into production code. Takes agent-spec-builder output and generates team orchestration, agents, prompts, and tools. Use when you have a complete specification and are ready to implement.
allowed-tools: Read, Glob, Grep, Task, Write, Edit, Bash
---

# Agent Implementation Builder Skill

## Purpose

An implementation skill that transforms agent specifications into production code. Takes the output from agent-spec-builder and generates working code with proper structure.

**Goal:** Autonomous code generation from specifications.

---

## When to Use This Skill

Use this skill when:
- You have a complete specification from agent-spec-builder
- Ready to generate production code
- Implementing an agent or agent team from scratch

**Skip this skill when:**
- Still gathering requirements (use agent-spec-builder instead)
- Only modifying prompts (use prompt-engineering directly)
- Debugging existing agents (use agent-debugger when available)

---

## Key Principles

1. **Spec-driven** — All implementation decisions come from the spec
2. **Task-based execution** — Break spec into discrete tasks with dependencies
3. **Parallel where possible** — Spawn sub-agents for independent work (e.g., prompts)
4. **Reference-guided** — Use pattern references from agent-config.yaml
5. **Only create what's needed** — Don't generate empty files
6. **Framework cheat sheets first** — Read framework rules before writing code
7. **Ask when unsure** — Never guess. If spec is unclear or documentation is missing, ask the user

---

## When to Ask for Feedback

**Always ask the user when:**
- Spec is missing required information (especially tool documentation links)
- API documentation doesn't match what spec describes
- Multiple implementation approaches are valid
- You encounter errors or unexpected behavior
- Spec seems incomplete or contradictory
- You're about to make an assumption not in the spec

**How to ask:**
> "The spec for [tool] doesn't include a documentation link. What API/library should I use?"
> "I found two ways to implement [feature]: [A] or [B]. Which do you prefer?"
> "The API documentation shows [X] but the spec says [Y]. Which is correct?"
> "I'm not confident about [specific implementation detail]. Can you clarify?"

**Never:**
- Invent APIs or endpoints not in the spec
- Guess at authentication methods
- Create placeholder tools that don't work (like "API integration required")
- Proceed with implementation when critical information is missing

---

## Framework Cheat Sheets

**CRITICAL: Read the framework cheat sheet BEFORE writing any code.**

Cheat sheets contain critical rules, patterns, and anti-patterns for each framework. They prevent common mistakes that are hard to debug.

| Framework | Cheat Sheet Location |
|-----------|---------------------|
| LangGraph | `frameworks/langgraph/CHEATSHEET.md` |
| DSPy | `frameworks/dspy/CHEATSHEET.md` |

**What cheat sheets contain:**
- **Critical Rules** — Things you MUST do / MUST NOT do
- **Common Patterns** — Quick reference for key patterns
- **Anti-patterns** — What NOT to do with examples of wrong code

**Example critical rule (LangGraph):**
> ToolNode MUST be added to the graph as a separate node. NEVER create ToolNode inside agent functions or manually invoke it.

**When to read:**
1. At the start of implementation (Phase 0)
2. Before implementing any tool-using agents
3. When combining patterns (e.g., router + tools)

---

## Child Skills (MANDATORY)

**These skills are MANDATORY. You MUST invoke them using the Skill tool at the specified points.**

| Skill | When | What It Provides |
|-------|------|------------------|
| `agent-teams` | Phase 1 - Team Scaffold | Team orchestration patterns, graph structure examples |
| `individual-agents` | Phase 3 - Agent Implementations | Agent implementation patterns per type |
| `prompt-engineering` | Phase 4 - Prompts | Invoked by prompt-creator sub-agent |
| `tools-and-utilities` | Phase 2 - Tools & Utilities | Tool implementation patterns, utility organization |

**How to invoke:**
```
Skill tool → skill: "agent-teams"
```

**Why these are mandatory:**
- Without `agent-teams`: You'll implement wrong orchestration patterns
- Without `individual-agents`: You'll miss type-specific implementation details
- Without `tools-and-utilities`: You'll create broken tools or misplace utilities

**If you skip these skills, the implementation will be incorrect or incomplete.**

---

## Input

Spec folder from agent-spec-builder:

**Single agent:**
```
project-name/
└── spec/
    ├── manifest.yaml        # ENTRY POINT - read this first
    ├── progress.md          # Design decisions and context
    ├── agent-config.yaml    # Machine-readable configuration
    └── my-agent.md          # Agent spec
```

**Single team:**
```
project-name/
└── spec/
    ├── manifest.yaml        # ENTRY POINT - read this first
    ├── progress.md
    └── content-review-loop/ # Team folder (self-contained)
        ├── team.md
        ├── agent-config.yaml # This team's config
        └── agents/
            ├── creator.md
            └── critic.md
```

**Nested teams:**
```
project-name/
└── spec/
    ├── manifest.yaml        # ENTRY POINT - hierarchy + file list
    ├── progress.md
    └── research-pipeline/   # Root team folder
        ├── team.md
        ├── agent-config.yaml # Root team config
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

**manifest.yaml provides:**
- System type (single-agent, agent-team, nested-teams)
- Hierarchy visualization
- Complete file list
- Parallel groups for implementation (sub-teams can run in parallel)

---

## Output

Production code - mirrors spec structure, each team folder is self-contained:

**Single agent:**
```
project-name/
├── pyproject.toml           # Project config + dependencies (managed by uv)
├── uv.lock                  # Lockfile (managed by uv)
├── .env.example             # Required environment variables
└── src/
    ├── agent.py             # Agent implementation
    ├── prompts.py           # Agent prompt
    └── tools.py             # Tools (if needed)
```

**Single team:**
```
project-name/
├── pyproject.toml           # Project config + dependencies (managed by uv)
├── uv.lock                  # Lockfile (managed by uv)
├── .env.example             # Required environment variables
└── src/
    └── content-review-loop/
        ├── team.py          # Orchestration + agents
        ├── prompts.py       # Agent prompts
        ├── tools.py         # Tool definitions (if needed)
        └── utils.py         # Utilities (if needed)
```

**Nested teams:**
```
project-name/
├── pyproject.toml           # Project config + dependencies (managed by uv)
├── uv.lock                  # Lockfile (managed by uv)
├── .env.example             # Required environment variables
└── src/
    └── research-pipeline/
        ├── team.py          # Top-level orchestration
        ├── content-refinement/
        │   ├── team.py
        │   ├── prompts.py
        │   ├── tools.py
        │   └── utils.py
        └── parallel-research/
            ├── team.py
            ├── prompts.py
            ├── tools.py
            └── utils.py
```

**Only create files if the team needs them.**

---

## Workflow

### Phase 0: Parse Spec and Initialize Project

**Step 1:** Read `spec/manifest.yaml` — this is your entry point.

The manifest provides:
1. **System type** — single-agent, agent-team, or nested-teams
2. **Hierarchy** — visual structure of teams and agents
3. **File list** — all spec files to read
4. **Implementation order** — suggested sequence

**Step 2:** Read `agent-config.yaml` for detailed configuration, including:
- Framework being used (langgraph, dspy)
- Agent types
- Tool requirements

**Step 3: READ THE FRAMEWORK CHEAT SHEET.**

Based on the framework in agent-config.yaml, read the corresponding cheat sheet:
- LangGraph → `frameworks/langgraph/CHEATSHEET.md`
- DSPy → `frameworks/dspy/CHEATSHEET.md`

**This step is CRITICAL.** The cheat sheet contains rules that prevent common implementation mistakes.

**Step 4:** Read individual spec files as needed.

**Step 5: Initialize project with uv.**

```bash
# Navigate to project directory
cd [project-name]

# Initialize uv project (if not already initialized)
uv init

# Create src directory structure
mkdir -p src/[team-name]
```

**Step 6: Add core dependencies.**

Read dependencies from `team.md` → Dependencies section and add them:

```bash
# Core framework dependencies
uv add langgraph langchain-anthropic

# Tool dependencies (from spec)
uv add httpx beautifulsoup4 youtube-transcript-api
```

**Add dependencies as you identify them from the spec.** Don't wait until the end.

**Step 7: CREATE the progress document.**

This is CRITICAL. Create `progress.md` in the project root BEFORE starting implementation.

1. **Read the template:** `agent-patterns/agent-implementation-builder/templates/progress.md`
2. **Create progress.md** in project root
3. **Populate with ALL tasks** derived from the spec:

For each team (including nested), add these tasks:
- Create team.py scaffold
- Create tools.py (if team has tool-using agents)
- Implement each agent (one task per agent, named)
- Create prompts (one task per agent, named)
- Create utils.py (if needed)
- Create .env.example

**Example progress.md content:**

```markdown
# YouTube Summarizer - Implementation Progress

## Status

**Current Phase:** Phase 0 - Setup
**Last Updated:** 2025-01-10
**Spec Location:** spec/

---

## Tasks

| Task | Status | Dependencies | Assigned To | Notes |
|------|--------|--------------|-------------|-------|
| team.py scaffold | pending | - | agent-impl-builder | |
| tools.py | pending | scaffold | agent-impl-builder | youtube-transcript-api |
| Implement fetcher | pending | tools.py | agent-impl-builder | |
| Implement summarizer | pending | tools.py | agent-impl-builder | |
| Prompt: fetcher | pending | fetcher impl | prompt-creator | |
| Prompt: summarizer | pending | summarizer impl | prompt-creator | |
| .env.example | pending | - | agent-impl-builder | |

**Status values:** pending | in_progress | done | blocked | skipped
```

4. **Update progress.md as you work** — mark tasks in_progress when starting, done when complete

**The progress document is your task list.** Refer to it before each phase to know what to do next.

### Phase 1: Team Scaffold

**STOP. Use the Skill tool now: `skill: "agent-teams"`**

This loads the team pattern implementation guides.

Create team.py with:
- Orchestration logic based on pattern (pipeline, router, fan-in-fan-out, loop)
- Placeholder functions for each agent

```python
# team.py scaffold example

async def creator(state: State) -> State:
    """Creator agent - generates initial content."""
    pass

async def critic(state: State) -> State:
    """Critic agent - reviews and provides feedback."""
    pass

# Orchestration logic here...
```

**Reference:** Use pattern file from `agent-config.yaml → team → reference`
- e.g., `agent-patterns/agent-teams/langgraph/loop.md`

### Phase 2: Tools

**STOP. Use the Skill tool now: `skill: "tools-and-utilities"`**

This loads the tool implementation patterns and utility function organization guidance.

Create tools.py with tool definitions from agent specs.

**Critical:** The spec provides documentation links. You MUST read the actual API/SDK documentation to create working tools.

For each agent that has tools:

1. **Read agent spec** (e.g., `creator.md`)
2. **Extract tool definitions** from Modifiers → Tools section
3. **For each tool, based on implementation type:**

**MCP Server:**
- Configure MCP server connection
- Use the specified tool name

**Existing API:**
- Read the documentation URL from spec
- Use `WebFetch` or `web-researcher` sub-agent to get:
  - Exact endpoint signatures
  - Request/response schemas
  - Error codes
- Create tool using `httpx` or appropriate HTTP client

**SDK/Library:**
- Read the documentation URL from spec
- Use `WebFetch` or `web-researcher` sub-agent to get:
  - Exact method signatures
  - Return types
  - Exception types
- Create tool using the specified library

**Custom Function:**
- Follow the algorithm/pseudocode in spec
- Implement the described logic

4. **Generate tool functions** with proper:
   - Type hints (from API docs)
   - Docstrings (describe what tool does)
   - Error handling (from error codes in docs/spec)
   - Return format (JSON string for LangGraph tools)

**If documentation link is missing or unclear, ASK the user before guessing.**

**Only create tools.py if at least one agent uses tools.**

### Phase 3: Agent Implementations

**STOP. Use the Skill tool now: `skill: "individual-agents"`**

This loads the agent type implementation guides.

Fill in placeholder functions with actual implementations.

For each agent:
1. Read agent spec (e.g., `creator.md`)
2. Read pattern reference from `agent-config.yaml → agent → reference`
   - e.g., `agent-patterns/individual-agents/langgraph/text-agent.md`
3. Generate implementation following the pattern

### Phase 4: Prompts

**Strategy:** Create scaffold first, then sub-agents edit directly. This keeps prompts out of main agent context.

**Step 1: Create prompts.py scaffold**

```python
# prompts.py - Generated scaffold

CREATOR_PROMPT = """
# TODO: Generated by prompt-creator sub-agent
"""

CRITIC_PROMPT = """
# TODO: Generated by prompt-creator sub-agent
"""
```

**Step 2: Spawn prompt-creator sub-agents to EDIT the file directly**

For each agent, spawn `prompt-creator` sub-agent with:
- Path to prompts.py file
- Which prompt variable to update (e.g., `CREATOR_PROMPT`)
- Agent spec file path (e.g., `agents/creator.md`)
- Prompt config from `agent-config.yaml → agent → prompt`

The sub-agent:
1. Reads the agent spec
2. Invokes `prompt-engineering` skill internally
3. **Edits prompts.py directly** (uses Edit tool to update the placeholder)
4. Does NOT return the prompt to main agent

**Parallel execution:** If 6 agents, spawn 6 prompt-creator agents simultaneously. Each edits a different variable in the same file.

**Why this approach:**
- Prompts don't flow through main agent context
- Sub-agents work directly on the file
- Main agent just waits for completion
- Cleaner context management

### Phase 5: Utilities

Create utils.py if shared utilities are needed.

Only create if:
- Multiple agents share common logic
- Team needs helper functions

### Phase 6: Environment Setup

Generate environment configuration file.

**Note:** Dependencies are already added via `uv add` in Phase 0. The `pyproject.toml` is managed by uv.

**Generate `.env.example`:**

```bash
# Required API keys
ANTHROPIC_API_KEY=your_key_here  # LLM provider
YOUTUBE_API_KEY=your_key_here    # For YouTube metadata (optional)

# Optional configuration
LOG_LEVEL=INFO
```

**Include comments** explaining what each variable is for and how to obtain it.

**Read from:** `team.md` → Dependencies → Environment Variables section

---

## Task Dependencies

```
team.py scaffold
       ↓
    tools.py
       ↓
agent implementations (can be parallel per agent if tools complete)
       ↓
   prompts.py (parallel - all prompts at once)
       ↓
    utils.py (as needed)
       ↓
requirements.txt + .env.example
```

---

## Navigating References

The agent-config.yaml provides paths to pattern references:

```yaml
team:
  name: content-review-loop
  pattern: loop
  framework: langgraph
  reference: agent-patterns/agent-teams/langgraph/loop.md  # ← Use this

  agents:
    - agent:
        name: creator
        type: text-agent
        framework: langgraph
        reference: agent-patterns/individual-agents/langgraph/text-agent.md  # ← Use this
        prompt:
          framework: single-turn
          role: creative-generator
          modifiers: [memory]
```

When implementing:
1. Read the reference file for the pattern/structure
2. Read the spec file (team.md, agent.md) for the specific requirements
3. Combine: pattern structure + spec requirements = implementation

---

## Sub-Agent Strategy

| Task | Sub-Agent | Notes |
|------|-----------|-------|
| Team scaffold | None | agent-impl-builder does directly |
| Tools | None | agent-impl-builder does directly |
| Agent implementations | None | agent-impl-builder does directly |
| Prompts | `prompt-creator` | One per agent, run in parallel, edits file directly |
| Utils | None | agent-impl-builder does directly |

**Prompt-creator invocation:**

When spawning prompt-creator sub-agents, provide these EXPLICIT instructions:

```
Task tool with subagent_type='prompt-creator'

PROMPT FOR SUB-AGENT:
"You are creating a prompt for the [AGENT_NAME] agent.

STEP 1: INVOKE THE PROMPT-ENGINEERING SKILL
You MUST use the Skill tool to invoke: skill: "prompt-engineering"
This loads the prompt engineering reference files. Do not skip this step.

STEP 2: READ THE REFERENCE FILES
After invoking the skill, read these files:
- agent-patterns/prompt-engineering/frameworks/[framework].md
- agent-patterns/prompt-engineering/roles/[role].md
- agent-patterns/prompt-engineering/modifiers/[each modifier].md

STEP 3: READ THE AGENT SPEC
Read the agent spec file: [path to agents/agent-name.md]
Extract: Purpose, Key Tasks, Inputs, Outputs, Behavioral Requirements, Examples

STEP 4: WRITE THE PROMPT
Using the reference files and agent spec, write the prompt.
Use XML tags to structure sections: <role>, <task>, <context>, <constraints>, <output_format>

STEP 5: EDIT THE FILE DIRECTLY
Use the Edit tool to update [prompts.py path]
Replace the placeholder for [VARIABLE_NAME] with your generated prompt.
Do NOT return the prompt content - edit the file directly.

Prompt config:
- Framework: [single-turn | conversational]
- Role: [role name]
- Modifiers: [list of modifiers]
"
```

**CRITICAL: The sub-agent MUST:**
1. Use Skill tool to invoke `prompt-engineering` skill FIRST
2. Read the framework reference file
3. Read the role reference file
4. Read modifier reference files (if any)
5. Read the agent spec
6. THEN write the prompt following the patterns in the reference files

**XML Tags in Prompts:**
All prompts MUST use XML tags to structure sections. This improves model comprehension.

```python
CREATOR_PROMPT = """
<role>
You are a content creator...
</role>

<context>
Background information...
</context>

<task>
Your task is to...
</task>

<constraints>
- Constraint 1
- Constraint 2
</constraints>

<output_format>
Return your response as...
</output_format>
"""
```

---

## Progress Tracking

Maintain a task list throughout implementation:

```markdown
# [Project Name] - Implementation Progress

## Status

**Current Phase:** Scaffold | Tools | Agents | Prompts | Utils
**Last Updated:** YYYY-MM-DD

## Tasks

| Task | Status | Dependencies | Notes |
|------|--------|--------------|-------|
| team.py scaffold | done | - | |
| tools.py | done | scaffold | |
| Implement creator | done | tools.py | |
| Implement critic | in_progress | tools.py | |
| Prompt: creator | pending | creator impl | |
| Prompt: critic | pending | critic impl | |
| utils.py | pending | - | May not be needed |

## Completed Files

- [x] team.py (scaffold)
- [ ] team.py (full)
- [ ] tools.py
- [ ] prompts.py
- [ ] utils.py

## Notes

[Implementation decisions, issues encountered, etc.]
```

---

## Handling Nested Teams

For nested teams, process depth-first with parallelization:

1. Read `manifest.yaml` for parallel groups
2. Sub-teams at the same level can be implemented in parallel
3. Parent team waits for all sub-teams to complete
4. Top-level team.py imports and orchestrates sub-teams

**Each sub-team folder is self-contained** - has its own `agent-config.yaml`, can be processed independently.

```
Parallel Group 1 (can run simultaneously):
├── Implement content-refinement/ (complete team)
└── Implement parallel-research/ (complete team)

Parallel Group 2 (after group 1 completes):
└── Implement research-pipeline/ top-level (orchestrates sub-teams)
```

**Spawn sub-agents for parallel work:**
- Each sub-team can be processed by a separate Task agent
- Use `manifest.yaml → implementation-order → parallel-groups` to determine what can run in parallel

---

## File Generation Order

**Per team (including nested):**

1. **team.py scaffold** — Orchestration structure + placeholder agents
2. **tools.py** — Tool definitions (if needed)
3. **team.py full** — Fill in agent implementations
4. **prompts.py** — All prompts (parallel generation)
5. **utils.py** — Shared utilities (if needed)

---

## Templates

Progress tracking template: `templates/progress.md`

---

## Feedback Loop: Updating Cheat Sheets

**When you receive feedback about generated code, update the cheat sheet to prevent the same mistake.**

This creates a learning loop where the cheat sheets evolve based on real-world implementation issues.

### When to Update

Update the cheat sheet when you receive feedback that:
- Points out an incorrect pattern you used
- Identifies a framework anti-pattern
- Highlights a rule you didn't follow
- Reveals a common mistake

### How to Update

1. **Identify the framework** — Which cheat sheet needs updating?
   - `frameworks/langgraph/CHEATSHEET.md`
   - `frameworks/dspy/CHEATSHEET.md`

2. **Categorize the feedback:**
   - **Critical Rule** — Add to "Critical Rules" section
   - **Anti-pattern** — Add to "Anti-Patterns" section with wrong code example
   - **Pattern clarification** — Add to relevant pattern section

3. **Format the update:**

**For anti-patterns:**
```markdown
### DO NOT: [Description of mistake]

```python
# WRONG
[Code that was incorrectly generated]
```

**Why:** [Explanation of why this is wrong]

**Correct approach:**
```python
# CORRECT
[How it should be done]
```
```

**For critical rules:**
```markdown
### [Number]. [Rule Name]

**CORRECT:**
```python
[Correct code]
```

**WRONG - DO NOT DO THIS:**
```python
[Wrong code]
```

**Why:** [Explanation]
```

4. **Edit the cheat sheet** using the Edit tool.

### Example

**Feedback received:**
> "The ToolNode is being created inside the agent function instead of being added to the graph."

**Action taken:**
1. Open `frameworks/langgraph/CHEATSHEET.md`
2. Add to Anti-Patterns section:

```markdown
### DO NOT: Create ToolNode inside agent functions

```python
# WRONG
async def agent(state):
    if response.tool_calls:
        tool_node = ToolNode(tools)  # WRONG - created inside function
        result = await tool_node.ainvoke(...)  # WRONG - manual invocation
```

**Why:** ToolNode is designed to be a graph node. Creating it inside functions bypasses LangGraph's execution model.
```

### Mandatory Update Triggers

**Always update the cheat sheet when:**
- [ ] User explicitly says the generated code is wrong
- [ ] A pattern was used incorrectly
- [ ] The code doesn't follow framework best practices
- [ ] A debugging session reveals a systematic issue

**Do not wait for multiple occurrences.** Add to the cheat sheet on first feedback to prevent repetition.

---

## References

- `frameworks/` — Framework cheat sheets (read first!)
- `agent-teams/` — Team pattern implementations
- `individual-agents/` — Agent type implementations
- `prompt-engineering/` — Prompt frameworks, roles, modifiers
- `agent-spec-builder/` — Specification format and structure
