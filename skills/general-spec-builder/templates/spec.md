# [Work Title]

## Meta

| Field | Value |
|-------|-------|
| Type | backend-api / frontend / agent-langgraph / agent-dspy / hybrid |
| Repo | [repository name] |
| Status | draft / in-progress / complete |
| Created | [date] |

## Overview

[What we're building and why. 2-3 paragraphs max. Operational, not exploratory.]

## Skills

Load these skills before starting:
- [skill-name-1]
- [skill-name-2]

## Requirements

[The actual requirements. What needs to be true when this is done.]

## Architecture

[Key decisions, patterns to follow, constraints. Optional for simple work.]

## Reference Files

<!-- Files consulted during discovery and spec creation. Helps executing agent understand context. -->

**From Discovery:**
- [file paths from discovery document's Reference Files section]

**From Spec Research:**
- [additional files examined during spec creation]

## Execution Plan

<!--
  Phases execute sequentially (Phase 2 starts after Phase 1 completes).
  Chunks within a phase execute in parallel across different agents.
  Work streams group related chunks so the same agent handles them for context continuity.
-->

### Work Streams

| Stream | Responsibility | Owns | Skills |
|--------|---------------|------|--------|
| [stream-name] | [what this stream handles] | [files/directories] | [skills to load] |

### Phase 1: [Name]

| Chunk | Stream | Outcome | Depends On |
|-------|--------|---------|------------|
| [chunk-name] | [stream] | [what success looks like] | — |

**Details:**

- [ ] **[Chunk name]**

  Outcome: [success statement]
  Stream: [stream-name]
  Skills: [skills this chunk's agent should load]

  - [Sub-task 1 — describe WHAT, not HOW]
  - [Sub-task 2]

### Phase 2: [Name]

| Chunk | Stream | Outcome | Depends On |
|-------|--------|---------|------------|
| [chunk-name] | [stream] | [what success looks like] | Phase 1 |
| [chunk-name] | [stream] | [what success looks like] | Phase 1 + [specific-chunk] |

**Details:**

- [ ] **[Chunk name]**

  Outcome: [success statement]
  Stream: [stream-name]
  Skills: [skills to load]

  - [Sub-task 1]
  - [Sub-task 2]

### Communication

| From | To | When | What |
|------|----|------|------|
| [stream] | [stream] | After [chunk/phase] | [what to communicate] |

## Acceptance Criteria

<!-- For the WHOLE spec, not individual chunks. Must be verifiable. -->

- [ ] [Criterion 1 - must be verifiable]
- [ ] [Criterion 2]
- [ ] All tests pass: `[test command]`
- [ ] Linting clean: `[lint command]`

## Completion Promise

<promise>[UNIQUE_COMPLETION_STRING]</promise>

## Notes

[Design decisions made during work, context discovered, etc.]
