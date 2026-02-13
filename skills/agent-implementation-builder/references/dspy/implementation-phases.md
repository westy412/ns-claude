# DSPy Implementation Phases

> **Context:** This reference covers DSPy-specific implementation details for Phase 4 (Prompts/Signatures). Read this when you reach Phase 4 of the workflow and the framework is DSPy.

---

## Phase 4: Signatures + Prompts (DSPy)

**CRITICAL: DSPy uses a two-file pattern. Signatures have empty docstrings; prompts live in separate `.md` files.**

**Strategy:** Create `signatures.py` with empty docstrings and `_load_prompt()` helper, then create `prompts/{agent_name}.md` files with rich XML-tagged prompt content. Teammates load the `prompt-engineering` skill when writing the `.md` files.

### Step 1: Create signatures.py with empty docstrings + prompt loader

```python
# signatures.py

import dspy
from pathlib import Path
from typing import Literal, Union

_PROMPTS_DIR = Path(__file__).parent / "prompts"

def _load_prompt(filename: str) -> str:
    """Load prompt content from a co-located markdown file."""
    return (_PROMPTS_DIR / filename).read_text()


class CreatorSignature(dspy.Signature):
    """"""  # Empty — loaded from prompts/creator.md

    # Inputs
    theme: str = dspy.InputField(desc="Content theme to write about")
    previous_feedback: str = dspy.InputField(
        desc="Optional feedback from prior iteration. If not provided, this is the first attempt.",
        default=None
    )

    # Outputs
    content: str = dspy.OutputField(desc="Generated content")


class CriticSignature(dspy.Signature):
    """"""  # Empty — loaded from prompts/critic.md

    content: str = dspy.InputField(desc="Content to review")
    criteria: str = dspy.InputField(desc="Quality criteria")

    feedback: str = dspy.OutputField(desc="Specific improvement suggestions")
    passed: bool = dspy.OutputField(desc="True if content meets criteria")
    score: int = dspy.OutputField(desc="Quality score 0-100")


# Load rich prompt content from markdown at module import time.
# DSPy reads __doc__ when Predict/ChainOfThought is instantiated.
CreatorSignature.__doc__ = _load_prompt("creator.md")
CriticSignature.__doc__ = _load_prompt("critic.md")
```

### Step 2: Create prompts/*.md files with XML-tagged content

For each agent, create a `prompts/{agent_name}.md` file using XML tags:

```xml
<!-- prompts/creator.md -->

<who_you_are>
You are a creative content generator in a quality-retry loop.
You produce initial content that a Critic will evaluate.
</who_you_are>

<context>
Workflow:
- Stage 1: YOU (Creator) — Generate content based on theme
- Stage 2: Critic — Evaluate and provide feedback
- Repeat: You receive feedback and improve

When previous_feedback is provided, you are on a retry iteration.
Incorporate the feedback to improve your output.
</context>

<task>
1. Read the theme and any previous feedback
2. Generate creative content that addresses the theme
3. If feedback is present, specifically address each point raised
4. Ensure output meets quality standards below
</task>

<quality_standards>
- Be specific and actionable, not generic
- Incorporate all critic feedback when available
- Each iteration must show measurable improvement
</quality_standards>

<anti_patterns>
- Do NOT ignore previous feedback
- Do NOT repeat the same content across iterations
- Do NOT produce generic filler content
</anti_patterns>

<important_notes>
- If no previous_feedback is provided, this is the first attempt
- Always improve on previous iteration when feedback exists
</important_notes>
```

---

## DSPy Prompt-Writing File Traversal

When writing DSPy `prompts/*.md` files, teammates should read these reference files in order:

| Order | File | Purpose |
|-------|------|---------|
| 1 | `agent-implementation-builder/frameworks/dspy/CHEATSHEET.md` | Signature patterns and DSPy-specific rules |
| 2 | `prompt-engineering/references/targets/dspy.md` | DSPy-specific sections to keep/skip/add |
| 3 | `prompt-engineering/references/frameworks/single-turn.md` | XML section structure template |
| 4 | `prompt-engineering/references/roles/{role}.md` | Role-specific section guidance |
| 5 | `prompt-engineering/references/modifiers/{applicable}.md` | Modifier adaptations for DSPy |
| 6 | `prompt-engineering/references/guidelines/prompt-writing.md` | Quality checklist |

---

## Do NOT

- Create `prompts.py` for DSPy projects
- Write inline docstring prompts — use `prompts/*.md` files loaded via `__doc__`
- Use `=== SECTION ===` headers — use XML tags (`<who_you_are>`, `<task>`, etc.)
- Use brief docstrings like "Extract data" — prompts must be 20+ lines of substantive content

**Why this matters:**
DSPy reads `Signature.__doc__` when `Predict`/`ChainOfThought` is instantiated. The `_load_prompt()` helper reads `.md` files at import time and assigns them to `__doc__`. This gives you the best of both worlds: typed Python interfaces in `signatures.py` and rich, maintainable prompt content in `.md` files that benefit from the full prompt-engineering skill guidelines.
