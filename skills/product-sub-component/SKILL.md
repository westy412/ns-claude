---
name: product-sub-component
description: Extract and structure sub-component documents with entity journeys from client call transcripts. Conversational — extracts journeys, acceptance criteria, and data requirements at the granular buildable level.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
argument-hint: "[transcript file path]"
---

> **Invoke with:** `/product-sub-component` | **Keywords:** sub-component, entity journey, user journey, acceptance criteria, detailed extraction

Extract sub-component detail from client call transcripts — entity journeys, acceptance criteria, data requirements, and granular functional requirements. This is the most concrete level: output feeds directly into the development workflow.

**Input:** A transcript file covering detailed discussion of specific features within a component
**Output:** Sub-component documents with entity journeys in the project's component directory

## Prerequisites

A component document must exist for the parent component. Sub-components are identified during component extraction and detailed here.

## Reference Files

| Topic | Reference File | When to Load |
|-------|---------------|--------------|
| Extraction guidance | [sub-component-extraction.md](references/sub-component-extraction.md) | Always — entity journey extraction, decomposition triggers |

## Templates

| Template | Purpose | When to Load |
|----------|---------|-------------|
| [sub-component.md](templates/sub-component.md) | Sub-component document — 8 sections with entity journeys | Always — the target structure |

## Key Principles

1. **Entity journeys are the core deliverable.** Each journey: entity + input + steps (Mermaid) + outcome + acceptance criteria. This is what gets built.

2. **Entity journeys, not just user journeys.** Entities can be users (UI) or agents (event processing). The template handles both.

3. **Product experience, not technical architecture.** Describe what the entity interacts with. Frontend/backend split happens in the development workflow.

4. **Atomic journeys.** Each journey should be completable within this sub-component. Cross-cutting journeys spanning multiple components are documented separately.

5. **Acceptance criteria are evals.** Write them so someone can verify each one against the built product.

6. **Recursive decomposition.** If a sub-component is too large (multiple distinct journeys that don't share state, own sub-parts that could be built independently), propose further decomposition.

7. **Knowledge-graph integrity — never write a dangling wikilink.** Every `[[link]]` must resolve to a file that exists. Reference not-yet-documented items as **plain text** (or create a stub first); add the `[[link]]` only once the file exists. Use shortest-path links (`[[name]]`, not `[[../name]]` or `[[sub-components/name]]`). After writing, run `python3 scripts/check-wikilinks.py` and fix anything it reports.

8. **Open questions go in the register.** Don't bury open questions at the bottom of a doc — add them to the central [[open-questions]] register and leave a short inline marker `_[⚠ open — see [[open-questions]] #N]_` where relevant.

9. **Status reflects real coverage.** Only mark a sub-component **Defined** after a dedicated deep-dive produced its entity journeys and acceptance criteria. Don't present inferred acceptance criteria as decided.

## Flow

```
User invokes /product-sub-component with a transcript path
    │
    ▼
Load sub-component-extraction.md + sub-component template
    │
    ▼
Read existing state:
    - Parent component document (context + identified sub-components)
    - Any existing sub-component documents
    - Vision document (overall context)
    │
    ▼
Read the full transcript
    │
    ▼
Identify which sub-components are discussed + coverage depth
    │
    ▼
For each sub-component with sufficient coverage:
    │
    Work through the 8 template sections:
    │
    Focus especially on Section 3 (Entity Journeys):
    1. Identify journeys described in the transcript
    2. Extract: entity, input, steps, outcome
    3. Propose Mermaid flowchart
    4. Derive acceptance criteria
    5. Present to user for confirmation
    │
    ▼
Check for further decomposition:
    │
    "This sub-component feels large — it has multiple distinct journey
     sets and its own sub-parts. Should we decompose further?"
    │
    ▼
After extraction:
    │
    1. Write sub-component documents
    2. Backfill the parent component's Sub-Components table (replace plain text with a [[link]] now this doc exists)
    3. Add wikilinks — up to the parent ([[component-name]], shortest-path) and cross-links to siblings that already exist
    4. Produce gap analysis
    5. Questions for next call
    6. Validate the graph — run `python3 scripts/check-wikilinks.py` and fix any broken links
```

## Entity Journey Extraction

When extracting journeys from transcripts:

**User journeys** — have a UI component: user sees, clicks, inputs something.

**Agent journeys** — event-driven: event arrives, agent processes, produces output. No UI.

**Hybrid journeys** — user triggers, agent processes in background, result appears in UI. Document as a single journey with clear handoff points.

For each journey:
1. Identify the entity and trigger
2. Map the steps (what happens in sequence, what decision points)
3. Define the successful outcome
4. Derive acceptance criteria from both explicit statements and implicit requirements
5. Propose a Mermaid `graph TD` flowchart

## Interaction Style

**Opening:** State which sub-components are discussed and at what depth. Note any that are candidates for further decomposition.

**During extraction:** Journey-focused. Present each extracted journey with its diagram and acceptance criteria. Ask: "Does this match? Anything missing?"

**Closing:**
1. Summary of journeys documented per sub-component
2. Gaps — missing journeys, incomplete criteria, unknown data requirements
3. Further decomposition recommendations if any
4. Questions for next call

## Related Skills

- `/product-manager` — General PM thinking partner
- `/product-component` — Component extraction (prerequisite for this skill)
- `/product-vision` — Vision extraction (establishes overall context)
