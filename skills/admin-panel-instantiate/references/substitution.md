# Repo Creation, Manifest Substitution, and Brand Assets

Steps 2–3: create both repos from the templates, then substitute every parameter
deterministically from `template.params.json`. Done when the grep gate passes.

## 1. Create the repos (done-probe: repo exists)

```bash
gh repo create Novosapien/<slug>-admin-panel --private --template Novosapien/admin-panel-template
gh repo create Novosapien/<slug>-admin-api   --private --template Novosapien/admin-api-template
```

`--template` clones the tree without history (both templates have the "Template
repository" flag set). **Done-probe:** `gh repo view Novosapien/<slug>-admin-panel`
returns 0 — if the repo already exists (re-run), skip creation. Clone both
locally to substitute:

```bash
gh repo clone Novosapien/<slug>-admin-panel && gh repo clone Novosapien/<slug>-admin-api
```

If the live template repos are not yet published, build against the LOCAL
template trees instead (copy with `rsync` excluding `node_modules`/`.venv`/`.git`)
and coordinate with the operator — the invocation is parameterized either way.

## 2. Manifest-driven substitution

Run `scripts/substitute.py` once per template. It reads the manifest, and for
each parameter replaces the `default` (acme) value with the resolved client value
in exactly the files the manifest lists — longest-value-first so `acme_member` is
replaced before `acme` and `Acme Member` before `Acme`.

```bash
python3 scripts/substitute.py --root <slug>-admin-panel \
  --manifest <slug>-admin-panel/template.params.json --values values.panel.json
python3 scripts/substitute.py --root <slug>-admin-api \
  --manifest <slug>-admin-api/template.params.json   --values values.api.json
```

Use `--dry-run` first to review the planned replacements. The script:
- Substitutes only manifest-listed files; warns (does not fail) if a listed file
  is absent under a given template.
- Applies the api template's structural renames: `supabase/acme/` →
  `supabase/<tenant_schema>/` and `06_verify_acme_resolution.sql` →
  `06_verify_<tenant_schema>_resolution.sql`.
- **Does not substitute** `moveOnly` (`apply.py` — it reads
  `settings.tenant_schema` at runtime) or `noSubstitution` (`alembic/env.py` —
  consumes schema + guard purely via settings; zero literal tokens).
- Never touches `operatorFixed` values (`Novosapien`, `novosapien_admin`, GCP
  project/region, WIF, shared-Supabase host/username/URL) — they are not in any
  parameter's `files[]`.
- Resolves `aliasOf` params (e.g. api `brand_display_name` `aliasOf`
  `identity.display_name`) by inheriting the aliased param's VALUE. Current
  aliasOf params ship `files: []` (value used only via app settings), so nothing
  is substituted for them; the inheritance keeps the script correct if a future
  aliasOf param gains `files[]`.

## 3. Regenerate lockfiles (required — they pin the package name)

The lockfiles pin the OLD (`acme`) distribution name and are NOT in any
parameter's `files[]`, so substitution does not touch them. Regenerate both so
the gate passes and the build/tests resolve the new name:

```bash
# api — regenerates uv.lock with the new [project] name from pyproject.toml
cd <slug>-admin-api && uv lock

# panel — regenerates package-lock.json under the new package.json name
cd <slug>-admin-panel && npm install
```

This is the same regen the panel `SETUP.md` step 4 calls out. Skipping it leaves
`name = "acme-admin-api"` in `uv.lock` (a real grep-gate hit, verified).

## 4. Brand assets + the globals.css color map

**Assets** — replace at their fixed paths (same filenames):
- panel `public/brand-logo.svg` (light), `public/brand-logo-dark.svg` (dark),
  `public/favicon.svg`.

**Colors** — the panel brand seam is TWO files that must move together
(`brand.config.ts` + `src/app/globals.css`). `substitute.py` handles the
`colors`/`fonts` objects **key-anchored** (it rewrites `key: "<oldhex>"` →
`key: "<newhex>"` in `brand.config.ts`), so leaves that share a default hex
(`background`/`cardBackground` both `#ffffff`; `primary`/`text` both `#2b2f36`)
resolve INDEPENDENTLY instead of colliding. **`substitute.py` does NOT touch
`globals.css`** — its `--var: hex` custom properties are applied by the operator
via the **1:1 ordered map in `admin-panel-template/docs/BRANDING.md`** as a manual
step that MUST run BEFORE the grep gate (otherwise globals.css still carries acme
hexes and the gate flags them — verified). Fonts in `src/app/layout.tsx` are
`next/font/google` imports, not `key: "value"`, so they are also a manual swap,
not a string replace. Apply the color table in order:

| `brand.config.ts` key | Light (`:root`) targets | Dark (`.dark`) |
|-----------------------|--------------------------|-----------------|
| `colors.primary` | `--primary`, `--brand-orange`, `--brand-navy`, `--ring`, `--foreground`, sidebar primaries, `--chart-1` | `--secondary` family (`--chart-2`) |
| `colors.primaryDark` | `--brand-orange-dark`, `--brand-navy-2` | `--primary`, `--ring`, sidebar primaries |
| `colors.secondary` | `--secondary`, `--brand-green`, `--chart-2` | `--chart-1` accent |
| `colors.secondaryLight` | `--brand-green-light`, `--chart-3` | `--secondary`, `--chart-2` |
| `colors.background` | `--background`, `--card`, `--popover` | dark graphite surfaces |
| `colors.text` | `--card-foreground`, `--popover-foreground`, `--accent-foreground` | `--foreground` (inverted) |
| `colors.red` | `--chart-5` | `--chart-5` |

Recompute the neutral surface tokens (`--destructive`, `--muted`, `--border`,
`--input`, `--accent`) from the substituted `primary`/`text` at reduced alpha
rather than pinning a client hue. `--sidebar-gradient` is decorative — override
per client if desired. Keep the `--brand-*` names (some components reference them
directly).

**Verify the seam:** `grep -rn '\-logo\.svg' src/` returns only `brand.config.ts`;
no legacy `--inplay-*`/`.inplay-*` tokens anywhere. Then run the grep gate
(`grep-gate.md`).

## 5. API-side brand + CORS

The api manifest also carries `cors_origin_regex` (rewritten to target
`<slug>-admin-panel` Cloud Run origins) and `brand_primary_color` /
`brand_display_name` for transactional email. These are in `src/app/config.py`
and the tfvars examples — `substitute.py` handles them from `values.api.json`.
