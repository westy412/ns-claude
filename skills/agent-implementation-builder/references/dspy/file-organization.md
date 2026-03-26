# DSPy File Organization

> **Context:** This reference covers DSPy-specific file structure, the two-file prompt pattern (signatures + prompts/*.md), and file placement rules. Read this when setting up a DSPy project or determining where files go.

---

## File Structure

**CRITICAL: DSPy has DIFFERENT file organization than LangGraph.**

DSPy uses a two-file pattern: Signature classes in `signatures.py` have **empty docstrings**, and rich prompt content lives in co-located `prompts/{agent_name}.md` files that get loaded into `Signature.__doc__` at import time.

**Directory naming:** Team directories use **snake_case** because they are Python packages that must be importable (e.g., `from src.content_review_loop.team import ...`). Kebab-case directories like `content-review-loop/` are invalid Python package names.

| Thing | Convention | Example |
|-------|-----------|---------|
| Team directories | snake_case | `content_review_loop/` |
| Python files | snake_case | `team.py`, `signatures.py` |
| Python classes | PascalCase | `PlanningSignature`, `ContentReviewLoop` |
| Python functions/variables | snake_case | `get_shared_lm()`, `call_with_retry()` |
| URL path segments | kebab-case | `/agents/draft/short-form-text` |
| Prompt files | snake_case | `prompts/planner.md`, `prompts/creator.md` |

**Single team:**
```
project-name/
├── pyproject.toml
├── uv.lock
├── .env.example
├── main.py                  # FastAPI service wrapper
└── src/
    └── content_review_loop/
        ├── team.py          # Orchestration module
        ├── signatures.py    # DSPy Signatures (empty docstrings)
        ├── prompts/
        │   ├── creator.md   # Rich prompt content loaded at runtime
        │   └── critic.md
        ├── models.py        # Pydantic models (if needed for complex outputs)
        ├── tools.py         # Tool definitions (if needed)
        └── utils.py         # Utilities + formatters (if needed)
```

**Nested teams (2-5 related teams):**
```
project-name/
├── pyproject.toml
├── uv.lock
├── .env.example
├── main.py                  # FastAPI service wrapper
└── src/
    └── research_pipeline/
        ├── team.py          # Top-level orchestration
        ├── models.py        # Shared Pydantic models (optional)
        ├── utils.py         # Shared utilities + formatters
        ├── content_refinement/
        │   ├── team.py
        │   ├── signatures.py
        │   ├── prompts/
        │   │   ├── creator.md
        │   │   └── critic.md
        │   ├── tools.py
        │   └── utils.py
        └── parallel_research/
            ├── team.py
            ├── signatures.py
            ├── prompts/
            │   ├── researcher.md
            │   └── merger.md
            ├── tools.py
            └── utils.py
```

**Multi-team service (many teams, shared infrastructure, multiple HTTP endpoints):**

This is the nested-teams pattern applied at service scale. The parent team's orchestration equivalent is `main.py` (FastAPI app + all endpoint handlers). Shared infrastructure sits at the parent level (`src/`). Each sub-team follows the standard team directory structure.

| When | Pattern |
|------|---------|
| 1 team | Single team (above) |
| 2-5 related teams | Nested teams (above) |
| Many teams (10+), shared infrastructure, multiple HTTP endpoints | Multi-team service (below) |

```
project-name/
├── pyproject.toml
├── .env.example
├── main.py                              # Parent orchestration — FastAPI app + all endpoint handlers
└── src/
    ├── config.py                        # Service configuration
    ├── schemas.py                       # All request/response schemas (base classes + per-endpoint)
    ├── models.py                        # Shared output models (or models/ directory if many)
    ├── utils.py                         # Shared utilities: singleton LM, retry, validators (or utils/ if many)
    ├── services.py                      # External clients (or services/ directory if many)
    │
    ├── document_draft/                  # Sub-team (standard team structure)
    │   ├── __init__.py
    │   ├── team.py                      # dspy.Module orchestration
    │   ├── signatures.py                # DSPy signatures
    │   ├── prompts/                     # Prompt .md files
    │   │   ├── planner.md
    │   │   ├── creator.md
    │   │   └── critic.md
    │   └── utils.py                     # Team-specific formatters (between-stage, if needed)
    │
    ├── document_revision/               # Sub-team
    │   ├── __init__.py
    │   ├── team.py
    │   ├── signatures.py
    │   ├── prompts/
    │   └── utils.py
    │
    ├── quality_check/                   # Sub-team
    │   ├── __init__.py
    │   ├── team.py
    │   ├── signatures.py
    │   └── prompts/
    │
    └── ... (more sub-teams)
```

**Multi-team service design principles:**
1. This IS the nested teams pattern, just at scale (parent = FastAPI service instead of dspy.Module)
2. `team.py` for orchestration in every sub-team (consistent with single-team and nested-team patterns)
3. Shared infrastructure at parent level when multiple sub-teams need it
4. Request schemas in parent-level `schemas.py` (base classes + per-endpoint extensions)
5. Endpoint handlers in `main.py` (thin wiring — ~15-20 lines each)
6. No separate `routes/` or `programs/` wrapper directories
7. Sub-teams sit directly under `src/`, not nested inside wrapper directories

---

## Shared Infrastructure (Nested & Multi-Team)

When multiple sub-teams need the same components, those components go at the parent level.

**Shared at parent level (`src/`):**
- Output models used by multiple sub-teams → `models.py` (or `models/`)
- Singleton LM factories → `utils.py` with `get_pro_lm()`, `get_flash_lm()` functions
- Retry utilities → `utils.py` with `call_with_retry()`
- External service clients → `services.py` (or `services/`)
- Request/response schemas → `schemas.py` (or `schemas/`)

**Not shared (stays in sub-team folders):**
- Signatures → each sub-team has its own `signatures.py` (never shared between siblings)
- Prompts → each sub-team has its own `prompts/*.md` (never shared)
- Team-specific formatters → sub-team's `utils.py` (between-stage formatting)

**When to promote a single file to a directory:**
- `models.py` → `models/` when it gets unwieldy
- `utils.py` → `utils/` when it gets unwieldy
- `schemas.py` → `schemas/` when it gets unwieldy
- Promote with `__init__.py` re-exporting for backwards compatibility

---

## Multi-Endpoint FastAPI Pattern

When a multi-team service has many HTTP endpoints (e.g., 10+ programs each with their own endpoint), the FastAPI layer follows this pattern.

**All endpoint handlers in `main.py`:**

```python
from fastapi import FastAPI
from src.schemas import DraftInput, DraftOutput
from src.document_draft.team import DocumentDraft

app = FastAPI()

@app.post("/agents/draft/document")
async def draft_document(request: DraftInput) -> DraftOutput:
    program = DocumentDraft()
    result = await program.aforward(**request.model_dump())
    return DraftOutput(**result)
```

After eliminating formatter layers (by using individual InputFields on signatures), handlers are thin wiring:
- Import request schema
- Import team module
- Call `aforward()` with unpacked request
- Return typed response

With many endpoints at ~15-20 lines each, `main.py` stays manageable (~300-500 lines).

**If main.py grows unwieldy (>500 lines), split by domain:**
- `src/draft_routes.py` — all draft endpoints
- `src/revision_routes.py` — all revision endpoints
- `src/specialized_routes.py` — specialized endpoints
- `main.py` imports and includes them: `app.include_router(draft_routes.router)`

**Request schemas pattern (in `src/schemas.py`):**

```python
class CommonContext(BaseModel):
    """Shared context fields used by all programs."""
    title: str
    description: str
    language: str
    # ... more shared fields

class DraftInput(CommonContext):
    """Base for all draft endpoints."""
    pass

class SpecializedDraftInput(DraftInput):
    """Domain-specific additions."""
    extra_field: Optional[str] = None
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
