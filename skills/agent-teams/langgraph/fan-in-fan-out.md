# Fan-in/Fan-out Pattern

## What It Is

An agent team where execution splits into multiple parallel branches (fan-out) and then converges (fan-in). Enables concurrent processing of independent tasks with result aggregation.

## When to Use

- Tasks are independent and can run in parallel
- Multiple perspectives needed on the same input
- Performance optimization via concurrency
- Different specialists analyzing the same data
- Aggregation or voting across multiple outputs

## When to Avoid

- Tasks have dependencies (one needs output of another) → use **Pipeline** instead
- Only one path should execute based on condition → use **Router** instead
- Iterative refinement needed → use **Loop** instead
- Parallelization adds complexity without benefit (simple tasks)

## Graph Structure

```
START
  ├──> Agent A ──┐
  ├──> Agent B ──┼──> END
  └──> Agent C ──┘
```

All branches execute in parallel (async). LangGraph waits for ALL branches to complete before proceeding past the fan-in point.

---

## LangGraph Implementation

### Code Template

```python
from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END


# =============================================================================
# CUSTOM REDUCER
# =============================================================================
# For parallel branches, we need a reducer to handle state merging.
# This reducer keeps the first non-empty value (prevents overwrites).

def first_non_empty(a: str, b: str) -> str:
    """Keep first non-empty value. Suitable for parallel branches."""
    return a if a else b


# =============================================================================
# STATE DEFINITION
# =============================================================================
# Each parallel branch writes to its own field.
# Custom reducer prevents conflicts when branches complete.

class FanOutState(TypedDict):
    # Input (shared by all branches)
    input_data: str

    # Parallel branch outputs
    analysis_a: Annotated[str, first_non_empty]
    analysis_b: Annotated[str, first_non_empty]
    analysis_c: Annotated[str, first_non_empty]

    # Aggregated output (optional merge node)
    combined_result: str


# =============================================================================
# AGENT TEAM CLASS
# =============================================================================
# Encapsulates all agents in the fan-in/fan-out pattern.
# Each agent method takes (self, state, name) for consistent interface.
# Node wrappers pass the name and are used in graph definition.

class FanOutAgentTeam:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    # -------------------------------------------------------------------------
    # AGENT A - TECHNICAL PERSPECTIVE
    # -------------------------------------------------------------------------

    async def agent_a(self, state: FanOutState, name: str) -> dict:
        """Technical analysis perspective."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Analyze from a technical perspective. Focus on implementation details."),
            ("user", "{input_data}"),
        ])

        chain = prompt | self.llm
        result = await chain.ainvoke({"input_data": state["input_data"]})

        return {
            "analysis_a": result.content,
        }

    async def agent_a_node(self, state: FanOutState) -> dict:
        """Node wrapper for agent A."""
        return await self.agent_a(state, "agent_a")

    # -------------------------------------------------------------------------
    # AGENT B - BUSINESS PERSPECTIVE
    # -------------------------------------------------------------------------

    async def agent_b(self, state: FanOutState, name: str) -> dict:
        """Business analysis perspective."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Analyze from a business perspective. Focus on ROI and strategy."),
            ("user", "{input_data}"),
        ])

        chain = prompt | self.llm
        result = await chain.ainvoke({"input_data": state["input_data"]})

        return {
            "analysis_b": result.content,
        }

    async def agent_b_node(self, state: FanOutState) -> dict:
        """Node wrapper for agent B."""
        return await self.agent_b(state, "agent_b")

    # -------------------------------------------------------------------------
    # AGENT C - RISK PERSPECTIVE
    # -------------------------------------------------------------------------

    async def agent_c(self, state: FanOutState, name: str) -> dict:
        """Risk analysis perspective."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Analyze from a risk perspective. Focus on potential issues and mitigations."),
            ("user", "{input_data}"),
        ])

        chain = prompt | self.llm
        result = await chain.ainvoke({"input_data": state["input_data"]})

        return {
            "analysis_c": result.content,
        }

    async def agent_c_node(self, state: FanOutState) -> dict:
        """Node wrapper for agent C."""
        return await self.agent_c(state, "agent_c")

    # -------------------------------------------------------------------------
    # GRAPH DEFINITION
    # -------------------------------------------------------------------------

    def create_graph(self):
        graph = StateGraph(FanOutState)

        # Add parallel nodes using node wrapper methods
        graph.add_node("agent_a", self.agent_a_node)
        graph.add_node("agent_b", self.agent_b_node)
        graph.add_node("agent_c", self.agent_c_node)

        # FAN-OUT: Multiple edges from START
        graph.add_edge(START, "agent_a")
        graph.add_edge(START, "agent_b")
        graph.add_edge(START, "agent_c")

        # FAN-IN: Multiple edges to END
        graph.add_edge("agent_a", END)
        graph.add_edge("agent_b", END)
        graph.add_edge("agent_c", END)

        return graph.compile()

    # -------------------------------------------------------------------------
    # RUN METHOD
    # -------------------------------------------------------------------------

    async def run(self, input_data: str) -> dict:
        """Execute the fan-out pattern with the given input.

        Args:
            input_data: The input to analyze from multiple perspectives.

        Returns:
            The final state dict containing all parallel outputs.
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
#     agent_team = FanOutAgentTeam(llm=llm)
#
#     result = await agent_team.run("Should we adopt microservices architecture?")
#     print("Technical:", result["analysis_a"])
#     print("Business:", result["analysis_b"])
#     print("Risk:", result["analysis_c"])
```

### LangGraph-Specific Notes

- **Async vs Sync:** All examples use `async def` with `await chain.ainvoke()`. For synchronous execution, use `def` with `chain.invoke()` instead.
- **Class-based agents:** All agents encapsulated in a single class with `__init__` for LLM setup
- **Name argument:** Each agent method takes `(self, state, name)` for tracing and message attribution
- **Node wrappers:** `async def X_node(self, state)` calls `self.X(state, "X")` — used in graph definition
- **Multiple edges = parallel:** Adding multiple edges from the same source triggers parallel execution
- **Automatic waiting:** LangGraph waits for ALL incoming edges before executing the target
- **Custom reducers:** Use `Annotated[type, reducer]` to handle state merging from parallel branches
- **Defer for asymmetric branches:** Use `graph.add_node("name", func, defer=True)` when branches have different lengths

---

## Variants

### With Merge Node

Add an aggregation step after parallel execution. The merge agent is also defined within the class:

```python
class FanOutWithMergeAgentTeam(FanOutAgentTeam):
    """Extends base team with a merge agent."""

    # -------------------------------------------------------------------------
    # MERGE AGENT
    # -------------------------------------------------------------------------

    async def merge(self, state: FanOutState, name: str) -> dict:
        """Combine results from all parallel branches."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Synthesize these three analyses into a cohesive recommendation."),
            ("user", """
Technical Analysis: {analysis_a}

Business Analysis: {analysis_b}

Risk Analysis: {analysis_c}
"""),
        ])

        chain = prompt | self.llm
        result = await chain.ainvoke({
            "analysis_a": state["analysis_a"],
            "analysis_b": state["analysis_b"],
            "analysis_c": state["analysis_c"],
        })

        return {
            "combined_result": result.content,
        }

    async def merge_node(self, state: FanOutState) -> dict:
        """Node wrapper for merge agent."""
        return await self.merge(state, "merge")

    # -------------------------------------------------------------------------
    # GRAPH DEFINITION WITH MERGE
    # -------------------------------------------------------------------------

    def create_graph(self):
        graph = StateGraph(FanOutState)

        # Add parallel nodes using node wrapper methods
        graph.add_node("agent_a", self.agent_a_node)
        graph.add_node("agent_b", self.agent_b_node)
        graph.add_node("agent_c", self.agent_c_node)
        graph.add_node("merge", self.merge_node)

        # Fan-out
        graph.add_edge(START, "agent_a")
        graph.add_edge(START, "agent_b")
        graph.add_edge(START, "agent_c")

        # Fan-in to merge node (not END)
        graph.add_edge("agent_a", "merge")
        graph.add_edge("agent_b", "merge")
        graph.add_edge("agent_c", "merge")

        # Then to END
        graph.add_edge("merge", END)

        return graph.compile()
```

**Flow:**
```
START → [A, B, C] (parallel) → merge → END
```

### Diamond Pattern

Fan-out to independent nodes, then fan-in to a dependent node:

```python
def create_diamond_graph():
    graph = StateGraph(DiamondState)

    graph.add_node("data_fetch", data_fetch_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("dependent", dependent_node)  # Needs both above

    # Fan-out from START
    graph.add_edge(START, "data_fetch")
    graph.add_edge(START, "analysis")

    # Fan-in to dependent node
    graph.add_edge("data_fetch", "dependent")
    graph.add_edge("analysis", "dependent")

    graph.add_edge("dependent", END)

    return graph.compile()
```

**Flow:**
```
START
  ├──> data_fetch ──┐
  └──> analysis ────┴──> dependent ──> END
```

### Nested Fan-Out (Hierarchical)

Subgraphs that internally use fan-out:

```python
async def subgraph_node(state: State) -> dict:
    """A node that runs its own fan-out graph internally."""
    # Create and run internal graph
    internal_graph = create_internal_fan_out_graph()
    result = await internal_graph.ainvoke(state)
    return result


def create_main_graph():
    graph = StateGraph(State)

    # Main level fan-out
    graph.add_node("subgraph_a", subgraph_a_node)  # Has internal parallelism
    graph.add_node("subgraph_b", subgraph_b_node)  # Has internal parallelism

    graph.add_edge(START, "subgraph_a")
    graph.add_edge(START, "subgraph_b")

    graph.add_edge("subgraph_a", END)
    graph.add_edge("subgraph_b", END)

    return graph.compile()
```

### Asymmetric Branches with Defer

When parallel branches have different lengths, use `defer=True` on the convergence node to ensure it waits for ALL branches to complete.

**The Problem:**
```
START → A → A2 → merge
START → B ──────→ merge
```

Without `defer`, the merge node could execute after B finishes but before A2 completes, resulting in missing data.

**Solution:**
```python
from typing import Annotated
import operator
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


class AsymmetricState(TypedDict):
    input_data: str
    branch_a_result: str
    branch_b_result: str
    merged_result: str


def step_a1(state: AsymmetricState) -> dict:
    """First step of longer branch."""
    return {"branch_a_result": "Step A1 done"}


def step_a2(state: AsymmetricState) -> dict:
    """Second step of longer branch."""
    return {"branch_a_result": state["branch_a_result"] + " → Step A2 done"}


def step_b(state: AsymmetricState) -> dict:
    """Single step branch (completes faster)."""
    return {"branch_b_result": "Step B done"}


def merge_results(state: AsymmetricState) -> dict:
    """Merge all branch results."""
    return {
        "merged_result": f"A: {state['branch_a_result']}, B: {state['branch_b_result']}"
    }


def create_asymmetric_graph():
    graph = StateGraph(AsymmetricState)

    graph.add_node("step_a1", step_a1)
    graph.add_node("step_a2", step_a2)
    graph.add_node("step_b", step_b)
    graph.add_node("merge", merge_results, defer=True)  # ← KEY: defer=True

    # Branch A: Two steps
    graph.add_edge(START, "step_a1")
    graph.add_edge("step_a1", "step_a2")
    graph.add_edge("step_a2", "merge")

    # Branch B: One step
    graph.add_edge(START, "step_b")
    graph.add_edge("step_b", "merge")

    graph.add_edge("merge", END)

    return graph.compile()
```

**Flow:**
```
START
  ├──> step_a1 → step_a2 ──┐
  └──> step_b ─────────────┴──> merge (defer=True) ──> END
```

**When to use `defer`:**
- Asymmetric branches (different execution lengths)
- Dynamic parallelization with Send API
- Consensus/voting patterns where all inputs must arrive
- Any fan-in where branches might complete at different times

**When NOT needed:**
- Symmetric branches (same length) — LangGraph already waits for all incoming edges
- Single-step parallel branches going directly to merge

### Dynamic Parallelization with Send API

The **Send API** is for dynamic parallelization—when you want the **same node executed multiple times in parallel**, each with different inputs. Unlike static edges (fixed at compile time), Send determines the number of parallel workers at runtime based on input data.

**Static edges vs Send:**
```python
# STATIC: Fixed 3 branches defined at compile time
graph.add_edge(START, "agent_a")
graph.add_edge(START, "agent_b")
graph.add_edge(START, "agent_c")

# DYNAMIC: Variable branches determined at runtime
def fan_out(state):
    return [
        Send("worker", {"item": item})
        for item in state["items"]  # Could be 2, 10, or 100 items
    ]
graph.add_conditional_edges(START, fan_out, ["worker"])
```

**How Send works:**
- `Send("node_name", state_dict)` spawns one parallel instance of the node
- Each instance receives its own state slice (e.g., one document, one query)
- All instances run in parallel
- Results merge back via reducers

**When to use Send vs Static Edges:**

| Use Case | Approach |
|----------|----------|
| Fixed perspectives (technical, business, risk) | Static edges |
| Process list of items (documents, URLs, queries) | Send API |
| Number of workers known at design time | Static edges |
| Number of workers depends on input | Send API |

**Map-Reduce Example:**

```python
from typing import Annotated, List
import operator
from typing_extensions import TypedDict
from langgraph.types import Send
from langgraph.graph import StateGraph, START, END


class MapReduceState(TypedDict):
    items: List[str]
    results: Annotated[list, operator.add]  # Reducer for accumulation
    final_result: str


class ItemState(TypedDict):
    item: str


def fan_out_to_workers(state: MapReduceState):
    """Dynamically create parallel tasks based on input."""
    return [
        Send("process_item", {"item": item})
        for item in state["items"]
    ]


def process_item(state: ItemState) -> MapReduceState:
    """Process a single item (runs in parallel)."""
    result = f"Processed: {state['item']}"
    return {"results": [result]}


def reduce_results(state: MapReduceState) -> dict:
    """Aggregate all parallel results."""
    return {"final_result": " | ".join(state["results"])}


def create_map_reduce_graph():
    graph = StateGraph(MapReduceState)

    graph.add_node("process_item", process_item)
    graph.add_node("reduce", reduce_results, defer=True)  # ← Waits for all Send tasks

    graph.add_conditional_edges(START, fan_out_to_workers, ["process_item"])
    graph.add_edge("process_item", "reduce")
    graph.add_edge("reduce", END)

    return graph.compile()


# Usage:
# graph = create_map_reduce_graph()
# result = graph.invoke({"items": ["a", "b", "c"], "results": []})
```

**Key points:**
- `Send` creates parallel instances of the same node, each with different input
- Number of parallel workers determined by input data, not graph structure
- `defer=True` on reduce node ensures ALL Send tasks complete before aggregation
- Always pair with `Annotated[list, operator.add]` reducer for collecting results
- Import: `from langgraph.types import Send`

---

## State Management

### Reducer Strategies

**1. First Non-Empty (for independent fields)**
```python
def first_non_empty(a: str, b: str) -> str:
    return a if a else b

class State(TypedDict):
    field_a: Annotated[str, first_non_empty]
    field_b: Annotated[str, first_non_empty]
```

**2. List Accumulation (for collecting all results)**
```python
import operator

class State(TypedDict):
    all_results: Annotated[list, operator.add]

# Each branch returns:
return {"all_results": [my_result]}  # Gets appended
```

**3. Custom Merge (for complex aggregation)**
```python
def merge_analyses(a: dict, b: dict) -> dict:
    """Merge analysis dictionaries, keeping higher confidence."""
    if not a:
        return b
    if not b:
        return a
    return a if a.get("confidence", 0) > b.get("confidence", 0) else b

class State(TypedDict):
    best_analysis: Annotated[dict, merge_analyses]
```

### Avoiding Conflicts

When multiple branches update the same field:

```python
# BAD: Multiple branches writing to same field without reducer
class State(TypedDict):
    result: str  # Last writer wins - unpredictable!

# GOOD: Each branch has its own field
class State(TypedDict):
    result_a: str
    result_b: str
    result_c: str

# GOOD: Use reducer for intentional merging
class State(TypedDict):
    result: Annotated[str, first_non_empty]
```

---

## State Flow

```
Initial State:
  input_data: "Should we adopt microservices?"
  analysis_a: ""
  analysis_b: ""
  analysis_c: ""

After Fan-Out (all branches run in parallel):
  [Agent A running...]
  [Agent B running...]
  [Agent C running...]

After Fan-In (all branches complete):
  input_data: "Should we adopt microservices?"
  analysis_a: "Technical perspective..."  ← From Agent A
  analysis_b: "Business perspective..."   ← From Agent B
  analysis_c: "Risk perspective..."       ← From Agent C

  (Reducer merged updates from parallel branches)
```

---

## Pitfalls & Best Practices

**Pitfalls:**

- **State field conflicts** — Multiple branches writing to same field without reducer. Use separate fields or proper reducers.

- **Missing reducer** — Without `Annotated[type, reducer]`, parallel updates may overwrite each other unpredictably.

- **Assuming order** — Parallel branches complete in arbitrary order. Don't depend on execution sequence.

- **Resource exhaustion** — Too many parallel branches can overwhelm LLM API rate limits.

**Best Practices:**

- **Separate output fields** — Give each parallel branch its own state field to write to.

- **Use appropriate reducers** — `first_non_empty` for independent fields, `operator.add` for lists.

- **Add merge node when needed** — If results need synthesis, add explicit aggregation step.

- **Limit parallelism** — Consider rate limits when designing many-branch fan-out.

- **Async nodes** — Use `async def` for true parallel execution (sync nodes run sequentially even with fan-out edges).

---

## Comparison with Other Patterns

| Aspect | Fan-in/Fan-out | Pipeline | Router | Loop |
|--------|----------------|----------|--------|------|
| Execution | Parallel | Sequential | Branched | Cyclical |
| Result | Multiple outputs | Single chain | One path | Refined output |
| State update | Merged via reducer | Accumulated | Path-dependent | Iterative |
| Use case | Multi-perspective | Transformation | Decision tree | Refinement |
