# Vault Setup — Scaffolding a New Client Project Vault

> **When to read:** When the vault itself doesn't exist yet — no repo, or an empty directory — or the user explicitly asks to set up a new project vault. For structure inside an existing vault, [project-structure.md](project-structure.md) is enough.

A client project vault is a **plain markdown Obsidian vault in a private git repo**, with the product skill suite copied in so any agent working in the repo has the conventions. No site generator, no build step.

> **History:** vaults used to be scaffolded with Quartz (static docs site + GitHub Pages). That's retired. Older vaults still contain Quartz files (`quartz/`, `quartz.config.ts`, `package.json`, a `vault/` or `content/` nesting) — leave them alone, don't replicate them.

---

## Step 1 — Gather inputs

- **Project name** — lowercase, hyphen-separated (e.g., "inplay", "txn", "meridian"). Used for the repo name (`[name]-vault`).
- **Client name** — display name for the landing page.
- **Parent directory** — where to create the vault locally. Default `~/Programming/[client]/`, confirm with the user.
- **Google Drive link** — optional; added to the landing page if provided.

## Step 2 — Create the repo

```bash
gh repo create Novosapien/[name]-vault --private --clone
```

## Step 3 — Content skeleton

Content lives at the **repo root** (no `vault/` nesting — that was a Quartz requirement). Scaffold the full working skeleton — every entry-point file `index.md` links to must exist on day one (no dangling links):

1. `index.md` — from the project-readme template, filled in with project name, client name, status "Discovery"
2. `vision.md` — stub from the vision template (status "Not started", pointer to run the vision-extraction skill)
3. `components/components.md` — empty component map
4. `architecture/architecture.md` — entry-point stub (overview + empty routing table; sections like tech-stack/ grow later)
5. `open-questions.md` — empty register with the standard table header
6. `meetings/` — empty directory with `.gitkeep`
7. `drafts/` — empty directory with `.gitkeep`
8. `.gitignore` — at minimum `.DS_Store` and `.obsidian/workspace.json`

`whats-new.md` is the only deferred file — created at the first real client-facing update. Beyond this scaffold set, the don't-create-empty-placeholders rule applies: everything else (components, sub-components, architecture sections, `product/pages/`) is created when there's content for it (see [project-structure.md](project-structure.md)).

## Step 4 — Copy the product skill suite

Copy the four product skills into the project so they're available to agents working in the repo — both agent trees:

```bash
for s in product-manager product-vision product-component product-sub-component; do
  cp -r ~/.claude/skills/$s [project-dir]/.claude/skills/
  cp -r ~/.codex/skills/$s  [project-dir]/.agents/skills/
done
```

**Staleness warning:** these are snapshots. When the global skills improve, project copies do NOT update automatically. Re-run this copy whenever the global product skills change, or when starting a significant new phase of work in an old vault — check first with:

```bash
diff -rq ~/.claude/skills/product-manager [project-dir]/.claude/skills/product-manager
```

## Step 5 — Project memory files

Write `CLAUDE.md` at the repo root, and mirror it to `AGENTS.md` (same content — the two agent platforms read different filenames):

```markdown
# [Project Name] Vault

This is the product knowledge vault for **[Client Name]**. It is an Obsidian
vault that doubles as an agent knowledge base.

## Git Workflow

- Never commit directly to main. Create a feature branch and open a PR.
- All merges to main happen through pull requests only.

## Content Structure

Content lives at the repo root and follows the directory-brain pattern —
every directory has a named entry-point file that is both router and summary.
Agents enter at `index.md` and follow wikilinks. If an agent needs `find` or
`ls` to locate a document, the knowledge graph has a broken link.

## Available Skills

| Skill | Purpose |
|-------|---------|
| product-manager | Thinking partner, meeting classification, routing |
| product-vision | Extract vision from transcript |
| product-component | Extract components from transcript |
| product-sub-component | Extract sub-components and entity journeys |

## Key Conventions

- Wikilinks: shortest-path (`[[vision]]`, never `[[../vision]]`); no dangling links
- Backfilling: creating a child document immediately updates the parent's routing table
- Meetings: `YYYY-MM-DD-<slug>.md`, date verified against the transcript, frontmatter at intake
- Naming: lowercase, hyphen-separated, files named after the thing they describe
```

## Step 6 — Commit and push

```bash
git add -A && git commit -m "vault-setup: scaffold [project-name] vault" && git push -u origin main
```

## Step 7 — Report

Tell the user: repo URL, what skills are available, and the usual next step — drop the vision call transcript in and run the vision-extraction skill.
