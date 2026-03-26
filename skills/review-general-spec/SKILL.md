---
name: review-general-spec
description: Comprehensive review of general specs from general-spec-builder. Spawns 3 parallel review agents (structural, source tracing, ambiguity) via teammate-spawn. Saves consolidated review to the spec's reviews/ folder.
allowed-tools: Read Glob Grep AskUserQuestion Write Skill TeamCreate TaskCreate TaskUpdate TaskList TaskGet SendMessage
---

# Review General Spec

## Purpose

Validate a completed general spec before handoff to implementation. Three dimensions, each run by a dedicated agent in its own context window:

1. **Structural correctness** — required sections, execution plan integrity, anti-patterns
2. **Source material fidelity** — does the spec capture everything from discovery/brainstorm/research?
3. **Ambiguity for autonomous agents** — could an agent misinterpret this and build the wrong thing?

This is the quality gate between spec-building and implementation.

---

## Input

A spec file produced by `general-spec-builder`. Typically located at:

```
[workforce-root]/specs/YYYY-MM-DD-feature-name/spec.md
```

The user provides the path to the spec file or its parent directory.

---

## Step 1: Locate Spec and Source Materials

Read the spec file provided by the user.

**Identify the spec folder** — the parent directory of the spec file.

**Find source materials in this order:**

1. Check the spec's **Reference Files** section for a discovery document path
2. Look for `discovery.md` in the spec folder (sibling convention)
3. Look for `brainstorm.md` in the spec folder
4. Look for a `research/` directory in the spec folder

**If no discovery document is found by either method:**
Ask the user: *"I cannot find the discovery document for this spec. Where is it located?"*

**If brainstorm or research documents exist**, note them — they will be used in source tracing.

Read all located source materials before proceeding.

---

## Step 2: Spawn Review Team

Load the `teammate-spawn` skill to generate teammate prompt files.

**Team composition (3 agents):**

| Agent | Dimension | Reference | Summary |
|-------|-----------|-----------|---------|
| `structural-checker` | Structural Checks | `references/structural-checks.md` | 11 structural validation checks |
| `source-tracer` | Source Tracing | `references/source-tracing.md` | Cross-reference spec against discovery/brainstorm |
| `ambiguity-analyzer` | Ambiguity Analysis | `references/ambiguity-analysis.md` | 6-category ambiguity detection |

**Setup sequence:**

1. Load the `teammate-spawn` skill: `Skill tool → skill: "teammate-spawn"`
2. Create a team via `TeamCreate`
3. Create one task per dimension via `TaskCreate`
4. Generate teammate prompt files — each prompt must include:
   - Path to the spec file
   - Paths to all source materials (discovery, brainstorm, research)
   - The specific reference file content for their dimension
   - The findings format they must report back in
   - Instruction: **read-only investigation, do NOT modify any files**
5. Spawn all 3 agents in parallel

**Each agent's prompt must contain:**
- The full spec content (or path to read it)
- The full discovery document content (or path to read it)
- The specific checks/methodology from their reference file
- The exact output format expected (tables from their reference)
- Instruction to send findings back via `SendMessage`

**Why separate context windows:** Each dimension requires holding the full spec + source materials in context alongside the detailed methodology. Running all three in one context would exceed useful context limits and reduce quality.

---

## Step 3: Collect Results

1. Monitor all 3 agents until complete
2. Each agent reports structured findings back via `SendMessage`
3. Collect all findings

---

## Step 4: Consolidate and Cross-Reference

**Cross-reference source tracing and ambiguity results:**
If the source tracer found a gap (something in discovery not in spec) AND the ambiguity analyzer flagged the same area as ambiguous — classify it as a **source tracing gap** (the answer exists in discovery but wasn't carried to the spec), not an ambiguity. This prevents double-counting.

**Merge findings into a single report** using `templates/review-output.md`:
- Section 1: Structural Checks (from structural-checker)
- Section 2: Source Material Tracing (from source-tracer)
- Section 3: Ambiguity Analysis (from ambiguity-analyzer, deduplicated)
- Section 4: Overall Summary with per-dimension verdicts

**Apply overall verdict:**
- Any FAIL in any dimension → Overall FAIL
- No FAILs but WARNs → Overall WARN
- All PASS → Overall PASS

---

## Step 5: Save Review and Present Results

**Save automatically** — reviews are non-destructive and always useful.

1. Create `reviews/` folder in the spec directory if it does not exist
2. Determine next review number: glob `reviews/review-*.md`, parse the highest number, add 1. Start at `001` if none exist.
3. Write review to `reviews/review-NNN.md` using `templates/review-output.md`
4. Clean up team: shutdown teammates, delete team

**Present to user:**
- Overall verdict (PASS/WARN/FAIL per dimension)
- Blocking issue count
- Warning count
- The path where the review was saved

**Then ask:**
*"The review has been saved to `[path]`. Would you like me to fix any of the issues found?"*

---

## Key Principles

- **Parallel execution in separate contexts** — each dimension gets its own agent with full context, preventing quality degradation from overloaded context
- **Source tracing is the highest-value dimension** — missing discovery items cause scope drift during implementation
- **Ambiguity findings must be actionable** — every finding includes a specific clarification question
- **Cross-reference before consolidating** — deduplicate between source tracing and ambiguity findings
- **Save reviews automatically** — non-destructive audit trail
- **Read-only investigation** — review agents do NOT modify the spec or any files

---

## Spec Folder Convention

This skill expects (and reinforces) the following folder structure:

```
[workforce-root]/specs/
  YYYY-MM-DD-feature-name/
    discovery.md          # source discovery document
    brainstorm.md         # optional (~20% of the time)
    research/             # optional external research
    spec.md               # the general spec
    reviews/              # review outputs (this skill writes here)
      review-001.md
    feedback/             # placeholder for implementation verification
    progress.md           # centralized progress tracking
```

---

## References

| Reference | Purpose |
|-----------|---------|
| `references/structural-checks.md` | 11 structural validation checks |
| `references/source-tracing.md` | Source material cross-referencing methodology |
| `references/ambiguity-analysis.md` | Ambiguity detection categories and process |
| `templates/review-output.md` | Review report template |
