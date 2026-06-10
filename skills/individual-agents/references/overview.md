# Individual Agent Types Overview

This document describes the 6-type taxonomy for individual agents based on **Output Format** and **Tool Usage**.

---

## The 6-Type Taxonomy

Individual agents are classified along two dimensions:

1. **Output Format:** What the agent returns
   - **Text:** Raw string/text (e.g., `result.content`)
   - **Message:** Message object for conversation (e.g., `AIMessage`)
   - **Structured Output:** Typed/schema-validated output (e.g., Pydantic model)

2. **Tool Usage:** Whether the agent uses tools
   - **No Tools:** Single LLM call, no external actions
   - **With Tools:** Can invoke tools, handle tool responses

### Classification Matrix

|                    | No Tools | With Tools |
|--------------------|----------|------------|
| **Text Output**    | Text Agent | Text + Tool Agent |
| **Message Output** | Message Agent | Message + Tool Agent |
| **Structured Output** | Structured Output Agent | Structured Output + Tool Agent |

---

## Quick Selection Guide

```
Is output machine-parseable (JSON, typed)?
├─ YES → Structured Output variant
│   └─ Needs tools? → Structured Output + Tool Agent
│   └─ No tools? → Structured Output Agent
│
├─ NO → Is this for conversation/chat?
│   ├─ YES → Message variant
│   │   └─ Needs tools? → Message + Tool Agent
│   │   └─ No tools? → Message Agent
│   │
│   └─ NO → Text variant
│       └─ Needs tools? → Text + Tool Agent
│       └─ No tools? → Text Agent
```

---

## Framework Coverage

| Framework | Coverage | Validation Status |
|-----------|----------|-------------------|
| LangGraph | Full (all 6 types documented) | **Validated** - grounded in analyzed codebase examples |
| DSPy | Full (4 types + alias documented) | **Validated** - grounded in ns-cold-outreach-workforce codebase |

> **Note on DSPy:** DSPy uses a different, simpler taxonomy than LangGraph. In DSPy, all outputs are defined via Signatures with typed fields, so the LangGraph distinction between Text/Message/Structured doesn't apply. See the DSPy Patterns section below.

---

## LangGraph Patterns

LangGraph implementations are fully validated against real codebase examples.

### Text Agent
**What:** Single LLM call returning raw text.

**Use when:** Drafting content, summaries, or any output intended for human reading where format is flexible.

**Pattern:**
```python
chain = prompt | self.llm
result = await chain.ainvoke({"input": data})
return {"output": result.content}
```

**Documentation:** [langgraph/text-agent.md](./langgraph/text-agent.md)

---

### Message Agent
**What:** Single LLM call returning a message object for conversation flow.

**Use when:** Building conversational agents where message history matters and output goes back into a conversation.

**Pattern:**
```python
chain = prompt | self.llm
result = await chain.ainvoke({"messages": messages})
return {"messages": messages + [result]}
```

**Documentation:** [langgraph/message-agent.md](./langgraph/message-agent.md)

---

### Structured Output Agent
**What:** Single LLM call returning typed/schema-validated output.

**Use when:** Output must be programmatically parsed or used as structured data by downstream code.

**Pattern:**
```python
chain = prompt | self.llm.with_structured_output(Schema)
result = await chain.ainvoke({"input": data})
return {"output": result.model_dump()}
```

**Documentation:** [langgraph/structured-output-agent.md](./langgraph/structured-output-agent.md)

---

### Text + Tool Agent
**What:** LLM with tools that returns text output after tool use.

**Use when:** Agent needs to take actions (search, API calls) but final output is human-readable text.

**Pattern:**
```python
tool_llm = self.llm.bind_tools([tool1, tool2])
# ... handle tool calls ...
# Final response is text
return {"output": final_response.content}
```

**Documentation:** [langgraph/text-tool-agent.md](./langgraph/text-tool-agent.md)

---

### Message + Tool Agent
**What:** LLM with tools that returns messages, maintaining conversation history.

**Use when:** Building conversational tool-using agents where the full message history (including tool calls/responses) is preserved.

**Pattern:**
```python
tool_llm = self.llm.bind_tools([tool1, tool2])
prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    MessagesPlaceholder("messages"),
])
chain = prompt | tool_llm
result = await chain.ainvoke({"messages": messages})
return {"messages": messages + [result]}
```

**Documentation:** [langgraph/message-tool-agent.md](./langgraph/message-tool-agent.md)

---

### Structured Output + Tool Agent
**What:** LLM with tools that returns typed/schema-validated output after tool use.

**Use when:** Agent needs to take actions AND return structured data for downstream processing.

**Pattern:**
```python
tool_llm = self.llm.bind_tools([tool1, tool2])
# ... handle tool calls ...
# Final response uses structured output
chain = prompt | self.llm.with_structured_output(Schema)
result = await chain.ainvoke({"input": data})
return {"output": result.model_dump()}
```

**Documentation:** [langgraph/structured-output-tool-agent.md](./langgraph/structured-output-tool-agent.md)

---

## DSPy Patterns

DSPy uses a simpler, DSPy-native taxonomy based on **module behavior** rather than output format. In DSPy, all outputs are defined via Signatures with typed fields, so the LangGraph distinction between Text/Message/Structured doesn't apply.

### Basic Agent
**What:** Single-turn prediction using `dspy.Predict(Signature)`. The core DSPy building block.

**Use when:** Extraction, classification, ranking, evaluation - any task with clear input/output mapping.

**Pattern:**
```python
class ExtractorSignature(dspy.Signature):
    """Extract company intelligence from website content."""
    company_name: str = dspy.InputField()
    website_content: str = dspy.InputField()

    overview: str = dspy.OutputField(description="2-3 sentence overview")
    industry: Literal["B2B SaaS", "Healthcare", "Other"] = dspy.OutputField()

class ExtractorAgent(dspy.Module):
    def __init__(self, shared_lm):
        self.predictor = dspy.Predict(ExtractorSignature)
        self.predictor.set_lm(shared_lm)
```

**Documentation:** [dspy/basic-agent.md](./dspy/basic-agent.md)

---

### Reasoning Agent
**What:** Uses `dspy.ChainOfThought(Signature)` to show reasoning before producing output.

**Use when:** Creative synthesis, complex decisions, multi-input reasoning where visible thinking improves quality.

**Pattern:**
```python
class CreatorSignature(dspy.Signature):
    """Create personalized outreach messages."""
    requirements: str = dspy.InputField()
    context: str = dspy.InputField()

    response: str = dspy.OutputField(description="Reasoning and approach")
    draft: str = dspy.OutputField(description="The created content")

class CreatorAgent(dspy.Module):
    def __init__(self, shared_lm):
        self.creator = dspy.ChainOfThought(CreatorSignature)
        self.creator.set_lm(shared_lm)
```

**Documentation:** [dspy/reasoning-agent.md](./dspy/reasoning-agent.md)

---

### Conversational Agent
**What:** Multi-turn agent using `dspy.History` for conversation context tracking.

**Use when:** Iterative loops, critic-iterator patterns, any workflow where agents build on previous exchanges.

**Pattern:**
```python
critic_history = dspy.History(messages=[])

result = await self.critic.acall(
    content=content,
    history=critic_history
)

critic_history.messages.append({
    "role": "assistant",
    "content": result.feedback
})
```

**Documentation:** [dspy/conversational-agent.md](./dspy/conversational-agent.md)

---

### Tool Agent
**What:** Agent that calls external tools using `dspy.ReAct` or manual tool orchestration.

**Use when:** Searching, API calls, database queries, or any external action.

**Pattern:**
```python
class ResearchSignature(dspy.Signature):
    """Research a topic using available tools."""
    query: str = dspy.InputField()
    summary: str = dspy.OutputField()

class ResearchAgent(dspy.Module):
    def __init__(self, shared_lm):
        tools = [search_tool, fetch_tool]
        self.agent = dspy.ReAct(ResearchSignature, tools=tools, max_iters=5)
        self.agent.set_lm(shared_lm)
```

**Documentation:** [dspy/tool-agent.md](./dspy/tool-agent.md)

---

### Text Agent (Alias)
**What:** Alias for Basic Agent. In DSPy, there is no distinction between "text" and "structured" output - all outputs use Signatures.

**Documentation:** [dspy/text-agent.md](./dspy/text-agent.md) (redirects to basic-agent)

---

## Choosing Between Types

### Text vs Message vs Structured Output

| Question | Text | Message | Structured |
|----------|------|---------|------------|
| Output for human reading? | Yes | Sometimes | Rarely |
| Output parsed by code? | No | Sometimes | Yes |
| Conversation history matters? | No | Yes | No |
| Format must be exact? | No | No | Yes |
| Validation needed? | No | No | Yes |

### When to Add Tools

Add tools when the agent needs to:
- Search or retrieve external information
- Call APIs or external services
- Interact with databases
- Perform calculations
- Execute code
- Take real-world actions

---

## Common Patterns Across Types

### Input Formatting
All types benefit from consistent input formatting:
```python
prompt_input = format_input(state).replace("{", "{{").replace("}", "}}")
```

### Error Handling
Structured Output agents should implement retry logic:
```python
attempts = 0
while attempts < 3:
    try:
        result = await chain.ainvoke(...)
        return result
    except Exception:
        attempts += 1
        # Inject schema hint for retry
```

### State Management
All agents in LangGraph update state via returned dict:
```python
return {"state_key": result}
```
