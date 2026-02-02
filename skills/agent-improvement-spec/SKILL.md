---
name: agent-improvement-spec
description: Design improvements to existing agent systems. Analyzes current implementation, researches solutions, and produces change specs for approval. Use when adding features, fixing bugs, or enhancing existing agents.
allowed-tools: Read, Glob, Grep, Task, Write, Edit, WebFetch
---

# Agent Improvement Spec Skill

## Purpose

A design skill for improving existing agent systems. Takes improvement requests (features, bugs, feedback) and produces change specifications for approval before implementation.

**Goal:** Produce detailed change specs that the agent-improvement-impl skill can execute autonomously.

---

## When to Use This Skill

Use this skill when:
- Adding features to existing agent systems
- Fixing bugs or issues
- Responding to user feedback
- Adding integrations (Telegram, Slack, etc.)
- Performance improvements
- Adding new agents to existing teams
- Enhancing tools or prompts

**Skip this skill when:**
- Building a new agent system from scratch (use agent-spec-builder)
- Only tweaking a single prompt (edit directly)
- The change is trivial and obvious

---

## Key Principles

1. **Understand before changing** — Research current implementation thoroughly
2. **Parallel research** — Use sub-agents to research in parallel, saving time and context
3. **Minimal changes** — Only change what's necessary for the improvement
4. **Backwards compatible** — Don't break existing functionality
5. **Ask when unsure** — Clarify requirements before designing changes

---

## Sub-Agents for Research

**CRITICAL:** Use sub-agents to parallelize research and keep context clean. Don't do all research yourself.

### codebase-researcher

**Purpose:** Explores and analyzes the existing codebase to understand implementations, patterns, and architecture.

**When to use:**
- Understanding how current agents work
- Finding where changes need to be made
- Identifying dependencies and side effects
- Understanding existing patterns to follow

**How to invoke:**
```
Task tool → subagent_type: "codebase-researcher"

Prompt: "Analyze the [agent-name] agent implementation:
1. How does it currently handle [feature]?
2. What tools does it use?
3. What's the data flow from input to output?
4. What files would need to change to add [new capability]?

Focus on: [specific files or directories]
Return: Summary of findings with file paths and line numbers."
```

**What it returns:**
- File paths and relevant code sections
- Architecture overview
- Identified patterns
- Suggested modification points

---

### web-researcher

**Purpose:** Researches external APIs, libraries, documentation, and best practices using Perplexity tools.

**When to use:**
- Finding APIs for new integrations (Telegram, Slack, etc.)
- Researching best libraries for a task
- Understanding external service requirements
- Finding documentation and examples

**How to invoke:**
```
Task tool → subagent_type: "web-researcher"

Prompt: "Research Telegram bot integration for Python:
1. What's the best library? (package name, docs URL)
2. How to set up a bot? (API token, webhook vs polling)
3. How to receive messages?
4. How to send messages?
5. Rate limits and constraints?

Return: Summary with documentation links and code examples."
```

**What it returns:**
- Library recommendations with pros/cons
- Documentation URLs
- Setup instructions
- Code examples
- Constraints and gotchas

---

### Parallel Research Pattern

**For improvements requiring both internal and external research, spawn both sub-agents simultaneously:**

```
# Example: Adding Telegram integration

# Spawn BOTH at the same time (parallel)
Task 1 → codebase-researcher:
"Analyze current input/output handling in the agent system:
- How does it currently receive requests?
- How does it send responses?
- Where would a new input channel plug in?
- What's the message format used internally?"

Task 2 → web-researcher:
"Research Telegram bot integration:
- Best Python library
- Bot setup process
- Message handling patterns
- Webhook vs long-polling tradeoffs"

# Wait for both to complete, then synthesize findings
```

**Benefits:**
- Faster than sequential research
- Each sub-agent has focused context
- Main agent context stays clean
- Results synthesized only when needed

---

## Input

Improvement request from user, plus existing system:

**Required:**
- Clear description of what to improve/add/fix
- Access to existing spec (if available)
- Access to existing implementation

**Optional:**
- User feedback or bug reports
- Performance metrics
- Priority/urgency

---

## Output

Change specification document:

```
project-name/
└── change-specs/
    └── YYYYMMDD-feature-name.md   # Change spec
```

---

## Workflow

### Phase 1: Understand the Request

1. **Clarify the improvement request**
   - What exactly needs to change?
   - What's the expected outcome?
   - Any constraints or preferences?

2. **Categorize the request**

| Type | Examples | Typical Scope |
|------|----------|---------------|
| **Feature** | Add Telegram, add export | New files + modifications |
| **Enhancement** | Improve accuracy, add validation | Modify existing |
| **Bug fix** | Tool fails on X, wrong output | Targeted fix |
| **Integration** | Connect to external service | New tool + config |
| **Performance** | Too slow, too many tokens | Optimization |

### Phase 2: Discovery & Brainstorming

**Purpose:** Explore options and debate approaches BEFORE committing to a solution.

**This phase is collaborative with the user.** Don't skip to designing changes.

#### Step 1: Initial Research (Parallel)

Spawn research sub-agents to gather information:

```
# Parallel research to understand the landscape

codebase-researcher: "How does [relevant area] currently work?"
web-researcher: "What are the common approaches to [improvement type]?"
```

#### Step 2: Present Options

Based on research, present multiple approaches to the user:

```
For [improvement], I found these approaches:

**Option A: [Name]**
- How it works: [description]
- Pros: [list]
- Cons: [list]
- Complexity: Low/Medium/High

**Option B: [Name]**
- How it works: [description]
- Pros: [list]
- Cons: [list]
- Complexity: Low/Medium/High

Which direction would you like to explore?
```

#### Step 3: Debate & Refine

Discuss with user:
- Trade-offs between options
- Constraints they care about
- Edge cases to consider
- Scope boundaries

**Questions to explore:**
> "Should this handle [edge case] or is that out of scope?"
> "Do you prefer [simpler approach] or [more flexible approach]?"
> "How important is [consideration] vs [other consideration]?"

#### Step 4: Agree on Direction

Get explicit confirmation before moving to detailed research:

> "So we're going with [chosen approach] because [reasons]. Ready to design the details?"

---

### Phase 3: Detailed Research (Parallel)

**Now that direction is agreed, research the specifics:**

| Research Need | Sub-Agent | Prompt Focus |
|---------------|-----------|--------------|
| Current implementation | codebase-researcher | How it works now |
| External API/service | web-researcher | API docs, libraries |
| Best practices | web-researcher | Patterns, examples |
| Side effects | codebase-researcher | What else might break |

**Example for Telegram integration:**

```markdown
## Research Tasks (spawn in parallel)

1. **codebase-researcher:** "Analyze current message handling..."
2. **web-researcher:** "Research python-telegram-bot library..."
3. **web-researcher:** "Research Telegram bot best practices..."
```

### Phase 4: Synthesize Findings

After sub-agents return:

1. **Combine insights** from all research
2. **Identify change points** in the codebase
3. **Map dependencies** between changes
4. **Note risks** or potential issues

### Phase 5: Design Changes

For each change needed:

1. **What file?** (new or existing)
2. **What changes?** (specific modifications)
3. **Why?** (connects to requirement)
4. **Dependencies?** (what must happen first)

### Phase 6: Generate Change Spec

Create `change-specs/YYYYMMDD-feature-name.md` using the template.

**Template location:** `templates/change-spec.md`

---

## Change Spec Structure

```markdown
# Change Spec: [Feature Name]

## Request
[Original user request, verbatim or summarized]

## Analysis

### Current State
[How it works now - from codebase-researcher]

### Research Findings
[What was learned - from web-researcher]

### Impact Assessment
- Files affected: X
- New dependencies: Y
- Risk level: Low/Medium/High

---

## Changes

### New Files

#### `path/to/new/file.py`
**Purpose:** [What this file does]
**Key components:**
- [Class/function 1]: [purpose]
- [Class/function 2]: [purpose]

**Depends on:** [other changes that must happen first]

---

### Modified Files

#### `path/to/existing/file.py`
**Current:** [What it does now]
**Change:** [What to add/modify]
**Reason:** [Why this change is needed]

**Specific changes:**
1. Add import for X
2. Add new function Y
3. Modify function Z to call Y

---

### Prompt Changes

#### Agent: [agent-name]
**Current behavior:** [How it behaves now]
**New behavior:** [How it should behave]
**Specific changes:**
- Add instruction: "[new instruction]"
- Modify constraint: "[old] → [new]"

---

### New Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| python-telegram-bot | >=20.0 | Telegram API |

---

### Environment Variables

| Variable | Purpose | How to Obtain |
|----------|---------|---------------|
| TELEGRAM_BOT_TOKEN | Bot authentication | @BotFather on Telegram |

---

## Implementation Order

1. [ ] Add dependencies
2. [ ] Create new files
3. [ ] Modify existing files
4. [ ] Update prompts
5. [ ] Update .env.example
6. [ ] Test integration

---

## Testing Checklist

- [ ] [Test case 1]
- [ ] [Test case 2]
- [ ] Existing functionality still works

---

## Rollback Plan

If issues occur:
1. [Step to revert]
2. [Step to revert]
```

---

## Asking for Approval

After generating the change spec:

1. **Summarize** the changes for the user
2. **Highlight** any risks or decisions needed
3. **Ask** for approval before implementation

```
I've created a change spec for [feature]. Here's the summary:

**Changes:**
- [X new files]
- [Y modified files]
- [Z new dependencies]

**Key decisions:**
- [Decision 1]: I chose [option] because [reason]
- [Decision 2]: Need your input on [question]

**Risks:**
- [Any identified risks]

Should I proceed with implementation, or would you like to review/modify the change spec first?
```

---

## When to Ask for Clarification

**Ask the user when:**
- Request is ambiguous
- Multiple valid approaches exist
- Trade-offs need user decision
- Research reveals complications
- Scope seems larger than expected

**Example:**
> "For Telegram integration, I found two approaches:
> 1. Webhook (requires public URL, lower latency)
> 2. Long-polling (simpler setup, slightly higher latency)
>
> Which would you prefer?"

---

## Child Skills

**Use these skills when the improvement involves their domain:**

| Improvement Type | Skill to Invoke | When |
|------------------|-----------------|------|
| Adding new agent | `individual-agents` | Designing the new agent's type and structure |
| Changing team structure | `agent-teams` | Adding agents, changing flow, new patterns |
| Modifying prompts | `prompt-engineering` | Prompt rewrites, new roles, modifiers |
| Adding tools or utilities | `tools-and-utilities` | Tools (agent-callable), utility functions, wrappers, helpers |

**How to invoke:**
```
Skill tool → skill: "individual-agents"
```

**Example flow for adding a new agent:**
1. Use `codebase-researcher` to understand current team
2. Invoke `individual-agents` skill to select agent type
3. Invoke `prompt-engineering` skill to design the prompt
4. Include all details in change spec

---

## References

- `templates/change-spec.md` — Change spec template
- `agent-improvement-impl/` — Implements approved change specs
- `agent-spec-builder/` — For new systems (not improvements)
- `individual-agents/` — Agent type selection
- `agent-teams/` — Team patterns
- `prompt-engineering/` — Prompt design
- `tools-and-utilities/` — Tools and utility function patterns
