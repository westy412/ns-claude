# Claude Code Extensions Reference

> **When to read:** When the user wants to create a Claude Code skill, or when adding Claude Code-specific features to a skill.

Claude Code follows the AgentSkills.io open standard and extends it with additional frontmatter fields, string substitutions, dynamic context injection, and subagent execution.

---

## Additional Frontmatter Fields

Beyond the AgentSkills.io base (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`), Claude Code adds:

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `disable-model-invocation` | boolean | `false` | Prevent Claude from automatically loading this skill. User must invoke via `/name`. |
| `user-invocable` | boolean | `true` | Whether skill appears in the `/` menu. Set `false` for background knowledge. |
| `argument-hint` | string | none | Hint shown during autocomplete (e.g., `[issue-number]`, `[filename] [format]`) |
| `context` | string | none | Set to `fork` to run in a forked subagent context |
| `agent` | string | `general-purpose` | Subagent type when `context: fork` is set (e.g., `Explore`, `Plan`, or custom agent name) |
| `model` | string | none | Model to use when this skill is active |
| `hooks` | object | none | Hooks scoped to this skill's lifecycle |

### Invocation Control Matrix

| Frontmatter | User can invoke | Claude can invoke | Context loading |
|-------------|----------------|-------------------|-----------------|
| (default) | Yes | Yes | Description always in context, full skill loads when invoked |
| `disable-model-invocation: true` | Yes | No | Description NOT in context, loads only when user invokes |
| `user-invocable: false` | No | Yes | Description always in context, loads when Claude invokes |

### When to Use Each

- **`disable-model-invocation: true`** -- For workflows with side effects: deploy, commit, send messages. You control when it runs.
- **`user-invocable: false`** -- For background knowledge: legacy system context, coding conventions. Claude loads when relevant but not a meaningful user command.

---

## String Substitutions

Available in skill content for dynamic values:

| Variable | Description | Example |
|----------|-------------|---------|
| `$ARGUMENTS` | All arguments passed when invoking | `/fix-issue 123` → `$ARGUMENTS` = `123` |
| `$ARGUMENTS[N]` | Specific argument by 0-based index | `/migrate Foo React Vue` → `$ARGUMENTS[1]` = `React` |
| `$N` | Shorthand for `$ARGUMENTS[N]` | `$0` = first arg, `$1` = second |
| `${CLAUDE_SESSION_ID}` | Current session ID | Useful for logging, session-specific files |

If `$ARGUMENTS` is not present in skill content and arguments are passed, they are appended as `ARGUMENTS: <value>`.

Example skill using substitutions:

```yaml
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---

Fix GitHub issue $ARGUMENTS following our coding standards.
1. Read the issue description
2. Implement the fix
3. Write tests
4. Create a commit
```

---

## Dynamic Context Injection

The `!`command`` syntax runs shell commands before skill content is sent to the agent. Output replaces the placeholder.

```yaml
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request...
```

This is preprocessing -- each command executes immediately, output replaces the placeholder, and the agent receives the fully-rendered prompt.

---

## Subagent Execution

Add `context: fork` to run a skill in isolation. The skill content becomes the prompt that drives the subagent. It will NOT have access to conversation history.

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:
1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

The `agent` field specifies which subagent type: built-in (`Explore`, `Plan`, `general-purpose`) or custom (from `.claude/agents/`).

> **Note:** `context: fork` only makes sense for skills with explicit task instructions. Guidelines-only skills ("use these conventions") produce no meaningful output in a subagent.

---

## Where Skills Live

| Location | Path | Scope |
|----------|------|-------|
| Enterprise | Managed settings | All users in organization |
| Personal | `~/.claude/skills/{name}/SKILL.md` | All your projects |
| Project | `.claude/skills/{name}/SKILL.md` | This project only |
| Plugin | `{plugin}/skills/{name}/SKILL.md` | Where plugin is enabled |

Priority: enterprise > personal > project. Plugin skills use `plugin-name:skill-name` namespace (no conflicts).

### Auto-Discovery

When working in subdirectories, Claude Code discovers skills from nested `.claude/skills/` directories. Supports monorepo setups where packages have their own skills.

Skills from `--add-dir` directories are also loaded and support live change detection.

---

## Tool Restriction

Use `allowed-tools` to limit what tools the agent can use when a skill is active:

```yaml
---
name: safe-reader
description: Read files without making changes
allowed-tools: Read, Grep, Glob
---
```

Permission rules in `/permissions` can also allow/deny specific skills:
```
Skill(commit)         # Allow exact match
Skill(review-pr *)    # Allow prefix match with any args
Skill(deploy *)       # Deny prefix match
```

---

## Hooks in Skills

Skills can define lifecycle hooks:

```yaml
---
name: my-skill
hooks:
  skill_start:
    - command: echo "Skill started"
  skill_end:
    - command: echo "Skill ended"
---
```

See the hooks documentation for full configuration format.
