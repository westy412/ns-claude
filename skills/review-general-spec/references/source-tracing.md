# Source Material Tracing: General Spec

> Cross-reference every requirement, decision, constraint, and scope item from source materials into the spec. Identify coverage gaps, misinterpretations, and fidelity issues.

---

## Why This Matters

Missing discovery items cause scope drift during implementation. Misinterpretations cause rework. The spec is the single source of truth for the implementation agent — if something was decided in discovery but didn't make it into the spec, the agent won't know about it.

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
- **Problem statement elements** — who has the problem, what the problem is, why it matters, what success looks like
- **Each key decision** — the decision itself AND its rationale (rationale matters because it constrains implementation choices)
- **Each constraint** — hard constraints (must respect) and soft constraints (should respect)
- **Each scope-in item** — what's explicitly included
- **Each scope-out item** — what's explicitly excluded (these should appear as excluded or absent in spec)
- **Each deferred item** — what's deferred to later (spec should acknowledge these exist but are not in scope)
- **Each open question** — should be resolved in spec or explicitly marked as still open
- **Reference files** — files consulted during discovery that the spec should also reference
- **Success criteria** — if the discovery defines success metrics

### From Brainstorm (if present)

- Ideas at "shaped" or "ready" maturity that were carried into discovery
- Key connections between ideas that influenced the system design
- Specific requirements or constraints that emerged from brainstorming discussion

### From Research (if present)

- Technical findings that should inform implementation decisions
- Constraints discovered through research (API limits, library limitations, etc.)
- Recommended approaches or patterns

---

## Step 2: Build Traceability Matrix

For each extracted item, search the spec for where it appears. Use both keyword matching and semantic matching (the spec may express the concept differently).

| # | Source | Item Summary | Found? | Spec Location | Fidelity |
|---|--------|-------------|--------|---------------|----------|
| 1 | Discovery: Decision 1 | [brief description] | YES/NO/PARTIAL | [section name] | FAITHFUL/DIVERGED/MISSING |
| 2 | Discovery: Constraint 1 | [brief description] | YES/NO/PARTIAL | [section name] | FAITHFUL/DIVERGED/MISSING |
| ... | | | | | |

**Fidelity definitions:**
- **FAITHFUL** — spec captures the item accurately, preserving intent
- **DIVERGED** — spec captures something related but the meaning has shifted or detail is lost
- **MISSING** — item does not appear in the spec at all

---

## Step 3: Classify Gaps

For each MISSING or DIVERGED item, classify importance:

| Importance | Criteria | Examples |
|------------|----------|----------|
| CRITICAL | Core requirement, hard constraint, or key decision that directly affects what gets built | A decision to use JWT auth not captured; a hard constraint on response time missing |
| MODERATE | Important context or secondary requirement that shapes implementation quality | Soft constraint on code style; secondary user persona not mentioned |
| MINOR | Nice-to-have context, deferred items acknowledged elsewhere, or background information | A deferred feature mentioned in discovery but not explicitly listed as deferred in spec |

---

## Step 4: Produce Coverage Report

### Coverage Summary

| Source | Total Items | Covered | Partial | Missing | Coverage % |
|--------|------------|---------|---------|---------|------------|
| Discovery | | | | | |
| Brainstorm | | | | | |
| Research | | | | | |
| **Total** | | | | | |

### Coverage Gaps (CRITICAL first, then MODERATE, then MINOR)

For each gap, provide:

| # | Importance | Source Item | Source Location | Why It Matters | Suggested Addition |
|---|-----------|-------------|-----------------|----------------|-------------------|
| 1 | CRITICAL | [item] | [doc: section] | [impact if missing] | [what to add and where in spec] |

### Misinterpretations

Where the spec captured something but changed the meaning:

| # | Source Item | Source Says | Spec Says | Impact | Suggested Fix |
|---|------------|-------------|-----------|--------|---------------|
| 1 | [item] | [original meaning] | [spec's version] | [what goes wrong] | [how to fix] |

---

## Scoring

- **FAIL** if any CRITICAL item is MISSING
- **FAIL** if any item is DIVERGED in a way that would cause implementation errors
- **WARN** if MODERATE items are MISSING
- **WARN** if there are misinterpretations (even on non-critical items)
- **PASS** if all CRITICAL and MODERATE items are FAITHFUL
