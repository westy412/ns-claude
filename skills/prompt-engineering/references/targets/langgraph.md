# LangGraph Target

## What You Produce

A prompt string for use in `prompts.py` or as a constant in a LangGraph node definition. The prompt follows the standard XML-section structure from the chosen framework template and gets passed to `ChatPromptTemplate` or used as a system message.

```python
# prompts.py
AGENT_NAME_PROMPT = """
<who_you_are>
...
</who_you_are>

<task>
...
</task>

<output_format>
...
</output_format>
"""
```

## Critical Quirk: Curly Brace Escaping

LangGraph uses `{variable_name}` syntax for template variables in `ChatPromptTemplate`. This means:

**Every literal curly brace in the prompt MUST be escaped by doubling it.**

```python
# WRONG - LangGraph interprets {key} and {value} as template variables
<output_format>
Return JSON: {"key": "value"}
</output_format>

# CORRECT - escaped curly braces
<output_format>
Return JSON: {{"key": "value"}}
</output_format>
```

This applies everywhere in the prompt:
- JSON examples in `<output_format>`
- Code snippets in `<task>` or `<examples>`
- Any literal `{` or `}` character

**Template variables** (intentional, NOT escaped):
```python
<context>
You are analyzing data for {company_name}.
The current date is {current_date}.
</context>
```

Template variables map to state fields or input parameters passed at runtime.

## Template Variable Pattern

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", AGENT_NAME_PROMPT),  # System prompt with {template_vars}
    ("human", "{user_input}"),       # Per-invocation input
])

# Variables are filled from state or direct invocation
chain = prompt | llm
result = chain.invoke({
    "company_name": "Acme Corp",
    "current_date": "2025-01-15",
    "user_input": "Analyze Q4 results"
})
```

Document all template variables in the `<inputs>` section of the prompt so downstream developers know what must be provided.

## Sections

LangGraph prompts use the **full XML-section structure** from the chosen framework template. No sections are skipped.

### Single-Turn (7 sections, all required)
`<who_you_are>` -> `<skill_map>` -> `<context>` -> `<inputs>` -> `<task>` -> `<output_format>` -> `<important_notes>`

### Conversational (10 sections)
`<who_you_are>` -> `<tone_and_style>` -> `<context>` -> `<inputs>` -> `<knowledge_scope>` -> `<capabilities>` -> `<operational_logic>` -> `<examples>` -> `<output_format>` -> `<constraints_and_safeguards>`

### Output Format Section

Unlike DSPy, LangGraph prompts **MUST** include a complete `<output_format>` section because:
- `with_structured_output()` uses the prompt to guide generation alongside the schema
- The prompt schema description and the Pydantic model should match
- Include an example with **escaped curly braces**

```xml
<output_format>
Return a JSON object with these fields:

- "category": One of "bug", "feature", "question", "other"
- "priority": Integer 1-5 (1 = highest)
- "summary": One sentence summary of the issue
- "tags": Array of relevant tags

Example:
{{
  "category": "bug",
  "priority": 2,
  "summary": "Login fails when password contains special characters",
  "tags": ["auth", "security"]
}}
</output_format>
```

## Modifier Adaptations

### Reasoning

Reasoning is a **prompt-level concern** in LangGraph. The full reasoning modifier patterns from `references/modifiers/reasoning.md` apply directly:
- Add "think step by step" or structured reasoning instructions in the prompt text
- Chain-of-Thought, Chain-of-Verification, Step-Back, Tree-of-Thoughts all work as prompt text
- If using structured output, embed reasoning as a field: `"reasoning": "step-by-step analysis..."`

### Tools

Tools are defined with `@tool` decorator or as `BaseTool` subclasses:
- Tool descriptions in the prompt should be consistent with the tool's docstring
- Use `llm.bind_tools([tool1, tool2])` for tool binding
- Prompt should describe tool selection logic in `<operational_logic>` or `<task>`
- Full tool modifier patterns from `references/modifiers/tool-usage.md` apply

### Structured Output

- Use `llm.with_structured_output(PydanticModel)` for validated output
- The prompt's `<output_format>` should describe schema fields with types and allowed values
- Include a JSON example (with escaped curly braces)
- The Pydantic model and prompt description should match

### Memory

Conversation history is handled by chat message passing — not a prompt concern. The LLM receives prior messages as part of the message array, not via prompt instructions.

The memory modifier only applies when there is **long-term or cross-session state** that the agent needs to reference:
- User preferences persisted across sessions
- Accumulated knowledge or summaries from prior interactions
- Session state objects (e.g., collected form data, workflow progress)

If there's no long-term state, skip this modifier entirely. Most LangGraph agents don't need it.

## Tips and Tricks

1. **Escape curly braces first, review last** -- After writing the prompt, do a final pass checking every `{` and `}`. If it's not a template variable, double it.
2. **Document template variables** -- List every `{variable_name}` in the `<inputs>` section with its type and description.
3. **JSON examples need escaping** -- The most common mistake. Every JSON example in `<output_format>` or `<examples>` needs `{{` and `}}`.
4. **System vs Human message split** -- The system message (your prompt) sets role/behavior. The human message provides per-invocation input via template variables.
5. **State field naming** -- Template variables should match the graph's state field names exactly. Document the mapping.
6. **Prompt length** -- No special constraints. Standard prompt lengths from the framework templates apply (300-600 for single-turn, 600-1200 for conversational).

## Checklist

- [ ] All literal curly braces escaped as `{{` and `}}`
- [ ] Template variables `{var_name}` documented in `<inputs>` section
- [ ] JSON examples in `<output_format>` use escaped braces
- [ ] `<output_format>` schema matches the Pydantic model
- [ ] Tool descriptions consistent between prompt and `@tool` docstrings
- [ ] Follows full XML-section structure from framework template
- [ ] Role-specific guidance applied to each section
- [ ] All selected modifiers incorporated
- [ ] Constraints placed in final section (recency effect)
- [ ] No TODOs or placeholders remain
