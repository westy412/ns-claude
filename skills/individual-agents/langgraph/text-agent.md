# Text Agent

## What It Is

A single-turn LLM call that returns raw text output. The most fundamental building block for any workflow, designed for maximum simplicity when structured output is not required.

## When to Use

- Drafting content (emails, reports, summaries)
- Generating human-readable explanations
- Creating flexible-format output (plain text, markdown)
- Simple agent-to-agent communication
- Any task where output is for human consumption

## When to Avoid

- Output must be programmatically parsed — use **Structured Output Agent** instead
- Output needs to maintain conversation history — use **Message Agent** instead
- Agent needs to call external tools — use **Text + Tool Agent** instead
- Format must be strictly validated — use **Structured Output Agent** instead

## Selection Criteria

- If output is for human reading and format is flexible → **Text Agent**
- If output needs parsing or validation → consider **Structured Output Agent**
- If building a conversation flow → consider **Message Agent**
- If agent needs to take actions → consider **Text + Tool Agent**

## Inputs / Outputs

**Inputs:**
- State fields containing context/data for the prompt
- Prompt template (system message + user input)

**Outputs:**
- Single string (accessed via `result.content`)
- Updates one state field with the text output

## Prompting Guidelines

Since there's no schema validation, prompt quality is critical:

- Be extremely specific about the desired task and output
- If a format is desired (markdown, bullet points), explicitly request it with examples
- For agent-to-agent communication, request concise responses to prevent "chatbot drift"
- Avoid ambiguous instructions that could lead to inconsistent outputs
- Include examples in the prompt for nuanced tasks

---

## LangGraph Implementation

### Code Template (LangGraph)

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# State definition
class WorkflowState(TypedDict):
    input_data: str
    text_output: str

# Text Agent function
async def text_agent(self, state: WorkflowState, name: str) -> WorkflowState:
    # 1. Extract and format input from state
    prompt_input = state["input_data"].replace("{", "{{").replace("}", "}}")

    # 2. Build prompt from system message and user input
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT.replace("{", "{{").replace("}", "}}")),
        ("user", "{prompt_input}"),
    ])

    # 3. Create chain and invoke
    chain = prompt | self.llm
    result = await chain.ainvoke({"prompt_input": prompt_input})

    # 4. Return updated state with text content
    return {"text_output": result.content}
```

### Full Example (from planning.py)

```python
async def _agent_persona_agent(self, state: ReplyPlanningState, name: str) -> ReplyPlanningState:
    """Generate agent persona based on context."""

    # Format input, escaping braces for prompt template
    prompt_input = get_agent_persona_prompt_input(state).replace("{", "{{").replace("}", "}}")

    # Build prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", agent_persona_prompt.replace("{", "{{").replace("}", "}}")),
        ("user", "{prompt_input}"),
    ])

    # Simple chain: prompt -> LLM
    chain = prompt | self.llm

    # Invoke and extract content
    result = await chain.ainvoke({"prompt_input": prompt_input})

    # Return state update
    return {"agent_persona": result.content}
```

### LangGraph-Specific Notes

- **State handling:** Function receives full state, returns dict with only the keys to update
- **Brace escaping:** Always escape `{` and `}` in dynamic content to prevent template conflicts
- **Async pattern:** Use `await chain.ainvoke()` for async execution
- **Graph registration:** Register with `graph.add_node("agent_name", agent_function)`

---

## Pitfalls & Best Practices

**Pitfalls:**

- **Parsing text output** — Never try to parse this output with regex or string splitting. If you need structured data, use Structured Output Agent instead.

- **Instruction drift** — In long chains of text agents, conversational tone can amplify. Keep prompts directive and concise for internal agent communication.

- **Inconsistent formatting** — Without schema validation, the same prompt can produce differently formatted outputs. If format matters, be explicit in the prompt or use Structured Output Agent.

- **Missing brace escaping** — Forgetting `.replace("{", "{{")` causes template errors when input contains braces (common in JSON or code).

**Best Practices:**

- **Clarity is king** — The prompt does 100% of the work. Be explicit, specific, and provide examples for nuanced tasks.

- **Embrace flexibility** — This agent type is ideal for creative, drafting, or brainstorming tasks where slight unpredictability is a feature.

- **Consistent input formatting** — Create dedicated `get_*_prompt_input()` functions to standardize how state is formatted for prompts.

- **Single responsibility** — Each text agent should do one thing well. Split complex tasks into multiple agents rather than overloading a single prompt.
