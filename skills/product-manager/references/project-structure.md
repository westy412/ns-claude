# Project Structure

> **When to read:** At the start of every `/product-manager` session. This defines the directory layout, wikilink conventions, and README routing pattern that all project documents must follow.

---

## Directory Layout

Every project follows this structure. Create directories and files as needed — not everything exists from the start. The structure grows as documents are produced.

```
[project-name]/
├── README.md                    ← Project router (always exists)
├── vision.md                    ← Vision document
├── architecture.md              ← Cross-cutting tech decisions (created when components are known)
├── transcripts/                 ← Raw meeting transcripts, named YYYY-MM-DD-<slug>.md
│   ├── 2026-05-05-initial-vision-call.md
│   └── 2026-05-08-component-deep-dive.md
└── components/
    ├── README.md                ← Component map router
    ├── [component-1]/
    │   ├── README.md            ← Component document
    │   └── sub-components/
    │       ├── [sub-comp-1].md
    │       └── [sub-comp-2].md
    ├── [component-2]/
    │   ├── README.md
    │   └── sub-components/
    │       └── ...
    └── ...
```

---

## Transcripts

Raw meeting transcripts are stored in the project's `transcripts/` directory. They are the source material that feeds extraction.

**Naming convention:** `YYYY-MM-DD-<slug>.md` — date of the meeting + a short descriptive title.

**Input modes:**
- User pastes transcript directly into the chat → offer to save it to `transcripts/` before extraction
- User provides a file path → read from that location, copy to `transcripts/` if not already there

**Source linking:** Extracted documents (vision, components, sub-components) link back to their source transcripts via a `Sources` field in the document header. This provides traceability — any content can be traced back to the specific conversation it came from.

```markdown
> **Sources:** [[transcripts/2026-05-05-initial-vision-call]], [[transcripts/2026-05-08-component-deep-dive]]
```

---

## The Directory-Brain Pattern

Every directory has a README.md that serves two purposes:

1. **Router** — links to all children with one-line overviews
2. **Summary** — enough context to understand what's here without going deeper

An agent or human navigates the project by entering at the top-level README, scanning the summary and links, and diving into the relevant child. At each level, the README tells you what's here and where to go next.



---

## README Templates

### Project README (top level)

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
| [[components/README]] | Component map — all major parts of the product | [Identifying / Defined / Building] |
```

### Components README (component map)

```markdown
# [Project Name] — Components

> **Vision:** [[../vision]]

## Overview

[1-2 sentences: how many components, current state of decomposition]

## Components

| Component | What it does | Status | Link |
|-----------|-------------|--------|------|
| [Name] | [One-line description] | [Status] | [[component-name/README]] |
| [Name] | [One-line description] | [Status] | [[component-name/README]] |
```

---

## Wikilink Conventions

All documents link to their parent and children using Obsidian **shortest-path wikilinks**. This means using just the filename (or filename with minimal path to disambiguate), not full relative paths. Obsidian resolves the link by finding the nearest match in the vault.

**Convention:** Shortest-path. Use `[[vision]]` not `[[../vision]]` or `[[../../vision]]`. Only add path segments if needed to disambiguate (e.g., two files with the same name in different directories).

**Link to parent:**
```markdown
> **Vision:** [[vision]]
> **Component:** [[component-name/README]]
```

**Link to children (in backfilled routing tables):**
```markdown
| Component | Overview | Link |
|-----------|----------|------|
| Landing Page | User acquisition and first impression | [[landing-page/README]] |
```

**Cross-links between siblings:**
```markdown
See also: [[trading/README]] for the trading component this feeds into.
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

1. **New component created** → update `components/README.md` (add row to component table) AND update `vision.md` (add row to Components table)
2. **New sub-component created** → update the parent component's `README.md` (add row to Sub-Components table)
3. **New sub-sub-component created** → update the parent sub-component document (add row to Sub-Sub-Components table)

**Always backfill immediately after creating a new document.** Don't batch — if you create a document and don't backfill, the knowledge graph has a broken link.

---

## Naming Conventions

**Directories:** lowercase, hyphen-separated. Match the component/sub-component name.
```
components/bloomberg-terminal/
components/onboarding-kyc/
components/landing-page/
```

**Files:** lowercase, hyphen-separated. Sub-components are `.md` files within a `sub-components/` directory.
```
sub-components/match-browser.md
sub-components/ai-research-partner.md
```

**README files:** always `README.md` (capitalised). This is the entry point for the directory.

---

## Creating the Initial Project Structure

When starting a new project, create:

1. The project directory: `[project-name]/`
2. The project README: `[project-name]/README.md`
3. The vision document: `[project-name]/vision.md` (from vision template)
4. The components directory: `[project-name]/components/`
5. The components README: `[project-name]/components/README.md`

Everything else gets created as documents are produced. Don't create empty placeholder directories — create them when there's content to put in them.
