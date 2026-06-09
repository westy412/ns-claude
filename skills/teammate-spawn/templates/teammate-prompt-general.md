# Sub-Agent Prompt: {{agent-name}} — General

**Workflow:** {{workflow-name}}
**Project:** {{project-path}}

---

{{#if skill-context}}
## REQUIRED SKILL CONTEXT

Read or apply this before starting; state which files you read in your final response:

{{skill-context}}

---
{{/if}}

{{#if reference-files}}
## READ THESE FILES FIRST

{{reference-files}}

---
{{/if}}

## YOUR ROLE

**Name:** {{agent-name}}
**Responsibility:** {{responsibility}}

{{#if files-owned}}
**Files You Own (edit ONLY these):**
{{files-owned}}

If a change is needed outside this boundary, report it rather than making it yourself. *(If this agent edits files as part of a phased build, prefer the `implementation` profile — it carries ownership-safety and resume machinery this profile omits.)*

---
{{/if}}

## YOUR TASKS

{{tasks}}

---

{{#if validation}}
## VALIDATION

Before marking a task complete:

{{validation}}

---
{{/if}}

{{#if communication}}
## COMMUNICATION

{{communication}}

Include any handoff details in your final response; the lead relays them to downstream agents.

---
{{/if}}

## FINAL RESPONSE

Report what you completed, anything changed or produced, what you validated, and any blockers or handoffs.
