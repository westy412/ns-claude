# Delegation Strategy

> **Context:** This reference covers how work is delegated during implementation. The primary execution model uses teammates (team mode) or direct execution (single-agent mode). Both modes can spawn sub-agents for research tasks to avoid polluting context windows.

---

## Execution Hierarchy

```
General Implementation Builder (team lead)
├── Spawns TEAMMATES (via TeamCreate + Task tool with team_name)
│   ├── Each teammate owns a work stream
│   ├── Teammates maintain context across phases within their stream
│   └── Teammates can spawn SUB-AGENTS for:
│       ├── codebase-researcher → Explore codebase patterns, find implementations
│       └── web-researcher → Read API docs, external documentation
│
└── Single-Agent Mode (no teammates)
    ├── Works through phases sequentially
    └── Can spawn SUB-AGENTS for research tasks
```

**Key distinction:**
- **Teammates** (agent teams): Interactive, persistent context, can message back and forth. Used for the main implementation work.
- **Sub-agents** (Task tool, no team_name): Fire-and-forget, return results and terminate. Used for research that would pollute context.

---

## When to Use Sub-Agents vs Direct Work

| Situation | Use | Why |
|-----------|-----|-----|
| Parallel phased work across streams | **Teammates** | Need persistent context, coordination |
| Implementing a file directly | **Do it yourself** | You have the context you need |
| Reading large API documentation | **Sub-agent** (web-researcher) | Large content pollutes context |
| Exploring codebase patterns | **Sub-agent** (codebase-researcher) | Returns only relevant findings |
| Simple file reads | **Do it yourself** | Sub-agent overhead not worth it |
| Understanding unfamiliar code areas | **Sub-agent** (codebase-researcher) | Focused research, clean results |

---

## Sub-Agents Available

### Codebase Researcher

Use when you need to understand existing code without reading everything into your context.

```
Task tool:
  subagent_type: codebase-researcher
  prompt: "How are API endpoints structured in src/? What patterns do existing routes follow?"
```

**Good use cases:**
- Understanding existing patterns before writing new code
- Finding how similar functionality is implemented elsewhere
- Locating relevant files without reading everything
- Checking for existing utilities or helpers to reuse

**The sub-agent reads files, analyzes patterns, and returns a summary** — keeping your context clean for actual code generation.

### Web Researcher

Use when you need external documentation.

```
Task tool:
  subagent_type: web-researcher
  prompt: "Read the Stripe API documentation for payment intents. What are the required parameters and response format?"
```

**Good use cases:**
- API documentation for integrations
- SDK/library reference documentation
- Best practices for specific technologies
- Framework documentation lookup

**Returns relevant findings with sources** — you get the information you need without consuming context on irrelevant docs.

---

## When NOT to Use Sub-Agents

- **Simple file reads** — Use Read tool directly if you need the file in context anyway
- **Quick lookups** — Grep/Glob for a function name is faster than spawning a sub-agent
- **Information you already have** — Don't re-research what you learned in a previous step
- **Small codebases** — If the entire project is small, just read the files directly
