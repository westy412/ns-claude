# Provisioning (GCP + GitHub + Secrets)

Step 5, after the grep gate passes. The research-verified order, each step with a
done-probe and create-if-absent semantics (R7). Shared-project prerequisites
(billing, API enablement, deployer SA, WIF pool) already exist — do NOT recreate
them. Operator-fixed refs: project `coral-smoke-430718-p1`, region `us-east1`, AR
repo `cloud-run-services`, WIF `projects/473347989513/.../github-provider`, deploy
SA `github-actions-deploy@coral-smoke-430718-p1.iam.gserviceaccount.com`.

Confirm with the operator before each step that touches live shared infra.

## 5.1 WIF repo binding (both repos)

Add each instantiated repo to the existing provider OR-condition and grant the
deploy SA `workloadIdentityUser` for it (per cloudrun-deploy "Adding a New Repo to
Existing WIF"). **Done-probe:** the repo already appears in the provider's
`attributeCondition` AND the binding already exists → skip.

```bash
PROJECT_ID=coral-smoke-430718-p1
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
for REPO in Novosapien/<slug>-admin-panel Novosapien/<slug>-admin-api; do
  gcloud iam service-accounts add-iam-policy-binding \
    github-actions-deploy@$PROJECT_ID.iam.gserviceaccount.com \
    --project=$PROJECT_ID --role=roles/iam.workloadIdentityUser \
    --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/$REPO"
done
# Update the provider attribute-condition to OR-in both new repos (read current
# condition first; append, don't overwrite existing clients).
```

## 5.2 Runtime service accounts

Create the four runtime SAs (ids validated in step 1). **Done-probe:**
`gcloud iam service-accounts describe <id>@...` returns 0 → skip.

```bash
for SA in <sa_prefix>-panel-runtime <sa_prefix>-panel-testing-runtime \
          <sa_prefix>-api-runtime  <sa_prefix>-api-rt-testing; do
  gcloud iam service-accounts create $SA --project=$PROJECT_ID \
    --display-name="$SA" || echo "exists — skip"
done
```

Terraform grants these SAs their runtime roles (the api runtime SA gets
`secretAccessor` on the docs-sync secret via `secrets.tf`). Do not hand-grant what
Terraform owns.

## 5.3 Docs-sync Secret Manager secret (generated value)

Create `<slug>-docs-sync-api-key` and `<slug>-docs-sync-api-key-testing`. The
skill GENERATES the value (e.g. `openssl rand -hex 32`). **Done-probe:**
`gcloud secrets describe <id>` returns 0 → reuse the existing value (do NOT
regenerate; the panel and api must share the identical value).

```bash
DOCS_KEY=$(openssl rand -hex 32)
for SUFFIX in "" "-testing"; do
  ID="<slug>-docs-sync-api-key$SUFFIX"
  gcloud secrets describe $ID --project=$PROJECT_ID >/dev/null 2>&1 \
    || printf '%s' "$DOCS_KEY" | gcloud secrets create $ID --data-file=- --project=$PROJECT_ID
done
```

## 5.4 GitHub Actions secrets (PANEL repo only)

`DOCS_SYNC_API_KEY` is a GitHub Actions secret on the **PANEL repo ONLY** — the
panel's build (`.github/workflows/deploy.yml`) passes it as a BuildKit secret so
`sync-vault.ts` can send `X-Sync-Key`. The **api does NOT** use an Actions secret
for it: the api's Cloud Run service mounts the same value from the Secret Manager
secret `<slug>-docs-sync-api-key` (`main.tf` `value_source → secret_key_ref →
var.docs_sync_api_key_secret_id`, provisioned in §5.3) — there is no
`secrets.DOCS_SYNC_API_KEY` in the api's workflows. **The invariant:** the panel
Actions secret value == the api's Secret Manager secret value == the generated key
(so the `X-Sync-Key` the panel sends equals the key the api validates).
**Done-probe:** `gh secret list --repo <panel>` shows `DOCS_SYNC_API_KEY` → already
set (values are write-only; re-setting is safe/idempotent).

```bash
# Panel build-time secrets (DOCS_SYNC_API_KEY + Supabase anon key):
gh secret set DOCS_SYNC_API_KEY --repo Novosapien/<slug>-admin-panel --body "$DOCS_KEY"
gh secret set NEXT_PUBLIC_SUPABASE_ANON_KEY --repo Novosapien/<slug>-admin-panel --body "<anon-key>"
# API side: NO Actions secret for DOCS_SYNC_API_KEY — it is the Secret Manager
# secret value from §5.3 (must equal $DOCS_KEY). The api's other secrets
# (DATABASE_PASSWORD, SUPABASE_*, RESEND_API_KEY) go in its gitignored tfvars (§5.7).
```

## 5.5 Vault deploy keypair (generated)

Generate an SSH keypair; private half → panel Actions secret `VAULT_DEPLOY_KEY`
(the build's BuildKit secret to clone the private vault), public half → the vault
repo as a read-only deploy key. **Done-probe:** panel secret `VAULT_DEPLOY_KEY`
exists AND the vault repo has the matching deploy key title → skip.

```bash
ssh-keygen -t ed25519 -N "" -C "<slug>-panel-vault-deploy" -f /tmp/vault_key
gh secret set VAULT_DEPLOY_KEY --repo Novosapien/<slug>-admin-panel --body "$(cat /tmp/vault_key)"
gh repo deploy-key add /tmp/vault_key.pub --repo Novosapien/<slug>-vault \
  --title "<slug>-panel-build (read-only)"   # read-only (no --allow-write)
rm -f /tmp/vault_key /tmp/vault_key.pub
```

This deploy-key pair is the most fragile part of instantiation (spec Notes) — the
success checklist verifies the triad (see `idempotency-and-checklist.md`).

## 5.6 Repo variables

Set GitHub Actions repo **variables** (not secrets) on the relevant repos.
**Done-probe:** `gh variable list` shows the name → already set.

```bash
# Panel:
gh variable set NEXT_PUBLIC_SUPABASE_URL --repo Novosapien/<slug>-admin-panel --body "https://rovnjpnozsinhpqtjweu.supabase.co"
gh variable set VAULT_REPO_URL          --repo Novosapien/<slug>-admin-panel --body "git@github.com:Novosapien/<slug>-vault.git"
gh variable set API_URL                 --repo Novosapien/<slug>-admin-panel --body "<prod api Cloud Run URL — set once api is deployed>"
gh variable set API_URL_TESTING         --repo Novosapien/<slug>-admin-panel --body "<testing api URL>"
# Enable deploys on BOTH repos (workflows no-op until this is true):
for REPO in Novosapien/<slug>-admin-panel Novosapien/<slug>-admin-api; do
  gh variable set DEPLOY_ENABLED --repo $REPO --body true
done
```

`API_URL` / `API_URL_TESTING` chicken-and-egg: they need the deployed api URLs, so
set placeholders now and finalize them after the api's first deploy (a checklist
item). The templates leave `DEPLOY_ENABLED` unset so the bare template CI stays
green; the instantiated client sets it true.

## 5.7 tfvars population guidance (manual → checklist)

The real `terraform.production.tfvars` / `terraform.testing.tfvars` are gitignored
and hold live secret VALUES. The skill does NOT write them (no live secrets in
artifacts). Emit guidance: copy each `*.tfvars.example` to the real name and
replace every `REPLACE_WITH_*` placeholder with the operator-collected value —
`DATABASE_PASSWORD`, `SUPABASE_JWT_SECRET`, `SUPABASE_ANON_KEY`,
`SUPABASE_SERVICE_ROLE_KEY`, `RESEND_API_KEY` — plus the finalized panel/api URLs.
`DOCS_SYNC_API_KEY` is mounted from Secret Manager (secrets.tf), NOT a tfvars env
var. Verify gitignore before any commit:
`git check-ignore -v infrastructure/terraform.production.tfvars`.

## Secret partition (R6) — who supplies what

| Class | Values |
|-------|--------|
| **Generated by the skill** | `DOCS_SYNC_API_KEY` value; vault deploy keypair |
| **Operator-collected (shared-project)** | `DATABASE_PASSWORD`, `SUPABASE_JWT_SECRET`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `RESEND_API_KEY` |
| **Checklist (manual)** | Real tfvars population; Supabase-dashboard founding-admin check |
