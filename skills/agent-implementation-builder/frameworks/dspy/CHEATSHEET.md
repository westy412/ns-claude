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
| 4. Predict vs ChainOfThought vs ReAct | Predict for extraction, CoT for creative synthesis, ReAct ONLY for multi-step tool chains |
| 5. Enum Validation | Small enums: prompting. Large enums (20+): `Union` + fuzzy matching |
| 6. Rich Docstrings | Workflow context + validation rules + anti-patterns |
| 7. Formatters | Convert structured outputs to markdown between stages |
| 8. Async Retry + Timeout | Exponential backoff + rate limit handling + timeout on every acall() |
| 9. asyncio.gather Fan-Out | Use `return_exceptions=True` for parallel module execution |
| 10. Multi-Model Singletons | Separate `get_flash_lm()` / `get_pro_lm()` factories for tiered models |
| 11. Optional InputFields | Use `default=None` + describe optionality in `desc` text |
| 12. Typed Outputs, NEVER str+JSON | Use typed OutputFields or Pydantic models — NEVER `str` with "output as JSON" |

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
            timeout=120,  # REQUIRED: prevents indefinite hangs
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

### Decision Table for Expert Panel Patterns

Expert panels appear in two contexts with different requirements:

| Stage | Task Type | Use | Rationale |
|-------|-----------|-----|-----------|
| **Expert Analysis** (Stage 1) | Identify themes, opportunities, warnings from research | `ChainOfThought` | Creative synthesis — extracting insights requires reasoning |
| **Expert Scoring** (Stage 3) | Score ideas against rubric (0.0-1.0 per dimension) | `Predict` | Evaluation checklist — applying scoring criteria is extraction |

**Example from ideation pipeline:**
```python
# Stage 1: Expert Panel — Analysis = ChainOfThought
self.expert_panel = dspy.ChainOfThought(ExpertPanelSignature)

# Stage 3: Expert Scoring — Evaluation = Predict
self.expert_scoring = dspy.Predict(ExpertScoringSignature)
```

**Rule of thumb:** If the expert is DISCOVERING insights → ChainOfThought.
If the expert is APPLYING a rubric to pre-existing ideas → Predict.

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

    NOTE: Timeout protection is configured at the dspy.LM() level
    (see Timeout Requirements section). This wrapper handles transient
    failures with retry logic.
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

**Why:** API calls fail due to rate limits, network issues, or transient errors. Without retry logic, a single failure aborts the entire workflow. Exponential backoff with jitter prevents thundering herd problems when multiple workflows retry simultaneously. Also ensure `timeout` is set on your `dspy.LM()` constructor (see Timeout Requirements section).

---

### 7. Use Typed Outputs, NEVER str+JSON

**CRITICAL: Never use `str` OutputField with instructions like "output as JSON" or "return a JSON object". DSPy has native structured output support — use it.**

**Simple typed outputs:**
```python
class EvaluationSignature(dspy.Signature):
    """Evaluate content quality."""

    content: str = dspy.InputField(desc="Content to evaluate")

    # Simple types — use directly as OutputField types
    passed: bool = dspy.OutputField(desc="True if content passes quality check")
    score: int = dspy.OutputField(desc="Quality score 0-100")
    confidence: float = dspy.OutputField(desc="Confidence level 0.0-1.0")
    category: Literal["good", "mediocre", "poor"] = dspy.OutputField(
        desc="EXACTLY one of: good, mediocre, poor"
    )

    # Lists and dicts — use typed collections
    keywords: list[str] = dspy.OutputField(desc="Extracted keywords")
    metadata: dict[str, Any] = dspy.OutputField(desc="Key-value metadata pairs")
```

**Complex structured outputs — use Pydantic BaseModel:**
```python
from pydantic import BaseModel, RootModel
from typing import List

# Single structured item
class ContactInfo(BaseModel):
    name: str
    email: str
    score: int

# List of structured items — use RootModel
class ContactList(RootModel[List[ContactInfo]]):
    pass

# In Signature — use Pydantic model as OutputField type
class ExtractorSignature(dspy.Signature):
    """Extract contacts from text."""

    text: str = dspy.InputField(desc="Text containing contact information")
    contacts: ContactList = dspy.OutputField(desc="Extracted contacts")

# Access in code
result = await agent.acall(text=text)
contacts_data = result.contacts.model_dump()  # Convert to dict/list
```

**WRONG — DO NOT DO THIS:**
```python
class ExtractorSignature(dspy.Signature):
    """Extract contacts. Output as JSON array."""

    text: str = dspy.InputField(desc="Text to extract from")

    # WRONG: str output with JSON instructions
    contacts: str = dspy.OutputField(
        desc="Return a JSON array of objects with name, email, score fields"
    )

    # WRONG: str output expecting structured data
    analysis: str = dspy.OutputField(
        desc="Return a JSON object with keys: summary, score, tags"
    )
```

**Why:** DSPy natively handles typed outputs through its adapter layer. When you use `bool`, `int`, `list[str]`, or Pydantic models as OutputField types, DSPy ensures the LLM output is correctly parsed and validated. Using `str` with JSON instructions forces manual parsing, loses type safety, and is fragile — the LLM may return malformed JSON, markdown-wrapped JSON, or inconsistent formats.

**Access patterns:**
- Simple types: `result.passed` → `True`, `result.score` → `85`
- Lists/dicts: `result.keywords` → `["ai", "ml"]`, `result.metadata` → `{"key": "val"}`
- Pydantic models: `result.contacts.model_dump()` → `[{"name": "...", ...}]`

**See also:** [Pydantic Models for Structured Outputs](#pydantic-models-for-structured-outputs) in Quick Patterns for full BaseModel/RootModel examples.

---

## Tool-Calling Patterns

### When to use ReAct vs Manual Tool Handling

| Pattern | Use When | LLM Calls | Latency |
|---------|----------|-----------|---------|
| `dspy.ReAct(sig, tools, max_iters=N)` | Multi-step reasoning requiring multiple tool calls in sequence | N+ per invocation | High (N * LLM latency) |
| `dspy.ChainOfThought(sig)` + `dspy.ToolCalls` | Single tool call with reasoning about parameters | 1 | Low |
| `dspy.Predict(sig)` + `dspy.ToolCalls` | Single tool call, no reasoning needed | 1 | Lowest |

### Manual Tool Handling Pattern (Preferred for Single-Tool Agents)

```python
import dspy

class SearchToolSignature(dspy.Signature):
    """Select and configure the right tool for this search."""
    search_intent: str = dspy.InputField()
    available_tools: list[dspy.Tool] = dspy.InputField()
    selected_tool_calls: dspy.ToolCalls = dspy.OutputField()

# Wrap existing functions as tools
tools = [dspy.Tool(my_search_function)]

# Single LLM call to decide parameters
agent = dspy.ChainOfThought(SearchToolSignature)
response = agent(search_intent="...", available_tools=tools)

# Execute tool calls manually
for call in response.selected_tool_calls.tool_calls:
    result = call.execute()
```

### Anti-Pattern: Using ReAct for Single-Tool Agents

```python
# BAD: ReAct with max_iters=5 makes 5+ LLM calls even for one tool
agent = dspy.ReAct(SearchSig, tools=[search_fn], max_iters=5)
# This will take 150-300 seconds with Gemini (30s * 5+ calls)

# GOOD: ChainOfThought + manual execution = 1 LLM call
agent = dspy.ChainOfThought(SearchToolSig)
# This takes 20-40 seconds
```

**When to use each:**
- **ReAct:** Multi-step tool chains where the LLM must reason between tool calls and decide what to call next
- **ChainOfThought + ToolCalls:** Single tool call where the LLM decides parameters with reasoning
- **Predict + ToolCalls:** Single tool call, straightforward parameter selection

---

## Timeout Requirements

### Rule: All LLM calls MUST have timeout protection

Timeout should be configured at the `dspy.LM()` constructor level. This ensures every LLM call through that instance has timeout protection without needing per-call wrapping.

```python
# BAD: No timeout on LM — calls can hang indefinitely
_shared_lm = dspy.LM("gemini/gemini-2.5-flash", api_key=api_key)

# GOOD: Timeout configured at LM level
_shared_lm = dspy.LM("gemini/gemini-2.5-flash", api_key=api_key, timeout=120)
```

### Required Timeouts (add to every DSPy project)

| Location | Pattern | Example |
|----------|---------|---------|
| `dspy.LM()` constructor | `timeout=N` parameter (REQUIRED) | `dspy.LM("gemini/flash", timeout=120)` |
| Thread pool `.result()` | `.result(timeout=N)` | `pool.submit(asyncio.run, coro).result(timeout=150)` |
| `call_with_retry()` | Retry wrapper handles transient failures | See Rule 6 above |

### Updated Singleton LM Pattern (with Timeout)

```python
_shared_lm = None

def get_shared_lm():
    global _shared_lm
    if _shared_lm is None:
        _shared_lm = dspy.LM(
            os.getenv("MODEL_NAME", "gemini/gemini-2.5-flash"),
            api_key=os.getenv("API_KEY"),
            max_parallel_requests=2000,
            timeout=120,  # REQUIRED: prevents indefinite hangs
        )
    return _shared_lm
```

**Note:** Always set `timeout` on every `dspy.LM()` constructor. This is the primary defense against hung API calls. The `call_with_retry` wrapper (Rule 6) handles transient failures with retry logic.

---

## Anti-Patterns Summary

### Use singleton LM (not per-module LM instances)
```python
# Use shared singleton — prevents connection pool exhaustion
shared_lm = get_shared_lm()
self.agent.set_lm(shared_lm)

# Instead of creating LM per module:
# self.lm = dspy.LM("gemini/...")  # Creates separate HTTP client
```

### Use Predict for extraction (not ChainOfThought)
```python
# Use Predict for extraction/classification tasks — faster, cheaper
self.extractor = dspy.Predict(ExtractorSignature)

# Reserve ChainOfThought for creative synthesis tasks
self.creator = dspy.ChainOfThought(CreatorSignature)
```

### Use Union types for large enums (20+ values)
```python
# For large enums — Union as safety net
industry: Union[Literal[...], str] = dspy.OutputField()

# For small enums (3-10 values) — strict Literal is fine with good prompting
category: Literal["A", "B", "C", "D"] = dspy.OutputField()
```

### Use typed OutputFields (not str with JSON instructions)
```python
# Use typed outputs — DSPy handles validation natively
contacts: ContactList = dspy.OutputField(desc="Extracted contacts")
keywords: list[str] = dspy.OutputField(desc="Extracted keywords")
score: int = dspy.OutputField(desc="Quality score 0-100")

# Instead of str + JSON parsing:
# contacts: str = dspy.OutputField(desc="Return a JSON array of {name, email}")
```

### Format outputs between stages (not raw Predictions)
```python
# Format to markdown for downstream LLM consumption
stage1_formatted = format_extraction_output(stage1_result)
stage2 = self.analyzer(previous_analysis=stage1_formatted)

# Instead of passing raw objects:
# stage2 = self.analyzer(previous=stage1_result)
```

### Use call_with_retry wrapper (not bare acall)
```python
# Wrap calls with retry for production resilience
result = await call_with_retry(self.agent, "agent_name", **kwargs)

# Instead of bare calls:
# result = await agent.acall(**kwargs)
```

### Use ChainOfThought + ToolCalls for single-tool agents (not ReAct)
```python
# Single tool call = ChainOfThought + manual execution (1 LLM call, 20-40s)
agent = dspy.ChainOfThought(SearchToolSig)

# Reserve ReAct for multi-step tool chains (N+ LLM calls, 150-300s)
# agent = dspy.ReAct(SearchSig, tools=[search_fn], max_iters=5)
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
            max_parallel_requests=2000,
            timeout=120,
        )
    return _shared_lm
```

### Pydantic Models for Structured Outputs
```python
from pydantic import BaseModel, RootModel
from typing import List

# Single structured item
class ContactInfo(BaseModel):
    name: str
    email: str
    score: int

# List of structured items - use RootModel
class ContactList(RootModel[List[ContactInfo]]):
    pass

# In Signature
class MySignature(dspy.Signature):
    """..."""
    # Use Pydantic model directly as type (NOT str with "output JSON")
    contacts: ContactList = dspy.OutputField(description="Extracted contacts")

# Access in code
result = await agent.acall(text=text)
contacts_data = result.contacts.model_dump()  # Convert to dict/list
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

    def forward(self, input_data: str):
        """Synchronous version for DSPy optimization (GEPA, MIPROv2)."""
        result1 = self.stage1(input=input_data)
        formatted = format_output(result1)
        result2 = self.stage2(context=formatted)
        return dspy.Prediction(output=result2.output)

    async def aforward(self, input_data: str):
        """Async version for production with retry logic."""
        result1 = await call_with_retry(self.stage1, "stage1", input=input_data)
        formatted = format_output(result1)
        result2 = await call_with_retry(self.stage2, "stage2", context=formatted)
        return dspy.Prediction(output=result2.output)
```

**⚠️ CRITICAL:** Both methods are REQUIRED. `forward()` enables DSPy prompt optimization. `aforward()` is for production with retry/logging/parallel execution. Implement both.

### Tool-Using Agents (ReAct vs Manual)

> **Full reference:** [`frameworks/dspy/react.md`](react.md) and [Tool-Calling Patterns](#tool-calling-patterns) above

**Default to ChainOfThought + manual tool handling.** Only use ReAct when multi-step tool chains are genuinely required (LLM must reason between tool calls and decide what to call next).

```python
# PREFERRED: Single-tool agents — ChainOfThought + ToolCalls (1 LLM call)
class SearchToolSignature(dspy.Signature):
    """Select and configure the right search tool."""
    search_intent: str = dspy.InputField()
    available_tools: list[dspy.Tool] = dspy.InputField()
    selected_tool_calls: dspy.ToolCalls = dspy.OutputField()

tools = [dspy.Tool(search_posts)]
agent = dspy.ChainOfThought(SearchToolSignature)
response = agent(search_intent="...", available_tools=tools)
for call in response.selected_tool_calls.tool_calls:
    result = call.execute()

# ONLY FOR MULTI-STEP TOOL CHAINS: ReAct (N+ LLM calls)
react = dspy.ReAct(
    signature=SearchSignature,
    tools=[search_posts],
    max_iters=5  # Safety limit (default: 20, use 3-5 for costly tools)
)
react.set_lm(shared_lm)
result = await react.acall(question="...")
```

**Decision guide:**
- Single tool call, LLM decides parameters → ChainOfThought + ToolCalls
- Multi-step tool chains with reasoning between calls → ReAct
- Fixed/predictable tool sequence → call tools explicitly in `aforward()`

---

### asyncio.gather Fan-Out

> **Full reference:** [`frameworks/dspy/async-patterns.md`](async-patterns.md)

```python
# Fan out N instances in parallel (with retry + timeout)
results = await asyncio.gather(*[
    call_with_retry(
        self.expert,
        f"expert_{perspective}",
        timeout=180,
        perspective=perspective,
        instructions=instructions,
        data=shared_data,
    )
    for perspective, instructions in self.perspectives
], return_exceptions=True)  # Graceful degradation

# Filter failures
successful = [r for r in results if not isinstance(r, Exception)]
```

**Shared LM is safe for concurrent use** — `max_parallel_requests` handles connection pooling.

---

### Multi-Model Singleton

> **Full reference:** [`frameworks/dspy/async-patterns.md`](async-patterns.md)

```python
# utils.py — separate factories for each model tier
_flash_lm = None
_pro_lm = None

def get_flash_lm():
    """Fast, cheap — for extraction, search, parallel fan-out."""
    global _flash_lm
    if _flash_lm is None:
        _flash_lm = dspy.LM("gemini/gemini-2.5-flash", api_key=os.getenv("GOOGLE_API_KEY"),
                             max_parallel_requests=2000, timeout=120)
    return _flash_lm

def get_pro_lm():
    """Powerful — for synthesis, creative generation, complex reasoning."""
    global _pro_lm
    if _pro_lm is None:
        _pro_lm = dspy.LM("gemini/gemini-2.5-pro", api_key=os.getenv("GOOGLE_API_KEY"),
                           max_parallel_requests=100, timeout=120)
    return _pro_lm

# Assign different LMs to different predictors
self.search_agent.set_lm(get_flash_lm())   # Fast operations
self.synthesizer.set_lm(get_pro_lm())       # Complex reasoning
```

**Tier guide:** Flash for parallel/high-volume tasks, Pro for single critical operations.

---

### Optional InputField

```python
class MySignature(dspy.Signature):
    """Process with optional inputs."""

    required_input: str = dspy.InputField(desc="Always required")

    # Optional field with default=None
    previous_feedback: str = dspy.InputField(
        desc="Optional feedback from prior iteration. If not provided, this is the first attempt.",
        default=None
    )
```

**IMPORTANT:** DSPy does NOT propagate `default` values into the prompt. The LLM won't know a field is optional unless you say so in the `desc`. Always describe the default behavior in the description text.

**Workaround:** In your module's `aforward()`, explicitly pass the default when the caller omits the field:

```python
async def aforward(self, input_text: str, feedback: str = None):
    return await self.predictor.acall(
        input_text=input_text,
        previous_feedback=feedback if feedback is not None else "",
    )
```

**When to use Optional vs separate signatures:**
- Use `default=None` when the field is sometimes present (e.g., retry feedback)
- Use separate signatures when the input shapes are fundamentally different

---

### Loop Orchestration

> **Full reference:** [`agent-teams/dspy/loop.md`](../../../agent-teams/dspy/loop.md)

The loop pattern implements while-loop with quality-check → retry-with-feedback:

```python
while not completed and attempts < self.max_iterations:
    # Critic evaluates current draft
    critic_result = await self.critic.acall(current_draft=current_draft, ...)

    if critic_result.completed:
        break

    # Iterator improves based on feedback
    iteration_result = await self.iterator.acall(
        current_draft=current_draft,
        critic_feedback=critic_result.feedback, ...
    )
    current_draft = iteration_result.improved_draft
    attempts += 1

# After loop: return best attempt (approved or not)
```

Key patterns: separate `dspy.History` per agent role, multi-flag termination, graceful degradation after max iterations.

---

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
