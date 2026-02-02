# Message Agent

## What It Is

A single-turn LLM call that returns a message object (e.g., `AIMessage`) and maintains conversation history. Designed for conversational flows where the full message history is passed forward.

## When to Use

- Building conversational interfaces
- Multi-turn dialogue systems where history matters
- Chat applications with message threading
- Agents that need to reference previous exchanges
- When output will be added back to a conversation

## When to Avoid

- Output is standalone content (no conversation context) — use **Text Agent** instead
- Output must be programmatically parsed — use **Structured Output Agent** instead
- Agent needs to call external tools — use **Message + Tool Agent** instead
- Simple content generation — use **Text Agent** instead (simpler)

## Selection Criteria

- If building conversation flow with history → **Message Agent**
- If output is standalone text → consider **Text Agent**
- If output needs parsing/validation → consider **Structured Output Agent**
- If agent needs tools in conversation → consider **Message + Tool Agent**

## Inputs / Outputs

**Inputs:**
- Message history (list of `HumanMessage`, `AIMessage`, etc.)
- System prompt providing context/instructions

**Outputs:**
- `AIMessage` object (the LLM's response)
- Updated message list (via `operator.add` - automatic concatenation)

## Prompting Guidelines

- System message sets the agent's role and behavior
- Use `MessagesPlaceholder` to inject conversation history
- Keep system prompts focused on conversational behavior
- Consider including examples of desired response style
- For multi-turn, reference how to handle context from previous messages

---

## LangGraph Implementation

### Code Template

```python
from typing import Annotated
import operator
from typing_extensions import TypedDict

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END


# =============================================================================
# STATE DEFINITION
# =============================================================================
# Use Annotated[list, operator.add] for automatic message concatenation.
# When you return {"messages": [result]}, LangGraph automatically appends
# to the existing list - you don't need to do messages + [result].

class ConversationState(TypedDict):
    messages: Annotated[list, operator.add]  # Auto-concatenates on return


# =============================================================================
# LLM SETUP
# =============================================================================
llm = ChatOpenAI(model="gpt-4")


# =============================================================================
# AGENT NODE
# =============================================================================
# The agent receives conversation history and generates a response.
# MessagesPlaceholder injects the full message history into the prompt.

async def agent_node(state: ConversationState) -> dict:
    # Build prompt with message history placeholder
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder(variable_name="messages"),  # Injects history
    ])

    # Create chain and invoke
    chain = prompt | llm
    result = await chain.ainvoke({"messages": state["messages"]})

    # Return just the new message - operator.add handles concatenation
    # DO NOT return messages + [result], just return [result]
    return {"messages": [result]}


# =============================================================================
# GRAPH DEFINITION
# =============================================================================
# Simple linear graph: START -> agent -> END

def create_graph():
    graph = StateGraph(ConversationState)

    graph.add_node("agent", agent_node)

    graph.add_edge(START, "agent")
    graph.add_edge("agent", END)

    return graph.compile()
```

### LangGraph-Specific Notes

- **Async vs Sync:** All examples use `async def` with `await chain.ainvoke()`. For synchronous execution, use `def` with `chain.invoke()` instead.
- **MessagesPlaceholder:** Essential for injecting message history into prompts
- **operator.add:** The `Annotated[list, operator.add]` pattern means LangGraph automatically concatenates returned lists. Return `[result]` not `messages + [result]`.
- **Message types:** Use `HumanMessage`, `AIMessage`, `SystemMessage` from langchain_core.messages
- **State accumulation:** Messages list grows with each turn — consider truncation for long conversations

---

## Pitfalls & Best Practices

**Pitfalls:**

- **Wrong return pattern** — When using `operator.add`, return `{"messages": [result]}` NOT `{"messages": messages + [result]}`. The operator handles concatenation automatically.

- **Unbounded history** — Message lists grow indefinitely. Implement truncation, summarization, or sliding window to prevent context overflow.

- **Message type confusion** — Mixing `dict` format with `Message` objects causes errors. Be consistent with message representation.

- **Lost context** — If system prompt doesn't instruct referencing history, the model may ignore previous messages. Be explicit about using context.

**Best Practices:**

- **Return only new messages** — With `operator.add`, return just the new message(s) in a list.

- **Explicit history reference** — Tell the model in the system prompt to reference previous messages when relevant.

- **Role consistency** — Use the same message types throughout. If starting with `HumanMessage`/`AIMessage`, continue with those.

- **Context windowing** — For long conversations, keep last N messages or summarize older messages to stay within context limits.

---

## Comparison: Message Agent vs Text Agent

| Aspect | Text Agent | Message Agent |
|--------|------------|---------------|
| Output | Raw string | Message object |
| History | Not preserved | Maintained and passed |
| Use case | Standalone generation | Conversational flow |
| State update | `{"field": result.content}` | `{"messages": [result]}` |
| Complexity | Simpler | More state management |
