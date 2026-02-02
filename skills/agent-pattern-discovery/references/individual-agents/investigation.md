# Individual Agent Investigation Instructions

How to find and extract agent patterns from codebases.

---

## What You're Looking For

Individual agents — discrete units that:
- Receive input
- Process (usually via LLM)
- Produce output
- May or may not use tools

**Agent Types to Identify (6-Type Taxonomy):**

Classification is based on **Output Format** × **Tool Usage**:

| Type | Output | Tools | Indicators |
|------|--------|-------|------------|
| Text Agent | Raw string | No | `result.content` returned, no `.bind_tools()` |
| Message Agent | Message object | No | Returns `AIMessage`, uses `MessagesPlaceholder` |
| Structured Output Agent | Pydantic model | No | `.with_structured_output(Schema)`, no tools |
| Text + Tool Agent | Raw string | Yes | `.bind_tools()` present, returns `result.content` |
| Message + Tool Agent | Message object | Yes | `.bind_tools()` + `MessagesPlaceholder` for history |
| Structured Output + Tool Agent | Pydantic model | Yes | Both `.bind_tools()` AND `.with_structured_output()` |

---

## Step 1: Identify Framework

First, determine which framework is used:

**LangGraph Detection:**
```bash
grep -r "from langgraph" --include="*.py"
grep -r "StateGraph\|add_node" --include="*.py"
grep -r "from langchain" --include="*.py"
```

**DSPy Detection:**
```bash
grep -r "import dspy\|from dspy" --include="*.py"
grep -r "dspy.Module\|dspy.Signature" --include="*.py"
```

Once identified, follow the appropriate section below.

---

## LangGraph Agent Investigation

### Finding LangGraph Agents

**Search patterns:**
```bash
grep -r "\.add_node\|def .*node\|def .*agent" --include="*.py"
grep -r "def .*\(state\)" --include="*.py"
grep -r "ChatOpenAI\|ChatAnthropic\|llm\.invoke" --include="*.py"
```

**LangGraph agents are typically:**
- Functions that take state dict/TypedDict, return updated state
- Classes with `__call__` or `invoke` methods
- Functions registered via `.add_node()`

### LangGraph Agent Structure

```python
# Typical LangGraph agent pattern
def agent_name(state: StateType) -> StateType:
    # 1. Extract inputs from state
    input_data = state["field_name"]
    
    # 2. Build prompt
    prompt = f"..."
    
    # 3. Invoke LLM
    response = llm.invoke(prompt)
    
    # 4. Return updated state
    return {"output_field": response.content}
```

### What to Extract (LangGraph)

| Element | Where to Find |
|---------|---------------|
| Inputs | State fields accessed at start of function |
| Outputs | Dict keys returned by function |
| Prompt | String building, template formatting |
| LLM Config | `ChatOpenAI()`, `ChatAnthropic()` instantiation |
| Tools | `tools=` parameter, `bind_tools()` calls |
| Output Schema | `with_structured_output()`, `response_model` |

### LangGraph Type Indicators (6-Type Taxonomy)

| Type | Code Indicators |
|------|-----------------|
| Text Agent | `chain = prompt \| self.llm`, returns `result.content` as string, no tools |
| Message Agent | Uses `MessagesPlaceholder`, returns message objects, no tools |
| Structured Output Agent | `.with_structured_output(Schema)`, returns Pydantic model, no tools |
| Text + Tool Agent | `llm.bind_tools([...])`, returns `result.content` after tool execution |
| Message + Tool Agent | `llm.bind_tools([...])` + `MessagesPlaceholder`, message history preserved |
| Structured Output + Tool Agent | Both `.bind_tools()` AND `.with_structured_output()` |

**Additional Indicators:**
| Pattern | What It Indicates |
|---------|-------------------|
| `Command(goto=..., update=...)` | Dynamic routing (any agent type can use this) |
| Retry loop with schema injection | Structured Output pattern (production-ready) |
| `MessagesPlaceholder("messages")` | Message-based agent (conversation history) |
| `result.tool_calls` checking | Tool-using agent |

---

## DSPy Agent Investigation

> **⚠️ UNVALIDATED:** The DSPy patterns and examples below are based on framework documentation and model knowledge. They have NOT been validated against real codebase implementations. When analyzing DSPy codebases, verify patterns against actual code before documenting.

### Finding DSPy Agents

**Search patterns:**
```bash
grep -r "class.*dspy.Module" --include="*.py"
grep -r "class.*dspy.Signature" --include="*.py"
grep -r "dspy.Predict\|dspy.ChainOfThought\|dspy.ReAct" --include="*.py"
```

**DSPy agents are typically:**
- Classes inheriting from `dspy.Module`
- Have a `forward()` method
- Use predictors: `dspy.Predict`, `dspy.ChainOfThought`, `dspy.ReAct`

### DSPy Agent Structure

```python
# Signature defines I/O contract
class AgentSignature(dspy.Signature):
    """Docstring becomes the task instruction."""
    
    input_field: str = dspy.InputField(desc="Description of input")
    output_field: str = dspy.OutputField(desc="Description of output")

# Module defines execution logic
class AgentModule(dspy.Module):
    def __init__(self):
        self.predictor = dspy.ChainOfThought(AgentSignature)
    
    def forward(self, input_field: str) -> str:
        result = self.predictor(input_field=input_field)
        return result.output_field
```

### What to Extract (DSPy)

| Element | Where to Find |
|---------|---------------|
| Inputs | `dspy.InputField` definitions in Signature |
| Outputs | `dspy.OutputField` definitions in Signature |
| Prompt | Signature docstring + field descriptions |
| Predictor Type | `dspy.Predict`, `dspy.ChainOfThought`, `dspy.ReAct` |
| Tools | `dspy.ReAct` with tool definitions |

### DSPy Type Indicators (6-Type Taxonomy)

> **⚠️ Note:** These indicators are theoretical and need validation against real DSPy implementations.

| Type | Code Indicators |
|------|-----------------|
| Text Agent | `dspy.Predict(Signature)`, single string `OutputField` |
| Message Agent | String history field, conversational signature |
| Structured Output Agent | `dspy.TypedPredictor`, multiple typed `OutputField`s |
| Text + Tool Agent | `dspy.ReAct(Signature, tools=[...])`, string output |
| Message + Tool Agent | `dspy.ReAct` with history handling |
| Structured Output + Tool Agent | `dspy.ReAct` with typed output fields |

**DSPy Predictor Types:**
| Predictor | Use Case |
|-----------|----------|
| `dspy.Predict` | Simple single-turn (Text Agent) |
| `dspy.ChainOfThought` | Reasoning tasks (any output type) |
| `dspy.TypedPredictor` | Structured output with Pydantic |
| `dspy.ReAct` | Tool-using agents (any output type) |

### DSPy-Specific Patterns

**Signature patterns:**
```bash
grep -rA 10 "class.*Signature" --include="*.py"
```

**Field descriptions (critical for prompting):**
```bash
grep -r "InputField\|OutputField" --include="*.py"
```

**Module composition:**
```bash
grep -r "def forward" --include="*.py"
```

---

### Step 3: Extract Agent Information

For each agent found, extract:

**1. Location**
- File path
- Line numbers (approximate)

**2. Agent Type (6-Type Classification)**

Determine by examining two dimensions:

**Dimension 1: Output Format**
| Check | Output Type |
|-------|-------------|
| Returns `result.content` as string | Text |
| Returns message object, uses `MessagesPlaceholder` | Message |
| Uses `.with_structured_output(Schema)` | Structured Output |

**Dimension 2: Tool Usage**
| Check | Tool Status |
|-------|-------------|
| Has `.bind_tools()` or tool definitions | With Tools |
| No tool binding | No Tools |

**Final Classification:**
| Output | No Tools | With Tools |
|--------|----------|------------|
| Text | Text Agent | Text + Tool Agent |
| Message | Message Agent | Message + Tool Agent |
| Structured | Structured Output Agent | Structured Output + Tool Agent |

**3. Inputs**

Look at:
- Function parameters
- State fields accessed
- DSPy InputField definitions
- Pydantic model fields for input

**4. Outputs**

Look at:
- Return type hints
- State fields modified
- DSPy OutputField definitions
- Pydantic model for output
- `response_model` parameter

**5. Prompt**

Prompts are typically found as:
- Triple-quoted strings (`"""..."""`)
- Variables named: `prompt`, `system_prompt`, `system_message`, `instructions`, `template`
- f-strings with placeholders
- DSPy Signature docstrings
- Separate prompt files (`.txt`, `.md`, `.prompt`)

Search patterns:
```bash
grep -r "system_prompt\|system_message\|instructions\s*=" --include="*.py"
grep -rn '"""' --include="*.py" | head -50
```

**6. LLM Configuration**

Look for:
- Model name (`gpt-4`, `claude`, etc.)
- Temperature settings
- Max tokens
- Other parameters

---

### Step 4: Identify Patterns

For each agent, note:

**Structure Pattern:**
- How is the agent organized? (single function, class, etc.)
- How is the prompt structured? (XML tags, sections, etc.)
- How are inputs injected into the prompt?

**Output Pattern:**
- How is output extracted/parsed?
- Any post-processing?
- Error handling?

**Tool Pattern (if applicable):**
- How are tools defined?
- How are tool results handled?
- Any tool selection logic?

---

## Output Format

Report findings with framework-specific sections:

### For LangGraph Agents

```
### Agent: [Name/Function Name]

**Framework:** LangGraph

**Location:** [file:line]

**Type Assessment:** [Structured Output / Tool Agent / etc.]

**Evidence:**
- [Why I think this type]
- [Key indicators found]

**State Access:**
- Reads: [state fields accessed]
- Writes: [state fields returned]

**Prompt Found:**
\`\`\`
[Prompt text or summary if too long]
\`\`\`

**LLM Configuration:**
- Model: [model name]
- Temperature: [if found]
- Other: [relevant config]

**Code Snippet:**
\`\`\`python
[Key code showing the pattern]
\`\`\`

**Notes:**
- [Anything notable]
- [Questions for user]
```

### For DSPy Agents

```
### Agent: [Name/Module Name]

**Framework:** DSPy

**Location:** [file:line]

**Type Assessment:** [Structured Output / ChainOfThought / ReAct / etc.]

**Signature:**
\`\`\`python
class [SignatureName](dspy.Signature):
    """[Docstring]"""
    [fields]
\`\`\`

**Predictor Type:** [Predict / ChainOfThought / ReAct / etc.]

**Inputs:**
- [field]: [description from InputField]

**Outputs:**
- [field]: [description from OutputField]

**Module Structure:**
\`\`\`python
[forward() method code]
\`\`\`

**Notes:**
- [Anything notable]
- [Questions for user]
```

---

## Common File Locations

| What | Common Locations |
|------|------------------|
| Agent definitions | `agents/`, `nodes/`, `chains/`, root `.py` files |
| Prompts | `prompts/`, inline in agent files, `templates/` |
| Schemas/Models | `models/`, `schemas/`, `types/` |
| Tools | `tools/`, inline in agent files |
| Graph/Orchestration | `graph.py`, `workflow.py`, `pipeline.py`, `main.py` |

---

## Red Flags (Potential Anti-Patterns)

Note if you observe:
- Prompts with no structure (wall of text)
- Missing type hints on inputs/outputs
- Hardcoded values that should be parameters
- No error handling
- Overly complex single agents (should be split)
- Prompt and logic mixed together messily
- Structured output without retry logic (fragile)
- Tool agents without iteration limits (infinite loops)

These may be candidates for "bad example" documentation.

---

## Reference Documentation

For detailed documentation of each agent type with code templates, see:

**Corpus Location:** `/Users/georgewestbrook/Programming/novosapien/agent-patterns/`

- `individual-agents/overview.md` — 6-type taxonomy overview
- `individual-agents/text-agent.md` — Text Agent documentation
- `individual-agents/message-agent.md` — Message Agent documentation
- `individual-agents/structured-output-agent.md` — Structured Output Agent documentation
- `individual-agents/text-tool-agent.md` — Text + Tool Agent documentation
- `individual-agents/message-tool-agent.md` — Message + Tool Agent documentation
- `individual-agents/structured-output-tool-agent.md` — Structured Output + Tool Agent documentation
- `notes/command-pattern.md` — Command return pattern for dynamic routing
- `analyzed-files.md` — Index of analyzed files with gold standard examples
