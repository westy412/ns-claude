# Basic Agent (dspy.Predict)

## What It Is

A single-turn LLM call that maps input fields to output fields via a Signature. The most fundamental building block in DSPy, designed for maximum efficiency when the task is straightforward extraction, classification, or transformation.

## When to Use

- Data extraction from unstructured text
- Classification and categorization tasks
- Simple transformations (format conversion, summarization)
- Agent-to-agent communication in pipelines
- Any task with clear input → output mapping
- When you need speed and don't require visible reasoning

## When to Avoid

- Task requires step-by-step reasoning traces — use **Reasoning Agent** (ChainOfThought) instead
- Agent needs conversation history — use **Conversational Agent** (dspy.History) instead
- Agent needs to call external tools — use **Tool Agent** (dspy.ReAct) instead
- Complex decisions that benefit from explicit reasoning — use **Reasoning Agent** instead

## Selection Criteria

- If input → output mapping is direct and clear → **Basic Agent**
- If you need visible reasoning for debugging or quality → **Reasoning Agent**
- If building a multi-turn conversation → **Conversational Agent**
- If agent needs external data or actions → **Tool Agent**

## Inputs / Outputs

**Inputs:**
- Input fields defined in the Signature
- Singleton LM instance (required for concurrency)

**Outputs:**
- Output fields defined in the Signature (accessed as `result.field_name`)
- Pydantic validation ensures type correctness

## Prompting Guidelines

In DSPy, the **Signature docstring** is the prompt. Quality docstrings = quality outputs:

- Include the agent's role in the larger workflow
- Document enum field constraints explicitly with VALID VALUES lists
- Add anti-patterns ("DO NOT output X")
- Provide workflow context so the agent understands downstream dependencies
- Use structured sections: `=== YOUR ROLE ===`, `=== ENUM COMPLIANCE ===`, etc.

---

## DSPy Implementation

### Signature Definition

```python
import dspy
from typing import Literal, Union

class DataExtractorSignature(dspy.Signature):
    """
    Extract company intelligence from website content.

    === YOUR ROLE IN THE WORKFLOW ===
    You are the FIRST analysis agent in a multi-stage pipeline.

    YOUR JOB: Extract comprehensive company information from website content.
    Your output becomes the foundation that all downstream agents build upon.

    WORKFLOW OVERVIEW:
    Stage 1: YOU (DataExtractor) → Extract company offerings
    Stage 2: CustomerAnalyzer → Identify target customers
    Stage 3: Categorizer → Match to predefined categories

    CRITICAL: Everything downstream depends on YOUR accuracy.

    === ENUM FIELD COMPLIANCE ===

    For the `industry` field, output EXACTLY one of these values:
    B2B SaaS, B2C Software, Enterprise Software, IT Services, Healthcare,
    Manufacturing, Financial Services, Other, Unknown

    DO NOT output variations (e.g., "SaaS" instead of "B2B SaaS")
    DO NOT output synonyms (e.g., "Consulting" instead of "IT Services")
    If uncertain, use "Unknown" - this is ALWAYS safer than guessing.

    === QUALITY STANDARDS ===
    - All claims must be traceable to the provided website content
    - No fabrication - only extract what's explicitly stated or clearly implied
    - Be specific - choose the MOST SPECIFIC category that applies
    """

    # Input fields
    company_name: str = dspy.InputField(description="Name of the company to analyze")
    website_content: str = dspy.InputField(description="Raw text content from company website")

    # Output fields
    overview: str = dspy.OutputField(
        description="2-3 sentence company overview based on website content"
    )
    industry: Literal[
        "B2B SaaS", "B2C Software", "Enterprise Software",
        "IT Services", "Healthcare", "Manufacturing",
        "Financial Services", "Other", "Unknown"
    ] = dspy.OutputField(
        description="Industry category - must be EXACTLY one of the valid values"
    )
    primary_offering: str = dspy.OutputField(
        description="Main product or service the company provides"
    )
```

### Module Implementation

```python
import os
import dspy

# ============================================
# SINGLETON LM PATTERN (CRITICAL)
# ============================================
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
            os.getenv("MODEL_NAME", "gemini/gemini-2.5-flash"),
            api_key=os.getenv("GOOGLE_API_KEY"),
            max_parallel_requests=2000,  # Critical for concurrency
        )
    return _shared_lm


# ============================================
# BASIC AGENT MODULE
# ============================================
class DataExtractor(dspy.Module):
    """
    Basic agent that extracts company data from website content.

    Uses dspy.Predict for efficient single-turn extraction.
    """

    def __init__(self, shared_lm):
        """
        Initialize with shared LM instance.

        Args:
            shared_lm: Singleton LM from get_shared_lm(). Required.

        Raises:
            ValueError: If shared_lm is None
        """
        if shared_lm is None:
            raise ValueError(
                "DataExtractor requires a shared_lm instance. "
                "Pass get_shared_lm() to enable connection pooling."
            )

        self.lm = shared_lm

        # Create predictor
        self.extractor = dspy.Predict(DataExtractorSignature)

        # CRITICAL: Inject singleton LM into predictor
        self.extractor.set_lm(self.lm)

    def forward(self, company_name: str, website_content: str) -> dspy.Prediction:
        """
        Synchronous forward pass for single extraction.

        Args:
            company_name: Name of company to analyze
            website_content: Raw website text

        Returns:
            dspy.Prediction with overview, industry, primary_offering fields
        """
        result = self.extractor(
            company_name=company_name,
            website_content=website_content
        )

        return result

    async def aforward(self, company_name: str, website_content: str) -> dspy.Prediction:
        """
        Async forward pass for concurrent workflows.

        Recommended for production - enables running many extractions in parallel.
        """
        result = await self.extractor.acall(
            company_name=company_name,
            website_content=website_content
        )

        return result


# ============================================
# USAGE EXAMPLE
# ============================================
async def main():
    # Get singleton LM
    lm = get_shared_lm()

    # Create agent
    extractor = DataExtractor(shared_lm=lm)

    # Run extraction
    result = await extractor.aforward(
        company_name="Acme Corp",
        website_content="Acme Corp provides B2B SaaS solutions for enterprise..."
    )

    # Access fields directly
    print(f"Industry: {result.industry}")
    print(f"Overview: {result.overview}")
    print(f"Offering: {result.primary_offering}")
```

### With Retry Wrapper (Production)

```python
import asyncio
import random
from typing import Any

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
    for attempt in range(max_retries):
        try:
            result = await agent.acall(**kwargs)
            if attempt > 0:
                print(f"[OK] {agent_name} succeeded on attempt {attempt + 1}")
            return result

        except Exception as e:
            is_rate_limit = "429" in str(e) or "rate limit" in str(e).lower()

            if attempt < max_retries - 1:
                if is_rate_limit:
                    wait_time = base_wait
                    print(f"[WARN] {agent_name} hit rate limit on attempt {attempt + 1}")
                else:
                    base_error_wait = (2 ** attempt) * 5  # 5s, 10s, 20s
                    jitter = random.uniform(0, base_error_wait * 0.3)
                    wait_time = base_error_wait + jitter
                    print(f"[WARN] {agent_name} failed: {type(e).__name__}")

                print(f"  Waiting {wait_time:.1f}s before retry...")
                await asyncio.sleep(wait_time)
            else:
                print(f"[ERROR] {agent_name} failed after {max_retries} attempts")
                raise


# Usage with retry wrapper
async def production_extraction(extractor, company_name, website_content):
    result = await call_with_retry(
        extractor.extractor,  # Pass the predictor, not the module
        agent_name="data_extractor",
        company_name=company_name,
        website_content=website_content
    )
    return result
```

### DSPy-Specific Notes

- **Signature = Prompt + Schema:** The docstring IS the system prompt. Output fields define the schema.
- **set_lm() is critical:** Without it, predictors use the global default LM, breaking connection pooling.
- **Predict vs ChainOfThought:** Use Predict for this pattern. Reserve ChainOfThought for tasks needing visible reasoning.
- **Sync vs Async:** Use `aforward()` / `acall()` for production concurrency. `forward()` / `__call__()` for simple scripts.
- **Field access:** Access outputs via `result.field_name` directly (e.g., `result.industry`).

---

## Pitfalls & Best Practices

**Pitfalls:**

- **Creating LM per module** — This causes connection pool exhaustion at scale. Always use the singleton pattern and pass `shared_lm` to each module.

- **Skipping set_lm()** — Without explicitly calling `predictor.set_lm(shared_lm)`, the predictor uses the global default, breaking connection pooling.

- **Poor docstrings** — A vague docstring like "Extract data" produces vague outputs. Be specific about role, workflow context, and constraints.

- **No retry logic** — API calls fail. Without retry, a single transient error aborts the entire workflow.

- **Using ChainOfThought for extraction** — Adds unnecessary latency and cost. Predict is faster and cheaper for straightforward extraction tasks.

**Best Practices:**

- **Always use singleton LM** — One LM instance shared across all modules in a workflow.

- **Rich Signature docstrings** — Include workflow context, enum constraints, anti-patterns, and quality standards.

- **Use retry wrapper in production** — The `call_with_retry` pattern handles rate limits and transient failures gracefully.

- **Validate enum outputs for large enums** — For enums with 20+ values, use `Union[Literal[...], str]` and fuzzy matching normalization as a safety net.

- **Format outputs between stages** — When passing results to another agent, convert to markdown for better comprehension.

---

## Comparison: Basic Agent vs Reasoning Agent

| Aspect | Basic Agent (Predict) | Reasoning Agent (ChainOfThought) |
|--------|----------------------|----------------------------------|
| Output fields | Defined in Signature | Defined in Signature + `reasoning` |
| Latency | Lower | Higher (extra reasoning tokens) |
| Cost | Lower | Higher |
| Debugging | Harder (no reasoning trace) | Easier (visible reasoning) |
| Best for | Extraction, classification | Complex decisions, synthesis |
| Token usage | Minimal | Higher (includes reasoning) |

---

## Source Reference

**Validated against:** `ns-cold-outreach-workforce/src/workflows/extract/extract_v2.py`

Patterns demonstrated:
- Singleton LM injection (lines 88-106)
- Multiple dspy.Predict instances (lines 113-124)
- Async execution with retry wrapper (lines 214-280)
