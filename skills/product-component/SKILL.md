---
name: product-component
description: Extract and structure component documents from client call transcripts. Conversational — proposes extractions, identifies sub-components, debates with user. Produces component-level documentation in the directory-brain pattern.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
argument-hint: "[transcript file path]"
---

> **Invoke with:** `/product-component` | **Keywords:** component, deep-dive, component extraction, functional parts

Extract component-level content from client call transcripts and structure it into component documents. Works conversationally — proposes what was extracted, surfaces sub-components, debates ambiguity.

**Input:** A transcript file from a client call (typically follow-up calls where specific parts of the product are discussed in detail)
**Output:** Component documents in the project's `components/` directory with Obsidian wikilinks

## Prerequisites

A vision document must exist for the project. Components are identified by decomposing the vision: "in order to deliver this vision to these personas, what functional parts need to exist?"

## Reference Files

| Topic | Reference File | When to Load |
|-------|---------------|--------------|
| Extraction guidance | [component-extraction.md](references/component-extraction.md) | Always — what to listen for, extraction process |

## Templates

| Template | Purpose | When to Load |
|----------|---------|-------------|
| [component.md](templates/component.md) | Component document — 10 sections including risks | Always — the target structure |

## Key Principles

1. **Conversational, not silent extraction.** Propose, ask, flag, debate.

2. **Product components, not technical components.** Think about what the user or agent interacts with — the product experience. Frontend/backend splits are resolved in the development workflow.

3. **Surface sub-components but don't document them.** As detail emerges, propose sub-component bucketing. List them as **plain text** (no wikilinks — their docs don't exist yet), "Collecting" status — detailed documentation happens via `/product-sub-component`.

4. **Persona mapping from vision doc.** Section 1 requires identifying which personas (from the vision) use this component and how. Always consult the vision document's persona list.

5. **Backfill the parent.** After creating a component document, update `components.md` AND the vision document's Components table.

6. **Knowledge-graph integrity — never write a dangling wikilink.** Every `[[link]]` must resolve to a file that exists. Reference not-yet-documented items as **plain text** (or create a stub first); add the `[[link]]` only once the file exists. Use shortest-path links (`[[name]]`, not `[[../name]]` or `[[sub-components/name]]`). After writing, run `python3 scripts/check-wikilinks.py` and fix anything it reports.

7. **Open questions go in the register.** Don't bury open questions at the bottom of a doc — add them to the central [[open-questions]] register and leave a short inline marker `_[⚠ open — see [[open-questions]] #N]_` where relevant.

8. **Status reflects real coverage.** Only mark a component/sub-component **Defined** after a dedicated deep-dive. Semi-structured or partial discussion stays **Collecting/Defining** with a "partially scoped" banner — never "Defined" with inferred acceptance criteria.

## Flow

```
User invokes /product-component with a transcript path
    │
    ▼
Load component-extraction.md + component template
    │
    ▼
Read existing state:
    - Vision document (context + persona list)
    - The component map (`components.md`) — what exists already
    - Any existing component documents
    │
    ▼
Read the full transcript
    │
    ▼
Identify which components are discussed + coverage depth
Present to user: "I see these components discussed. Focus on all or prioritise?"
    │
    ▼
For each component with sufficient coverage:
    │
    Work through the 10 template sections conversationally:
    1. Present extracted content
    2. Ask about ambiguities
    3. Flag gaps
    4. Let user confirm/correct
    │
    ▼
Surface sub-components:
    │
    "From the discussion I can see these natural sub-components: [list].
     Does that match what you heard?"
    │
    ▼
After extraction:
    │
    1. Write/update component documents
    2. Backfill `components.md`
    3. Backfill vision.md Components table
    4. List sub-components in the component's backfill table (plain text — no links until their docs exist)
    5. Produce gap analysis per component
    6. Generate questions for next call
    7. Validate the graph — run `python3 scripts/check-wikilinks.py` and fix any broken links
```

## Handling Multiple Components

When a transcript covers multiple components:
1. Process in order of coverage depth (most detail first)
2. Note cross-references between components (these become dependencies)
3. After all processed, review dependency consistency
4. Update all routing documents

## Interaction Style

**Opening:** Summarise which components are discussed and at what depth. Propose a plan.

**During extraction:** Per template section — show extraction, ask questions, flag gaps.

**Sub-component surfacing:** Present proposed bucketing, let user confirm. Don't over-decompose.

**Closing:**
1. Summary per component
2. Gaps grouped by component and section
3. Questions for next call
4. Updated project directory state

## Related Skills

- `/product-manager` — General PM thinking partner, project setup
- `/product-vision` — Vision extraction (prerequisite for this skill)
- `/product-sub-component` — Sub-component extraction (next step after this)
