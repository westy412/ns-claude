---
name: review-product-extraction
description: Factual review of product extraction outputs (vision, component, sub-component docs) against their source transcripts. Spawns 3 parallel review agents (grounding, assumption audit, integrity) via teammate-spawn. Runs as the mandatory final step of product-vision / product-component / product-sub-component; also invocable standalone. Saves consolidated review to the vault's private/reviews/ folder.
allowed-tools: Read Glob Grep Write Bash AskUserQuestion Skill TeamCreate TaskCreate TaskUpdate TaskList TaskGet SendMessage
argument-hint: "[doc path(s) or meeting path — plus vault path if not obvious]"
---

# Review Product Extraction

> **Invoke with:** `/review-product-extraction` | **Keywords:** review extraction, fact check, grounding, hallucination check, transcript fidelity

## Purpose

Validate extracted product documents against the transcripts they came from. Three dimensions, each run by a dedicated agent in its own context window:

1. **Grounding** — does every substantive claim trace to the transcript? Catches fabrications and wrong attributions.
2. **Assumption audit** — is anything presented as decided that was only discussed, proposed, or inferred? Catches assumptions-as-facts and status inflation.
3. **Integrity** — are the mechanics right? Numbers, names, quotes, cross-doc consistency, knowledge-graph conventions.

This is the quality gate at the end of every extraction. Docs that fail get fixed (through the extraction skill's propose-first conventions) before the session closes.

---

## Input

Either end of the extraction:

- One or more **extracted docs** (vision.md, a component doc, sub-component docs), or
- A **meeting file** (the review covers everything in its `extracted-to` list)

The knowledge graph links the two directions: a doc's `Sources:` header names its meeting files; a meeting's `extracted-to:` frontmatter names its docs. Given either, resolve the other.

---

## Step 1: Locate the Review Set

1. Resolve the **reviewed docs** and **source transcripts** via `Sources:` / `extracted-to:` as above. Ask the user only if neither resolves.
2. Add the **graph surfaces** touched by the extraction — they carry claims too:
   - `components.md` rows + vision Components table rows for the reviewed docs
   - `open-questions.md` rows raised by this extraction
   - The meeting file's post-call analysis
3. Read nothing at the lead level beyond what consolidation needs — the reviewers read the full material in their own contexts.

Scope note: multiple docs from one transcript (e.g. a component + its six sub-components) are ONE review run — the reviewers see the full set, which is what makes cross-doc contradictions visible.

---

## Step 2: Spawn Review Team via Teammate-Spawn

> **MANDATORY PROCESS — You MUST use the teammate-spawn skill to generate prompt files.**
> Do NOT spawn agents with inline prompts. Do NOT use the Agent tool directly with inline instructions.
> Every review agent MUST read its instructions from a file generated through teammate-spawn.
> Agents ignore long inline prompts — the file IS the brief.

### 2a: Load teammate-spawn

```
Skill tool → skill: "teammate-spawn"
```

**STOP until loaded.** Use the `review` profile: read `teammate-spawn/references/review.md` and `teammate-spawn/templates/teammate-prompt-review.md`.

### 2b: Read all three dimension references

1. `references/grounding-tracing.md`
2. `references/assumption-audit.md`
3. `references/integrity-checks.md`

### 2c: Create a team

Create a team via `TeamCreate`.

### 2d: Generate prompt files for all 3 agents

| Agent | Dimension | Reference |
|-------|-----------|-----------|
| `grounding-tracer` | Claim-by-claim transcript tracing | `references/grounding-tracing.md` |
| `assumption-auditor` | Certainty-ladder audit | `references/assumption-audit.md` |
| `integrity-checker` | Mechanical + graph verification | `references/integrity-checks.md` |

For EACH agent, fill the teammate-spawn review template with:

- **Role**: the agent's dimension
- **Reviewing**: absolute paths to ALL reviewed docs + graph surfaces
- **Review against**: absolute paths to ALL source transcripts
- **Tasks**: the full content of that dimension's reference file (embed it — the agent has no other context)
- **Communication**: findings back to the lead via `SendMessage`, in the reference's output-table format
- **Constraint**: read-only — reviewers change nothing

Write each to: `{vault}/private/teammate-prompts/review-product-extraction/{agent-name}.md`
(`private/` is excluded from vault publishing — prompts and reviews must never reach the client portal.)

### 2e: Create tasks and spawn all 3 in parallel

One task per dimension via `TaskCreate`; spawn prompt is ONLY a pointer:

```
You are teammate {agent-name} on team {team-name}.
Read your full instructions at:
  {vault}/private/teammate-prompts/review-product-extraction/{agent-name}.md
Follow all steps in order.
```

**Why separate contexts:** each dimension needs the full transcript(s) + full doc set + its methodology in one window. Combined, quality degrades.

---

## Step 3: Collect Results

Monitor all 3 agents; each reports structured findings via `SendMessage`. Collect all before consolidating.

---

## Step 4: Consolidate

**Dedupe by root cause.** The same sentence often trips two reviewers:

- In the transcript as discussion-but-not-decision → **assumption finding** (not fabrication)
- Absent from the transcript entirely → **grounding finding** (fabrication)
- Present and decided but wrong number/name/quote → **integrity finding**

One finding per defect, classified by root cause.

**Session-confirmation disposition — the extraction was conversational.** Some claims have no transcript basis because the USER confirmed or corrected them in the extraction chat (they were in the room). For each grounding/assumption finding:

- If THIS session's conversation contains that confirmation → disposition **session-confirmed**: not a defect; will fix by adding a source marker (e.g. `(confirmed in session, 2026-07-20)`) so the doc stops looking fabricated to the next reviewer.
- If running standalone (no session record) → the finding stands as **needs you** — the user is the only person who can attest it.

Never silently excuse a finding as "probably confirmed."

**Verdict:** any FAIL in any dimension → Overall FAIL; else any WARN → WARN; else PASS.

---

## Step 5: Save, Present, Fix

1. Create `{vault}/private/reviews/` if missing; number `review-NNN.md` by globbing existing (start `001`).
2. Write the consolidated report using `templates/review-output.md` — fill the machine-readable `review_verdict` header.
3. Clean up: shut down teammates, delete team, remove `private/teammate-prompts/review-product-extraction/`.
4. **Present a digest in chat** — complete on errors, ruthless on everything else. Format:
   - Verdict line: `<overall> — N blocking · N warnings · N need your input`
   - Findings grouped FAIL then WARN, two lines each:
     line 1 — the issue, plainly;
     line 2, indented — `<dimension> · <doc §location> · <disposition>` where disposition is **`will fix (how)`** (transcript or session record settles it), **`session-confirmed (add marker)`**, or **`needs you → Qn`**
   - `Clean:` line — passing checks as counts only
   - Saved path
   - Questions block last — every `needs you` as a numbered, answerable question
5. **Apply fixes through the extraction conventions** — propose-first, then edit the docs, register, and graph surfaces. Doc defects are fixed in the docs; never patch the review report instead. If fixes were substantial, offer a re-run of the failed dimension(s).

Every FAIL and WARN appears in the digest — never collapse errors into a count.

---

## Integration: Mandatory Closing Step

The extraction skills invoke this skill as their final step — after graph validation, before the closing summary:

| Caller | Reviews |
|--------|---------|
| `product-vision` | vision.md + index/components backfills + register rows + meeting file |
| `product-component` | component doc(s) + components.md/vision backfills + register rows + meeting file |
| `product-sub-component` | sub-component docs + parent backfill + register rows + meeting file |

When called by an extraction skill, the extraction session IS the session record for session-confirmation dispositions. The extraction's closing summary must include the review verdict and fixes applied.

Standalone use: reviewing older docs, re-reviewing after fixes, or auditing a vault you didn't extract.

---

## Key Principles

- **Parallel, separate contexts** — one dimension per agent, full material each
- **The transcript is the authority** — with one exception: recorded user confirmations from the extraction session
- **Grounding is the highest-value dimension** — a fabricated claim in a client-visible vault is the worst failure mode
- **Findings must be actionable** — every finding names the doc, the location, and the fix or the question
- **Read-only reviewers** — all edits happen at the lead level through extraction conventions, propose-first
- **Reviews are private** — reports and prompts live under `private/`, never in the published vault

---

## References

| Reference | Purpose |
|-----------|---------|
| `references/grounding-tracing.md` | Claim classification (verbatim → fabricated), attribution checks |
| `references/assumption-audit.md` | Certainty ladder, decision inflation, status honesty |
| `references/integrity-checks.md` | Numbers/quotes/names, cross-doc consistency, graph conventions |
| `templates/review-output.md` | Consolidated report with machine-readable verdict |
