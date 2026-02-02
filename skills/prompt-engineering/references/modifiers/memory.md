# Memory Modifier

## Purpose

Configures how agents handle conversation history and state across turns. Memory determines whether agents operate in single-turn (stateless) or multi-turn (stateful) mode.

---

## Memory Types

| Type | Description | Use When |
|------|-------------|----------|
| **None (Stateless)** | Each invocation is independent | Discrete processing tasks |
| **Conversation History** | Message history passed each turn | Multi-turn dialogue |
| **Session State** | Structured state persisted across turns | Complex workflows |

---

## Stateless (No Memory)

### Characteristics
- Each agent call is independent
- No knowledge of previous invocations
- Input contains all needed context

### When to Use
- Single-Turn agents
- Processing pipelines
- Agents that receive all context in inputs

### Prompt Implications
- Everything needed must be in `<inputs>`
- No reference to "earlier in the conversation"

---

## Conversation History

### Characteristics
- Message history passed with each turn
- Agent sees full conversation context
- Can reference and build on previous exchanges

### Prompt Adjustments

In `<inputs>`, document the history:

```xml
<inputs>
**Conversation History**
- What it is: Previous messages in this conversation
- Information included: User and assistant messages with timestamps
- How to use it:
  - Maintain context across turns
  - Don't repeat questions already answered
  - Reference previous statements when relevant
  - Build on established understanding
</inputs>
```

In `<operational_logic>`, define how to use history:

```xml
<operational_logic>
**Using conversation history:**
- Before asking a question, check if it was already answered
- Reference previous context: "As we discussed earlier..."
- If user says "the same thing" or "like before", look up what they mean
- If context seems missing, check history before asking user to repeat
</operational_logic>
```

### Handling Long Histories

```xml
<important_notes>
- Focus on recent messages (last 5-10 turns) for immediate context
- For earlier context, summarize rather than quote
- If history is very long, key decisions and facts are in the first few messages
</important_notes>
```

---

## Agent-to-Agent vs User-to-Agent

Memory behaves differently based on who the agent talks to:

### User-Facing Conversations

```xml
<operational_logic>
**Conversation style:**
- Use natural language
- Allow for follow-up questions
- Handle "yes", "no", "that one" with context
- Acknowledge when you remember something
</operational_logic>
```

### Agent-to-Agent Communication

```xml
<operational_logic>
**Inter-agent communication:**
- Be concise and specific
- Don't use conversational filler
- Reference previous outputs by name/ID, not vague references
- Assume the receiving agent has no context beyond what you provide
</operational_logic>
```

---

## Session State

For complex workflows, structured state may be more appropriate than raw history.

### In `<inputs>`:

```xml
<inputs>
**Session State**
- What it is: Structured data about the current session
- Information included:
  - current_step: Where we are in the workflow
  - collected_info: Information gathered so far
  - decisions_made: Choices already determined
  - pending_actions: What still needs to happen
- How to use it: Continue from current state, don't restart
</inputs>
```

### State-Aware Operational Logic:

```xml
<operational_logic>
**State-based flow:**
IF current_step == "gathering_info" AND collected_info is incomplete
  → Ask for missing information
IF current_step == "confirmation"
  → Summarize and ask for confirmation
IF current_step == "execution"
  → Perform actions and report results

**Never:**
- Re-ask for information in collected_info
- Re-explain what's in decisions_made
</operational_logic>
```

---

## Framework Implementation

### LangGraph with Message History

```python
from langgraph.checkpoint.memory import MemorySaver

# Add checkpointer for memory
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# Invoke with thread_id for persistence
config = {"configurable": {"thread_id": "user-123"}}
result = await graph.ainvoke(input_state, config)
```

### DSPy with History

```python
class ConversationalAgent(dspy.Module):
    def forward(self, message: str, history: list[dict]):
        # History passed explicitly as input
        context = self.format_history(history)
        return self.predictor(context=context, message=message)
```

---

## Memory Length Considerations

| History Length | Consideration |
|----------------|---------------|
| 1-5 turns | Pass full history |
| 5-20 turns | Consider summarizing older turns |
| 20+ turns | Summarize + keep recent turns verbatim |

### Summarization Prompt Pattern

```xml
<operational_logic>
When history exceeds 10 turns:
1. The first 3 messages contain initial context
2. A summary of turns 4 through (N-5) is provided
3. The last 5 turns are verbatim

Use the summary for background context, recent turns for immediate context.
</operational_logic>
```

---

## Common Pitfalls

1. **Ignoring history** — If history is provided, use it. Don't re-ask answered questions.

2. **Over-relying on history** — For long conversations, summarize; don't expect perfect recall.

3. **Inconsistent state** — If using session state, ensure it's updated atomically.

4. **Mixing paradigms** — Choose either message history OR session state, not both confusingly.

5. **Agent-to-agent with user patterns** — Inter-agent communication should be concise, not conversational.

6. **No history pruning** — Very long histories degrade performance. Implement summarization.

---

## Decision Guide

```
Is this a single, discrete task?
├── Yes → No memory needed
└── No (multi-turn)
    └── Is it user-facing conversation?
        ├── Yes → Conversation history
        │   └── Is the workflow complex with many steps?
        │       ├── Yes → Consider session state
        │       └── No → Message history is sufficient
        └── No (agent-to-agent)
            └── Pass required context explicitly, stateless preferred
```
