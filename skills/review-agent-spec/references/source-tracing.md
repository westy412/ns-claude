# Source Material Tracing: Agent Spec

> Cross-reference every requirement, decision, constraint, and scope item from source materials into the agent spec. Identify coverage gaps, misinterpretations, and fidelity issues — with special attention to how requirements map to agent boundaries and data flow.

---

## Why This Matters

Missing discovery items cause scope drift during implementation. For agent specs, this is especially dangerous because requirements must be decomposed across multiple agents — a missed requirement may mean an entire agent is under-specified or a data flow path is incomplete.

---

## Source Material Types

| Type | Frequency | What to Extract |
|------|-----------|-----------------|
| Discovery document | Always | Requirements, decisions + rationale, constraints, scope (in/out/deferred), open questions, reference files |
| Brainstorm / idea cards | ~20% | Key ideas at shaped/ready maturity, connections that influenced design |
| Research documents | Occasionally | Technical findings, API constraints, performance benchmarks, recommended approaches |

---

## Step 1: Extract Traceable Items

Read each source document and extract a numbered list of discrete, traceable items.

### From Discovery Document

Extract each of these as separate items:
- **Problem statement elements** — who, what, why, success criteria
- **Each key decision** — the decision AND its rationale
- **Each constraint** — hard and soft
- **Each scope-in item**
- **Each scope-out item** — should be absent or explicitly excluded
- **Each deferred item** — spec should acknowledge but not implement
- **Each open question** — should be resolved or marked as still open
- **Reference files**
- **Success criteria**
- **Integration requirements** — external APIs, databases, services
- **Tool/integration decisions** — specific tools or services chosen

### From Brainstorm (if present)

- Ideas at "shaped" or "ready" maturity carried into discovery
- Key connections between ideas that influenced system design
- Specific requirements that emerged from brainstorming

### From Research (if present)

- Technical findings informing implementation
- Constraints discovered through research
- Recommended approaches or patterns

---

## Step 2: Build Traceability Matrix

For each extracted item, search the spec for where it appears. Check across all spec files: `manifest.yaml`, `overview.md`, `team.md`, `agent-config.yaml`, and individual `agents/*.md` files.

| # | Source | Item Summary | Found? | Spec File(s) | Fidelity |
|---|--------|-------------|--------|-------------|----------|
| 1 | Discovery: Decision 1 | [brief] | YES/NO/PARTIAL | [file:section] | FAITHFUL/DIVERGED/MISSING |

**Fidelity definitions:**
- **FAITHFUL** — spec captures the item accurately, preserving intent
- **DIVERGED** — spec captures something related but meaning has shifted
- **MISSING** — item does not appear in any spec file

---

## Step 3: Agent-Specific Tracing

Beyond general traceability, verify these agent-specific mappings:

### Requirement-to-Agent Mapping

For each requirement from discovery, identify which agent(s) are responsible:

| Requirement | Responsible Agent(s) | Captured in Agent Spec? | Notes |
|-------------|---------------------|------------------------|-------|
| [requirement] | [agent name] | YES/NO/PARTIAL | |

FAIL if a requirement has no responsible agent.
WARN if a requirement spans multiple agents but the handoff isn't defined.

### Scope-to-Boundary Mapping

Verify that scope decisions from discovery align with agent boundaries:

| Scope Decision | Agent Boundary | Aligned? | Notes |
|---------------|----------------|----------|-------|
| [in/out/deferred item] | [which agent's scope] | YES/NO | |

### Tool/Integration Mapping

Verify that tool and integration decisions from discovery appear in agent tool definitions:

| Discovery Decision | Expected in Agent | Found in Tools? | Notes |
|-------------------|-------------------|-----------------|-------|
| [tool/API decision] | [agent name] | YES/NO | |

### Data Flow Alignment

Verify that data flow decisions from discovery match the agent pipeline:

| Discovery Data Flow | Spec Data Flow | Aligned? | Notes |
|--------------------|----------------|----------|-------|
| [how data moves] | [how spec defines it] | YES/NO | |

---

## Step 4: Classify Gaps

For each MISSING or DIVERGED item, classify importance:

| Importance | Criteria |
|------------|----------|
| CRITICAL | Core requirement, hard constraint, key decision, or missing agent responsibility |
| MODERATE | Important context, secondary requirement, or incomplete tool definition |
| MINOR | Nice-to-have context, deferred items acknowledged elsewhere |

---

## Step 5: Produce Coverage Report

### Coverage Summary

| Source | Total Items | Covered | Partial | Missing | Coverage % |
|--------|------------|---------|---------|---------|------------|
| Discovery | | | | | |
| Brainstorm | | | | | |
| Research | | | | | |
| **Total** | | | | | |

### Coverage Gaps (CRITICAL first)

| # | Importance | Source Item | Source Location | Why It Matters | Suggested Addition |
|---|-----------|-------------|-----------------|----------------|-------------------|

### Misinterpretations

| # | Source Item | Source Says | Spec Says | Impact | Suggested Fix |
|---|------------|-------------|-----------|--------|---------------|

### Agent-Specific Gaps

| # | Gap Type | Detail | Affected Agent(s) | Suggested Fix |
|---|----------|--------|--------------------|---------------|

---

## Scoring

- **FAIL** if any CRITICAL item is MISSING
- **FAIL** if any requirement has no responsible agent
- **FAIL** if any item is DIVERGED in a way that would cause implementation errors
- **WARN** if MODERATE items are MISSING
- **WARN** if there are misinterpretations
- **WARN** if tool/integration mappings are incomplete
- **PASS** if all CRITICAL and MODERATE items are FAITHFUL
