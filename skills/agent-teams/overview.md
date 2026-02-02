# Agent Teams - Structural Patterns

## Overview

Agent Teams are multi-agent workflows where individual agents are composed into larger systems. This documentation covers the 4 core structural patterns available in both **LangGraph** and **DSPy**.

Each pattern represents a different **topology** - the shape of how agents connect and pass work between each other.

---

## The 4 Core Patterns

| Pattern | Structure | Use Case |
|---------|-----------|----------|
| **Pipeline** | A → B → C | Sequential processing, each agent transforms/enriches state |
| **Router** | A → (B \| C \| D) | Dynamic dispatch based on runtime decisions |
| **Fan-in/Fan-out** | A → [B, C, D] → E | Parallel execution with result aggregation |
| **Loop** | A ↔ B | Iterative refinement with feedback cycles |

---

## Pattern Selection Guide

### Choose Pipeline when:
- Tasks are sequential and dependent
- Each agent needs output from the previous
- Order of execution matters
- Simple, predictable flow

### Choose Router when:
- Different paths based on input/state
- Early exit conditions possible
- Decision trees or branching logic
- Dynamic next-agent selection

### Choose Fan-in/Fan-out when:
- Tasks are independent and parallelizable
- Multiple perspectives needed simultaneously
- Performance optimization via concurrency
- Results need aggregation

### Choose Loop when:
- Iterative refinement needed
- Creator-critic feedback patterns
- Quality gates before completion
- Multiple approval conditions

---

## Visual Comparison

```
PIPELINE:
  START → Agent A → Agent B → Agent C → END

ROUTER:
  START → Decision Agent → Agent A → END
                        ↘ Agent B → END
                        ↘ Agent C → END

FAN-IN/FAN-OUT:
  START → Agent A ──┐
        → Agent B ──┼→ Merge → END
        → Agent C ──┘

LOOP:
  START → Creator → Critic → Creator (repeat) → END
              ↑_________|
```

---

## Pattern Files

### LangGraph
- [langgraph/pipeline.md](langgraph/pipeline.md)
- [langgraph/router.md](langgraph/router.md)
- [langgraph/fan-in-fan-out.md](langgraph/fan-in-fan-out.md)
- [langgraph/loop.md](langgraph/loop.md)

### DSPy
- [dspy/pipeline.md](dspy/pipeline.md)
- [dspy/router.md](dspy/router.md)
- [dspy/fan-in-fan-out.md](dspy/fan-in-fan-out.md)
- [dspy/loop.md](dspy/loop.md)

---

## Comparison with Individual Agents

| Aspect | Individual Agents | Agent Teams |
|--------|-------------------|-------------|
| Scope | Single LLM call + tools | Multiple agents coordinated |
| Focus | Input/Output types | Structural topology |
| State | Single agent's state | Shared state across agents |
| Complexity | Simple | Compositional |

Agent Teams are built FROM Individual Agents. Each node in a team pattern can be any of the individual agent types.
