# Feedback Loop

> **Context:** This reference covers how to handle feedback about generated code and prevent the same mistakes from recurring. Read this when you receive feedback about implementation quality.

---

## When to Record Feedback

Record feedback in progress.md's Implementation Notes section when:
- User says generated code is wrong
- A pattern was used incorrectly
- Code doesn't follow project conventions
- Debugging reveals a systematic issue
- A fix needs to be applied across multiple files

---

## How to Process Feedback

### Step 1: Understand the Issue

When feedback arrives:
1. Identify what was wrong (incorrect pattern, missing convention, bad approach)
2. Understand WHY it was wrong (what should have been done instead)
3. Determine if this is a one-off mistake or a systematic issue

### Step 2: Fix the Triggering Instance

Apply the fix to the specific code that was flagged.

### Step 3: Sweep for Other Instances

**If the issue is systematic** (same pattern used elsewhere):

1. Search the codebase for all instances of the same pattern
2. Apply the same fix to ALL qualifying instances
3. Document the sweep scope

This prevents the same mistake from appearing in later chunks or phases.

### Step 4: Record in Progress Document

Add the feedback to progress.md → Implementation Notes → Decisions Made:

```markdown
### Decisions Made

- **[date]:** User feedback: [description of issue]. Fix: [what was changed].
  Applied to: [list of files/locations]. Rule: [pattern to follow going forward].
```

**Why progress.md instead of a cheat sheet:** This skill is technology-agnostic. There are no framework-specific cheat sheets to update. Instead, lessons learned are recorded in the progress document so they persist across sessions and are visible to all teammates.

### Step 5: Inform Teammates (Team Mode)

If in team mode and the feedback affects other streams:

```
SendMessage:
  type: message
  recipient: [affected-stream-name]
  content: "Pattern correction: [describe the fix and the rule going forward]"
  summary: "Pattern correction from feedback"
```

---

## Mandatory Feedback Triggers

Always process feedback when:
- [ ] User explicitly says the generated code is wrong
- [ ] A pattern was used incorrectly
- [ ] Code doesn't follow existing project conventions
- [ ] Debugging reveals a systematic issue
- [ ] The same mistake has appeared more than once

**Do not wait for multiple occurrences.** Record on first feedback to prevent repetition.
