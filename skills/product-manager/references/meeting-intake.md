# Meeting Intake

> **When to read:** Whenever a transcript arrives, a meeting file is created, or the meeting workflow is being explained. Defines the intake checklist, naming, frontmatter, types, post-call analysis, and the digest process.

Meeting transcripts are stored in the project's `meetings/` directory. They are the raw source material that feeds extraction and changelog updates.

---

## The Intake Checklist (blocking)

No meeting file is accepted into `meetings/` until every box is checked. Raw transcript dumps with no metadata are how knowledge graphs rot.

- [ ] **Filename is `YYYY-MM-DD-<slug>.md`** — ISO date order, so files sort chronologically.
- [ ] **Date verified against the transcript itself** — read the date stated inside the transcript (most exports print it in the header). Never trust the upload filename or "today's date"; live vaults have shipped mis-dated files this way.
- [ ] **Frontmatter written at intake** — classification proposed to the user in human-readable form, confirmed, then written. Not deferred to "later".
- [ ] **`status: raw` until extraction actually happens** — only move to `extracted` / `partially-extracted` when the work is done.
- [ ] **Post-call analysis written before status moves to `extracted`.**

**Input modes:**
- User pastes transcript directly into the chat → offer to save it to `meetings/` (through this checklist) before extraction
- User provides a file path → read from that location, copy to `meetings/` if not already there, renaming to the convention

---

## Meeting Frontmatter

```yaml
---
date: YYYY-MM-DD
type: vision-call | component-session | sub-component-session | general | standup
scope:                              # What this meeting focused on (if focused)
  - "[[component-or-sub-component]]"
status: raw | extracted | partially-extracted
extracted-to:                       # Filled after processing
  - "[[destination-doc-or-changelog]]"
---
```

**Field notes:**
- **`type`** — proposed after reading the transcript, in human-readable form ("This looks like a component deep-dive on the bloomberg terminal"), not raw YAML. User confirms or corrects before it's written.
- **`scope`** — for focused meetings, the specific document being extracted to. For general/standup, omitted or lists multiple items.
- **`status`** — `raw` when first created, `extracted` after full processing, `partially-extracted` if some findings were deferred.
- **`extracted-to`** — the traceability link: every document created or updated as a result of this meeting.

---

## Meeting Types

| Type | What it is | Duration | Next step |
|------|-----------|----------|-----------|
| `vision-call` | Focused vision conversation | ~2 hours | Route to the vision-extraction skill |
| `component-session` | Focused component deep-dive | ~1 hour | Route to the component-extraction skill |
| `sub-component-session` | Focused sub-component / entity journey session | ~1 hour | Route to the sub-component-extraction skill |
| `general` | Review session, longer discussion | ~1 hour | Digest process |
| `standup` | Status update with discussion | ~30 min | Digest process |

---

## Post-Call Analysis

After processing, the agent writes a post-call analysis between the frontmatter and the raw transcript. This is the traceability artifact — it shows what the meeting produced and where each finding went.

For **focused meetings**, the analysis is light — confirming what was extracted and linking to the output document.

For **general/standup meetings**, the analysis is the main output — mapping every piece of product-relevant intelligence to its destination in the knowledge graph. Format is a findings table, not prose:

```markdown
## Post-Call Analysis

| Finding | Destination | Action |
|---------|-------------|--------|
| Filter UX confusion | [[match-browser]] changelog | Entry added |
| Auth provider — leaning Clerk | [[architecture]] | Note added |
| Watchlist feature mentioned | [[bloomberg-terminal]] | Flagged — potential new sub-component |
| Timeline discussion | — | No action (status update only) |
```

---

## Digest Process (General and Standup Meetings)

General and standup meetings can touch any part of the knowledge graph. Before processing, load the project's component tree (`components.md` + sub-component lists from each component doc) so findings map to known entities.

1. Load the full component tree
2. Read the transcript and identify product-relevant intelligence
3. Present findings as a list — each item mapped to a known entity. Flag anything unmatched.
4. User confirms, corrects, or removes items
5. Write changelog entries, architecture notes, and flags
6. Write the post-call analysis at the top of the meeting file
7. Update meeting frontmatter (`status`, `extracted-to`)

Digest outputs are **light** — mostly changelog entries and notes. Deep extraction happens in focused sessions. New components, vision-level shifts, and significant rewrites are flagged for focused sessions, not written by the digest.

---

## Source Linking

Extracted documents (vision, components, sub-components) link back to their source transcripts via a `Sources` field in the document header:

```markdown
> **Sources:** [[meetings/2026-05-05-initial-vision-call]], [[meetings/2026-05-08-component-deep-dive]]
```
