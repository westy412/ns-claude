# Router Pattern

## What It Is

An agent team where nodes dynamically decide the next node at runtime using the `Command` object. Unlike conditional edges (defined at graph compile time), Router pattern allows each node to determine its successor based on execution results.

## When to Use

- Decision trees with runtime branching
- Early exit conditions (skip remaining nodes if done)
- Multi-path workflows based on input classification
- Dynamic routing that can't be predetermined
- When the agent itself should decide where to go next

## When to Avoid

- Simple sequential flow → use **Pipeline** instead
- Parallel execution needed → use **Fan-in/Fan-out** instead
- Iterative refinement → use **Loop** instead
- Routing logic is simple and static → use conditional edges instead

## Graph Structure

```
START → Decision Agent → Agent A → END
                      ↘ Agent B → END
                      ↘ Agent C → END
```

Key difference from conditional edges:
- **Conditional edges:** Router function examines state, defined at graph build time
- **Command pattern:** Each node returns where to go next, decided at runtime

---

## LangGraph Implementation

### Code Template

```python
from typing import TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from pydantic import BaseModel


# =============================================================================
# STATE DEFINITION
# =============================================================================
# State contains fields for ALL possible paths.
# Not all fields will be populated - depends on which path is taken.

class RouterState(TypedDict):
    # Input
    input_data: str

    # Decision result (set by decision node)
    classification: str

    # Path-specific outputs (only one will be set)
    path_a_result: str
    path_b_result: str
    path_c_result: str


# =============================================================================
# STRUCTURED OUTPUTS
# =============================================================================

class ClassificationSchema(BaseModel):
    category: str  # "category_a", "category_b", or "category_c"
    reasoning: str


# =============================================================================
# AGENT TEAM CLASS
# =============================================================================
# Encapsulates all agents in the router pattern.
# Each agent method takes (self, state, name) for consistent interface.
# Node wrappers pass the name and are used in graph definition.

class RouterAgentTeam:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    # -------------------------------------------------------------------------
    # DECISION AGENT
    # -------------------------------------------------------------------------

    async def decision(self, state: RouterState, name: str) -> Command:
        """Classify input and route to appropriate handler."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Classify the input into one of these categories:
- category_a: For technical questions
- category_b: For business questions
- category_c: For general inquiries"""),
            ("user", "{input_data}"),
        ])

        chain = prompt | self.llm.with_structured_output(ClassificationSchema)
        result = await chain.ainvoke({"input_data": state["input_data"]})

        # Prepare state update
        state_update = {
            "classification": result.category,
        }

        # Dynamic routing based on classification
        if result.category == "category_a":
            return Command(
                goto="path_a_agent",
                update=state_update,
            )
        elif result.category == "category_b":
            return Command(
                goto="path_b_agent",
                update=state_update,
            )
        else:
            return Command(
                goto="path_c_agent",
                update=state_update,
            )

    async def decision_node(self, state: RouterState) -> Command:
        """Node wrapper for decision agent."""
        return await self.decision(state, "decision")

    # -------------------------------------------------------------------------
    # PATH A AGENT
    # -------------------------------------------------------------------------

    async def path_a(self, state: RouterState, name: str) -> Command:
        """Handle category A (technical questions)."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a technical expert. Provide detailed technical answers."),
            ("user", "{input_data}"),
        ])

        chain = prompt | self.llm
        result = await chain.ainvoke({"input_data": state["input_data"]})

        # Terminal node - route to END
        return Command(
            goto=END,
            update={"path_a_result": result.content}
        )

    async def path_a_node(self, state: RouterState) -> Command:
        """Node wrapper for path A agent."""
        return await self.path_a(state, "path_a")

    # -------------------------------------------------------------------------
    # PATH B AGENT
    # -------------------------------------------------------------------------

    async def path_b(self, state: RouterState, name: str) -> Command:
        """Handle category B (business questions)."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a business analyst. Provide strategic insights."),
            ("user", "{input_data}"),
        ])

        chain = prompt | self.llm
        result = await chain.ainvoke({"input_data": state["input_data"]})

        return Command(
            goto=END,
            update={"path_b_result": result.content}
        )

    async def path_b_node(self, state: RouterState) -> Command:
        """Node wrapper for path B agent."""
        return await self.path_b(state, "path_b")

    # -------------------------------------------------------------------------
    # PATH C AGENT
    # -------------------------------------------------------------------------

    async def path_c(self, state: RouterState, name: str) -> Command:
        """Handle category C (general inquiries)."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Provide clear, friendly answers."),
            ("user", "{input_data}"),
        ])

        chain = prompt | self.llm
        result = await chain.ainvoke({"input_data": state["input_data"]})

        return Command(
            goto=END,
            update={"path_c_result": result.content}
        )

    async def path_c_node(self, state: RouterState) -> Command:
        """Node wrapper for path C agent."""
        return await self.path_c(state, "path_c")

    # -------------------------------------------------------------------------
    # GRAPH DEFINITION
    # -------------------------------------------------------------------------

    def create_graph(self):
        graph = StateGraph(RouterState)

        # Add all nodes using node wrapper methods
        graph.add_node("decision", self.decision_node)
        graph.add_node("path_a_agent", self.path_a_node)
        graph.add_node("path_b_agent", self.path_b_node)
        graph.add_node("path_c_agent", self.path_c_node)

        # Only define entry edge - Command handles the rest
        graph.add_edge(START, "decision")

        # No conditional edges needed!
        # Each node returns Command(goto=...) to control flow

        return graph.compile()

    # -------------------------------------------------------------------------
    # RUN METHOD
    # -------------------------------------------------------------------------

    async def run(self, input_data: str) -> dict:
        """Execute the router with the given input.

        Args:
            input_data: The input to classify and route.

        Returns:
            The final state dict containing classification and path result.
        """
        # Initialize starting state (inputs only)
        initial_state = {
            "input_data": input_data,
        }

        # Create and invoke graph
        graph = self.create_graph()
        result = await graph.ainvoke(initial_state)

        return result


# =============================================================================
# USAGE EXAMPLE
# =============================================================================
# async def main():
#     llm = ChatOpenAI(model="gpt-4")
#     agent_team = RouterAgentTeam(llm=llm)
#
#     result = await agent_team.run("How do I optimize database queries?")
#     # Check which path was taken
#     print(f"Classification: {result['classification']}")
#     print(f"Path A: {result.get('path_a_result')}")
#     print(f"Path B: {result.get('path_b_result')}")
#     print(f"Path C: {result.get('path_c_result')}")
```

### LangGraph-Specific Notes

- **Async vs Sync:** All examples use `async def` with `await chain.ainvoke()`. For synchronous execution, use `def` with `chain.invoke()` instead.
- **Class-based agents:** All agents encapsulated in a single class with `__init__` for LLM setup
- **Name argument:** Each agent method takes `(self, state, name)` for tracing and message attribution
- **Node wrappers:** `async def X_node(self, state)` calls `self.X(state, "X")` — used in graph definition
- **Command import:** `from langgraph.types import Command`
- **No edges needed:** Beyond `START → first_node`, Command handles all routing
- **State update:** `Command(goto="node", update=state_dict)` updates state AND routes
- **Terminal routing:** Use `Command(goto=END, update=state)` to end execution

---

## Routing Strategies

### Binary Decision

Simple if/else routing:

```python
async def binary_decision(state: State) -> Command:
    result = await analyze(state)

    if result["is_valid"]:
        return Command(
            goto="valid_handler",
            update={"validated": True},
        )
    else:
        return Command(
            goto="invalid_handler",
            update={"validated": False},
        )
```

### Multi-Path Decision

Multiple possible destinations:

```python
async def multi_path_decision(state: State) -> Command:
    result = await classify(state)
    category = result["category"]

    # Map categories to nodes
    routing_map = {
        "urgent": "urgent_handler",
        "normal": "normal_handler",
        "low": "low_priority_handler",
        "spam": "spam_handler",
    }

    next_node = routing_map.get(category, "default_handler")
    return Command(
        goto=next_node,
        update={"category": category},
    )
```

### Early Exit

Skip remaining nodes when condition is met:

```python
async def check_and_maybe_exit(state: State) -> Command:
    # Check if we can exit early
    if state.get("already_resolved"):
        return Command(
            goto=END,
            update={"result": "Resolved from cache"}
        )

    # Otherwise continue to next node
    return Command(
        goto="process_agent",
        update={"needs_processing": True}
    )
```

### Sequential with Decision Points

Linear flow with exit ramps:

```python
# Node 1: Always goes to Node 2
async def node_1(state: State) -> Command:
    result = await process_step_1(state)
    return Command(
        goto="node_2",
        update={"step_1": result},
    )

# Node 2: May exit or continue
async def node_2(state: State) -> Command:
    result = await process_step_2(state)

    if result["complete"]:
        return Command(
            goto=END,
            update={"final": result},
        )
    else:
        return Command(
            goto="node_3",
            update={"step_2": result},
        )

# Node 3: Terminal
async def node_3(state: State) -> Command:
    result = await process_step_3(state)
    return Command(
        goto=END,
        update={"final": result},
    )
```

---

## State Flow

```
Initial State:
  input_data: "How do I optimize database queries?"
  classification: None
  path_a_result: None
  path_b_result: None
  path_c_result: None

After Decision Node:
  input_data: "How do I optimize database queries?"
  classification: "category_a"  ← Set by decision
  path_a_result: None
  path_b_result: None
  path_c_result: None

  Command(goto="path_a_agent") ← Routes to technical handler

After Path A Agent:
  input_data: "How do I optimize database queries?"
  classification: "category_a"
  path_a_result: "Technical answer..."  ← Set by handler
  path_b_result: None                   ← Never set (different path)
  path_c_result: None                   ← Never set (different path)

  Command(goto=END) ← Terminates
```

---

## Comparison: Command vs Conditional Edges

| Aspect | Conditional Edges | Command Pattern |
|--------|------------------|-----------------|
| Routing defined | Graph compile time | Node runtime |
| Routing function | Separate function | Within node logic |
| State updates | After routing | Simultaneous with routing |
| Complexity | Good for simple branches | Better for complex trees |
| Debugging | Static graph visualization | Need runtime tracing |

### When to use Conditional Edges

```python
# Simple routing based on state field
def router(state: State) -> str:
    if state["completed"]:
        return "__end__"
    return "continue"

graph.add_conditional_edges(
    source="agent",
    path=router,
    path_map={"continue": "next_agent", "__end__": END}
)
```

### When to use Command

```python
# Complex routing with state updates
async def agent(state: State) -> Command:
    result = await process(state)

    # Routing decision based on processing result
    if result["type"] == "A" and result["score"] > 0.8:
        return Command(
            goto="high_confidence_a",
            update={"result": result},
        )
    elif result["type"] == "A":
        return Command(
            goto="low_confidence_a",
            update={"result": result},
        )
    elif result["type"] == "B":
        return Command(
            goto="type_b_handler",
            update={"result": result},
        )
    else:
        return Command(
            goto=END,
            update={"result": result},
        )
```

---

## Pitfalls & Best Practices

**Pitfalls:**

- **Missing nodes** — If Command routes to a node that doesn't exist, graph fails. Ensure all possible destinations are added as nodes.

- **No default case** — If classification returns unexpected value, routing fails. Always have a fallback.

- **State field access on wrong path** — Fields set by path A won't exist if path B was taken. Use `.get()` with defaults.

**Best Practices:**

- **Comprehensive state definition** — Include fields for ALL paths in TypedDict, even if not all are used.

- **Use `.get()` for path-dependent fields** — `result.get("path_a_result")` instead of `result["path_a_result"]`.

- **Document routing logic** — Comment which conditions lead to which paths.

- **Consider hybrid approach** — Use Command for complex decisions, conditional edges for simple ones.

---

## Comparison with Other Patterns

| Aspect | Router | Pipeline | Fan-in/Fan-out | Loop |
|--------|--------|----------|----------------|------|
| Flow | Dynamic branching | Linear | Parallel | Cyclical |
| Edges | Command objects | Direct edges | Multiple edges | Conditional edges |
| Next node | Runtime decision | Predetermined | All at once | Condition-based |
| Use case | Decision trees | Sequential processing | Parallelization | Refinement |
