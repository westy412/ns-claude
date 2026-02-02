# Prompt Engineering By-Type Template

Use this template when documenting type-specific prompting guidelines (structured output, tool calling, etc.).

---

```markdown
# Prompting for [Agent Type]

## Overview
[How prompting differs for this agent type]

## Required Elements
[What MUST be in the prompt for this type to work]
- [Element 1]: [Why it's required]
- [Element 2]: [Why it's required]

## Recommended Elements
[What SHOULD be in the prompt for best results]
- [Element 1]: [What it improves]
- [Element 2]: [What it improves]

## Type-Specific Guidelines

### [Guideline 1]
[Explanation]

**Do:**
```
[Good example]
```

**Don't:**
```
[Bad example]
```

### [Guideline 2]
[Explanation]

**Do:**
```
[Good example]
```

**Don't:**
```
[Bad example]
```

## Output Format Instructions
[How to instruct the agent about output format]

```
[Example output format instruction block]
```

## Common Additions to Base Framework
[What sections/elements to add to the One-Turn or Conversational framework for this type]

```
[Additional sections/tags]
```

## Pitfalls & Best Practices

**Pitfalls:**
- [Common mistake] — [why it fails for this type]

**Best Practices:**
- [Do this] — [why it works for this type]
```

---

## Template Field Guidance

### Required vs Recommended Elements
- Required = it won't work without this
- Recommended = it works but results are worse without this

### Type-Specific Guidelines
- Focus on what's DIFFERENT for this type
- Don't repeat universal prompting principles
- Show concrete do/don't examples

### Output Format Instructions
- This is critical for structured output types
- Show the exact language that works
- Include schema definition patterns

### Common Additions
- Show what to add to the base frameworks
- Make it easy to combine with framework docs
