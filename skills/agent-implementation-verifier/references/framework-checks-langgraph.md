# LangGraph Framework Compliance Checks

> **When to read:** When the agent-config.yaml specifies `framework: langgraph`. Include this content in the framework-compliance-verifier agent's prompt.

---

## State and Graph Structure (Critical)

| Check | Status if violated |
|-------|--------------------|
| `State` is defined as a `TypedDict` with all spec inputs and outputs | FAIL |
| All node functions return a `State` dict | FAIL |
| `StateGraph` is used for graph construction | FAIL |
| Graph is compiled before use (`graph.compile()`) | FAIL |
| Graph has proper entry and exit points | FAIL |

---

## Prompt Pattern

| Check | Status if violated |
|-------|--------------------|
| `prompts.py` exists with named prompt constants | FAIL |
| Prompts use XML tags for structure | WARN |
| Prompt content aligns with agent's declared role from agent-config.yaml | WARN |
| Each agent has a corresponding prompt constant | FAIL |
| No `prompts/` directory exists (that's the DSPy pattern, not LangGraph) | FAIL |

---

## Agent Type Compliance

| Agent Type in Spec | Expected Implementation | Check |
|-------------------|------------------------|-------|
| `text-agent` | Returns text output in State | State has string output field |
| `message-agent` | Works with message lists | State has messages field |
| `structured-output-agent` | Returns structured output | Uses Pydantic model or structured output |
| `text-tool-agent` | Text agent with tool access | Has tools bound and ToolNode |
| `message-tool-agent` | Message agent with tool access | Has tools bound and ToolNode |
| `structured-output-tool-agent` | Structured output with tools | Has tools, structured output, and ToolNode |

Flag type mismatches as FAIL.

---

## ToolNode Pattern (Critical)

| Check | Status if violated |
|-------|--------------------|
| `ToolNode` is added as a SEPARATE graph node | FAIL |
| `ToolNode` is NOT created inside agent functions | FAIL |
| Tools are bound to the model via `.bind_tools()` | FAIL |
| Conditional edges route between agent node and tool node correctly | FAIL |
| Tool node routes back to the calling agent node | WARN |

---

## Model Configuration

| Check | Status if violated |
|-------|--------------------|
| Model tier matches spec (Opus preferred, Sonnet only if explicitly specified) | WARN |
| Haiku is NOT used (unless explicitly specified in spec) | FAIL |
| Model is initialized with correct provider | FAIL |
| Temperature setting matches spec | WARN |

---

## Graph Patterns by Team Type

### Pipeline
| Check | Status if violated |
|-------|--------------------|
| Nodes are connected sequentially (A -> B -> C) | FAIL |
| No conditional routing between pipeline stages | WARN |
| Each stage processes and passes state forward | FAIL |

### Router
| Check | Status if violated |
|-------|--------------------|
| Router node has conditional edges to target nodes | FAIL |
| Routing logic matches spec's routing criteria | FAIL |
| All possible routes are covered (no dead ends) | FAIL |

### Fan-in-Fan-out
| Check | Status if violated |
|-------|--------------------|
| Fan-out node sends to multiple parallel branches | FAIL |
| Fan-in node collects results from all branches | FAIL |
| State merging is handled correctly at fan-in | FAIL |

### Loop
| Check | Status if violated |
|-------|--------------------|
| Loop has a termination condition | FAIL |
| Loop body processes and updates state | FAIL |
| Maximum iteration guard exists | WARN |

---

## I/O and Data Flow

| Check | Status if violated |
|-------|--------------------|
| All spec inputs present in State TypedDict | FAIL |
| All spec outputs present in State TypedDict | FAIL |
| Inter-agent data flow uses State (not function parameters) | FAIL |
| `code-resolved` fields handled outside LLM calls | FAIL |
| `pass-through` fields preserved through the graph | WARN |

---

## Multi-Team / Nested Team

| Check | Status if violated |
|-------|--------------------|
| Each sub-team has its own `team.py` and `prompts.py` | FAIL |
| Parent team.py orchestrates sub-teams correctly | FAIL |
| Sub-team graphs are compiled independently | WARN |
| State is properly marshalled between parent and sub-team graphs | FAIL |
| Sub-teams are standalone modules (no factory function generation) | FAIL |

---

## Anti-Pattern Summary

| Anti-Pattern | Detection | Severity |
|-------------|-----------|----------|
| `prompts/` directory exists (DSPy pattern in LangGraph project) | Directory check | FAIL |
| `ToolNode` created inside agent function | Grep for `ToolNode(` inside node functions | FAIL |
| Node function doesn't return State dict | Check return type of each node function | FAIL |
| Graph not compiled | Grep for `.compile()` | FAIL |
| Haiku model used without explicit spec approval | Grep for haiku model references | FAIL |
| State fields not matching spec I/O | Compare TypedDict fields to spec | FAIL |
| Missing conditional edge handling for tools | Check graph edges after tool-using agents | FAIL |
