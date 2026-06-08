---
name: skill-updater
description: Update an existing skill across BOTH the Claude Code (~/.claude/skills) and Codex (~/.codex/skills) trees at once, applying structured feedback and respecting the platform capability boundary. Use when changing, improving, fixing, or reconciling an existing skill. NOT for creating new skills (use skill-builder) or improving agent product systems (use agent-improvement-spec).
allowed-tools: Read, Glob, Grep, Edit, Write, Bash
argument-hint: [skill-name]
---

> **Invoke with:** `/skill-updater` | **Keywords:** update skill, edit skill, improve skill, fix skill, sync skills, reconcile skill, apply skill feedback

Update an existing skill in lockstep across both skill trees. The cardinal rule: **a skill change always lands in both trees** — Claude Code (`~/.claude/skills/`) and Codex (`~/.codex/skills/`) — with shared reasoning kept identical and platform mechanics adapted per platform. Editing one tree alone is how the trees drift; this skill exists to make that impossible to do by accident.

**Input:** a target skill + the change (an explicit request, or structured feedback from the dev-workflow self-evolution log).
**Output:** both trees updated — base content equivalent, execution sections platform-correct, validated.

## When to Use This Skill

Use this skill when:
- Changing, improving, or fixing an existing skill's content.
- Applying structured feedback (the layer-4 friction log) to a skill.
- Reconciling drift between the two trees for a skill.

**Skip this skill when:**
- **Creating a new skill** → use `skill-builder`.
- **Improving an agent _product_ system** (not a skill) → use `agent-improvement-spec` / `agent-improvement-impl`.
- A skill exists in only one tree and the counterpart must be designed from scratch → use `skill-builder` for the missing one, then return here to keep them synced.

## Reference Files

| Topic | Reference File | When to Load |
|-------|---------------|--------------|
| Base vs execution split + Claude↔Codex tool map | [platform-boundary.md](references/platform-boundary.md) | Before applying a change — to classify it as base or execution |
| Full update procedure: intake, classification, validation gate, edge cases | [update-protocol.md](references/update-protocol.md) | When executing an update (from "locate both trees" onward) |

## The two-tree model (why this skill exists)

Every skill factors into:
- **BASE** — the reasoning: elicitation logic, checklists, validation gates, doctrine, templates, reference content. **Platform-neutral. Authored once, identical in both trees.**
- **EXECUTION** — the orchestration mechanics that legitimately differ: spawn-tool names, skill-invocation syntax, frontmatter keys, inter-agent coordination.

The skill format is now a shared open standard (`agentskills.io`), so base content is byte-identical-able across trees. Drift comes from platform nouns threaded *inline* through reasoning prose. Fix it structurally: write base prose in neutral terms and confine platform mechanics to a fenced "Execution" section. The canonical, fully-sourced research lives at `documents/operations/skill-platform-capability-boundary.md` in the cofounder vault.

## Process

Load [update-protocol.md](references/update-protocol.md) for the detailed steps, classification heuristics, validation checklist, and edge cases. In brief:

1. **Intake.** Identify the target skill and the change. If structured feedback exists (a dev-workflow friction log, a review, a critique), read it and extract the concrete change(s). If the request is vague, ask once — what specifically should change, and why. Keep the question brief and specific — one concrete ask; ASCII-sketch the options if structure is involved. This brevity is for the question only; the propose-gate diff (step 5) still shows the full before → after.
2. **Load references.** Read [platform-boundary.md](references/platform-boundary.md). Hold the authoring best practices: SKILL.md is a routing layer < 300 lines; reference files are one-topic, < 200 lines, no frontmatter; progressive disclosure (metadata → instructions → resources).
3. **Locate both trees.** Read the skill at `~/.claude/skills/<name>/` **and** `~/.codex/skills/<name>/` in full, including reference files. If it is missing from one tree, STOP and flag (see protocol edge cases).
4. **Classify & plan.** For each change, decide BASE or EXECUTION and draft the exact edits — but do **not** write yet:
   - BASE → the *same* edit in both trees, in neutral prose.
   - EXECUTION → a per-platform edit using the tool map (Claude tools in the Claude tree, Codex in the Codex tree).
   - Most content changes are base. When in doubt, write it neutral (base) and only fence the part that names a tool.
5. **Propose & confirm (blocking).** Before writing anything, show the user the full change plan — every target file across both trees, with the concrete **before → after** for each edit (or a tight summary + key hunks for large changes), marking base vs execution. **Stop and get explicit approval. Never write a change the user has not seen.** On "adjust", revise and re-propose.
6. **Apply & validate.** Write the approved edits, then re-read both trees and assert the gate: base content equivalent (diff-clean outside fenced execution sections); execution sections platform-correct; line budgets respected; frontmatter correct per platform. On pass, **commit both tree repos** (`~/.claude` and `~/.codex`). Do not finish on unresolved drift.

## Cardinal rules

1. **Both trees, always.** Never edit one tree and leave the other. That single habit is the entire source of the fork drift.
2. **Propose before applying.** Never write a skill change the user has not seen. Surface the full plan — files, trees, before → after — and wait for an explicit go. Skills are shared infrastructure; no silent edits.
3. **Base in neutral prose.** About to write a platform tool name inside reasoning content? Stop — abstract it ("delegate to a research sub-agent", "enforce a phase barrier") and push the concrete name into the fenced execution section.
4. **Design to the common denominator.** Base assumes the parent-orchestrated star (the model both platforms support). Claude's peer-messaging teams are experimental — treat peer-mesh as a Claude-only execution enhancement, never a base assumption.
5. **Validate, then commit both trees.** The dual-tree consistency check is a gate, not a nicety; on pass, commit `~/.claude` and `~/.codex`.
