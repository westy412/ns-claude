---
name: agent-pattern-discovery
description: Extract and document agent design patterns from codebases. Use when building documentation for individual agents, agent teams, or prompt engineering guidelines. Supports two modes - user provides examples directly, or investigation of repos to discover patterns. Produces structured documentation for internal use and AI agent context.
---

# Agent Pattern Discovery

Build documentation corpus for agent design by extracting patterns from existing code.

## Process Overview

```
Step 1: Determine what we're building
    ↓
Step 2: Determine discovery mode
    ↓
Step 3: Extract patterns (using codebase-researcher if needed)
    ↓
Step 4: Present findings and discuss
    ↓
Step 5: Document in appropriate location
```

---

## Step 1: Determine What We're Building

Ask the user what they want to document:

| Area | Description | Reference Files |
|------|-------------|-----------------|
| **Individual Agents** | Agent type patterns (structured output, tool calling, etc.) | `references/individual-agents/` |
| **Agent Teams** | Team orchestration patterns (linear, loop, fan-out, etc.) | `references/agent-teams/` |
| **Prompt Engineering** | Prompting frameworks, type-specific, use-case, team communication | `references/prompt-engineering/` |

Once determined, load the relevant reference files:
- `template.md` — documentation structure to produce
- `investigation.md` — how to find patterns in code

---

## Step 2: Determine Discovery Mode

**Mode A: User-Provided Example**
```
User says: "This file/repo is a good example of X"
    ↓
Load relevant template
    ↓
Extract pattern from provided location
    ↓
Present findings for confirmation
    ↓
Document
```

**Mode B: Investigation**
```
User says: "Find X patterns in this repo" or "What patterns exist here?"
    ↓
Load relevant investigation instructions
    ↓
Dispatch codebase-researcher sub-agent(s)
    ↓
Present findings
    ↓
Discuss with user (good example? bad example? what type?)
    ↓
Document validated patterns
```

---

## Step 3: Extract Patterns

### For User-Provided Examples

1. Load the relevant template from references
2. Read the file(s) the user pointed to
3. Extract information to fill the template
4. If information is missing, ask the user

### For Investigation Mode

Dispatch `codebase-researcher` sub-agent with:

```
You are investigating a codebase to discover [agent/team/prompting] patterns.

REPOSITORY: [path]
AREA: [Individual Agents / Agent Teams / Prompt Engineering]

INVESTIGATION INSTRUCTIONS:
[Paste from references/[area]/investigation.md]

TASK:
1. Follow the investigation instructions
2. For each pattern found, extract:
   - Location (file path)
   - Pattern type (if identifiable)
   - Key code snippets
   - Any prompts found
3. Return findings for review

Do NOT document yet — just extract and report.
```

**Multiple Repos:** If investigating multiple repositories, dispatch sub-agents in parallel, one per repo. Collect all findings before proceeding.

---

## Step 4: Present Findings and Discuss

Present extracted patterns to user:

```
I found the following patterns in [repo]:

### Pattern 1: [Location]
- **Type (my assessment):** [e.g., Structured Output Agent]
- **Key characteristics:** [what I observed]
- **Code snippet:**
[relevant code]

### Pattern 2: [Location]
...

Questions:
1. Is Pattern 1 a good or bad example?
2. Is my type assessment correct?
3. Should this be documented?
```

Discuss until user confirms:
- Pattern type
- Good vs bad example
- Should be documented (yes/no)
- Any corrections or additional context

---

## Step 5: Document

Once patterns are validated:

1. Load the appropriate template from references
2. Fill in the template with extracted information + user input
3. Ask user: Where should this be saved?
4. Create/update the documentation file

**For new pattern types:** Create a new file following the template structure.

**For existing pattern types:** Add examples to existing file, or update if this is a better example.

---

## Reference Files

### Individual Agents
- [template.md](references/individual-agents/template.md) — Documentation structure
- [investigation.md](references/individual-agents/investigation.md) — How to find agent patterns

### Agent Teams
- [template.md](references/agent-teams/template.md) — Documentation structure
- [investigation.md](references/agent-teams/investigation.md) — How to find team patterns

### Prompt Engineering
- [templates/](references/prompt-engineering/templates/) — Documentation structures
  - `framework.md` — For One-Turn / Conversational frameworks
  - `by-type.md` — For type-specific prompting (structured output, tool calling)
  - `by-use-case.md` — For use-case prompting (researcher, critic)
  - `team-communication.md` — For inter-agent communication patterns
- [investigation.md](references/prompt-engineering/investigation.md) — How to find prompting patterns

---

## Corpus Structure

When documenting, patterns go into this structure:

```
[corpus-location]/
├── individual-agents/
│   ├── overview.md
│   ├── structured-output.md
│   ├── simple-text-output.md
│   ├── simple-message-agent.md
│   ├── simple-tool-agent.md
│   ├── structured-output-tool-calling.md
│   └── [new types as discovered]
│
├── agent-teams/
│   ├── overview.md
│   ├── linear.md
│   ├── two-agent-loop.md
│   ├── fan-out-aggregate.md
│   ├── hybrid.md
│   └── [new patterns as discovered]
│
└── prompt-engineering/
    ├── principles.md
    ├── frameworks/
    │   ├── one-turn.md
    │   └── conversational.md
    ├── by-implementation/
    │   ├── langgraph.md
    │   └── dspy.md
    ├── by-type/
    │   └── [matches individual-agents types]
    ├── by-use-case/
    │   ├── researcher.md
    │   ├── critic.md
    │   └── [others]
    └── team-communication/
        ├── production-line.md
        ├── two-agent-loop.md
        └── fan-out-aggregate.md
```

Ask user for corpus location if not specified.

---

## Guidelines

### Good vs Bad Examples

When user indicates an example is "bad":
- Still document the pattern
- Mark clearly as anti-pattern
- Explain WHY it's bad
- Include in Pitfalls section

### Incomplete Information

If investigation doesn't surface enough information:
- Ask user for clarification
- Ask user to point to specific files
- Note gaps in documentation

### Existing Documentation

Before creating new docs:
- Check if pattern type already documented
- If yes, ask: Replace existing? Add as additional example? Skip?

### Multiple Patterns in One File

Common to find multiple patterns in single file. Document each separately, reference the same source file.
