# Pipeline Pattern

## What It Is

A sequential chain of DSPy modules where each predictor processes data and passes results to the next. The simplest agent team structure: A → B → C. In DSPy, this is implemented as a single `dspy.Module` containing multiple `Predict` instances that execute sequentially.

## When to Use

- Sequential processing where order matters
- Each agent needs output from the previous agent
- Data enrichment pipelines (each agent adds to state)
- Transformation chains (input → process → format → output)
- Multi-stage analysis with classification and ranking

## When to Avoid

- Tasks are independent and could run in parallel → use **Fan-in/Fan-out** instead
- Different paths needed based on runtime conditions → use **Router** instead
- Iterative refinement needed → use **Loop** instead
- Single agent can handle the entire task → use **Individual Agent** instead

## Pipeline Structure

```
START → Stage 1 → format() → Stage 2 → format() → Stage 3 → END
         ↓                      ↓                     ↓
      Predict              Predict               Predict
```

Each stage:
1. Receives input (raw data or formatted output from previous stage)
2. Executes via `dspy.Predict(Signature)`
3. Output is formatted to markdown for next stage
4. Returns consolidated `dspy.Prediction`

---

## DSPy Implementation

### Code Template

```python
import os
import dspy
from typing import Literal
from pydantic import BaseModel


# =============================================================================
# SINGLETON LM FACTORY
# =============================================================================
# CRITICAL: Use module-level singleton to prevent connection exhaustion
# when running concurrent workflows.

_shared_lm = None

def get_shared_lm():
    """Get or create singleton LM instance for connection pooling."""
    global _shared_lm
    if _shared_lm is None:
        _shared_lm = dspy.LM(
            os.getenv("MODEL_NAME", "gemini/gemini-2.5-flash"),
            api_key=os.getenv("API_KEY"),
            max_parallel_requests=2000,
            timeout=120,  # REQUIRED: prevents indefinite hangs
        )
    return _shared_lm


# =============================================================================
# SIGNATURES (Input/Output Contracts)
# =============================================================================
# Each signature defines a stage in the pipeline.
# Rich docstrings improve output quality.
#
# STRUCTURED OUTPUT RULE: Use typed output fields (bool, int, list[str],
# dict[str, Any]) or Pydantic BaseModel/RootModel as OutputField types.
# NEVER use str fields with JSON parsing instructions.
# See frameworks/dspy/CHEATSHEET.md Critical Rules.

class Stage1Signature(dspy.Signature):
    """
    First analysis stage - Extract core information.

    === YOUR ROLE IN THE WORKFLOW ===
    You are the FIRST agent in a 3-stage pipeline.
    Your output becomes the foundation for downstream agents.

    === QUALITY STANDARDS ===
    - Extract only what's explicitly stated in the input
    - No fabrication or assumptions
    - Be specific and comprehensive
    """
    # Inputs
    raw_input: str = dspy.InputField(description="Raw data to analyze")
    context: str = dspy.InputField(description="Additional context")

    # Outputs
    analysis: str = dspy.OutputField(description="Comprehensive analysis")
    # Small enum (5 values) - strict Literal is fine with good prompting
    category: Literal[
        "Category A", "Category B", "Category C", "Other", "Unknown"
    ] = dspy.OutputField(
        description="EXACTLY one of: Category A, Category B, Category C, Other, Unknown"
    )


class Stage2Signature(dspy.Signature):
    """
    Second stage - Enrich with additional analysis.

    === YOUR ROLE IN THE WORKFLOW ===
    You are the SECOND agent. You receive formatted output from Stage 1.
    Your job is to add deeper analysis based on the initial extraction.
    """
    # Inputs (includes formatted output from Stage 1)
    stage1_analysis: str = dspy.InputField(description="Formatted analysis from Stage 1")
    raw_input: str = dspy.InputField(description="Original input for reference")

    # Outputs
    enriched_analysis: str = dspy.OutputField(description="Enriched analysis with deeper insights")
    confidence: int = dspy.OutputField(description="Confidence score 0-100")


class Stage3Signature(dspy.Signature):
    """
    Final stage - Rank and produce final output.

    === YOUR ROLE IN THE WORKFLOW ===
    You are the FINAL agent. You receive all previous analysis.
    Your job is to synthesize everything and produce a quality ranking.
    """
    # Inputs (structured fields from previous stages)
    stage1_category: str = dspy.InputField(description="Category from Stage 1")
    stage2_enriched: str = dspy.InputField(description="Enriched analysis from Stage 2")
    stage2_confidence: int = dspy.InputField(description="Confidence from Stage 2")

    # Outputs
    # Small enum (4 values) - strict Literal is fine with good prompting
    rank: Literal["A", "B", "C", "D"] = dspy.OutputField(
        description="EXACTLY one of: A (excellent), B (good), C (fair), D (poor)"
    )
    justification: str = dspy.OutputField(description="Reasoning for the rank")


# =============================================================================
# FORMATTERS (Data Transformation Layer)
# =============================================================================
# Convert structured Prediction outputs to markdown for LLM consumption.

def format_stage1_output(prediction) -> str:
    """Format Stage 1 output as markdown for Stage 2."""
    if not prediction:
        return "No analysis available."

    # Handle both Prediction objects and dicts
    if hasattr(prediction, '_store'):
        data = prediction._store
    elif hasattr(prediction, '__dict__'):
        data = prediction.__dict__
    else:
        data = prediction

    markdown = "# Stage 1 Analysis Report\n\n"

    if 'analysis' in data:
        markdown += f"## Analysis\n{data['analysis']}\n\n"

    if 'category' in data:
        markdown += f"## Category\n**{data['category']}**\n\n"

    return markdown


def format_stage2_output(prediction) -> str:
    """Format Stage 2 output as markdown."""
    if not prediction:
        return "No enriched analysis available."

    if hasattr(prediction, '_store'):
        data = prediction._store
    elif hasattr(prediction, '__dict__'):
        data = prediction.__dict__
    else:
        data = prediction

    markdown = "# Stage 2 Enriched Analysis\n\n"

    if 'enriched_analysis' in data:
        markdown += f"## Enriched Analysis\n{data['enriched_analysis']}\n\n"

    if 'confidence' in data:
        markdown += f"**Confidence:** {data['confidence']}%\n\n"

    return markdown


# =============================================================================
# RETRY WRAPPER
# =============================================================================

async def call_with_retry(agent, agent_name: str, max_retries: int = 3, **kwargs):
    """Retry agent calls with exponential backoff."""
    import asyncio
    import random

    for attempt in range(max_retries):
        try:
            result = await agent.acall(**kwargs)
            return result
        except Exception as e:
            is_rate_limit = "429" in str(e) or "rate limit" in str(e).lower()

            if attempt < max_retries - 1:
                wait_time = 30 if is_rate_limit else (2 ** attempt) * 5
                print(f"⚠ {agent_name} failed on attempt {attempt + 1}, waiting {wait_time}s")
                await asyncio.sleep(wait_time)
            else:
                print(f"✗ {agent_name} failed after {max_retries} attempts")
                raise


# =============================================================================
# PIPELINE MODULE
# =============================================================================

class PipelineModule(dspy.Module):
    """
    Multi-stage sequential pipeline.

    Orchestrates multiple predictors with formatters between stages.
    Uses singleton LM for connection pooling.
    """

    def __init__(self, shared_lm):
        """
        Initialize pipeline with shared LM instance.

        Args:
            shared_lm: Singleton LM instance (REQUIRED)

        Raises:
            ValueError: If shared_lm is None
        """
        if shared_lm is None:
            raise ValueError(
                "PipelineModule requires a shared_lm instance. "
                "Pass get_shared_lm() to enable connection pooling."
            )

        self.lm = shared_lm

        # Create predictors for each stage
        self.stage1 = dspy.Predict(Stage1Signature)
        self.stage2 = dspy.Predict(Stage2Signature)
        self.stage3 = dspy.Predict(Stage3Signature)

        # CRITICAL: Inject singleton LM into ALL predictors
        self.stage1.set_lm(self.lm)
        self.stage2.set_lm(self.lm)
        self.stage3.set_lm(self.lm)

    def forward(self, raw_input: str, context: str = "", **kwargs):
        """
        Synchronous execution for optimization/testing.

        All stages execute sequentially without retry logic.
        Used for DSPy optimization (GEPA/MIPROv2).
        """
        # Stage 1: Initial analysis
        stage1_result = self.stage1(
            raw_input=raw_input,
            context=context,
            **kwargs
        )
        stage1_formatted = format_stage1_output(stage1_result)

        # Stage 2: Enrichment (receives formatted Stage 1 output)
        stage2_result = self.stage2(
            stage1_analysis=stage1_formatted,
            raw_input=raw_input,
            **kwargs
        )
        stage2_formatted = format_stage2_output(stage2_result)

        # Stage 3: Ranking (receives structured fields)
        stage3_result = self.stage3(
            stage1_category=stage1_result.category,
            stage2_enriched=stage2_result.enriched_analysis,
            stage2_confidence=stage2_result.confidence,
            **kwargs
        )

        # Return consolidated prediction
        return dspy.Prediction(
            stage1=stage1_result,
            stage2=stage2_result,
            stage3=stage3_result,
            final_rank=stage3_result.rank,
            final_justification=stage3_result.justification,
            # Include formatted outputs for downstream use
            stage1_formatted=stage1_formatted,
            stage2_formatted=stage2_formatted,
        )

    async def aforward(self, raw_input: str, context: str = "", **kwargs):
        """
        Async production execution with retries and timing.

        Includes:
        - Retry logic with exponential backoff
        - Timing data collection
        - Error handling
        """
        import time
        timings = {}

        # Stage 1: Initial analysis
        start = time.time()
        stage1_result = await call_with_retry(
            self.stage1,
            agent_name="stage1",
            raw_input=raw_input,
            context=context,
            **kwargs
        )
        stage1_formatted = format_stage1_output(stage1_result)
        timings['stage1'] = time.time() - start

        # Stage 2: Enrichment
        start = time.time()
        stage2_result = await call_with_retry(
            self.stage2,
            agent_name="stage2",
            stage1_analysis=stage1_formatted,
            raw_input=raw_input,
            **kwargs
        )
        stage2_formatted = format_stage2_output(stage2_result)
        timings['stage2'] = time.time() - start

        # Stage 3: Ranking
        start = time.time()
        stage3_result = await call_with_retry(
            self.stage3,
            agent_name="stage3",
            stage1_category=stage1_result.category,
            stage2_enriched=stage2_result.enriched_analysis,
            stage2_confidence=stage2_result.confidence,
            **kwargs
        )
        timings['stage3'] = time.time() - start
        timings['total'] = sum(timings.values())

        return dspy.Prediction(
            stage1=stage1_result,
            stage2=stage2_result,
            stage3=stage3_result,
            final_rank=stage3_result.rank,
            final_justification=stage3_result.justification,
            stage1_formatted=stage1_formatted,
            stage2_formatted=stage2_formatted,
            timings=timings,
        )


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

async def main():
    # Initialize singleton LM
    shared_lm = get_shared_lm()

    # Create pipeline with shared LM
    pipeline = PipelineModule(shared_lm=shared_lm)

    # Run async execution
    result = await pipeline.aforward(
        raw_input="Company website content here...",
        context="B2B SaaS analysis context"
    )

    print(f"Final Rank: {result.final_rank}")
    print(f"Justification: {result.final_justification}")
    print(f"Timings: {result.timings}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## DSPy-Specific Notes

> **Structured Output Rule:** When defining signatures for pipeline stages, use typed DSPy output fields (`bool`, `int`, `list[str]`, `dict[str, Any]`) or Pydantic `BaseModel`/`RootModel` as OutputField types. NEVER use `str` fields with JSON parsing instructions. See `frameworks/dspy/CHEATSHEET.md` Critical Rules.

- **Singleton LM Pattern:** All predictors share one LM instance via `set_lm()`. This is critical for connection pooling when running concurrent workflows.

- **forward() + aforward() — Both REQUIRED:** `forward()` enables DSPy prompt optimization (GEPA/MIPROv2) — runs all stages synchronously without retry. `aforward()` is for production with retry logic and timing. Always implement both.

- **Formatters:** Convert Prediction objects to markdown between stages. LLMs comprehend structured markdown better than nested dicts.

- **Dual Data Flow:** Some stages receive formatted markdown (for narrative understanding), others receive structured fields (for algorithmic matching). Design based on what the downstream agent needs.

- **Signature Docstrings:** Rich docstrings with workflow context improve output quality. Include enum valid values directly in the docstring.

---

## Multi-Model Singleton Pattern

When different pipeline stages need different model tiers:

```python
_flash_lm = None
_pro_lm = None

def get_flash_lm():
    """Flash model for extraction/classification (fast, cheap)."""
    global _flash_lm
    if _flash_lm is None:
        _flash_lm = dspy.LM(
            os.getenv("FLASH_MODEL", "gemini/gemini-2.5-flash"),
            api_key=os.getenv("API_KEY"),
            max_parallel_requests=2000,
            timeout=120,
        )
    return _flash_lm

def get_pro_lm():
    """Pro model for synthesis/complex reasoning (slower, better)."""
    global _pro_lm
    if _pro_lm is None:
        _pro_lm = dspy.LM(
            os.getenv("PRO_MODEL", "gemini/gemini-2.5-pro"),
            api_key=os.getenv("API_KEY"),
            max_parallel_requests=100,
            timeout=120,
        )
    return _pro_lm
```

**Model tier guidance for pipelines:**
| Stage Type | Model | Rationale |
|-----------|-------|-----------|
| Extraction/classification (early stages) | Flash | Structured extraction, fast |
| Enrichment/analysis (middle stages) | Flash or Pro | Depends on complexity |
| Synthesis/ranking (final stages) | Pro | Complex multi-source reasoning |

```python
# In __init__:
self.stage1.set_lm(flash_lm)   # Extraction → Flash
self.stage2.set_lm(flash_lm)   # Enrichment → Flash
self.stage3.set_lm(pro_lm)     # Final synthesis → Pro
```

---

## State Flow

```
Initial Input:
  raw_input: "website content"
  context: "analysis context"

After Stage 1:
  stage1.analysis: "Comprehensive analysis..."
  stage1.category: "Category A"
  stage1_formatted: "# Stage 1 Analysis Report\n..."

After Stage 2:
  stage2.enriched_analysis: "Deeper insights..."
  stage2.confidence: 85
  stage2_formatted: "# Stage 2 Enriched Analysis\n..."

After Stage 3:
  stage3.rank: "A"
  stage3.justification: "High quality because..."

Final Prediction:
  final_rank: "A"
  final_justification: "..."
  timings: {stage1: 2.1, stage2: 1.8, stage3: 1.5, total: 5.4}
```

---

## Variants

### Pipeline with Early Exit

When poor results should terminate early:

```python
async def aforward(self, raw_input: str, **kwargs):
    stage1_result = await call_with_retry(self.stage1, "stage1", ...)

    # Early exit if Stage 1 confidence is too low
    if stage1_result.confidence < 30:
        return dspy.Prediction(
            early_exit=True,
            reason="Low confidence in initial analysis",
            stage1=stage1_result
        )

    # Continue to Stage 2...
```

### Pipeline with Shared Context

When all stages need access to common context:

```python
class Stage2Signature(dspy.Signature):
    # Shared context (read by all stages)
    company_context: str = dspy.InputField()
    icp_definitions: str = dspy.InputField()

    # Stage-specific inputs
    stage1_analysis: str = dspy.InputField()
```

---

## Pitfalls & Best Practices

**Pitfalls:**

- **Creating LM per module** — Without singleton pattern, 100+ concurrent workflows cause 20x slowdown from connection exhaustion.

- **Skipping formatters** — Passing raw Prediction objects between stages confuses LLMs. Always format to markdown.

- **No retry logic in production** — API calls fail. Always use `call_with_retry()` wrapper.

- **Weak signature docstrings** — DSPy compiles docstrings into prompts. Brief docstrings = poor outputs.

**Best Practices:**

- **Validate shared_lm in __init__** — Raise `ValueError` if None to enforce singleton pattern.

- **Call set_lm() on ALL predictors** — Every predictor must use the shared LM instance.

- **Use forward() for optimization, aforward() for production** — Keeps optimization clean while production has retry logic.

- **Include timings** — Track execution time per stage for performance monitoring.

- **Document data flow** — Comment which fields each stage reads and writes.

---

## When Pipeline Isn't Enough

If you find yourself adding:
- **Multiple starting points** → Consider Fan-in/Fan-out pattern
- **Conditional routing** → Consider Router pattern
- **Cycles back to earlier stages** → Consider Loop pattern
- **Parallel execution** → Consider Fan-in/Fan-out pattern

Pipeline is the foundation. More complex patterns build on it.
