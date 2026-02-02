# Prompt Engineering Investigation Instructions

How to find and extract prompting patterns from codebases.

---

## What You're Looking For

Prompting patterns including:
- Framework structures (One-Turn, Conversational)
- Type-specific patterns (structured output instructions, tool usage)
- Role-specific patterns (researcher, critic, generator prompts)
- Inter-agent communication (how outputs become inputs)

---

## Investigation Steps

### Step 1: Find All Prompts

**Search for prompt strings:**
```bash
grep -rn '"""' --include="*.py" | head -100
grep -r "system_prompt\|system_message\|instructions" --include="*.py"
grep -r "prompt\s*=\|PROMPT\s*=" --include="*.py"
grep -r "template\s*=" --include="*.py"
```

**Search for prompt files:**
```bash
find . -name "*.txt" -o -name "*.prompt" -o -name "*.md" | grep -i prompt
```

**DSPy-specific (signatures):**
```bash
grep -r "dspy.Signature\|InputField\|OutputField" --include="*.py"
grep -r '""".*"""' --include="*.py"  # Docstrings often contain DSPy prompts
```

**Common locations:**
- `prompts/`, `templates/`
- Inline in agent files
- Constants at top of files
- Separate config files

---

### Step 2: Identify Framework Structure

**Look for XML-style tags:**
```bash
grep -r "<.*>" --include="*.py" | grep -v "import\|#"
```

Common tags indicate frameworks:
- `<who you are>`, `<persona>` → Identity section
- `<context>`, `<knowledge_domain>` → Context section
- `<task>`, `<instructions>` → Task section
- `<output_format>`, `<output>` → Output section
- `<rules>`, `<constraints>` → Rules section
- `<inputs>` → Input definition section

**Classify the framework:**

| Indicators | Framework |
|------------|-----------|
| Single `<task>`, defined `<inputs>`, `<output_format>` | One-Turn / Structured I/O |
| `<persona>`, `<interaction_flow>`, `<capabilities>` | Conversational |

---

### Step 3: Extract Type-Specific Patterns

**Structured Output:**
Look for:
```bash
grep -r "JSON\|json\|schema\|Pydantic\|BaseModel" --include="*.py"
grep -r "response_model\|output_schema" --include="*.py"
```

In prompts, look for:
- JSON schema definitions
- Output format examples
- "Return as JSON" instructions
- Field definitions

**Tool Calling:**
Look for:
```bash
grep -r "tools\s*=\|tool_choice\|function_call" --include="*.py"
grep -r "def.*tool\|@tool" --include="*.py"
```

In prompts, look for:
- Tool descriptions
- When to use tools
- Tool selection criteria
- Tool output handling

---

### Step 4: Extract Role-Specific Patterns

Identify agent roles by examining prompts for:

| Role | Prompt Indicators |
|------|-------------------|
| Researcher | "search", "find", "gather", "investigate", "sources" |
| Analyzer | "analyze", "evaluate", "assess", "examine", "compare" |
| Generator | "create", "write", "generate", "produce", "draft" |
| Critic | "critique", "review", "score", "grade", "feedback" |
| Orchestrator | "coordinate", "decide", "route", "manage" |

For each role found, extract:
- Core directives
- Skill requirements
- Input expectations
- Output expectations

---

### Step 5: Trace Inter-Agent Communication

For multi-agent systems, trace the message flow:

**Find state/message passing:**
```bash
grep -r "state\[" --include="*.py"
grep -r "\.get\(\|\.update\(" --include="*.py"
```

**Identify transformations:**
Look for code between agents that:
- Strips fields (removing reasoning, metadata)
- Reformats output
- Combines multiple outputs
- Filters or selects content

**Document for each handoff:**
1. What Agent A outputs
2. Any transformation applied
3. What Agent B receives
4. What's in system message vs user message

---

### Step 6: Identify DSPy-Specific Patterns

DSPy uses a different prompting approach:

**Signatures:**
```python
class AgentSignature(dspy.Signature):
    """Docstring becomes the prompt instruction"""
    
    input_field: str = dspy.InputField(desc="Description")
    output_field: str = dspy.OutputField(desc="Description")
```

Extract:
- Signature class name
- Docstring (this is the main prompt)
- Input fields and descriptions
- Output fields and descriptions

**Module composition:**
```python
class Agent(dspy.Module):
    def __init__(self):
        self.step1 = dspy.ChainOfThought(Signature1)
        self.step2 = dspy.Predict(Signature2)
```

Note the composition pattern and what modules are used.

---

## Output Format

### For Framework Patterns

```
### Framework: [Name/Location]

**File:** [path]

**Type:** [One-Turn / Conversational]

**Structure Found:**
```
[The template structure with tags]
```

**Sections Identified:**
- [Section 1]: [Purpose]
- [Section 2]: [Purpose]

**Example Prompt:**
```
[Actual prompt text]
```

**Notes:**
- [Observations]
```

### For Type-Specific Patterns

```
### Type Pattern: [Type] in [Location]

**File:** [path]

**Agent Type:** [Structured Output / Tool Calling / etc.]

**Type-Specific Elements Found:**
```
[Relevant prompt sections]
```

**How Output Format is Specified:**
```
[Output format instructions]
```

**Notes:**
- [What works well]
- [Potential issues]
```

### For Role Patterns

```
### Role Pattern: [Role] in [Location]

**File:** [path]

**Role:** [Researcher / Critic / etc.]

**Core Directives Found:**
- [Directive 1]
- [Directive 2]

**Skill/Capability Framing:**
```
[Relevant prompt sections]
```

**Task Framing:**
```
[How tasks are presented]
```

**Notes:**
- [Observations]
```

### For Team Communication

```
### Communication Pattern: [From Agent] → [To Agent]

**Files:** [paths]

**Pattern Type:** [Production Line / Loop / Fan-Out]

**Agent A Output:**
```
[What A produces]
```

**Transformation (if any):**
```python
[Code that transforms]
```

**Agent B Input:**
```
[What B receives]
```

**What's Stripped/Curated:**
- [Element 1]
- [Element 2]

**Notes:**
- [Observations]
```

---

## Red Flags (Potential Anti-Patterns)

Note if you observe:
- Unstructured prompts (no clear sections)
- Missing output format specifications
- Overly long prompts (could be split)
- Hardcoded examples that should be dynamic
- Inconsistent tag usage
- No clear role definition
- Missing input/output contracts
- Passing too much context between agents
- Not stripping reasoning when appropriate

These may be candidates for "bad example" documentation.
