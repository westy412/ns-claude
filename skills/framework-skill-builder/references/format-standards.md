# Format Standards

Standards for the output files produced by the Framework Skill Builder. Writers and reviewers should reference this to ensure consistent quality.

---

## SKILL.md Format

The SKILL.md is the routing layer — the first file loaded when the skill is invoked. It should enable Claude to quickly find the right reference file for any task.

### Required Sections

```markdown
---
name: {framework-name}
description: {1-2 sentence description}
metadata:
  tags: {comma-separated tags}
---

# {Framework Name}

> **Invoke with:** `/{framework-name}` | **Keywords:** {relevant search keywords}

{1-2 paragraph description of what this skill covers and when to use it.}

---

## Purpose

{When to use this skill. What it helps with. What it doesn't cover.}

## Reference Files

| Task | Reference File | Description |
|------|----------------|-------------|
| **{user task}** | [{filename}](./references/{filename}) | {what this file covers} |
| ... | ... | ... |

> **Maintenance Note**: If any patterns in the reference files are found to be incorrect during implementation, update the corresponding reference file with the correct pattern.

---

## Core Concepts

{3-5 paragraphs covering the key concepts of the framework. This gives Claude enough context to understand the framework without reading all reference files.}

---

## Quick Reference

{Most commonly needed APIs/patterns. Include 2-3 short code examples showing the most basic usage patterns.}

---

## Documentation Links

- **Docs**: {official docs URL}
- **GitHub**: {repo URL if applicable}
- **API Reference**: {API docs URL if separate}
```

### SKILL.md Guidelines

- The routing table is the most important section — make task descriptions match what users actually ask for
- Core Concepts should be enough for Claude to understand the framework at a high level
- Quick Reference should show the absolute basics (install, hello world, most common pattern)
- Keep the file under 300 lines — details belong in reference files

---

## Reference File Format

Reference files contain the detailed technical content. Each file covers one topic or group of related topics.

### Structure

```markdown
# {Framework Name} -- {Topic Name} Reference

## {Major Section}

{Explanation of concept.}

```{language}
{code example}
```

### {Subsection}

{More detail.}

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `param1` | `string` | `""` | What it does |
| `param2` | `int` | `0` | What it does |

---

## {Next Major Section}

...

---

## Documentation Links

- [{Page Title}]({url}) - {Brief description}
- [{Page Title}]({url}) - {Brief description}
```

### Reference File Rules

| Rule | Correct | Wrong |
|------|---------|-------|
| Frontmatter | None | `---\nname: ...\n---` |
| Title | `# Framework -- Topic Reference` | `# Topic` |
| Code blocks | ` ```python ` with language tag | ` ``` ` without tag |
| Parameters | Table format | Inline prose |
| Doc links | Section at bottom | Inline links only |

### Content Guidelines

**Headings:**
- H1: File title (one per file)
- H2: Major sections
- H3: Subsections within a section
- H4: Rarely needed, use sparingly

**Code examples:**
- Always include language tag on fenced blocks
- Include import statements
- Show complete, runnable examples (not fragments)
- Use the framework's conventions (e.g., async/await if that's the norm)
- Annotate with comments only where the code isn't self-explanatory

**Tables:**
- Use for parameter listings, option comparisons, feature matrices
- Always include header row with column names
- Wrap code in backticks within table cells

**Notes and tips:**
- Use `>` blockquotes for important notes
- Use `**Note:**` prefix for inline callouts
- Keep tips practical and actionable

---

## Documentation Links Section

Every reference file must end with a Documentation Links section. This section provides traceability back to official sources.

### Format

```markdown
---

## Documentation Links

- [Getting Started Guide](https://docs.example.com/getting-started) - Installation and first steps
- [API Reference: create_foo](https://docs.example.com/api/create-foo) - Full parameter docs
- [Advanced Patterns](https://docs.example.com/advanced) - Best practices and patterns
```

### Guidelines

- Include 2-8 links per file (the most relevant ones)
- Link to the specific pages relevant to this topic (not just the docs homepage)
- Use descriptive link text (the page title or a clear description)
- Add a brief description after each link
- Verify URLs are valid and point to the right content

---

## Example: Well-Formatted Reference File

```markdown
# FastAPI -- Dependency Injection Reference

## Overview

FastAPI's dependency injection system uses Python's type hints and `Depends()` to declare, share, and nest dependencies. Dependencies can be functions, classes, or generators.

## Basic Dependencies

### Function Dependencies

```python
from fastapi import Depends, FastAPI

app = FastAPI()

async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons
```

### Class Dependencies

```python
from fastapi import Depends, FastAPI

app = FastAPI()

class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

@app.get("/items/")
async def read_items(commons: CommonQueryParams = Depends(CommonQueryParams)):
    return commons
```

## Dependency Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dependency` | `Callable` | required | The dependency function or class |
| `use_cache` | `bool` | `True` | Cache results within same request |

## Nested Dependencies

Dependencies can depend on other dependencies, forming a dependency tree.

```python
def query_extractor(q: str | None = None):
    return q

def query_or_cookie_extractor(
    q: str = Depends(query_extractor),
    last_query: str | None = Cookie(default=None),
):
    if not q:
        return last_query
    return q
```

> **Note:** FastAPI resolves the full dependency tree automatically and caches results per-request by default.

---

## Documentation Links

- [Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) - Tutorial on dependency injection basics
- [Classes as Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/) - Using classes with Depends
- [Sub-dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/sub-dependencies/) - Nesting dependencies
- [Advanced Dependencies](https://fastapi.tiangolo.com/advanced/advanced-dependencies/) - Parameterized and global dependencies
```

---

## Anti-Patterns

Avoid these common mistakes in skill files:

| Anti-Pattern | Why It's Wrong | Fix |
|-------------|----------------|-----|
| YAML frontmatter in reference files | Only SKILL.md gets frontmatter | Remove it |
| No code examples | Reference files must be practical | Add working examples |
| Placeholder content ("TODO", "TBD") | Files must be complete | Fill in or remove |
| Copying docs verbatim | Should be restructured for reference use | Rewrite in reference style |
| Missing import statements | Code examples should be runnable | Add imports |
| No Documentation Links section | Required for traceability | Add section at bottom |
| Overly long SKILL.md | Details belong in reference files | Move content to references |
| Single massive reference file | Split by topic cohesion | Break into focused files |
