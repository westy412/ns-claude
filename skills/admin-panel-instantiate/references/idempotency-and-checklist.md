# Idempotency, Done-Probes, and Checklist Output (R7 / EC2)

Governs every step. On mid-run failure the skill keeps completed steps, emits a
remaining-steps checklist, and re-runs resume where they stopped. Each step
declares a done-probe and uses create-if-absent semantics, so partial completion
within a step is also safe to re-run.

## State tracking

`scripts/state.py` owns a per-run `.instantiate-state.json` (map of step-id →
`pending|done|failed` + detail). The 17 steps in execution order:

```
inputs, repo_panel, repo_api, substitute_panel, substitute_api, grep_gate,
wif_binding, sa_panel, sa_api, docs_sync_secret, actions_secrets,
vault_deploy_key, repo_vars, tfvars_guidance, ddl, deploy_testing, deploy_production
```

```bash
python3 scripts/state.py init --run-dir <run-dir>
python3 scripts/state.py set  --run-dir <run-dir> --step repo_panel --status done
python3 scripts/state.py get  --run-dir <run-dir>                 # print all statuses
python3 scripts/state.py checklist --run-dir <run-dir> --phase failure   # EC2
python3 scripts/state.py checklist --run-dir <run-dir> --phase success   # manual residue
```

Mark a step `done` only after its done-probe confirms the world, so a lost state
file is recoverable by re-running the probes.

## Done-probes (R7) — the required set

| Step | Done-probe (skip if it passes) |
|------|-------------------------------|
| repo_panel / repo_api | `gh repo view Novosapien/<slug>-admin-{panel,api}` exit 0 |
| substitute_* | grep gate passes for that tree (no acme/manifest-default residue) |
| grep_gate | `grep_gate.py` exits 0 across both trees |
| wif_binding | repo in provider attribute-condition AND `workloadIdentityUser` binding present |
| sa_panel / sa_api | `gcloud iam service-accounts describe <id>@...` exit 0 (each of the 4) |
| docs_sync_secret | `gcloud secrets describe <slug>-docs-sync-api-key(-testing)` exit 0 |
| actions_secrets | `gh secret list --repo <panel>` shows `DOCS_SYNC_API_KEY` + `NEXT_PUBLIC_SUPABASE_ANON_KEY` (PANEL repo only; api mounts docs-sync from Secret Manager) |
| vault_deploy_key | panel `VAULT_DEPLOY_KEY` secret present AND vault repo has the deploy key |
| repo_vars | `gh variable list` shows the vars incl. `DEPLOY_ENABLED=true` |
| ddl | schema in `pg_namespace`; 7 tables present; realtime rows present; `06` verify passes |
| deploy_testing / deploy_production | `gcloud run services describe <service>` has a deployed revision |

**Create-if-absent** everywhere: repo create tolerates existing; SA/secret create
checks `describe` first; `gh secret set` is idempotent; DDL uses
`create … if not exists` + `04` done-probe + `07` on-conflict/drop-if-exists.

## Re-run behavior (WE5)

After a complete run, re-running detects every step's done-state and skips —
including `04_realtime.sql` (its publication-rows done-probe). The DDL stage
reports "nothing to do"; the skill exits reporting the run already complete.

## Checklist output — both success and failure

**On failure (EC2):** `checklist --phase failure` lists every not-done step as a
remaining action so the operator (or the re-run) knows exactly where to resume,
followed by the manual-residue block.

**On success:** `checklist --phase success` emits the manual-residue checklist —
items no automation should attempt:

1. **Deploy-key triad (spec Notes — the fragile part):** the private half is the
   panel repo Actions secret `VAULT_DEPLOY_KEY`; the public half is a read-only
   deploy key on the vault repo; the `DOCS_SYNC_API_KEY` value is **identical**
   across the PANEL repo's Actions secret (build-time), the api's Secret Manager
   secret value (mounted into Cloud Run), and the generated key. The api has NO
   `DOCS_SYNC_API_KEY` Actions secret — it reads the Secret Manager mount.
2. Populate the gitignored real tfvars on both repos with the operator-collected
   secret VALUES (`DATABASE_PASSWORD`, `SUPABASE_JWT_SECRET`, `SUPABASE_ANON_KEY`,
   `SUPABASE_SERVICE_ROLE_KEY`, `RESEND_API_KEY`). Never commit them.
3. Confirm the founding-admin email exists in the shared Supabase `auth.users`
   before the DDL 05 step (and is set in `05_bootstrap_admin.sql`).
4. Finalize `vars.API_URL` / `vars.API_URL_TESTING` to the deployed api URLs once
   the api is live (they gate the panel build + deploy workflows).

The checklist is emitted on EVERY run outcome — a completed run still has manual
residue to verify.
