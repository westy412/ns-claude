---
name: agent-spec-builder
description: Design agent systems through collaborative discovery and produce specifications for implementation. Acts as a design consultant - brainstorms with users, asks questions, and produces specs detailed enough for agent-impl-builder to work autonomously. Use when starting a new agent or agent team project.
allowed-tools: Read, Glob, Grep, Task, AskUserQuestion
---

# Agent Spec Builder Skill

## Purpose

A design consultant skill that helps users design agent systems through collaborative discovery. The spec is an output from consulting, brainstorming, and planning with the user - not a form to fill out.

**Goal:** Produce specifications detailed enough for agent-impl-builder to work autonomously.

---

## When to Use This Skill

Use this skill when:
- Starting a new agent or agent team project
- User needs help thinking through an agent system design
- Capturing requirements before implementation

**Skip this skill when:**
- Implementing an existing specification (use agent-impl-builder instead)
- Only modifying prompts (use prompt-engineering directly)

---

## Key Principles

1. **Design consultant, not form-filler** — Brainstorm with user, ask questions, help them think through their system
2. **First question: Single agent or agent team?** — Not everything needs a multi-agent system
3. **Always ask framework preference** — NEVER assume LangGraph or DSPy. Even if existing code uses one framework, the user may want to use the other for the new system. Ask explicitly.
4. **Incremental, top-down** — High-level first, then granular details
5. **Progress tracking** — Maintain progress document for handover between sessions
6. **User approval required** — Before handoff to agent-impl-builder
7. **Ask when unsure** — Never guess. If unclear about requirements, APIs, or approach, ask the user
8. **Context-conscious loading** — Load child skills one at a time, only at the phase that needs them. Never invoke multiple skills preemptively. Persist all decisions to progress.md before moving to the next phase so a new session can resume without re-reading everything.
9. **Ask on ambiguity** — When encountering unclear requirements, especially around hierarchical outputs (campaigns containing posts), field population mechanisms (how scores are assigned to nested objects), or diversity enforcement (hard constraint vs soft signal), ask the user rather than guessing. Ambiguity in the spec becomes bugs in the implementation.
10. **Research data contracts** — Before defining input/output models, check if there's an existing API, database schema, or upstream service that defines the entities being processed. Understand what data actually flows through the system — field names, types, optional vs required. Use real data structures from the existing system, not imagined ones. If the project has an API spec, read it. If there's a database schema, reference it.
11. **No code examples in specs** — Specs describe WHAT should happen (behavior, data flow, acceptance criteria), not HOW to implement it. Do not include Python code examples, pseudo-code implementations, or framework-specific patterns in specs. Schemas (Pydantic model definitions, API contracts) are acceptable because they describe data structure. But implementation code (how to call DSPy, how to set up retry logic) belongs in skills, not specs. If a spec's code example conflicts with a skill rule, the skill wins — so avoid the conflict by not putting code in specs.

---

## When to Ask for Feedback

**Always ask the user when:**
- **Framework choice (LangGraph vs DSPy)** — NEVER default based on existing codebase. Always ask explicitly, even if other agents in the repo use a specific framework.
- Unsure which API/library to use for a tool
- Multiple valid approaches exist (present options)
- Requirements are ambiguous
- You need to make assumptions
- Tool documentation is unclear or missing
- You're not confident about a design decision

**How to ask:**
> "I'm not sure about [specific thing]. Could you clarify [specific question]?"
> "I found multiple options for [tool/approach]. Which would you prefer: [Option A] or [Option B]?"
> "The documentation for [API] doesn't specify [detail]. Do you know how this works?"

**Never:**
- **Assume framework choice** — Do not default to LangGraph or DSPy based on existing codebase patterns. Always ask.
- Guess at API endpoints or authentication methods
- Assume tool implementations without verification
- Make design decisions without user input when multiple valid options exist
- Leave vague specifications that will cause impl-builder to guess

---

## Child Skills (Just-in-Time Loading)

**CONTEXT BUDGET RULE: Only invoke ONE child skill at a time, and ONLY when you reach the phase that needs it.** Loading all skills upfront will exhaust the context window and cause session failure.

| Skill | Invoke At | What It Provides |
|-------|-----------|------------------|
| `tools-and-utilities` | Phase 1, Section 6 (Tools) | Tool vs utility decision tree, design patterns |
| `agent-teams` | Phase 2 (Pattern Selection) | Team patterns (pipeline, router, loop, fan-out), selection criteria |
| `individual-agents` | Phase 3 (Agent Types) | Agent type definitions (LLM, Tool, Router, etc.), selection criteria |
| `prompt-engineering` | Phase 3 (Prompt Config) | Prompt frameworks, roles, modifiers reference |

**How to invoke (one at a time):**
```
Skill tool → skill: "agent-teams"
```

**Loading rules:**
1. DO NOT invoke any child skill until you reach the phase that requires it
2. Before invoking a child skill, update progress.md with ALL decisions made so far
3. After completing the phase that used a child skill, update progress.md with all new decisions before proceeding
4. If context is getting large, trigger the Handover Protocol BEFORE loading the next skill

**Why just-in-time:** Each child skill loads substantial reference material (hundreds to thousands of lines). Loading all four at once consumes ~15,000+ lines of context, leaving insufficient room for the actual design work and user conversation.

---

## Sub-Agents for Delegation

Child skills load into YOUR context window. Sub-agents run in their OWN context window and auto-load their own skills. Use sub-agents to offload analysis that requires skill knowledge without consuming your context budget.

| Sub-Agent | What It Does | When to Use |
|-----------|-------------|-------------|
| `agent-type-advisor` | Proposes agent types with reasoning | Phase 3a — after Phase 2 complete |
| `prompt-config-advisor` | Proposes prompt configs with reasoning | Phase 3b — after types validated |
| `team-spec-writer` | Writes team.md + agent-config.yaml | Phase 3c — after all decisions validated |
| `agent-spec-writer` | Writes complete agent spec files | Phase 3d — fills in placeholders |

```
Execution flow:
├── agent-type-advisor (all agents) → user validates → save to progress.md
├── prompt-config-advisor (can batch) → user validates → save to progress.md
├── team-spec-writer → creates structure
└── agent-spec-writer (parallel batches of 5-6) → fills in specs
```

**Detailed spawn examples, batching strategies, and step-by-step flow:** Read `references/sub-agent-delegation.md`

---

## Workflow Overview

```
Setup → Discovery → High-Level Design → Agent Detail (per agent) → Finalize Spec → Execution Plan
```

**Incremental write pattern:** At each phase, the cycle is:
1. **Load** the skill needed for this phase (one at a time)
2. **Discuss** with the user — present options, ask questions, get decisions
3. **Write** the spec output for this phase (don't accumulate — write it NOW)
4. **Save** everything to progress.md — decisions, reasoning, thoughts, context
5. **Advance** to the next phase (or handover if context is getting large)

**Critical rule:** Write spec files at each phase, not all at the end. By the time you finish a phase, the corresponding spec sections should exist on disk. Progress.md must capture enough detail (including reasoning and thought process) that a new session can resume without re-discussing anything.

---

## Phase Reference

| Phase | Purpose | Reference | Skill to Load |
|-------|---------|-----------|---------------|
| **0** | Setup — project folder, spec directory, resumption | `references/phase-0-setup.md` | — |
| **1** | Discovery — 8 areas of requirements gathering | `references/phase-1-discovery.md` | `tools-and-utilities` (Section 6) |
| **2** | High-Level Design — single vs team, pattern selection | `references/phase-2-high-level-design.md` | `agent-teams` |
| **3** | Agent Detail — per-agent type, prompt config, I/O | `references/phase-3-agent-detail.md` | `individual-agents`, then `prompt-engineering` |
| **4** | Generate Spec — folder structure, files, validation | `references/phase-4-generate-spec.md` | — |
| **5** | Execution Plan — implementation phases, streams | `references/phase-5-execution-plan.md` | — |

### Phase Quick Decision

```
Starting fresh?
├── New project → Phase 0 (Setup) → references/phase-0-setup.md
└── Resuming → Read progress.md → jump to indicated phase

At Phase 0 complete:
└── Phase 1 (Discovery) → references/phase-1-discovery.md
    └── Cover 8 areas, invoke tools-and-utilities at Section 6

At Phase 1 complete:
└── Phase 2 (High-Level Design) → references/phase-2-high-level-design.md
    ├── Single agent? → Skip to Phase 3 (single agent detail)
    └── Agent team? → Invoke agent-teams skill, select pattern

At Phase 2 complete:
└── Phase 3 (Agent Detail) → references/phase-3-agent-detail.md
    ├── Direct: Load individual-agents, then prompt-engineering
    └── Delegated: Spawn sub-agents → references/sub-agent-delegation.md

At Phase 3 complete:
└── Phase 4 (Generate Spec) → references/phase-4-generate-spec.md
    └── Run ALL validation checks before proceeding

At Phase 4 complete:
└── Phase 5 (Execution Plan) → references/phase-5-execution-plan.md
```

---

## Tools vs Utilities

| Level | What | Examples |
|-------|------|----------|
| **Agent tools** | Individual agent capabilities | Search API, database query, code execution |
| **Team utilities** | Shared integrations at team level | Teams webhook, WhatsApp API, email service |

---

## Output of This Skill

A complete specification folder containing:
1. `progress.md` — Handover document with all decisions and progress
2. `agent-config.yaml` — Machine-readable configuration
3. `team.md` — Team overview and orchestration
4. `{agent}.md` files — Detailed spec for each agent
5. `manifest.yaml` — System hierarchy + **execution plan** for implementation

This feeds into the `agent-impl-builder` skill.

---

## Handover Protocol

When context is getting large or a session is ending, follow the handover protocol to persist state for cold-start resumption.

**Detailed steps and triggers:** Read `references/handover-protocol.md`

---

## Templates

All templates are in `templates/` folder:

| Template | Purpose |
|----------|---------|
| `templates/manifest.yaml` | Entry point for impl-builder (hierarchy + file list) |
| `templates/progress.md` | Progress and handover tracking |
| `templates/agent-config.yaml` | Configuration file with examples |
| `templates/team.md` | Team specification |
| `templates/agent.md` | Individual agent specification |

---

## References

- `references/sub-agent-delegation.md` — Sub-agent spawn examples, batching, flow
- `references/phase-0-setup.md` — Project setup and resumption
- `references/phase-1-discovery.md` — 8 discovery areas + tools deep-dive
- `references/phase-2-high-level-design.md` — Single vs team, pattern selection
- `references/phase-3-agent-detail.md` — Per-agent detail capture
- `references/phase-4-generate-spec.md` — Spec folder structure, nesting, validation
- `references/phase-5-execution-plan.md` — Implementation task grouping, streams
- `references/handover-protocol.md` — Handover steps and triggers
- `agent-teams/SKILL.md` — Team pattern selection criteria (child skill)
- `individual-agents/SKILL.md` — Agent type selection criteria (child skill)
- `prompt-engineering/SKILL.md` — Prompt configuration (child skill)
