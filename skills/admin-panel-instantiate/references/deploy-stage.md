# Deploy Stage — Delegate to cloudrun-deploy

Step 7. Deployment is delegated to the `cloudrun-deploy` skill (load it). Both
templates already ship the **Option C Hybrid** pattern: the GitHub Actions
workflow owns the SHA-tagged image, Terraform owns env vars / scaling / IAM, and
the Cloud Run resource has `lifecycle { ignore_changes = [image] }`. The skill
does not re-derive the deploy — it drives the existing runbook.

## What each template already provides

- `infrastructure/` with `main.tf` (image ignored), `variables.tf`, `iam.tf`,
  `outputs.tf`, `secrets.tf` (api, docs-sync secret mount), `*.tfvars.example`.
- `.github/workflows/deploy.yml` (push to `main`) + `deploy-testing.yml` (push to
  `testing`), gated on `vars.DEPLOY_ENABLED == 'true'`.
- `CLAUDE.md` documents the Image-deployment + Updating-Environment-Variables
  runbook (both required subsections — already present in the templates).

## Order: testing first, then production (never combined)

For each of the two repos (api first so its URL exists for the panel's
`API_URL`, then panel):

1. Populate the real gitignored tfvars (checklist item; operator supplies live
   secret values).
2. `cd infrastructure/`
3. **`terraform plan` FIRST** — verify `0 to destroy` and that the `image` field
   is NOT in the diff (it must be in `ignore_changes`):
   ```bash
   terraform plan -var-file=terraform.testing.tfvars -state=terraform.testing.tfstate
   ```
   (Local backend → append `-state=...`; GCS backend → omit it. Check
   `infrastructure/backend.tf`.)
4. Apply only after a clean plan, then verify on Cloud Run.
5. Repeat for production.

State stays per-client, per-repo, LOCAL (gitignored) — no shared backend, no
central registration (matches existing clients).

**Done-probe (R7):** `gcloud run services describe <service> --region=us-east1`
returns a deployed revision → the deploy step for that env is done.

## Failure handling (EC2)

If the deploy stage fails after DDL applied, the schema + repos are left intact.
The skill emits a checklist listing the remaining deploy steps and re-runs resume
at deploy — it does not re-do DDL (its done-probe reports complete). Record the
failure via `state.py set --step deploy_testing --status failed`.

## Loud-build behaviors to surface, not silence (EC6)

- Panel build with `VAULT_REPO_URL` set but unreachable **fails loudly** by design
  (sync-vault clones the private vault). The deploy stage reports it; it does not
  silently skip. A green build needs the vault deploy key correctly wired (the
  triad).
- Panel PR/CI build leaves `VAULT_REPO_URL` unset so the vault clone is skipped —
  that is the buildable shape (WE1), not an error.

## Dry-run STOPS at `terraform plan` (Phase 3 hard constraint)

In the Phase 3 dry-run, the deploy stage runs `terraform plan` ONLY — no
`terraform apply`, no live Cloud Run deploy, no live GCP provisioning beyond what
the plan reads. See `dry-run-validation.md`.
