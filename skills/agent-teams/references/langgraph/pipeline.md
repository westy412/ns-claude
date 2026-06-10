# Pipeline Pattern

## What It Is

A linear chain of agents where each agent processes state and passes it to the next. The simplest agent team structure: A → B → C.

## When to Use

- Sequential processing where order matters
- Each agent needs output from the previous agent
- Data enrichment pipelines (each agent adds to state)
- Transformation chains (input → process → format → output)
- When parallelization isn't possible or needed

## When to Avoid

- Tasks are independent and could run in parallel → use **Fan-in/Fan-out** instead
- Different paths needed based on runtime conditions → use **Router** instead
- Iterative refinement needed → use **Loop** instead
- Single agent can handle the entire task → use **Individual Agent** instead

## Graph Structure

```
START → Agent A → Agent B → Agent C → END
```

Each node:
1. Reads state from previous node
2. Performs its task
3. Updates state with its output
4. Passes to next node via direct edge

---

## LangGraph Implementation

### Code Template

```python
from typing import Annotated
import operator
from typing_extensions import TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END


# =============================================================================
# STATE DEFINITION
# =============================================================================
# State accumulates data from each agent in the pipeline.
# Each agent reads what it needs and adds its contribution.

class PipelineState(TypedDict):
    # Input
    raw_input: str

    # Agent A output
    processed_data: str

    # Agent B output
    enriched_data: str

    # Agent C output (final)
    final_output: str


# =============================================================================
# AGENT TEAM CLASS
# =============================================================================
# Encapsulates all agents in the pipeline pattern.
# Each agent method takes (self, state, name) for consistent interface.
# Node wrappers pass the name and are used in graph definition.

class PipelineAgentTeam:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    # -------------------------------------------------------------------------
    # AGENT A - PROCESSOR
    # -------------------------------------------------------------------------

    async def agent_a(self, state: PipelineState, name: str) -> dict:
        """First stage: Process raw input."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a data processor. Clean and structure the input."),
            ("user", "{raw_input}"),
        ])

        chain = prompt | self.llm
        result = await chain.ainvoke({"raw_input": state["raw_input"]})

        return {
            "processed_data": result.content,
        }

    async def agent_a_node(self, state: PipelineState) -> dict:
        """Node wrapper for agent A."""
        return await self.agent_a(state, "agent_a")

    # -------------------------------------------------------------------------
    # AGENT B - ENRICHER
    # -------------------------------------------------------------------------

    async def agent_b(self, state: PipelineState, name: str) -> dict:
        """Second stage: Enrich processed data."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a data enricher. Add context and metadata."),
            ("user", "{processed_data}"),
        ])

        chain = prompt | self.llm
        result = await chain.ainvoke({"processed_data": state["processed_data"]})

        return {
            "enriched_data": result.content,
        }

    async def agent_b_node(self, state: PipelineState) -> dict:
        """Node wrapper for agent B."""
        return await self.agent_b(state, "agent_b")

    # -------------------------------------------------------------------------
    # AGENT C - FORMATTER
    # -------------------------------------------------------------------------

    async def agent_c(self, state: PipelineState, name: str) -> dict:
        """Third stage: Format final output."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a formatter. Create the final polished output."),
            ("user", "{enriched_data}"),
        ])

        chain = prompt | self.llm
        result = await chain.ainvoke({"enriched_data": state["enriched_data"]})

        return {
            "final_output": result.content,
        }

    async def agent_c_node(self, state: PipelineState) -> dict:
        """Node wrapper for agent C."""
        return await self.agent_c(state, "agent_c")

    # -------------------------------------------------------------------------
    # GRAPH DEFINITION
    # -------------------------------------------------------------------------

    def create_graph(self):
        graph = StateGraph(PipelineState)

        # Add nodes using node wrapper methods
        graph.add_node("agent_a", self.agent_a_node)
        graph.add_node("agent_b", self.agent_b_node)
        graph.add_node("agent_c", self.agent_c_node)

        # Linear edges (the pipeline)
        graph.add_edge(START, "agent_a")
        graph.add_edge("agent_a", "agent_b")
        graph.add_edge("agent_b", "agent_c")
        graph.add_edge("agent_c", END)

        return graph.compile()

    # -------------------------------------------------------------------------
    # RUN METHOD
    # -------------------------------------------------------------------------

    async def run(self, raw_input: str) -> dict:
        """Execute the pipeline with the given input.

        Args:
            raw_input: The raw data to process through the pipeline.

        Returns:
            The final state dict containing all outputs.
        """
        # Initialize starting state (inputs only)
        initial_state = {
            "raw_input": raw_input,
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
#     agent_team = PipelineAgentTeam(llm=llm)
#
#     result = await agent_team.run("Some raw data to process")
#     print(result["final_output"])
```

### LangGraph-Specific Notes

- **Async vs Sync:** All examples use `async def` with `await chain.ainvoke()`. For synchronous execution, use `def` with `chain.invoke()` instead.
- **Class-based agents:** All agents encapsulated in a single class with `__init__` for LLM setup
- **Name argument:** Each agent method takes `(self, state, name)` for tracing and message attribution
- **Node wrappers:** `async def X_node(self, state)` calls `self.X(state, "X")` — used in graph definition
- **Direct edges:** Use `graph.add_edge(source, target)` for unconditional flow
- **State accumulation:** Each node adds to state, downstream nodes see previous outputs
- **No routing logic needed:** Pipeline is deterministic, no conditionals

---

## State Flow

```
Initial State:
  raw_input: "user data"
  processed_data: None
  enriched_data: None
  final_output: None

After Agent A:
  raw_input: "user data"
  processed_data: "cleaned data"  ← Added
  enriched_data: None
  final_output: None

After Agent B:
  raw_input: "user data"
  processed_data: "cleaned data"
  enriched_data: "enriched data"  ← Added
  final_output: None

After Agent C:
  raw_input: "user data"
  processed_data: "cleaned data"
  enriched_data: "enriched data"
  final_output: "final output"    ← Added
```

---

## Variants

### Pipeline with Shared Context

When all agents need access to common context:

```python
class PipelineState(TypedDict):
    # Shared context (read by all agents)
    context: str
    instructions: str

    # Pipeline-specific fields
    stage_1_output: str
    stage_2_output: str
    final_output: str
```

### Pipeline with Message History

When agents should see conversation history:

```python
class PipelineState(TypedDict):
    messages: Annotated[list, operator.add]  # Accumulates messages
    final_output: str

async def agent_a(state: PipelineState) -> dict:
    # Agent adds its message to history
    return {
        "messages": [AIMessage(content="Agent A processed the input")],
    }
```

---

## Pitfalls & Best Practices

**Pitfalls:**

- **Overloading state** — Don't pass entire state when agent only needs one field. Extract what's needed.

- **Missing intermediate fields** — Ensure each agent's output field exists in TypedDict before downstream agents try to read it.

- **No error handling** — If one agent fails, entire pipeline fails. Consider adding try/except in critical nodes.

**Best Practices:**

- **Clear field naming** — Name fields by stage: `stage_1_output`, `stage_2_output`, or by purpose: `processed_data`, `enriched_data`.

- **Minimal state updates** — Each node returns only the fields it modifies.

- **Document dependencies** — Comment which fields each agent reads and writes.

- **Consider validation** — Add a validation node at the end if output quality is critical.

---

## When Pipeline Isn't Enough

If you find yourself adding:
- **Conditional edges** → Consider Router pattern
- **Multiple paths from START** → Consider Fan-in/Fan-out pattern
- **Edges that loop back** → Consider Loop pattern
- **Dynamic next-node decisions** → Consider Command-based Router

Pipeline is the foundation. More complex patterns build on it.
