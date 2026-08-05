# Panel Extras — Layered on the Base Vault Scaffold

> **When to read:** Phase 2, immediately after completing steps 1–7 of
> `~/.claude/skills/product-manager/references/vault-setup.md`. Everything here is a DELTA
> on that scaffold — do not repeat base steps.

---

## 1. `brand/` folder

The panel's `sync-brand` publishes the vault's `brand/` folder to `public/ci/` as the
Corporate Identity collection — **publicly served, no auth gating** (InPlay pattern,
pinned decision 2026-07-18).

Create:

```bash
mkdir -p brand/logos
cp [skill-dir]/templates/brand-manifest.json brand/manifest.json
cat > brand/README.md <<'EOF'
# Brand assets

Everything in this folder is published PUBLICLY to the client admin panel's
Corporate Identity browser (/admin/ci). Supported types: svg, images (png/jpg/webp),
html. Subfolders become categories (e.g. logos/ -> "Logos"); loose files fall under
"General". manifest.json may override an asset's title/category, keyed by the file's
path relative to brand/.

NEVER put confidential material here. Logos, brand guidelines, and approved
marketing assets only.
EOF
```

Notes:
- `brand/README.md` is markdown but lives inside `brand/` — sync-brand skips unsupported
  types, and `walkMarkdown` roots at the repo where `brand/` is not in `excludeDirs`; the
  README will therefore also appear as a docs-portal page. That is fine (it documents the
  folder), but keep it free of anything non-public.
- `manifest.json` is optional at runtime; shipping the example teaches the pattern. Adjust
  or empty it (`{}`) if no overrides are needed yet.
- Real client logos land here later; the scaffold ships the folder + README + manifest so
  the sync test has a working target and the day-one vault teaches the convention.
  Add at least one placeholder asset for the test (see panel-sync-test.md — the test can
  inject a temporary asset instead if you want the pushed vault asset-free).

## 2. Excluded directories

The panel excludes `private`, `templates`, `.obsidian`, `drafts` from docs publishing
(`brandConfig.vault.excludeDirs` in the panel template). The base scaffold already creates
`drafts/`. Add the other two operator-facing ones so unpublished content has a sanctioned
home from day one:

```bash
mkdir -p private templates && touch private/.gitkeep templates/.gitkeep
```

## 3. CLAUDE.md / AGENTS.md — panel-publishing conventions

Append this section to BOTH `CLAUDE.md` and `AGENTS.md` (they mirror each other):

```markdown
## Admin Panel Publishing

This vault is the content source for the client's admin panel
([name]-admin-panel). At panel build time, sync-vault clones this repo and:

- Publishes ALL root-level markdown (recursive) into the authenticated docs
  portal (served only via /api/docs-content — auth required).
- Publishes brand/ PUBLICLY to /admin/ci (no auth). Never put confidential
  material in brand/.
- Excludes private/, templates/, .obsidian/, drafts/ from publishing entirely —
  put non-published working material there.

Implications for writing:
- Every root-level markdown file is client-visible in the portal. Draft in
  drafts/ or private/ until ready.
- Wikilinks resolve in the portal the same directory-brain way — no dangling
  links, or the portal shows broken navigation.
```

Also confirm the base scaffold's `## Description frontmatter` block is present in
both `CLAUDE.md` and `AGENTS.md` (it comes from the vault-setup Step 5 template).
If the vault predates it, append the canonical block from the `product-manager`
skill's `vault-setup.md` reference.

## 4. Deploy-key readiness (nothing to generate here)

`admin-panel-instantiate` owns the vault deploy keypair: it generates the key, stores the
private half as the panel repo's `VAULT_DEPLOY_KEY` Actions secret, and runs
`gh repo deploy-key add` (read-only) against THIS vault repo (its
`references/provisioning.md` §5.5, done-probe on the key title).

This skill's only obligations:
- The repo exists, is **private**, and is named `[slug]-vault` so the derived SSH URL
  `git@github.com:Novosapien/[slug]-vault.git` resolves.
- Do NOT pre-create deploy keys — the instantiation done-probe matches on its own title.

## 5. Commit the extras

```bash
git add -A && git commit -m "admin-vault-setup: panel extras (brand/, excludes, publishing conventions)" && git push
```

Then proceed to Phase 3 — the vault is not done until the panel-sync test passes
(`panel-sync-test.md`).
