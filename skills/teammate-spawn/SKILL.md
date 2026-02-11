---
name: teammate-spawn
description: Generates structured teammate prompt files for any agent team workflow. Use when spawning teammates via TeamCreate to provide reviewable, file-based prompts with optional skill loading enforcement.
allowed-tools: Read, Glob, Grep, Write, Bash
---

# Teammate Spawn

Generates file-based teammate prompts for any agent team workflow. Each teammate gets a structured prompt file they read before starting work. Prompts are reviewable, consistent, and optionally enforce skill loading.

**If you are using the agent-implementation-builder skill**, you MUST use `agent-impl-teammate-spawn` instead of this skill. It reads manifest.yaml and generates framework-specific prompts with mandatory skill loading enforcement.

## Why file-based prompts

Teammates do NOT inherit the team lead's context. When spawned, the prompt IS their entire world. Long inline prompts embedded in Task tool calls are:
- Easy for teammates to skim over or ignore sections
- Hard for team leads to review before spawning
- Not visible to users or other agents
- Inconsistent across teammates

File-based prompts solve all of these. The team lead generates a file, can review it, and the teammate reads it as their first action.

## When to use

Use this skill when you are:
- Creating a team with `TeamCreate` and spawning teammates
- Running any multi-agent workflow that isn't agent-implementation-builder
- Coordinating parallel work across multiple sub-agents that need structured instructions

Common workflows this supports:
- **Spec-builder teams** — advisor and writer sub-agents
- **Research orchestration** — parallel research sub-agents
- **Improvement workflows** — analysis and implementation sub-agents
- **Any custom team** — wherever you spawn teammates with the Task tool

## Quick start

For each teammate you need to spawn:

1. Decide what the teammate needs to know (role, tasks, skills, files)
2. Read the template at [templates/teammate-prompt.md](templates/teammate-prompt.md)
3. Fill in the template — skip optional sections that don't apply
4. Write to `{project}/teammate-prompts/{team-name}/{teammate-name}.md`
5. Spawn with a minimal prompt pointing to the file

## Generating a teammate prompt

### Step 1: Define the teammate's context

Gather what this teammate needs. Not all fields apply to every workflow — use what's relevant:

| Field | Required? | Description |
|-------|-----------|-------------|
| Teammate name | Yes | Identifier for this teammate (used in file name, SendMessage) |
| Team name | Yes | From your TeamCreate call |
| Role/responsibility | Yes | What this teammate does |
| Skills to load | Optional | List of skills with exact Skill tool syntax |
| Files they own | Optional | Files they may edit (enforces ownership boundaries) |
| Tasks | Yes | What work they should do, with enough detail to act on |
| Communication | Optional | Who to message, when, with what |
| Validation | Optional | Checklist before marking work complete |
| Reference files | Optional | Files to read for context |

### Step 2: Read and fill the template

Read [templates/teammate-prompt.md](templates/teammate-prompt.md). Fill in the `{{variable}}` placeholders. Delete any optional sections that don't apply — a shorter, focused prompt is better than a long one with empty sections.

### Step 3: Write the prompt file

```
{project-path}/teammate-prompts/{team-name}/{teammate-name}.md
```

Create the directory if it doesn't exist.

### Step 4: Spawn the teammate

```
Task tool:
  team_name: {team-name}
  name: {teammate-name}
  subagent_type: {appropriate type}
  model: {appropriate model}
  prompt: |
    You are teammate {teammate-name} on team {team-name}.

    Read your full instructions at:
      {project-path}/teammate-prompts/{team-name}/{teammate-name}.md

    Follow all steps in order.{if skills: " DO NOT skip Step 1 (Load Required Skills). After loading skills, confirm to team-lead via SendMessage."}
```

### Step 5: Verify skill loading (if skills were specified)

If the teammate's prompt includes skills to load:

1. Wait for their first message — it should confirm skill loading
2. If they skip it, send them back: "Load your required skills first. See Step 1 in your prompt file."
3. Do not let them work until confirmed

If the teammate has no skills to load, they can proceed directly to their tasks.

## Cleanup

After team completion:

```bash
rm -rf {project-path}/teammate-prompts/{team-name}/
rmdir {project-path}/teammate-prompts/ 2>/dev/null
```

## Skill loading: when and how

Skill loading is **optional per teammate**. Include it when:
- The teammate needs domain-specific patterns (agent-teams, individual-agents, prompt-engineering, etc.)
- The teammate will write code that must follow specific conventions
- You've seen teammates produce incorrect output without skills in the past

Skip it when:
- The teammate is doing research or analysis (no skill-specific patterns needed)
- The task is simple enough that general knowledge suffices
- The teammate is a specialized sub-agent type that already has its own context (e.g., prompt-creator)

When you DO include skills, the generated prompt must contain:
1. The exact skill names
2. The exact invocation syntax (`Skill tool -> skill: "name"`)
3. A clear statement that skills must be loaded BEFORE any other work
4. A confirmation message to send to team-lead

This is critical — listing skill names without the invocation syntax means teammates won't know HOW to load them and will skip the step.

## Examples

### Research team (no skills needed)

```
teammate-prompts/content-research/web-researcher.md
```

Prompt includes: role, research questions, output format, where to send results. No skills section.

### Spec-writing team (skills needed)

```
teammate-prompts/agent-spec/team-spec-writer.md
```

Prompt includes: role, skills to load (agent-teams), progress file path, validated decisions, output files. Skills section with exact invocation syntax.

### Parallel batch workers (minimal)

```
teammate-prompts/prompt-batch/agent-creator-1.md
```

Prompt includes: role, agent spec to read, output file to write, skills to load (prompt-engineering). Minimal sections — just what they need.
