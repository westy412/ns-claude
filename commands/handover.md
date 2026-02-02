---
argument-hint: '[linear-issue-id-or-instructions]'
description: Persist state to Git and Linear, then generate a handover message for yourself or the next session.
---

# Handover Procedure

You are preparing a handover for yourself or the next session.

## Philosophy

State lives in **Git** and **Linear**, not in session documents. The handover:
1. Ensures state is persisted to the right places
2. Creates a concise message telling the next session where to look

The next session will read reality (spec + Linear + git) - not this handover message.

---

## Step 1: Persist State

Before creating the handover message, ensure state is properly persisted:

### Update Linear Issue

If working on a Linear issue:
1. **Check off completed tasks** in the issue description
2. **Add a progress comment** summarizing what was done this session
3. **Update issue state** if needed (e.g., move to "In Review" if PR created)

Use `mcp__linear__update_issue` and `mcp__linear__create_comment`.

### Commit Work

If there are uncommitted changes:
1. **Only commit files you worked on** (use `git add <specific-files>`)
2. **Use proper commit format:**
   ```
   NS-XXX: <action-verb> <what>

   WHAT:
   - <change 1>
   - <change 2>

   WHY: <rationale>

   Linear: <issue-url>
   ```
3. Reference the Linear issue ID

### Update Spec (if phase complete)

If a Linear issue (phase) was completed:
1. Check off the Work Breakdown item in the spec
2. Commit the spec: `git commit specs/[name].md -m "NS-XXX: Mark [phase] complete in spec"`

---

## Step 2: Create Handover Message

Output the following in chat (do NOT save to a file):

### Format

```
## Session Handover

### Context
- **Spec**: [path to spec file, or "No spec - working from Linear/conversation"]
- **Linear Issue**: [NS-XXX: Title] or "None"
- **Branch**: [current branch]

### What Was Done
[2-3 bullet points of what was accomplished]

### Git State
[Output of `git log --oneline -5` or note recent commits]

### Next Task
[First unchecked task in the Linear issue, or next phase to start]

### Blockers / Open Questions
[Any HUMAN_NEEDED items or questions for the user]

### How to Resume
1. Read the spec: `[spec path]`
2. Read Linear issue: `[NS-XXX]`
3. Check git log: `git log --oneline -10`
4. Continue from: [specific task or phase]
```

---

## Step 3: Handle Arguments

Analyze the provided argument `$ARGUMENTS`:

**If it's a Linear Issue ID (e.g., NS-123, TEAM-456):**
- Fetch the issue using `mcp__linear__get_issue`
- Include issue details in the handover
- This is the issue being worked on

**If it's NOT a Linear Issue ID and NOT empty (Custom Instructions):**
- The user has provided specific requirements for this handover
- **CRITICAL:** Prioritize these instructions
- Ensure the specific points or requests are explicitly addressed in the handover
- These instructions define what MUST be included

**If empty or "NONE":**
- Check if there's an obvious Linear issue from the conversation
- If none, note "No Linear issue associated"

---

## Key Principles

1. **Don't create session documents** - State lives in Git and Linear
2. **Commit before handover** - Uncommitted work is lost context
3. **Update Linear before handover** - Task checkboxes and comments persist
4. **Keep handover concise** - It's a pointer, not the source of truth
5. **Tell next session WHERE to look** - Not everything that was discussed

$ARGUMENTS
