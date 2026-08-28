---
name: admin-panel-instantiate
description: Stand up a complete new Novosapien client admin portal (panel + api repo pair) from the admin-panel-template / admin-api-template GitHub template repositories. Collects client inputs, derives identity slugs, creates both repos, substitutes every template parameter, runs a strict zero-leftover grep gate, provisions GCP/GitHub/Supabase resources with idempotent done-probes, applies the tenant-schema DDL, delegates Cloud Run deployment to the cloudrun-deploy skill, and emits a checklist of remaining manual steps. Use when onboarding a new client admin portal, creating a client repo pair, or replacing the hand-fork process. Keeps completed steps on failure and re-runs idempotently.
allowed-tools: Bash, Read, Write, Edit, Skill
---

> **Invoke with:** `/admin-panel-instantiate` | **Keywords:** new client admin panel, instantiate client portal, onboard client, admin repo pair, client provisioning

Stand up a complete client admin portal — `<slug>-admin-panel` (Next.js 16) +
`<slug>-admin-api` (FastAPI on the shared Supabase project, one Postgres schema
per client) — from the two client-neutral GitHub template repositories. Replaces
the error-prone hand-fork process, which leaks prior-client identity into every
new client.

**Input:** A client display name (e.g. "Zenith Freight"), brand assets/colors,
a vault repo URL, an always-prompted `sa_prefix`, and operator-collected
shared-project secrets.
**Output:** Two live client repos, provisioned GCP/GitHub/Supabase resources, a
deployed pair (or `terraform plan` in dry-run), and a checklist of remaining
manual steps.

## When to Use This Skill

Use this skill when:
- Onboarding a new client admin portal from the template line
- Creating a `<client>-admin-panel` + `<client>-admin-api` repo pair
- Re-running after a partial/failed instantiation (idempotent resume)

**Skip this skill when:**
- Building or changing the templates themselves (edit `admin-panel-template/` /
  `admin-api-template/` directly — those are read-only to this skill)
- Deploying an already-instantiated client (use its own CI/CD + `cloudrun-deploy`)
- Scaffolding the client vault repo (that is `admin-vault-setup`'s job — run it FIRST: this skill adds a deploy key to the vault, so `Novosapien/<slug>-vault` must already exist and should have passed admin-vault-setup's panel-sync test)

## Required Skills

Load before running:
- `cloudrun-deploy` — the deploy stage delegates to it (Option C Hybrid pattern)
- `skill-builder` — only if authoring/altering this skill

## Key Principles

1. **Buildable neutral defaults, not `{{tokens}}`** — templates ship a working
   fictional client `acme`. Substitution replaces `acme` values deterministically
   from `template.params.json`; the grep gate then treats `acme` residue exactly
   like prior-client residue.
2. **Strict gate over allowlists** — after instantiation the gate returns zero
   hits for prior-client tokens AND the per-run token set (acme variants + every
   manifest default). A miss stops the run with exact `file:line`.
3. **Operator identity stays fixed** — `Novosapien` / `novosapien_admin` and the
   shared GCP/Supabase infra refs denote the operator, not the tenant. Never
   substitute them (see `operatorFixed` in the api manifest).
4. **Validate before provisioning** — the GCP 30-char SA-id cap is checked from
   derived inputs BEFORE any repo or cloud resource is created (EC1).
5. **Credentials are skill inputs, never the new client's tfvars** — the DDL
   stage reads shared-Supabase connection creds from prompt/env, so it is not
   blocked on tfvars population.
6. **Keep progress on failure** — every step declares a done-probe and uses
   create-if-absent semantics. A failed run keeps completed steps, emits a
   remaining-steps checklist, and re-runs resume where they stopped.
7. **No live secrets in artifacts, additive DDL only, plan-before-apply** — the
   security invariants of R9 are preserved and parameterized, never weakened.

## Templates (read-only inputs to this skill)

| Template | Local path | Manifest |
|----------|-----------|----------|
| Panel | `/Users/georgewestbrook/Programming/novosapien/admin-panel-template` | `template.params.json` |
| API | `/Users/georgewestbrook/Programming/novosapien/admin-api-template` | `template.params.json` |

Both ship a `SETUP.md` documenting the manual path this skill automates; the api
DDL directory ships `apply.py` (the provisioner this skill drives). The
`gh repo create --template Novosapien/<name>-template` invocation is
parameterized — coordinate with the operator if the live template repos are not
yet published (build/test against the local trees meanwhile).

## Flow

```
inputs → derive+validate → create repos → substitute → GREP GATE
   → provision (WIF, SAs, secrets, deploy key, repo vars, tfvars guidance)
   → DDL stage (apply.py, founding-admin precheck)
   → deploy (cloudrun-deploy, testing then production)
   → checklist (emitted on success AND on any failure)
```

Each arrow is a step with a **done-probe** and **create-if-absent** semantics
(see `references/idempotency-and-checklist.md`). The grep gate is a hard gate:
failure stops the run and the run is not marked complete (EC4).

## Reference Files

Load just-in-time for the stage you are executing:

| Stage | Reference File | When to Load |
|-------|---------------|--------------|
| Inputs + identity derivation + SA-cap validation | [inputs-and-derivation.md](references/inputs-and-derivation.md) | First — before touching anything |
| Repo creation + manifest substitution + brand assets | [substitution.md](references/substitution.md) | After inputs confirmed |
| Strict grep gate (fixed regex + per-run token set) | [grep-gate.md](references/grep-gate.md) | After substitution, before provisioning |
| Provisioning (WIF, SAs, secrets, deploy key, repo vars) | [provisioning.md](references/provisioning.md) | After gate passes |
| Tenant-schema DDL via apply.py + founding-admin precheck | [ddl-stage.md](references/ddl-stage.md) | After provisioning |
| Deploy delegation to cloudrun-deploy | [deploy-stage.md](references/deploy-stage.md) | After DDL |
| Done-probes, state tracking, checklist output | [idempotency-and-checklist.md](references/idempotency-and-checklist.md) | Throughout — governs every step |
| Phase 3 end-to-end dry-run validation | [dry-run-validation.md](references/dry-run-validation.md) | Only when running the dry-run |

## Scripts

| Script | Purpose |
|--------|---------|
| [scripts/derive_identity.py](scripts/derive_identity.py) | Derive slug/compact/org/role from display name; validate SA-id 30-char cap (EC1) |
| [scripts/grep_gate.py](scripts/grep_gate.py) | Strict gate: fixed prior-client regex + per-run token set, with the verified benign exclusions; reports file:line |
| [scripts/substitute.py](scripts/substitute.py) | Manifest-driven token substitution + DDL-directory rename (api), respecting moveOnly / noSubstitution / operatorFixed |
| [scripts/state.py](scripts/state.py) | Per-run state file: mark/read step status, done-probe helpers, remaining-steps checklist rendering |

## Steps (execution order)

1. **Inputs + derivation + validation** — collect display name, brand, vault URL,
   `sa_prefix`, and operator secrets. Derive every identity value; show all for
   confirm/override. Validate the SA-id cap BEFORE provisioning (EC1). See
   `inputs-and-derivation.md`.
2. **Create repos** — `gh repo create Novosapien/<slug>-admin-{panel,api} --private
   --template Novosapien/admin-{panel,api}-template`. Done-probe: repo exists.
3. **Substitute** — run `substitute.py` per template using the manifests (colors/
   fonts key-anchored in `brand.config.ts`); regenerate lockfiles (`uv lock` /
   `npm install`); place brand logo/favicon assets; then apply the ordered
   `globals.css` ↔ `brand.config.ts` color map and swap `layout.tsx` fonts
   (manual, BRANDING.md) BEFORE the gate. `substitute.py` HARD-ABORTS on a
   same-file same-literal different-value routing collision — the manifest must be
   fixed, not guessed. See `substitution.md`.
4. **Grep gate** — run `grep_gate.py` on EACH tree against ITS OWN manifest's
   tokens (panel tree/panel manifest, api tree/api manifest — not a pooled union,
   or a panel brand hex like `#ffffff` would false-flag legitimate api email HTML).
   Zero hits required on both; a hit stops the run with `file:line` and it is NOT
   marked complete (EC4). See `grep-gate.md`.
5. **Provision** — WIF repo binding + `workloadIdentityUser` grant, runtime SAs,
   docs-sync Secret Manager secret (generated value), `gh secret set` panel/api
   Actions secrets, vault deploy keypair (generate → panel `VAULT_DEPLOY_KEY` +
   vault repo deploy key), repo variables incl. `DEPLOY_ENABLED=true`, tfvars
   population guidance. See `provisioning.md`.
6. **DDL stage** — drive `apply.py` (`--mode all`) with shared-Supabase creds
   from prompt/env; founding-admin precheck surfaces to checklist on abort (EC3).
   See `ddl-stage.md`.
7. **Deploy** — delegate to `cloudrun-deploy` (testing then production). In
   dry-run, STOP at `terraform plan`. See `deploy-stage.md`.
8. **Checklist** — emit remaining-steps checklist on success (manual residue,
   incl. the deploy-key verification triad) AND on any failure (EC2). See
   `idempotency-and-checklist.md`.

## Security (hard constraints)

- No live secrets in any generated artifact; tfvars ship only `REPLACE_WITH_*`
  placeholders and are gitignored.
- Shared-host DDL only via `apply.py`'s shared-host assertion; disposable local
  Postgres for validation uses `--allow-nonshared`.
- Deploy is plan-before-apply; dry-run never runs `terraform apply`.
- Never substitute `operatorFixed` values (`Novosapien`, `novosapien_admin`, GCP
  project/region, WIF, shared-Supabase refs).

## When to Ask for Feedback

Always confirm before:
- Proceeding past the derived-identity table (confirm/override each value)
- Any step that touches live shared infrastructure (WIF, Secret Manager, DDL
  against the shared host, live deploy)
- Marking the run complete when the grep gate has any hit (it cannot be — the
  gate is a hard stop)
