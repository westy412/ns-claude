# Team Patterns Reference

Links to detailed documentation for DSPy team topologies.

## Available Patterns

| Pattern | Flow | Use Case | Documentation |
|---------|------|----------|---------------|
| Pipeline | A → B → C | Sequential processing | [pipeline.md](../../agent-teams/dspy/pipeline.md) |
| Loop | A ↔ B (iterate) | Refinement with feedback | [loop.md](../../agent-teams/dspy/loop.md) |
| Fan-in-Fan-out | A → [B, C, D] → E | Parallel processing | [fan-in-fan-out.md](../../agent-teams/dspy/fan-in-fan-out.md) |
| Router | R → A or B or C | Conditional routing | [router.md](../../agent-teams/dspy/router.md) |

## Quick Selection Guide

```
What is your workflow shape?

Sequential stages, each builds on previous?
└── Pipeline

Refinement with feedback until quality threshold?
└── Loop (Creator-Critic)

Multiple independent analyses combined?
└── Fan-in-Fan-out

Different paths based on input characteristics?
└── Router
```

## Pattern Overviews

### Pipeline
```
Input → Stage 1 → Stage 2 → Stage 3 → Output
         (Extract)  (Analyze)  (Rank)
```

- Each stage transforms and passes to next
- Formatters convert between stages
- Each stage can use different predictor type

### Loop (Creator-Critic)
```
        ┌───────────────────┐
        │                   │
Input → Creator → Critic → (complete?)
                    │          │
                    └── No ────┘
                         │
                        Yes → Output
```

- Creator generates, Critic evaluates
- Iteration continues until quality threshold
- Separate histories per agent role

### Fan-in-Fan-out
```
         ┌─→ Analysis A ─┐
Input ───┼─→ Analysis B ─┼──→ Synthesizer → Output
         └─→ Analysis C ─┘
```

- Parallel independent analyses
- Results combined by synthesizer
- Use `asyncio.gather()` for parallel execution

### Router
```
           ┌─→ Technical Handler
Input → Router ─┼─→ Business Handler
           └─→ Support Handler
```

- LLM classifies input
- Routes to specialized handler
- Each handler optimized for its domain

## Pattern Combinations

Patterns can be nested:

```
Pipeline Stage 1 → Fan-out → Pipeline Stage 2
                      │
                  [Loop A]
                  [Loop B]
                  [Loop C]
                      │
                   Combine
```

## Common Configurations

| Use Case | Pattern | Agents |
|----------|---------|--------|
| Data extraction pipeline | Pipeline | Predict → Predict → Predict |
| Content creation | Loop | ChainOfThought ↔ Predict |
| Multi-aspect analysis | Fan-in-Fan-out | [Predict, Predict, Predict] → ChainOfThought |
| Support ticket routing | Router | Predict (router) → Predict (handlers) |

## See Also

- [Agent Types](agent-types.md) - Individual agent patterns
- [History Patterns](../history-patterns.md) - For loops needing conversation context
- [Formatters](../formatters.md) - For pipeline stage transitions
