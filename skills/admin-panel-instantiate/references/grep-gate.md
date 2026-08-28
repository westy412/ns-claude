# Strict Grep Gate (R8 / EC4)

Step 4, a hard gate. After substitution the scan over tracked files must return
**zero hits**. A hit means a substitution was missed: the run STOPS, exact
`file:line` hits are reported, and the run is NOT marked complete (EC4). There is
no allowlist for real residue.

## What the gate scans for

The gate = **fixed prior-client regex** PLUS a **per-run generated token set**:

- **Fixed prior-client regex** (never changes, from both manifests):
  ```
  totaljobs|total-jobs|Total Jobs|TotalJobs|totaljobs_member|txn|TXN|txn_member|inplay|inPlay|InPlay|inplay_member|tj-
  ```
- **Per-run token set** for instantiation verification:
  - the acme variants `acme`, `Acme`, `ACME`, `acme_member`, PLUS
  - **every `default` value declared in each `template.params.json`** — service
    names, secret ids, the acme hex colors, font families, URLs, etc. (extracted
    by `--tokens-from`).

## Running it — gate EACH tree against ITS OWN manifest

Gate the panel tree with the panel manifest's tokens, and the api tree with the
api manifest's tokens — do NOT pool both manifests' tokens across both trees. A
value default from one manifest (e.g. the panel `colors` default `#ffffff`) is a
brand token only in the panel; the api has no color param, and `#ffffff` appears
legitimately in the api's transactional-email HTML (`background:#ffffff`). Pooling
would false-flag that legitimate api content. Each repo carries its own
`template.params.json`, so each is gated against its own declared defaults (R8).

```bash
# Panel tree, panel tokens:
python3 scripts/grep_gate.py \
  --root <slug>-admin-panel \
  --tokens acme Acme ACME acme_member \
  --tokens-from <slug>-admin-panel/template.params.json

# API tree, api tokens:
python3 scripts/grep_gate.py \
  --root <slug>-admin-api \
  --tokens acme Acme ACME acme_member \
  --tokens-from <slug>-admin-api/template.params.json
```

Both must exit 0. Exit 0 = PASS (0 hits); exit 1 = FAIL (hits printed as
`repo/file:line: [match] context`). Add `--json` for machine-readable output. The
identity tokens (`acme` variants) are the same for both; only the value-token set
differs per manifest.

## Verified-benign exclusions (NOT allowlisting real residue)

Only these structural exclusions are applied (from Phase 1 verification):

1. **Gate-definition strings** in `template.params.json` and `SETUP.md` — those
   files legitimately quote the tokens they scan for. Scoped to those two
   filenames only.
2. **Base64 integrity hashes in lockfiles** — case-insensitive `txn`/`tj`
   substrings inside `sha512-`/`sha256-` integrity lines of `package-lock.json` /
   `uv.lock` are coincidental, not identity.
3. **Diagnostic/generated/secret artifacts** are excluded from the templates
   entirely (R8), so they are skipped: `before.txt`/`after.txt`, `*.tfstate`,
   real `terraform.*.tfvars`, `.env*`, `docs-data/` contents, `public/vision/`,
   plus `node_modules`, `.next`, `.git`, `.venv`, and caches.

Everything else must be zero. If a genuine hit appears (e.g. `uv.lock` still
naming `acme-admin-api` because the lock was not regenerated), fix the cause —
do not add an exclusion.

## Token classes (why the gate does not false-positive on brand values)

The gate matches two classes differently:
- **Identity tokens** (`acme`, `Acme`, `ACME`, `acme_member`, + the fixed
  prior-client regex) — SUBSTRING match, aggressive. Catches concatenated residue
  like `acmeVault`, `acme-admin-panel`, `acme_member`.
- **Manifest value defaults** (brand hex colors, font families, URLs, service
  names extracted by `--tokens-from`) — SMART-BOUNDARY match, so common values
  don't false-positive: `Inter` does NOT match inside `Internal`; `#ffffff` does
  NOT match inside `#ffffffab`. A residual acme brand value is still caught when
  it stands as its own token.

## Known template-owned residue (verified benign — surface, do not silently pass)

Two panel-template locations carry gate tokens that are NOT in any manifest
parameter's `files[]`, so substitution does not touch them and they are NOT
covered by the current exclusions. They are benign but WILL show as hits on a real
instantiation — treat them as template-owner items, not per-run substitution
misses:

1. `scripts/sync-brand.ts` — an `acme` **example inside a code comment**
   (`acme-admin-panel -> ../acme-vault`); the code derives the slug at runtime
   from the repo name. Benign, but the comment should be neutralized in the
   template (owner: panel-template) so the gate reaches zero.
2. `src/components/admin/docs/KnowledgeGraph.tsx` — hardcoded chart palette
   (`#ff9e8c` coral, `#ffffff`) that coincidentally equals the acme `red` /
   `background` defaults. These are graph colors, not brand tokens.

When the gate flags ONLY these, report them to the operator as known
template-owned items (the substitution was complete); do not add a per-run
exclusion. The placeholder brand SVGs (`public/brand-logo*.svg`, `favicon.svg`)
also carry `Acme`/acme hexes/`Inter` — those are resolved by the asset-swap step
(replace the SVGs), so any remaining hit there means the assets were not swapped.

## On failure

Report every `file:line` hit to the operator, do NOT proceed to provisioning, and
do NOT mark the run complete. The typical fixes:
- a lockfile not regenerated (`uv lock` / `npm install`),
- a color hex in `globals.css` not covered by the ordered map,
- a manifest file that was edited by hand and reverted.

Re-run the gate after each fix until it passes.
