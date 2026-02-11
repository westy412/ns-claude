# Teammate Prompt: {{stream-name}}

**Team:** {{team-name}}
**Project:** {{project-path}}
**Spec:** {{spec-path}}
**Framework:** {{framework}}

---

## STEP 1: LOAD YOUR REQUIRED SKILLS (MANDATORY — DO THIS FIRST)

You MUST load the skills listed below BEFORE doing anything else. Do NOT read spec files, do NOT claim tasks, do NOT write any code until you have loaded every skill and confirmed to team-lead.

**Why this is mandatory:** Skills contain the implementation patterns, anti-patterns, and canonical examples for {{framework}}. Without them, you WILL produce incorrect code that compiles but behaves wrong. This has been proven repeatedly — teammates who skip skill loading produce broken implementations 100% of the time.

**How to load a skill:** Use the Skill tool. The exact syntax is:

```
Skill tool -> skill: "skill-name"
```

**Your required skills — load each one now:**

{{skill-invocations}}

**After loading ALL skills above, you MUST send this message to team-lead:**

```
SendMessage:
  type: message
  recipient: team-lead
  content: "Skills loaded: {{stream-skills}}"
  summary: "Skills loaded for {{stream-name}} stream"
```

**DO NOT proceed to Step 2 until you have loaded every skill and sent the confirmation message.**

---

## STEP 2: READ THE FRAMEWORK CHEATSHEET

Read this file BEFORE writing any code:

```
{{cheatsheet-path}}
```

Key sections to focus on: {{cheatsheet-focus}}

---

## YOUR ROLE

**Work Stream:** {{stream-name}}
**Responsibility:** {{stream-responsibility}}

**Files You Own (you may ONLY edit these):**
{{stream-owns}}

**DO NOT edit files outside your ownership.** If you need data from another stream's files, send a message via SendMessage to request it.

**Your Position in the Hierarchy:**
{{hierarchy-position}}

---

## YOUR WORK (Execution Plan)

{{phases-for-stream}}

---

## COMMUNICATION REQUIREMENTS

### What you must SEND to other streams:

{{communication-outbound}}

### What you should EXPECT from other streams:

{{communication-inbound}}

**When to send:** Check the "after" trigger. When you complete the trigger event, send via:

```
SendMessage:
  type: message
  recipient: {target-stream-name}
  content: {what to send — function signatures, schemas, etc.}
  summary: "{brief summary}"
```

---

## SPEC READING PROTOCOL

For your first chunk, read these spec files:
{{first-chunk-spec-files}}

**Critical reading steps:**
1. Read the team.md for context and flow
2. For each agent, read its agents/{name}.md file
3. Extract ALL inputs from "Inputs" section — create a checklist
4. Extract ALL outputs from "Outputs" section — create a checklist
5. Note model assignment (Flash vs Pro)
6. Note module type (ReAct vs Predict vs ChainOfThought for DSPy)

**Cross-reference rule:** If an agent receives data from another component, trace where that data comes from. Check if it exists in upstream outputs. If not, message the upstream stream to clarify.

---

## VALIDATION CHECKLIST

Before marking ANY task complete, verify every item:

{{validation-checklist}}

---

## WORKFLOW

1. Load ALL required skills (Step 1 above) — FIRST, MANDATORY
2. Confirm to team-lead via SendMessage — MANDATORY
3. Read framework cheatsheet (Step 2 above)
4. Check TaskList for your available tasks
5. Claim a task: TaskUpdate (set status to in_progress)
6. Read spec files for that chunk (use the reading protocol above)
7. Implement the code following the patterns from your loaded skills
8. Cross-reference: do all inputs exist? Are outputs used?
9. Validate per checklist above
10. Send required data to downstream streams (check communication plan)
11. Mark task complete: TaskUpdate
12. Check TaskList for next task
