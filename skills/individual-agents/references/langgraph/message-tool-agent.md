# Message + Tool Agent

## What It Is

An LLM agent with access to tools that maintains conversation history as messages. Combines tool capabilities with full conversational context.

## When to Use

- Building conversational assistants that can take actions
- Multi-turn interactions where tool results should be part of history
- Chat interfaces with function calling capabilities
- When tool calls and responses need to be visible in conversation
- Agents that iterate on tool results through dialogue

## When to Avoid

- Output is standalone text (no conversation context) — use **Text + Tool Agent** instead
- Output must be structured data — use **Structured Output + Tool Agent** instead
- No tools needed — use **Message Agent** instead (simpler)
- Simple one-shot tool use — use **Text + Tool Agent** instead (simpler)

## Selection Criteria

- If agent needs tools AND conversation history matters → **Message + Tool Agent**
- If agent needs tools AND output is standalone text → consider **Text + Tool Agent**
- If agent needs tools AND output must be structured → consider **Structured Output + Tool Agent**
- If no tools needed but conversation matters → consider **Message Agent**

## Inputs / Outputs

**Inputs:**
- Message history (list of `HumanMessage`, `AIMessage`, `ToolMessage`, etc.)
- Tool definitions (functions the agent can call)
- System prompt providing context/instructions

**Outputs:**
- `AIMessage` object (may contain tool calls or final response)
- Updated message list (history + new messages + tool results)

## Prompting Guidelines

- Use `MessagesPlaceholder` to inject conversation history into prompts
- Clearly define available tools and their purposes in the system prompt
- Specify completion conditions (when to stop calling tools)
- Handle tool validation — tell the agent which tools are available

---

## LangGraph Implementation

### Code Template

```python
from typing import Annotated
import operator
from typing_extensions import TypedDict

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode


# =============================================================================
# TOOL DEFINITIONS
# =============================================================================
# Define tools with @tool decorator. Docstrings help the LLM understand
# when to use each tool.

@tool
async def search_info(query: str) -> str:
    """Search for relevant information."""
    return f"Found information about: {query}"

@tool
async def submit_response(response: str) -> str:
    """Submit the final response."""
    return f"Response submitted: {response}"

tools = [search_info, submit_response]


# =============================================================================
# TOOL NODE
# =============================================================================
# ToolNode handles tool execution automatically.

tool_node = ToolNode(tools)


# =============================================================================
# LLM SETUP
# =============================================================================
llm = ChatOpenAI(model="gpt-4")


# =============================================================================
# STATE DEFINITION
# =============================================================================
# Messages use operator.add for automatic concatenation.
# Track attempts for retry logic and completed for termination.

class ConversationState(TypedDict):
    messages: Annotated[list, operator.add]  # Full conversation history
    completed: bool                           # Whether agent is done
    attempts: int                             # Track retry attempts


MAX_ATTEMPTS = 6  # Maximum iterations before forced termination


# =============================================================================
# AGENT NODE
# =============================================================================
# The agent sees full message history including tool results.
# Returns just the new message - operator.add handles concatenation.
# Wrapped in try/except - on failure, increment attempts and continue.

async def agent_node(state: ConversationState) -> dict:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Use tools when needed."),
        MessagesPlaceholder(variable_name="messages"),
    ])

    # Bind tools to LLM
    chain = prompt | llm.bind_tools(tools)

    attempts = state.get("attempts", 0)

    try:
        result = await chain.ainvoke({"messages": state["messages"]})

        # Check if agent wants to call tools
        if result.tool_calls:
            # Tool calls don't increment attempts - let it loop through tools
            return {
                "messages": [result],
                "completed": False,
            }

        # No tool calls - agent is done
        return {
            "messages": [result],
            "attempts": attempts + 1,
            "completed": True,
        }

    except Exception as e:
        # On failure, increment attempts and retry
        # Router will check attempts and end if over limit
        return {
            "messages": [AIMessage(content=f"Error occurred: {e}")],
            "attempts": attempts + 1,
            "completed": False,
        }


# =============================================================================
# ROUTER
# =============================================================================
# Determines next step based on state.
# Order matters: completed → attempts → tool_calls → retry

def agent_router(state: ConversationState) -> str:
    # 1. If completed, continue to next node
    if state.get("completed"):
        return "continue"

    # 2. If over max attempts, end to prevent infinite loops
    if state.get("attempts", 0) >= MAX_ATTEMPTS:
        return "__end__"

    messages = state.get("messages", [])
    if not messages:
        return "__end__"

    last_message = messages[-1]

    # 3. If agent called tools, route to tool_node
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    # 4. Default: retry (error or unexpected state - try again until max attempts)
    return "retry"


# =============================================================================
# GRAPH DEFINITION
# =============================================================================
# Graph structure:
#   START -> agent -> (router) -> tools -> agent -> ... -> END
#
# Tools always return to agent. Agent decides whether to call more tools.

def create_graph():
    graph = StateGraph(ConversationState)

    # Add nodes
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    # Entry point
    graph.add_edge(START, "agent")

    # Agent routes through router to decide: continue, tools, retry, or end
    graph.add_conditional_edges(
        source="agent",
        path=agent_router,
        path_map={
            "continue": END,  # In larger workflows, map to next node
            "tools": "tools",
            "retry": "agent",  # Retry on error until max attempts
            "__end__": END,
        }
    )

    # Tools always return to agent - agent decides if more tools needed
    graph.add_edge("tools", "agent")

    return graph.compile()


# =============================================================================
# USAGE EXAMPLE
# =============================================================================
# async def main():
#     graph = create_graph()
#     result = await graph.ainvoke({
#         "messages": [HumanMessage(content="Search for Python tutorials")],
#         "completed": False,
#         "attempts": 0,
#     })
#     # Final messages include full conversation history
#     print(result["messages"])
```

### LangGraph-Specific Notes

- **Async vs Sync:** All examples use `async def` with `await chain.ainvoke()`. For synchronous execution, use `def` with `chain.invoke()` instead.
- **operator.add:** Return `{"messages": [result]}` NOT `messages + [result]`. The operator handles concatenation.
- **ToolNode:** Handles tool execution and adds ToolMessage to state automatically
- **Direct edge from tools:** Tools always return to agent. Agent decides if more tools needed.
- **Attempts tracking:** Don't increment attempts on tool calls - only on failures

---

## Pitfalls & Best Practices

**Pitfalls:**

- **Wrong return pattern** — Return `{"messages": [result]}` NOT `{"messages": messages + [result]}`. operator.add handles concatenation.

- **Incrementing attempts on tool calls** — Don't increment attempts when calling tools. Only increment on errors.

- **No error handling** — Wrap LLM calls in try/except. On failure, increment attempts and let router terminate.

**Best Practices:**

- **Router order matters** — Check completed first, then attempts, then tool_calls.

- **Use ToolNode** — Don't manually execute tools. ToolNode handles this cleanly.

- **Direct edge from tools** — Tools always return to agent. Agent decides if more tools needed.

- **Set MAX_ATTEMPTS** — 6 is a reasonable default. Adjust based on your use case.

---

## Comparison: Message + Tool vs Other Patterns

| Aspect | Text + Tool | Message + Tool | Structured + Tool |
|--------|-------------|----------------|-------------------|
| Output | Raw string | Message object | Pydantic model |
| History | Internal only | Full conversation | Internal only |
| Tool tracking | Via ToolNode | Via ToolNode + history | Via ToolNode |
| Use case | One-shot research | Conversational | Data extraction |
| State update | `output` field | `messages` list | Structured dict |
