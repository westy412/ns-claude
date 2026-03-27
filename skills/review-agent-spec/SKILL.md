---
name: review-agent-spec
description: Comprehensive review of agent specs from agent-spec-builder. Spawns 3 parallel review agents (structural, source tracing, ambiguity) via teammate-spawn. 9-category ambiguity analysis (6 general + 3 agent-specific). Saves consolidated review to the spec's reviews/ folder.
allowed-tools: Read Glob Grep AskUserQuestion Write Skill TeamCreate TaskCreate TaskUpdate TaskList TaskGet SendMessage
---

# Review Agent Spec

## Purpose

Validate a completed agent spec before handoff to implementation. Three dimensions, each run by a dedicated agent in its own context window:

1. **Structural correctness** — manifest integrity, team folder completeness, data flow consistency, anti-patterns
2. **Source material fidelity** — does the spec capture everything from discovery/brainstorm/research?
3. **Ambiguity for autonomous agents** — could an implementation agent misinterpret this and build the wrong thing?

Agent specs have more implicit assumptions than general specs — agent boundaries, tool behavior, orchestration logic, and data flow between agents all create additional surfaces for ambiguity.

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

## Step 2: Spawn Review Team

Load the `teammate-spawn` skill to generate teammate prompt files.

**Team composition (3 agents):**

| Agent | Dimension | Reference | Summary |
|-------|-----------|-----------|---------|
| `structural-checker` | Structural Checks | `references/structural-checks.md` | 15 structural validation checks (incl. data flow, manifest sync) |
| `source-tracer` | Source Tracing | `references/source-tracing.md` | Cross-reference spec against discovery + agent-specific mappings |
| `ambiguity-analyzer` | Ambiguity Analysis | `references/ambiguity-analysis.md` | 9-category ambiguity detection (6 general + 3 agent-specific) |

**Setup sequence:**

1. Load the `teammate-spawn` skill: `Skill tool → skill: "teammate-spawn"`
2. Create a team via `TeamCreate`
3. Create one task per dimension via `TaskCreate`
4. Generate teammate prompt files — each prompt must include:
   - Path to the spec folder (with manifest.yaml)
   - Paths to all source materials (discovery, brainstorm, research)
   - The specific reference file content for their dimension
   - The findings format they must report back in
   - Instruction: **read-only investigation, do NOT modify any files**
5. Spawn all 3 agents in parallel

**Each agent's prompt must contain:**
- The spec folder path and list of all spec files (from manifest.yaml)
- The full discovery document content (or path to read it)
- The specific checks/methodology from their reference file
- The exact output format expected (tables from their reference)
- Instruction to send findings back via `SendMessage`

**Why separate context windows:** Agent specs are larger than general specs (multiple files across team/agent structure). Each dimension needs the full spec + source materials + methodology. Running all three in one context would severely degrade quality.

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
- Section 2: Source Material Tracing with requirement-to-agent mapping (from source-tracer)
- Section 3: Ambiguity Analysis with agent-specific categories (from ambiguity-analyzer, deduplicated)
- Section 4: Overall Summary with per-dimension verdicts

**Apply overall verdict:**
- Any FAIL in any dimension → Overall FAIL
- No FAILs but WARNs → Overall WARN
- All PASS → Overall PASS

---

## Step 5: Save Review and Present Results

**Save automatically** — reviews are non-destructive and always useful.

1. Create `reviews/` folder in the **parent** spec directory (not inside spec/) if it does not exist
2. Determine next review number: glob `reviews/review-*.md`, parse the highest number, add 1. Start at `001` if none exist.
3. Write review to `reviews/review-NNN.md` using `templates/review-output.md`
4. Clean up team: shutdown teammates, delete team

**Present the FULL findings to the user in the chat.** Do NOT just show a summary — the user needs to see what's wrong. Output:

1. **Overall verdict** (PASS/WARN/FAIL per dimension) as a summary table
2. **All blocking issues** — list every FAIL with the specific issue, where it was found, and the suggested fix
3. **All warnings** — list every WARN with the specific issue and suggestion
4. **Source tracing gaps** — show the coverage gaps table (CRITICAL and MODERATE items)
5. **Ambiguity findings** — show the ambiguity table with clarification questions for HIGH and MEDIUM items
6. **Requirement-to-agent mapping gaps** — show any requirements with no responsible agent
7. **Path where the full review was saved** — for reference

**Then ask:**
*"The review has been saved to `[path]`. Would you like me to fix any of the issues found?"*

The user must be able to read the chat and understand exactly what's wrong without opening the review file.

---

## Key Principles

- **Parallel execution in separate contexts** — each dimension gets its own agent with full context, preventing quality degradation
- **Agent specs have more implicit assumptions** — agent boundaries, tool behavior, and orchestration logic all create additional ambiguity surfaces. Be especially thorough on Categories 7-9.
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
    spec/                 # the agent spec folder
      manifest.yaml       # entry point
      overview.md
      [team-folders]/
    progress.md           # SINGLE centralized progress file (ALL skills read/write)
    reviews/              # review outputs (this skill writes here)
      review-001.md
    feedback/             # placeholder for implementation verification
```

---

## References

| Reference | Purpose |
|-----------|---------|
| `references/structural-checks.md` | 15 structural validation checks |
| `references/source-tracing.md` | Source material cross-referencing methodology |
| `references/ambiguity-analysis.md` | Ambiguity detection (9 categories) |
| `templates/review-output.md` | Review report template |
