# File Organization

DSPy has specific file organization rules that differ from other frameworks.

## Directory Structure

```
src/team-name/
├── signatures.py    # All DSPy Signature classes - REQUIRED
├── models.py        # Pydantic models (optional, for complex outputs)
├── tools.py         # Tool functions (if agents use tools)
├── utils.py         # Singleton LM + formatters + retry - REQUIRED
└── team.py          # dspy.Module orchestration
```

## Key Rules

### 1. Signatures in signatures.py (NEVER in models.py)

```python
# signatures.py - ALL signatures go here

import dspy
from typing import Literal

class AgentASignature(dspy.Signature):
    """
    THIS DOCSTRING IS THE PROMPT.

    DSPy compiles this docstring directly into the LLM call.
    Do NOT create a separate prompts.py file.

    === YOUR ROLE IN THE WORKFLOW ===
    You are Agent A in a pipeline...
    """

    raw_input: str = dspy.InputField(desc="Input text to analyze")
    category: Literal["A", "B", "C"] = dspy.OutputField(
        desc="EXACTLY one of: A, B, C"
    )
```

### 2. Pydantic Models in models.py

```python
# models.py - ONLY Pydantic models, NOT signatures

from pydantic import BaseModel, RootModel
from typing import List

class ContactInfo(BaseModel):
    """Complex nested output structure."""
    name: str
    email: str
    score: int

class ContactList(RootModel[List[ContactInfo]]):
    pass
```

### 3. Team Orchestration in team.py

```python
# team.py - Import signatures from signatures.py

from .signatures import AgentASignature, AgentBSignature
from .utils import get_shared_lm

class MyTeam(dspy.Module):
    def __init__(self, shared_lm):
        self.agent_a = dspy.Predict(AgentASignature)
        self.agent_a.set_lm(shared_lm)
```

### 4. NO prompts.py for DSPy

DSPy compiles signature docstrings directly into prompts. Creating separate prompts.py files:
- Creates confusion about which prompt is used
- Wastes context
- Doesn't integrate with DSPy's optimization

## Anti-Patterns

```python
# WRONG: Signatures in models.py
# models.py
import dspy

class AgentASignature(dspy.Signature):  # WRONG LOCATION
    """..."""

# WRONG: Creating prompts.py for DSPy
# prompts.py
AGENT_A_PROMPT = """..."""  # WRONG - DSPy doesn't use this pattern

# WRONG: Brief docstrings
class AgentASignature(dspy.Signature):
    """Extract data."""  # WRONG - Too brief, needs comprehensive instructions
```

## File Placement Summary

| File | DSPy | LangGraph |
|------|------|-----------|
| signatures.py | YES - all signatures with docstring prompts | NO |
| prompts.py | NO - don't create | YES - separate prompt strings |
| models.py | Optional - only for complex Pydantic outputs | Optional - same |
| utils.py | YES - singleton LM + formatters required | Optional |

## Why This Organization?

1. **Separation of concerns**: Signatures (contracts) separate from models (data structures) and orchestration (logic)

2. **Docstrings ARE prompts**: No ambiguity about where prompts live

3. **Reusability**: Signatures can be imported by any team.py that needs them

4. **Optimization-ready**: DSPy's optimization works on signatures.py directly
