# Digest Process

> **When to read:** At the start of every `/meeting-digest` invocation. Contains the full phase-by-phase procedure.

---

## Phase 1: Load Context

Before reading the transcript, load the knowledge graph so you know what exists:

1. Read `vault/index.md` — understand the project and its current state
2. Read `vault/components/components.md` — know all components
3. For each component, read the component document to know its sub-components
4. Skim `vault/architecture/architecture.md` — know what architecture decisions exist

You need this context to accurately map findings to known entities. Without it, you're guessing.

---

## Phase 2: Read and Identify

Read the transcript in full. Identify every piece of product-relevant intelligence. For each finding, determine:

- **What** — the substance of what changed or was discussed
- **Where** — which component, sub-component, or architecture area it maps to
- **Type** — what kind of update it requires:

| Type | Description | Action |
|------|-------------|--------|
| `component-update` | Update to an existing component document | Write (after proposal) |
| `sub-component-update` | Update to an existing sub-component document | Write (after proposal) |
| `changelog` | Small change, append to sub-component changelog | Write (after proposal) |
| `architecture` | Architecture decision or integration note | Write (after proposal) |
| `flag-new` | Potential new component or sub-component | Flag only — needs focused session |
| `flag-vision` | Vision-level shift | Flag only — too significant for digest |
| `action-item` | Not product knowledge, needs doing | Note in post-call analysis |
| `no-action` | Status update, timeline chat | Note in post-call analysis |

---

## Phase 3: Present Findings

Present findings as a scannable list. Not prose, not YAML:

```
Found 5 things in this meeting:

1. Match Browser — users struggling with advanced filter panel
   → Sub-component update: simplify filter options
   
2. Onboarding — email verification requirement from client
   → Component update: add requirement to onboarding doc
   
3. Auth provider — team leaning toward Clerk
   → Architecture: update integrations
   
4. Client mentioned "watchlist" feature
   → Flag: not in current components, needs focused session
   
5. Timeline — shipping end of month
   → No action

Which of these should I update? (You can remove items or correct where they map to)
```

Wait for the user to confirm, correct, or remove items before proceeding.

---

## Phase 4: Propose Changes

For each confirmed finding, propose the specific change **before writing it**. Show:

1. **The file** being updated (full path)
2. **The current state** of the relevant section (read it and display it)
3. **The proposed change** — what will be added, modified, or appended
4. **The scope** — one-line addition? Paragraph? New section?

**Example proposal:**

```
Updating: vault/components/bloomberg-terminal/sub-components/match-browser/match-browser.md

Section: "What Needs to Happen?" → Functional requirements

Current:
> - Display all available matches with key metrics
> - Allow filtering by sport, league, and date range
> - Support sorting by multiple criteria

Adding:
> - Simplify filter UX: reduce to 3 core filters (sport, league, date),
>   move advanced filters (form, odds range, head-to-head) behind
>   an "Advanced" toggle. (Source: standup 2026-05-16)

Does this look right? Should I adjust the scope?
```

**Rules:**
- Never write without showing the user what will change
- If the change is larger than a few lines, suggest a focused session instead
- If unsure where a finding maps, ask — don't guess
- Source-tag every addition with the meeting date

---

## Phase 5: Write Changes

Once the user agrees on the scope of each change:

1. Write the updates to the relevant files
2. For changelog entries, use the format from `references/update-formats.md`
3. Source-tag inline additions: `(Source: standup 2026-05-16)`

---

## Phase 6: Post-Call Analysis

Write the post-call analysis between the frontmatter and the raw transcript in the meeting file:

```markdown
## Post-Call Analysis

| Finding | Destination | Action |
|---------|-------------|--------|
| [Finding description] | [[destination]] | [What was done] |
```

Update the meeting frontmatter:
- Set `status` to `extracted` (or `partially-extracted` if items were deferred)
- Fill in `extracted-to` with links to every file that was updated

---

## Phase 7: Commit

Stage only the files updated by this digest. Commit with:

```
meeting-digest: [meeting-date] [meeting-type] — [summary of what was updated]
```

Example: `meeting-digest: 2026-05-16 standup — match-browser filter UX, onboarding email verification, auth provider note`

Do not push — let the user decide when to push.
