# Singleton LM Pattern

**Critical for production**: One shared LM instance prevents 20x slowdown at scale.

## The Problem

Creating separate LM instances per module causes connection pool exhaustion when running 100+ concurrent workflows.

**Error you'll see:**
```
httpcore.ConnectError: [Errno 24] Too many open files
```
or:
```
httpx.HTTPStatusError: 429 Too Many Requests
```

## The Pattern

```python
import os
import dspy

# Module-level singleton
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
```

## Using the Singleton

```python
class MyPipeline(dspy.Module):
    def __init__(self, shared_lm):
        # Validate that singleton is passed
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

## Complete Example

```python
# utils.py
import os
import dspy

_shared_lm = None

def get_shared_lm():
    global _shared_lm
    if _shared_lm is None:
        _shared_lm = dspy.LM(
            os.getenv("MODEL_NAME", "gemini/gemini-2.5-flash"),
            api_key=os.getenv("GOOGLE_API_KEY"),
            max_parallel_requests=2000,
        )
    return _shared_lm


# team.py
from .utils import get_shared_lm
from .signatures import ExtractorSignature, AnalyzerSignature

class ExtractionPipeline(dspy.Module):
    def __init__(self, shared_lm):
        if shared_lm is None:
            raise ValueError("shared_lm required")

        self.extractor = dspy.Predict(ExtractorSignature)
        self.analyzer = dspy.Predict(AnalyzerSignature)

        self.extractor.set_lm(shared_lm)
        self.analyzer.set_lm(shared_lm)

    async def aforward(self, input_data: str):
        result1 = await self.extractor.acall(input=input_data)
        result2 = await self.analyzer.acall(extraction=result1.output)
        return result2


# main.py
async def main():
    lm = get_shared_lm()
    pipeline = ExtractionPipeline(shared_lm=lm)

    # Run many concurrent workflows with shared connection pool
    results = await asyncio.gather(*[
        pipeline.aforward(data)
        for data in large_dataset
    ])
```

## Anti-Patterns

```python
# WRONG: Creating LM instance per module
class MyPipeline(dspy.Module):
    def __init__(self):
        # Creates separate HTTP client - causes connection exhaustion
        self.lm = dspy.LM("gemini/gemini-2.5-flash")

        self.agent_a = dspy.Predict(AgentASignature)
        # WRONG: Not calling set_lm() - uses global default
```

```python
# WRONG: Creating LM in forward()
class MyPipeline(dspy.Module):
    async def aforward(self, input):
        lm = dspy.LM("gemini/...")  # New instance per call!
        self.agent.set_lm(lm)
        return await self.agent.acall(input=input)
```

## Checklist

- [ ] Singleton defined at module level in utils.py
- [ ] `max_parallel_requests=2000` configured
- [ ] Constructor validates `shared_lm is not None`
- [ ] `set_lm()` called on ALL predictors
- [ ] No LM instances created in `forward()` / `aforward()`

## Configuration

Also configure DSPy settings at module level:

```python
# At top of utils.py, BEFORE any async code
import dspy
dspy.settings.configure(async_max_workers=2000)
```
