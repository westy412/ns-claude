# Output Type Modifier

## Purpose

Configures whether an agent outputs raw text or structured data (Pydantic models, JSON schemas).

---

## Options

| Type | Description | Use When |
|------|-------------|----------|
| **Text** | Free-form string output | Human consumption, flexible format |
| **Structured** | Validated schema output | Machine parsing, downstream processing |

---

## Text Output

### Characteristics
- Output is a single string
- Format controlled by prompt, not validated
- Flexible but less predictable

### Prompt Adjustments

Use `<output_format>` to describe the expected format:

```xml
<output_format>
Return your response as a bulleted list with:
- Main point first
- Supporting details below
- Keep each bullet to one sentence
</output_format>
```

### When to Use
- Content for humans to read
- Creative or generative tasks
- When format can vary based on content
- Agent-to-agent communication where parsing isn't needed

---

## Structured Output

### Characteristics
- Output matches a defined schema
- Validated by the framework (Pydantic, JSON Schema)
- Predictable and machine-parseable

### Prompt Adjustments

Reference the schema in `<output_format>`:

```xml
<output_format>
Return a JSON object matching this schema:

{
  "sentiment": "positive" | "negative" | "neutral",
  "confidence": 0.0-1.0,
  "key_phrases": ["string", ...],
  "summary": "string (max 100 chars)"
}

All fields are required.
</output_format>
```

### Schema Documentation in Prompts

For complex schemas, document field meanings:

```xml
<output_format>
Return the AnalysisResult schema:

Fields:
- category (string): Primary classification. One of: "bug", "feature", "question", "other"
- priority (int): 1=critical, 2=high, 3=medium, 4=low
- tags (list[str]): Relevant tags, max 5
- reasoning (str): Brief explanation of your classification

Example:
{
  "category": "bug",
  "priority": 2,
  "tags": ["auth", "login"],
  "reasoning": "User reports login failure, which is a high-priority bug"
}
</output_format>
```

### When to Use
- Output feeds into code/automation
- Downstream agents need specific fields
- Validation is important
- Data goes into databases or APIs

---

## Framework Implementation

### LangGraph with Structured Output

```python
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate

class AnalysisResult(BaseModel):
    category: str
    priority: int
    tags: list[str]
    reasoning: str

# Use with_structured_output
llm_with_schema = self.llm.with_structured_output(AnalysisResult)
chain = prompt | llm_with_schema
result = await chain.ainvoke({"input": data})
# result is an AnalysisResult instance
```

### DSPy with Structured Output

```python
import dspy
from pydantic import BaseModel

class AnalysisResult(BaseModel):
    category: str
    priority: int
    tags: list[str]
    reasoning: str

class Analyzer(dspy.Signature):
    """Analyze the input and classify it."""
    input_text: str = dspy.InputField()
    result: AnalysisResult = dspy.OutputField()
```

---

## Hybrid Approach

Some agents need both: structured data plus free-form explanation.

```xml
<output_format>
Return a JSON object with:
{
  "classification": {
    "category": "string",
    "confidence": 0.0-1.0
  },
  "explanation": "Free-form text explaining your reasoning (2-3 sentences)"
}
</output_format>
```

---

## Common Pitfalls

1. **Text when structured is needed** — If you're parsing the output with regex, switch to structured.

2. **Over-structured** — Don't use schemas for simple outputs. A single string is fine.

3. **Schema in prompt doesn't match code** — Keep prompt schema and Pydantic model in sync.

4. **Missing required fields** — Be explicit about which fields are required vs optional.

5. **Enum mismatches** — If a field has specific allowed values, list them explicitly.

---

## Decision Guide

```
Is the output parsed by code?
├── Yes → Structured output
│   └── Is it a simple value (yes/no, category)?
│       ├── Yes → Consider text with strict format
│       └── No → Structured output
└── No → Text output
    └── Does format matter?
        ├── Yes → Define format in <output_format>
        └── No → Minimal format guidance
```
