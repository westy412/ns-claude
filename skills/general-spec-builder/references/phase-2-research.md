# Phase 2: Research

> **When to read:** After Phase 1 (Intake) is complete. This phase gathers codebase and external context before writing the spec. Skip if the discovery document already provides sufficient context.

---

## When to Research

Research is needed when:
- The discovery doc identifies patterns to follow but doesn't detail them
- The work involves integrating with existing code (need to understand conventions)
- External APIs or libraries are involved (need documentation)
- Reference projects exist that should inform the design

Research is NOT needed when:
- The discovery doc is comprehensive and self-contained
- The work is greenfield with no existing patterns to follow
- The user has already provided all necessary context

---

## Codebase Research

Use the `codebase-researcher` sub-agent to gather patterns without polluting your context.

**What to look for:**
- How are similar features structured in this repo?
- What conventions are used (naming, file organization, error handling)?
- What patterns should be followed for consistency?
- Where would this new feature fit in the existing structure?

**How to spawn:**

```
Task tool → subagent_type: "codebase-researcher"
Prompt: "Examine [repo path] for:
1. How existing [feature type] features are structured
2. File organization conventions
3. Naming patterns
4. Error handling patterns
5. Test patterns
Focus on [specific directories or files relevant to the work]."
```

**After results return:**
- Extract what's relevant to the spec
- Record findings in progress.md under Research Findings
- Note specific files to include in the Reference Files section

---

## Reference Project Research

If the user mentions reference projects or existing implementations to follow:

Ask: "Are there reference projects I should look at for patterns?"

**How to research:**

```
Task tool → subagent_type: "codebase-researcher"
Prompt: "Examine [reference project path] for:
1. Architecture patterns used
2. How [specific feature] is implemented
3. Conventions that should be adopted
Return actionable patterns, not a full code walkthrough."
```

---

## Web Research

Use the `web-researcher` sub-agent for external context.

**When to use:**
- API documentation for integrations
- Best practices for specific technologies
- Library/framework patterns
- Current pricing or rate limits for external services

**How to spawn:**

```
Task tool → subagent_type: "web-researcher"
Prompt: "Research [specific topic]:
1. [Specific question 1]
2. [Specific question 2]
Include documentation links and any rate limits or authentication details."
```

---

## Parallelization

When multiple research tasks are independent, spawn them in parallel:

```
Task tool (parallel, same message):
- subagent_type: "codebase-researcher" → "What patterns exist for [X] in this repo?"
- subagent_type: "web-researcher" → "[Technology] best practices for [feature]"
```

This saves time — both research tasks run simultaneously in separate context windows.

---

## Recording Research Findings

After all research completes, update progress.md:

1. **Codebase patterns** — What conventions to follow, with file references
2. **Reference project findings** — Patterns to adopt
3. **Web research findings** — API details, best practices, links
4. **Files to reference** — Add to the Reference Files section of the spec

---

## Phase Completion Checklist

Before moving to Phase 3:
- [ ] Codebase patterns understood (if applicable)
- [ ] Reference projects examined (if applicable)
- [ ] Web research completed (if applicable)
- [ ] Findings recorded in progress.md
- [ ] Reference files identified for the spec
