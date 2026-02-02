# DSPy Optimization Overview

## What is DSPy Optimization?

DSPy treats prompt engineering as **compilation** rather than manual crafting. Instead of hand-tuning prompts:

1. **Define structure** - Signatures and Modules specify task input/output
2. **Provide examples** - Training data shows desired behavior
3. **Define metrics** - Functions that measure success
4. **Run optimizer** - Automatically improves prompts to maximize metrics

This enables:
- **Reproducible improvements** - Metrics track progress objectively
- **Systematic iteration** - Data quality → metric refinement → optimizer selection
- **Transfer learning** - Optimized prompts can be saved and reloaded
- **Distillation** - Large model knowledge can be distilled into smaller models

---

## The Optimization Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DSPy Optimization Workflow                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. DEFINE                    2. PREPARE                   3. OPTIMIZE      │
│  ┌──────────────┐            ┌──────────────┐            ┌──────────────┐   │
│  │  Signatures  │            │  Training    │            │   Select     │   │
│  │  & Modules   │            │  Data        │            │  Optimizer   │   │
│  └──────┬───────┘            └──────┬───────┘            └──────┬───────┘   │
│         │                           │                           │           │
│         │  Define I/O               │  Create Examples          │  Run      │
│         │  types                    │  with labels              │  compile()│
│         ▼                           ▼                           ▼           │
│  ┌──────────────┐            ┌──────────────┐            ┌──────────────┐   │
│  │   Metric     │◀───────────│  Stratified  │───────────▶│  Optimized   │   │
│  │  Function    │            │   Split      │            │   Program    │   │
│  └──────────────┘            └──────────────┘            └──────────────┘   │
│                                                                  │           │
│                                                                  │           │
│  4. DEPLOY                                                       │           │
│  ┌──────────────┐                                               │           │
│  │  Production  │◀──────────────────────────────────────────────┘           │
│  │   .load()    │                                                           │
│  └──────────────┘                                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## When to Optimize

### Good Candidates for Optimization

| Scenario | Why Optimize |
|----------|--------------|
| Multi-agent pipelines | Joint optimization across modules improves system performance |
| Classification/ranking tasks | Clear right/wrong answers enable strong metrics |
| Structured output with enums | Validation failures provide actionable feedback |
| Have production logs/feedback | Real usage data enables targeted improvements |
| Need consistent quality | Optimization reduces variance across inputs |

### Poor Candidates for Optimization

| Scenario | Better Approach |
|----------|-----------------|
| Exploratory/creative tasks | Manual prompt tuning with human feedback |
| < 20 training examples | Few-shot prompting or manual examples |
| No clear success metric | Define metrics first, then optimize |
| Rapidly changing requirements | Stabilize requirements before investing in optimization |
| Simple single-turn tasks | Direct prompting often sufficient |

---

## Optimizer Selection Guide

| Scenario | Optimizer | Why |
|----------|-----------|-----|
| **Small data** (<50 examples) | `BootstrapFewShot` | Self-teaching with minimal data |
| **Medium data** (50-200 examples) | `MIPROv2` | Bayesian optimization of instructions |
| **Have feedback/logs** | `GEPA` | Pareto frontier + feedback-aware improvement |
| **Multi-signature modules** | `GEPA` | Better at joint optimization of multiple components |
| **Need smaller model** | `BootstrapFinetune` | Distill to efficient production model |
| **Budget constrained** | `BootstrapFewShot` | Fewest LLM calls during optimization |

### GEPA vs MIPROv2

For multi-agent workflows, **GEPA is recommended** because:

1. **Feedback-aware** - Uses structured feedback to guide instruction proposals
2. **Pareto frontier** - Finds best trade-offs across competing objectives
3. **Component-aware** - Routes feedback to specific modules via `pred_name`
4. **Custom proposers** - Supports domain-aware instruction generation
5. **Merge capability** - Combines best instructions from different candidates

---

## Cost Considerations

### Optimization Cost Factors

| Factor | Impact | Mitigation |
|--------|--------|------------|
| **Trainset size** | More examples = more LLM calls | Start with 50-100 examples |
| **Valset evaluations** | Full evals are expensive | Keep valset small (10-15), stratified |
| **Reflection LM** | Expensive model for feedback | Use thinking budget wisely |
| **Iterations** | More iterations = better results | Set max_full_evals limit |
| **Parallel threads** | Faster but concurrent API load | Match to rate limits |

### Cost Estimation

For a 7-module pipeline with 116 train / 12 val examples:

```
Per iteration:
- Trainset sampling: ~20 examples × 7 modules × reflection_lm = 140 calls
- Proposal generation: ~7 modules × proposer_lm = 7 calls
- Full evaluation: 12 val examples × 7 modules = 84 calls

8 iterations total: ~1,848 LLM calls
```

**Tip:** Use cheaper models for student (2.5 Flash Lite) and expensive models only for reflection/proposing (2.5 Pro).

---

## Three-Tier Model Architecture

Production-proven model configuration for optimization:

```python
# 1. STUDENT LM - Cheap, used by agents during optimization
student_lm = dspy.LM(
    "gemini/gemini-2.5-flash-lite",
    temperature=0.7,
    thinking={"type": "disabled"},  # No reasoning needed
    max_tokens=30000
)

# 2. REFLECTION LM - Expensive, used for evaluation and feedback
reflection_lm = dspy.LM(
    "gemini/gemini-2.5-pro",
    temperature=0.7,
    thinking_budget=10000,  # Extended thinking for analysis
    max_tokens=60000
)

# 3. PROPOSER LM - Expensive, used for instruction generation
# (Often same as reflection_lm, or configured in custom proposer)
```

---

## Quick Start Example

```python
import dspy

# 1. Define your module (already done)
class MyPipeline(dspy.Module):
    def __init__(self):
        self.agent_a = dspy.Predict(SignatureA)
        self.agent_b = dspy.Predict(SignatureB)

    def forward(self, input_field):
        result_a = self.agent_a(input=input_field)
        result_b = self.agent_b(input=result_a.output)
        return dspy.Prediction(output=result_b.output)

# 2. Load training data
trainset, valset = load_stratified_data()

# 3. Define metric
def my_metric(example, pred, trace=None, pred_name=None):
    score = evaluate_output(example, pred)
    feedback = generate_feedback(example, pred, pred_name)
    return dspy.Prediction(score=score, feedback=feedback)

# 4. Run optimization
gepa = dspy.GEPA(
    metric=my_metric,
    reflection_lm=reflection_lm,
    num_threads=16,
    max_full_evals=8,
    use_merge=True,
    component_selector="all"
)

optimized = gepa.compile(
    student=MyPipeline(),
    trainset=trainset,
    valset=valset
)

# 5. Save for production
optimized.save("my_pipeline_optimized.json")
```

---

## Related Documentation

- [Metrics Design](metrics.md) - How to write effective metrics
- [Training Data](data.md) - Preparing and splitting training data
- [GEPA Workflow](gepa-workflow.md) - End-to-end GEPA optimization
- [Custom Proposers](custom-proposers.md) - Domain-aware instruction generation
