# Skill SKILL.md Template

Use this as a starting structure when generating SKILL.md files. Adapt sections based on the skill archetype. Remove sections that don't apply.

---

## AgentSkills.io Version

```yaml
---
name: [skill-name]
description: [What this skill does and when to use it. Include keywords that help agents identify relevant tasks.]
# Optional fields:
# license: [license name or file reference]
# compatibility: [environment requirements]
# metadata:
#   author: [author]
#   version: "[version]"
# allowed-tools: [space-delimited tool list]
---
```

## Claude Code Version (superset)

```yaml
---
name: [skill-name]
description: [What this skill does and when to use it. Include keywords that help agents identify relevant tasks.]
# Optional AgentSkills.io fields:
# license: [license name]
# compatibility: [environment requirements]
# metadata:
#   tags: [comma, separated, tags]
# allowed-tools: [Tool1, Tool2, Tool3]
#
# Claude Code extensions:
# disable-model-invocation: [true if user-only invocation]
# user-invocable: [false if model-only invocation]
# argument-hint: [hint shown in autocomplete, e.g., "[issue-number]"]
# context: [fork - to run in subagent]
# agent: [Explore | Plan | general-purpose | custom-agent-name]
# model: [model override]
---
```

## Body Sections

### Section 1: Invoke Line (optional)

```markdown
> **Invoke with:** `/[skill-name]` | **Keywords:** [keyword1], [keyword2], [keyword3]
```

### Section 2: Description

```markdown
[One-paragraph description of what the skill does.]

**Input:** [What the skill needs from the user]
**Output:** [What the skill produces]
```

### Section 3: When to Use (recommended)

```markdown
## When to Use This Skill

Use this skill when:
- [Positive trigger 1]
- [Positive trigger 2]

**Skip this skill when:**
- [Negative trigger] (use `[alternative-skill]` instead)
```

### Section 4: Routing (if skill has branching logic)

```markdown
## Routing

[ASCII decision tree or routing table]
```

### Section 5: Reference Files (if skill has reference files)

```markdown
## Reference Files

| Topic | Reference File | When to Load |
|-------|---------------|--------------|
| [Topic 1] | [file.md](references/file.md) | [Specific trigger] |
```

### Section 6: Key Principles (recommended)

```markdown
## Key Principles

1. **[Principle name]** -- [Brief explanation]
2. **[Principle name]** -- [Brief explanation]
```

### Section 7: Main Content

Choose based on archetype:

**Workflow:** Phase table + phase summaries
**Reference:** Core concepts + quick reference examples
**Process:** Numbered steps
**Generator:** Generation workflow + output format
**Meta/Router:** Routing decision tree + child skills table

### Section 8: Output (for skills that produce files)

```markdown
## Output

[Directory tree showing what the skill produces]

Output location: [where files are saved]
```

### Section 9: Feedback Points (optional)

```markdown
## When to Ask for Feedback

Always ask before:
- [Decision point 1]
- [Decision point 2]
```
