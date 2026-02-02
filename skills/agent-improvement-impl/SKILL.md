---
name: agent-improvement-impl
description: Implement approved change specs for existing agent systems. Takes change specs from agent-improvement-spec and executes the changes. Use after a change spec has been approved.
allowed-tools: Read, Glob, Grep, Task, Write, Edit, Bash, WebFetch
---

# Agent Improvement Implementation Skill

## Purpose

An implementation skill for applying improvements to existing agent systems. Takes approved change specs and executes the changes systematically.

**Goal:** Implement changes from change specs accurately and completely.

---

## When to Use This Skill

Use this skill when:
- A change spec has been approved
- Implementing features, fixes, or enhancements to existing agents
- Adding integrations to existing systems

**Skip this skill when:**
- Building new agent system from scratch (use agent-impl-builder)
- Change spec not yet approved (use agent-improvement-spec first)
- Only making a trivial single-file edit

---

## Key Principles

1. **Follow the change spec** — The spec is your source of truth
2. **Read before modifying** — Always read existing files before editing
3. **Minimal changes** — Only change what the spec requires
4. **Test as you go** — Verify changes work before moving on
5. **Update progress** — Track completion in progress document
6. **Ask when unsure** — If spec is unclear, ask before guessing

---

## Framework Cheat Sheets

**If the change involves framework code, READ THE CHEAT SHEET FIRST.**

| Framework | Cheat Sheet Location |
|-----------|---------------------|
| LangGraph | `frameworks/langgraph/CHEATSHEET.md` |
| DSPy | `frameworks/dspy/CHEATSHEET.md` |

---

## Child Skills

**Use these skills when implementing specific types of changes:**

| Change Type | Skill | When |
|-------------|-------|------|
| New agent implementation | `individual-agents` | Implementing new agent code |
| Team structure changes | `agent-teams` | Modifying orchestration |
| Prompt updates | `prompt-engineering` | Writing/modifying prompts |
| New tools or utilities | `tools-and-utilities` | Implementing tools, helpers, integrations |

**The prompt-creator sub-agent should handle prompt changes.**

---

## Sub-Agents

### prompt-creator

**Use for:** Implementing prompt changes from the change spec.

**How to invoke:**
```
Task tool → subagent_type: "prompt-creator"

Prompt: "Update the [agent-name] prompt in [prompts.py path].

Current prompt variable: [VARIABLE_NAME]

Changes required (from change spec):
- Add instruction: "[new instruction]"
- Modify constraint: "[old] → [new]"

Agent spec reference: [path to agent spec if available]

Read the current prompt, apply the changes, and edit the file directly."
```

---

## Input

Approved change spec from agent-improvement-spec:

```
project-name/
└── change-specs/
    └── YYYYMMDD-feature-name.md   # Approved change spec
```

---

## Output

Modified project files as specified in the change spec.

---

## Workflow

### Phase 0: Parse Change Spec and Create Progress

**Step 1: Read the change spec.**

Read `change-specs/YYYYMMDD-feature-name.md` completely.

**Step 2: Verify approval status.**

Check that the spec status is "Approved". If not, stop and ask user.

**Step 3: Create progress document.**

Create `change-specs/YYYYMMDD-feature-name-progress.md`:

```markdown
# Implementation Progress: [Feature Name]

**Change Spec:** change-specs/YYYYMMDD-feature-name.md
**Started:** YYYY-MM-DD
**Status:** In Progress

## Tasks

| Task | Status | Notes |
|------|--------|-------|
| Add dependencies | pending | |
| Create [new-file.py] | pending | |
| Modify [existing-file.py] | pending | |
| Update [agent] prompt | pending | |
| Update .env.example | pending | |
| Test changes | pending | |

## Log

- [timestamp] Started implementation
```

**Step 4: Read framework cheat sheet if applicable.**

If changes involve LangGraph or DSPy code, read the cheat sheet first.

---

### Phase 1: Dependencies

**Step 1: Add new packages.**

From change spec → Dependencies → Python Packages:

```bash
uv add package-name>=X.Y.Z
```

**Step 2: Update progress.**

Mark dependencies task as done.

---

### Phase 2: New Files

For each new file in the change spec:

**Step 1: Read the spec for that file.**

What's the purpose, key components, skeleton?

**Step 2: Read related existing files.**

Understand patterns, imports, conventions used in the project.

**Step 3: If implementing a new agent:**

Use the Skill tool: `skill: "individual-agents"`

**Step 4: Create the file.**

Follow the skeleton and components from the change spec.

**Step 5: Update progress.**

---

### Phase 3: Modified Files

For each modified file in the change spec:

**Step 1: Read the current file.**

Understand what exists before changing.

**Step 2: Apply changes in order.**

Follow the "Specific changes" list from the change spec.

**Step 3: Verify the change.**

Re-read the section to confirm it looks correct.

**Step 4: Update progress.**

---

### Phase 4: Prompt Changes

For each prompt change in the change spec:

**Step 1: Spawn prompt-creator sub-agent.**

```
Task tool → subagent_type: "prompt-creator"

Prompt: "Update the [agent-name] prompt.

File: [path to prompts.py]
Variable: [PROMPT_VARIABLE_NAME]

Required changes:
[List from change spec]

Edit the file directly with the updated prompt."
```

**Step 2: Verify the change.**

Read the prompts file to confirm update was applied.

**Step 3: Update progress.**

---

### Phase 5: Environment & Config

**Step 1: Update .env.example.**

Add new environment variables from change spec.

**Step 2: Add comments.**

Explain what each new variable is for and how to obtain it.

---

### Phase 6: Testing (Optional)

**Testing is optional.** Ask the user before running tests.

**Step 1: Ask the user about testing.**

```
Implementation is complete. Would you like me to test the changes?

Options:
1. Run the test checklist from the change spec
2. Run specific tests (tell me which)
3. Skip testing for now
4. Other approach

How would you like to proceed?
```

**Step 2: If user wants testing, clarify approach.**

| Test Type | What to Do |
|-----------|------------|
| Unit tests | Run pytest on specific files |
| Integration test | Test the full flow manually |
| Smoke test | Quick check that it runs without errors |
| Manual verification | User tests themselves |

**Step 3: Execute chosen testing approach.**

Follow user's preference for testing method.

**Step 4: Document results.**

If tests were run, update progress document with outcomes.

---

### Phase 7: Completion

**Step 1: Update progress document.**

Mark all tasks complete, add completion timestamp.

**Step 2: Update change spec status.**

Change status from "Approved" to "Implemented".

**Step 3: Summarize for user.**

```
Implementation complete for [feature name].

Changes made:
- [X new files created]
- [Y files modified]
- [Z prompts updated]

New dependencies: [list]
New env vars: [list]

Testing: [pass/fail summary]

Next steps:
- Copy .env.example values to .env
- [Any other setup needed]
```

---

## Error Handling

**If you encounter issues:**

1. **Unclear spec:** Ask user for clarification before proceeding
2. **Conflicting code:** Note the conflict, ask how to resolve
3. **Missing dependency:** Check if it needs to be added
4. **Test failure:** Document what failed, ask for guidance

**Never:**
- Guess at implementation details not in the spec
- Skip steps without documenting why
- Leave changes half-applied

---

## References

- `frameworks/` — Framework cheat sheets
- `agent-improvement-spec/` — Creates change specs
- `individual-agents/` — Agent implementation patterns
- `agent-teams/` — Team patterns
- `prompt-engineering/` — Prompt patterns
- `tools-and-utilities/` — Tool and utility function patterns
