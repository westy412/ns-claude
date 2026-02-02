# Text + Tool Agent

## What It Is

An LLM agent with access to tools that returns text output after tool execution. Combines the simplicity of text output with the capability to take actions via tool calls.

## When to Use

- Agent needs to retrieve external information before responding
- Performing searches, lookups, or API calls with human-readable output
- Research tasks where results should be summarized as text
- When tool results should be processed and explained to humans
- Simple action-taking agents with text-based responses

## When to Avoid

- Output must be programmatically parsed — use **Structured Output + Tool Agent** instead
- Conversation history is important — use **Message + Tool Agent** instead
- No external actions needed — use **Text Agent** instead (simpler)
- Tool results need to be preserved in message history — use **Message + Tool Agent** instead

## Selection Criteria

- If agent needs tools AND output is human-readable text → **Text + Tool Agent**
- If agent needs tools AND output must be structured → consider **Structured Output + Tool Agent**
- If agent needs tools AND conversation history matters → consider **Message + Tool Agent**
- If no tools needed → consider **Text Agent**

## Inputs / Outputs

**Inputs:**
- State fields containing context/data for the prompt
- Tool definitions (functions the agent can call)
- Prompt template (system message + user input)

**Outputs:**
- Text string (final response after tool execution)
- Updated state with output field

## Prompting Guidelines

- Clearly describe available tools and when to use them in the system prompt
- Instruct the agent to explain its reasoning and tool usage
- Specify when the agent should stop calling tools and provide a final answer
- Consider limiting the number of tool calls to prevent loops

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
# Define tools with @tool decorator. Include clear docstrings - these are
# shown to the LLM and help it understand when to use each tool.

@tool
async def search_database(query: str) -> str:
    """Search the database for relevant information."""
    return f"Results for: {query}"

@tool
async def get_current_data(metric: str) -> str:
    """Get current value of a metric."""
    return f"Current {metric}: 42"

tools = [search_database, get_current_data]


# =============================================================================
# TOOL NODE
# =============================================================================
# ToolNode from langgraph.prebuilt handles tool execution automatically.
# It reads tool_calls from the last message and executes them.

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

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]  # Conversation/tool history
    output: str                               # Final text output
    completed: bool                           # Whether agent is done
    attempts: int                             # Track retry attempts


MAX_ATTEMPTS = 6  # Maximum iterations before forced termination


# =============================================================================
# AGENT NODE
# =============================================================================
# The agent receives messages and decides whether to call tools or finish.
# Uses MessagesPlaceholder to see full history including tool results.
# Wrapped in try/except - on failure, increment attempts and continue.

async def agent_node(state: AgentState) -> dict:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Use tools to gather information, then provide a final answer."),
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

        # No tool calls - agent is done, extract text output
        return {
            "messages": [result],
            "output": result.content,
            "attempts": attempts + 1,
            "completed": True,
        }

    except Exception as e:
        # On failure, increment attempts and return empty
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

def agent_router(state: AgentState) -> str:
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
    graph = StateGraph(AgentState)

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
#     print(result["output"])
```

### LangGraph-Specific Notes

- **Async vs Sync:** All examples use `async def` with `await chain.ainvoke()`. For synchronous execution, use `def` with `chain.invoke()` instead.
- **ToolNode:** Use `ToolNode` from `langgraph.prebuilt` to handle tool execution automatically
- **Direct edge from tools:** Tools always return to agent. Agent decides if more tools needed.
- **Tool binding:** Use `llm.bind_tools(tools)` to give the LLM access to tools
- **Attempts tracking:** Don't increment attempts on tool calls - only on failures

---

## Pitfalls & Best Practices

**Pitfalls:**

- **Infinite tool loops** — Without attempts tracking, agents can loop forever. Router checks attempts and ends if over limit.

- **Incrementing attempts on tool calls** — Don't increment attempts when calling tools. Only increment on errors.

- **No error handling** — Wrap LLM calls in try/except. On failure, increment attempts and let router terminate.

**Best Practices:**

- **Router order matters** — Check completed first, then attempts, then tool_calls.

- **Use ToolNode** — Don't manually execute tools. ToolNode handles this cleanly.

- **Direct edge from tools** — Tools always return to agent. Agent decides if more tools needed.

- **Set MAX_ATTEMPTS** — 6 is a reasonable default. Adjust based on your use case.

---

## Comparison: Text + Tool vs Message + Tool

| Aspect | Text + Tool Agent | Message + Tool Agent |
|--------|------------------|---------------------|
| Output | Raw text string | Message object |
| History | Used internally | Preserved for conversation |
| Tool tracking | Via ToolNode | Via ToolNode + history |
| Use case | Single-shot research | Conversational tool use |
| Final state | `output` field | `messages` list |
