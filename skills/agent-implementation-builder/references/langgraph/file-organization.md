# LangGraph File Organization

> **Context:** This reference covers LangGraph-specific file structure and placement rules. Read this when setting up a LangGraph project or determining where files go.

---

## File Structure

LangGraph follows a straightforward structure:

**Single team:**
```
project-name/
├── pyproject.toml           # Project config + dependencies (managed by uv)
├── uv.lock                  # Lockfile (managed by uv)
├── .env.example             # Required environment variables
└── src/
    └── content-review-loop/
        ├── team.py          # Orchestration + agents
        ├── prompts.py       # Agent prompts
        ├── tools.py         # Tool definitions (if needed)
        └── utils.py         # Utilities (if needed)
```

**Nested teams:**
```
project-name/
├── pyproject.toml
├── uv.lock
├── .env.example
└── src/
    └── research-pipeline/
        ├── team.py          # Top-level orchestration
        ├── content-refinement/
        │   ├── team.py
        │   ├── prompts.py
        │   ├── tools.py
        │   └── utils.py
        └── parallel-research/
            ├── team.py
            ├── prompts.py
            ├── tools.py
            └── utils.py
```

**Only create files if the team needs them.**

---

## File Placement Rules

| File | What Goes Here | Required? |
|------|----------------|-----------|
| `team.py` | Orchestration logic + agent node functions | YES |
| `prompts.py` | Separate prompt strings for each agent | YES |
| `tools.py` | Tool definitions with `@tool` decorator | If agents use tools |
| `utils.py` | Shared utilities, helpers | If needed |

---

## File Generation Order (LangGraph)

1. **team.py scaffold** — Orchestration structure + placeholder agents
2. **tools.py** — Tool definitions (if needed)
3. **team.py full** — Fill in agent implementations
4. **prompts.py** — All prompts (parallel generation via prompt-creator sub-agents)
5. **utils.py** — Shared utilities (if needed)
6. **main.py** — FastAPI wrapper (root level only)

---

## Task Dependencies (LangGraph)

```
team.py scaffold
       ↓
    tools.py
       ↓
agent implementations (can be parallel per agent if tools complete)
       ↓
   prompts.py (parallel - all prompts at once)
       ↓
    utils.py (as needed)
       ↓
  .env.example
       ↓
    main.py (FastAPI wrapper)
```
