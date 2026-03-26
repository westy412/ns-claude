---
name: review-spec
description: Validate and review specs produced by general-spec-builder or agent-spec-builder. Identifies structural issues, missing sections, inconsistencies, and anti-patterns before handoff to implementation.
allowed-tools: Read, Glob, Grep, AskUserQuestion
---

# Review Spec Skill

## Purpose

Validate a completed spec before it's handed off to implementation. Catches structural defects, missing sections, inconsistencies, and anti-patterns that would cause implementation failures.

---

## Input

A spec file or spec folder produced by either:
1. **General Spec Builder** — a single `/specs/[name].md` file
2. **Agent Spec Builder** — a spec folder containing `manifest.yaml`, `overview.md`, agent/team specs

---

## Step 1: Identify Spec Type

Read the spec path provided by the user.

**If it's a single `.md` file** with a Meta table containing `Type:` (backend-api, frontend, hybrid, etc.):
- This is a **General Spec** — load `references/review-general-spec.md`

**If it's a folder containing `manifest.yaml`:**
- This is an **Agent Spec** — load `references/review-agent-spec.md`

**If unclear**, ask the user which spec builder produced it.

---

## Step 2: Run Review

Follow the checks in the appropriate reference file. For each check:
- **PASS** — requirement met
- **WARN** — non-blocking issue, flag for user
- **FAIL** — blocking issue, must be fixed before implementation

---

## Step 3: Present Results

Present a summary table:

| Check | Status | Notes |
|-------|--------|-------|
| ... | PASS/WARN/FAIL | ... |

If any FAIL results, list them with specific fix suggestions.

Ask the user: "Want me to fix the issues found, or is the spec good to go?"

---

## References

| Reference | When |
|-----------|------|
| `references/review-general-spec.md` | Spec is a single `.md` from general-spec-builder |
| `references/review-agent-spec.md` | Spec is a folder from agent-spec-builder |
