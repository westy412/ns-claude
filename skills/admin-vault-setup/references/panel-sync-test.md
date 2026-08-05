# Panel-Sync Test — Prove the Vault Is Panel-Consumable

> **When to read:** Phase 3, after the scaffold + panel extras are committed and pushed.
> The vault is NOT done until this passes. `scripts/panel_sync_test.sh` runs it
> deterministically; this file explains what it does and how to interpret failures.

The test instantiates nothing and touches no client repos: it copies the **acme panel
template** to a scratch dir, points it at the new vault, and runs the real sync + build.

---

## Preconditions

- Vault pushed to `Novosapien/[name]-vault` (private) — or, for a fully-local test, a
  local clone path (sync-vault accepts a local path clone via git).
- Panel template available: prefer the local tree
  `~/Programming/novosapien/admin-panel-template`; fall back to
  `gh repo clone Novosapien/admin-panel-template`.
- Node 20+, npm. No GCP/Supabase needed — build runs with placeholder env.
- `brand/` contains at least one supported asset (svg/png/jpg/webp/html). If the pushed
  vault is deliberately asset-free, the script injects a temporary placeholder SVG into a
  LOCAL CLONE of the vault only (never pushed) so the CI-manifest assertion is meaningful.

## What the script does

```bash
scripts/panel_sync_test.sh <vault-git-url-or-local-path> [panel-template-path]
```

1. Copies the panel template to `mktemp -d` (excludes `node_modules`, `.next`, `.git`).
2. Clones the vault into the scratch area; injects a placeholder brand asset if `brand/`
   has no supported assets (local clone only).
3. `npm ci` in the scratch panel.
4. `VAULT_REPO_URL=<local-vault-clone> npm run sync-vault` — real docs sync + syncBrand.
5. `npm run build` (VAULT_REPO_URL still set to the local clone — reachable, so the
   prebuild sync runs again; this also re-proves the EC6 loud-failure path guards you).

## Assertions (all must hold)

| # | Assertion | How |
|---|-----------|-----|
| 1 | sync-vault exit 0 | script checks |
| 2 | Docs snapshot contains the scaffold pages | `index`, `vision`, `components/components`, `architecture/architecture`, `open-questions` present in the server-only docs snapshot output |
| 3 | Excluded dirs NOT in the snapshot | nothing from `private/`, `templates/`, `drafts/` |
| 4 | `public/ci/manifest.json` exists and lists every supported `brand/` asset with correct type + category (subfolder → category, loose → General; manifest.json overrides honored) | script parses JSON |
| 5 | `npm run build` exit 0 | script checks |
| 6 | No dangling wikilinks warned by sync-vault for scaffold pages | scan sync output for link warnings |

## Cleanup

The script removes the scratch dir (panel copy + local vault clone) on exit — pass
`--keep` to retain it for debugging. Nothing is ever pushed to the vault by the test.

## Interpreting failures

| Symptom | Likely cause | Fix side |
|---------|-------------|----------|
| Clone fails in sync-vault | Wrong vault URL/name, or repo not pushed | vault (this skill) |
| Scaffold page missing from snapshot (assert 2) | Page not created, or accidentally placed in an excluded dir | vault |
| Excluded content appears (assert 3) | Content outside `private/templates/drafts`, or panel `excludeDirs` diverged | vault first; if `brand.config.ts` excludeDirs changed, that's a template question |
| Empty/missing CI manifest (assert 4) | No supported assets in `brand/`, or unsupported types only | vault |
| Wrong titles/categories (assert 4) | `brand/manifest.json` keys not relative to `brand/` | vault |
| Build fails (assert 5) | Read the error — if it's sync-vault FATAL, vault-side; anything else is template-side and should be raised against `admin-panel-template` |
| Link warnings (assert 6) | Dangling wikilinks in scaffold content | vault |

Report the assertion table with PASS/FAIL to the user. On full PASS, the vault is ready
for `admin-panel-instantiate` (give the user the SSH URL to feed it).
