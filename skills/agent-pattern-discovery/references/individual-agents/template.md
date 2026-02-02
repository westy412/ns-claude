# Individual Agent Documentation Template

Use this template when documenting an agent type. Create separate sections for LangGraph and DSPy implementations.

---

```markdown
# [Agent Type Name]

## What It Is
[1-2 sentence definition of this agent type]

## When to Use
[Situations/problems that call for this type]
- [Situation 1]
- [Situation 2]
- [Situation 3]

## When to Avoid
[When this is the wrong choice]
- [Situation 1] — use [alternative] instead
- [Situation 2] — use [alternative] instead

## Selection Criteria
[Quick decision checklist]
- If [condition] → this type
- If [condition] → consider [other type]
- If [condition] → consider [other type]

## Inputs / Outputs

**Inputs:**
- [Input 1]: [Description]
- [Input 2]: [Description]

**Outputs:**
- [Output 1]: [Description]
- [Output format/schema if relevant]

## Prompting Guidelines
[Quick, type-specific prompting notes — reference full prompting docs for detail]
- [Guideline 1]
- [Guideline 2]
- [Guideline 3]

---

## LangGraph Implementation

### Code Template (LangGraph)

> **Note:** Inline comments are for explanation only. Remove them when using this template.

```python
# [Imports and setup]
[code]

# [State definition if needed]
[code]

# [Agent function/class]
[code]

# [LLM invocation pattern]
[code]

# [Output handling]
[code]
```

### LangGraph-Specific Notes
- [Note about LangGraph implementation]
- [Note about state handling]
- [Note about integration with graphs]

---

## DSPy Implementation

### Code Template (DSPy)

> **Note:** Inline comments are for explanation only. Remove them when using this template.

```python
# [Imports]
[code]

# [Signature definition]
class [SignatureName](dspy.Signature):
    """[Docstring that becomes the prompt]"""
    
    # [Input fields]
    [field]: [type] = dspy.InputField(desc="[description]")
    
    # [Output fields]
    [field]: [type] = dspy.OutputField(desc="[description]")

# [Module definition]
class [AgentName](dspy.Module):
    def __init__(self):
        # [Predictor setup]
        [code]
    
    def forward(self, [inputs]):
        # [Execution logic]
        [code]
```

### DSPy-Specific Notes
- [Note about signature design]
- [Note about field descriptions]
- [Note about module composition]

---

## Pitfalls & Best Practices

**Pitfalls:**
- [Common mistake] — [why it breaks]
- [Common mistake] — [why it breaks]

**Best Practices:**
- [Do this] — [why it works]
- [Do this] — [why it works]
```

---

## Template Field Guidance

### What It Is
- Keep to 1-2 sentences
- Focus on the defining characteristic
- Example: "A one-turn agent that produces structured JSON output conforming to a Pydantic schema."

### When to Use / When to Avoid
- Be specific, not generic
- Include concrete scenarios
- Reference other types when relevant ("use X instead")

### Selection Criteria
- Frame as if/then decisions
- Make it a quick reference, not exhaustive
- Help user choose between similar types

### Inputs / Outputs
- List the typical inputs this agent type receives
- Note schemas or formats if they're part of the type definition
- Don't list every possible input — list what's characteristic

### Prompting Guidelines
- Only type-specific notes here
- Keep brief — full prompting guidance is in prompt-engineering docs
- Example: "Always include JSON schema in prompt for structured output agents"

### Code Template
- Use real code, not pseudocode
- Comments explain WHY, not just WHAT
- Include imports if relevant
- Show the minimal complete example

### Pitfalls & Best Practices
- Draw from actual experience
- Explain the "why" — not just the rule
- Be specific enough to be actionable
