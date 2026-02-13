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
3. **Parallel where possible** — Spawn teammates for independent work streams
4. **Reference-guided** — Use pattern references from agent-config.yaml
5. **Only create what's needed** — Don't generate empty files
6. **Framework cheat sheets first** — Read framework rules before writing code
7. **Ask when unsure** — Never guess. If spec is unclear or documentation is missing, ask the user
8. **Context-conscious loading** — Load child skills one at a time, only at the phase that needs them. The framework cheatsheet is the only reference to load upfront (Phase 0). All other skills are loaded just-in-time per phase. Persist progress to progress.md before each new skill load.
9. **Specs describe behavior, skills describe implementation** — Specs say WHAT should happen — behavior descriptions, data flow, acceptance criteria. Skills say HOW to implement it — framework patterns, code conventions, anti-patterns. If a spec includes code/pseudo-code that conflicts with a skill rule, follow the skill. Specs are not authoritative on implementation details. Schemas (data structures, API contracts) in specs are valid references; code examples are not.
10. **Fix propagation — sweep the codebase** — When applying a pattern fix (e.g., fixing model validation, adding retry logic), search ALL instances of the same pattern in the codebase, not just the failing one. Process: 1) Fix the triggering instance, 2) Search for all instances of the same pattern, 3) Apply the same fix to ALL qualifying instances, 4) Document the sweep scope in the commit message.
11. **Model-consumer lockstep** — When modifying a Pydantic model (adding/removing/renaming fields), you MUST update ALL consumers in the same commit. Process: 1) Change the model, 2) grep for all usages of the class name AND field names being changed, 3) Update every consumer, 4) Commit model + all consumer changes together.

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

| Framework | Cheat Sheet Location |
|-----------|---------------------|
| LangGraph | `frameworks/langgraph/CHEATSHEET.md` |
| DSPy | `frameworks/dspy/CHEATSHEET.md` |

**What cheat sheets contain:**
- **Critical Rules** — Things you MUST do / MUST NOT do
- **Common Patterns** — Quick reference for key patterns
- **Anti-patterns** — What NOT to do with examples of wrong code

**When to read:**
1. At the start of implementation (Phase 0)
2. Before implementing any tool-using agents
3. When combining patterns (e.g., router + tools)

---

## Child Skills (Just-in-Time Loading)

**CONTEXT BUDGET RULE: Only invoke ONE child skill at a time, and ONLY when you reach the phase that needs it.** The only upfront reading is the framework cheatsheet (Phase 0, Step 3). Everything else is loaded just-in-time.

### Who Loads Which Skills

| Skill | Loaded By | When | Why |
|-------|-----------|------|-----|
| **Framework cheatsheet** | Main agent | Phase 0, Step 3 | Critical rules for all code generation |
| **agent-teams** | Teammates (research, ideation, scaffold streams) | Before writing team modules | Team-specific orchestration patterns |
| **individual-agents** | Teammates (research, ideation, signatures streams) | Before writing agent code | Agent type patterns |
| **tools-and-utilities** | Teammates (tools stream) | Before writing tool functions | Tool design patterns |
| **prompt-engineering** | Teammates (signatures stream, DSPy) OR prompt-creator sub-agents (LangGraph) | Before writing prompts/signatures | Prompt structure patterns |

**CRITICAL: Main agent does NOT load child skills.** Loading all skills would consume ~10K+ lines of context, leaving no room for spec files or code generation. Instead:
- Main agent loads framework cheatsheet once (Phase 0)
- Teammates load their specific child skills just-in-time when needed
- This distributes context load across teammate contexts

**In team mode:** Each teammate gets its own context window. Skills loaded by a teammate do NOT consume the main agent's context.

*Important: IF YOU ARE USING TEAM MODE MAKE SURE TO LOAD IN THE agent-impl-teammate-spawn skill*

**Loading rules:**
1. Phase 0: Read ONLY the framework cheatsheet. DO NOT invoke any child skills yet.
2. At each subsequent phase, teammates invoke the ONE skill needed for that phase.
3. Before invoking a new child skill, update progress.md with all completed work.
4. After completing a phase, update progress.md before proceeding.
5. If context is large after completing a phase, consider a session handover before loading the next skill.
6. For Phase 4 (LangGraph): `prompt-engineering` is loaded by prompt-creator sub-agents in their own context, NOT by the main agent.

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
        │   ├── agent-config.yaml
        │   └── agents/
        └── parallel-research/
            ├── team.md
            ├── agent-config.yaml
            └── agents/
```

---

## Output

Production code — framework determines file organization:

```
What framework are you using?
├── DSPy → Read `references/dspy/file-organization.md`
└── LangGraph → Read `references/langgraph/file-organization.md`
```

| Framework | Key Differences |
|-----------|----------------|
| **DSPy** | `signatures.py` + `prompts/*.md` (two-file pattern), NO `prompts.py`, `utils.py` REQUIRED |
| **LangGraph** | `team.py` + `prompts.py`, standard structure |

**Only create files if the team needs them.**

---

## Workflow

### Phase Routing Table

| Phase | What | Reference | Skill to Load |
|-------|------|-----------|---------------|
| 0 | Parse Spec & Init | `references/common/workflow-phases.md` | Framework cheatsheet only |
| 1 | Team Scaffold | `references/common/workflow-phases.md` | `agent-teams` |
| 2 | Tools | `references/common/workflow-phases.md` | `tools-and-utilities` |
| 3 | Agent Implementations | `references/common/workflow-phases.md` | `individual-agents` |
| 4 | Prompts/Signatures | *Framework-specific — see below* | `prompt-engineering` (loaded by teammates/sub-agents) |
| 5 | Utilities | `references/common/workflow-phases.md` | — |
| 6 | Environment Setup | `references/common/workflow-phases.md` | — |
| 7 | FastAPI Wrapper | `references/common/workflow-phases.md` | — |

### Phase 4: Framework-Specific Routing

```
Phase 4: Prompts & Signatures
├── DSPy → Read `references/dspy/implementation-phases.md`
│   Creates: signatures.py (empty docstrings) + prompts/*.md files
│   Teammates load prompt-engineering skill when writing .md files
│
└── LangGraph → Read `references/langgraph/implementation-phases.md`
    Creates: prompts.py scaffold → prompt-creator sub-agents edit directly
    Sub-agents invoke prompt-engineering skill internally
```

#### Signals for DSPy
- `agent-config.yaml` says `framework: dspy`
- Project has `signatures.py` and `models.py` files
- Uses `dspy.Module`, `Predict`, `ChainOfThought`

#### Signals for LangGraph
- `agent-config.yaml` says `framework: langgraph`
- Project has `team.py` with state graph
- Uses `ChatPromptTemplate`, `@tool`, `StateGraph`

### Execution Mode Decision (Phase 0, Step 4.5)

```
Does execution-plan in manifest.yaml have parallel chunks across different streams?
├── Yes (2+ streams in any phase) → TEAM MODE
│   Read: `references/common/team-mode.md`
│   Load: agent-impl-teammate-spawn skill
│
└── No (sequential, missing, or single stream) → SINGLE-AGENT MODE
    Proceed through phases sequentially
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

## Delegation Strategy

```
Implementation Builder (team lead)
├── Spawns TEAMMATES (via TeamCreate + Task tool with team_name)
│   └── Teammates can spawn SUB-AGENTS for:
│       ├── codebase-researcher → Explore patterns without polluting context
│       ├── web-researcher → Read API docs, external documentation
│       └── prompt-creator → Generate prompts (edits files directly)
```

| Situation | Method | Reference |
|-----------|--------|-----------|
| Parallel work streams | Teammates | `references/common/team-mode.md` |
| Codebase research | Sub-agent (codebase-researcher) | `references/common/sub-agents.md` |
| API doc research | Sub-agent (web-researcher) | `references/common/sub-agents.md` |
| Prompt generation | Sub-agent (prompt-creator) | `references/common/sub-agents.md` |

Full details: `references/common/sub-agents.md`

---

## Implementation Patterns

| Pattern | When to Use | Reference |
|---------|-------------|-----------|
| Template-to-Instances | Multiple sub-teams share structure, differ in config | `references/common/patterns.md` |
| Nested Teams | Sub-teams at same level, depth-first processing | `references/common/patterns.md` |
| 3-Level Nesting | Root → phase teams → sub-teams | `references/common/patterns.md` |

**CRITICAL: Factory functions are FORBIDDEN.** When multiple sub-teams share the same template, generate each as a standalone, self-contained module. See `references/common/patterns.md` for details.

---

## Progress Tracking

**Create `progress.md` BEFORE starting implementation (Phase 0, Step 7).**

| Topic | Reference |
|-------|-----------|
| Progress document format | `references/common/progress-tracking.md` |
| Cross-session resumption | `references/common/progress-tracking.md` |
| Progress template | `templates/progress.md` |

---

## Feedback Loop

When you receive feedback about generated code, update the framework cheat sheet to prevent the same mistake.

Full process: `references/common/feedback-loop.md`

**Mandatory triggers:**
- User says generated code is wrong
- A pattern was used incorrectly
- Code doesn't follow framework best practices
- Debugging reveals a systematic issue

---

## Templates

Progress tracking template: `templates/progress.md`

---

## References

### Framework-Specific
- `references/dspy/file-organization.md` — DSPy file structure, two-file prompt pattern, signature rules
- `references/dspy/implementation-phases.md` — DSPy Phase 4 details, prompt-writing file traversal
- `references/langgraph/file-organization.md` — LangGraph file structure
- `references/langgraph/implementation-phases.md` — LangGraph Phase 4 details, prompt scaffold pattern

### Common
- `references/common/workflow-phases.md` — Phases 0-3, 5-7 (framework-agnostic)
- `references/common/team-mode.md` — Team mode execution & orchestration
- `references/common/patterns.md` — Template-to-instances, nested teams, 3-level nesting
- `references/common/sub-agents.md` — Delegation strategy, sub-agent invocation patterns
- `references/common/progress-tracking.md` — Progress tracking & cross-session resumption
- `references/common/feedback-loop.md` — Cheat sheet update process

### Existing (DO NOT MODIFY)
- `frameworks/langgraph/CHEATSHEET.md` — LangGraph critical rules and patterns
- `frameworks/dspy/CHEATSHEET.md` — DSPy critical rules and patterns
- `frameworks/dspy/async-patterns.md` — DSPy async patterns
- `frameworks/dspy/react.md` — DSPy ReAct patterns
- `frameworks/dspy/optimization/` — DSPy optimization guides
- `templates/progress.md` — Progress tracking template
