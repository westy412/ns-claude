# LangGraph Cheat Sheet

**Read this BEFORE implementing any LangGraph code.**

This cheat sheet contains critical rules, patterns, and anti-patterns for LangGraph implementations.

---

## Critical Rules

### 1. ToolNode MUST Be a Graph Node

**CORRECT:**
```python
# Tool node created at class/module level
tool_node = ToolNode(tools)

def create_graph(self):
    graph = StateGraph(State)
    graph.add_node("agent", self.agent_node)
    graph.add_node("tools", tool_node)  # ← Added to graph

    # Conditional routing to tools
    graph.add_conditional_edges(
        source="agent",
        path=self.router,
        path_map={"tools": "tools", "continue": "next_node"}
    )
    graph.add_edge("tools", "agent")  # Tools return to agent
```

**WRONG - DO NOT DO THIS:**
```python
async def agent_node(self, state):
    response = await chain.ainvoke(state)

    if response.tool_calls:
        # WRONG: Creating ToolNode inside agent function
        tool_node = ToolNode(self.tools)
        # WRONG: Manually invoking ToolNode
        tool_result = await tool_node.ainvoke({"messages": [response]})
```

**Why:** ToolNode is designed to be a graph node with proper state management. Creating it inside agent functions bypasses LangGraph's execution model.

---

### 2. Command Pattern vs Conditional Edges

| Use | When |
|-----|------|
| **Command** | Dynamic routing decided by agent at runtime |
| **Conditional Edges** | Routing based on state inspection (tool calls, completed flag) |

**Command Pattern:**
```python
async def agent_node(self, state) -> Command:
    result = await chain.ainvoke(state)

    # Agent decides where to go
    if result.category == "A":
        return Command(goto="handler_a", update={"category": "A"})
    else:
        return Command(goto="handler_b", update={"category": "B"})
```

**Conditional Edges:**
```python
def router(state) -> str:
    # Inspect state to decide routing
    if state.get("completed"):
        return "end"
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "continue"

graph.add_conditional_edges("agent", router, {"tools": "tools", "continue": END})
```

**Key Rule:** Use conditional edges for tool routing. Use Command for business logic routing.

---

### 3. Tool-Using Agents in Router Pattern

When combining router pattern (Command) with tool-using agents:

**Option A: Separate tool nodes per agent**
```python
def create_graph(self):
    graph = StateGraph(State)

    # Router
    graph.add_node("router", self.router_node)

    # Agent + Tool pairs
    graph.add_node("youtube_agent", self.youtube_agent_node)
    graph.add_node("youtube_tools", ToolNode(self.youtube_tools))

    graph.add_node("github_agent", self.github_agent_node)
    graph.add_node("github_tools", ToolNode(self.github_tools))

    # Entry
    graph.add_edge(START, "router")

    # Tool routing for each agent
    graph.add_conditional_edges(
        "youtube_agent",
        self.tool_router,
        {"tools": "youtube_tools", "continue": "next_node"}
    )
    graph.add_edge("youtube_tools", "youtube_agent")
```

**Option B: Shared tool node (if tools are the same)**
```python
# All agents share one tool node
all_tools = [fetch_content, search_web]
shared_tool_node = ToolNode(all_tools)

graph.add_node("tools", shared_tool_node)
# Multiple agents can route to same tool node
```

---

### 4. State Definition Patterns

**Message-based state (for tool agents):**
```python
from typing import Annotated
import operator

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]  # Auto-concatenates
    output: str
    completed: bool
```

**Simple state (for non-tool agents):**
```python
class SimpleState(TypedDict):
    input: str
    output: str
    metadata: dict
```

**Router pattern state:**
```python
class RouterState(TypedDict):
    # Input
    input_data: str

    # Include fields for ALL paths (some will be None)
    path_a_result: Optional[str]
    path_b_result: Optional[str]
```

---

### 5. Async Patterns

**Always use async:**
```python
async def agent_node(self, state) -> dict:
    result = await chain.ainvoke(state)  # ainvoke, not invoke
    return {"output": result.content}
```

**Graph invocation:**
```python
result = await graph.ainvoke(initial_state)  # ainvoke
```

---

### 6. Escape Curly Braces in Prompts with JSON Examples

LangChain's `ChatPromptTemplate` interprets `{text}` as template variables. If your system prompts contain JSON examples, they will break at runtime.

**CORRECT - Use a helper function:**
```python
def _escape_braces(prompt: str) -> str:
    """Escape curly braces for LangChain prompt templates."""
    return prompt.replace("{", "{{").replace("}", "}}")

ROUTER_PROMPT = _escape_braces("""
<output_format>
Return JSON:
{
  "category": "one" | "two",
  "confidence": 0.0-1.0
}
</output_format>
""")
```

**WRONG - Unescaped braces in prompt:**
```python
# WRONG - Will fail with KeyError at runtime
ROUTER_PROMPT = """
Return JSON:
{
  "category": "one"
}
"""

# Error: KeyError: 'Input to ChatPromptTemplate is missing variables'
```

**Why:** The `{` and `}` in JSON examples are interpreted as template variables like `{url}`. Using a helper function keeps prompts readable while escaping at runtime.

**When to use:** Apply `_escape_braces()` to any system prompt containing JSON examples, code snippets with braces, or any literal `{` or `}` characters.

---

## Anti-Patterns

### DO NOT: Manually invoke ToolNode

```python
# WRONG
tool_node = ToolNode(tools)
result = await tool_node.ainvoke({"messages": [response]})
```

### DO NOT: Create ToolNode inside functions

```python
# WRONG
async def agent(state):
    if response.tool_calls:
        tool_node = ToolNode(tools)  # WRONG
```

### DO NOT: Skip conditional edges for tool routing

```python
# WRONG - No way to route to tools
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
graph.add_edge("agent", "tools")  # Always goes to tools
graph.add_edge("tools", END)      # Can't loop back
```

### DO NOT: Mix Command and tool routing incorrectly

```python
# WRONG - Command doesn't handle tool calls
async def agent(state) -> Command:
    response = await chain.ainvoke(state)
    if response.tool_calls:
        return Command(goto="tools")  # Tools need conditional edges, not Command
```

### DO NOT: Leave curly braces unescaped in prompts

```python
# WRONG - JSON braces will be interpreted as template variables
PROMPT = """
Return: {"status": "ok"}
"""
# Runtime error: KeyError: 'Input to ChatPromptTemplate is missing variables {"status"}'
```

---

## Quick Reference

| Task | Pattern |
|------|---------|
| Add tools to agent | `llm.bind_tools(tools)` |
| Create tool node | `ToolNode(tools)` at module/class level |
| Add tool node to graph | `graph.add_node("tools", tool_node)` |
| Route to tools | Conditional edges checking `tool_calls` |
| Return from tools | Direct edge back to agent |
| Dynamic routing | Command pattern |
| State-based routing | Conditional edges |
| Agent with structured output | `llm.with_structured_output(Schema)` |

---

## Imports Reference

```python
# Core
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langgraph.prebuilt import ToolNode

# LangChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

# Pydantic
from pydantic import BaseModel, Field

# Typing
from typing import TypedDict, Annotated, Optional, List, Literal
from typing_extensions import TypedDict
import operator
```
