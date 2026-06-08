# Skill Update Protocol

> **When to read:** When executing an update — for the full intake → locate → classify → apply → validate procedure, the validation gate, and the edge cases.

The detailed procedure behind the SKILL.md process overview. Steps, classification heuristics, the validation gate, and edge cases.

---

## 1. Intake & feedback sources

Establish two things: **which skill**, and **what change**.

The change can arrive as:
- An **explicit request** ("add a validation gate to general-spec-builder").
- **Structured feedback** — the dev-workflow layer-4 friction log, a `review-*-spec` output, an elicitation critique, or a captured failure. Read it in full and extract concrete, applyable change(s). Feedback describes a *problem*; restate it as a *skill change* before touching files.
- A **drift-reconciliation** task — the two trees diverged and the base must be made consistent again. Here the "change" is "make base equivalent, keeping each tree's execution sections."

If the change is vague or you are inferring intent, **ask once**: what specifically should change, and why. Do not draft a guess into shared infrastructure.

---

## 2. Locate & read both trees

- Claude: `~/.claude/skills/<name>/`
- Codex: `~/.codex/skills/<name>/`

Read `SKILL.md` and every reference/template in **both** trees before editing. You cannot keep base in sync if you have only seen one side.

Establish a baseline diff of the non-execution content so you know where the trees already agree or differ:
```bash
diff -r ~/.claude/skills/<name>/ ~/.codex/skills/<name>/
```
Expect differences only in: frontmatter (`allowed-tools`), invocation-syntax lines, and fenced execution sections. Anything else that differs is **pre-existing drift** — flag it and fold its reconciliation into this update.

---

## 3. Classification heuristics — base vs execution

For each discrete change, ask: *does this name or depend on a platform mechanism?*

- **No** → BASE. Reasoning, criteria, doctrine, checklists, examples that don't hinge on a tool. Apply identically to both trees.
- **Yes** → EXECUTION. It names a spawn tool, an invocation syntax, a frontmatter key, or assumes peer messaging. Apply per platform via the tool map in `platform-boundary.md`.

Tie-breakers:
- If a base paragraph currently names a tool inline, **rewrite it neutral** (abstraction discipline) and move the tool name into the execution section — improving sync while you're there.
- If a change assumes teammate↔teammate messaging, re-express the base as parent-relay (common-denominator rule); the Claude tree *may* add a peer-mesh enhancement in its execution section, but the base must not require it.
- Frontmatter is always execution: Claude keeps `allowed-tools`; Codex omits it (house style).

---

## 4. Apply

- BASE edits: make the **same** edit in both trees. Prefer identical text so the regions stay diff-clean.
- EXECUTION edits: make the platform-correct edit in each tree.
- Respect authoring budgets: `SKILL.md` < 300 lines (routing layer); reference files one-topic, < 200 lines, no YAML frontmatter.
- If a base reference file is genuinely identical across trees, author it once and copy it to the other tree (`cp`) to guarantee byte-identity, rather than hand-typing twice.

---

## 5. Validation gate (blocking)

Re-read both trees and assert all of the following before declaring done:

- [ ] **Both trees touched.** No edit landed in one tree only.
- [ ] **Base equivalent.** `diff -r` shows differences *only* in frontmatter, invocation lines, and fenced execution sections. No reasoning content drifted.
- [ ] **Execution correct.** Each tree's execution sections use that platform's tools (Claude tools in Claude; Codex tools in Codex) — no cross-contamination (e.g. `spawn_agent` in the Claude tree).
- [ ] **Common-denominator honored.** No base content requires Claude's experimental peer mesh.
- [ ] **Budgets & format.** SKILL.md < 300 lines; references < 200 lines, no frontmatter; frontmatter correct per platform.
- [ ] **Feedback resolved.** The intake change is actually reflected, not partially applied.

If any check fails, fix it before finishing. The gate is the point of the skill.

---

## 6. Edge cases

- **Skill missing in one tree.** STOP. This is not an update — it's a create-for-parity. Use `skill-builder` to design the missing counterpart (porting the existing tree's base, adapting execution), then return here to keep them synced. Do not silently single-tree the change.
- **Execution-only change** (e.g. a platform renamed a tool). Edit only the affected tree's execution section; base stays untouched; the validation diff should still be clean.
- **Frontmatter-only change.** Apply per platform; trivial, but still verify both trees.
- **New reference file.** If base, author once and copy to both trees. If it documents platform mechanics, it belongs in the execution layer — keep platform-specific content clearly labeled.
- **Pre-existing drift discovered mid-update.** Reconcile it as part of this pass (that is the whole job); note non-trivial reconciliations so the change is reviewable.

---

## 7. Record (layer-4 tie-in)

When the change came from structured feedback, note what was changed and why — this is the self-evolution loop closing. A per-skill friction log (the `scars.md` pattern applied to skills) accumulates these; a skill-change is the compounding output. Keep it lightweight: one line per applied change is enough.
