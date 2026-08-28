# Inputs, Identity Derivation, and SA-Cap Validation

The first step. Collect inputs, derive every identity value, show all for
confirm/override, and validate the GCP service-account 30-char cap BEFORE any
repo or cloud resource is created (spec R6, EC1). Nothing downstream runs until
this passes.

## Inputs to collect

| Input | Source | Notes |
|-------|--------|-------|
| `display_name` | Prompt | May contain spaces (e.g. "Zenith Freight"). Sole source of `brandConfig.name`. |
| `sa_prefix` | Prompt (ALWAYS) | No safe derivation — GCP caps SA ids at 30 chars, so long slugs need an abbreviation. |
| brand colors | Prompt / brand brief | 8 palette keys (see `substitution.md`); default to the neutral acme greys if unbranded. |
| brand logos/favicon | File paths | `logo_light`, `logo_dark`, `favicon` SVGs. Neutral placeholders ship in the template. |
| brand fonts | Prompt (optional) | Default Inter + IBM Plex Mono. |
| `vault_repo_url` | Prompt | Defaults to `git@github.com:Novosapien/<slug>-vault.git` (SSH form for CI). |
| Shared-Supabase connection creds | Prompt or env | `DATABASE_HOST/USERNAME/PASSWORD/NAME` — for the DDL stage. **Never** read from the new client's tfvars. |
| Operator-collected secret values | Prompt or env | `SUPABASE_JWT_SECRET`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `RESEND_API_KEY`. Checklist for tfvars, not committed. |

## Derivation chain (R6)

Run `scripts/derive_identity.py --display "<name>" --sa-prefix <prefix> --json`.
It computes:

| Value | Rule | "Zenith Freight" |
|-------|------|------------------|
| `display_name` | as entered | `Zenith Freight` |
| `slug` | lowercase, spaces → hyphens | `zenith-freight` |
| `compact` | slug with hyphens stripped | `zenithfreight` |
| `tenant_schema` | = compact | `zenithfreight` |
| `org_token` | display with spaces stripped | `ZenithFreight` |
| `member_role` | `<compact>_member` | `zenithfreight_member` |
| `member_role_label` | `<display> Member` | `Zenith Freight Member` |
| `sa_prefix` | **prompted** (no derivation) | `zf` |
| repos | `Novosapien/<slug>-admin-{panel,api}` | … |
| service names | `<slug>-admin-{panel,api}` | … |
| `docs_sync_secret_id` | `<slug>-docs-sync-api-key` | … |
| `vault_repo_url` | `git@github.com:Novosapien/<slug>-vault.git` | … |

**Show the full derived table to the operator and get confirm/override on each
value before proceeding.** Overrides feed straight into the `values.json` the
substitution step consumes.

## SA-cap validation (EC1) — before any provisioning

`derive_identity.py` computes the four runtime SA ids and validates them against
the GCP rule (`^[a-z][-a-z0-9]{4,28}[a-z0-9]$`, max 30 chars):

| SA | Id pattern |
|----|-----------|
| panel prod | `<sa_prefix>-panel-runtime` |
| panel testing | `<sa_prefix>-panel-testing-runtime` |
| api prod | `<sa_prefix>-api-runtime` |
| api testing | `<sa_prefix>-api-rt-testing` |

The longest (`<sa_prefix>-panel-testing-runtime`, = `sa_prefix` + 22) governs the
cap, so `sa_prefix` must be ≤ 8 chars. If any id is too long or malformed the
script exits nonzero with a message naming the cap and the offending id(s); the
skill **stops and re-prompts** for a shorter `sa_prefix`. No repos or cloud
resources are created before this check passes (EC1).

## Building `values.json`

The substitution step (`substitution.py`) consumes a `values.json` mapping each
**manifest parameter name** to its resolved value. Take `derive_identity.py
--json` output and add brand values. The panel and api manifests share most
param names but differ on `service_name` (panel `<slug>-admin-panel`, api
`<slug>-admin-api`) and brand keys — build one values file per template, or a
merged file the substitute step reads per manifest. Every manifest parameter that
has a non-empty `files[]` list MUST have a value, or `substitute.py` aborts
(a missing value would leave acme residue that fails the grep gate).
