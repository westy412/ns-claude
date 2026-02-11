# DSPy Skill

Guide for working with DSPy using Novosapien conventions and production-tested patterns.

## When to Use

- Writing DSPy code directly
- Designing DSPy signatures
- Debugging DSPy workflows
- Learning DSPy best practices
- Working with DSPy outside of agent-spec-builder/agent-implementation-builder

## Quick Start

1. **File organization**: See [file-organization.md](file-organization.md)
2. **Pydantic usage**: See [pydantic-patterns.md](pydantic-patterns.md)
3. **Critical patterns**: [singleton-lm.md](singleton-lm.md), [signatures.md](signatures.md), [predictor-selection.md](predictor-selection.md)

## Core Patterns

| Pattern | File | One-Line Summary |
|---------|------|------------------|
| File Organization | [file-organization.md](file-organization.md) | Signatures in signatures.py, NOT models.py |
| Pydantic Models | [pydantic-patterns.md](pydantic-patterns.md) | BaseModel for single objects, RootModel for lists |
| Singleton LM | [singleton-lm.md](singleton-lm.md) | One shared LM prevents 20x slowdown at scale |
| Signatures | [signatures.md](signatures.md) | Docstrings ARE prompts - make them comprehensive |
| Predictor Selection | [predictor-selection.md](predictor-selection.md) | Predict for extraction, ChainOfThought for synthesis |
| Enum Handling | [enum-handling.md](enum-handling.md) | Small enums: prompting. Large enums: Union + fuzzy |
| Formatters | [formatters.md](formatters.md) | Convert Predictions to markdown between stages |
| Retry Patterns | [retry-patterns.md](retry-patterns.md) | Exponential backoff + rate limit handling |
| History Patterns | [history-patterns.md](history-patterns.md) | dspy.History for multi-turn conversations |

## Anti-Patterns (Quick Reference)

```python
# WRONG: Creating LM per module
class MyModule(dspy.Module):
    def __init__(self):
        self.lm = dspy.LM("gemini/...")  # Causes connection exhaustion

# WRONG: Signatures in models.py
# models.py
class MySignature(dspy.Signature):  # Should be in signatures.py
    """..."""

# WRONG: Brief docstrings
class MySignature(dspy.Signature):
    """Extract data."""  # Too brief, DSPy needs comprehensive instructions

# WRONG: ChainOfThought for extraction
self.extractor = dspy.ChainOfThought(...)  # Use Predict for extraction

# WRONG: Strict Literal for large enums
industry: Literal[...50 values...]  # Use Union[Literal[...], str] for 20+ values

# WRONG: Passing raw Predictions between stages
stage2 = self.analyzer(previous=stage1_result)  # Format to markdown first
```

## Common Imports

```python
# DSPy Core
import dspy
from dspy import Signature, InputField, OutputField, Predict, ChainOfThought, Module

# Type Hints for Signatures
from typing import Literal, Union, List, Optional, Any

# Pydantic (for complex nested outputs)
from pydantic import BaseModel, RootModel

# Async utilities
import asyncio
import os

# Configuration at module level (BEFORE any async code)
dspy.settings.configure(async_max_workers=2000)
```

## References

### Agent Types
See [references/agent-types.md](references/agent-types.md) for links to:
- Basic Agent (Predict)
- Reasoning Agent (ChainOfThought)
- Conversational Agent (dspy.History)
- Tool Agent (ReAct)

### Team Patterns
See [references/team-patterns.md](references/team-patterns.md) for links to:
- Pipeline
- Loop (Creator-Critic)
- Fan-in-Fan-out
- Router

### Full Cheatsheet
For comprehensive reference: `~/.claude/skills/agent-implementation-builder/frameworks/dspy/CHEATSHEET.md`

## Related Skills

- **agent-spec-builder**: Design complete agent systems with DSPy implementation
- **agent-implementation-builder**: Build full agent teams from specifications
- **individual-agents**: Detailed patterns for each agent type
- **agent-teams**: Team topology patterns with DSPy implementations
