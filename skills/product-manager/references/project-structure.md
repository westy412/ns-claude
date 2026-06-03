# Project Structure

> **When to read:** At the start of every `/product-manager` session. This defines the directory layout, wikilink conventions, and named entry-point pattern that all project documents must follow.

---

## Directory Layout

Every project follows this structure. Create directories and files as needed — not everything exists from the start. The structure grows as documents are produced.

```
[project-name]/
├── index.md                     ← Project landing page (always exists)
├── vision.md                    ← Vision document
├── architecture/                ← Cross-cutting tech decisions (created when components are known)
│   ├── architecture.md          ← Entry point: overview, routes to sections
│   ├── tech-stack/
│   │   └── tech-stack.md        ← Frameworks, languages, databases, rationale
│   ├── infrastructure/
│   │   └── infrastructure.md    ← Hosting, deployment, CI/CD, environments
│   └── integrations/
│       └── integrations.md      ← Third-party services, APIs, data feeds
├── meetings/                    ← Raw meeting transcripts, named YYYY-MM-DD-<slug>.md
│   ├── 2026-05-05-initial-vision-call.md
│   └── 2026-05-08-component-deep-dive.md
└── components/
    ├── components.md            ← Component map
    ├── [component-1]/
    │   ├── [component-1].md     ← Component document
    │   └── sub-components/
    │       ├── [sub-comp-1]/
    │       │   ├── [sub-comp-1].md    ← Sub-component document
    │       │   ├── changelog.md       ← Iteration log (append-only)
    │       │   └── changes/           ← Active change documents
    │       └── [sub-comp-2]/
    │           ├── [sub-comp-2].md
    │           ├── changelog.md
    │           └── changes/
    ├── [component-2]/
    │   ├── [component-2].md
    │   └── sub-components/
    │       └── ...
    └── ...
```

---

## Meetings

Meeting transcripts are stored in the project's `meetings/` directory. They are the raw source material that feeds extraction and changelog updates.

**Naming convention:** `YYYY-MM-DD-<slug>.md` — date of the meeting + a short descriptive title.

**Input modes:**
- User pastes transcript directly into the chat → offer to save it to `meetings/` before extraction
- User provides a file path → read from that location, copy to `meetings/` if not already there

### Meeting Frontmatter

Every meeting file has frontmatter written by the agent after reading the transcript. The agent proposes the classification in human-readable form ("This looks like a component deep-dive on the bloomberg terminal") — the user confirms or corrects before the agent writes it.

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

### Meeting Types

| Type | What it is | Duration | Next step |
|------|-----------|----------|-----------|
| `vision-call` | Focused vision conversation | ~2 hours | Route to `/product-vision` |
| `component-session` | Focused component deep-dive | ~1 hour | Route to `/product-component` |
| `sub-component-session` | Focused sub-component / entity journey session | ~1 hour | Route to `/product-sub-component` |
| `general` | Review session, longer discussion | ~1 hour | Digest process |
| `standup` | Status update with discussion | ~30 min | Digest process |

### Post-Call Analysis

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

### Digest Process (General and Standup Meetings)

General and standup meetings can touch any part of the knowledge graph. Before processing, the agent must load the project's component tree (`components.md` + sub-component lists from each component doc) so it can map findings to known entities.

1. Load the full component tree
2. Read the transcript and identify product-relevant intelligence
3. Present findings as a list — each item mapped to a known entity. Flag anything unmatched.
4. User confirms, corrects, or removes items
5. Write changelog entries, architecture notes, and flags
6. Write the post-call analysis at the top of the meeting file
7. Update meeting frontmatter (`status`, `extracted-to`)

Digest outputs are **light** — mostly changelog entries and notes. Deep extraction happens in focused sessions.

### Source Linking

Extracted documents (vision, components, sub-components) link back to their source transcripts via a `Sources` field in the document header:

```markdown
> **Sources:** [[meetings/2026-05-05-initial-vision-call]], [[meetings/2026-05-08-component-deep-dive]]
```

---

## The Directory-Brain Pattern

Every directory has a named entry-point file that serves two purposes:

1. **Router** — links to all children with one-line overviews
2. **Summary** — enough context to understand what's here without going deeper

The entry-point file is named after the thing it describes: the project root uses `index.md`, the components directory uses `components.md`, each component directory uses `component-name.md`, and each sub-component directory uses `sub-component-name.md`.

An agent or human navigates the project by entering at the top-level `index.md`, scanning the summary and links, and diving into the relevant child. At each level, the entry-point file tells you what's here and where to go next.



---

## Entry-Point Templates

### Project Landing Page (`index.md`)

```markdown
# [Project Name]

> **Client:** [Name]
> **Status:** [Discovery | Components | Building | Live]
> **Date started:** [Date]

## Overview

[2-3 sentences: what this project is, who it's for, current phase]

## Documents

| Document | Description | Status |
|----------|------------|--------|
| [[vision]] | Product vision — what we're building and why | [Draft / Agreed / Evolving] |
| [[architecture]] | Cross-cutting technical decisions | [Not started / In progress / Agreed] |
| [[components]] | Component map — all major parts of the product | [Identifying / Defined / Building] |
```

### Component Map (`components.md`)

```markdown
# [Project Name] — Components

> **Vision:** [[vision]]

## Overview

[1-2 sentences: how many components, current state of decomposition]

## Components

| Component | What it does | Status | Link |
|-----------|-------------|--------|------|
| [Name] | [One-line description] | [Status] | [[component-name]] |
| [Name] | [One-line description] | [Status] | [[component-name]] |
```

---

## Wikilink Conventions

All documents link to their parent and children using Obsidian **shortest-path wikilinks**. This means using just the filename (or filename with minimal path to disambiguate), not full relative paths. Obsidian resolves the link by finding the nearest match in the vault.

**Convention:** Shortest-path. Use `[[vision]]` not `[[../vision]]` or `[[../../vision]]`. Only add path segments if needed to disambiguate (e.g., two files with the same name in different directories).

**Link to parent:**
```markdown
> **Vision:** [[vision]]
> **Component:** [[component-name]]
```

**Link to children (in backfilled routing tables):**
```markdown
| Component | Overview | Link |
|-----------|----------|------|
| Landing Page | User acquisition and first impression | [[landing-page]] |
```

**Cross-links between siblings:**
```markdown
See also: [[trading]] for the trading component this feeds into.
```

**Rules:**
- Every document links UP to its parent
- Every document links DOWN to its children (backfilled as children are created)
- Cross-links between siblings are optional but encouraged when components have dependencies
- Use shortest-path — just the filename or minimal path needed for Obsidian to resolve unambiguously
- Wikilinks use the `[[path]]` format, not markdown `[text](url)` format
- If two files share a name across projects, add enough path to disambiguate: `[[inplay/vision]]` vs `[[txn/vision]]`

---

## Backfilling Protocol

When a new document is created, the parent must be updated:

1. **New component created** → update `components/components.md` (add row to component table) AND update `vision.md` (add row to Components table)
2. **New sub-component created** → update the parent component document (add row to Sub-Components table)
3. **New sub-sub-component created** → update the parent sub-component document (add row to Sub-Sub-Components table)

**Always backfill immediately after creating a new document.** Don't batch — if you create a document and don't backfill, the knowledge graph has a broken link.

---

## Agent Navigation and Interlinking

The knowledge graph is only useful if agents can efficiently navigate it and if every document is reachable. These rules govern how agents traverse the graph and how documents must be interlinked when written.

### How Agents Navigate

Agents enter the knowledge graph at `index.md` and navigate downward by following wikilinks. They should never need to guess file paths or scan directories — every document is reachable by following links from the entry point.

**Loading strategy (breadth-first, depth on demand):**

1. **Start at `index.md`** — read the landing page to understand the project, its status, and what exists.
2. **Load the relevant entry point** — `vision.md` for product context, `components.md` for the component map, `architecture.md` for technical decisions.
3. **Go deep only when the task requires it** — if working on a specific sub-component, follow the chain: `components.md` → `component-name.md` → `sub-component-name.md`. Don't load all sub-components when you only need one.
4. **Cross-reference via links in the document** — if a sub-component mentions an integration, follow the link to `integrations.md` for the detail. The links are the navigation; the filesystem is the storage.

**Rule: if an agent has to use `find` or `ls` to locate a document, the knowledge graph has a broken link.** Every document must be reachable by following wikilinks from the root.

### Interlinking Rules

Every document in the knowledge graph must have three types of links:

**1. Vertical links (parent ↔ child)**

Every document links UP to its parent and DOWN to its children. These are mandatory — they form the spine of the graph.

- Header metadata links up: `> **Component:** [[bloomberg-terminal]]`
- Routing tables link down: the Sub-Components table at the bottom of a component doc
- Both directions must exist. If a child links to its parent but the parent doesn't list the child, the graph is broken.

**2. Cross-links (sibling ↔ sibling)**

When two documents at the same level have a dependency, they link to each other inline where the dependency is mentioned.

- Component A depends on Component B for auth → Component A's Dependencies section links to `[[component-b]]`
- Sub-component mentions a related sub-component in another component → inline link where it's referenced
- Cross-links are contextual, not in a dedicated section — they appear where the relationship is discussed.

**3. Cross-cutting links (architecture ↔ components)**

Architecture decisions affect components. Components surface architecture needs. These must be linked bidirectionally:

- Architecture docs reference which components they affect: "Used by: [[bloomberg-terminal]], [[trading]]"
- Component docs reference which architecture decisions apply: in the "How Are We Going to Solve It?" section, link to `[[tech-stack]]` or `[[integrations]]` where a decision is made at the architecture level rather than locally.
- Integration docs reference which components consume them: "Consumed by: [[bloomberg-terminal]], [[trading]]"

### Routing Within Pages

Every document must have a routing mechanism that lets a reader (human or agent) navigate to related content without going back up the tree. This means:

**Entry-point files** have a routing table — a table or list near the top that links to all children with one-line descriptions and status. This is the primary navigation mechanism.

**Content files** (vision, component, sub-component docs) have routing at the bottom — backfilled tables that link to their children. The content is the body; the routing is the footer.

**Changelog and change documents** link back to their parent sub-component doc and forward to any dev workflow artifacts (specs, PRs) they produce:
- `changelog.md` header: `> **Sub-component:** [[sub-component-name]]`
- Change documents header: `> **Sub-component:** [[sub-component-name]]`
- Change document body references which changelog entries it addresses

### Orphan Prevention

A document is orphaned if no other document links to it. Orphans are invisible to agents navigating the graph.

**Rules:**
- Every document must be linked from at least one other document (its parent at minimum)
- The backfilling protocol (below) prevents orphans at creation time
- Meeting transcripts are linked from the documents they sourced via the `Sources` field
- Change documents are linked from the changelog entries that spawned them
- If you create a document and aren't sure where it should be linked from, it probably doesn't belong in the knowledge graph yet — put it in Drafts

---

## Naming Conventions

**Directories:** lowercase, hyphen-separated. Match the component/sub-component name.
```
components/bloomberg-terminal/
components/onboarding-kyc/
components/landing-page/
```

**Files:** lowercase, hyphen-separated. Named after the thing they describe.

**Entry-point files:** named after the thing they describe. Component directories use `component-name.md`. The project root uses `index.md`. The component map uses `components.md`.

**Sub-components** are directories (not flat files), containing a named document, a changelog, and a changes directory:
```
sub-components/match-browser/match-browser.md
sub-components/ai-research-partner/ai-research-partner.md
```

---

## Creating the Initial Project Structure

When starting a new project, create:

1. The project directory: `[project-name]/`
2. The project landing page: `[project-name]/index.md`
3. The vision document: `[project-name]/vision.md` (from vision template)
4. The components directory: `[project-name]/components/`
5. The component map: `[project-name]/components/components.md`

Everything else gets created as documents are produced. Don't create empty placeholder directories — create them when there's content to put in them.
