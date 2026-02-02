# DSPy Metrics Design

## Metric Function Signature

Every DSPy metric follows this signature:

```python
def metric(example, pred, trace=None, pred_name=None):
    """
    Evaluate a prediction against ground truth.

    Args:
        example: Ground truth dspy.Example with expected outputs
        pred: Model prediction (dspy.Prediction)
        trace: Optimization trace (None during eval, populated during optimization)
        pred_name: Which signature being optimized (for GEPA module-specific feedback)

    Returns:
        float: Score between 0.0 and 1.0
        OR
        dspy.Prediction: With 'score' and 'feedback' fields
    """
```

---

## Trace-Aware Metrics

The `trace` parameter distinguishes **optimization** from **evaluation**:

```python
def metric(example, pred, trace=None, pred_name=None):
    # During optimization (trace is not None)
    # - Can access intermediate steps via trace
    # - Feedback is used to improve prompts

    # During evaluation (trace is None)
    # - Only final output matters
    # - Feedback is optional (for logging)

    if trace is not None:
        # Optimization mode - return feedback for improvement
        return dspy.Prediction(
            score=score,
            feedback="Specific feedback for instruction improvement"
        )
    else:
        # Evaluation mode - just return score
        return score
```

---

## Module-Specific Feedback Routing

For multi-module pipelines, GEPA calls your metric with `pred_name` indicating which module is being optimized.

### The Pattern

```python
def create_judge(example, pred, trace=None, pred_name=None):
    """
    Route feedback to specific modules based on pred_name.

    CRITICAL: Return the SAME overall_score regardless of pred_name,
    but DIFFERENT feedback based on which module is being optimized.

    Why: System performance is what matters (same score), but each
    module needs targeted feedback to improve (different feedback).
    """
    # Run full evaluation
    result = evaluate_all_modules(example, pred)
    overall_score = result["overall_score"]

    # If no pred_name, return just the score
    if pred_name is None:
        return overall_score

    # Route feedback based on which module is being optimized
    if pred_name == "agent_a.predict":
        feedback = result.get("agent_a_feedback", "")
    elif pred_name == "agent_b.predict":
        feedback = result.get("agent_b_feedback", "")
    elif pred_name == "agent_c.predict":
        feedback = result.get("agent_c_feedback", "")
    else:
        # Default: comprehensive feedback for all modules
        feedback = format_all_feedback(result)

    return dspy.Prediction(
        score=overall_score,  # SAME score for all modules
        feedback=feedback     # DIFFERENT feedback per module
    )
```

### Why This Pattern Works

1. **GEPA calls metric with `pred_name`** when optimizing each component
2. **Same overall score** ensures we optimize system performance, not individual metrics
3. **Module-specific feedback** helps proposer generate targeted improvements
4. **Fallback to comprehensive feedback** handles unknown component names

**Important:** Use `warn_on_score_mismatch=False` in GEPA config since the score intentionally stays the same across `pred_name` values.

---

## Dimensional Evaluation Pattern

Break complex evaluation into atomic dimensions for granular feedback:

```python
class DimensionalMetric(dspy.Module):
    """
    Evaluate output across multiple independent dimensions.

    Each dimension is scored separately, then aggregated.
    This provides granular feedback for optimization.
    """

    def __init__(self):
        self.evaluator = dspy.Predict(DimensionalEvaluatorSignature)

    def forward(self, pred, gold):
        result = self.evaluator(
            output=pred.output,
            expected=gold.expected_output
        )

        # Extract individual dimension scores
        dimension_scores = {
            "factual_accuracy": result.factual_accuracy_score,
            "format_compliance": result.format_compliance_score,
            "tone_appropriateness": result.tone_score,
            "length_compliance": result.length_score,
            "completeness": result.completeness_score,
        }

        # Aggregate (simple average or weighted)
        overall_score = sum(dimension_scores.values()) / len(dimension_scores)

        # Generate dimension-specific feedback
        feedback = self._format_dimension_feedback(dimension_scores, result)

        return {
            "score": overall_score / 100,  # Normalize to 0-1
            "feedback": feedback,
            "dimension_scores": dimension_scores
        }
```

### Example: 8-Bucket Semantic Evaluation

Instead of field-by-field scoring, group related fields into semantic buckets:

```python
def get_score(llm_judge_output) -> float:
    """
    Sum all dimension scores and normalize to 0-1 range.

    Uses 8 semantic buckets instead of field-by-field scoring.
    """
    all_scores = [
        # BUCKET 1: CORE IDENTITY (3 scores)
        llm_judge_output.core_identity_content_score,
        llm_judge_output.core_identity_format_score,
        llm_judge_output.specificity_score,

        # BUCKET 2: OFFERINGS (3 scores)
        llm_judge_output.offering_content_score,
        llm_judge_output.offering_format_score,
        llm_judge_output.sales_alignment_score,

        # BUCKET 3: TARGET AUDIENCE (2 scores)
        llm_judge_output.audience_content_score,
        llm_judge_output.audience_format_score,

        # ... more buckets
    ]

    total_score = sum(all_scores)
    max_possible = len(all_scores) * 100
    return total_score / max_possible
```

**Why buckets over fields:**
- Captures cross-field relationships
- Reduces metric complexity
- Enables "content" vs "format" separation
- Provides actionable feedback categories

---

## Pre-Validation Gating

Validate constraints BEFORE expensive LLM evaluation:

```python
def metric_with_gating(example, pred, trace=None, pred_name=None):
    """
    Gate expensive LLM evaluation behind cheap validation.

    If validation fails, return low score + validation-only feedback.
    This focuses optimization on fixing validation errors first.
    """
    # 1. CHEAP VALIDATION FIRST
    enum_errors = validate_enum_fields(pred, ENUM_FIELD_DEFINITIONS)

    if enum_errors:
        # CRITICAL: Skip LLM evaluation entirely
        return dspy.Prediction(
            score=0.05,  # Very low score to penalize failures
            feedback=format_enum_errors(enum_errors) +
                     "\n\nNO FURTHER EVALUATION. Fix enum errors first."
        )

    # 2. EXPENSIVE LLM EVALUATION (only if validation passes)
    result = run_llm_evaluation(example, pred)

    return dspy.Prediction(
        score=result["score"],
        feedback=result["feedback"]
    )
```

**Why this matters:**
- Enum validation is exact string matching (character-for-character)
- Invalid enum values cause workflow abort (Pydantic validation failure)
- 0.05 score + enum-only feedback forces GEPA to fix enums first
- Prevents wasting LLM calls on outputs that will fail validation

---

## AI-Judged Metrics

For subjective qualities, use an LLM as the judge:

```python
class LLMJudgeSignature(dspy.Signature):
    """
    Evaluate output quality across multiple dimensions.

    You are an expert evaluator. Score each dimension 0-100.
    Be critical and specific in your feedback.
    """

    output: str = dspy.InputField(desc="The output to evaluate")
    expected: str = dspy.InputField(desc="What good output looks like")
    criteria: str = dspy.InputField(desc="Evaluation criteria")

    factual_accuracy_score: int = dspy.OutputField(desc="0-100: Are facts correct?")
    format_compliance_score: int = dspy.OutputField(desc="0-100: Correct format?")
    quality_score: int = dspy.OutputField(desc="0-100: Overall quality?")
    feedback: str = dspy.OutputField(desc="Specific improvement suggestions")


class LLMJudgeMetric(dspy.Module):
    def __init__(self, judge_lm):
        self.judge = dspy.Predict(LLMJudgeSignature)
        self.judge.set_lm(judge_lm)  # Use expensive model for judging

    def forward(self, pred, gold):
        result = self.judge(
            output=pred.output,
            expected=gold.expected_output,
            criteria=self._get_criteria()
        )

        score = (
            result.factual_accuracy_score +
            result.format_compliance_score +
            result.quality_score
        ) / 300  # Normalize to 0-1

        return {"score": score, "feedback": result.feedback}
```

---

## Structured Feedback Format

Use consistent structure for actionable feedback:

```python
def format_feedback(dimension_scores, issues):
    """
    Format feedback with WHAT/WHY/HOW/TARGET structure.
    """
    feedback = f"""# EVALUATION REPORT

## OVERALL SCORE: {score:.2f}/1.0

## DIMENSION SCORES:
┌─────────────────────────┬───────┬──────────────────┐
│ Dimension               │ Score │ Status           │
├─────────────────────────┼───────┼──────────────────┤
│ Factual Accuracy        │ {scores['factual']:>5} │ {'✓ PASS' if scores['factual'] >= 70 else '✗ NEEDS WORK'} │
│ Format Compliance       │ {scores['format']:>5} │ {'✓ PASS' if scores['format'] >= 70 else '✗ NEEDS WORK'} │
└─────────────────────────┴───────┴──────────────────┘

## WHAT IS WRONG:
{bullet_list(issues)}

## WHY IT MATTERS:
- [Business impact of the issues]

## HOW TO IMPROVE:
- [Specific actions to fix]

## WHAT WOULD SCORE HIGHER:
- [Target behaviors for improvement]
"""
    return feedback
```

---

## Score Normalization

**Critical:** GEPA requires scores in [0, 1] range. Use these patterns:

### Pattern 1: Equal-Weighted Component Scores

```python
def get_score(llm_judge_output) -> float:
    """
    Sum all dimension scores and normalize to 0-1 range.

    Formula: sum(scores) / (num_scores * 100) = score in [0, 1]
    """
    # Individual scores are 0-100 scale
    all_scores = [
        llm_judge_output.factual_accuracy_score,
        llm_judge_output.format_compliance_score,
        llm_judge_output.tone_alignment_score,
        llm_judge_output.length_compliance_score,
        llm_judge_output.personalization_score,
    ]

    # Normalize: max = num_scores * 100
    total_score = sum(all_scores)
    max_possible = len(all_scores) * 100  # 5 * 100 = 500
    normalized_score = total_score / max_possible  # Always 0-1

    return normalized_score
```

### Pattern 2: Pipeline-Level Weighted Aggregation

When combining already-normalized stage scores, use weights that sum to 1.0:

```python
def aggregate_pipeline_scores(stage_scores: dict) -> float:
    """
    Combine stage scores with weights that sum to 1.0.

    IMPORTANT: Weights MUST sum to 1.0 to keep result in [0, 1].
    """
    weights = {
        "final_output": 0.40,    # Most important
        "creation": 0.25,        # Foundation
        "critic": 0.20,          # Quality gating
        "iteration": 0.15,       # Polish
    }
    # Verify: 0.40 + 0.25 + 0.20 + 0.15 = 1.0

    overall = sum(
        stage_scores[stage] * weight
        for stage, weight in weights.items()
    )

    return overall  # Guaranteed [0, 1]
```

**Key principle:** When aggregating already-normalized [0, 1] scores, weights must sum to 1.0.

---

## Complete Metric Example

Putting it all together:

```python
def create_pipeline_metric(example, pred, trace=None, pred_name=None):
    """
    Complete metric for a multi-agent pipeline.

    1. Pre-validates enum fields
    2. Runs dimensional LLM evaluation
    3. Aggregates across agents
    4. Routes feedback by pred_name
    """
    # 1. Pre-validation gating
    enum_errors = validate_all_enums(pred)
    if enum_errors:
        return dspy.Prediction(
            score=0.05,
            feedback=format_enum_errors(enum_errors)
        )

    # 2. Run evaluators for each agent
    evaluator = PipelineEvaluator()
    result = evaluator(pred=pred, gold=example)

    overall_score = result["overall_score"]

    # 3. Return score only if no pred_name
    if pred_name is None:
        return overall_score

    # 4. Route feedback based on pred_name
    if pred_name == "agent_a.predict":
        feedback = result["agent_a_feedback"]
    elif pred_name == "agent_b.predict":
        feedback = result["agent_b_feedback"]
    elif pred_name == "agent_c.predict":
        feedback = result["agent_c_feedback"]
    else:
        feedback = result["comprehensive_feedback"]

    return dspy.Prediction(
        score=overall_score,
        feedback=feedback
    )
```

---

## Related Documentation

- [Overview](overview.md) - Optimization concepts
- [Training Data](data.md) - Preparing training examples
- [GEPA Workflow](gepa-workflow.md) - Using GEPA optimizer
- [Custom Proposers](custom-proposers.md) - Domain-aware instruction generation
