# Fan-in/Fan-out Pattern

## What It Is

A parallel execution pattern where multiple agents process the same input simultaneously (fan-out), then results are aggregated (fan-in). In DSPy, this is implemented using `asyncio.gather()` to run multiple predictors concurrently.

## When to Use

- Multiple independent analyses of the same data
- Parallel evaluation from different perspectives (multi-critic)
- Tasks that don't depend on each other
- Performance optimization (reduce total execution time)
- Ensemble approaches (aggregate multiple opinions)

## When to Avoid

- Tasks have dependencies → use **Pipeline** instead
- Results from one agent determine what others do → use **Router** instead
- Iterative refinement needed → use **Loop** instead
- Only one agent needed → use **Individual Agent** instead

## Pattern Structure

```
              ┌─── Agent A ───┐
              │               │
START ───────┼─── Agent B ───┼──── Aggregator ──── END
              │               │
              └─── Agent C ───┘
```

Key insight: All agents receive the SAME input and run in PARALLEL. Results are merged by an aggregator function or agent.

---

## DSPy Implementation

### Code Template

```python
import os
import asyncio
import dspy
from typing import Union, Literal, List


# =============================================================================
# SINGLETON LM FACTORY
# =============================================================================

_shared_lm = None

def get_shared_lm():
    """Get or create singleton LM instance for connection pooling."""
    global _shared_lm
    if _shared_lm is None:
        _shared_lm = dspy.LM(
            os.getenv("MODEL_NAME", "gemini/gemini-2.5-flash"),
            api_key=os.getenv("API_KEY"),
            max_parallel_requests=2000,
        )
    return _shared_lm


# =============================================================================
# SIGNATURES (Multiple Perspectives)
# =============================================================================

class TechnicalCriticSignature(dspy.Signature):
    """
    Evaluate content from a TECHNICAL accuracy perspective.

    Focus ONLY on:
    - Factual correctness
    - Technical accuracy
    - Data integrity
    """
    content: str = dspy.InputField(description="Content to evaluate")
    context: str = dspy.InputField(description="Background context")

    technical_score: int = dspy.OutputField(description="Score 0-100")
    technical_feedback: str = dspy.OutputField(description="Technical issues found")
    technical_approved: bool = dspy.OutputField(description="True if technically sound")


class StyleCriticSignature(dspy.Signature):
    """
    Evaluate content from a STYLE and CLARITY perspective.

    Focus ONLY on:
    - Writing clarity
    - Tone consistency
    - Readability
    """
    content: str = dspy.InputField(description="Content to evaluate")
    context: str = dspy.InputField(description="Background context")

    style_score: int = dspy.OutputField(description="Score 0-100")
    style_feedback: str = dspy.OutputField(description="Style issues found")
    style_approved: bool = dspy.OutputField(description="True if style is good")


class CompletenessCriticSignature(dspy.Signature):
    """
    Evaluate content from a COMPLETENESS perspective.

    Focus ONLY on:
    - All requirements addressed
    - Nothing missing
    - Appropriate depth
    """
    content: str = dspy.InputField(description="Content to evaluate")
    requirements: str = dspy.InputField(description="Original requirements")

    completeness_score: int = dspy.OutputField(description="Score 0-100")
    completeness_feedback: str = dspy.OutputField(description="Missing elements")
    completeness_approved: bool = dspy.OutputField(description="True if complete")


# =============================================================================
# AGGREGATOR SIGNATURE
# =============================================================================

class AggregatorSignature(dspy.Signature):
    """
    Synthesize feedback from multiple critics into a final assessment.

    Combine all perspectives and produce:
    - Overall score (weighted average)
    - Combined feedback (prioritized)
    - Final approval decision
    """
    technical_feedback: str = dspy.InputField()
    technical_score: int = dspy.InputField()
    technical_approved: bool = dspy.InputField()

    style_feedback: str = dspy.InputField()
    style_score: int = dspy.InputField()
    style_approved: bool = dspy.InputField()

    completeness_feedback: str = dspy.InputField()
    completeness_score: int = dspy.InputField()
    completeness_approved: bool = dspy.InputField()

    overall_score: int = dspy.OutputField(description="Weighted average score")
    combined_feedback: str = dspy.OutputField(description="Prioritized feedback")
    approved: bool = dspy.OutputField(description="True only if ALL critics approve")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def call_with_retry(agent, agent_name: str, max_retries: int = 3, **kwargs):
    """Retry agent calls with exponential backoff."""
    import random

    for attempt in range(max_retries):
        try:
            result = await agent.acall(**kwargs)
            return result
        except Exception as e:
            is_rate_limit = "429" in str(e) or "rate limit" in str(e).lower()

            if attempt < max_retries - 1:
                wait_time = 30 if is_rate_limit else (2 ** attempt) * 5
                print(f"⚠ {agent_name} retry {attempt + 1}, waiting {wait_time}s")
                await asyncio.sleep(wait_time)
            else:
                raise


def aggregate_scores(results: dict, weights: dict = None) -> int:
    """Calculate weighted average of scores."""
    if weights is None:
        weights = {"technical": 0.4, "style": 0.3, "completeness": 0.3}

    total = (
        results['technical'].technical_score * weights['technical'] +
        results['style'].style_score * weights['style'] +
        results['completeness'].completeness_score * weights['completeness']
    )
    return int(total)


def combine_feedback(results: dict) -> str:
    """Combine feedback from all critics, prioritized by severity."""
    feedback_parts = []

    # Technical issues first (most critical)
    if not results['technical'].technical_approved:
        feedback_parts.append(f"**Technical Issues:**\n{results['technical'].technical_feedback}")

    # Completeness second
    if not results['completeness'].completeness_approved:
        feedback_parts.append(f"**Missing Elements:**\n{results['completeness'].completeness_feedback}")

    # Style last
    if not results['style'].style_approved:
        feedback_parts.append(f"**Style Issues:**\n{results['style'].style_feedback}")

    if not feedback_parts:
        return "All criteria passed!"

    return "\n\n".join(feedback_parts)


# =============================================================================
# FAN-IN/FAN-OUT MODULE
# =============================================================================

class FanInFanOutModule(dspy.Module):
    """
    Multi-critic parallel evaluation pattern.

    Runs multiple critics in parallel, then aggregates results.
    """

    def __init__(self, shared_lm):
        """
        Initialize with shared LM instance.

        Args:
            shared_lm: Singleton LM instance (REQUIRED)
        """
        if shared_lm is None:
            raise ValueError("FanInFanOutModule requires a shared_lm instance.")

        self.lm = shared_lm

        # Create critics (all use Predict - evaluation tasks)
        self.technical_critic = dspy.Predict(TechnicalCriticSignature)
        self.style_critic = dspy.Predict(StyleCriticSignature)
        self.completeness_critic = dspy.Predict(CompletenessCriticSignature)

        # Optional: LLM-based aggregator
        self.aggregator = dspy.Predict(AggregatorSignature)

        # Inject singleton LM into ALL predictors
        self.technical_critic.set_lm(self.lm)
        self.style_critic.set_lm(self.lm)
        self.completeness_critic.set_lm(self.lm)
        self.aggregator.set_lm(self.lm)

    def forward(self, content: str, context: str = "", requirements: str = "", **kwargs):
        """
        Synchronous execution (sequential) for optimization.

        Note: In sync mode, we run sequentially. Use aforward() for parallel.
        """
        # Run critics sequentially
        technical = self.technical_critic(
            content=content,
            context=context,
            **kwargs
        )

        style = self.style_critic(
            content=content,
            context=context,
            **kwargs
        )

        completeness = self.completeness_critic(
            content=content,
            requirements=requirements,
            **kwargs
        )

        # Aggregate (using function, not LLM for simplicity in sync mode)
        results = {'technical': technical, 'style': style, 'completeness': completeness}
        overall_score = aggregate_scores(results)
        combined_feedback = combine_feedback(results)
        all_approved = (
            technical.technical_approved and
            style.style_approved and
            completeness.completeness_approved
        )

        return dspy.Prediction(
            technical=technical,
            style=style,
            completeness=completeness,
            overall_score=overall_score,
            combined_feedback=combined_feedback,
            approved=all_approved,
        )

    async def aforward(self, content: str, context: str = "", requirements: str = "", **kwargs):
        """
        Async production execution with PARALLEL critics.

        Uses asyncio.gather() to run all critics simultaneously.
        """
        import time
        start = time.time()

        # =================================================================
        # FAN-OUT: Run all critics in parallel
        # =================================================================
        technical_task = call_with_retry(
            self.technical_critic,
            agent_name="technical_critic",
            content=content,
            context=context,
            **kwargs
        )

        style_task = call_with_retry(
            self.style_critic,
            agent_name="style_critic",
            content=content,
            context=context,
            **kwargs
        )

        completeness_task = call_with_retry(
            self.completeness_critic,
            agent_name="completeness_critic",
            content=content,
            requirements=requirements,
            **kwargs
        )

        # Execute all tasks in parallel
        technical, style, completeness = await asyncio.gather(
            technical_task,
            style_task,
            completeness_task
        )

        parallel_time = time.time() - start

        # =================================================================
        # FAN-IN: Aggregate results
        # =================================================================
        results = {'technical': technical, 'style': style, 'completeness': completeness}

        # Option 1: Function-based aggregation (faster, deterministic)
        overall_score = aggregate_scores(results)
        combined_feedback = combine_feedback(results)
        all_approved = (
            technical.technical_approved and
            style.style_approved and
            completeness.completeness_approved
        )

        # Option 2: LLM-based aggregation (uncomment if you need synthesis)
        # aggregator_result = await call_with_retry(
        #     self.aggregator,
        #     agent_name="aggregator",
        #     technical_feedback=technical.technical_feedback,
        #     technical_score=technical.technical_score,
        #     technical_approved=technical.technical_approved,
        #     style_feedback=style.style_feedback,
        #     style_score=style.style_score,
        #     style_approved=style.style_approved,
        #     completeness_feedback=completeness.completeness_feedback,
        #     completeness_score=completeness.completeness_score,
        #     completeness_approved=completeness.completeness_approved,
        # )

        return dspy.Prediction(
            technical=technical,
            style=style,
            completeness=completeness,
            overall_score=overall_score,
            combined_feedback=combined_feedback,
            approved=all_approved,
            timings={'parallel_critics': parallel_time},
        )


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

async def main():
    shared_lm = get_shared_lm()
    module = FanInFanOutModule(shared_lm=shared_lm)

    result = await module.aforward(
        content="Draft email content here...",
        context="B2B SaaS outreach",
        requirements="Must mention product benefits and include CTA"
    )

    print(f"Overall Score: {result.overall_score}")
    print(f"Approved: {result.approved}")
    print(f"Combined Feedback:\n{result.combined_feedback}")
    print(f"Parallel execution time: {result.timings['parallel_critics']:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## DSPy-Specific Notes

- **asyncio.gather() for parallelism:** DSPy predictors support `acall()` for async execution. Use `asyncio.gather()` to run multiple calls simultaneously.

- **Shared LM enables parallelism:** The singleton LM pattern with `max_parallel_requests=2000` allows true concurrent execution without connection exhaustion.

- **Function vs LLM aggregation:** For simple aggregation (weighted scores, combining feedback), use Python functions. Only use an LLM aggregator if you need synthesis or complex reasoning.

- **All critics use Predict:** Evaluation tasks don't benefit from ChainOfThought reasoning. Use `dspy.Predict` for all critics.

---

## Key Patterns

### 1. Parallel Execution with asyncio.gather

```python
# Create tasks (don't await yet)
task_a = call_with_retry(self.agent_a, "agent_a", ...)
task_b = call_with_retry(self.agent_b, "agent_b", ...)
task_c = call_with_retry(self.agent_c, "agent_c", ...)

# Execute all in parallel
result_a, result_b, result_c = await asyncio.gather(
    task_a, task_b, task_c
)
```

### 2. Weighted Score Aggregation

```python
def aggregate_scores(results: dict, weights: dict) -> int:
    """Combine scores with configurable weights."""
    total = sum(
        getattr(results[key], f"{key}_score") * weight
        for key, weight in weights.items()
    )
    return int(total)
```

### 3. Multi-Flag Approval

```python
# ALL critics must approve
all_approved = all([
    results['technical'].technical_approved,
    results['style'].style_approved,
    results['completeness'].completeness_approved,
])
```

### 4. Prioritized Feedback Combination

```python
# Order feedback by criticality
if not technical_approved:
    feedback.append(technical_feedback)  # Most critical first
if not completeness_approved:
    feedback.append(completeness_feedback)
if not style_approved:
    feedback.append(style_feedback)  # Least critical last
```

---

## Variants

### Fan-out Only (No Aggregation)

When you just need parallel results without combining:

```python
async def aforward(self, content: str, **kwargs):
    results = await asyncio.gather(
        self.analyst_a.acall(content=content),
        self.analyst_b.acall(content=content),
        self.analyst_c.acall(content=content),
    )

    return dspy.Prediction(
        analyst_a=results[0],
        analyst_b=results[1],
        analyst_c=results[2],
    )
```

### Dynamic Fan-out

When the number of parallel agents varies:

```python
async def aforward(self, content: str, perspectives: List[str], **kwargs):
    tasks = [
        self.generic_critic.acall(content=content, perspective=p)
        for p in perspectives
    ]

    results = await asyncio.gather(*tasks)

    return dspy.Prediction(
        results=list(zip(perspectives, results)),
    )
```

---

## Pitfalls & Best Practices

**Pitfalls:**

- **Sequential when parallel is possible** — If tasks are independent, use `asyncio.gather()` instead of sequential `await`.

- **No error handling in gather** — One failed task fails all. Consider `return_exceptions=True` for graceful degradation.

- **Creating LM per parallel task** — All parallel tasks should share the singleton LM.

**Best Practices:**

- **Keep aggregation simple** — Use Python functions for score math. Only use LLM aggregator for complex synthesis.

- **Order feedback by priority** — Technical/factual issues before style issues.

- **Time the parallel section** — Track how much time parallel execution saves.

- **Use return_exceptions for resilience:**
  ```python
  results = await asyncio.gather(*tasks, return_exceptions=True)
  valid_results = [r for r in results if not isinstance(r, Exception)]
  ```

---

## Comparison with Other Patterns

| Aspect | Fan-in/Fan-out | Pipeline | Router | Loop |
|--------|----------------|----------|--------|------|
| Execution | Parallel | Sequential | Conditional | Cyclical |
| Data flow | Same input to all | Output → Input | Input determines path | Iterative refinement |
| Use case | Multi-perspective | Transformation | Decision routing | Quality gates |
| Performance | Faster (parallel) | Slower (sequential) | Varies | Varies |
