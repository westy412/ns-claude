# GEPA Optimization Workflow

## Why GEPA for Multi-Agent Pipelines

GEPA (Guided Evolution with Pareto Aggregation) is the recommended optimizer for multi-signature DSPy modules because:

| Feature | Benefit |
|---------|---------|
| **Feedback-aware** | Uses structured feedback to guide instruction proposals |
| **Pareto frontier** | Finds best trade-offs across competing objectives |
| **Component-aware** | Routes feedback to specific modules via `pred_name` |
| **Custom proposers** | Supports domain-aware instruction generation |
| **Merge capability** | Combines best instructions from different candidates |

---

## Setting Up GEPA

### Basic Configuration

```python
import dspy

# 1. Configure LMs
student_lm = dspy.LM(
    "gemini/gemini-2.5-flash-lite",
    temperature=0.7,
    thinking={"type": "disabled"},
    max_tokens=30000
)

reflection_lm = dspy.LM(
    "gemini/gemini-2.5-pro",
    temperature=0.7,
    thinking_budget=10000,
    max_tokens=60000
)

# 2. Set student as default
dspy.configure(lm=student_lm)

# 3. Create GEPA optimizer
gepa = dspy.GEPA(
    metric=create_judge,                    # Your metric function
    reflection_lm=reflection_lm,            # Expensive model for feedback
    num_threads=16,                         # Parallel evaluation
    track_stats=True,                       # Track optimization statistics
    track_best_outputs=True,                # Save best outputs per iteration
    max_full_evals=8,                       # Maximum full evaluations on valset
    use_merge=True,                         # Combine best components
    component_selector="all",               # Optimize all components
    warn_on_score_mismatch=False            # Required for module-specific feedback
)
```

### Key Parameters

| Parameter | Recommended | Purpose |
|-----------|-------------|---------|
| `max_full_evals` | 4-8 | Limits expensive full valset evaluations |
| `num_threads` | 16 | Parallel candidate evaluation |
| `use_merge` | True | Combines best instructions across candidates |
| `component_selector` | "all" | Optimizes all modules each iteration |
| `warn_on_score_mismatch` | False | Required when using module-specific feedback routing |
| `track_stats` | True | Enables optimization analytics |
| `track_best_outputs` | True | Saves best outputs for review |

---

## Running Optimization

```python
# Load your module
student = MyPipeline()

# Load stratified data
trainset, valset = load_stratified_data()

# Run optimization
optimized_program = gepa.compile(
    student=student,
    trainset=trainset,
    valset=valset
)

# Save for production
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
optimized_program.save(f"pipeline_optimized_{timestamp}.json")
```

---

## Custom Instruction Proposers

The default GEPA proposer generates generic instruction improvements. For complex domains, create a **custom proposer** that injects domain knowledge.

See [Custom Proposers](custom-proposers.md) for full documentation.

```python
from your_proposers import DomainAwareProposer

# Create custom proposer with domain context
custom_proposer = DomainAwareProposer(
    domain_definitions=load_domain_definitions(),
    proposer_lm=reflection_lm
)

# Use in GEPA
gepa = dspy.GEPA(
    metric=create_judge,
    reflection_lm=reflection_lm,
    instruction_proposer=custom_proposer,  # Inject custom proposer
    # ... other params
)
```

---

## Scoring Patterns

### Pattern 1: Equal Weighting Within Components

The standard pattern uses equal weighting with simple averaging:

```python
def get_score(llm_judge_output) -> float:
    """
    Sum all individual scores and normalize to 0-1 range.

    Pattern: sum(scores) / (num_scores * 100) = score in [0, 1]
    """
    # Individual scores are 0-100 scale
    all_scores = [
        llm_judge_output.factual_accuracy_score,      # 0-100
        llm_judge_output.format_compliance_score,     # 0-100
        llm_judge_output.tone_alignment_score,        # 0-100
        llm_judge_output.length_compliance_score,     # 0-100
        llm_judge_output.personalization_score,       # 0-100
    ]

    # Sum and normalize: max = num_scores * 100
    total_score = sum(all_scores)
    max_possible = len(all_scores) * 100  # 5 * 100 = 500
    normalized_score = total_score / max_possible  # Result is 0-1

    return normalized_score
```

**Why this works:** GEPA expects scores in [0, 1] range. By dividing by `(num_scores * 100)`, we guarantee the result is always between 0 and 1.

### Pattern 2: Pipeline-Level Weighted Aggregation

When combining scores from different pipeline stages, use explicit weights that sum to 1.0:

```python
def aggregate_pipeline_scores(stage_scores: dict) -> float:
    """
    Combine stage scores with weights that sum to 1.0.

    This allows prioritizing certain stages (e.g., final output quality).
    """
    # Weights MUST sum to 1.0 to keep result in [0, 1]
    weights = {
        "final_output": 0.40,    # Most important - 40%
        "creation": 0.25,        # Foundation - 25%
        "critic": 0.20,          # Quality gating - 20%
        "iteration": 0.15,       # Improvement - 15%
    }
    # Sum: 0.40 + 0.25 + 0.20 + 0.15 = 1.0

    overall_score = sum(
        stage_scores[stage] * weight
        for stage, weight in weights.items()
    )

    return overall_score  # Guaranteed to be in [0, 1]
```

### Weight Selection Guide

| Stage/Dimension | Weight | Rationale |
|-----------------|--------|-----------|
| **Final output quality** | 0.40 | What the user sees matters most |
| **Initial creation** | 0.25 | Sets the foundation |
| **Quality gating** | 0.20 | Catches issues |
| **Iteration/refinement** | 0.15 | Polish and fixes |

**Key principle:** Weights must sum to 1.0 when aggregating already-normalized scores. This keeps the final score in [0, 1] range.

---

## Module-Specific Optimization

GEPA can optimize specific modules differently using `pred_name` routing:

```python
def create_judge(example, pred, trace=None, pred_name=None):
    """
    Return same overall score but module-specific feedback.
    """
    result = run_full_evaluation(example, pred)
    overall_score = result["overall_score"]

    if pred_name is None:
        return overall_score

    # Route feedback based on which module is being optimized
    feedback_map = {
        "agent_a.predict": result["agent_a_feedback"],
        "agent_b.predict": result["agent_b_feedback"],
        "agent_c.predict": result["agent_c_feedback"],
    }

    feedback = feedback_map.get(pred_name, result["comprehensive_feedback"])

    return dspy.Prediction(score=overall_score, feedback=feedback)
```

---

## Saving and Loading Optimized Programs

### Save After Optimization

```python
# Save with timestamp for versioning
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
optimized_program.save(f"pipeline_optimized_{timestamp}.json")

# Also save as "latest" for production
optimized_program.save("pipeline_optimized.json")
```

### Load in Production

```python
# In production code
pipeline = MyPipeline(shared_lm=get_shared_lm())
pipeline.load("pipeline_optimized.json")

# Execute with optimized prompts
result = await pipeline.acall(**inputs)
```

### What Gets Saved

The JSON file contains:
- Optimized instructions for each component
- Component names matching module structure
- Signature field definitions

It does **not** save:
- LM configuration (set at runtime)
- Module code (imported from source)
- Training data or metrics

---

## Production Integration

### Singleton LM Pattern

Critical for production performance with concurrent workflows:

```python
_shared_lm = None

def get_shared_lm():
    """Singleton LM for connection pooling."""
    global _shared_lm
    if _shared_lm is None:
        _shared_lm = dspy.LM(
            "gemini/gemini-2.5-flash-lite",
            temperature=0.7,
            thinking={"type": "disabled"},
            max_tokens=30000
        )
    return _shared_lm


class ProductionWorkflow:
    def __init__(self):
        self.lm = get_shared_lm()

        # Initialize and load optimized program
        self.pipeline = MyPipeline(shared_lm=self.lm)
        self.pipeline.load("pipeline_optimized.json")

    async def run(self, **inputs):
        return await self.pipeline.acall(**inputs)
```

### Why Singleton Matters

Without singleton LM at 100+ concurrent workflows:
```
httpcore.ConnectError: [Errno 24] Too many open files
```
or:
```
httpx.HTTPStatusError: 429 Too Many Requests
```

Singleton enables connection pooling, preventing 20x slowdown.

---

## Monitoring Optimization (MLflow)

MLflow provides automatic logging for DSPy optimization. One-line setup, no manual logging needed.

```python
import mlflow

# Enable autologging - this does EVERYTHING automatically
try:
    mlflow.dspy.autolog(
        log_compiles=True,              # Track optimization process
        log_evals=True,                 # Track evaluation results
        log_traces_from_compile=True    # Track program traces
    )

    # Configure local MLflow server
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("DSPy-Optimization-MyWorkflow")
except Exception:
    pass  # Don't break optimization if MLflow unavailable


# Now just run optimization normally - MLflow tracks everything
optimized = gepa.compile(
    student=student,
    trainset=trainset,
    valset=valset
)
```

**What gets logged automatically:**
- All optimization iterations
- Evaluation scores on train/val sets
- Program traces during compilation
- Best candidates at each iteration

**Note:** MLflow is for local development only. Wrap in try/except so it doesn't break optimization if the MLflow server isn't running.

---

## Complete GEPA Example

```python
import dspy
import json
from datetime import datetime

# 1. Configure LMs
student_lm = dspy.LM(
    "gemini/gemini-2.5-flash-lite",
    temperature=0.7,
    thinking={"type": "disabled"},
    max_tokens=30000
)

reflection_lm = dspy.LM(
    "gemini/gemini-2.5-pro",
    temperature=0.7,
    thinking_budget=10000,
    max_tokens=60000
)

dspy.configure(lm=student_lm)

# 2. Load data
trainset, valset = load_stratified_data()

# 3. Create custom proposer (optional but recommended)
custom_proposer = DomainAwareProposer(
    domain_definitions=load_domain_defs(),
    proposer_lm=reflection_lm
)

# 4. Configure GEPA
gepa = dspy.GEPA(
    metric=create_judge,
    reflection_lm=reflection_lm,
    instruction_proposer=custom_proposer,
    num_threads=16,
    track_stats=True,
    track_best_outputs=True,
    max_full_evals=8,
    use_merge=True,
    component_selector="all",
    warn_on_score_mismatch=False
)

# 5. Run optimization
student = MyPipeline()
optimized = gepa.compile(
    student=student,
    trainset=trainset,
    valset=valset
)

# 6. Save result
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
optimized.save(f"pipeline_optimized_{timestamp}.json")
optimized.save("pipeline_optimized.json")  # Latest for production

print(f"Optimization complete. Saved to pipeline_optimized_{timestamp}.json")
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Score not improving | Metric too coarse | Add dimensional scoring |
| Same score across modules | Missing `pred_name` routing | Implement feedback routing |
| Optimization very slow | Too many full evals | Reduce `max_full_evals` |
| Out of memory | Large trainset | Sample trainset, keep full valset |
| Rate limit errors | Too many parallel threads | Reduce `num_threads` |

---

## Related Documentation

- [Overview](overview.md) - Optimization concepts
- [Metrics](metrics.md) - Designing effective metrics
- [Training Data](data.md) - Preparing training examples
- [Custom Proposers](custom-proposers.md) - Domain-aware instruction generation
