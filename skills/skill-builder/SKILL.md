---
name: skill-builder
description: Build new skills through guided conversation. Analyzes requirements, determines skill archetype, and generates complete skill directories with SKILL.md, references, templates, and scripts. Routes framework/SDK documentation skills to framework-skill-builder. Use when creating a new skill, designing a skill structure, or when the user says "build a skill."
allowed-tools: Read, Glob, Grep, Task, AskUserQuestion, Write, Edit, Bash, Skill
---

> **Invoke with:** `/skill-builder` | **Keywords:** build skill, create skill, new skill, design skill, skill structure

Build any type of skill through guided conversation. Acts as a design consultant -- understands what you need, determines the right archetype and structure, then generates a complete skill directory.

**Input:** A description of what you want the skill to do (or just an idea)
**Output:** Complete skill directory with SKILL.md + supporting files

## When to Use This Skill

Use this skill when:
- Creating a new skill from scratch
- Designing the structure for a complex skill
- Converting an existing workflow or process into a skill
- Unsure what archetype or structure a skill should use

**Skip this skill when:**
- Building a skill for an SDK/framework's documentation (use `framework-skill-builder` instead)
- Just need to edit an existing skill's content (edit files directly)

## Routing

```
User wants to build a skill
├── Is it for SDK/framework documentation? (e.g., "build a skill for Next.js")
│   └── YES → Invoke skill: "framework-skill-builder" -- handles the 3-phase team process
└── NO → Continue with this skill
```

## Reference Files

Load these just-in-time based on conversation needs:

| Topic | Reference File | When to Load |
|-------|---------------|--------------|
| AgentSkills.io spec | [agentskills-io-spec.md](references/agentskills-io-spec.md) | When user chooses AgentSkills.io or both specs |
| Claude Code extensions | [claude-code-extensions.md](references/claude-code-extensions.md) | When user chooses Claude Code or both specs |
| Skill archetypes | [skill-archetypes.md](references/skill-archetypes.md) | During discovery to determine archetype |
| Progressive disclosure | [progressive-disclosure.md](references/progressive-disclosure.md) | When designing reference file structure |
| Common patterns | [patterns-catalog.md](references/patterns-catalog.md) | When designing skill features (teams, routing, sub-agents) |

**Template:**

| Template | Purpose |
|----------|---------|
| [skill-md.md](templates/skill-md.md) | Starting structure for SKILL.md generation |

## Key Principles

1. **Conversation first, structure second** -- Understand the need before proposing an archetype
2. **Progressive disclosure always** -- SKILL.md is the routing layer (<300 lines); details go in reference files
3. **Existing patterns over invention** -- Research and reuse proven patterns from the codebase
4. **Ask about spec target early** -- AgentSkills.io, Claude Code, or both determines available features
5. **One reference file = one topic** -- Keep reference files focused and independently loadable
6. **Route, don't duplicate** -- If framework-skill-builder handles it, delegate

## Conversational Flow

This is a guided conversation, not a rigid pipeline. Cover these areas naturally:

### Phase 0: Upfront Questions

Gather essential context before designing. Ask naturally, not as a form:

**Required (ask these first):**
1. **What does the skill do?** -- Core purpose and when it should trigger
2. **Spec target** -- AgentSkills.io, Claude Code, or both?
3. **Output location** -- Where to save?
   - Claude Code personal: `~/.claude/skills/{name}/`
   - Claude Code project: `.claude/skills/{name}/` (relative to project root)
   - AgentSkills.io: user-specified path
   - Both: one path per spec variant

**Discover through conversation:**
4. Who invokes it? (user via `/command`, model automatically, or both?)
5. Does it need reference files? (complex topics with multiple concerns → yes)
6. Does it need templates? (structured output → yes)
7. Does it need scripts? (executable actions → yes)
8. Does it reference other skills? (which ones?)

### Phase 1: Discovery & Archetype

Read [skill-archetypes.md](references/skill-archetypes.md) to determine the best fit.

Research existing skills if needed:
```
Task tool -> subagent_type: "codebase-researcher"
  Prompt: "Read skill {name} at ~/.claude/skills/{name}/SKILL.md to understand patterns for {topic}"
```

Present the proposed archetype and structure to the user. Get agreement before proceeding.

### Phase 2: Structure Design

Based on the archetype, design the complete directory structure:

```
{skill-name}/
├── SKILL.md
├── references/         (if needed)
│   ├── {topic-1}.md
│   └── {topic-N}.md
├── templates/          (if needed)
│   └── {template}.md
└── scripts/            (if needed)
    └── {script}.py
```

Read the appropriate spec reference:
- AgentSkills.io → [agentskills-io-spec.md](references/agentskills-io-spec.md)
- Claude Code → [claude-code-extensions.md](references/claude-code-extensions.md)
- Both → read both, note the differences

Read [progressive-disclosure.md](references/progressive-disclosure.md) for structuring decisions.
Read [patterns-catalog.md](references/patterns-catalog.md) if the skill uses teams, routing, or sub-agents.

Present the proposed structure (directory tree + SKILL.md outline + reference file topics). Get agreement before building.

### Phase 3: Build

Write all files using [skill-md.md](templates/skill-md.md) as starting structure:

1. **SKILL.md first** -- Entry point and routing layer
2. **Reference files** -- Detailed content for each topic
3. **Templates** -- Structured output formats
4. **Scripts** -- Executable utilities

Reference file rules:
- NO YAML frontmatter (only SKILL.md gets frontmatter)
- H1 title, H2 major sections, `---` between sections
- Code blocks with language tags
- Tables for structured data
- Under 200 lines per file

If generating **both specs**, write:
1. AgentSkills.io version first (portable baseline)
2. Claude Code version second (superset with extensions)
3. Highlight differences to the user

### Phase 4: Review

Walk the user through the generated skill:
- SKILL.md is under 300 lines
- Reference files are focused (one topic each)
- Frontmatter matches chosen spec
- Progressive disclosure is correct (metadata → instructions → resources)
- If both specs: differences are clear

Offer: "The skill is ready. Want me to walk through what it does, or would you like to make changes?"

## When to Ask for Feedback

Always ask before:
- Committing to an archetype
- Finalizing the directory structure
- Writing files (show outline first)

## Spec Quick Reference

### AgentSkills.io
- **Required:** `name`, `description`
- **Optional:** `license`, `compatibility`, `metadata`, `allowed-tools`
- **Name rules:** lowercase + hyphens, 1-64 chars, must match directory name
- **Directories:** `scripts/`, `references/`, `assets/`

### Claude Code (superset)
- **Recommended:** `description` (name defaults to directory name)
- **Additional fields:** `disable-model-invocation`, `user-invocable`, `context`, `agent`, `model`, `hooks`, `argument-hint`
- **Features:** `$ARGUMENTS` substitution, `!`command`` dynamic context, subagent execution
- **Save to:** `~/.claude/skills/{name}/` (personal) or `.claude/skills/{name}/` (project)

### Both Specs
- Generate two skill directories (one per spec)
- AgentSkills.io version: portable, no Claude Code extensions
- Claude Code version: full feature set
- Same core content, different frontmatter and features
