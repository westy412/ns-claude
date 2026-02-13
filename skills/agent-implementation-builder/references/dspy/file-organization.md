# DSPy File Organization

> **Context:** This reference covers DSPy-specific file structure, the two-file prompt pattern (signatures + prompts/*.md), and file placement rules. Read this when setting up a DSPy project or determining where files go.

---

## File Structure

**CRITICAL: DSPy has DIFFERENT file organization than LangGraph.**

DSPy uses a two-file pattern: Signature classes in `signatures.py` have **empty docstrings**, and rich prompt content lives in co-located `prompts/{agent_name}.md` files that get loaded into `Signature.__doc__` at import time.

**Single team:**
```
project-name/
├── pyproject.toml
├── uv.lock
├── .env.example
├── main.py                  # FastAPI service wrapper
└── src/
    └── content-review-loop/
        ├── team.py          # Orchestration module
        ├── signatures.py    # DSPy Signatures (empty docstrings)
        ├── prompts/
        │   ├── creator.md   # Rich prompt content loaded at runtime
        │   └── critic.md
        ├── models.py        # Pydantic models (if needed for complex outputs)
        ├── tools.py         # Tool definitions (if needed)
        └── utils.py         # Utilities + formatters (if needed)
```

**Nested teams:**
```
project-name/
├── pyproject.toml
├── uv.lock
├── .env.example
├── main.py                  # FastAPI service wrapper
└── src/
    └── research-pipeline/
        ├── team.py          # Top-level orchestration
        ├── models.py        # Shared Pydantic models (optional)
        ├── utils.py         # Shared utilities + formatters
        ├── content-refinement/
        │   ├── team.py
        │   ├── signatures.py
        │   ├── prompts/
        │   │   ├── creator.md
        │   │   └── critic.md
        │   ├── tools.py
        │   └── utils.py
        └── parallel-research/
            ├── team.py
            ├── signatures.py
            ├── prompts/
            │   ├── researcher.md
            │   └── merger.md
            ├── tools.py
            └── utils.py
```

---

## File Placement Rules

| File | What Goes Here | Required? |
|------|----------------|-----------|
| `signatures.py` | DSPy Signature classes with empty docstrings + `_load_prompt()` helper | YES (always for DSPy) |
| `prompts/*.md` | Rich prompt content (XML-tagged sections) loaded via `__doc__` at import | YES (one per agent) |
| `models.py` | Pydantic BaseModel classes for complex nested outputs | If needed |
| `team.py` | dspy.Module class with Predict/ChainOfThought instances | YES |
| `tools.py` | Tool functions returning dicts (NOT @tool decorated) | If agents use tools |
| `utils.py` | Singleton LM factories, formatters, retry wrapper | YES (formatters needed between stages) |
| `prompts.py` | **DO NOT CREATE** for DSPy | NO |

---

## Two-File Prompt Pattern

```python
# signatures.py — typed interface with empty docstrings

import dspy
from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent / "prompts"

def _load_prompt(filename: str) -> str:
    """Load prompt content from a co-located markdown file."""
    return (_PROMPTS_DIR / filename).read_text()


class MyAgentSignature(dspy.Signature):
    """"""  # Empty — loaded from prompts/my_agent.md

    input_field: str = dspy.InputField(desc="What this input contains")
    output_field: str = dspy.OutputField(desc="What to return")


# Load at import time — DSPy reads __doc__ when Predict/ChainOfThought is instantiated
MyAgentSignature.__doc__ = _load_prompt("my_agent.md")
```

**Why separate .md files (not inline docstrings):**
- Prompts are editable without touching Python code — prompt engineers iterate on `.md` files without modifying typed interfaces
- Version control clarity — prompt changes vs I/O contract changes show up as separate diffs
- prompt-engineering skill applies directly — XML-tagged sections, role guidance, and quality standards from the skill work naturally with `.md` files
- DSPy optimization compatible — GEPA/MIPROv2 see `__doc__` as a normal string

---

## Structured Output — Critical Rule

When generating DSPy signatures, NEVER use `str` output fields with JSON parsing instructions.
- Use typed fields: `bool`, `int`, `float`, `list[str]`, `dict[str, Any]`, `Literal[...]`
- Use Pydantic `BaseModel` for complex nested outputs, `RootModel[List[...]]` for lists of objects
- Define Pydantic models in `models.py`, import them in `signatures.py`
- Access results: `result.field_name` for typed fields, `result.field_name.model_dump()` for Pydantic models
- See `frameworks/dspy/CHEATSHEET.md` Critical Rules §7 for full guidance and examples

---

## Signature Organization

- **Small teams (1-5 agents):** All signatures in team's `signatures.py`
- **Large teams (6+ agents):** Consider grouping by role or stage within signatures.py, use comments as section headers
- **Nested teams:** Each sub-team has its own `signatures.py` + `prompts/` directory; shared signatures can go in root-level `models.py` if reused

---

## File Generation Order (DSPy)

1. **signatures.py + prompts/*.md** — Signature classes (empty docstrings) + co-located prompt .md files loaded via `__doc__`
2. **tools.py** — Tool functions returning dicts (if needed)
3. **utils.py** — Singleton LM factories, formatters, retry wrapper (REQUIRED)
4. **models.py** — Pydantic models for complex nested outputs (if needed)
5. **team.py** — dspy.Module with Predict/ChainOfThought instances
6. **main.py** — FastAPI wrapper (root level only)

**Key DSPy differences from LangGraph:**
- signatures.py has empty docstrings; rich prompts are in `prompts/{agent_name}.md` files
- prompts/*.md files use XML tags (`<who_you_are>`, `<task>`, etc.) and are loaded at import time via `__doc__` reassignment
- NO prompts.py file — use `prompts/` directory with `.md` files instead
- prompt-engineering skill IS used for DSPy (teammates load it when writing `.md` prompt files)
- utils.py is REQUIRED (not optional) — must have singleton LM + formatters
- models.py only for complex Pydantic outputs, NOT for signatures

---

## Task Dependencies (DSPy)

```
signatures.py + prompts/*.md (empty docstrings + separate .md prompt files)
       ↓
    tools.py (if needed)
       ↓
    utils.py (singleton LM, formatters, retry wrapper)
       ↓
    models.py (Pydantic models if needed for complex outputs)
       ↓
    team.py (dspy.Module with Predict instances)
       ↓
  .env.example
       ↓
    main.py (FastAPI wrapper)
```
