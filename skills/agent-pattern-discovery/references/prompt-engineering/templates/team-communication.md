# Prompt Engineering Team Communication Template

Use this template when documenting inter-agent communication patterns.

---

```markdown
# [Communication Pattern Name] (e.g., Production Line, Two-Agent Loop)

## Overview
[How agents communicate in this pattern]

## Message Flow
[What messages pass between agents and how]

```
[Diagram showing message flow]

Agent A Output → [Transform?] → Agent B Input
```

## System Message Patterns

### Agent A (Sender Role)
```
[System message content relevant to sending]
```

### Agent B (Receiver Role)
```
[System message content relevant to receiving]
```

## User Message Construction

### What Agent A Produces
```
[Output format from Agent A]
```

### How It's Transformed (if applicable)
```python
# Transformation code/logic
```

### What Agent B Receives
```
[Input format for Agent B]
```

## Output Curation

### What to Include
- [Element 1]: [Why include]
- [Element 2]: [Why include]

### What to Strip/Remove
- [Element 1]: [Why remove] (e.g., reasoning, chain-of-thought)
- [Element 2]: [Why remove]

### Transformation Patterns
```python
# Example transformation code
```

## Context Passing

### What Context Carries Forward
- [Context element 1]
- [Context element 2]

### What Context Resets
- [Context element 1]
- [Context element 2]

## Handoff Phrasing
[How to phrase the handoff in prompts]

**In Agent A's prompt (sending):**
```
[How to instruct about output for next agent]
```

**In Agent B's prompt (receiving):**
```
[How to instruct about input from previous agent]
```

## Loop-Specific Patterns (if applicable)

### Iteration Context
[How to track/communicate iteration state]
```
[Example]
```

### Feedback Formatting
[How feedback from later agent reaches earlier agent]
```
[Example]
```

### Termination Signaling
[How completion is communicated]
```
[Example]
```

## Complete Example

### Agent A Prompt
```
[Full prompt]
```

### Agent A Output
```
[Example output]
```

### Transformed Message to Agent B
```
[What B actually receives]
```

### Agent B Prompt
```
[Full prompt]
```

## Pitfalls & Best Practices

**Pitfalls:**
- [Common mistake] — [why it breaks communication]

**Best Practices:**
- [Do this] — [why it improves communication]
```

---

## Template Field Guidance

### Output Curation
- This is critical — agents often produce more than the next agent needs
- Be explicit about what to strip (reasoning, metadata, etc.)
- Show the transformation code

### Context Passing
- What state carries through the team
- What resets at each step
- Critical for loops to avoid context explosion

### Handoff Phrasing
- The actual prompt language that makes handoffs work
- Both sending and receiving perspectives
- Make it copy-pasteable

### Loop-Specific
- Only include for loop patterns
- Iteration tracking is crucial
- Feedback formatting prevents confusion
