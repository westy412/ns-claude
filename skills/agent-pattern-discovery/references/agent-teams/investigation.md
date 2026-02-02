# Agent Team Investigation Instructions

How to find and extract team orchestration patterns from codebases.

---

## What You're Looking For

Agent teams — orchestrated groups of agents that:
- Coordinate multiple agents
- Pass state between agents
- Have defined flow (linear, loop, conditional)
- Produce a combined output

**Team Patterns to Identify:**
| Pattern | Indicators |
|---------|------------|
| Linear / Production Line | Sequential flow, no cycles |
| Two-Agent Loop | Two steps with cycle, condition to exit |
| Fan-Out / Aggregate | One step fans to multiple, then converge |
| Conditional Branching | Different paths based on state |
| Hybrid | Combination of above |

---

## Step 1: Identify Framework

**LangGraph Detection:**
```bash
grep -r "StateGraph\|from langgraph" --include="*.py"
grep -r "\.add_node\|\.add_edge\|\.compile" --include="*.py"
```

**DSPy Detection:**
```bash
grep -r "import dspy\|from dspy" --include="*.py"
grep -r "class.*dspy.Module" --include="*.py"
```

Once identified, follow the appropriate section below.

---

## LangGraph Team Investigation

LangGraph uses explicit graph-based orchestration with StateGraph.

### Finding LangGraph Teams

**Search patterns:**
```bash
grep -r "StateGraph\|from langgraph" --include="*.py"
grep -r "\.add_node\|\.add_edge\|\.compile" --include="*.py"
```

**Common locations:**
- `graph.py`, `workflow.py`, `pipeline.py`
- `main.py`, `app.py`
- `orchestration/`, `flows/`

### Map the LangGraph Structure

**Find State Definition:**
```bash
grep -r "TypedDict\|class.*State\|BaseModel" --include="*.py"
```

State is typically:
- A `TypedDict` with fields for each piece of data
- A Pydantic `BaseModel`
- Defines what flows between agents

**Find All Nodes:**
```bash
grep -r "\.add_node" --include="*.py"
```

Extract:
- Node name
- Function/class it points to
- Location of that function/class

**Find All Edges:**
```bash
grep -r "\.add_edge\|\.add_conditional_edges" --include="*.py"
```

Extract:
- Source node
- Target node
- Condition (if conditional)

**Find Entry and Exit:**
```bash
grep -r "START\|END\|set_entry_point\|set_finish_point" --include="*.py"
```

### Identify LangGraph Pattern

Draw the flow based on edges:

**Linear Pattern:**
- All edges are sequential
- No node appears as target more than once
- No cycles
```
START → A → B → C → END
```

**Two-Agent Loop:**
- Exactly two main nodes
- Edges form a cycle between them
- Conditional edge to exit
```
START → A → B → (condition) → A (loop back) OR END
```

**Fan-Out / Aggregate:**
- One node has edges to multiple targets
- Multiple nodes converge to one aggregator
```
A → [B, C, D] → Aggregator → ...
```

**Conditional Branching:**
- Uses `add_conditional_edges()`
- Different paths based on state
```
A → (if X) → B
  → (if Y) → C
  → (else) → D
```

### What to Extract (LangGraph)

| Element | Where to Find |
|---------|---------------|
| State Definition | `TypedDict` or `BaseModel` class |
| Nodes | `.add_node()` calls |
| Edges | `.add_edge()` and `.add_conditional_edges()` calls |
| Entry Point | `set_entry_point()` or `START` |
| Exit Points | `END` references |
| Conditions | Functions passed to `add_conditional_edges()` |

---

## DSPy Team Investigation

DSPy uses module composition rather than explicit graphs. "Teams" are modules that compose other modules.

### Finding DSPy Teams

**Search patterns:**
```bash
grep -r "class.*dspy.Module" --include="*.py"
grep -r "def forward" --include="*.py"
```

Look for modules that:
- Instantiate multiple other modules/predictors in `__init__`
- Call multiple predictors in sequence in `forward()`
- Have conditional logic or loops in `forward()`

### DSPy Team Structure

**Simple Composition (Linear):**
```python
class TeamModule(dspy.Module):
    def __init__(self):
        self.step_a = dspy.ChainOfThought(SignatureA)
        self.step_b = dspy.ChainOfThought(SignatureB)
    
    def forward(self, x):
        a = self.step_a(input=x)
        b = self.step_b(input=a.output)
        return b
```

**Loop Pattern:**
```python
def forward(self, x):
    result = self.generator(x)
    for i in range(self.max_iterations):
        critique = self.critic(result.output)
        if critique.passed:
            break
        result = self.refiner(x, feedback=critique.feedback)
    return result
```

**Conditional Pattern:**
```python
def forward(self, x):
    decision = self.router(x)
    if decision.route == "option_a":
        return self.handler_a(x)
    else:
        return self.handler_b(x)
```

### What to Extract (DSPy)

| Element | Where to Find |
|---------|---------------|
| Sub-modules | `__init__` method assignments |
| Flow | `forward()` method logic |
| Signatures | Classes inheriting `dspy.Signature` |
| Predictor Types | `dspy.Predict`, `dspy.ChainOfThought`, etc. |
| Loops | `for`/`while` in `forward()` |
| Conditions | `if`/`else` in `forward()` |

### Identify DSPy Pattern

| Pattern | forward() Indicators |
|---------|---------------------|
| Linear | Sequential calls: `a = step1(); b = step2(a)` |
| Loop | `for`/`while` with break condition |
| Conditional | `if`/`else` branching to different predictors |
| Fan-Out | Multiple independent calls, results combined |

---

## Output Format

### For LangGraph Teams

```
### Team: [Name/File Name]

**Framework:** LangGraph

**Location:** [file:line]

**Pattern Assessment:** [Linear / Loop / Fan-Out / Hybrid]

**Flow Diagram:**
\`\`\`
[ASCII diagram]
\`\`\`

**State Definition:**
\`\`\`python
[State TypedDict or model]
\`\`\`

**Nodes:**

| Node | Agent Type | Reads | Writes |
|------|------------|-------|--------|
| [name] | [type] | [fields] | [fields] |

**Edges:**
- `A → B` (unconditional)
- `B → A` (if not complete)
- `B → END` (if complete)

**Termination:**
- [Condition 1]
- [Condition 2]

**Inter-Agent Communication:**
- [How outputs are passed]
- [Any transformations]

**Code Snippet:**
\`\`\`python
[Graph construction code]
\`\`\`

**Notes:**
- [Anything notable]
- [Questions for user]
```

### For DSPy Teams

```
### Team: [Name/Module Name]

**Framework:** DSPy

**Location:** [file:line]

**Pattern Assessment:** [Linear / Loop / Conditional / Hybrid]

**Flow Diagram:**
\`\`\`
[ASCII diagram]
\`\`\`

**Sub-Modules:**

| Module | Type | Purpose |
|--------|------|---------|
| [name] | [Predict/ChainOfThought/etc.] | [what it does] |

**Signatures Used:**
\`\`\`python
[Signature definitions]
\`\`\`

**Forward Method:**
\`\`\`python
[forward() implementation]
\`\`\`

**Termination (if loop):**
- [Condition 1]
- [Max iterations]

**Data Flow:**
- [How outputs pass between steps]
- [Any transformations]

**Notes:**
- [Anything notable]
- [Questions for user]
```

---

## Common File Locations

| What | Common Locations |
|------|------------------|
| LangGraph graphs | `graph.py`, `workflow.py`, `pipeline.py`, `main.py` |
| LangGraph state | Same file, or `state.py`, `models.py`, `types.py` |
| DSPy modules | `modules/`, `agents/`, root `.py` files |
| DSPy signatures | `signatures/`, same file as module |
| Individual agents | `agents/`, `nodes/`, referenced from orchestration |

---

## Red Flags (Potential Anti-Patterns)

**LangGraph:**
- Overly complex graphs (too many nodes for the task)
- Missing termination conditions (infinite loops)
- State pollution (fields that shouldn't be there)
- Tight coupling (agents that know too much about each other)
- No error handling paths
- Missing conditional edges where needed

**DSPy:**
- Overly long `forward()` methods (should decompose)
- Missing loop termination conditions
- Too many predictors in one module (should split)
- Ignoring predictor outputs (wasted computation)
- No type hints on forward parameters/returns

These may be candidates for "bad example" documentation.
