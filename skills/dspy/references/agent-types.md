# Agent Types Reference

Links to detailed documentation for each DSPy agent type.

## Available Agent Types

| Type | Predictor | Use Case | Documentation |
|------|-----------|----------|---------------|
| Basic Agent | `dspy.Predict` | Extraction, classification, evaluation | [basic-agent.md](../../individual-agents/dspy/basic-agent.md) |
| Reasoning Agent | `dspy.ChainOfThought` | Creative synthesis, complex decisions | [reasoning-agent.md](../../individual-agents/dspy/reasoning-agent.md) |
| Conversational Agent | `dspy.History` | Multi-turn loops, dialogue | [conversational-agent.md](../../individual-agents/dspy/conversational-agent.md) |
| Tool Agent | `dspy.ReAct` | External data, actions | [tool-agent.md](../../individual-agents/dspy/tool-agent.md) |

## Quick Selection Guide

```
Is the task straightforward input → output?
├── YES → Basic Agent (Predict)
└── NO
    │
    ├── Does it need visible reasoning?
    │   └── YES → Reasoning Agent (ChainOfThought)
    │
    ├── Does it need conversation history?
    │   └── YES → Conversational Agent (dspy.History)
    │
    └── Does it need external tools/data?
        └── YES → Tool Agent (ReAct)
```

## When to Use Each

### Basic Agent (Predict)
- Data extraction from text
- Classification and categorization
- Simple transformations
- Evaluation checklists

### Reasoning Agent (ChainOfThought)
- Creative content generation
- Complex decisions requiring justification
- Multi-source synthesis
- Tasks where "why" matters for debugging

### Conversational Agent (dspy.History)
- Creator-Critic loops
- Feedback incorporation workflows
- Chatbots and dialogue systems
- Any pattern with accumulated context

### Tool Agent (ReAct)
- Fetching external data (APIs, databases)
- Performing actions (send email, create record)
- Dynamic tool selection
- Multi-step workflows with external dependencies

## Combining Types

Agents can be combined in teams:

```python
class ContentPipeline(dspy.Module):
    def __init__(self, shared_lm):
        # Basic agents for extraction
        self.extractor = dspy.Predict(ExtractorSignature)

        # Reasoning agent for creative work
        self.creator = dspy.ChainOfThought(CreatorSignature)

        # Basic agent for evaluation
        self.critic = dspy.Predict(CriticSignature)
```

## See Also

- [Team Patterns](team-patterns.md) - How to combine agents
- [Predictor Selection](../predictor-selection.md) - Choosing the right predictor
