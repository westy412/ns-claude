# Meeting Template

## About This Document

This template defines the structure for a **meeting file** — a transcript with metadata and (after processing) a post-call analysis. Meeting files live in the project's `meetings/` directory and are the raw source material that feeds extraction and changelog updates.

**Naming convention:** `YYYY-MM-DD-<slug>.md` — date of the meeting + a short descriptive title.

**Workflow:**
1. User creates the file and pastes in the raw transcript
2. Agent reads the transcript, classifies it, and proposes the frontmatter in human-readable form
3. User confirms or corrects
4. Agent writes the frontmatter and routes to the appropriate next step
5. After processing, agent writes the post-call analysis at the top of the transcript section

**Meeting types and what happens next:**

| Type | What it is | Next step |
|------|-----------|-----------|
| `vision-call` | Focused vision conversation (~2 hours) | Route to `/product-vision` for extraction |
| `component-session` | Focused component deep-dive (~1 hour) | Route to `/product-component` for extraction |
| `sub-component-session` | Focused sub-component / entity journey session | Route to `/product-sub-component` for extraction |
| `general` | Review session, longer discussion (~1 hour) | Digest: load component tree, list findings, user confirms, write changelog entries |
| `standup` | Status update with discussion (~30 min) | Digest: same process as general |

**For general and standup meetings:** Before processing, the agent must load the project's component tree (`components.md` + sub-component lists from each component doc) so it can accurately map findings to known entities in the knowledge graph.

---

## Frontmatter

```yaml
---
date: YYYY-MM-DD
type: vision-call | component-session | sub-component-session | general | standup
scope:                              # What this meeting focused on (if focused)
  - "[[component-or-sub-component]]"
status: raw | extracted | partially-extracted
extracted-to:                       # Filled after processing — where the intelligence went
  - "[[destination-doc-or-changelog]]"
---
```

**Field notes:**

- **`type`** — the agent proposes this after reading the transcript. Proposed in human-readable form ("This looks like a component deep-dive on the bloomberg terminal"), not as raw YAML.
- **`scope`** — for focused meetings (vision-call, component-session, sub-component-session), this is the specific document being extracted to. For general/standup meetings, this is omitted or lists multiple items if the meeting clearly centred on certain areas.
- **`status`** — `raw` when first created, `extracted` after full processing, `partially-extracted` if some findings were processed but others deferred.
- **`extracted-to`** — the traceability link. Lists every document that was created or updated as a result of this meeting. Written by the agent after processing.

---

## Post-Call Analysis

After processing, the agent writes a post-call analysis between the frontmatter and the raw transcript. This is the traceability artifact — it shows what the meeting produced and where each finding went.

**Format:** A findings table, not prose.

```markdown
## Post-Call Analysis

| Finding | Destination | Action |
|---------|-------------|--------|
| [What was found — plain language] | [[destination]] | Entry added / Note added / Flagged / No action |
```

**For focused meetings** (vision-call, component-session, sub-component-session), the post-call analysis is lighter — just a note confirming what was extracted and linking to the output document.

**For general/standup meetings**, the post-call analysis is the main output — it maps every piece of product-relevant intelligence to its destination in the knowledge graph.

---

## Skeleton: What the Filled-In Document Looks Like

### Focused meeting (after extraction)

```markdown
---
date: 2026-05-15
type: component-session
scope:
  - "[[bloomberg-terminal]]"
status: extracted
extracted-to:
  - "[[bloomberg-terminal]]"
---

## Post-Call Analysis

| Finding | Destination | Action |
|---------|-------------|--------|
| Component extraction — bloomberg terminal | [[bloomberg-terminal]] | Document created |
| 3 sub-components identified | [[bloomberg-terminal]] | Listed in Sub-Components table |

---

## Transcript

[raw transcript content]
```

### General meeting (after digest)

```markdown
---
date: 2026-05-15
type: standup
status: extracted
extracted-to:
  - "[[match-browser/changelog]]"
  - "[[architecture]]"
---

## Post-Call Analysis

| Finding | Destination | Action |
|---------|-------------|--------|
| Filter UX confusion — users struggling with advanced panel | [[match-browser]] changelog | Entry added |
| Auth provider discussion — leaning toward Clerk | [[architecture]] | Note added to integrations |
| Watchlist feature mentioned | [[bloomberg-terminal]] | Flagged — potential new sub-component |
| Timeline discussion — shipping end of month | — | No action (status update only) |

---

## Transcript

[raw transcript content]
```
