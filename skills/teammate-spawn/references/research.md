# Profile: Research

> A read-only sub-agent that explores and **returns findings**. The leanest profile — keeps large context out of the parent.

Use for codebase exploration, API/doc lookup, or any "find out X" task where nothing is edited.

## Fill the template

Template: `templates/teammate-prompt-research.md`. Fields:

| Field | Required | Notes |
|-------|----------|-------|
| Agent name, workflow | Yes | identity |
| Research questions | Yes | the specific questions to answer |
| Where to look | Optional | files, dirs, docs, or URLs to start from |

## Final response = findings + sources

Answer the questions concisely, each with sources (file paths, line numbers, URLs). Surface what you could not determine. No ownership, no state, no validation — this agent only reads and reports.
