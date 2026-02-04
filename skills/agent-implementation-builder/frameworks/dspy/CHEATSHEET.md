# DSPy Implementation Cheat Sheet

**Read this BEFORE implementing any DSPy code.**

This cheat sheet contains critical rules, patterns, and anti-patterns for DSPy implementations based on production-tested patterns from real concurrent workflows.

---

## Quick Reference

| Rule | One-Line Description |
|------|---------------------|
| 1. Signatures in signatures.py | All DSPy Signatures live in signatures.py (NOT models.py) |
| 2. Docstrings ARE Prompts | Signature docstrings are compiled into LLM calls - NO separate prompts.py |
| 3. Singleton LM | Use module-level singleton for shared LM instance |
| 4. Predict vs ChainOfThought | Predict for extraction/classification, CoT for creative synthesis |
| 5. Enum Validation | Small enums: prompting. Large enums (20+): `Union` + fuzzy matching |
| 6. Rich Docstrings | Workflow context + validation rules + anti-patterns |
| 7. Formatters | Convert structured outputs to markdown between stages |
| 8. Async Retry | Exponential backoff + rate limit handling |

---

## Critical Rules

### 0. File Organization and Signatures

**CRITICAL: DSPy has specific file organization rules that differ from LangGraph.**

**File Structure:**
```
src/team-name/
├── signatures.py    # All DSPy Signature classes - REQUIRED
├── models.py        # Pydantic models (optional, for complex outputs)
├── tools.py         # Tool functions (if agents use tools)
├── utils.py         # Singleton LM + formatters + retry - REQUIRED
└── team.py          # dspy.Module orchestration
```

**CORRECT:**
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
    You are Agent A in a pipeline. You receive raw input and extract
    structured data for downstream agents.

    === YOUR TASK ===
    Extract the following fields from the input text...

    [... Comprehensive prompt continues ...]
    """

    raw_input: str = dspy.InputField(desc="Input text to analyze")
    category: Literal["A", "B", "C"] = dspy.OutputField(
        desc="EXACTLY one of: A, B, C"
    )


class AgentBSignature(dspy.Signature):
    """
    THIS DOCSTRING IS THE PROMPT.

    === YOUR ROLE IN THE WORKFLOW ===
    You are Agent B. You receive formatted output from Agent A...

    [... Comprehensive prompt continues ...]
    """

    agent_a_output: str = dspy.InputField(desc="Formatted output from Agent A")
    result: str = dspy.OutputField(desc="Final result")
```

```python
# models.py - ONLY Pydantic models, NOT signatures

from pydantic import BaseModel

class ComplexOutput(BaseModel):
    """Complex nested output structure."""
    field1: str
    field2: int
    nested: dict
```

```python
# team.py - Import signatures from signatures.py

from .signatures import AgentASignature, AgentBSignature

class MyTeam(dspy.Module):
    def __init__(self, shared_lm):
        self.agent_a = dspy.Predict(AgentASignature)
        self.agent_a.set_lm(shared_lm)
```

**WRONG - DO NOT DO THIS:**
```python
# WRONG: Signatures in models.py
# models.py
import dspy

class AgentASignature(dspy.Signature):  # WRONG LOCATION
    """..."""
```

```python
# WRONG: Creating prompts.py for DSPy
# prompts.py
AGENT_A_PROMPT = """..."""  # WRONG - DSPy doesn't use this pattern
```

```python
# WRONG: Brief docstrings
class AgentASignature(dspy.Signature):
    """Extract data."""  # WRONG - Too brief, DSPy needs comprehensive instructions

    raw_input: str = dspy.InputField()
    output: str = dspy.OutputField()
```

**Why:**

1. **signatures.py is the correct location** - Separates signature definitions (contracts) from Pydantic models (data structures) and team orchestration (logic).

2. **Docstrings ARE prompts** - DSPy compiles signature docstrings directly into the LLM prompt. Creating separate prompts.py files creates confusion about which prompt is actually used and wastes context.

3. **Comprehensive docstrings required** - Brief docstrings like "Extract data" produce poor outputs. Include workflow context, quality standards, constraints, and anti-patterns directly in the docstring.

4. **No prompt-creator sub-agents for DSPy** - Since prompts are docstrings, write them directly when creating signatures.py. Using prompt-creator sub-agents adds unnecessary complexity and may produce prompts that don't integrate properly with the signature structure.

**File placement summary:**

| File | DSPy | LangGraph |
|------|------|-----------|
| signatures.py | YES - contains all signatures with docstring prompts | NO |
| prompts.py | NO - don't create | YES - separate prompt strings |
| models.py | Optional - only for complex Pydantic outputs | Optional - same |
| utils.py | YES - singleton LM + formatters required | Optional |

---

### 1. Singleton LM Pattern

**CORRECT:**
```python
# Module-level singleton (workflow.py)
_shared_lm = None

def get_shared_lm():
    """
    Get or create singleton LM instance.

    CRITICAL: Prevents 20x slowdown when running 100+ concurrent workflows.
    Without this, each workflow creates its own HTTP client, exhausting connections.
    """
    global _shared_lm
    if _shared_lm is None:
        _shared_lm = dspy.LM(
            "gemini/gemini-2.5-flash",
            api_key=os.getenv("GOOGLE_API_KEY"),
            max_parallel_requests=2000,  # Critical for concurrency
        )
    return _shared_lm


# In your module class
class MyPipeline(dspy.Module):
    def __init__(self, shared_lm):
        if shared_lm is None:
            raise ValueError(
                "MyPipeline requires a shared_lm instance. "
                "Pass get_shared_lm() to enable connection pooling."
            )

        self.lm = shared_lm

        # Create predictors
        self.agent_a = dspy.Predict(AgentASignature)
        self.agent_b = dspy.Predict(AgentBSignature)

        # CRITICAL: Inject singleton into ALL predictors
        self.agent_a.set_lm(self.lm)
        self.agent_b.set_lm(self.lm)
```

**WRONG - DO NOT DO THIS:**
```python
class MyPipeline(dspy.Module):
    def __init__(self):
        # WRONG: Creating LM instance per module
        self.lm = dspy.LM("gemini/gemini-2.5-flash")

        self.agent_a = dspy.Predict(AgentASignature)
        # WRONG: Not calling set_lm() - uses global default
```

**Why:** Creating separate LM instances causes connection pool exhaustion at scale. Running 100+ concurrent workflows without singleton causes 20x slowdown due to lack of HTTP connection pooling (LiteLLM + aiohttp session management).

**Error you'll see at scale:**
```
httpcore.ConnectError: [Errno 24] Too many open files
```
or:
```
httpx.HTTPStatusError: 429 Too Many Requests
```

---

### 2. Predict vs ChainOfThought Selection

**Decision Logic:**

| Use | When | Example Tasks |
|-----|------|---------------|
| `dspy.Predict` | Structured extraction, classification, evaluation | Data extraction, category matching, checklist evaluation |
| `dspy.ChainOfThought` | Creative synthesis, complex reasoning | Content generation, multi-input synthesis |

**CORRECT:**
```python
class MyPipeline(dspy.Module):
    def __init__(self, shared_lm):
        # EXTRACTION TASKS - Use Predict (faster, cheaper)
        self.data_extractor = dspy.Predict(DataExtractorSignature)
        self.categorizer = dspy.Predict(CategorizerSignature)
        self.ranker = dspy.Predict(RankerSignature)
        self.critic = dspy.Predict(CriticSignature)  # Evaluation is a checklist

        # CREATIVE TASKS - Use ChainOfThought (shows reasoning)
        self.content_creator = dspy.ChainOfThought(CreatorSignature)
```

**WRONG - DO NOT DO THIS:**
```python
class MyPipeline(dspy.Module):
    def __init__(self, shared_lm):
        # WRONG: ChainOfThought everywhere adds unnecessary latency/cost
        self.data_extractor = dspy.ChainOfThought(DataExtractorSignature)
        self.categorizer = dspy.ChainOfThought(CategorizerSignature)
        self.ranker = dspy.ChainOfThought(RankerSignature)
```

**Why:** ChainOfThought adds a reasoning step that increases token usage and latency. For structured extraction (extracting specific fields from text) or classification (matching to predefined categories), the reasoning step provides minimal benefit. Reserve ChainOfThought for tasks where visible reasoning improves output quality.

---

### 3. Enum Validation with Union Types

**Problem:** LLMs output close-but-not-exact enum values (e.g., "Denmark" instead of "Nordics", "SaaS" instead of "B2B SaaS"), causing Pydantic validation to fail and abort the workflow.

**Two-Tier Approach:**

| Enum Size | Strategy |
|-----------|----------|
| **Small (3-10 values)** | Good prompting only. LLMs handle small enums reliably. |
| **Large (20+ values)** | `Union[Literal[...], str]` + fuzzy matching as safety net |

**SMALL ENUMS - Prompting is sufficient:**
```python
class RouterSignature(dspy.Signature):
    """
    Classify input into a category.

    Output EXACTLY one of: technical, business, support, general
    """
    input_text: str = dspy.InputField()

    # For small enums, strict Literal is fine with good prompting
    category: Literal["technical", "business", "support", "general"] = dspy.OutputField(
        description="EXACTLY one of: technical, business, support, general"
    )
```

**LARGE ENUMS - Union + fuzzy matching as last resort:**
```python
from typing import Literal, Union, List
import dspy

class MySignature(dspy.Signature):
    """
    Extract company information.

    ENUM FIELD: industry
    VALID VALUES: B2B SaaS, B2C Software, Enterprise Software, IT Services & Consulting,
    Financial Services, Healthcare, Manufacturing, Telecommunications, Cybersecurity,
    Marketing Agency, Legal Services, ... (50+ options)
    """

    # Large enum (50+ values): Union allows any string, normalize afterward
    industry: Union[Literal[
        "B2B SaaS", "B2C Software", "Enterprise Software",
        "IT Services & Consulting", "Financial Services",
        "Healthcare", "Manufacturing", "Telecommunications",
        # ... many more values
        "Other", "Unknown"
    ], str] = dspy.OutputField(
        description="Select the closest industry from the VALID VALUES list above."
    )


# LAST RESORT: Fuzzy matching normalization for large enums only
def normalize_enum_output(output, valid_values: list, field_name: str) -> str:
    """
    Normalize LLM output to closest valid enum value using fuzzy matching.

    USE ONLY FOR LARGE ENUMS (20+ values) where LLM mistakes are common.
    For small enums, rely on good prompting instead.
    """
    from difflib import get_close_matches

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

**WRONG - DO NOT DO THIS:**
```python
class MySignature(dspy.Signature):
    # WRONG for large enums: Strict Literal without Union causes validation failure
    industry: Literal[
        "B2B SaaS", "B2C Software", "Enterprise Software",
        # ... 50 more values
    ] = dspy.OutputField(description="Select industry")
```

**Why Union for large enums:** With 50+ enum values, LLMs occasionally output variations ("Denmark" instead of "Nordics", "Pay-as-you-go" instead of "Usage-based"). Without `Union[..., str]`, Pydantic raises `ValidationError` and aborts the workflow. The Union type accepts any string as a safety net, and fuzzy matching normalizes it afterward.

**Why NOT Union for small enums:** For 3-10 options, LLMs are reliable with good prompting. Adding Union + normalization is unnecessary complexity.

**Error you'd see with strict Literal on large enums:**
```
ValidationError: 1 validation error for MySignature
industry
  Input should be 'B2B SaaS', 'B2C Software', ... (received: 'Denmark')
```

---

### 4. Rich Signature Docstrings

**Problem:** DSPy uses the signature docstring as the primary instruction source. Poor docstrings = poor outputs.

**CORRECT:**
```python
class DataExtractor(dspy.Signature):
    """
    Extract company intelligence from website content.

    === YOUR ROLE IN THE WORKFLOW ===
    You are the FIRST analysis agent in a 7-stage pipeline.

    YOUR JOB: Extract comprehensive company information from website content.
    Your output becomes the foundation that all downstream agents build upon.

    WORKFLOW OVERVIEW:
    Stage 1: YOU (DataExtractor) -> Extract company offerings
    Stage 2: CustomerAnalyzer -> Identify target customers
    Stage 3: Categorizer -> Match to predefined categories
    Stage 4: Ranker -> Assign quality tier (A/B/C/D)

    CRITICAL: Everything downstream depends on YOUR accuracy.

    === ENUM FIELD COMPLIANCE ===

    **WHY THIS MATTERS:**
    Your output is parsed by downstream systems that perform EXACT STRING MATCHING.
    If you output ANY value not in the valid options list, the workflow may fail.

    **REQUIREMENTS:**
    - Output EXACTLY one of the listed valid options
    - DO NOT output variations (e.g., "SaaS" instead of "B2B SaaS")
    - DO NOT output synonyms (e.g., "Consulting" instead of "IT Services")
    - If uncertain, use "Other" or "Unknown" - these are ALWAYS safer

    ENUM FIELD: industry
    VALID VALUES: B2B SaaS, B2C Software, Enterprise Software, IT Services, Other, Unknown

    === QUALITY STANDARDS ===
    - All claims must be traceable to the provided website content
    - No fabrication - only extract what's explicitly stated
    - Be specific - choose the MOST SPECIFIC category that applies
    """

    # Input fields
    company_name: str = dspy.InputField()
    website_content: str = dspy.InputField()

    # Output fields
    overview: str = dspy.OutputField(description="2-3 sentence company overview")
    industry: Union[Literal[...], str] = dspy.OutputField(description="See VALID VALUES above")
```

**WRONG - DO NOT DO THIS:**
```python
class DataExtractor(dspy.Signature):
    """Extract company info."""  # WRONG: Too brief

    company_name: str = dspy.InputField()
    website_content: str = dspy.InputField()
    industry: str = dspy.OutputField()  # WRONG: No validation guidance
```

**Why:** DSPy compiles the docstring into the prompt. Comprehensive docstrings with workflow context, validation rules, and anti-patterns dramatically improve output quality and consistency.

---

### 5. Formatters Between Stages

**Problem:** Raw DSPy Prediction objects don't transfer well between agents. LLMs process markdown better than nested dicts.

**CORRECT:**
```python
def format_extraction_output(prediction) -> str:
    """
    Convert DSPy Prediction to markdown for downstream LLM consumption.
    """
    if not prediction:
        return "No data available."

    # Handle both Prediction objects and dicts
    if hasattr(prediction, '_store'):
        data = prediction._store
    elif hasattr(prediction, '__dict__'):
        data = prediction.__dict__
    else:
        data = prediction

    markdown = "# Company Analysis Report\n\n"

    if 'overview' in data:
        markdown += f"## Overview\n{data['overview']}\n\n"

    if 'industry' in data:
        markdown += f"## Industry\n{data['industry']}\n\n"

    # Add semantic definitions for enum fields
    if 'pricing_model' in data and data['pricing_model']:
        model = data['pricing_model']
        markdown += f"## Pricing Model\n**{model}**\n"
        # Inject definition for context
        definitions = {
            "Subscription": "Recurring payments for ongoing access",
            "Usage-based": "Pay per unit consumed",
            "One-time": "Single purchase, perpetual license"
        }
        if model in definitions:
            markdown += f"*{definitions[model]}*\n\n"

    return markdown


# Usage in pipeline
class MyPipeline(dspy.Module):
    async def aforward(self, input_data: str):
        # Stage 1
        stage1_result = await self.extractor.acall(input=input_data)
        stage1_formatted = format_extraction_output(stage1_result)

        # Stage 2 receives formatted markdown, not raw Prediction
        stage2_result = await self.analyzer.acall(
            previous_analysis=stage1_formatted,  # Markdown string
            input=input_data
        )
```

**WRONG - DO NOT DO THIS:**
```python
# WRONG: Passing raw Prediction object
stage2_result = await self.analyzer.acall(
    previous_analysis=stage1_result,  # Raw object, not formatted
    input=input_data
)

# WRONG: Passing dict with nested structures
stage2_result = await self.analyzer.acall(
    previous_analysis=stage1_result.__dict__,  # Nested dict
)
```

**Why:** LLMs comprehend markdown with headers and bullets better than nested data structures. Formatters also allow injecting semantic definitions for enum fields (e.g., explaining what "Usage-based" pricing means), enriching context for downstream agents.

---

### 6. Async Retry Wrapper

**CORRECT:**
```python
import asyncio
from typing import Any, Callable

async def call_with_retry(
    agent,
    agent_name: str,
    max_retries: int = 3,
    base_wait: float = 30.0,
    **kwargs
) -> Any:
    """
    Retry a DSPy agent call with exponential backoff.

    - Rate limit (429): Wait 30 seconds, retry
    - Other errors: Exponential backoff (5s, 10s, 20s)
    - After max_retries: Raise with detailed error message
    """
    import random

    for attempt in range(max_retries):
        try:
            result = await agent.acall(**kwargs)
            if attempt > 0:
                print(f"✓ {agent_name} succeeded on attempt {attempt + 1}")
            return result

        except Exception as e:
            is_rate_limit = "429" in str(e) or "rate limit" in str(e).lower()

            if attempt < max_retries - 1:
                if is_rate_limit:
                    wait_time = base_wait  # Fixed 30s for rate limits
                    print(f"⚠ {agent_name} hit rate limit on attempt {attempt + 1}")
                else:
                    # Exponential backoff with jitter
                    base_error_wait = (2 ** attempt) * 5  # 5s, 10s, 20s
                    jitter = random.uniform(0, base_error_wait * 0.3)
                    wait_time = base_error_wait + jitter
                    print(f"⚠ {agent_name} failed: {type(e).__name__}")

                print(f"  Waiting {wait_time:.1f}s before retry...")
                await asyncio.sleep(wait_time)
            else:
                print(f"✗ {agent_name} failed after {max_retries} attempts")
                raise


# Usage
result = await call_with_retry(
    self.extractor,
    agent_name="data_extractor",
    company_name=company_name,
    website_content=website_content
)
```

**WRONG - DO NOT DO THIS:**
```python
# WRONG: No retry logic
result = await self.extractor.acall(
    company_name=company_name,
    website_content=website_content
)

# WRONG: Simple retry without backoff
for i in range(3):
    try:
        result = await self.extractor.acall(**kwargs)
        break
    except:
        pass  # No wait, no logging
```

**Why:** API calls fail due to rate limits, network issues, or transient errors. Without retry logic, a single failure aborts the entire workflow. Exponential backoff with jitter prevents thundering herd problems when multiple workflows retry simultaneously.

---

## Anti-Patterns Summary

### DO NOT: Create LM per module
```python
# WRONG
class MyModule(dspy.Module):
    def __init__(self):
        self.lm = dspy.LM("gemini/...")  # Creates separate HTTP client
```

### DO NOT: Use ChainOfThought for extraction
```python
# WRONG - Unnecessary overhead
self.extractor = dspy.ChainOfThought(ExtractorSignature)
```

### DO NOT: Use strict Literal types for LARGE enums without Union
```python
# WRONG for large enums (20+ values) - Causes validation failures
industry: Literal["B2B SaaS", "B2C Software", ...50 more...] = dspy.OutputField()

# CORRECT for large enums - Union as safety net
industry: Union[Literal[...], str] = dspy.OutputField()

# NOTE: For small enums (3-10 values), strict Literal is fine with good prompting
category: Literal["A", "B", "C", "D"] = dspy.OutputField()  # OK
```

### DO NOT: Pass raw Predictions between stages
```python
# WRONG - LLMs struggle with nested objects
stage2 = self.analyzer(previous=stage1_result)
```

### DO NOT: Skip retry logic
```python
# WRONG - Single failure aborts workflow
result = await agent.acall(**kwargs)
```

---

## Common Imports

```python
# DSPy Core
import dspy
from dspy import Signature, InputField, OutputField, Predict, ChainOfThought, Module

# Type Hints for Signatures
from typing import Literal, Union, List, Optional, Any

# Pydantic (for complex nested outputs)
from pydantic import BaseModel, Field

# Async utilities
import asyncio
import os

# Configuration at module level (BEFORE any async code)
dspy.settings.configure(async_max_workers=2000)
```

---

## Quick Patterns

### Singleton LM Factory
```python
_shared_lm = None

def get_shared_lm():
    global _shared_lm
    if _shared_lm is None:
        _shared_lm = dspy.LM(
            os.getenv("MODEL_NAME", "gemini/gemini-2.5-flash"),
            api_key=os.getenv("API_KEY"),
            max_parallel_requests=2000
        )
    return _shared_lm
```

### Basic Pipeline Structure
```python
class MyPipeline(dspy.Module):
    def __init__(self, shared_lm):
        if shared_lm is None:
            raise ValueError("shared_lm required")

        self.stage1 = dspy.Predict(Stage1Signature)
        self.stage2 = dspy.Predict(Stage2Signature)

        self.stage1.set_lm(shared_lm)
        self.stage2.set_lm(shared_lm)

    async def aforward(self, input_data: str):
        result1 = await call_with_retry(self.stage1, "stage1", input=input_data)
        formatted = format_output(result1)
        result2 = await call_with_retry(self.stage2, "stage2", context=formatted)
        return dspy.Prediction(output=result2.output)
```

### dspy.History for Loops
```python
# Initialize separate histories per agent role
critic_history = dspy.History(messages=[])
iterator_history = dspy.History(messages=[])

# Add messages with proper roles
critic_history.messages.append({
    "role": "user",
    "content": "Content to evaluate"
})

# Pass history to agent
result = await self.critic.acall(
    content=content,
    history=critic_history
)

# Add agent's response to its own history
critic_history.messages.append({
    "role": "assistant",
    "content": result.feedback
})
```
