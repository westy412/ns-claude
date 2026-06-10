# Project Structure

> **When to read:** At the start of every product-manager session. This defines the directory layout and named entry-point pattern that all project documents must follow.
>
> **Sibling references:** [knowledge-graph.md](knowledge-graph.md) — wikilinks, backfilling, navigation, open questions. [meeting-intake.md](meeting-intake.md) — meeting files, classification, digest. [vault-setup.md](vault-setup.md) — scaffolding a brand-new vault.

---

## Directory Layout

Every project follows this structure. Create directories and files as needed — not everything exists from the start. The structure grows as documents are produced.

```
[project-name]/
├── index.md                     ← Project landing page (always exists)
├── vision.md                    ← Vision document
├── whats-new.md                 ← Rolling client-facing update log (created at first update)
├── open-questions.md            ← Central open-questions register
├── architecture/                ← Cross-cutting tech decisions (created when components are known)
│   ├── architecture.md          ← Entry point: overview, routes to sections
│   ├── tech-stack/
│   │   └── tech-stack.md        ← Frameworks, languages, databases, rationale
│   ├── infrastructure/
│   │   └── infrastructure.md    ← Hosting, deployment, CI/CD, environments
│   └── integrations/
│       └── integrations.md      ← Third-party services, APIs, data feeds
├── meetings/                    ← Raw meeting transcripts, named YYYY-MM-DD-<slug>.md
├── product/                     ← OPTIONAL: product surface layer (app products)
│   └── pages/
│       ├── PAGES.md             ← Screen inventory entry point
│       └── [area]/[screen].md   ← One doc per screen, grouped by app area
├── drafts/                      ← Work-in-progress documents
└── components/
    ├── components.md            ← Component map
    └── [component]/
        ├── [component].md       ← Component document
        └── sub-components/
            └── [sub-comp]/
                ├── [sub-comp].md      ← Sub-component document
                ├── changelog.md       ← Iteration log (append-only)
                └── changes/           ← Active change documents
```

**Legacy note:** older vaults nest content under a `vault/` or `content/` subdirectory (a leftover from the retired Quartz setup) and may contain Quartz framework files (`quartz/`, `quartz.config.ts`, `package.json`). Ignore the Quartz files — they are unused. The structure above applies relative to the content root, wherever it sits.

### Architecture grows by section

The three baseline sections are tech-stack, infrastructure, integrations. Real projects grow more — known examples from live vaults: `decisions/`, `services/`, `data-flows/`, `performance/`, `frontend/`. Create a section when there's content for it, never as an empty placeholder. Every new section gets a row in `architecture.md`'s routing table.

---

## The Directory-Brain Pattern

Every directory has a named entry-point file that serves two purposes:

1. **Router** — links to all children with one-line overviews
2. **Summary** — enough context to understand what's here without going deeper

The entry-point file is named after the thing it describes: the project root uses `index.md`, the components directory uses `components.md`, each component directory uses `component-name.md`, each sub-component directory uses `sub-component-name.md`, and the pages directory uses `PAGES.md`.

An agent or human navigates the project by entering at the top-level `index.md`, scanning the summary and links, and diving into the relevant child. At each level, the entry-point file tells you what's here and where to go next.

---

## Rolling Updates — `whats-new.md` + Recent Activity

Two mechanisms, two audiences, no duplication:

- **`index.md` → Recent Activity table** — the internal log. One line per event, newest first: date + what happened. For the team and for agents orienting on project state.
- **`whats-new.md`** — the client-facing log. Narrative digests of shipped or changed work, written for the client to read. Created when there's a first real update to report; linked from the `index.md` Documents table. Header links back to `[[index]]`.

When both exist, Recent Activity rows stay one-liners — the narrative lives in `whats-new.md` only. Never write the same update twice.

---

## The Product Surface Layer (optional — app products)

For products with a user-facing app, the knowledge graph can carry a `product/pages/` layer: one document per screen, grouped by app area, with `PAGES.md` as the entry point (total screen count, tab/navigation structure, routing table by area).

- Page docs describe **what users see and do**: content, actions, navigation in/out, states.
- Each page doc links to the component or sub-component that owns its behaviour; the sub-component doc holds the spec, the page doc holds the surface.
- Create this layer when screen-level documentation starts mattering (design reviews, build phase) — not during early discovery.

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
| [[whats-new]] | Client-facing update log | [Rolling] |
| [[open-questions]] | Open questions register | [Rolling] |

## Recent Activity

| Date | What happened |
|------|--------------|
| | |
```

(Only list `whats-new` / `open-questions` rows once the files exist — see the dangling-wikilink rule in [knowledge-graph.md](knowledge-graph.md).)

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
```

---

## Naming Conventions

**Directories:** lowercase, hyphen-separated. Match the component/sub-component name.

**Files:** lowercase, hyphen-separated. Named after the thing they describe.

**Entry-point files:** named after the thing they describe. Component directories use `component-name.md`. The project root uses `index.md`. The component map uses `components.md`. The pages inventory uses `PAGES.md`.

**Sub-components** are directories (not flat files), containing a named document, a changelog, and a changes directory:
```
sub-components/match-browser/match-browser.md
```

**Meetings:** `YYYY-MM-DD-<slug>.md`, ISO date order — see the intake checklist in [meeting-intake.md](meeting-intake.md).

---

## Creating the Initial Project Structure

When starting a new project **inside an existing vault**, create:

1. The project landing page: `index.md`
2. The vision document: `vision.md` (from vision template)
3. The components directory and map: `components/components.md`

Everything else gets created as documents are produced. Don't create empty placeholder directories — create them when there's content to put in them.

When the vault itself doesn't exist yet (no repo, empty directory), load [vault-setup.md](vault-setup.md) and scaffold it first.
