# Common Skill Patterns Catalog

> **When to read:** During Phase 2 (Structure Design) when the skill needs team orchestration, routing, sub-agent delegation, or other advanced patterns.

Patterns observed across 30+ existing skills. Use these as building blocks -- don't reinvent what already works.

---

## When to Use / Skip Section

Standard routing section that appears near the top of SKILL.md:

```markdown
## When to Use This Skill

Use this skill when:
- [positive trigger 1]
- [positive trigger 2]

**Skip this skill when:**
- [negative trigger] (use `{alternative-skill}` instead)
- [negative trigger] (use `{alternative-skill}` instead)
```

The "skip" entries form a routing graph between skills. Always name the alternative.

---

## Routing Decision Trees

ASCII trees for skill-internal routing:

```markdown
## Routing

Starting point
├── Condition A?
│   ├── YES → Action or phase
│   └── NO → Continue
├── Condition B?
│   └── YES → Route to skill: "other-skill"
└── Default → Proceed with this skill
```

Use when the skill has branching logic. Keep trees shallow (2-3 levels max).

---

## Reference Files Routing Table

The standard pattern for linking SKILL.md to reference files:

```markdown
## Reference Files

| Topic | Reference File | When to Load |
|-------|---------------|--------------|
| Topic 1 | [file.md](references/file.md) | Specific trigger |
| Topic 2 | [file.md](references/file.md) | Specific trigger |
```

Variations:
- **Phase-linked:** Reference file per phase (workflow skills)
- **Topic-linked:** Reference file per topic (reference skills)
- **Hybrid:** Mix of phases and topics

---

## Child Skill Loading (Just-in-Time)

When a skill invokes other skills during execution:

```markdown
## Child Skills (Just-in-Time Loading)

**CONTEXT BUDGET RULE: Only invoke ONE child skill at a time.**

| Skill | Invoke At | What It Provides |
|-------|-----------|------------------|
| `skill-name` | Phase/step where needed | What knowledge it adds |
```

Loading mechanism:
```
Skill tool → skill: "child-skill-name"
```

---

## Sub-Agent Delegation

When a skill dispatches work to autonomous sub-agents:

```markdown
## Sub-Agents for Delegation

| Sub-Agent | Use For | How to Spawn |
|-----------|---------|--------------|
| codebase-researcher | Understanding existing code patterns | Task tool → subagent_type: "codebase-researcher" |
| web-researcher | External documentation and best practices | Task tool → subagent_type: "web-researcher" |
| prompt-creator | Generating system prompts | Task tool → subagent_type: "prompt-creator" |
```

Sub-agents run in their OWN context windows. Use when:
- Research can happen in parallel
- Work is independent and self-contained
- You want to protect the main context from large results

---

## Team Mode Orchestration

For skills that spawn teams of agents for parallel work:

```
Lifecycle:
1. TeamCreate with team name
2. TaskCreate with tasks for each work stream
3. Generate teammate prompts (teammate-spawn skill or inline)
4. Spawn teammates with Task tool (team_name parameter)
5. Teammates work, communicate via SendMessage
6. TeamDelete when phase/work is complete
7. Clean up prompt files if applicable
```

Use when:
- Multiple independent work streams can execute in parallel
- Work streams have clear boundaries (no shared files)
- The overhead of team setup is justified by parallelism

---

## Upfront Questions Pattern

Gather all input before execution begins:

```markdown
## Upfront Questions

**Gather ALL information before starting execution. No questions during phases.**

**Question 1: [Topic]**
- What to ask
- Default if not provided

**Question 2: [Topic]**
- What to ask
- How to validate

### Validated Input
After gathering:
field_1: type
field_2: type
field_3: type | default
```

Use for skills that need structured input before they can begin (especially team-orchestrated skills where you can't pause mid-execution to ask).

---

## Progress Tracking

For skills that span multiple sessions or have long-running phases:

```markdown
## Progress Tracking

Create `progress-{skill-name}.md` from template at the start.
Update after each phase/step completion.

### Resume Protocol
1. Check for existing progress file
2. Read current phase and state
3. Jump to indicated phase
4. Continue from last checkpoint
```

Template pattern:
```markdown
# Progress: {Skill Name}

## Current Phase: [phase-name]
## Status: [in-progress | blocked | complete]

## Completed
- [x] Phase 1: description
- [ ] Phase 2: description

## Key Decisions
- Decision 1: reasoning
```

---

## Validation Gates

Checkpoints between phases that must pass before continuing:

```markdown
## Phase Completion Checklist

Before moving to Phase N+1:
- [ ] Criterion 1 is met
- [ ] Criterion 2 is verified
- [ ] Output from this phase is saved
- [ ] User has reviewed and approved
```

Use at the end of each phase reference file.

---

## Output Location Patterns

Three approaches for where to save skill output:

| Pattern | When | Example |
|---------|------|---------|
| **Ask the user** | Output location varies | "Where should I save this?" |
| **Default + confirm** | Common convention exists | "I'll save to `~/.claude/skills/{name}/`. OK?" |
| **Hardcoded convention** | Team-wide standard | Always saves to `~/brainstorms/` |

For skill-builder, always ask with a sensible default.

---

## Invoke With / Keywords Line

Inline trigger documentation at the top of SKILL.md body:

```markdown
> **Invoke with:** `/skill-name` | **Keywords:** keyword1, keyword2, keyword3
```

Place immediately after frontmatter, before the description. Helps both users and agents discover the skill.

---

## Template Placeholder Conventions

Two styles in use:

| Style | Syntax | When to use |
|-------|--------|-------------|
| Bracket | `[placeholder-name]` | Simple fill-in-the-blank templates |
| Handlebars | `{{placeholder-name}}` | Templates with conditionals: `{{#if flag}}...{{/if}}` |

Pick one style per skill and use it consistently.

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Wrong | Fix |
|-------------|----------------|-----|
| YAML frontmatter in reference files | Only SKILL.md gets frontmatter | Remove it |
| Reference files > 200 lines | Too much context loaded at once | Split into focused files |
| SKILL.md > 300 lines | Loaded every activation, wastes context | Move details to references |
| Vague "When to Load" triggers | Agent loads files unnecessarily | Use specific triggers |
| Deep reference chains (A → B → C) | Context window bloat | Keep one level deep |
| Loading all child skills at once | Context explosion | Load ONE at a time |
| No routing table in SKILL.md | Agent doesn't know what files exist | Always include one |
