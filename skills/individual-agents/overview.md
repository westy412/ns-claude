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
| DSPy | Partial (signatures documented, modules vary) | **⚠️ Unvalidated** - based on model knowledge, not real code |

> **Note on DSPy:** The DSPy examples in this documentation are theoretical and based on framework documentation. They have NOT been validated against real codebase implementations. When working with DSPy, verify patterns against actual codebases before production use.

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

> **⚠️ UNVALIDATED:** DSPy implementations are based on framework documentation and have NOT been validated against real codebases.

### Text Agent
**What:** Single prediction returning text output using DSPy signatures.

**Pattern:**
```python
class TextGenerationSignature(dspy.Signature):
    """Generate text output based on the input context."""
    context: str = dspy.InputField(desc="The context and requirements")
    output: str = dspy.OutputField(desc="The generated text response")

class TextAgent(dspy.Module):
    def __init__(self):
        self.generator = dspy.Predict(TextGenerationSignature)
```

**Documentation:** [dspy/text-agent.md](./dspy/text-agent.md)

---

### Message Agent
**What:** Conversational agent maintaining history as formatted text.

**Pattern:**
```python
class ConversationSignature(dspy.Signature):
    """Generate a conversational response based on chat history."""
    history: str = dspy.InputField(desc="The conversation history")
    current_message: str = dspy.InputField(desc="The latest user message")
    response: str = dspy.OutputField(desc="The assistant's response")
```

**Documentation:** [dspy/message-agent.md](./dspy/message-agent.md)

---

### Structured Output Agent
**What:** Agent returning typed/validated output using TypedPredictor.

**Pattern:**
```python
class RankingSignature(dspy.Signature):
    """Rank items by relevance."""
    context: str = dspy.InputField(desc="The context for ranking")
    rankings: List[dict] = dspy.OutputField(desc="List of ranked items")

class StructuredAgent(dspy.Module):
    def __init__(self):
        self.ranker = dspy.TypedPredictor(RankingSignature)
```

**Documentation:** [dspy/structured-output-agent.md](./dspy/structured-output-agent.md)

---

### Text + Tool Agent
**What:** ReAct agent using tools and returning text output.

**Pattern:**
```python
class ResearchSignature(dspy.Signature):
    """Research using tools and provide summary."""
    query: str = dspy.InputField(desc="The research query")
    summary: str = dspy.OutputField(desc="Summary of findings")

class TextToolAgent(dspy.Module):
    def __init__(self):
        tools = [search_database, get_current_data]
        self.agent = dspy.ReAct(ResearchSignature, tools=tools, max_iters=5)
```

**Documentation:** [dspy/text-tool-agent.md](./dspy/text-tool-agent.md)

---

### Message + Tool Agent
**What:** Conversational ReAct agent with tool access.

**Pattern:**
```python
class ConversationalAgentSignature(dspy.Signature):
    """Converse while using tools to complete tasks."""
    history: str = dspy.InputField(desc="The conversation history")
    current_message: str = dspy.InputField(desc="Current user message")
    response: str = dspy.OutputField(desc="Your response")

class MessageToolAgent(dspy.Module):
    def __init__(self):
        tools = [search_tool, submit_tool]
        self.agent = dspy.ReAct(ConversationalAgentSignature, tools=tools)
```

**Documentation:** [dspy/message-tool-agent.md](./dspy/message-tool-agent.md)

---

### Structured Output + Tool Agent
**What:** ReAct agent returning typed output after tool use.

**Pattern:**
```python
class StructuredAnalysisSignature(dspy.Signature):
    """Analyze using tools and return structured findings."""
    query: str = dspy.InputField(desc="The analysis query")
    analysis: AnalysisResult = dspy.OutputField(desc="Structured result")

class StructuredToolAgent(dspy.Module):
    def __init__(self):
        tools = [search, verify]
        self.researcher = dspy.ReAct(StructuredAnalysisSignature, tools=tools)
```

**Documentation:** [dspy/structured-output-tool-agent.md](./dspy/structured-output-tool-agent.md)

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
