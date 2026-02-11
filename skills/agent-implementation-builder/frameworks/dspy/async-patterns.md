# DSPy Async Patterns Reference

**When to read this:** Before implementing parallel module execution, multi-model setups, or fan-out patterns in DSPy.

This document covers async execution, parallel fan-out, multi-model singletons, and graceful degradation.

---

## Quick Reference

```python
# Fan-out N instances in parallel
results = await asyncio.gather(*[
    module.acall(input=config) for config in configs
], return_exceptions=True)

# Filter out failures
successful = [r for r in results if not isinstance(r, Exception)]

# Multi-model setup
flash_lm = get_flash_lm()  # Fast, cheap
pro_lm = get_pro_lm()      # Powerful, expensive
self.extractor.set_lm(flash_lm)
self.synthesizer.set_lm(pro_lm)
```

---

## asyncio.gather Fan-Out Pattern

Use `asyncio.gather()` to run multiple DSPy modules in parallel. This is the primary pattern for fan-in-fan-out architectures.

### Basic Fan-Out

```python
import asyncio
import dspy


class FanOutTeam(dspy.Module):
    def __init__(self, shared_lm, configs: list[dict]):
        if shared_lm is None:
            raise ValueError("shared_lm required")

        self.lm = shared_lm
        self.configs = configs

        # One predictor shared across all fan-out instances
        self.analyzer = dspy.ChainOfThought(AnalysisSignature)
        self.analyzer.set_lm(self.lm)

    async def aforward(self, input_data: str) -> dspy.Prediction:
        # Fan out: run N instances in parallel
        results = await asyncio.gather(*[
            self.analyzer.acall(
                input_data=input_data,
                perspective=config["perspective"],
                instructions=config["instructions"],
            )
            for config in self.configs
        ])

        return dspy.Prediction(analyses=results)
```

### Fan-Out with Different Modules

```python
class ParallelPipeline(dspy.Module):
    def __init__(self, shared_lm):
        self.idea_gen = dspy.ChainOfThought(IdeaSignature)
        self.evidence = dspy.Predict(EvidenceSignature)

        self.idea_gen.set_lm(shared_lm)
        self.evidence.set_lm(shared_lm)

    async def aforward(self, question: str) -> dspy.Prediction:
        # Run independent modules in parallel
        idea_result, evidence_result = await asyncio.gather(
            self.idea_gen.acall(question=question),
            self.evidence.acall(question=question),
        )

        return dspy.Prediction(
            ideas=idea_result.ideas,
            evidence=evidence_result.evidence,
        )
```

### Fan-Out of N Instances (Expert Panel Pattern)

When the same signature is called N times with different configs:

```python
class ExpertPanel(dspy.Module):
    """Fan out 6 expert perspectives in parallel."""

    def __init__(self, shared_lm):
        if shared_lm is None:
            raise ValueError("shared_lm required")

        self.expert = dspy.ChainOfThought(ExpertSignature)
        self.expert.set_lm(shared_lm)

        self.perspectives = [
            ("trend_analyst", TREND_INSTRUCTIONS),
            ("brand_guardian", BRAND_INSTRUCTIONS),
            ("performance_analyst", PERFORMANCE_INSTRUCTIONS),
            ("platform_specialist", PLATFORM_INSTRUCTIONS),
            ("contrarian", CONTRARIAN_INSTRUCTIONS),
            ("audience_proxy", AUDIENCE_INSTRUCTIONS),
        ]

    async def aforward(self, research_docs: str, entity_profile: str,
                       content_pillars: str) -> dspy.Prediction:
        results = await asyncio.gather(*[
            self.expert.acall(
                expert_perspective=perspective,
                perspective_instructions=instructions,
                research_docs=research_docs,
                entity_profile=entity_profile,
                content_pillars=content_pillars,
            )
            for perspective, instructions in self.perspectives
        ])

        return dspy.Prediction(expert_analyses=results)
```

---

## Graceful Degradation

Use `return_exceptions=True` to prevent one failure from killing all parallel tasks. This is essential for production systems where some sub-modules may fail (e.g., broken Apify actors).

### Pattern: return_exceptions=True

```python
async def aforward(self, input_data: str) -> dspy.Prediction:
    results = await asyncio.gather(*[
        module.acall(input=config)
        for config in self.configs
    ], return_exceptions=True)  # Failed tasks return Exception objects

    # Separate successes from failures
    successful = []
    failed = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            failed.append({
                "config": self.configs[i],
                "error": str(result),
            })
        else:
            successful.append(result)

    if not successful:
        # All failed — return error
        return dspy.Prediction(
            results=[],
            error=f"All {len(failed)} modules failed",
            failed=failed,
        )

    # Continue with partial results
    return dspy.Prediction(
        results=successful,
        error=None,
        failed=failed,
    )
```

### When to Use Graceful Degradation

| Scenario | Pattern | Reasoning |
|----------|---------|-----------|
| Multiple independent data sources | `return_exceptions=True` | One source failing shouldn't block others |
| Expert panel (N perspectives) | `return_exceptions=True` | 4 of 6 experts is still useful |
| Pipeline stages (sequential) | Retry, then fail | Each stage depends on the previous |
| Critical single operation | Retry with backoff | Must succeed for workflow to continue |

**Key distinction:** Graceful degradation handles **permanent** failures (broken actor, missing data source). This is different from **retry** logic, which handles **transient** failures (rate limits, timeouts). Use both together:

```python
# Retry handles transient errors per-module
# Graceful degradation handles permanent failures across modules
results = await asyncio.gather(*[
    call_with_retry(module, f"module_{i}", input=config)
    for i, config in enumerate(self.configs)
], return_exceptions=True)
```

---

## Multi-Model Singleton Pattern

When a team uses different model tiers for different tasks (e.g., Flash for extraction, Pro for synthesis).

### Factory Functions

```python
# utils.py

import os
import dspy

_flash_lm = None
_pro_lm = None


def get_flash_lm():
    """
    Get singleton Flash LM for fast, cheap operations.

    Use for: extraction, classification, search parameter reasoning,
    simple evaluation, high-volume parallel tasks.
    """
    global _flash_lm
    if _flash_lm is None:
        _flash_lm = dspy.LM(
            os.getenv("FLASH_MODEL", "gemini/gemini-2.5-flash"),
            api_key=os.getenv("GOOGLE_API_KEY"),
            max_parallel_requests=2000,
            timeout=120,
        )
    return _flash_lm


def get_pro_lm():
    """
    Get singleton Pro LM for complex reasoning tasks.

    Use for: multi-document synthesis, creative generation,
    complex evaluation, tasks requiring deep reasoning.
    """
    global _pro_lm
    if _pro_lm is None:
        _pro_lm = dspy.LM(
            os.getenv("PRO_MODEL", "gemini/gemini-2.5-pro"),
            api_key=os.getenv("GOOGLE_API_KEY"),
            max_parallel_requests=100,  # Pro is more expensive, limit concurrency
            timeout=120,
        )
    return _pro_lm
```

### Assigning Different LMs to Different Predictors

```python
class ResearchTeam(dspy.Module):
    def __init__(self, flash_lm, pro_lm):
        if flash_lm is None or pro_lm is None:
            raise ValueError("Both flash_lm and pro_lm required")

        # Fast operations use Flash
        self.search_agent = dspy.ReAct(
            signature=SearchSignature,
            tools=[search_tool],
            max_iters=5
        )
        self.search_agent.set_lm(flash_lm)

        self.analyzer = dspy.Predict(AnalysisSignature)
        self.analyzer.set_lm(flash_lm)

        # Complex synthesis uses Pro
        self.synthesizer = dspy.ChainOfThought(SynthesisSignature)
        self.synthesizer.set_lm(pro_lm)

    async def aforward(self, query: str) -> dspy.Prediction:
        # Search (Flash) → Analyze (Flash) → Synthesize (Pro)
        search_result = await self.search_agent.acall(query=query)
        analysis = await self.analyzer.acall(data=search_result.raw_results)
        synthesis = await self.synthesizer.acall(
            analysis=format_analysis(analysis)
        )
        return synthesis
```

### Model Tier Selection Guide

| Task Type | Model Tier | Examples |
|-----------|-----------|---------|
| Extraction / classification | Flash | Data extraction, category matching, routing |
| Search parameter reasoning | Flash | ReAct agents deciding search terms |
| Simple evaluation (checklist) | Flash | Quality checks, pass/fail decisions |
| High-volume parallel tasks | Flash | 5+ concurrent instances, fan-out panels |
| Multi-document synthesis | Pro | Signal Blender, cross-platform analysis |
| Creative generation | Pro | Content drafting, idea generation |
| Complex reasoning | Pro | Multi-factor evaluation, strategic analysis |
| Quality-critical decisions | Pro | Final selection, refinement |

**Cost rule of thumb:** If the agent runs N instances in parallel, use Flash. If it runs once and its output is critical, consider Pro.

---

## Shared LM and Concurrency

The singleton LM pattern is safe for concurrent use. DSPy's LM class uses `max_parallel_requests` to manage concurrent API calls through connection pooling.

```python
# Safe: multiple modules sharing one LM instance
shared_lm = get_shared_lm()

# All these can run concurrently via asyncio.gather
agent_a = dspy.Predict(SignatureA)
agent_b = dspy.Predict(SignatureB)
agent_c = dspy.ReAct(SignatureC, tools=[tool])

agent_a.set_lm(shared_lm)
agent_b.set_lm(shared_lm)
agent_c.set_lm(shared_lm)

# Concurrent execution — shared LM handles connection pooling
results = await asyncio.gather(
    agent_a.acall(input="..."),
    agent_b.acall(input="..."),
    agent_c.acall(input="..."),
)
```

**Key config:** `max_parallel_requests` on the LM instance controls how many concurrent API requests are allowed. Set this based on your API provider's rate limits.

---

## Anti-Patterns

### DO NOT: Create separate LM instances per fan-out instance

```python
# WRONG: Creates N LM instances for N parallel tasks
results = await asyncio.gather(*[
    create_agent_with_new_lm(config).acall(input=data)
    for config in configs
])
```

**Why:** Connection pool exhaustion at scale. Use one shared LM.

### DO NOT: Skip return_exceptions for independent tasks

```python
# WRONG: One failure kills all parallel tasks
results = await asyncio.gather(*[
    module.acall(input=config)
    for config in configs
])  # Missing return_exceptions=True
```

**Why:** If 1 of 5 search agents fails, you lose all 5 results.

### DO NOT: Use Pro model for high-volume parallel tasks

```python
# WRONG: 6 parallel Pro calls is expensive and slow
for expert in experts:
    expert.set_lm(get_pro_lm())  # Pro for each of 6 experts
```

**Instead:** Use Flash for parallel fan-out, Pro for single critical operations.

---

## Related Documentation

- [DSPy Cheatsheet](CHEATSHEET.md) — Critical rules and singleton LM pattern
- [ReAct Module](react.md) — Tool-using agents with ReAct
- [Loop Pattern](../../../agent-teams/dspy/loop.md) — Iterative refinement with quality gates
