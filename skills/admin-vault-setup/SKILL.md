---
name: admin-vault-setup
description: Scaffold a new client project vault shaped for the admin-panel template line (docs portal + Corporate Identity), then prove it panel-consumable with a local sync test. Permutation of vault-setup — use when a client is getting an admin panel/api pair via admin-panel-instantiate and needs its vault stood up first. Also use when an existing vault must be made panel-ready (brand/ folder, publishing conventions, deploy-key readiness).
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
argument-hint: "[project-name]"
---

> **Invoke with:** `/admin-vault-setup` or `/admin-vault-setup [project-name]`
> **Keywords:** admin vault, panel vault, client vault for admin panel, vault for instantiation

Scaffolds a client project vault that doubles as the **content source for the client's
admin panel**: root markdown syncs into the authenticated docs portal at build time, and a
`brand/` folder publishes publicly to the panel's `/admin/ci` Corporate Identity browser.
Ends with a **local panel-sync test** that proves the vault is consumable by the panel
template before any client instantiation happens.

**Input:** project name (plus client display name, parent directory)
**Output:** `Novosapien/<name>-vault` — private repo, full product-vault scaffold + panel
extras, panel-sync test PASS

---

## When to Use This Skill

Use this skill when:
- A new client is getting an admin panel/api pair (`admin-panel-instantiate`) and the vault
  does not exist yet — **the vault must exist BEFORE instantiation** (the instantiation
  skill adds a deploy key to it)
- An existing plain vault needs to become panel-ready (add `brand/`, verify publishing
  conventions, run the sync test)

**Skip this skill when:**
- The client has no admin panel and just needs a knowledge vault (use `vault-setup`)
- The vault exists and is already panel-ready — you only want to re-verify (run just the
  test: `references/panel-sync-test.md`)

## Relationship to Other Skills

| Skill | Relationship |
|-------|-------------|
| `vault-setup` → `product-manager/references/vault-setup.md` | The base procedure this skill permutes. Phase 1 follows it verbatim, then layers panel extras. Do NOT duplicate its steps — read and follow it. |
| `admin-panel-instantiate` | Downstream consumer. It prompts for this vault's SSH URL (`git@github.com:Novosapien/<name>-vault.git`), generates the deploy keypair, and runs `gh repo deploy-key add` against this repo (its `references/provisioning.md` §5.5). Run THIS skill first. |
| `product-manager` (+ vision/component skills) | Copied into the vault by the base scaffold; conventions for content that will appear in the docs portal. |

## Workflow

### Phase 1 — Base scaffold (follow vault-setup)

Read `~/.claude/skills/product-manager/references/vault-setup.md` and execute its steps
1–7 exactly (inputs → `gh repo create Novosapien/[name]-vault --private --clone` →
content skeleton → product skill suite copy → CLAUDE.md/AGENTS.md → commit/push → report).

One naming constraint this permutation adds at Step 1: the project name MUST equal the
client slug used by `admin-panel-instantiate` (lowercase, hyphen-separated — e.g.
`zenith-freight`), because the instantiation skill derives the vault URL from the slug.

### Phase 2 — Panel extras

Read `references/scaffold.md`. It layers, on top of the base scaffold:
1. `brand/` folder + `brand/manifest.json` example (from `templates/brand-manifest.json`)
2. Panel-publishing conventions appended to CLAUDE.md/AGENTS.md (what syncs where,
   what is public vs auth-gated, which dirs are excluded)
3. `private/` and `templates/` directories (the panel's exclude set, so operators have a
   sanctioned place for non-published content from day one)
4. Deploy-key readiness note (nothing to generate here — instantiation owns the keypair)

### Phase 3 — Panel-sync test (proof, not vibes)

Read `references/panel-sync-test.md` and run it: scratch copy of the acme panel template →
`VAULT_REPO_URL` pointed at the new vault → `npm ci` + sync-vault + sync-brand +
`npm run build` → assert docs snapshot contains the scaffold pages, `public/ci/manifest.json`
reflects `brand/` assets, build exit 0 → clean up scratch.

`scripts/panel_sync_test.sh` runs the whole test deterministically.

A vault is NOT done until this test passes. Report the result to the user either way.

## Publishing Contract (memorize — verified against the template's sync-vault.ts)

| Vault content | Where it lands in the panel | Access |
|---------------|----------------------------|--------|
| All root-level markdown (recursive) | Docs portal snapshot, served via `/api/docs-content` | Authenticated only |
| `brand/` folder (svg / image / html assets) | `public/ci/` + `/admin/ci` gallery | **PUBLIC** — no auth |
| `private/`, `templates/`, `.obsidian/`, `drafts/` | Never published (`brandConfig.vault.excludeDirs`) | — |
| `brand/manifest.json` | Optional title/category overrides, keyed by path relative to `brand/` | consumed at sync |

Because `brand/` is public: **no client-confidential material ever goes in `brand/`.**
Logos, brand guidelines, approved marketing assets only.

## References

- `references/scaffold.md` — Phase 2 panel extras on top of the base vault-setup procedure
- `references/panel-sync-test.md` — Phase 3 local test: setup, assertions, cleanup
- `templates/brand-manifest.json` — example `brand/manifest.json` override file
- `scripts/panel_sync_test.sh` — deterministic Phase 3 runner
