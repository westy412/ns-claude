---
name: agent-impl-teammate-spawn
description: Generates structured teammate prompt files for agent-implementation-builder team mode. Use when spawning teammates to enforce skill loading, provide reviewable prompts, and ensure consistent structure across work streams.
allowed-tools: Read, Glob, Grep, Write, Bash
---

# Agent Implementation Teammate Spawn

Generates file-based teammate prompts for agent-implementation-builder team mode. Each teammate gets a structured prompt file they must read before starting work. This replaces long embedded spawn prompts that teammates skim over and ignore.

## Why this skill exists: The skill loading problem

Teammates DO NOT inherit the team lead's context. When spawned, the prompt IS their entire world. In practice, teammates consistently ignore skill loading instructions embedded in long spawn prompts:

- **Evidence from NS-1158:** 4 of 5 original teammates never loaded required skills. 3 of 3 fixer teammates initially ignored skill loading. Result: every teammate produced incorrect code patterns.
- **Root cause:** Skills contain critical implementation patterns, anti-patterns, and canonical examples. Without them, teammates generate code based on general knowledge which produces subtly wrong implementations that compile but behave incorrectly.

**The generated prompt file MUST:**
1. List the EXACT skills to load by name
2. Show the EXACT syntax for loading each skill (the `Skill` tool call)
3. Make skill loading Step 1 before any other work
4. Require confirmation to team lead before proceeding
5. State clearly WHY skipping skills will cause implementation failure

If the generated prompt does not explicitly tell the teammate what skills to load and how to load them, the implementation WILL fail. This is not a suggestion — it is the entire reason this skill exists.

## Quick start

For each stream that needs a teammate:

1. Gather stream data from `manifest.yaml` and `agent-config.yaml`
2. Read the template at [templates/teammate-prompt.md](templates/teammate-prompt.md)
3. Fill in the template variables with stream-specific data
4. Write to `{project}/teammate-prompts/{team-name}/{stream-name}.md`
5. Spawn the teammate with a minimal prompt pointing to the file

## What you need before generating

| Data | Source |
|------|--------|
| Stream name, responsibility, owns, skills | `manifest.yaml` -> `execution-plan.streams` |
| Phases and chunks for this stream | `manifest.yaml` -> `execution-plan.phases` (filter by stream) |
| Communication rules | `manifest.yaml` -> `execution-plan.communication` |
| Framework | `agent-config.yaml` -> `team.framework` |
| Team name | Your `TeamCreate` call |
| Project path | Absolute path to the project |
| Spec path | Relative path to spec directory (usually `spec/`) |
| Task IDs | Your `TaskCreate` results (map chunks to task IDs) |

## Step-by-step generation

### Step 1: Read the stream definition

From `manifest.yaml`, extract the target stream:

```yaml
streams:
  - name: research
    responsibility: Research team modules and sub-agent implementations
    owns: [src/research/]
    skills: [agent-teams, individual-agents]
```

### Step 2: Filter phases for this stream

From `manifest.yaml`, find all chunks where `chunk.stream == this stream`:

```yaml
phases:
  - phase: 2
    name: Sub-Team Modules
    chunks:
      - name: research-modules
        stream: research          # matches
        spec-files:
          - research-team/team.md
          - research-team/agents/search-agent.md
```

### Step 3: Determine required skills (CRITICAL)

Every stream that writes agent code MUST have skills assigned. If you skip this step or assign the wrong skills, the teammate will produce incorrect code.

If the stream has `skills` in manifest.yaml, use those. Otherwise, apply this default mapping based on `stream.owns`:

| Stream Pattern | Owns | Required Skills |
|---------------|------|----------------|
| models | `src/models.py`, `src/schemas/` | (none) |
| tools | `src/tools/`, `tools.py` | tools-and-utilities |
| signatures | `src/signatures/` (DSPy) | prompt-engineering, individual-agents |
| prompts | `src/prompts/`, `prompts.py` (LangGraph) | prompt-engineering |
| agents | agent implementation files | individual-agents |
| team/orchestration | `team.py`, `pipeline.py` | agent-teams |
| scaffold/root | root pipeline, FastAPI wrapper | agent-teams |

When filling the template, the `{{skill-invocations}}` variable MUST generate the exact Skill tool syntax for each skill. Not just the skill names — the actual invocation the teammate should use. Example for a stream with `[agent-teams, individual-agents]`:

```
You MUST use the Skill tool to load each of these skills BEFORE doing any other work:

  Skill tool -> skill: "agent-teams"
  Skill tool -> skill: "individual-agents"

These skills contain the implementation patterns you need. Without them you WILL write incorrect code.
After loading ALL skills, send a message to team-lead confirming: "Skills loaded: agent-teams, individual-agents"
```

Do NOT just list skill names. Do NOT assume the teammate knows how to invoke the Skill tool. Spell it out explicitly every time.

### Step 4: Read and fill the template

Read [templates/teammate-prompt.md](templates/teammate-prompt.md). Fill in all `{{variable}}` placeholders with the data gathered above. See [Template variable reference](#template-variable-reference) for the complete list.

For the `{{validation-checklist}}` variable, use the appropriate framework checklist below:

**DSPy validation checklist:**
- [ ] All spec inputs have corresponding InputField or function parameter
- [ ] All spec outputs have corresponding OutputField or return type
- [ ] Typed outputs used — NO str + JSON parsing patterns
- [ ] Both forward() and aforward() methods implemented
- [ ] aforward() uses await agent.acall() with call_with_retry
- [ ] Singleton LM used (get_flash_lm(), get_pro_lm()) — NOT dspy.LM() directly
- [ ] Model tier matches spec (Flash vs Pro)
- [ ] DSPy module type matches spec (ReAct / Predict / ChainOfThought)
- [ ] All imports work: `uv run python -c "from ... import ..."`
- [ ] Sent required data to downstream streams per Communication Requirements

**LangGraph validation checklist:**
- [ ] All spec inputs present in State TypedDict
- [ ] All spec outputs present in State TypedDict
- [ ] ToolNode added as a separate graph node — NOT created inside agent functions
- [ ] Graph compiled before use
- [ ] All node functions return State dict
- [ ] Model tier matches spec (Haiku vs Sonnet vs Opus)
- [ ] Prompt template matches agent role from spec
- [ ] All imports work: `uv run python -c "from ... import ..."`
- [ ] Sent required data to downstream streams per Communication Requirements

### Step 5: Write the prompt file

Create the directory and write the file:

```
{project-path}/teammate-prompts/{team-name}/{stream-name}.md
```

### Step 6: Spawn the teammate

Use a minimal spawn prompt:

```
Task tool:
  team_name: {team-name}
  name: {stream-name}
  subagent_type: general-purpose
  model: opus (for complex streams) or sonnet
  prompt: |
    You are teammate {stream-name} on team {team-name}.

    Read your full instructions at:
      {project-path}/teammate-prompts/{team-name}/{stream-name}.md

    Follow ALL steps in order. DO NOT skip Step 1 (Load Required Skills).
    After loading skills, confirm to team-lead via SendMessage.
```

### Step 7: Verify skill loading (MANDATORY — DO NOT SKIP)

This is the enforcement mechanism. Without this step, teammates will skip skill loading and produce broken code.

After spawning all teammates:

1. Wait for the first message from each teammate
2. The message MUST confirm skill loading with the specific skill names (e.g., "Skills loaded: agent-teams, individual-agents")
3. If the first message is about anything other than skill loading — the teammate skipped Step 1. Send them back:
   > "STOP. You must load your required skills before doing any work. Go back to Step 1 in your prompt file at {path}. Use the Skill tool to load each skill listed there. Confirm to me when done."
4. Do NOT assign tasks, do NOT allow work to begin, do NOT respond to implementation questions until skills are confirmed
5. If a teammate claims a task without confirming skills — revoke it immediately and enforce loading

## Cleanup

After team completion (after `TeamDelete`):

```bash
rm -rf {project-path}/teammate-prompts/{team-name}/
rmdir {project-path}/teammate-prompts/ 2>/dev/null
```

## Template variable reference

Variables in [templates/teammate-prompt.md](templates/teammate-prompt.md):

| Variable | Source | Example |
|----------|--------|---------|
| `{{team-name}}` | TeamCreate team_name | `idea-agents-impl` |
| `{{project-path}}` | Project absolute path | `/Users/.../project` |
| `{{spec-path}}` | Spec directory | `spec/` |
| `{{framework}}` | agent-config.yaml `team.framework` | `dspy` |
| `{{stream-name}}` | Stream name from manifest | `research` |
| `{{stream-responsibility}}` | `streams[].responsibility` | `Research team modules` |
| `{{stream-owns}}` | `streams[].owns` (bulleted list) | `- src/research/` |
| `{{skill-invocations}}` | Generated from skills list | One `Skill tool` call per skill |
| `{{cheatsheet-path}}` | Derived from framework | `~/.claude/skills/.../CHEATSHEET.md` |
| `{{cheatsheet-focus}}` | Framework-dependent key sections | DSPy: `Typed Outputs, Singleton LM` |
| `{{hierarchy-position}}` | From manifest hierarchy | Level, parent, children, contracts |
| `{{phases-for-stream}}` | Filtered phases/chunks with task IDs and spec-files | Markdown checklist per phase |
| `{{communication-outbound}}` | communication where `from == stream` | What to send after phases |
| `{{communication-inbound}}` | communication where `to == stream` | What to expect from others |
| `{{validation-checklist}}` | Framework checklist from Step 4 above | Framework-specific items |
| `{{first-chunk-spec-files}}` | First chunk's `spec-files` | Bulleted list of spec paths |
