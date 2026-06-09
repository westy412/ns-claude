---
name: teammate-spawn
description: Generates structured teammate prompt files for any agent team workflow. Routes by profile (implementation / review / research / general) to the matching reference + template. Use when spawning sub-agents that need reviewable, file-based briefs.
allowed-tools: Read, Glob, Grep, Write, Bash
---

# Teammate Spawn

Generates file-based prompts for the sub-agents you spawn. Each spawned agent reads its prompt file before starting work — reviewable, consistent, and explicit about ownership and reporting.

**If you are using the `agent-implementation-builder` skill**, use `agent-impl-teammate-spawn` instead — it reads `manifest.yaml` and generates framework-specific prompts with mandatory skill-context confirmation.

## Why file-based prompts

Sub-agents do not inherit the parent's working context. The prompt file IS their brief. Long inline prompts get skimmed, are hard to review before spawning, and dilute the instructions. A file is reviewable up front and read by the agent as its first action.

## Pick a profile (router)

Different sub-agents need different briefs — a read-only reviewer should not carry file-ownership or Git/Linear resumption machinery, and an implementation worker must. Choose the profile that matches the work, read its reference, then fill its template:

| Profile | Use when | Reference | Template |
|---------|----------|-----------|----------|
| `implementation` | the agent edits files, owns a stream, and may need to resume mid-build | `references/implementation.md` | `templates/teammate-prompt-implementation.md` |
| `review` | the agent reviews code or a spec against criteria (read-mostly, may write a findings file) | `references/review.md` | `templates/teammate-prompt-review.md` |
| `research` | the agent explores read-only and returns findings | `references/research.md` | `templates/teammate-prompt-research.md` |
| `general` | structured multi-agent work that fits none of the above | `references/general.md` | `templates/teammate-prompt-general.md` |

**When unsure between `implementation` and `general`:** if the agent owns files and edits them, it's `implementation`.

## Process

1. Pick the profile (table above) and read its reference.
2. Fill its template — skip optional sections that don't apply; a short focused brief beats a long one with empty sections.
3. Write to `{project}/teammate-prompts/{workflow-name}/{agent-name}.md` (create the directory if needed).
4. Spawn the agent with a minimal prompt pointing to the file (see Execution).
5. Collect results when you need them for the next phase; **review the agent's reported output before accepting it.**

## Model policy

Use the default model. Do NOT set a `model` parameter when spawning unless the user explicitly requests one or the task has a clear, justified need.

## Execution

Spawn with the `Task` tool (`team_name`, `name`, `subagent_type`), with a minimal prompt telling the agent to read its prompt file first:

```
Task tool:
  team_name: {team-name}
  name: {agent-name}
  subagent_type: {appropriate type}
  prompt: |
    You are {agent-name} on team {team-name}.
    Read your full instructions at:
      {project-path}/teammate-prompts/{workflow-name}/{agent-name}.md
    Follow all steps in order.
```

If the profile's template includes a skill-loading step, wait for the teammate's `SendMessage` confirmation before letting it work. Collect results via teammate messages / the task list.

## Cleanup

After the team completes:

```bash
rm -rf {project-path}/teammate-prompts/{workflow-name}/
rmdir {project-path}/teammate-prompts/ 2>/dev/null
```
