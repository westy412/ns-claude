---
name: agent-teams
description: Select structural patterns for multi-agent workflows. Choose from Pipeline, Router, Fan-in-fan-out, or Loop topologies. Use when building multi-agent systems, coordinating work across agents, or choosing agent communication patterns.
allowed-tools: Read, Glob, Grep, Task
---

# Agent Teams Skill

## Purpose

Provides structural patterns for composing individual agents into coordinated multi-agent workflows. Each pattern represents a different **topology** — the shape of how agents connect and pass work between each other.

---

## When to Use This Skill

Use this skill when:
- Building a multi-agent system (more than one agent working together)
- Coordinating work across multiple specialized agents
- Choosing how agents should communicate and sequence their work

**Skip this skill when:**
- Building a single agent (use `individual-agents` skill instead)
- Only one LLM call is needed

---

## Prerequisites

Before selecting an agent team pattern:

1. **Framework selection** — Ask user preference: LangGraph or DSPy
2. **Problem understanding** — Understand the business problem and requirements

---

## The 4 Core Patterns

| Pattern | Structure | Key Signal |
|---------|-----------|------------|
| **Pipeline** | A → B → C | Sequential processing, each step depends on previous |
| **Router** | A → (B \| C \| D) | Dynamic dispatch based on input, branching logic |
| **Fan-in/Fan-out** | A → [B, C, D] → E | Parallel independent work, then aggregation |
| **Loop** | A ↔ B | Iterative refinement with feedback cycles |

---

## Selection Decision Tree

```
START
  │
  ├─ Need to route to different specialists based on input?
  │   └─ YES → ROUTER
  │
  ├─ Need parallel processing of independent work?
  │   └─ YES → FAN-IN-FAN-OUT
  │
  ├─ Need iterative refinement with feedback?
  │   └─ YES → LOOP
  │
  └─ Sequential stages, each builds on previous?
      └─ YES → PIPELINE
```

---

## Pattern Selection Guide

### Choose Pipeline when:
- Tasks are sequential and dependent
- Each agent needs output from the previous
- Order of execution matters
- Simple, predictable flow
- **Examples:** Document processing (extract → analyze → summarize), research chains

### Choose Router when:
- Different paths based on input/state
- Early exit conditions possible
- Decision trees or branching logic
- Dynamic next-agent selection
- **Examples:** Support ticket routing, content categorization, intent classification

### Choose Fan-in/Fan-out when:
- Tasks are independent and parallelizable
- Multiple perspectives needed simultaneously
- Performance optimization via concurrency
- Results need aggregation
- **Examples:** Multi-source research, parallel analysis, voting systems

### Choose Loop when:
- Iterative refinement needed
- Creator-critic feedback patterns
- Quality gates before completion
- Multiple approval conditions
- **Examples:** Content generation with review, code generation with tests, iterative search

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

## Nesting: Composing Teams of Teams

Teams can be nested to any depth. Each level has its own pattern, team.md, and agent-config.yaml.

### 2-Level Nesting (Common)

A parent team orchestrates child teams:
```
research-pipeline/ (pipeline)
├── team.md, agent-config.yaml
├── content-refinement/ (loop)
│   ├── team.md, agent-config.yaml
│   └── agents/
└── parallel-research/ (fan-in-fan-out)
    ├── team.md, agent-config.yaml
    └── agents/
```

### 3-Level Nesting (Complex Systems)

A root team orchestrates phase teams, which orchestrate sub-teams:
```
root-pipeline/ (pipeline)                     ← Level 1: Root
├── team.md, agent-config.yaml
├── research-team/ (fan-in-fan-out)           ← Level 2: Phase team
│   ├── team.md, agent-config.yaml
│   ├── agents/                               ← Direct agents at level 2
│   │   ├── platform-synthesizer.md
│   │   └── signal-blender.md
│   ├── keyword-loop/ (loop)                  ← Level 3: Sub-team
│   │   ├── team.md, agent-config.yaml
│   │   └── agents/
│   └── analytics-team/ (fan-in-fan-out)      ← Level 3: Sub-team
│       ├── team.md, agent-config.yaml
│       └── agents/
└── ideation-team/ (pipeline)                 ← Level 2: Phase team
    ├── team.md, agent-config.yaml
    └── agents/
```

### Nesting Rules

1. **Each level has its own pattern** — A pipeline parent can have loop and fan-in-fan-out children. Patterns are independent at each level.
2. **Each team folder has its own agent-config.yaml** — Parent config includes `sub-teams` key listing child folders. Child configs are self-contained.
3. **Parent team.md documents orchestration** — How it invokes children, what data flows between them, the import/composition chain.
4. **Mixed patterns are normal** — A fan-in-fan-out parent can orchestrate loop children AND fan-in-fan-out children. Each child uses its own pattern internally.
5. **A team can have BOTH sub-teams AND direct agents** — Agents at a level are distinct from agents inside sub-teams (e.g., synthesizer agents at level 2 that aggregate sub-team outputs).

### Parent team.md Orchestration Documentation

When generating team.md for a parent with sub-teams, include:
- **How it invokes children** — parallel (asyncio.gather) or sequential
- **Each child's pattern** — annotated in the Sub-Teams table
- **The import/composition chain** — how parent.forward() calls child.forward()
- **Data flow between levels** — what the parent passes down and what it receives back

---

## Workflow

1. **Ask framework preference** — LangGraph or DSPy
2. **Identify the dominant flow** — Use decision tree above
3. **Select pattern** — Reference the appropriate pattern file
4. **Identify agent slots** — Each pattern has natural roles (see pattern docs)
5. **Hand off to individual-agents skill** — Select agent types for each slot
6. **Hand off to prompt-engineering skill** — Write prompts for each agent

---

## Framework Support

| Pattern | LangGraph | DSPy |
|---------|-----------|------|
| Pipeline | `langgraph/pipeline.md` | `dspy/pipeline.md` |
| Router | `langgraph/router.md` | `dspy/router.md` |
| Fan-in/Fan-out | `langgraph/fan-in-fan-out.md` | `dspy/fan-in-fan-out.md` |
| Loop | `langgraph/loop.md` | `dspy/loop.md` |

---

## Framework Comparison

| Aspect | LangGraph | DSPy |
|--------|-----------|------|
| **Paradigm** | Graph-based state machine | Signature-based modules |
| **State** | TypedDict shared state | Inputs/outputs via signatures |
| **Routing** | Conditional edges, Command | Python conditionals |
| **Optimization** | Manual prompt tuning | GEPA/MIPROv2 automatic optimization |
| **Best for** | Complex routing, human-in-loop | Structured output, optimization workflows |

**Choose LangGraph when:**
- Need complex conditional routing
- Human approval steps required
- State persistence across sessions

**Choose DSPy when:**
- Structured input/output is critical
- Want automatic prompt optimization
- Multi-agent pipelines with clear signatures

---

## What Each Pattern Doc Contains

Each pattern reference file includes:
- Complete code implementation
- State management approach
- Run methods and invocation
- Variations and when to use each
- Common pitfalls

**DSPy-specific additions:**
- Singleton LM pattern for concurrency
- Formatter utilities between stages
- Async execution patterns

---

## Output of This Skill

After selecting a pattern, you should have:
1. **Selected pattern** — One of the 4 core patterns
2. **Selected framework** — LangGraph or DSPy
3. **Agent slots identified** — The roles needed (e.g., creator/critic for Loop)

These feed into the next skills in the chain.

---

## References

### Overview
- `overview.md` — Pattern overview and comparison

### LangGraph Patterns
- `langgraph/pipeline.md` — Linear chain pattern
- `langgraph/router.md` — Dynamic dispatch pattern
- `langgraph/fan-in-fan-out.md` — Parallel execution pattern
- `langgraph/loop.md` — Iterative refinement pattern

### DSPy Patterns
- `dspy/pipeline.md` — Sequential module composition
- `dspy/router.md` — Conditional dispatch pattern
- `dspy/fan-in-fan-out.md` — Parallel execution with asyncio.gather
- `dspy/loop.md` — Iterative refinement with dspy.History

### DSPy Optimization (Advanced)
- `../agent-implementation-builder/frameworks/dspy/optimization/overview.md` — Optimization concepts
- `../agent-implementation-builder/frameworks/dspy/optimization/gepa-workflow.md` — GEPA optimization workflow
