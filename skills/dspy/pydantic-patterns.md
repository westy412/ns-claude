# Pydantic Patterns

When and how to use Pydantic models with DSPy OutputFields.

## When to Use Pydantic

| Output Type | Use |
|-------------|-----|
| Single string/number | Primitive type directly |
| Single structured object | `BaseModel` |
| List of structured items | `RootModel[List[T]]` |
| Enum with few values (3-10) | `Literal[...]` |
| Enum with many values (20+) | `Union[Literal[...], str]` |

## BaseModel for Single Objects

```python
from pydantic import BaseModel
import dspy

class ContactInfo(BaseModel):
    name: str
    email: str
    score: int

class ExtractorSignature(dspy.Signature):
    """Extract contact information."""
    text: str = dspy.InputField()
    contact: ContactInfo = dspy.OutputField(description="Extracted contact")

# Usage
result = await extractor.acall(text=text)
contact = result.contact  # This is a ContactInfo instance
print(contact.name)       # Direct attribute access
data = contact.model_dump()  # Convert to dict
```

## RootModel for Lists

For list outputs, use `RootModel[List[T]]`:

```python
from pydantic import BaseModel, RootModel
from typing import List
import dspy

class OutreachMessage(BaseModel):
    sequence_number: int
    message: str

# RootModel wraps the list
class OutreachSequence(RootModel[List[OutreachMessage]]):
    pass

class CreationSignature(dspy.Signature):
    """Create outreach messages."""
    context: str = dspy.InputField()
    sequence: OutreachSequence = dspy.OutputField(description="Created messages")

# Usage
result = await creator.acall(context=context)
sequence = result.sequence  # This is an OutreachSequence (RootModel)

# Convert to list of dicts
sequence_data = sequence.model_dump()  # Returns List[dict]

# Access individual items
for msg in sequence.root:  # RootModel stores data in .root
    print(f"Message {msg.sequence_number}: {msg.message[:50]}...")
```

## Complete Production Example

From `ns-cold-outreach-workforce/src/workflows/message_creation/signatures.py`:

```python
from pydantic import BaseModel, RootModel
from typing import List
import dspy

# Define Pydantic models (simple, no validators)
class OutreachMessage(BaseModel):
    """Single message in an outreach sequence."""
    sequence_number: int
    message: str

# For List outputs, use RootModel
class OutreachSequence(RootModel[List[OutreachMessage]]):
    pass

class CreationAgent(dspy.Signature):
    """
    Create personalized B2B outreach messages for a specific lead.

    Generate a sequence of cold outreach messages that follow the provided
    message skeleton while incorporating specific details about the lead.

    CRITICAL: Must contain ZERO em-dash characters. Use commas/periods instead.
    """

    # Inputs
    lead_name: str = dspy.InputField(description="Name of the lead")
    company_name: str = dspy.InputField(description="Company name")
    context: str = dspy.InputField(description="Lead intelligence and context")
    message_skeleton: str = dspy.InputField(description="Template structure")

    # Outputs - use Pydantic models directly
    response: str = dspy.OutputField(description="Explanation of approach")
    sequence: OutreachSequence = dspy.OutputField(description="Created messages")
```

## Why Pydantic Instead of "Output JSON"

| Approach | Problem |
|----------|---------|
| `str` with "output as JSON" | Requires string parsing, no validation |
| Pydantic `BaseModel` | Type safety, validation, clean serialization |

Benefits:
- DSPy natively supports Pydantic in OutputFields
- Type safety at runtime
- Automatic validation
- Better IDE support
- Clean serialization via `.model_dump()`
- No string parsing needed

## Rules

1. **Keep models simple** - No Field validators, just type annotations
2. **Use RootModel for lists** - `RootModel[List[T]]` not `List[T]` directly
3. **Access via .root** - RootModel stores data in `.root` attribute
4. **Serialize with model_dump()** - Convert to dict/list for storage or API responses
5. **Put models in models.py** - Not in signatures.py

## Anti-Patterns

```python
# WRONG: Using str with JSON instruction
class MySignature(dspy.Signature):
    output: str = dspy.OutputField(description="Return as JSON: {name, email}")

# WRONG: List directly without RootModel
class MySignature(dspy.Signature):
    contacts: List[ContactInfo] = dspy.OutputField()  # May have serialization issues

# WRONG: Complex validators in Pydantic models
class ContactInfo(BaseModel):
    email: str

    @validator('email')
    def validate_email(cls, v):  # Don't do this - keep it simple
        if '@' not in v:
            raise ValueError('Invalid email')
        return v
```
