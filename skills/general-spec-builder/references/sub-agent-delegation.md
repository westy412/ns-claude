# Sub-Agent Delegation

> **When to read:** During Phase 2 (Research) or anytime you need to gather context without polluting your context window.

---

## Available Sub-Agents

| Sub-Agent | What It Does | When to Use |
|-----------|-------------|-------------|
| `codebase-researcher` | Reads and analyzes code files, returns structured findings | Understanding existing patterns, finding conventions, locating relevant files |
| `web-researcher` | Searches web, returns relevant findings with sources | API documentation, best practices, library/framework patterns, pricing/rate limits |

---

## When to Use Sub-Agents vs Doing It Directly

| Situation | Use Sub-Agent | Do Directly |
|-----------|---------------|-------------|
| Broad codebase exploration | Yes — keeps your context clean | No |
| Reading 1-2 specific files | No | Yes — faster and simpler |
| API documentation lookup | Yes — large docs would pollute context | No |
| Quick pattern check (e.g., "what's in src/models/") | No | Yes — a simple Glob/Grep |

**Rule of thumb:** If the research might return large amounts of content that you'll need to filter, use a sub-agent. If you know exactly what file to read and it's small, do it directly.

---

## Spawning Patterns

### Codebase Researcher

```
Task tool → subagent_type: "codebase-researcher"
Prompt: "Examine [repo/directory] for:
1. [Specific pattern to look for]
2. [Convention to identify]
3. [Files relevant to the work]
Return a structured summary with file paths."
```

### Web Researcher

```
Task tool → subagent_type: "web-researcher"
Prompt: "Research [specific topic]:
1. [Specific question]
2. [Documentation to find]
Include links and any authentication/rate limit details."
```

### Parallel Research

When codebase and web research are independent, spawn both in the same message:

```
Task tool (parallel, same message):
- subagent_type: "codebase-researcher" → "How does auth work in this codebase?"
- subagent_type: "web-researcher" → "FastAPI JWT authentication best practices"
```

---

## After Research Returns

1. Extract what's relevant to the spec
2. Record findings in progress.md under Research Findings
3. Note specific files for the Reference Files section
4. Don't info-dump — integrate findings into your spec writing naturally
