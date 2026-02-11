# DSPy Target

## What You Produce

Two artifacts that work together:

1. **`signatures.py`** — Python file with typed `InputField`/`OutputField` definitions, Pydantic output types, and an **empty docstring**
2. **`prompts/{agent_name}.md`** — Markdown file containing the prompt content that gets loaded into the signature's docstring at runtime

The separation is intentional: `signatures.py` defines the typed interface (what goes in, what comes out), while the markdown prompt file defines the behavioral instructions (how the agent should think and act). At runtime, the prompt markdown content is injected into the signature's docstring.

## Architecture: Why Separate Files

- **Prompts are editable without touching Python code** — content writers and prompt engineers can iterate on behavior without modifying typed interfaces
- **Version control clarity** — changes to the prompt vs changes to the I/O contract show up as separate diffs
- **Clean separation of concerns** — the signature defines structure; the prompt defines behavior
- **Reusable across optimizers** — DSPy optimizers can modify the docstring without changing the signature file

## Output Artifacts

### signatures.py

```python
import dspy
from typing import Literal, Union
from models import ResultModel  # Pydantic models from models.py

class AgentNameSignature(dspy.Signature):
    """"""  # Empty — populated from prompts/agent_name.md at runtime

    # Inputs
    company_name: str = dspy.InputField(
        description="Name of the company to analyze"
    )
    website_content: str = dspy.InputField(
        description="Raw text content scraped from the company's website"
    )

    # Outputs
    overview: str = dspy.OutputField(
        description="2-3 sentence company overview based solely on website content"
    )
    industry: Literal[
        "B2B SaaS", "B2C Software", "Enterprise Software",
        "IT Services", "Healthcare", "Manufacturing",
        "Financial Services", "Other", "Unknown"
    ] = dspy.OutputField(
        description="Industry category — must be EXACTLY one of the valid values"
    )
    result: ResultModel = dspy.OutputField(
        description="Structured analysis result"
    )
```

### prompts/agent_name.md

```xml
<who_you_are>
You are a competitive research analyst specializing in B2B SaaS markets.
You extract structured company intelligence from raw website content.
</who_you_are>

<context>
You are the FIRST analysis agent in a 7-stage pipeline.
Your output becomes the foundation that all downstream agents build upon.

Workflow:
- Stage 1: YOU (DataExtractor) — extract company offerings
- Stage 2: CustomerAnalyzer — identify target customers
- Stage 3: Categorizer — match to predefined categories

Everything downstream depends on YOUR accuracy.
</context>

<task>
1. Read the provided website content carefully
2. Extract the company's primary business offering
3. Identify the industry from the VALID VALUES list
4. Write a concise 2-3 sentence overview
5. Compile the structured analysis result

All claims must be traceable to the provided website content.
Do not fabricate or infer beyond what is explicitly stated.
</task>

<enum_compliance>
For the `industry` output field, you MUST output EXACTLY one of these values:
B2B SaaS, B2C Software, Enterprise Software, IT Services, Healthcare,
Manufacturing, Financial Services, Other, Unknown

DO NOT output variations (e.g., "SaaS" instead of "B2B SaaS").
DO NOT output synonyms (e.g., "Consulting" instead of "IT Services").
If uncertain, use "Other" or "Unknown" — these are always safer than guessing.
</enum_compliance>

<quality_standards>
- All claims traceable to provided website content
- No fabrication — only extract what is explicitly stated
- Choose the MOST SPECIFIC category that applies
- Overview must be 2-3 sentences, not a single line
</quality_standards>

<important_notes>
- Do NOT invent information absent from the website content
- Do NOT use em-dash characters in output fields
- If the website content is empty or unintelligible, set industry to "Unknown" and note the issue in the overview
</important_notes>
```

## Sections to SKIP

These sections are **not needed** in DSPy prompts because typed fields handle them:

| Section | Why It's Skipped | What Handles It Instead |
|---------|-----------------|------------------------|
| `<output_format>` | Output structure is defined by typed `OutputField` declarations and Pydantic models | `OutputField` types + `models.py` |

Do NOT include output schema instructions in the prompt. The types ARE the schema.

## Sections to KEEP

These sections work the same as LangGraph/General targets, using the same XML tags:

| Section | Purpose | Notes |
|---------|---------|-------|
| `<who_you_are>` | Agent identity and expertise | Same as other targets |
| `<skill_map>` | Agent capabilities and competencies | Keep even for single-task agents — helps the model understand its scope |
| `<context>` | Workflow position, upstream/downstream agents | Critical for pipeline agents — explain where they sit |
| `<task>` | Step-by-step instructions | Same as other targets |
| `<important_notes>` | Hard constraints, edge cases, what NOT to do | Place last for recency effect |

For **Conversational** framework, also keep: `<tone_and_style>`, `<knowledge_scope>`, `<capabilities>`, `<operational_logic>`, `<examples>`, `<constraints_and_safeguards>`

## Sections to ADD

These are DSPy-specific sections that don't exist in the general framework templates:

### `<enum_compliance>`

Required for ANY output field using `Literal[...]` or `Union[Literal[...], str]`:

```xml
<enum_compliance>
For the `{field_name}` output field, you MUST output EXACTLY one of these values:
Value1, Value2, Value3, Value4

DO NOT output variations, synonyms, or paraphrases.
If uncertain, use "{fallback_value}" — this is always safer than guessing.
</enum_compliance>
```

List the valid values in BOTH the prompt AND the field description. Double-reinforce.

### `<quality_standards>`

What "good" output looks like. More specific than general constraints:

```xml
<quality_standards>
- All claims must be traceable to the source material
- Scores must use the full range (0.0-1.0), not cluster around 0.7
- Feedback must be actionable: "tone is too casual for enterprise positioning" not "improve brand fit"
</quality_standards>
```

### `<anti_patterns>`

Explicit behaviors the agent must avoid. Distinct from `<important_notes>` — these are common failure modes specific to this agent's task:

```xml
<anti_patterns>
- Do NOT filter or remove items (the Selection Agent does that)
- Do NOT compute aggregate scores (a utility function handles that)
- Do NOT produce vague reasoning like "this is good" without specifics
- Do NOT inflate scores to be "nice" — a mediocre item should score 0.4-0.5
</anti_patterns>
```

## Modifier Adaptations

### Reasoning — Architectural, NOT Prompt Text

Reasoning in DSPy is a **module selection choice**, not something you write into the prompt:

| Task Type | Module | What Happens |
|-----------|--------|-------------|
| Extraction, classification, evaluation | `dspy.Predict(Sig)` | Direct input-to-output mapping |
| Creative synthesis, complex judgment | `dspy.ChainOfThought(Sig)` | Automatic `reasoning` field added before outputs |
| Multi-step tool use | `dspy.ReAct(Sig, tools=[...])` | Iterative reasoning + tool calling loop |

**Do NOT** add "think step by step" to DSPy prompts — `ChainOfThought` handles this automatically by injecting a `reasoning` field.

**DO** describe what quality reasoning looks like for the domain in `<quality_standards>`:
```xml
<quality_standards>
- Reasoning must reference specific evidence from the source material
- Each score must be justified with at least one concrete observation
</quality_standards>
```

**Predictor selection guide** (note this in the signature file or spec, not in the prompt):
- Extraction tasks (pull data from input) → `Predict`
- Classification (assign categories) → `Predict`
- Evaluation/scoring (apply checklist) → `Predict`
- Creative content generation → `ChainOfThought`
- Multi-source synthesis → `ChainOfThought`
- Complex judgment calls → `ChainOfThought`

### Tools — Python Functions, Not Prompt Descriptions

DSPy tools are Python functions with type annotations and docstrings. The tool API is extracted automatically from the function signature:

```python
def search_web(query: str) -> str:
    """Search the web for information about a topic.

    Args:
        query: The search query string

    Returns:
        Search results as formatted text
    """
    ...
```

Tools are passed to `dspy.ReAct(signature, tools=[search_web])`.

**In the prompt**: Describe WHEN and WHY to use tools, and the decision logic for choosing between them. Do NOT describe the tool API — that comes from the function docstring.

```xml
<task>
1. First, check if the question can be answered from the provided context alone
2. If the context is insufficient, use the search tool to find additional information
3. Prefer the provided context over search results when both are available
4. If search returns no results, state that the information is unavailable
</task>
```

### Structured Output — Handled by Typed Fields

Structured output is defined entirely through `OutputField` types and Pydantic models:

```python
# models.py
from pydantic import BaseModel, RootModel

class ContactInfo(BaseModel):
    name: str
    email: str
    role: str

class ContactList(RootModel[list[ContactInfo]]):
    pass

# signatures.py
class ExtractorSignature(dspy.Signature):
    """"""
    text: str = dspy.InputField(description="Text containing contact information")
    contacts: ContactList = dspy.OutputField(description="Extracted contacts with name, email, and role")
```

**Do NOT** add output schema instructions to the prompt. The types handle structure.

**Key patterns:**
- `str` for free text
- `bool` for yes/no decisions
- `int` / `float` for numeric values
- `list[str]` for simple lists
- `Literal["a", "b", "c"]` for small enums (3-15 values)
- `Union[Literal[...], str]` for large enums (15+ values) — prevents validation errors, use fuzzy matching post-processing
- `BaseModel` for structured objects
- `RootModel[list[T]]` for lists of structured objects (NOT `list[T]` directly)

**Models go in `models.py`**, not in `signatures.py`.

### Memory — Not Usually a Prompt Concern

Conversation history in DSPy is handled by passing messages as an input field, not via prompt instructions:

```python
class ConversationalSignature(dspy.Signature):
    """"""
    history: str = dspy.InputField(description="Prior conversation messages formatted as markdown")
    user_message: str = dspy.InputField(description="Current user message")
    response: str = dspy.OutputField(description="Agent response")
```

The memory modifier only applies when there is **long-term or cross-session state**:
- User preferences persisted across sessions
- Accumulated knowledge or summaries
- Session state objects (collected data, workflow progress)

If there's no long-term state, skip this modifier. Most DSPy agents don't need it.

When long-term state IS needed, describe how to USE it in the prompt:
```xml
<task>
Review the user_preferences input to personalize your response.
If preferences conflict with the current request, follow the current request.
</task>
```

## Tips and Tricks

1. **Field descriptions are part of the prompt.** DSPy includes field descriptions in the compiled prompt. Make them specific and actionable — "2-3 sentence overview based on website content" is better than "overview."

2. **Longer docstrings produce better outputs.** Production signatures need 20+ lines of prompt content. Brief prompts like "Extract data from the input" produce poor results. Be comprehensive.

3. **Double-reinforce enum values.** List valid values in BOTH the `<enum_compliance>` section AND the field description. The model sees both, and redundancy improves compliance.

4. **Union[Literal, str] for large enums.** If you have 15+ valid values, use `Union[Literal[...], str]` as the type. Pure `Literal` with many values causes Pydantic validation failures when the model outputs slight variations. Add fuzzy matching in post-processing.

5. **Predictor type is NOT a prompt decision.** Choosing `Predict` vs `ChainOfThought` vs `ReAct` happens at the module level, not in the prompt. Note the recommended predictor in the spec/signature file comments, not in the prompt content.

6. **Pydantic models in `models.py`, signatures in `signatures.py`.** Never mix these. Signatures import from models, not the other way around.

7. **RootModel for list outputs.** Don't use `list[MyModel]` as an OutputField type — use `RootModel[list[MyModel]]`. Access the data via `.root` attribute.

8. **No output format instructions.** Never write "return a JSON object with fields..." in a DSPy prompt. The typed fields handle this. Adding output format instructions creates confusion between the prompt's instructions and DSPy's type-driven formatting.

## Checklist

### signatures.py
- [ ] Empty docstring (`""""""`) — content comes from prompt file
- [ ] All `InputField`s have descriptive `description` parameter
- [ ] All `OutputField`s have descriptive `description` parameter
- [ ] Output types use specific Python types (not `str` for everything)
- [ ] Enum fields use `Literal[...]` or `Union[Literal[...], str]`
- [ ] Complex outputs use Pydantic `BaseModel` or `RootModel` (imported from `models.py`)
- [ ] Predictor type noted in a comment (Predict / ChainOfThought / ReAct)

### prompts/{agent_name}.md
- [ ] Uses XML-tagged sections consistent with other targets
- [ ] `<who_you_are>` establishes identity and expertise
- [ ] `<context>` explains workflow position and upstream/downstream dependencies
- [ ] `<task>` provides numbered step-by-step instructions
- [ ] `<enum_compliance>` present for every Literal/Union output field
- [ ] `<quality_standards>` defines what good output looks like
- [ ] `<important_notes>` or `<anti_patterns>` captures constraints and failure modes
- [ ] NO `<output_format>` section (typed fields handle this)
- [ ] NO "return JSON" or output schema instructions
- [ ] NO "think step by step" instructions (ChainOfThought handles this)
- [ ] Prompt is 20+ lines of substantive content
- [ ] Enum valid values listed in both prompt AND field descriptions
