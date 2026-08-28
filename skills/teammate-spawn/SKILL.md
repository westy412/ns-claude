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

Spawn with the `Agent` tool. Always give the agent a `name`. The `name` makes the
agent a teammate. A named agent joins the session team file, and other agents can
address it by that name.

```
Agent:
  name: {agent-name}
  subagent_type: {appropriate type}
  description: {3-5 word label}
  prompt: |
    You are {agent-name}.
    Read your full instructions at:
      {project-path}/teammate-prompts/{workflow-name}/{agent-name}.md
    Follow all steps in order.
```

Do not pass `team_name`. Claude Code removed the `TeamCreate` and `TeamDelete`
tools in v2.1.178. Each session now has one implicit team. The `Agent` tool still
accepts `team_name`, but it ignores the value.

Results arrive as task notifications and as teammate messages. There is no task
list to poll.

If the profile's template includes a skill-loading step, wait for the teammate's
`SendMessage` confirmation before you let it work.

## How teammate messaging works

Teammates send messages to each other with `SendMessage`. The transport is
reliable. The delivery time is not immediate. Follow these rules.

**Messages arrive at turn boundaries.** A teammate receives its messages when its
turn ends. A teammate does not receive a message between the tool calls inside one
turn. The `SendMessage` tool description says that messages "drain at the
receiver's next tool round". That statement is wrong for in-process teammates.

**Never put a wait loop in a brief.** A loop of `sleep` calls stays inside one
turn. The receiver gets nothing and then reports a false negative. In two tests,
receivers polled for 45 seconds and for 200 seconds and received nothing. Each
message arrived immediately after the turn ended.

**Use send-then-finish.** Tell the sender to send the message and then end its
turn. Tell the receiver to end its turn and wait. A new message resumes a finished
teammate. The teammate then reads its full inbox.

**Do not plan a live conversation.** Teammates exchange turns. Two teammates
cannot hold a back-and-forth inside one turn.

**Name every peer in the brief.** A teammate has no `ListAgents` tool and cannot
look up its peers. A system reminder gives it a roster at spawn time, but the
brief must still name the peer to write to.

The receiver sees this wrapper:

```
<teammate-message teammate_id="{sender}" color="{color}" summary="{summary}">
  {message text}
</teammate-message>
```

Each teammate has an inbox file at
`~/.claude/teams/session-{id}/inboxes/{agent-name}.json`. Read that file to debug
a message that a teammate did not report.

## Cleanup

After the team completes:

```bash
rm -rf {project-path}/teammate-prompts/{workflow-name}/
rmdir {project-path}/teammate-prompts/ 2>/dev/null
```
