# Loop Pattern

## What It Is

An agent team with cyclical execution where agents iterate until a termination condition is met. Typically used for creator-critic feedback loops where output is refined through multiple passes.

## When to Use

- Iterative refinement (draft → feedback → revision)
- Quality gates before completion
- Creator-critic patterns
- Multiple approval conditions needed
- Output must meet specific criteria

## When to Avoid

- Single-pass processing is sufficient → use **Pipeline** instead
- Tasks are independent → use **Fan-in/Fan-out** instead
- Different paths based on input type → use **Router** instead
- No clear termination condition defined

## Graph Structure

### Simple Loop (2 nodes)
```
START → Creator → Critic → Creator (loop) → END
            ↑________|
```

### Complex Loop (with parallel critics)
```
START → Setup → Creator → [Critic A, B, C] → Creator (loop) → Finalize → END
                    ↑___________|
```

---

## LangGraph Implementation

### Simple Loop Template

```python
from typing import Annotated
import operator
from typing_extensions import TypedDict

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel


# =============================================================================
# STATE DEFINITION
# =============================================================================
# Separate message channels for each agent role.
#
# WHY SEPARATE CHANNELS?
# Each agent should see its OWN previous messages as AIMessage (assistant role)
# and OTHER agents' messages as HumanMessage (user role). This maintains proper
# conversation structure where the agent always "responds" to feedback rather
# than seeing a confusing mix of AI messages from different sources.
#
# - creator_messages: Creator sees its drafts as AI, feedback as Human
# - critic_messages: Critic sees its analyses as AI, drafts to review as Human

class LoopState(TypedDict):
    # Input
    task: str

    # Message channels (isolated per agent)
    creator_messages: Annotated[list[BaseMessage], operator.add]
    critic_messages: Annotated[list[BaseMessage], operator.add]

    # Loop control
    completed: bool
    attempts: int

    # Output
    final_output: str


MAX_ATTEMPTS = 6


# =============================================================================
# STRUCTURED OUTPUTS
# =============================================================================

class CreatorOutput(BaseModel):
    reasoning: str
    draft: str


class CriticOutput(BaseModel):
    analysis: str
    feedback: str
    completed: bool  # True if draft is acceptable


# =============================================================================
# AGENT TEAM CLASS
# =============================================================================
# Encapsulates all agents in the loop pattern.
# Each agent method takes (self, state, name) for consistent interface.
# Node wrappers pass the name and are used in graph definition.

class LoopAgentTeam:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    # -------------------------------------------------------------------------
    # CREATOR AGENT
    # -------------------------------------------------------------------------

    async def creator(self, state: LoopState, name: str) -> dict:
        """Generate or revise draft based on critic feedback."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a content creator. Create or revise content based on the task.
If there is previous feedback, incorporate it into your revision."""),
            ("user", "Task: {task}"),
            MessagesPlaceholder(variable_name="creator_messages"),
        ])

        chain = prompt | self.llm.with_structured_output(CreatorOutput)
        result = await chain.ainvoke({
            "task": state["task"],
            "creator_messages": state.get("creator_messages", []),
        })

        # Update both message channels
        creator_msg = AIMessage(content=f"Draft:\n{result.draft}", name=name)
        critic_msg = HumanMessage(content=f"Please review this draft:\n{result.draft}")

        return {
            "creator_messages": [creator_msg],
            "critic_messages": [critic_msg],
            "final_output": result.draft,
            "attempts": state.get("attempts", 0) + 1,
        }

    async def creator_node(self, state: LoopState) -> dict:
        """Node wrapper for creator agent."""
        return await self.creator(state, "creator")

    # -------------------------------------------------------------------------
    # CRITIC AGENT
    # -------------------------------------------------------------------------

    async def critic(self, state: LoopState, name: str) -> dict:
        """Evaluate draft and provide feedback or approve."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a quality critic. Review the draft and either:
1. Provide specific feedback for improvement (completed=false)
2. Approve the draft if it meets quality standards (completed=true)"""),
            ("user", "Please review the following draft and provide your analysis."),
            MessagesPlaceholder(variable_name="critic_messages"),
        ])

        chain = prompt | self.llm.with_structured_output(CriticOutput)
        result = await chain.ainvoke({
            "critic_messages": state.get("critic_messages", []),
        })

        # Feedback goes to creator's message channel
        if result.completed:
            feedback_msg = HumanMessage(content="Approved! The draft meets quality standards.")
        else:
            feedback_msg = HumanMessage(content=f"Feedback:\n{result.feedback}")

        critic_msg = AIMessage(content=f"Analysis: {result.analysis}\nCompleted: {result.completed}", name=name)

        return {
            "creator_messages": [feedback_msg],  # Creator sees feedback
            "critic_messages": [critic_msg],      # Critic's own history
            "completed": result.completed,
        }

    async def critic_node(self, state: LoopState) -> dict:
        """Node wrapper for critic agent."""
        return await self.critic(state, "critic")

    # -------------------------------------------------------------------------
    # ROUTER
    # -------------------------------------------------------------------------

    def loop_router(self, state: LoopState) -> str:
        """Determine next step: continue loop, retry, or end."""

        # Primary termination: critic approved
        if state.get("completed"):
            return "__end__"

        # Safety termination: max attempts reached
        if state.get("attempts", 0) >= MAX_ATTEMPTS:
            return "__end__"

        # Continue loop: back to creator
        return "creator"

    # -------------------------------------------------------------------------
    # GRAPH DEFINITION
    # -------------------------------------------------------------------------

    def create_graph(self):
        graph = StateGraph(LoopState)

        # Add nodes using node wrapper methods
        graph.add_node("creator", self.creator_node)
        graph.add_node("critic", self.critic_node)

        # Entry
        graph.add_edge(START, "creator")

        # Creator always goes to critic
        graph.add_edge("creator", "critic")

        # Critic conditionally loops back or ends
        graph.add_conditional_edges(
            source="critic",
            path=self.loop_router,
            path_map={
                "creator": "creator",  # Loop back
                "__end__": END,        # Exit
            }
        )

        return graph.compile()

    # -------------------------------------------------------------------------
    # RUN METHOD
    # -------------------------------------------------------------------------

    async def run(self, task: str) -> dict:
        """Execute the loop with the given task.

        Args:
            task: The task to complete through iterative refinement.

        Returns:
            The final state dict containing the refined output.
        """
        # Initialize starting state (inputs only)
        initial_state = {
            "task": task,
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
#     agent_team = LoopAgentTeam(llm=llm)
#
#     result = await agent_team.run("Write a haiku about programming")
#     print(f"Final output (after {result['attempts']} iterations):")
#     print(result["final_output"])
```

### LangGraph-Specific Notes

- **Async vs Sync:** All examples use `async def` with `await chain.ainvoke()`. For synchronous execution, use `def` with `chain.invoke()` instead.
- **Class-based agents:** All agents encapsulated in a single class with `__init__` for LLM setup
- **Name argument:** Each agent method takes `(self, state, name)` for tracing and message attribution
- **Node wrappers:** `async def X_node(self, state)` calls `self.X(state, "X")` — used in graph definition
- **Message channel segregation:** Each agent has its own message list via `operator.add`
- **Conditional edges create loops:** Use `add_conditional_edges` with path that returns to earlier node
- **Safety counter:** Always include `attempts` field and `MAX_ATTEMPTS` check
- **Completion flag:** Primary termination via `completed: bool` field

---

## Complex Loop: Multi-Critic Pattern

When one creator needs approval from multiple critics:

```python
import asyncio
from typing import Annotated
import operator
from typing_extensions import TypedDict

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel


# =============================================================================
# STATE DEFINITION
# =============================================================================
# WHY SEPARATE CHANNELS?
# Each agent should see its OWN previous messages as AIMessage (assistant role)
# and OTHER agents' messages as HumanMessage (user role). This maintains proper
# conversation structure where the agent always "responds" rather than seeing
# a confusing mix of AI messages from different sources.

class MultiCriticState(TypedDict):
    # Input
    task: str

    # Creator messages
    creator_messages: Annotated[list[BaseMessage], operator.add]

    # Separate channels for each critic
    critic_a_messages: Annotated[list[BaseMessage], operator.add]
    critic_b_messages: Annotated[list[BaseMessage], operator.add]
    critic_c_messages: Annotated[list[BaseMessage], operator.add]

    # Individual completion flags
    critic_a_completed: bool
    critic_b_completed: bool
    critic_c_completed: bool

    # Master completion (all critics must approve)
    completed: bool
    attempts: int

    # Output
    final_output: str


MAX_ATTEMPTS = 6


# =============================================================================
# STRUCTURED OUTPUTS
# =============================================================================

class CriticOutput(BaseModel):
    analysis: str
    feedback: str
    completed: bool


# =============================================================================
# AGENT TEAM CLASS
# =============================================================================

class MultiCriticAgentTeam:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    # -------------------------------------------------------------------------
    # CREATOR AGENT
    # -------------------------------------------------------------------------

    async def creator(self, state: MultiCriticState, name: str) -> dict:
        """Generate or revise draft based on combined critic feedback."""
        # Implementation similar to simple loop creator
        # ...
        pass

    async def creator_node(self, state: MultiCriticState) -> dict:
        """Node wrapper for creator agent."""
        return await self.creator(state, "creator")

    # -------------------------------------------------------------------------
    # INDIVIDUAL CRITIC AGENTS
    # -------------------------------------------------------------------------
    # Each critic returns a dict with 'message' as a formatted string
    # containing all analysis fields. This string is used both for the
    # critic's own history AND to share with other critics.

    async def critic_a(self, state: MultiCriticState, name: str) -> dict:
        """Critic A: Focus on technical accuracy."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a technical accuracy critic. Focus on factual correctness."),
            ("user", "Please review the draft for technical accuracy."),
            MessagesPlaceholder(variable_name="critic_a_messages"),
        ])

        chain = prompt | self.llm.with_structured_output(CriticOutput)
        result = await chain.ainvoke({
            "critic_a_messages": state.get("critic_a_messages", []),
        })

        # Build message as string amalgamation of all fields
        message = f"""
# Technical Accuracy Critic:
Analysis: {result.analysis}
---
Feedback: {result.feedback}
---
Completed: {result.completed}
        """

        return {
            "completed": result.completed,
            "feedback": result.feedback,
            "message": message,
            "name": name,
        }

    async def critic_b(self, state: MultiCriticState, name: str) -> dict:
        """Critic B: Focus on clarity and style."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a clarity and style critic. Focus on readability."),
            ("user", "Please review the draft for clarity and style."),
            MessagesPlaceholder(variable_name="critic_b_messages"),
        ])

        chain = prompt | self.llm.with_structured_output(CriticOutput)
        result = await chain.ainvoke({
            "critic_b_messages": state.get("critic_b_messages", []),
        })

        message = f"""
# Clarity Critic:
Analysis: {result.analysis}
---
Feedback: {result.feedback}
---
Completed: {result.completed}
        """

        return {
            "completed": result.completed,
            "feedback": result.feedback,
            "message": message,
            "name": name,
        }

    async def critic_c(self, state: MultiCriticState, name: str) -> dict:
        """Critic C: Focus on completeness."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a completeness critic. Ensure nothing is missing."),
            ("user", "Please review the draft for completeness."),
            MessagesPlaceholder(variable_name="critic_c_messages"),
        ])

        chain = prompt | self.llm.with_structured_output(CriticOutput)
        result = await chain.ainvoke({
            "critic_c_messages": state.get("critic_c_messages", []),
        })

        message = f"""
# Completeness Critic:
Analysis: {result.analysis}
---
Feedback: {result.feedback}
---
Completed: {result.completed}
        """

        return {
            "completed": result.completed,
            "feedback": result.feedback,
            "message": message,
            "name": name,
        }

    # -------------------------------------------------------------------------
    # PARALLEL CRITIC EXECUTION NODE
    # -------------------------------------------------------------------------

    async def critics_node(self, state: MultiCriticState) -> dict:
        """Run all critics in parallel, aggregate feedback."""

        # Launch critics in parallel with their names
        tasks = [
            self.critic_a(state, "critic_a"),
            self.critic_b(state, "critic_b"),
            self.critic_c(state, "critic_c"),
        ]

        result_a, result_b, result_c = await asyncio.gather(*tasks)

        # Check if ALL critics are satisfied
        all_completed = (
            result_a["completed"] and
            result_b["completed"] and
            result_c["completed"]
        )

        # Aggregate feedback for creator (only include critics with feedback)
        if all_completed:
            combined_feedback = "All critics have approved your draft!"
        else:
            feedback_parts = []
            if not result_a["completed"]:
                feedback_parts.append(f"# {result_a['name']}:\n{result_a['feedback']}")
            if not result_b["completed"]:
                feedback_parts.append(f"# {result_b['name']}:\n{result_b['feedback']}")
            if not result_c["completed"]:
                feedback_parts.append(f"# {result_c['name']}:\n{result_c['feedback']}")
            combined_feedback = "\n\n".join(feedback_parts)

        # Cross-pollination: each critic sees other critics' feedback
        other_critics_snippet = "Here is the feedback from the other critics:"

        return {
            # Creator sees aggregated feedback as HumanMessage
            "creator_messages": [HumanMessage(content=combined_feedback)],

            # Each critic sees:
            # 1. Its own message as AIMessage (it produced this)
            # 2. Other critics' messages as HumanMessage (cross-pollination)
            "critic_a_messages": [
                AIMessage(content=result_a["message"]),
                HumanMessage(content=f"{other_critics_snippet}\n{result_b['message']}\n{result_c['message']}"),
            ],
            "critic_b_messages": [
                AIMessage(content=result_b["message"]),
                HumanMessage(content=f"{other_critics_snippet}\n{result_a['message']}\n{result_c['message']}"),
            ],
            "critic_c_messages": [
                AIMessage(content=result_c["message"]),
                HumanMessage(content=f"{other_critics_snippet}\n{result_a['message']}\n{result_b['message']}"),
            ],

            "critic_a_completed": result_a["completed"],
            "critic_b_completed": result_b["completed"],
            "critic_c_completed": result_c["completed"],
            "completed": all_completed,
        }

    # -------------------------------------------------------------------------
    # ROUTER
    # -------------------------------------------------------------------------

    def multi_critic_router(self, state: MultiCriticState) -> str:
        """Check if all critics are satisfied."""

        # All critics must be completed
        if (state.get("critic_a_completed") and
            state.get("critic_b_completed") and
            state.get("critic_c_completed")):
            return "__end__"

        # Safety limit
        if state.get("attempts", 0) >= MAX_ATTEMPTS:
            return "__end__"

        # Continue loop
        return "creator"

    # -------------------------------------------------------------------------
    # GRAPH DEFINITION
    # -------------------------------------------------------------------------

    def create_graph(self):
        graph = StateGraph(MultiCriticState)

        # Add nodes using node wrapper methods
        graph.add_node("creator", self.creator_node)
        graph.add_node("critics", self.critics_node)

        graph.add_edge(START, "creator")
        graph.add_edge("creator", "critics")

        graph.add_conditional_edges(
            source="critics",
            path=self.multi_critic_router,
            path_map={
                "creator": "creator",
                "__end__": END,
            }
        )

        return graph.compile()

    # -------------------------------------------------------------------------
    # RUN METHOD
    # -------------------------------------------------------------------------

    async def run(self, task: str) -> dict:
        """Execute the multi-critic loop with the given task.

        Args:
            task: The task to complete through iterative refinement.

        Returns:
            The final state dict containing the refined output.
        """
        # Initialize starting state (inputs only)
        initial_state = {
            "task": task,
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
#     agent_team = MultiCriticAgentTeam(llm=llm)
#
#     result = await agent_team.run("Write a technical blog post")
#     print(f"Final output (after {result['attempts']} iterations):")
#     print(result["final_output"])
```

---

## Key Patterns

### 1. Message Channel Segregation

Prevent context pollution by giving each agent its own message list:

```python
class State(TypedDict):
    creator_messages: Annotated[list[BaseMessage], operator.add]
    critic_messages: Annotated[list[BaseMessage], operator.add]
```

Each agent only sees its relevant history via `MessagesPlaceholder`.

### 2. Cross-Pollination

Let agents see each other's feedback:

```python
return {
    "creator_messages": [combined_feedback],  # Creator sees all feedback
    "critic_a_messages": [
        own_message,
        HumanMessage(content=f"Other critics said: {critic_b_msg}, {critic_c_msg}")
    ],
}
```

### 3. Multi-Flag Termination

Require multiple conditions to be satisfied:

```python
def router(state: State) -> str:
    if (state["critic_a_completed"] and
        state["critic_b_completed"] and
        state["critic_c_completed"]):
        return "__end__"
    return "creator"
```

### 4. Safety Counter

Prevent infinite loops:

```python
MAX_ATTEMPTS = 6

def router(state: State) -> str:
    if state.get("completed"):
        return "__end__"
    if state.get("attempts", 0) >= MAX_ATTEMPTS:
        return "__end__"  # Force exit
    return "continue"
```

### 5. Internal Retry Loop

Guarantee structured output before continuing:

```python
async def agent_with_retry(state: State) -> dict:
    attempts = 0
    while attempts < 3:
        try:
            result = await chain.ainvoke(state)
            parsed = result.model_dump()
            return {"output": parsed}
        except Exception as e:
            attempts += 1
            if attempts >= 3:
                raise Exception(f"Failed after {attempts} attempts")
            # Inject schema reminder and retry
            prompt.append(("user", f"Error: {e}. Schema: {schema}"))
```

---

## State Flow

```
Iteration 1:
  attempts: 0 → 1
  creator_messages: [] → [AI: "Draft v1"]
  critic_messages: [] → [Human: "Review draft v1", AI: "Feedback: improve X"]
  completed: False
  ↓
  [Router: completed=False, attempts<6 → "creator"]

Iteration 2:
  attempts: 1 → 2
  creator_messages: [..., Human: "Feedback: improve X", AI: "Draft v2"]
  critic_messages: [..., Human: "Review draft v2", AI: "Approved!"]
  completed: True
  final_output: "Draft v2"
  ↓
  [Router: completed=True → "__end__"]
```

---

## Pre/Post-Loop Pipeline

Combine setup and finalization with the loop:

```python
def create_full_workflow():
    graph = StateGraph(State)

    # Pre-loop setup
    graph.add_node("setup", setup_node)

    # Loop nodes
    graph.add_node("creator", creator_node)
    graph.add_node("critic", critic_node)

    # Post-loop finalization
    graph.add_node("finalize", finalize_node)

    # Setup phase
    graph.add_edge(START, "setup")
    graph.add_edge("setup", "creator")

    # Loop phase
    graph.add_edge("creator", "critic")
    graph.add_conditional_edges(
        source="critic",
        path=loop_router,
        path_map={
            "creator": "creator",
            "__end__": "finalize",  # Exit to finalization, not END
        }
    )

    # Finalization phase
    graph.add_edge("finalize", END)

    return graph.compile()
```

**Flow:**
```
START → setup → creator ↔ critic → finalize → END
```

---

## Pitfalls & Best Practices

**Pitfalls:**

- **No safety limit** — Missing `MAX_ATTEMPTS` check can cause infinite loops if completion condition is never met.

- **Single message channel** — Using one message list for all agents causes context pollution. Each agent sees irrelevant history.

- **Silent termination** — When safety limit triggers, final output may be incomplete. Consider logging or returning partial result.

- **Missing completion flag** — If critic never sets `completed=True`, loop runs until safety limit.

**Best Practices:**

- **Always include safety counter** — `attempts` field + `MAX_ATTEMPTS` check in router.

- **Segregate message channels** — Each agent role gets its own message list with `operator.add`.

- **Clear termination conditions** — Document when `completed` becomes True.

- **Increment attempts correctly** — Only increment on actual iterations, not on every state update.

- **Use structured output for critic** — Ensures `completed` flag is always present and typed.

---

## Comparison with Other Patterns

| Aspect | Loop | Pipeline | Router | Fan-in/Fan-out |
|--------|------|----------|--------|----------------|
| Flow | Cyclical | Linear | Branched | Parallel |
| Termination | Condition-based | End of chain | Path completion | All branches done |
| State | Iteratively refined | Accumulated | Path-dependent | Merged via reducer |
| Use case | Quality refinement | Transformation | Decision routing | Multi-perspective |
