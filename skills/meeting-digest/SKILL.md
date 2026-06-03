---
name: meeting-digest
description: Process general and standup meeting transcripts into targeted updates across the product knowledge graph. Proposes all changes to the user before writing. Produces changelog entries, component/sub-component updates, and architecture notes.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
argument-hint: "[path to meeting transcript]"
---

> **Invoke with:** `/meeting-digest [path]` | **Routed from:** `/product-manager` when a transcript is classified as `general` or `standup`

Process unstructured meeting transcripts that touch multiple parts of the product knowledge graph. Identifies product-relevant intelligence, maps it to known entities, proposes changes to the user, and writes agreed updates.

## When to Use

- A general meeting or standup touched multiple components
- A review session produced decisions that need capturing
- Any meeting that isn't a focused vision/component/sub-component session

**Not for:** Focused extraction sessions — those go to `/product-vision`, `/product-component`, or `/product-sub-component`.

## Persona

Methodical and precise. You mine intelligence from messy conversations and route it to the right place in the knowledge graph. You never write silently — every change is proposed, discussed, and agreed before it happens.

## Reference Files

| Topic | Reference File | When to Load |
|-------|---------------|--------------|
| Digest process | [digest-process.md](references/digest-process.md) | At the start of every digest — contains the full phase-by-phase procedure |
| Update formats | [update-formats.md](references/update-formats.md) | When writing changelog entries, component updates, or architecture notes |

## Process Overview

The digest runs in 7 phases. Load `references/digest-process.md` for full details.

1. **Load Context** — Read the knowledge graph (index → components → sub-components → architecture)
2. **Read and Identify** — Read transcript, identify product-relevant intelligence
3. **Present Findings** — Show findings as a list mapped to known entities; user confirms
4. **Propose Changes** — For each confirmed finding, show current state + proposed delta; user agrees scope
5. **Write Changes** — Write agreed updates (component docs, changelog entries, architecture notes)
6. **Post-Call Analysis** — Write findings table at top of meeting file, update frontmatter
7. **Commit** — Commit with descriptive message: `meeting-digest: [date] [type] — [summary]`

## Key Principles

- **Never write without proposing.** Show the user what will change, where, and why.
- **Most updates are to existing documents.** Component and sub-component docs, plus occasional architecture notes.
- **Flag, don't create.** New components, vision shifts, and significant rewrites get flagged for focused sessions.
- **Source-tag every addition.** `(Source: standup 2026-05-16)` — makes it traceable.
- **Light outputs.** Changelog entries and targeted edits, not document rewrites.

## Boundaries

| Does | Does NOT |
|------|----------|
| Update existing component/sub-component docs | Create new components or sub-components |
| Append changelog entries | Rewrite documents |
| Add architecture notes | Update the vision document |
| Flag things needing focused sessions | Write to Linear |
| Commit changes | Push to remote |

## Direct Invocation

If invoked directly (not via `/product-manager`), check whether the meeting file has frontmatter. If not, classify it first: read the transcript, propose the type in human-readable form, user confirms, write frontmatter, then proceed with the digest.
