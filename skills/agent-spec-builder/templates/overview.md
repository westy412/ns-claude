---
system: [system-name]
type: [single-agent | agent-team | nested-teams]
framework: [langgraph | dspy]
status: [draft | complete]
date: YYYY-MM-DD
---

# [System Name] — Overview

<!--
  TEMPLATE INSTRUCTIONS (remove before finalizing):

  This is the system-level "front door" document. It sits above team.md and
  agent.md specs and serves two audiences:
  1. Human reviewers — understand the system at a glance
  2. impl-builder agents — get oriented before diving into team/agent specs

  Sections marked [REQUIRED] must be filled for every spec.
  Sections marked [CONDITIONAL] are included only when applicable.
  Delete unused conditional sections entirely (don't leave empty placeholders).

  Content source for each section is noted in comments.
-->

## Purpose & Context
<!-- [REQUIRED] Source: Phase 1 Discovery — Problem & Purpose, Current State -->

### Problem Statement
<!-- What problem does this system solve? Why does it need to exist? -->
[Description of the problem this agent system addresses]

### Why Agents
<!-- Why an agent system vs traditional code? What makes this an AI problem? -->
[Specific reasoning for why this requires LLM-powered agents]

### Success Criteria
<!-- Measurable outcomes. When is this system "working correctly"? -->
- [Criterion 1]
- [Criterion 2]

---

## System Architecture
<!-- [REQUIRED] Source: Phase 2 High-Level Design — Pattern Selection, Flow Diagram -->

### Architecture Diagram

<!--
  For single agent: show inputs → agent → outputs.
  For agent team: show team flow with pattern annotation.
  For nested/multi-team: show inter-team data flow.
  Use ASCII art. Mermaid optional as secondary.
-->

```
[ASCII art diagram showing how teams/agents connect, data flow,
 and the coordination pattern]
```

### Teams & Agents Summary

<!--
  Quick reference table. Details live in individual team.md and agent.md files.
  For single agent specs, replace with a one-line agent description.
-->

| Team / Agent | Pattern | Purpose | Spec File |
|---|---|---|---|
| [name] | [pattern] | [one-line purpose] | [relative path] |

### Data Flow

<!--
  Trace data from system input to system output.
  For single agents, this can be brief.
  For multi-team systems, show what passes between teams.
-->

| Stage | Input From | Output To | Data Description |
|---|---|---|---|
| [stage] | [source] | [destination] | [what data flows] |

---

## Key Decisions
<!-- [REQUIRED] Source: Phases 1-3 — promoted from progress.md Decisions Made tables

  PURPOSE: These decisions are the design rationale that progress.md captured
  during discovery. They are promoted here so they survive the handoff to
  implementation. Without these, the impl-builder will re-derive or guess at
  choices already made.

  Include decisions that affect implementation. Skip session-management decisions
  (like "use template-based spec approach") that are irrelevant post-handoff.

  Format: Decision → Choice → Rationale (one line each, not paragraphs).
-->

| # | Decision | Choice | Rationale |
|---|---|---|---|
| 1 | [decision topic] | [what was chosen] | [why — one sentence] |

---

## Integration Points
<!-- [CONDITIONAL] Include when the system connects to external services, APIs,
  or other internal systems. Skip for self-contained systems.
  Source: Phase 1 Discovery — Interaction Mode, Integrations & Tools -->

### Upstream Systems
<!-- What sends data to this system? How is it triggered? -->

| System | Trigger / Interface | Data Provided |
|---|---|---|
| [system name] | [HTTP / event / manual] | [what data] |

### Downstream Systems
<!-- What consumes this system's output? -->

| System | Interface | Data Consumed |
|---|---|---|
| [system name] | [HTTP callback / DB write / event] | [what data] |

### External Services
<!-- Third-party APIs, MCP servers, or external tools used by agents -->

| Service | Used By | Purpose | Auth |
|---|---|---|---|
| [service name] | [agent/team name] | [what it does] | [API key / OAuth / none] |

---

## Shared Infrastructure
<!-- [CONDITIONAL] Include when cross-cutting components exist that are NOT owned
  by any single team. Skip for single-agent specs or simple team specs where
  everything is self-contained.
  Source: Phase 1 Discovery — Integrations & Tools, LLM Configuration

  If a separate shared-infrastructure.md exists, summarize and reference it.
  If not, document shared components inline here. -->

### Shared Components

| Component | Purpose | Used By |
|---|---|---|
| [component name] | [what it does] | [which teams/agents] |

<!-- If a detailed shared infrastructure document exists: -->
**Full details:** [shared/shared-infrastructure.md](shared/shared-infrastructure.md)

### LLM Strategy
<!-- Model allocation across agents. Source: Phase 1 Discovery — LLM Configuration -->

| Model | Provider | Used For | Reasoning |
|---|---|---|---|
| [model name] | [provider] | [which agent roles] | [why this model for these roles] |

---

## Endpoint Contracts
<!-- [CONDITIONAL] Include when the system exposes HTTP endpoints or has formal
  API contracts. Skip for embedded agent systems with no HTTP surface.
  Source: Phase 1 Discovery — Inputs & Outputs, Phase 3 Agent Detail

  If a separate endpoint-contracts.md exists, summarize and reference it.
  If not, provide a quick reference table here. -->

### Endpoints Summary

| Endpoint | Method | Input | Output | Program/Agent |
|---|---|---|---|---|
| [path] | [POST/GET] | [schema name] | [schema name] | [which handles it] |

**Full contracts:** [shared/endpoint-contracts.md](shared/endpoint-contracts.md)

---

## Output Models
<!-- [CONDITIONAL] Include when the system produces structured output models that
  are shared across multiple teams/agents (e.g., discriminated unions, shared
  Pydantic models). Skip if each agent has its own simple output.
  Source: Phase 3 Agent Detail — structured output definitions

  If a separate output-models.md exists, summarize and reference it. -->

### Models Summary

| Model | Discriminator | Used By | Key Fields |
|---|---|---|---|
| [model name] | [format_type value] | [which programs/agents] | [notable fields] |

**Full definitions:** [shared/output-models.md](shared/output-models.md)

---

## Migration Context
<!-- [CONDITIONAL] Include ONLY when this system replaces an existing system.
  Delete entirely for greenfield projects.
  Source: Phase 1 Discovery — Current State & Constraints

  If a separate MIGRATION-NOTES.md exists, summarize and reference it. -->

### What Changes

| Change Type | Item | Details |
|---|---|---|
| Removed | [endpoint/feature] | [why removed] |
| New | [endpoint/feature] | [why added] |
| Modified | [endpoint/feature] | [what changed] |

### Preserved Contracts
<!-- What MUST remain identical to the existing system for compatibility -->
- [contract/model that must not change]

**Full migration notes:** [MIGRATION-NOTES.md](MIGRATION-NOTES.md)

---

## Domain Context
<!-- [CONDITIONAL] Include when domain-specific knowledge is needed to understand
  the system. Skip when the domain is self-evident from the purpose section.
  Source: Phase 1 Discovery — any domain-specific findings

  For large domain models, link to a separate definitions document. -->

### Key Concepts

| Term | Definition |
|---|---|
| [domain term] | [what it means in this context] |

### Domain Constraints
<!-- Hard rules from the business domain that constrain agent behavior -->
- [constraint 1]
- [constraint 2]

---

## System Constraints
<!-- [REQUIRED] Source: Phase 1 Discovery — Complexity & Reliability,
  Current State & Constraints -->

### Non-Functional Requirements

| Requirement | Value | Notes |
|---|---|---|
| Interaction mode | [user-facing / autonomous / agent-facing] | [implications] |
| Error tolerance | [strict / best-effort] | [retry/fallback strategy] |
| Latency | [real-time / async acceptable] | [SLA if any] |
| Scale | [expected volume] | [concurrency needs] |
| Cost | [budget constraints] | [affects model selection] |

---

## Reading Guide
<!-- [REQUIRED] Source: Generated from manifest.yaml file list + section purposes.
  This tells the impl-builder (and human reviewers) what to read and in what order. -->

### For Implementation (impl-builder reading order)

1. **This document** (`overview.md`) — System context, architecture, key decisions
2. **`manifest.yaml`** — Hierarchy, file locations, execution plan
3. **Shared documents** (if they exist):
   - `shared/shared-infrastructure.md` — Cross-cutting utilities and LM config
   - `shared/output-models.md` — Pydantic model definitions
   - `shared/endpoint-contracts.md` — API surface and schemas
4. **Per-team specs** (in execution plan order):
   - `[team-name]/team.md` — Team orchestration and flow
   - `[team-name]/agent-config.yaml` — Machine-readable agent configuration
   - `[team-name]/agents/*.md` — Individual agent specs

### File Map

<!--
  Annotated listing of all spec files with purpose.
  Generated from manifest.yaml files section.
-->

| File | Purpose |
|---|---|
| `overview.md` | System-level context and architecture (this file) |
| `manifest.yaml` | Machine-readable hierarchy + execution plan |
| `progress.md` | Session tracking (spec-builder internal, not for impl-builder) |
| [additional files from manifest] | [purpose] |
