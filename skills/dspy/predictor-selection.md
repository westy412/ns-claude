# Predictor Selection

Choose the right DSPy predictor for your task.

## Decision Table

| Task Type | Predictor | Why |
|-----------|-----------|-----|
| Data extraction | `Predict` | Direct mapping, no reasoning needed |
| Classification | `Predict` | Checklist evaluation |
| Evaluation/scoring | `Predict` | Criteria checking |
| Ranking | `Predict` | Comparison task |
| Creative synthesis | `ChainOfThought` | Benefits from visible reasoning |
| Complex decisions | `ChainOfThought` | Needs justification |
| Multi-source integration | `ChainOfThought` | Requires synthesis |
| Tool usage (dynamic) | `ReAct` | LLM decides which tools |

## Predict (Basic Agent)

Use for straightforward input → output mapping.

```python
# Good for: extraction, classification, evaluation
self.extractor = dspy.Predict(ExtractorSignature)
self.categorizer = dspy.Predict(CategorizerSignature)
self.critic = dspy.Predict(CriticSignature)  # Evaluation is a checklist
self.ranker = dspy.Predict(RankerSignature)
```

**Characteristics:**
- Fastest execution
- Lowest token usage
- No reasoning trace
- Best for well-defined tasks

## ChainOfThought (Reasoning Agent)

Use when visible reasoning improves quality or debugging.

```python
# Good for: creative tasks, complex synthesis
self.content_creator = dspy.ChainOfThought(CreatorSignature)
self.summarizer = dspy.ChainOfThought(SummarizerSignature)
```

**Characteristics:**
- Adds automatic `reasoning` field
- Higher latency (reasoning tokens)
- Higher cost
- Easier debugging (see the thinking)

## ReAct (Tool Agent)

Use when the agent needs external data or actions.

```python
# Good for: dynamic tool selection
self.researcher = dspy.ReAct(
    signature=ResearchSignature,
    tools=[search_web, query_database],
    max_iters=5
)
```

**Characteristics:**
- Multiple LLM calls (iterative)
- Highest latency
- Highest cost
- Needed when data isn't in the prompt

## Common Mistakes

### Using ChainOfThought for Everything

```python
# WRONG: ChainOfThought for extraction adds unnecessary overhead
self.extractor = dspy.ChainOfThought(ExtractorSignature)
self.categorizer = dspy.ChainOfThought(CategorizerSignature)

# CORRECT: Predict for extraction/classification
self.extractor = dspy.Predict(ExtractorSignature)
self.categorizer = dspy.Predict(CategorizerSignature)
```

### Using Predict for Creative Tasks

```python
# WRONG: Predict for creative synthesis loses reasoning value
self.content_creator = dspy.Predict(CreatorSignature)

# CORRECT: ChainOfThought captures creative reasoning
self.content_creator = dspy.ChainOfThought(CreatorSignature)
```

## Example: Mixed Pipeline

```python
class ContentPipeline(dspy.Module):
    def __init__(self, shared_lm):
        # EXTRACTION TASKS - Use Predict (faster, cheaper)
        self.data_extractor = dspy.Predict(DataExtractorSignature)
        self.categorizer = dspy.Predict(CategorizerSignature)
        self.ranker = dspy.Predict(RankerSignature)
        self.critic = dspy.Predict(CriticSignature)

        # CREATIVE TASKS - Use ChainOfThought (shows reasoning)
        self.content_creator = dspy.ChainOfThought(CreatorSignature)

        # Inject LM into all
        for predictor in [self.data_extractor, self.categorizer,
                          self.ranker, self.critic, self.content_creator]:
            predictor.set_lm(shared_lm)
```

## Performance Comparison

| Predictor | Relative Latency | Relative Cost | Reasoning Trace |
|-----------|-----------------|---------------|-----------------|
| Predict | 1x | 1x | No |
| ChainOfThought | 1.5-2x | 1.5-2x | Yes |
| ReAct (3 iterations) | 3-5x | 3-5x | Yes (trajectory) |

## Quick Reference

**When in doubt:**
- Is the output format well-defined? → **Predict**
- Does understanding "why" help? → **ChainOfThought**
- Do you need external data? → **ReAct** or explicit tool calls
