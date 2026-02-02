# Agent Team Documentation Template

Use this template when documenting a team orchestration pattern. Note that LangGraph is the primary framework for team orchestration, while DSPy uses module composition.

---

```markdown
# [Team Pattern Name]

## What It Is
[1-2 sentence definition of this orchestration pattern]

## When to Use
[Situations/problems that call for this pattern]
- [Situation 1]
- [Situation 2]
- [Situation 3]

## When to Avoid
[When this is the wrong choice]
- [Situation 1] — use [alternative] instead
- [Situation 2] — use [alternative] instead

## Selection Criteria
[Quick decision checklist]
- If [condition] → this pattern
- If [condition] → consider [other pattern]
- If [condition] → consider [other pattern]

## Inputs / Outputs

**Team Inputs:**
- [Input 1]: [Description]
- [Input 2]: [Description]

**Team Outputs:**
- [Output 1]: [Description]

## Termination Conditions
[What causes this team to complete]
- [Condition 1]
- [Condition 2]

## Process Flow

```
[ASCII diagram showing agent orchestration]

Example for Linear:
Input → [Agent A] → [Agent B] → [Agent C] → Output

Example for Loop:
Input → [Agent A] → [Agent B] → Condition?
                         ↑          ↓ No
                         └──────────┘
                                    ↓ Yes
                                  Output

Example for Fan-Out:
                    ┌→ [Agent B] ─┐
Input → [Agent A] ─┼→ [Agent C] ─┼→ [Aggregator] → [Agent A] → ...
                    └→ [Agent D] ─┘
```

## Agent Composition
[What types of agents typically make up this team]
- **[Role 1]:** [Agent type] — [Purpose in team]
- **[Role 2]:** [Agent type] — [Purpose in team]
- **[Role 3]:** [Agent type] — [Purpose in team]

---

## LangGraph Implementation

### State Definition (LangGraph)

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph

class TeamState(TypedDict):
    # [Field explanations]
    [field]: [type]
    [field]: [type]
```

### Graph Construction (LangGraph)

> **Note:** Inline comments are for explanation only. Remove them when using this template.

```python
# [Build the graph]
graph = StateGraph(TeamState)

# [Add nodes - reference individual agent docs for node implementations]
graph.add_node("agent_a", agent_a_function)
graph.add_node("agent_b", agent_b_function)

# [Add edges]
graph.add_edge("agent_a", "agent_b")

# [Add conditional edges if needed]
graph.add_conditional_edges(
    "agent_b",
    condition_function,
    {
        "continue": "agent_a",
        "done": END
    }
)

# [Set entry point]
graph.set_entry_point("agent_a")

# [Compile]
app = graph.compile()
```

### LangGraph-Specific Notes
- [Note about state management]
- [Note about edge conditions]
- [Note about checkpointing if relevant]

---

## DSPy Implementation

DSPy handles team-like patterns through module composition rather than explicit graphs.

### Module Composition (DSPy)

> **Note:** Inline comments are for explanation only. Remove them when using this template.

```python
import dspy

# [Individual signatures for each "agent"]
class StepASignature(dspy.Signature):
    """[Task for step A]"""
    input_field: str = dspy.InputField()
    output_field: str = dspy.OutputField()

class StepBSignature(dspy.Signature):
    """[Task for step B]"""
    input_field: str = dspy.InputField()
    output_field: str = dspy.OutputField()

# [Composed module acts as the "team"]
class TeamModule(dspy.Module):
    def __init__(self):
        self.step_a = dspy.ChainOfThought(StepASignature)
        self.step_b = dspy.ChainOfThought(StepBSignature)
    
    def forward(self, input_field: str):
        # [Sequential composition]
        result_a = self.step_a(input_field=input_field)
        result_b = self.step_b(input_field=result_a.output_field)
        return result_b
```

### DSPy Composition Patterns

**Sequential (Linear):**
```python
def forward(self, x):
    a = self.step_a(x)
    b = self.step_b(a.output)
    c = self.step_c(b.output)
    return c
```

**Conditional (Branching):**
```python
def forward(self, x):
    decision = self.router(x)
    if decision.route == "path_a":
        return self.path_a(x)
    else:
        return self.path_b(x)
```

**Loop (Iterative):**
```python
def forward(self, x, max_iterations=5):
    result = self.generator(x)
    for _ in range(max_iterations):
        critique = self.critic(result.output)
        if critique.passed:
            break
        result = self.generator(x, feedback=critique.feedback)
    return result
```

### DSPy-Specific Notes
- [Note about module composition]
- [Note about forward() method design]
- [Note about state passing between steps]

---

## Pitfalls & Best Practices

**Pitfalls:**
- [Common mistake] — [why it breaks]
- [Common mistake] — [why it breaks]

**Best Practices:**
- [Do this] — [why it works]
- [Do this] — [why it works]
```

---

## Template Field Guidance

### What It Is
- Define the orchestration pattern, not the specific use case
- Example: "A looping pattern where two agents iterate until a quality threshold is met."

### Process Flow
- Always include ASCII diagram
- Show decision points clearly
- Label branches (Yes/No, Pass/Fail, etc.)
- Show where loops return

### Agent Composition
- Reference individual agent types (links to individual-agents docs)
- Focus on ROLES not specific implementations
- Example: "Critic: Structured Output Agent — evaluates quality and returns pass/fail with feedback"

### State Management
- Document the state object structure
- Show what each agent reads/writes
- Note any state that persists across loops

### Termination Conditions
- Be explicit — this is critical for loops
- Include both success and failure terminations
- Note any max iteration limits

### Code Template
- Show the graph construction, not agent internals
- Include state definition
- Show edge definitions (including conditionals)
- Show entry and exit points
