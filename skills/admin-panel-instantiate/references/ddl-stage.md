# DDL Stage — Tenant-Schema Provisioning

Step 6, after provisioning. Applies the client's Postgres schema on the shared
Supabase project via the api template's `apply.py`. Preserves every R9 safety
invariant. Credentials come from skill inputs (prompt/env), never the new client's
tfvars — so this stage is not blocked on tfvars population.

## The applier

`supabase/<tenant_schema>/apply.py` (moved+renamed with the DDL dir, NOT token-
substituted — it reads `settings.tenant_schema` at runtime). It reads connection +
schema from app config / env: `DATABASE_HOST`, `DATABASE_USERNAME`,
`DATABASE_PASSWORD`, `DATABASE_NAME`, `TENANT_SCHEMA`, `SHARED_DB_HOST_FRAGMENTS`.

### CLI

```
--mode {before|apply|after|diff|verify|isolation|all}   (required)
--allow-nonshared    bypass the shared-host assertion (disposable local/CI DB ONLY)
--dry-run            resolve config + list ordered files; NO DB connection
```

`--mode all` order:
`00(before) → 01 → 02 → 03 → 04(guarded) → 05 → 07 → 00(after) → diff → 06(verify) → isolation`.

### Safety invariants (do not weaken — R9)

- **Shared-host assertion** — refuses to connect unless `DATABASE_HOST`/username
  matches a `SHARED_DB_HOST_FRAGMENTS` entry. Exits nonzero otherwise. Bypass
  ONLY with `--allow-nonshared` on a disposable DB.
- **Session mode (5432)** — forced for DDL regardless of the app's port.
- **`04_realtime.sql` done-probe** — if this tenant's three tables
  (`feedback`, `feedback_comments`, `doc_feedback`) are already in
  `supabase_realtime`, 04 is SKIPPED (ALTER PUBLICATION ADD is not idempotent),
  so a re-run is safe (WE5).
- **before/after diff** — fails loudly (exit 2) if any non-tenant schema changed;
  only additive `<schema>.*` realtime rows may differ.
- **HARD-STOP on first error** — stops at the first failing file; no improvised
  fixes.
- **`06` verify self-rolls-back** — proves `search_path=<schema>` resolves reads +
  scoped writes to the tenant schema, never `public` or another tenant.

## Founding-admin precheck (EC3)

`05_bootstrap_admin.sql` seeds the first `novosapien_admin` from an existing
Supabase Auth identity and **hard-aborts if the email is absent** from the shared
`auth.users` (the template ships a `founding-admin@example.com` placeholder the
operator must set). Before running `--mode all`:

1. Confirm the founding-admin email is set in `05` (edit `v_admin_email` /
   `v_admin_full_name`).
2. Confirm that email exists in Dashboard → Authentication → Users (create/invite
   if absent — this is a manual, dashboard-only step).

If 05 hard-aborts, the skill surfaces the Supabase-dashboard step in the checklist
and stops the DDL stage cleanly (schema + repos left intact) — the run resumes at
the DDL step once the founding admin exists.

## Running it (live shared host)

Confirm with the operator first (this writes to the shared project). Supply the
shared-Supabase creds via env (from skill inputs, NOT tfvars):

```bash
cd <slug>-admin-api
export DATABASE_HOST=aws-1-us-east-2.pooler.supabase.com
export DATABASE_USERNAME=postgres.rovnjpnozsinhpqtjweu
export DATABASE_PASSWORD='<from operator input>'
export DATABASE_NAME=postgres
export TENANT_SCHEMA=<tenant_schema>
export SHARED_DB_HOST_FRAGMENTS='rovnjpnozsinhpqtjweu,aws-1-us-east-2.pooler.supabase.com'

python3 supabase/<tenant_schema>/apply.py --mode all --dry-run   # inspect first
python3 supabase/<tenant_schema>/apply.py --mode all             # apply + verify
```

**Done-probe for the whole stage (R7):** schema present in `pg_namespace`, the 7
tables present, realtime publication rows present for the three tables, `06`
verify passes. On re-run, `--mode apply` skips 04 via its done-probe and the other
files are create-if-absent (`create schema if not exists`, `create table if not
exists`, `07` on-conflict-do-nothing + drop-if-exists policies), so a completed
DDL stage reports "nothing to do" (WE5).

## Never run alembic against the shared host (EC5)

`src/app/alembic/env.py` hard-aborts if the host matches
`shared_db_host_fragments` unless `ALLOW_ALEMBIC_ON_SHARED=1` (disposable DB only).
The fragments are re-pinned per client via config, never removed — the guard must
still fire on the instantiated api.

## Validation (dry-run uses a disposable LOCAL Postgres)

For Phase 3 dry-run, run against a disposable local Postgres with
`--allow-nonshared` — NEVER the shared Supabase project. See
`dry-run-validation.md`.
