# Structured Output Agent

## What It Is

A single-turn LLM call that returns typed, schema-validated output using Pydantic models. The most reliable pattern when output must be programmatically parsed or used as structured data by downstream code.

## When to Use

- Output must be parsed by code (not just read by humans)
- Data extraction from unstructured text
- Classification or categorization tasks
- Generating data that feeds into APIs or databases
- Any task requiring guaranteed field presence and types
- When downstream agents depend on specific data structure

## When to Avoid

- Output is for human reading only — use **Text Agent** instead (simpler)
- Output needs conversation history — use **Message Agent** instead
- Agent needs to call external tools — use **Structured Output + Tool Agent** instead
- Simple content generation — use **Text Agent** instead (less overhead)

## Selection Criteria

- If output must be programmatically parsed → **Structured Output Agent**
- If output is human-readable text → consider **Text Agent**
- If building conversation flow → consider **Message Agent**
- If agent needs tools AND structured output → consider **Structured Output + Tool Agent**

## Inputs / Outputs

**Inputs:**
- State fields containing context/data for the prompt
- Prompt template (system message + user input)
- Pydantic schema defining expected output structure

**Outputs:**
- Pydantic model instance (validated against schema)
- Converted to dict via `model_dump()` for state updates

## Prompting Guidelines

The schema provides structure, but the prompt still drives quality:

- Include the schema structure or field descriptions in the system prompt
- Be explicit about what each field should contain
- Provide examples of desired output format in the prompt
- On retry, inject the full JSON schema to help the model recover
- Escape curly braces in prompts: `.replace("{", "{{").replace("}", "}}")`

---

## LangGraph Implementation

### Code Template (LangGraph)

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List
import asyncio

# Define Pydantic schema for structured output
class OutputSchema(BaseModel):
    field_one: str = Field(description="Description of field one")
    field_two: int = Field(description="Description of field two")
    items: List[str] = Field(description="List of items")

# Structured Output Agent function
async def structured_output_agent(self, state: WorkflowState, name: str) -> dict:
    # 1. Format input from state
    prompt_input = format_input(state)

    # 2. Build prompt with escaped braces
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT.replace("{", "{{").replace("}", "}}")),
        ("user", "{prompt_input}"),
    ])

    # 3. Retry loop with schema injection on failure
    attempts = 0
    while attempts < 3:
        # Create chain with structured output
        chain = prompt | self.llm.with_structured_output(OutputSchema, include_raw=True)

        try:
            result = await chain.ainvoke({"prompt_input": prompt_input})

            # Extract parsed result (handles both dict and direct model)
            parsed_result = result['parsed'] if isinstance(result, dict) else result
            result_dict = parsed_result.model_dump()

            return {"output_field": result_dict}

        except Exception as e:
            attempts += 1
            if attempts >= 3:
                raise Exception(f"Agent failed after {attempts} attempts. Error: {e}")
            else:
                # Inject schema on retry to help model recover
                schema_str = str(OutputSchema.model_json_schema()).replace("{", "{{").replace("}", "}}")
                retry_msg = f"Previous attempt failed. Please use this schema: {schema_str}"
                prompt.messages.append(("user", retry_msg))
                await asyncio.sleep(1)
```

### Full Example (from arsenal_curation.py)

```python
async def _pain_points_ranking_agent(self, state: MasterWorkflowState, name: str) -> Dict[str, Any]:
    """
    Pain Points Ranking Agent - Structured Output Node

    Ranks pain points by relevance and personalizes the top 2-3 items
    with third-person analytical insights.
    """
    prompt_input = format_pain_points_input(state)

    # Create prompt template with escaped braces
    prompt = ChatPromptTemplate.from_messages([
        ("system", PAIN_POINTS_RANKING_SYSTEM_PROMPT.replace("{", "{{").replace("}", "}}")),
        ("user", "{prompt_input}"),
    ])

    attempts = 0
    while attempts < 3:
        chain = prompt | self.llm.with_structured_output(RankedPainPointsSchema, include_raw=True)

        try:
            result = await chain.ainvoke({"prompt_input": prompt_input})
            parsed_result = result['parsed'] if isinstance(result, dict) else result
            result_dict = parsed_result.model_dump()

            # Transform to domain models
            ranked_pain_points = []
            for pp_data in result_dict["pain_points"]:
                pain_point = RankedPainPoint(
                    rank=pp_data["rank"],
                    justification=pp_data["justification"],
                    problem=pp_data["problem"],
                    impact=pp_data["impact"]
                )
                ranked_pain_points.append(pain_point)

            return {"ranked_pain_points": ranked_pain_points}

        except Exception as e:
            attempts += 1
            if attempts >= 3:
                raise Exception(f"Pain Points Ranking failed after {attempts} attempts. Error: {e}")
            else:
                schema_str = str(RankedPainPointsSchema.model_json_schema()).replace("{", "{{").replace("}", "}}")
                retry_msg = f"Previous attempt failed. Use this schema: {schema_str}"
                prompt.messages.append(("user", retry_msg))
                await asyncio.sleep(1)
```

### Schema Definition Example

```python
from pydantic import BaseModel, Field
from typing import List

class RankedPainPointSchema(BaseModel):
    rank: int = Field(description="Ranking position (1 = most relevant)")
    justification: str = Field(description="Why this pain point is relevant to the lead")
    problem: str = Field(description="The pain point problem statement")
    impact: str = Field(description="Business impact of this pain point")

class RankedPainPointsSchema(BaseModel):
    pain_points: List[RankedPainPointSchema] = Field(
        description="List of ranked pain points, ordered by relevance"
    )
```

### LangGraph-Specific Notes

- **with_structured_output():** Pass `include_raw=True` to access both parsed and raw results for debugging
- **Chain recreation:** Recreate the chain on each retry attempt (don't reuse)
- **Brace escaping:** Always escape `{` and `}` in prompts AND in schema strings
- **State updates:** Return dict with state keys to update
- **Domain transformation:** Consider transforming schema objects to domain models after parsing

---

## Pitfalls & Best Practices

**Pitfalls:**

- **No retry logic** — Without retries, a single malformed response fails the entire agent. Always implement 3-attempt retry loops for production.

- **Forgetting brace escaping** — Both prompts AND schema strings need `.replace("{", "{{")` to avoid template conflicts.

- **Reusing the chain** — Don't reuse the chain object between retry attempts. Recreate it each time to get fresh state.

- **Ignoring include_raw** — Without `include_raw=True`, you lose access to the raw response for debugging failures.

- **Over-complex schemas** — Deep nesting and many optional fields increase failure rates. Keep schemas as flat as possible.

**Best Practices:**

- **Always implement retry logic** — The 3-attempt pattern with schema injection dramatically improves reliability.

- **Use Field descriptions** — Pydantic `Field(description="...")` helps the model understand what each field should contain.

- **Transform to domain models** — After parsing, convert schema objects to your domain models for type safety downstream.

- **Log failures** — On retry, log the error to understand common failure modes.

- **Test with edge cases** — Test with inputs that might produce empty lists, null values, or unusual characters.

- **Use expensive models for structured output** — Consider using a more capable model (e.g., GPT-4, gemini-1.5-pro) for structured output tasks, as they comply with schemas more reliably.

---

## Comparison: Structured Output vs Text Agent

| Aspect | Text Agent | Structured Output Agent |
|--------|------------|------------------------|
| Output | Raw string | Pydantic model |
| Validation | None | Schema-enforced |
| Parsing | Manual (fragile) | Automatic (reliable) |
| Retry needed | Rarely | Almost always |
| Use case | Human reading | Code consumption |
| Complexity | Simpler | More setup |
| Reliability | Variable format | Guaranteed structure |

---

## Retry Pattern Deep Dive

The retry pattern is critical for production reliability:

```python
attempts = 0
while attempts < 3:
    try:
        # Attempt LLM call
        result = await chain.ainvoke({"prompt_input": prompt_input})
        parsed_result = result['parsed'] if isinstance(result, dict) else result
        return {"output": parsed_result.model_dump()}

    except Exception as e:
        attempts += 1

        if attempts >= 3:
            # Final failure - raise with context
            raise Exception(f"Failed after {attempts} attempts. Error: {e}")
        else:
            # Prepare retry with schema hint
            schema_str = str(Schema.model_json_schema()).replace("{", "{{").replace("}", "}}")
            retry_msg = f"Previous attempt failed. Schema: {schema_str}"
            prompt.messages.append(("user", retry_msg))

            # Brief delay before retry
            await asyncio.sleep(1)
```

**Why this works:**
1. **Schema injection** reminds the model of exact structure needed
2. **Message appending** preserves conversation context
3. **Sleep delay** prevents rate limiting
4. **3 attempts** balances reliability with latency
