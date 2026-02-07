# [Project Name] - Spec Progress

## Status

**Current Phase:** Discovery | High-Level Design | Agent Detail | Generate Spec | Execution Plan
**Current Position:** [Exact description, e.g., "Phase 3 - completed creator agent, starting critic agent"]
**Next Skill to Load:** [none | agent-teams | individual-agents | prompt-engineering | tools-and-utilities]
**Last Updated:** YYYY-MM-DD

### Resumption Instructions

[For a new session: what to do first, what skill to load, what to read. Must be specific enough that a cold-start session can continue without re-reading the discovery document or original handover message.]

---

## Decisions Made

### Core Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Single agent or team? | | |
| Interaction mode | | |
| Framework (LangGraph/DSPy) | | |
| Pattern (if team) | | |

### Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| | | |

---

## Discovery Findings

### Problem & Purpose
**What problem does this solve:**
[Full description, not just a label]

**Why an agent (vs traditional code):**
[Specific reasoning]

**Success criteria:**
[Measurable outcomes]

### Current State & Constraints
**What exists today:**
[Existing systems, code, processes]

**Technical constraints:**
[APIs, latency, cost, etc.]

**Organizational constraints:**
[Compliance, approvals, etc.]

### Interaction Mode
**Mode:** [User-facing | Autonomous | Agent-facing]
**Implications:**
[How this affects design]

### Journey Mapping
**Primary flow:**
[Step-by-step description of the main path]

**Decision points / branches:**
[Where the flow diverges and why]

### Inputs & Outputs
**Triggers:** [What starts the agent/team]
**Inputs:** [Data, format, source]
**Outputs:** [Data, format, consumer]

### Integrations & Tools
[See "Tool Implementation Details" section below for full specs]

**Tools identified:**
- [Tool name] -- [purpose] -- [implementation approach: MCP/API/SDK/Custom]

### Complexity & Reliability
**Expected volume/scale:**
**Error tolerance:**
**Retry/fallback needs:**

### LLM Configuration
**Model strategy:** [Same for all agents / Different per agent]
**Provider:** [Anthropic / OpenAI / Google / Local]
**Cost constraints:**
**Latency requirements:**

---

## Tool Implementation Details

[One section per tool. Capture enough detail that a new session can write the spec without re-researching.]

### [Tool Name]
**Purpose:**
**Implementation type:** [MCP Server | Existing API | SDK/Library | Custom Function]
**API/Library:** [Exact name]
**Documentation URL:**
**Authentication:** [Method + how to obtain credentials]
**Key details:** [Endpoints, methods, rate limits, etc.]
**Error handling notes:**

---

## User Q&A Log

Capture important questions and the user's answers. Prevents re-asking in a new session.

| Question Asked | User's Answer |
|---------------|---------------|
| | |

---

## Design Overview

### System Description
[High-level description once captured]

### Pattern Selected
**Pattern:** [Pipeline | Router | Fan-in-fan-out | Loop | Single Agent]
**Why this pattern:**
[Reasoning for pattern choice]

### Flow Diagram
```
[ASCII art diagram]
```

### Teams/Agents Identified

| Name | Type | Role | Prompt Config | Status |
|------|------|------|---------------|--------|
| | | | Framework: / Role: / Modifiers: | Not started |

---

## Agent Progress

### [Agent Name]
**Type:** [Text Agent | Message Agent | Structured Output Agent | etc.]
**Type rationale:** [Why this type was chosen]
**Prompt config:** Framework: [single-turn/conversational], Role: [role], Modifiers: [list]

- [ ] Purpose section complete
- [ ] Framework & Role reasoning
- [ ] Modifiers defined
- [ ] Inputs/Outputs documented
- [ ] Context flow mapped
- [ ] Domain context captured
- [ ] Behavioral requirements
- [ ] Examples provided

**Key behavioral notes:**
[Important constraints, edge cases, what NOT to do -- captured so a new session does not need to re-derive them]

---

## Open Questions

1.
2.
3.

---

## Next Steps

1.
2.
3.

---

## Session Log

| Date | Phase | Summary | Key Decisions |
|------|-------|---------|---------------|
| | | | |
