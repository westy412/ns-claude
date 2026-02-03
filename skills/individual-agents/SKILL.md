---
name: individual-agents
description: Select implementation types for agents in a team. Given a team pattern with defined slots, determines which of the 6 agent types (LLM, Tool, Human-in-Loop, Subgraph, Router, Retriever) to use for each slot. Use after agent-teams skill to implement individual agents.
allowed-tools: Read, Glob, Grep, Task
---

# Individual Agents Skill

## Purpose

Selects implementation types for all agents in an agent team. Given a team pattern with defined slots, this skill determines which of the 6 agent types to use for each slot.

---

## When to Use This Skill

Use this skill **after the agent-teams skill** — once you have:
- Selected team pattern (Pipeline, Router, Fan-in-fan-out, or Loop)
- Identified all agent slots/roles in that pattern
- Selected team framework (LangGraph or DSPy)

**Invocation:** This skill is invoked **once per team** to select types for all agents simultaneously.

---

## Input to This Skill

From the agent-teams skill:
1. **Team pattern** — Pipeline, Router, Fan-in-fan-out, or Loop
2. **Agent slots** — List of roles (e.g., creator, critic for Loop pattern)
3. **Team framework** — LangGraph or DSPy

---

## Framework Selection Rules

| Team Framework | Individual Agent Framework Options |
|----------------|-----------------------------------|
| DSPy | DSPy only |
| LangGraph | LangGraph **or** DSPy (per agent) |

- **DSPy team** → All agents must be DSPy
- **LangGraph team** → Each agent can independently use LangGraph or DSPy

---

## The 6 Agent Types (2x3 Matrix)

|                        | No Tools | With Tools |
|------------------------|----------|------------|
| **Text Output**        | Text Agent | Text + Tool Agent |
| **Message Output**     | Message Agent | Message + Tool Agent |
| **Structured Output**  | Structured Output Agent | Structured Output + Tool Agent |

---

## Selection Process

For **each slot** in the team, answer these questions:

### Question 1: What is the output format?

| Format | Choose When |
|--------|-------------|
| **Text** | Human-readable output, flexible format (drafts, summaries, explanations) |
| **Message** | Part of conversation, history matters (chat, dialogue agents) |
| **Structured** | Code will parse output, schema required (routing decisions, data extraction) |

### Question 2: Does this agent need tools?

**Add tools** when:
- Search or retrieve external information
- Call APIs or external services
- Interact with databases
- Perform calculations or execute code

**No tools** when:
- Pure reasoning/generation
- Transform input to output
- No external dependencies

### Question 3: What framework for this agent? (LangGraph team only)

When team uses LangGraph, choose per-agent:
- **LangGraph** — Default, native integration
- **DSPy** — When optimization/compilation benefits outweigh integration simplicity

---

## Decision Tree (Per Slot)

```
For each slot:
  │
  ├─ Output machine-parseable (JSON, typed schema)?
  │   ├─ YES → Structured Output
  │   │   └─ Needs tools? → Structured Output + Tool Agent
  │   │   └─ No tools? → Structured Output Agent
  │   │
  │   └─ NO → For conversation/chat?
  │       ├─ YES → Message
  │       │   └─ Needs tools? → Message + Tool Agent
  │       │   └─ No tools? → Message Agent
  │       │
  │       └─ NO → Text
  │           └─ Needs tools? → Text + Tool Agent
  │           └─ No tools? → Text Agent
```

---

## Slot-to-Agent Mapping Guide

Common mappings from team pattern slots:

| Slot Role | Typical Type | Reasoning |
|-----------|-------------|-----------|
| Router/Decision | Structured Output | Returns routing decision as enum/model |
| Critic/Reviewer | Structured Output | Returns analysis + score + feedback |
| Creator/Writer | Text or Message | Creative output; Message if history needed |
| Researcher | Text + Tools | Searches and returns findings |
| Transformer | Text | Simple input → output transform |
| Merger/Aggregator | Structured Output | Combines results into defined model |
| Assistant | Message + Tools | Conversational with tool access |

---

## Example: Loop Pattern Selection

**Input:**
- Pattern: Loop (iterative refinement)
- Slots: `creator`, `critic`
- Team Framework: LangGraph

**Selection:**

| Slot | Output Format | Tools? | Framework | Selected Type |
|------|---------------|--------|-----------|---------------|
| creator | Text | No | LangGraph | Text Agent |
| critic | Structured | No | LangGraph | Structured Output Agent |

---

## Example: Fan-in-fan-out Pattern Selection

**Input:**
- Pattern: Fan-in-fan-out (parallel research)
- Slots: `researcher_a`, `researcher_b`, `researcher_c`, `merger`
- Team Framework: LangGraph

**Selection:**

| Slot | Output Format | Tools? | Framework | Selected Type |
|------|---------------|--------|-----------|---------------|
| researcher_a | Text | Yes | LangGraph | Text + Tool Agent |
| researcher_b | Text | Yes | LangGraph | Text + Tool Agent |
| researcher_c | Text | Yes | DSPy | Text + Tool Agent |
| merger | Structured | No | LangGraph | Structured Output Agent |

*(Note: researcher_c uses DSPy for optimization benefits)*

---

## Output of This Skill

A markdown document mapping all slots to their types:

```markdown
## Agent Roster

### creator
- **Type:** Text Agent
- **Framework:** LangGraph
- **Tools:** None
- **Reference:** `langgraph/text-agent.md`

### critic
- **Type:** Structured Output Agent
- **Framework:** LangGraph
- **Tools:** None
- **Schema:** `CriticFeedback` (score, passed, feedback, suggestions)
- **Reference:** `langgraph/structured-output-agent.md`
```

This feeds into the prompt-engineering skill.

---

## Framework Support

### LangGraph Agent Types (2x3 Matrix)

| Agent Type | Reference |
|------------|-----------|
| Text Agent | `langgraph/text-agent.md` |
| Message Agent | `langgraph/message-agent.md` |
| Structured Output Agent | `langgraph/structured-output-agent.md` |
| Text + Tool Agent | `langgraph/text-tool-agent.md` |
| Message + Tool Agent | `langgraph/message-tool-agent.md` |
| Structured Output + Tool Agent | `langgraph/structured-output-tool-agent.md` |

### DSPy Agent Types

DSPy uses a different taxonomy based on module behavior rather than output format:

| Agent Type | Reference | Use When |
|------------|-----------|----------|
| Basic Agent | `dspy/basic-agent.md` | Simple input→output, no reasoning trace needed |
| Reasoning Agent | `dspy/reasoning-agent.md` | Needs chain-of-thought or multi-step reasoning |
| Conversational Agent | `dspy/conversational-agent.md` | Multi-turn dialogue, conversation history |
| Tool Agent | `dspy/tool-agent.md` | Needs to call external tools (ReAct pattern) |
| Text Agent | `dspy/text-agent.md` | Long-form text generation |

---

## Example: DSPy Pipeline Selection

**Input:**
- Pattern: Pipeline (multi-hop QA)
- Slots: `retriever`, `reasoner`
- Team Framework: DSPy

**Selection:**

| Slot | Agent Type | Framework | Reference |
|------|-----------|-----------|-----------|
| retriever | Tool Agent | DSPy | `dspy/tool-agent.md` |
| reasoner | Reasoning Agent | DSPy | `dspy/reasoning-agent.md` |

---

## Workflow Summary

1. **Receive team definition** — Pattern + slots from agent-teams skill
2. **Check framework rules** — DSPy team = DSPy agents only; LangGraph team = flexible
3. **For each slot:**
   - Determine output format (Text/Message/Structured)
   - Assess tool needs
   - Select framework (if LangGraph team)
   - Select agent type
4. **Compile agent roster** — Markdown document with all agents
5. **Hand off to prompt-engineering** — Write prompts for all agents

---

## References

- `overview.md` — Full taxonomy, detailed comparisons, code examples
- `langgraph/*.md` — LangGraph agent implementations
- `dspy/*.md` — DSPy agent implementations
