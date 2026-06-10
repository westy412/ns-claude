# Enum Handling

Two-tier strategy for enum fields based on the number of valid values.

## The Problem

LLMs output close-but-not-exact enum values:
- "Denmark" instead of "Nordics"
- "SaaS" instead of "B2B SaaS"
- "Pay-as-you-go" instead of "Usage-based"

Without proper handling, Pydantic validation fails and aborts the workflow.

## Two-Tier Strategy

| Enum Size | Strategy |
|-----------|----------|
| **Small (3-10 values)** | Good prompting only. LLMs handle small enums reliably. |
| **Large (20+ values)** | `Union[Literal[...], str]` + fuzzy matching as safety net |

## Small Enums (3-10 values)

For small enums, strict `Literal` with good prompting is sufficient:

```python
class RouterSignature(dspy.Signature):
    """
    Classify input into a category.

    Output EXACTLY one of: technical, business, support, general
    """
    input_text: str = dspy.InputField()

    # Strict Literal is fine for small enums
    category: Literal["technical", "business", "support", "general"] = dspy.OutputField(
        description="EXACTLY one of: technical, business, support, general"
    )
```

**Why it works:** With 3-10 options and explicit prompting, LLMs are reliable.

## Large Enums (20+ values)

For large enums, use `Union` as a safety net with fuzzy matching as LAST RESORT:

```python
from typing import Literal, Union
import dspy

class MySignature(dspy.Signature):
    """
    Extract company information.

    ENUM FIELD: industry
    VALID VALUES: B2B SaaS, B2C Software, Enterprise Software, IT Services & Consulting,
    Financial Services, Healthcare, Manufacturing, Telecommunications, Cybersecurity,
    Marketing Agency, Legal Services, ... (50+ options)
    """

    # Large enum: Union allows any string as safety net
    industry: Union[Literal[
        "B2B SaaS", "B2C Software", "Enterprise Software",
        "IT Services & Consulting", "Financial Services",
        "Healthcare", "Manufacturing", "Telecommunications",
        # ... many more values
        "Other", "Unknown"
    ], str] = dspy.OutputField(
        description="Select the closest industry from the VALID VALUES list above."
    )
```

## Fuzzy Matching (LAST RESORT)

Only use fuzzy matching for large enums where LLM mistakes are common:

```python
from difflib import get_close_matches

def normalize_enum_output(output, valid_values: list, field_name: str) -> str:
    """
    Normalize LLM output to closest valid enum value using fuzzy matching.

    USE ONLY FOR LARGE ENUMS (20+ values) where LLM mistakes are common.
    For small enums, rely on good prompting instead.
    """
    value = getattr(output, field_name)
    if value in valid_values:
        return value

    # Fuzzy match to closest valid value
    matches = get_close_matches(value, valid_values, n=1, cutoff=0.6)
    if matches:
        corrected = matches[0]
        setattr(output, field_name, corrected)
        print(f"Normalized {field_name}: '{value}' -> '{corrected}'")
        return corrected

    # Fallback to "Other" or "Unknown"
    fallback = "Unknown" if "Unknown" in valid_values else valid_values[-1]
    setattr(output, field_name, fallback)
    return fallback
```

## Usage in Pipeline

```python
class ExtractionPipeline(dspy.Module):
    VALID_INDUSTRIES = [
        "B2B SaaS", "B2C Software", "Enterprise Software",
        "IT Services & Consulting", "Financial Services",
        # ... 50+ values
        "Other", "Unknown"
    ]

    async def aforward(self, website_content: str):
        result = await self.extractor.acall(content=website_content)

        # Only normalize for large enums
        if len(self.VALID_INDUSTRIES) > 20:
            normalize_enum_output(result, self.VALID_INDUSTRIES, "industry")

        return result
```

## Anti-Patterns

```python
# WRONG: Strict Literal for large enums
industry: Literal[
    "B2B SaaS", "B2C Software", "Enterprise Software",
    # ... 50 more values
] = dspy.OutputField()  # Will fail on variations like "Denmark"

# WRONG: Using fuzzy matching for small enums
# If you have 4 options, just prompt well - no need for normalization
category: Literal["A", "B", "C", "D"]
normalize_enum_output(result, ["A", "B", "C", "D"], "category")  # Unnecessary

# WRONG: Union for small enums
# Adds unnecessary complexity when prompting is sufficient
category: Union[Literal["A", "B", "C", "D"], str]  # Just use Literal
```

## Prompting Best Practices

In the signature docstring, include:

```python
"""
=== ENUM FIELD COMPLIANCE ===

ENUM FIELD: industry
VALID VALUES: B2B SaaS, B2C Software, Enterprise Software, IT Services, Other, Unknown

**WHY THIS MATTERS:**
Your output is parsed by downstream systems that perform EXACT STRING MATCHING.
If you output ANY value not in the valid options list, the workflow may fail.

**REQUIREMENTS:**
- Output EXACTLY one of the listed valid options
- DO NOT output variations (e.g., "SaaS" instead of "B2B SaaS")
- DO NOT output synonyms (e.g., "Consulting" instead of "IT Services")
- If uncertain, use "Other" or "Unknown" - these are ALWAYS safer
"""
```

## Decision Flow

```
Is enum size <= 10?
├── YES → Use strict Literal + good prompting
└── NO (20+ values)
    ├── Use Union[Literal[...], str]
    └── Add fuzzy matching normalization as safety net
```

## Error Without Union (Large Enums)

```
ValidationError: 1 validation error for MySignature
industry
  Input should be 'B2B SaaS', 'B2C Software', ... (received: 'Denmark')
```
