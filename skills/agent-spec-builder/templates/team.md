---
name: [team-name]
pattern: [pipeline | router | fan-in-fan-out | loop]
framework: [langgraph | dspy]
reference: agent-patterns/agent-teams/[framework]/[pattern].md
---

# [Team Name]

## Purpose

### What it does
Detailed description of what this team accomplishes.

### Why it exists
The problem it solves, the need it addresses.

### Success criteria
What does successful execution look like? Measurable outcomes.

## Framework Reasoning

**Pattern:** [Pipeline | Router | Fan-in-fan-out | Loop]
**Why:** [e.g., "Iterative refinement with creator-critic feedback cycle"]

**Framework:** [LangGraph | DSPy]
**Why:** [e.g., "Need fine-grained state control for iteration counting"]

## Inputs

What the team receives:
- **[Input name]**: Description, format, source

## Outputs

What the team produces:
- **[Output name]**: Description, format, who consumes it

## Flow Diagram

```
[ASCII art showing how agents connect]

Example for Loop pattern:
┌──────────┐     ┌──────────┐
│ Creator  │────▶│  Critic  │
└──────────┘     └────┬─────┘
      ▲               │
      │   feedback    │
      └───────────────┘
```

## Agents

| Agent | File | Description |
|-------|------|-------------|
| [name] | [name.md](./name.md) | One-line description |

## Utilities

Team-level integrations:
- **[Utility name]**: What it does, what it connects to

## Dependencies

### Python Packages

```txt
# Core framework (pick one based on framework choice)
# LangGraph:
langgraph>=0.x.x
langchain-anthropic>=0.x.x
# DSPy:
dspy>=2.x.x

# Tool dependencies (from agent specs)
package-name>=1.0.0  # For [tool-name] - [brief reason]
another-package>=2.0.0  # For [tool-name]
```

### Environment Variables

| Variable | Purpose | How to Obtain |
|----------|---------|---------------|
| `API_KEY_NAME` | Authentication for [service] | [URL or instructions] |
| `ANOTHER_VAR` | [purpose] | [instructions] |

### External Services

| Service | Required For | Setup |
|---------|--------------|-------|
| [Service name] | [which tool/agent] | [setup instructions or link] |

## Signatures

Each team/sub-team folder gets its own signatures file (e.g., `signatures.py` for DSPy).
Do NOT share signature files between sibling teams. Agent specs in this team reference
this team's signatures only — not a parent or shared location.

Even if multiple sibling teams start with identical signatures (e.g., template instances),
each gets its own copy for independent evolution and LLM maintainability.

## Notes

Any additional context, constraints, or considerations.

<!-- =============================================================================
TEMPLATE-TO-INSTANCES GUIDANCE
If this team.md describes a TEMPLATE (generic pattern used by multiple instances):
- Mark it clearly as "TEMPLATE — not instantiated directly"
- Each instance MUST have its own fully explicit team.md with:
  - All details inlined (not "see template" references)
  - Platform/config-specific values filled in
  - Its own agent-config.yaml with concrete values
  - Its own agent spec files (not shared with template or siblings)
- The impl-builder should be able to implement any instance by reading ONLY
  that instance's folder — no cross-referencing the template required.
============================================================================= -->
