---
name: product-vision
description: Extract and structure vision documents from client call transcripts. Conversational — proposes extractions, flags unknowns, debates ambiguity. Produces the top-level product vision following the directory-brain pattern.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
argument-hint: "[transcript file path]"
---

> **Invoke with:** `/product-vision` | **Keywords:** vision, transcript, product vision, first call, what are we building

Extract vision-level content from client call transcripts and structure it into a vision document. Works conversationally — proposes what was extracted, asks about gaps, debates ambiguity with the user who was in the room.

**Input:** A transcript file from a client call (typically the first call or any conversation covering what the product is, who it's for, why it exists)
**Output:** A vision document in the project directory with Obsidian wikilinks

## Reference Files

| Topic | Reference File | When to Load |
|-------|---------------|--------------|
| Extraction guidance | [vision-extraction.md](references/vision-extraction.md) | Always — defines what to listen for, extraction process, gap analysis |

## Templates

| Template | Purpose | When to Load |
|----------|---------|-------------|
| [vision.md](templates/vision.md) | Vision document — 8 sections with detailed extraction guidance per field | Always — the target structure |

## Key Principles

1. **Conversational, not silent extraction.** Propose what you've extracted, ask about ambiguity, debate with the user. They were in the room — you weren't.

2. **Flag unknowns explicitly.** If the transcript doesn't cover something, say so. Never fabricate content to fill gaps.

3. **Collect first, bucket after.** Client conversations are non-linear. Extract all relevant information first, then map to template sections.

4. **Gap analysis drives the next call.** After extraction, produce a clear list of what's still unknown with specific questions for the next conversation.

5. **Build the knowledge graph.** Create wikilinks (only to docs that exist), update parent entry-points (`index.md` / `components.md`), backfill routing tables.

6. **Knowledge-graph integrity — never write a dangling wikilink.** Every `[[link]]` must resolve to a file that exists. List not-yet-created components as **plain text** (or create a stub first); add the `[[link]]` only once the file exists. Use shortest-path links (`[[name]]`, not `[[../name]]`). After writing, run `python3 scripts/check-wikilinks.py` and fix anything it reports.

7. **Open questions go in the register.** Don't bury open questions at the bottom of the vision — add them to the central [[open-questions]] register and leave a short inline marker `_[⚠ open — see [[open-questions]] #N]_` where relevant.

8. **Status reflects real coverage.** Surfaced-in-vision components are **Collecting** — never **Defined** without a dedicated deep-dive.

## Flow

```
User invokes /product-vision with a transcript path
    │
    ▼
Load vision-extraction.md + vision template
    │
    ▼
Check: does a project directory exist?
    │
    ├── No → Suggest invoking /product-manager first to set up the project structure
    │
    └── Yes → Read existing vision document (if any)
              Understand what's already captured
    │
    ▼
Read the full transcript before speaking
    │
    ▼
Present coverage map per section (✅ good / ⚠️ partial / ❌ none)
    │
    ▼
Work through sections conversationally:
    │
    - Present extraction with key quotes
    - Ask about ambiguities
    - Flag gaps
    - Let user confirm/correct/expand
    │
    ▼
After all sections processed:
    │
    1. Attempt component identification from the narrative
    2. Write/update vision document
    3. Backfill `index.md` and `components.md`
    4. Produce gap analysis with questions for next call
    5. Validate the graph — run `python3 scripts/check-wikilinks.py` and fix any broken links
```

## Interaction Style

**Opening:** Read the transcript fully. Then summarise: key themes, coverage level per section, proposed plan.

**During extraction:** Section by section. Show what you found (with transcript quotes). Ask clarifying questions. Flag zero-coverage sections.

**Closing:**
1. Summary of what was captured
2. All gaps grouped by section
3. Specific questions for the next call
4. Current state of the project directory

## Component Identification

If the vision narrative is detailed enough, attempt to identify high-level components:
- Read through section 1's narrative
- Ask: "In order to deliver this vision to these personas, what functional parts need to exist?"
- Propose an initial component list
- Let user confirm/modify

**Do NOT create component documents.** Just list them in the vision document's Components backfill table with one-line descriptions and "Collecting" status — as **plain text** (no wikilinks until the component docs exist).

## Related Skills

- `/product-manager` — General PM thinking partner, project setup, routing
- `/product-component` — Component-level extraction (use after vision is established)
- `/product-sub-component` — Sub-component extraction with entity journeys
