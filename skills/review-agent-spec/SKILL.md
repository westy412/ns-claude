---
name: review-agent-spec
description: Comprehensive review of agent specs from agent-spec-builder. Runs 15 structural checks, traces source material coverage against discovery/brainstorm docs, and performs ambiguity analysis with 9 categories (6 general + 3 agent-specific). Saves review to the spec's reviews/ folder.
allowed-tools: Read Glob Grep AskUserQuestion Write
---

# Review Agent Spec

## Purpose

Validate a completed agent spec before handoff to implementation. Three dimensions:

1. **Structural correctness** — manifest integrity, team folder completeness, data flow consistency, anti-patterns
2. **Source material fidelity** — does the spec capture everything from discovery/brainstorm/research?
3. **Ambiguity for autonomous agents** — could an implementation agent misinterpret this and build the wrong thing?

Agent specs have more implicit assumptions than general specs — agent boundaries, tool behavior, orchestration logic, and data flow between agents all create additional surfaces for ambiguity. This review is especially thorough on those dimensions.

---

## Input

A spec folder produced by `agent-spec-builder`. Typically located at:

```
[workforce-root]/specs/YYYY-MM-DD-feature-name/spec/
```

The folder must contain `manifest.yaml` as the entry point.

The user provides the path to the spec folder or its parent directory.

---

## Step 1: Locate Spec and Source Materials

Read the spec folder. Confirm `manifest.yaml` exists — this identifies it as an agent spec.

**Identify the spec's parent folder** — source materials live as siblings to the `spec/` directory.

**Find source materials in this order:**

1. Check the spec's `overview.md` for references to a discovery document
2. Look for `discovery.md` in the parent folder (sibling convention)
3. Look for `brainstorm.md` in the parent folder
4. Look for a `research/` directory in the parent folder

**If no discovery document is found by either method:**
Ask the user: *"I cannot find the discovery document for this spec. Where is it located?"*

**If brainstorm or research documents exist**, note them — they will be used in source tracing.

Read all located source materials before proceeding.

---

## Step 2: Run Structural Checks

Load `references/structural-checks.md`.

Execute all 15 checks against the spec. Record PASS/WARN/FAIL for each.

Checks 14 (DSPy path validation) and 15 (instance parity) are conditional — skip if not applicable and mark as N/A.

---

## Step 3: Run Source Material Tracing

Load `references/source-tracing.md`.

Cross-reference every requirement, decision, constraint, and scope item from the discovery document (and any brainstorm/research documents) against the spec.

**Agent-specific tracing includes:**
- Do discovery requirements map to specific agents? (Which agent handles which requirement?)
- Do scope decisions align with agent boundaries?
- Do decisions about tools/integrations from discovery appear in agent tool definitions?
- Do data flow decisions from discovery match the agent data flow specs?

Produce:
- Traceability matrix
- Coverage gaps (classified by importance: CRITICAL/MODERATE/MINOR)
- Misinterpretations (where spec diverges from source intent)

---

## Step 4: Run Ambiguity Analysis

Load `references/ambiguity-analysis.md`.

**Important:** Cross-reference with source tracing results from Step 3. If the discovery document answers a question the spec leaves ambiguous, classify that as a **source tracing gap** (Step 3), not an ambiguity finding. This prevents double-counting.

Analyze using all 9 categories (6 general + 3 agent-specific):
1. Multiple interpretations
2. Undefined edge cases
3. Implicit assumptions
4. Vague scope boundaries
5. Contradictory requirements
6. Missing failure/recovery scenarios
7. **Agent boundary ambiguity** — unclear which agent handles what
8. **Tool behavior ambiguity** — tool behavior/error modes undefined
9. **Orchestration ambiguity** — retry/failure cascade/parallel execution unclear

Produce findings with **specific, answerable clarification questions** for each ambiguity.

---

## Step 5: Save Review and Present Results

**Save automatically** — reviews are non-destructive and always useful.

1. Create `reviews/` folder in the **parent** spec directory (not inside spec/) if it does not exist
2. Determine next review number: glob `reviews/review-*.md`, parse the highest number, add 1. Start at `001` if none exist.
3. Write review to `reviews/review-NNN.md` using `templates/review-output.md`

**Present to user:**
- Overall verdict (PASS/WARN/FAIL per dimension)
- Blocking issue count
- Warning count
- The path where the review was saved

**Then ask:**
*"The review has been saved to `[path]`. Would you like me to fix any of the issues found?"*

---

## Key Principles

- **Agent specs have more implicit assumptions** — agent boundaries, tool behavior, and orchestration logic all create additional ambiguity surfaces. Be especially thorough on Categories 7-9.
- **Source tracing is the highest-value dimension** — missing discovery items cause scope drift during implementation
- **Ambiguity findings must be actionable** — every finding includes a specific clarification question
- **Source tracing runs before ambiguity analysis** — prevents false positives
- **Save reviews automatically** — non-destructive audit trail
- **All 15 structural checks are preserved** — no regression from the original review-spec skill

---

## Spec Folder Convention

This skill expects (and reinforces) the following folder structure:

```
[workforce-root]/specs/
  YYYY-MM-DD-feature-name/
    discovery.md          # source discovery document
    brainstorm.md         # optional (~20% of the time)
    research/             # optional external research
    spec/                 # the agent spec folder
      manifest.yaml       # entry point
      overview.md
      [team-folders]/
    progress.md           # SINGLE centralized progress file (ALL skills read/write)
    reviews/              # review outputs (this skill writes here)
      review-001.md
    feedback/             # placeholder for implementation verification
      implementation.md
```

---

## References

| Reference | Purpose |
|-----------|---------|
| `references/structural-checks.md` | 15 structural validation checks |
| `references/source-tracing.md` | Source material cross-referencing methodology |
| `references/ambiguity-analysis.md` | Ambiguity detection (9 categories) |
| `templates/review-output.md` | Review report template |
