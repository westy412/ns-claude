# Structured Output + Tool Agent

## What It Is

An LLM agent with access to tools that returns typed, schema-validated output. Combines tool capabilities with structured output by using a "completion tool" pattern - the agent calls tools to gather data, then calls a special tool to submit structured results.

## When to Use

- Agent needs to gather data via tools AND return structured results
- Data extraction pipelines that require external lookups
- Research tasks where findings must be in a specific format
- When downstream code requires both tool actions AND structured data

## When to Avoid

- Output is for human reading — use **Text + Tool Agent** instead
- Conversation history is important — use **Message + Tool Agent** instead
- No tools needed — use **Structured Output Agent** instead (simpler)
- Simple tool use with text output — use **Text + Tool Agent** instead (simpler)

## Selection Criteria

- If agent needs tools AND output must be structured → **Structured Output + Tool Agent**
- If agent needs tools AND output is human-readable → consider **Text + Tool Agent**
- If agent needs tools AND conversation history matters → consider **Message + Tool Agent**
- If no tools needed but output must be structured → consider **Structured Output Agent**

## Inputs / Outputs

**Inputs:**
- State fields containing context/data for the prompt
- Tool definitions (functions the agent can call)
- "Completion tool" for submitting structured output

**Outputs:**
- Structured data (extracted from completion tool call)
- Converted to dict for state updates

## Prompting Guidelines

- Define both data-gathering tools and a completion tool
- Tell the agent to use tools to gather information first
- Instruct the agent to call the completion tool when done
- The completion tool's arguments define the structured output schema

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
# Define data-gathering tools and a "completion tool" for structured output.
# The completion tool's arguments define the output schema.

@tool
async def search_info(query: str) -> str:
    """Search for relevant information."""
    return f"Found information about: {query}"

@tool
async def get_details(item: str) -> str:
    """Get detailed information about an item."""
    return f"Details for {item}: ..."


# The completion tool defines the structured output schema via its arguments.
# This is a "dummy" tool - we intercept its args, not its return value.
@tool
async def submit_result(summary: str, key_findings: str, confidence: str) -> str:
    """
    Submit the final structured result.

    Args:
        summary: Brief summary of findings
        key_findings: Main discoveries or insights
        confidence: Confidence level (high/medium/low)
    """
    return "Result submitted"


# Separate tools for gathering vs completion
gathering_tools = [search_info, get_details]
completion_tool = submit_result
all_tools = gathering_tools + [completion_tool]


# =============================================================================
# TOOL NODE
# =============================================================================
# ToolNode handles tool execution for gathering tools only.
# We intercept the completion tool in the agent before it reaches ToolNode.

tool_node = ToolNode(gathering_tools)


# =============================================================================
# LLM SETUP
# =============================================================================
llm = ChatOpenAI(model="gpt-4")


# =============================================================================
# STATE DEFINITION
# =============================================================================
# Track attempts for retry logic and completed for termination.

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]  # Conversation/tool history
    output: dict                              # Structured output
    completed: bool                           # Whether agent is done
    attempts: int                             # Track retry attempts


MAX_ATTEMPTS = 6  # Maximum iterations before forced termination


# =============================================================================
# AGENT NODE
# =============================================================================
# Agent gathers data with tools, then calls completion tool to submit results.
# We intercept the completion tool call to extract structured data.
# Wrapped in try/except - on failure, increment attempts and continue.

async def agent_node(state: AgentState) -> dict:
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a research assistant. Use tools to gather information.
When you have enough data, call submit_result with your findings."""),
        MessagesPlaceholder(variable_name="messages"),
    ])

    # Bind all tools (including completion tool)
    chain = prompt | llm.bind_tools(all_tools)

    attempts = state.get("attempts", 0)

    try:
        result = await chain.ainvoke({"messages": state["messages"]})

        # Check for tool calls
        if result.tool_calls:
            tool_name = result.tool_calls[0]["name"]

            # Check if it's the completion tool - intercept and extract output
            if tool_name == "submit_result":
                args = result.tool_calls[0]["args"]
                output = {
                    "summary": args.get("summary", ""),
                    "key_findings": args.get("key_findings", ""),
                    "confidence": args.get("confidence", ""),
                }
                return {
                    "messages": [result],
                    "output": output,
                    "attempts": attempts + 1,
                    "completed": True,
                }

            # Otherwise, it's a gathering tool - continue loop
            # Tool calls don't increment attempts
            return {
                "messages": [result],
                "completed": False,
            }

        # No tool calls - shouldn't happen, increment attempts and retry
        return {
            "messages": [result],
            "attempts": attempts + 1,
            "completed": False,
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

def agent_router(state: AgentState) -> str:
    # 1. If completed (completion tool was called), continue to next node
    if state.get("completed"):
        return "continue"

    # 2. If over max attempts, end to prevent infinite loops
    if state.get("attempts", 0) >= MAX_ATTEMPTS:
        return "__end__"

    messages = state.get("messages", [])
    if not messages:
        return "__end__"

    last_message = messages[-1]

    # 3. If agent called gathering tools, route to tool_node
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
#         "messages": [HumanMessage(content="Research Python frameworks")],
#         "completed": False,
#         "attempts": 0,
#         "output": {},
#     })
#     print(result["output"])  # Structured output dict
```

### Forced Tool Calling Variant

To force the agent to always call the completion tool (guaranteeing structured output):

```python
# Bind with tool_choice to force the completion tool
bound_llm = llm.bind_tools(
    [submit_result],
    tool_choice="submit_result"  # Forces this tool to be called
)

async def forced_output_agent(state: AgentState) -> dict:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize the gathered information."),
        MessagesPlaceholder(variable_name="messages"),
    ])

    attempts = state.get("attempts", 0)

    try:
        chain = prompt | bound_llm
        result = await chain.ainvoke({"messages": state["messages"]})

        # Tool will definitely be called due to tool_choice
        if result.tool_calls:
            args = result.tool_calls[0]["args"]
            return {
                "messages": [result],
                "output": {
                    "summary": args.get("summary", ""),
                    "key_findings": args.get("key_findings", ""),
                    "confidence": args.get("confidence", ""),
                },
                "attempts": attempts + 1,
                "completed": True,
            }

        # Fallback if tool_choice fails - increment attempts and retry
        return {
            "messages": [result],
            "attempts": attempts + 1,
            "completed": False,
        }

    except Exception as e:
        # On failure, increment attempts and retry
        return {
            "messages": [AIMessage(content=f"Error: {e}")],
            "attempts": attempts + 1,
            "completed": False,
        }
```

### LangGraph-Specific Notes

- **Async vs Sync:** All examples use `async def` with `await chain.ainvoke()`. For synchronous execution, use `def` with `chain.invoke()` instead.
- **Completion tool pattern:** Define structured output as a tool's arguments, intercept the call
- **tool_choice:** Use `bind_tools(tools, tool_choice="tool_name")` to force a specific tool call
- **ToolNode for gathering only:** Use ToolNode only for data-gathering tools, not the completion tool
- **Intercept completion:** Check tool name and extract args instead of executing the tool
- **Direct edge from tools:** Tools always return to agent. Agent decides if more tools needed.

---

## Pitfalls & Best Practices

**Pitfalls:**

- **Running completion tool through ToolNode** — The completion tool is for schema definition, not execution. Intercept it in the agent.

- **Missing fields** — Use `.get()` with defaults when extracting args to handle missing fields gracefully.

- **No error handling** — Wrap LLM calls in try/except. On failure, increment attempts and let router terminate.

**Best Practices:**

- **Router order matters** — Check completed first, then attempts, then tool_calls.

- **Direct edge from tools** — Tools always return to agent. Agent decides if more tools needed.

- **Separate tool types** — Distinguish between gathering tools (ToolNode) and completion tool (intercepted).

- **Use tool_choice for guarantees** — When you need guaranteed structured output, force the tool call.

- **Validate extracted data** — Consider validating extracted args against a Pydantic model.

---

## Comparison: All Tool-Using Patterns

| Aspect | Text + Tool | Message + Tool | Structured + Tool |
|--------|-------------|----------------|-------------------|
| Output | Raw string | Message object | Dict/Pydantic |
| Validation | None | None | Via tool args |
| History | Internal only | Full conversation | Internal only |
| Completion | No tool calls | No tool calls | Completion tool |
| Use case | Research summaries | Conversational | Data extraction |
