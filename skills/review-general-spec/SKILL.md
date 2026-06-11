---
name: review-general-spec
description: Comprehensive review of general specs from general-spec-builder. Spawns 3 parallel review agents (structural, source tracing, ambiguity) via teammate-spawn. Saves consolidated review to the spec's reviews/ folder.
allowed-tools: Read Glob Grep AskUserQuestion Write Skill TeamCreate TaskCreate TaskUpdate TaskList TaskGet SendMessage
---

# Review General Spec

> **Mirrored machinery.** `review-general-spec` and `review-agent-spec` share their review
> engine: `autonomy-and-escalation.md` + `grounding-and-testability.md` are byte-identical
> copies; `ambiguity-analysis` / `source-tracing` / `structural-checks` are deliberate per-track
> specializations of the same structure. Change shared machinery via `skill-updater` across all
> copies — never assume the sibling covers a fix made here.


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

## Step 2: Spawn Review Team via Teammate-Spawn

> **MANDATORY PROCESS — You MUST use the teammate-spawn skill to generate prompt files.**
> Do NOT spawn agents with inline prompts. Do NOT use the Agent tool directly.
> Every review agent MUST read their instructions from a file generated through teammate-spawn.
> If you skip this process, the review quality will degrade — agents ignore long inline prompts.

### Step 2a: Load teammate-spawn skill

```
Skill tool → skill: "teammate-spawn"
```

**STOP HERE until the skill is loaded.** Do not proceed to team creation or agent spawning until teammate-spawn is loaded and you have read its template.

### Step 2b: Read the teammate-spawn template

Read the template file at `skills/teammate-spawn/templates/teammate-prompt.md`. You will fill this in once for each of the 3 agents below.

### Step 2c: Read the reference files for all 3 dimensions

Read ALL THREE reference files now — you need their content to embed in each teammate's prompt file:

1. `references/structural-checks.md` — 11 structural validation checks
2. `references/source-tracing.md` — Cross-reference spec against discovery/brainstorm
3. `references/ambiguity-analysis.md` — 6-category ambiguity detection

### Step 2d: Create a team

Create a team via `TeamCreate`.

### Step 2e: Generate prompt files for all 3 agents

**Team composition:**

| Agent | Dimension | Reference |
|-------|-----------|-----------|
| `structural-checker` | Structural Checks | `references/structural-checks.md` |
| `source-tracer` | Source Tracing | `references/source-tracing.md` |
| `ambiguity-analyzer` | Ambiguity Analysis | `references/ambiguity-analysis.md` |

**For EACH of the 3 agents above**, follow the teammate-spawn process:

1. Fill in the teammate-spawn template with:
   - **Role**: The agent's review dimension
   - **Reference files**: Path to the spec file AND paths to all source materials (discovery, brainstorm, research)
   - **Tasks**: The specific checks/methodology from their dimension's reference file (embed the full content)
   - **Communication**: Send findings back to the team lead via `SendMessage`
   - **Validation**: The exact output format expected (tables from their reference file)
   - **Constraint**: Read-only investigation — do NOT modify any files
2. Write the filled template to: `{spec-folder}/teammate-prompts/review-general-spec/{agent-name}.md`

You MUST write all 3 prompt files before spawning any agents.

### Step 2f: Create tasks and spawn all 3 agents

1. Create one task per dimension via `TaskCreate`
2. Spawn all 3 agents in parallel — each agent's spawn prompt is ONLY a pointer to their prompt file:

```
You are teammate {agent-name} on team {team-name}.

Read your full instructions at:
  {spec-folder}/teammate-prompts/review-general-spec/{agent-name}.md

Follow all steps in order.
```

**Do NOT put review instructions in the spawn prompt itself.** The prompt file IS their instructions.

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

**Lead-run checks (not delegated) — Grounding & Testability:** before applying the verdict, run `references/grounding-and-testability.md` against the spec yourself — reality-grounding (FAIL unanchored I/O) + scale/known-risk, and test-derivability (FAIL un-testable Requirements). Emit the liftable cases to `reviews/review-NNN-testseed.md`. These add two dimensions — `reality_grounding` and `test_derivability` — to the verdict below.

**Apply overall verdict:**
- Any FAIL in any dimension → Overall FAIL
- No FAILs but WARNs → Overall WARN
- All PASS → Overall PASS

---

## Step 5: Save Review and Present Results

**Save automatically** — reviews are non-destructive and always useful.

1. Create `reviews/` folder in the spec directory if it does not exist
2. Determine next review number: glob `reviews/review-*.md`, parse the highest number, add 1. Start at `001` if none exist.
3. Write review to `reviews/review-NNN.md` using `templates/review-output.md` — **fill the machine-readable `review_verdict` header** at the top; it is what the implementation-builder parses to block on FAIL. Also write the liftable cases to `reviews/review-NNN-testseed.md`.
4. Clean up team: shutdown teammates, delete team

**Present a digest in chat — complete on errors, ruthless on everything else.** The full detail
lives in `reviews/review-NNN.md`; the chat digest exists for the user's fix-or-proceed decision,
not as a second archive. Output:

1. **Verdict line** — overall + per-dimension with counts, ONE line
   (e.g. `FAIL — structural PASS · source-tracing FAIL (2 critical) · ambiguity WARN (3)`).
2. **Blocking issues** — EVERY FAIL, one line each: `[location] — what's wrong → fix`.
   For an ambiguity item, the clarification question IS the line.
3. **Warnings** — EVERY WARN, same one-line shape.
4. **Everything else as counts only** — clean checks, LOW/info items: a single summary line
   (e.g. `Clean: 14 checks · 5 LOW notes — see the saved review`). No tables for these.
5. **Saved path.**

**Digest rules:** every FAIL and WARN appears — never collapse errors into a count; one line per
finding — no nested tables, no severity-legend boilerplate, no restating what a finding means; if
a line needs two sentences, it's two findings.

**Spec-defect loopback.** When a finding is that the *spec itself* is wrong or under-specified (not mere reviewer uncertainty), the fix loops **back into the spec** via the spec-builder — never patched downstream, or the spec-derived tests stay wrong too. See `references/autonomy-and-escalation.md`.

**Then ask:**
*"The review has been saved to `[path]`. Would you like me to fix any of the issues found?"*

The user must grasp every error from the chat digest alone — and read it in under a minute. Depth lives in the saved file.

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
| `references/grounding-and-testability.md` | Reality-grounding + test-derivability (lead-run at consolidation); emits the test seed |
| `references/autonomy-and-escalation.md` | Fix-or-ask contract: spec-defect loopback + escalation comms standard (clause C) |
| `references/ambiguity-analysis.md` | Ambiguity detection categories and process |
| `templates/review-output.md` | Review report template |
