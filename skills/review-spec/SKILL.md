---
name: review-spec
description: Routes to review-general-spec or review-agent-spec based on the spec type provided. Maintained for backward compatibility — prefer invoking the specific skill directly.
allowed-tools: Read Glob Grep AskUserQuestion Skill
---

# Review Spec (Router)

> **This is a routing skill.** It detects the spec type and delegates to the appropriate review skill. For direct invocation, use `/review-general-spec` or `/review-agent-spec` instead.

---

## Step 1: Identify Spec Type

Read the spec path provided by the user.

**If it's a single `.md` file** with a Meta table containing `Type:` (backend-api, frontend, hybrid, etc.):
- This is a **General Spec** — invoke `/review-general-spec`

**If it's a folder containing `manifest.yaml`:**
- This is an **Agent Spec** — invoke `/review-agent-spec`

**If it's a directory containing `spec.md`:**
- This is a **General Spec** in the new folder convention — invoke `/review-general-spec` with the path to `spec.md`

**If it's a directory containing a `spec/` subdirectory with `manifest.yaml`:**
- This is an **Agent Spec** in the new folder convention — invoke `/review-agent-spec` with the path to the `spec/` directory

**If unclear**, ask the user which spec builder produced it.

---

## Step 2: Delegate

Pass the spec path and any source material paths the user provided to the appropriate skill. The delegated skill handles all review logic, source tracing, ambiguity analysis, and output.
