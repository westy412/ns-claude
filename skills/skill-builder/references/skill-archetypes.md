# Skill Archetypes Reference

> **When to read:** During Phase 1 (Discovery) to determine the best archetype for the skill being built.

Every skill fits one of five archetypes. The archetype determines the structure, complexity, and patterns to use. Some skills blend archetypes -- pick the primary one and borrow patterns from others.

---

## Quick Selection

```
What does the skill primarily do?
├── Guides through a multi-step process with phases → Workflow
├── Provides knowledge/documentation for a topic → Reference
├── Follows a specific procedure step-by-step → Process
├── Produces structured output (files, configs, code) → Generator
└── Orchestrates or routes to other skills → Meta/Router
```

---

## 1. Workflow Skill

Multi-phase process with decision points, optional team orchestration, and progress tracking.

**When to use:**
- Task has distinct phases that build on each other
- May need parallel execution via teams
- Requires progress tracking across sessions
- Has validation gates between phases

**Typical structure:**
```
{skill-name}/
├── SKILL.md              (routing table + phase overview)
├── references/
│   ├── phase-1-{name}.md
│   ├── phase-2-{name}.md
│   ├── phase-N-{name}.md
│   └── handover.md       (session resumption protocol)
└── templates/
    └── progress.md        (progress tracking template)
```

**Key characteristics:**
- SKILL.md contains phase table linking phases to reference files
- Each phase loaded just-in-time (one at a time)
- Progress file tracks current phase and state
- May use child skills (loaded per phase)
- Optional team mode for parallel phases

**SKILL.md outline:**
- Frontmatter + description
- When to Use / Skip
- Phase table (phase → reference file → what happens)
- Key principles
- Phase quick decision tree
- Child skills table (if applicable)
- Sub-agent delegation table (if applicable)

**Examples:** `agent-spec-builder`, `general-spec-builder`, `agent-implementation-builder`, `general-implementation-builder`, `framework-skill-builder`

---

## 2. Reference Skill

Provides knowledge, documentation, or conventions that agents apply to their current work. Runs inline alongside the conversation.

**When to use:**
- Skill provides background knowledge (API conventions, coding standards)
- Content is informational, not action-oriented
- Agent should apply this knowledge while doing other tasks
- Multiple topics need progressive disclosure

**Typical structure:**
```
{skill-name}/
├── SKILL.md              (overview + routing table to references)
└── references/
    ├── {topic-1}.md
    ├── {topic-2}.md
    └── {topic-N}.md
```

**Key characteristics:**
- SKILL.md is a concise overview with routing table
- Reference files loaded on-demand by topic
- No templates or scripts typically needed
- Often `user-invocable: false` (Claude loads when relevant)
- Focused on WHAT to know, not WHAT to do

**SKILL.md outline:**
- Frontmatter + description
- Core Concepts (3-5 paragraphs)
- Reference Files routing table (topic → file → when to load)
- Quick Reference (2-3 key patterns or examples)

**Examples:** `dspy`, `langchain-deep-agents`, `langchain-mcp-adapters`, `remotion-best-practices`, `prompt-engineering`

---

## 3. Process Skill

Step-by-step procedure for a specific action. Often user-invoked via `/command`.

**When to use:**
- Task follows a defined procedure
- Steps are sequential and well-known
- Often has side effects (deploy, commit, send)
- User wants to control when it runs

**Typical structure:**
```
{skill-name}/
├── SKILL.md              (complete procedure)
└── scripts/              (optional - helper scripts)
    └── {script}.sh
```

**Key characteristics:**
- Often fits in a single SKILL.md (no reference files needed)
- Usually `disable-model-invocation: true` (user-controlled)
- May use `$ARGUMENTS` for parameterization
- May use `!`command`` for dynamic context
- Steps are numbered and explicit

**SKILL.md outline:**
- Frontmatter with `disable-model-invocation: true`
- Arguments description
- Numbered steps
- Error handling / edge cases
- Completion criteria

**Examples:** `cloudrun-deploy`, `weekly-review`, `project-management`

---

## 4. Generator Skill

Produces structured output -- files, configurations, code, documents.

**When to use:**
- Primary purpose is creating output files
- Output follows a consistent structure/template
- May need templates for output format
- Input varies but output structure is predictable

**Typical structure:**
```
{skill-name}/
├── SKILL.md              (generation workflow + output format)
├── templates/
│   ├── {output-1}.md
│   └── {output-2}.md
└── references/            (optional - generation guidelines)
    └── format-rules.md
```

**Key characteristics:**
- Templates define the output structure
- SKILL.md describes the generation workflow
- May gather input through conversation
- Output location is a key decision (ask or default)
- Templates use placeholder conventions: `[brackets]` or `{{handlebars}}`

**SKILL.md outline:**
- Frontmatter + description
- Input requirements
- Output format description
- Generation steps
- Template reference
- Output location options

**Examples:** `teammate-spawn`, `agent-impl-teammate-spawn`, `brainstorm` (produces idea cards), `discovery` (produces discovery document)

---

## 5. Meta/Router Skill

Orchestrates or routes to other skills. Acts as a coordinator.

**When to use:**
- Skill's primary job is deciding which other skill to invoke
- Coordinates a pipeline of skills
- Provides a unified entry point for related capabilities
- May transform or adapt between skills

**Typical structure:**
```
{skill-name}/
├── SKILL.md              (routing logic + decision tree)
└── references/            (optional - routing context)
    └── {decision-context}.md
```

**Key characteristics:**
- Contains routing decision trees
- References child skills by name
- May load child skills via `Skill tool`
- SKILL.md focuses on WHEN to route WHERE
- Minimal own content -- delegates to other skills

**SKILL.md outline:**
- Frontmatter + description
- Routing decision tree (ASCII)
- Child skills table (skill → when → what it provides)
- Fallback behavior

**Examples:** `skill-builder` (this skill!), `general-spec-builder` (routes agent work to agent-spec-builder)

---

## Blended Archetypes

Some skills combine archetypes:

| Blend | Example | Pattern |
|-------|---------|---------|
| Workflow + Generator | `agent-spec-builder` | Phased workflow that produces spec documents |
| Reference + Process | `prompt-engineering` | Reference knowledge applied through a creation process |
| Meta + Workflow | `skill-builder` | Routes to other skills OR runs its own workflow |
| Generator + Process | `brainstorm` | Follows a process to generate structured output |

When blending, pick the **primary** archetype for the overall structure, then borrow specific patterns from the secondary:
- Primary determines directory structure and SKILL.md layout
- Secondary provides specific section patterns (e.g., add a templates/ dir from Generator to a Workflow skill)
