---
name: review-general-spec
description: Comprehensive review of general specs from general-spec-builder. Runs structural checks, traces source material coverage against discovery/brainstorm docs, and performs ambiguity analysis to catch requirements an autonomous agent could misinterpret. Saves review to the spec's reviews/ folder.
allowed-tools: Read Glob Grep AskUserQuestion Write
---

# Review General Spec

## Purpose

Validate a completed general spec before handoff to implementation. Three dimensions:

1. **Structural correctness** — required sections, execution plan integrity, anti-patterns
2. **Source material fidelity** — does the spec capture everything from discovery/brainstorm/research?
3. **Ambiguity for autonomous agents** — could an agent misinterpret this and build the wrong thing?

This is the quality gate between spec-building and implementation. A spec that passes all three dimensions is safe to hand to an autonomous implementation agent.

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

## Step 2: Run Structural Checks

Load `references/structural-checks.md`.

Execute all 11 checks against the spec. Record PASS/WARN/FAIL for each.

---

## Step 3: Run Source Material Tracing

Load `references/source-tracing.md`.

Cross-reference every requirement, decision, constraint, and scope item from the discovery document (and any brainstorm/research documents) against the spec.

Produce:
- Traceability matrix
- Coverage gaps (classified by importance: CRITICAL/MODERATE/MINOR)
- Misinterpretations (where spec diverges from source intent)

---

## Step 4: Run Ambiguity Analysis

Load `references/ambiguity-analysis.md`.

**Important:** Cross-reference with source tracing results from Step 3. If the discovery document answers a question the spec leaves ambiguous, classify that as a **source tracing gap** (Step 3), not an ambiguity finding. This prevents double-counting.

Analyze every requirement, acceptance criterion, and architectural constraint for:
- Multiple possible interpretations
- Undefined edge cases
- Implicit assumptions
- Vague scope boundaries
- Contradictory requirements
- Missing failure/recovery scenarios

Produce findings with **specific, answerable clarification questions** for each ambiguity.

---

## Step 5: Save Review and Present Results

**Save automatically** — reviews are non-destructive and always useful.

1. Create `reviews/` folder in the spec directory if it does not exist
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

- **Source tracing is the highest-value dimension** — missing discovery items cause scope drift during implementation
- **Ambiguity findings must be actionable** — every finding includes a specific clarification question, not just "this is vague"
- **Source tracing runs before ambiguity analysis** — this ordering prevents false positives
- **Save reviews automatically** — they are non-destructive and create an audit trail
- **All existing structural checks are preserved** — no regression from the original review-spec skill

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
      implementation.md
    progress.md           # spec-builder progress tracking
```

---

## References

| Reference | Purpose |
|-----------|---------|
| `references/structural-checks.md` | 11 structural validation checks |
| `references/source-tracing.md` | Source material cross-referencing methodology |
| `references/ambiguity-analysis.md` | Ambiguity detection categories and process |
| `templates/review-output.md` | Review report template |
