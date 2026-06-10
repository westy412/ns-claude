# Knowledge Graph — Linking, Navigation, Integrity

> **When to read:** Before writing or restructuring any project document. This defines wikilink conventions, the backfilling protocol, agent navigation rules, and the open-questions register.

---

## Wikilink Conventions

All documents link to their parent and children using Obsidian **shortest-path wikilinks**: just the filename (or filename with minimal path to disambiguate), not full relative paths.

**Convention:** Use `[[vision]]` not `[[../vision]]` or `[[../../vision]]`. Only add path segments if needed to disambiguate (e.g., two files with the same name in different directories).

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

**Rules:**
- Every document links UP to its parent
- Every document links DOWN to its children (backfilled as children are created)
- Cross-links between siblings are optional but encouraged when components have dependencies
- Wikilinks use the `[[path]]` format, not markdown `[text](url)` format
- If two files share a name across projects, add enough path to disambiguate: `[[inplay/vision]]` vs `[[txn/vision]]`

**Never write a dangling wikilink.** A routing-table or cross-link target must point to a file that already exists. If you're listing something not yet documented (a surfaced-but-undocumented sub-component, a not-yet-created component), list it as **plain text** (no `[[link]]`) or create a stub first — add the `[[link]]` only once the file exists. After any write, run `python3 scripts/check-wikilinks.py` if the project has it, and fix anything it reports.

**Status reflects real coverage.** Only mark a component or sub-component **Defined** after a dedicated deep-dive produced its scope and acceptance criteria. Content from a semi-structured or partial discussion stays **Collecting/Defining** and carries a "partially scoped — not a formal deep-dive" banner. Never present inferred acceptance criteria as decided.

---

## Backfilling Protocol

When a new document is created, the parent must be updated:

1. **New component created** → update `components/components.md` (add row to component table) AND update `vision.md` (add row to Components table)
2. **New sub-component created** → update the parent component document (add row to Sub-Components table)
3. **New sub-sub-component created** → update the parent sub-component document (add row to Sub-Sub-Components table)

**Always backfill immediately after creating a new document.** Don't batch — if you create a document and don't backfill, the knowledge graph has a broken link.

---

## Agent Navigation

Agents enter the knowledge graph at `index.md` and navigate downward by following wikilinks. They should never need to guess file paths or scan directories.

**Loading strategy (breadth-first, depth on demand):**

1. **Start at `index.md`** — read the landing page to understand the project, its status, and what exists.
2. **Load the relevant entry point** — `vision.md` for product context, `components.md` for the component map, `architecture.md` for technical decisions.
3. **Go deep only when the task requires it** — follow the chain: `components.md` → `component-name.md` → `sub-component-name.md`. Don't load all sub-components when you only need one.
4. **Cross-reference via links in the document** — if a sub-component mentions an integration, follow the link to `integrations.md`. The links are the navigation; the filesystem is the storage.

**Rule: if an agent has to use `find` or `ls` to locate a document, the knowledge graph has a broken link.** Every document must be reachable by following wikilinks from the root.

---

## Interlinking Rules

Every document in the knowledge graph must have three types of links:

**1. Vertical links (parent ↔ child)** — mandatory; they form the spine of the graph.
- Header metadata links up: `> **Component:** [[bloomberg-terminal]]`
- Routing tables link down: the Sub-Components table at the bottom of a component doc
- Both directions must exist. If a child links to its parent but the parent doesn't list the child, the graph is broken.

**2. Cross-links (sibling ↔ sibling)** — when two documents at the same level have a dependency, they link to each other inline where the dependency is mentioned. Contextual, not in a dedicated section.

**3. Cross-cutting links (architecture ↔ components)** — bidirectional:
- Architecture docs reference which components they affect: "Used by: [[bloomberg-terminal]], [[trading]]"
- Component docs link to `[[tech-stack]]` or `[[integrations]]` where a decision is made at the architecture level
- Integration docs reference which components consume them

---

## Routing Within Pages

Every document must let a reader navigate to related content without going back up the tree:

- **Entry-point files** have a routing table near the top linking to all children with one-line descriptions and status.
- **Content files** (vision, component, sub-component docs) have routing at the bottom — backfilled tables linking to their children.
- **Changelog and change documents** link back to their parent sub-component doc (`> **Sub-component:** [[name]]`) and forward to any dev-workflow artifacts (specs, PRs) they produce.

---

## Orphan Prevention

A document is orphaned if no other document links to it. Orphans are invisible to agents navigating the graph.

- Every document must be linked from at least one other document (its parent at minimum)
- The backfilling protocol prevents orphans at creation time
- Meeting transcripts are linked from the documents they sourced via the `Sources` field
- Change documents are linked from the changelog entries that spawned them
- If you create a document and aren't sure where it should be linked from, it probably doesn't belong in the knowledge graph yet — put it in `drafts/`

---

## Open Questions Register

Unresolved questions live in one central register — `open-questions.md` at the project root — not buried at the bottom of individual documents. Each row: the question, the area, where the answer belongs (a wikilink), the meeting it was raised in, and status (`Open` / `Answered` / `Parked`).

In the doc where a question is relevant, leave a short inline marker linking to the register:

```markdown
_[⚠ open — see [[open-questions]] #N]_
```

When a question is answered, set its status to `Answered` and note where the answer landed. The register is linked from `index.md` so it's reachable from the root.
