# Phase 3 — End-to-End Dry-Run Validation

Load only when running the dry-run. Instantiate the test client "Zenith Freight"
end-to-end with deployment stopped at `terraform plan`, and verify all Test
Sources. **This is Phase 3 and stays blocked until the team lead unblocks it.**

## Hard constraints

- **Deploy STOPS at `terraform plan`** — no `terraform apply`, no live Cloud Run
  deploy, no live GCP provisioning beyond what the plan reads.
- **DDL runs against a disposable LOCAL Postgres only** (Docker) with
  `--allow-nonshared`. NEVER touch the shared Supabase project.
- **No live secrets** — all test-run secrets are generated/dummy values.

## Test inputs (WE2)

| Field | Value |
|-------|-------|
| display | `Zenith Freight` |
| slug | `zenith-freight` |
| compact / schema | `zenithfreight` |
| org token | `ZenithFreight` |
| member role | `zenithfreight_member` |
| sa_prefix | `zf` |
| vault URL | `git@github.com:Novosapien/zenith-freight-vault.git` |

## Sequence

1. **Inputs + derivation + EC1** — `derive_identity.py --display "Zenith Freight"
   --sa-prefix zf`; confirm the table. Separately verify EC1: a too-long
   `sa_prefix` is rejected before any provisioning.
2. **Create repos** — `gh repo create` both from the live templates (private).
3. **Substitute** — `substitute.py` per template; regenerate lockfiles
   (`uv lock`, `npm install`); apply brand assets + the globals.css color map.
4. **Grep gate (WE2 / EC4)** — `grep_gate.py` over both trees with acme variants +
   both manifests' defaults → 0 hits. Also verify EC4: seed one missed
   substitution (e.g. revert `acme` in one file) and confirm the gate FAILS with
   the exact `file:line`, then fix it.
5. **Verify substituted values (WE2)** — panel `brand.config.ts` name = "Zenith
   Freight"; api `src/app/database.py` search_path = `zenithfreight`.
6. **DDL against disposable local Postgres (WE3)** — spin up Docker Postgres; set
   `DATABASE_*` / `TENANT_SCHEMA=zenithfreight` / `SHARED_DB_HOST_FRAGMENTS` to the
   local host; run `apply.py --mode all --allow-nonshared`. Confirm `01→05` apply
   in order, `07` runs, `06_verify` passes, and the schema has the 7 tables +
   `screenshots` bucket policies from `07_storage.sql`.
7. **Builds/tests (WE1 shape)** — panel `npm run build` with `VAULT_REPO_URL`
   unset (vault clone skipped by design); api `uv sync && pytest`.
8. **Idempotency re-run (WE5)** — re-run the skill/DDL: every step detects
   done-state and skips, incl. `04_realtime.sql` (publication-rows probe); exit
   reports "nothing to do".
9. **Simulated mid-run failure (EC2)** — mark a step failed via `state.py` (e.g.
   `deploy_testing`) and emit `checklist --phase failure`; confirm the remaining
   steps + manual residue render and re-run would resume at deploy.
10. **Deploy dry-run** — `cd infrastructure/` and run `terraform plan` only
    (testing then production), confirming `0 to destroy` and the `image` field not
    in the diff. STOP — no apply.

## Local disposable Postgres

```bash
docker run -d --name zf-pg -e POSTGRES_PASSWORD=devpass -p 55432:5432 postgres:16
export DATABASE_HOST=localhost DATABASE_PORT=55432 DATABASE_NAME=postgres \
       DATABASE_USERNAME=postgres DATABASE_PASSWORD=devpass \
       TENANT_SCHEMA=zenithfreight \
       SHARED_DB_HOST_FRAGMENTS='localhost'   # matches so --allow-nonshared not even needed; still pass it to be explicit
python3 supabase/zenithfreight/apply.py --mode all --allow-nonshared
```

`07_storage.sql` references Supabase `storage.buckets`/`storage.objects` — a bare
Postgres lacks the `storage` schema. Create a minimal `storage` schema with the
`buckets` + `objects` tables (or a stub) before `07`, OR assert `07`'s SQL parses
and the bucket-policy statements are present and defer live execution to the real
Supabase host. Document whichever path you take.

## WE/EC coverage table (fill during the run)

| Test | What it checks | Result |
|------|----------------|--------|
| WE1 | panel builds (vault unset), api tests pass | |
| WE2 | repos exist; gate 0 hits; brand name; search_path | |
| WE3 | DDL 01→05 + 07; 06 verify; 7 tables + bucket policies | |
| WE5 | re-run skips every step incl. 04 | |
| EC1 | SA-cap rejection before provisioning | |
| EC2 | deploy-fail checklist + resume-at-deploy | |
| EC4 | seeded missed substitution → gate fails file:line | |

(WE4 — the CI brand feature — is a panel-feature check, exercised via
`npm run sync-brand` against a vault `brand/` folder if included in scope; EC3/EC5/
EC6 are covered by the DDL founding-admin abort, the alembic guard, and the loud
vault-build behavior respectively.)

## Teardown (mandatory)

```bash
gh repo delete Novosapien/zenith-freight-admin-panel --yes
gh repo delete Novosapien/zenith-freight-admin-api   --yes
docker rm -f zf-pg
rm -rf <local scratch trees>
```

Also remove any test SAs/secrets/deploy keys created during the run. Report
teardown evidence to the team lead. Document this teardown in the skill (this
file).
