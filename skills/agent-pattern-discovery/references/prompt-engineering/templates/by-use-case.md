# Prompt Engineering By-Use-Case Template

Use this template when documenting use-case specific prompting guidelines (researcher, critic, generator, etc.).

---

```markdown
# Prompting for [Use Case / Role] Agents

## Overview
[What this agent role does and how prompting supports it]

## Core Directives
[The primary instructions that define this role]
- [Directive 1]
- [Directive 2]
- [Directive 3]

## Skill Map
[Capabilities this agent should embody]
- [Skill 1]
- [Skill 2]
- [Skill 3]

## Context Framing
[How to frame the context for this role]

```
[Example context section]
```

## Task Framing
[How to frame tasks for this role]

```
[Example task section]
```

## Role-Specific Patterns

### [Pattern 1 Name]
**When to use:** [Situation]
**Example:**
```
[Prompt snippet]
```

### [Pattern 2 Name]
**When to use:** [Situation]
**Example:**
```
[Prompt snippet]
```

## Input Handling
[How this role typically receives and processes inputs]
- [Input type 1]: [How to present it]
- [Input type 2]: [How to present it]

## Output Expectations
[What this role typically produces]
- [Output type]: [How to request it]

## Interaction with Other Roles
[How this role typically interacts in a team]
- **Receives from:** [Role] — [What it receives]
- **Passes to:** [Role] — [What it passes]

## Complete Example

```
[Full example prompt for this role]
```

## Pitfalls & Best Practices

**Pitfalls:**
- [Common mistake for this role] — [why it fails]

**Best Practices:**
- [Do this for this role] — [why it works]
```

---

## Template Field Guidance

### Core Directives
- The "soul" of the agent
- What it must always do
- Keep to 3-5 key directives

### Skill Map
- Capabilities, not personality
- Things the agent should be good at
- Informs how it approaches tasks

### Role-Specific Patterns
- Prompting techniques that work especially well for this role
- Show the actual prompt text
- Explain when to use each

### Interaction with Other Roles
- Critical for team context
- What upstream provides
- What downstream expects
- Any transformations between
