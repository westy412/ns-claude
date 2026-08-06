# Phase 3 — Provision GCP and Deploy

> **When to read:** Third phase. Everything here is idempotent to re-run except
> secret creation (guarded below). The bootstrap ORDER is the content.

All commands target the shared operator project. Fixed facts (never re-create):
project `coral-smoke-430718-p1`, region `us-east1`, Artifact Registry
`cloud-run-services`, VPC `default`, and ONE egress firewall rule
`vault-mcp-deny-all-egress` scoped to tag `vault-mcp-noegress`. A new client
ATTACHES the tag; a second deny-all rule (or an untagged one) takes ~30
unrelated services offline.

---

## 1. Generate and store the access secret

No committed script does this — the commands are:

```bash
SECRET=$(python3 -c 'import base64,os;print(base64.urlsafe_b64encode(os.urandom(16)).decode().rstrip("="))')
echo "[\"$SECRET\"]" > /tmp/access.json     # JSON ARRAY — the server requires it

gcloud secrets describe <service_name>-access-secrets --project=coral-smoke-430718-p1 \
  || gcloud secrets create <service_name>-access-secrets --project=coral-smoke-430718-p1 \
       --replication-policy=automatic
gcloud secrets versions add <service_name>-access-secrets \
  --project=coral-smoke-430718-p1 --data-file=/tmp/access.json
rm /tmp/access.json
```

Rules the server enforces at startup (it refuses to boot otherwise): base64url,
≥22 chars, ≥128 bits decoded, no duplicates, valid JSON array. The array shape
exists so per-person secrets later are a config change, not a rebuild.

The secret must exist BEFORE the first terraform apply — terraform reads it as
a `data` source only; the value never enters state or tfvars.

## 2. WIF allowlist — before any CI deploy

Add the NEW server repo to both places (this was missed for InPlay and broke
the first CI run):

- The attribute condition on
  `github-pool/providers/github-provider` (repository allowlist).
- The `roles/iam.workloadIdentityUser` binding on
  `github-actions-deploy@coral-smoke-430718-p1.iam.gserviceaccount.com`.

Inspect current state first; mirror the existing entries' shape exactly.

## 3. Terraform — two-pass bootstrap

`allowed_hosts` needs the service's TWO Cloud Run hostnames, which do not exist
until the service does. So:

```bash
cd infrastructure
cp terraform.production.tfvars.example terraform.production.tfvars   # fill in values
terraform init
terraform apply -var-file=terraform.production.tfvars -state=terraform.production.tfstate
```

**Pass 1** creates the SA, IAM, and the service (first revision may 403 hosts —
expected). Read the two hostnames: the project-number form
(`<service>-<project_number>.<region>.run.app`) and the hashed form
(`<service>-<hash>-<region-code>.a.run.app`) — `gcloud run services describe`
shows both. Put BOTH in `allowed_hosts` in tfvars, then **pass 2**: apply again.
`mcp` 1.29 rejects any unlisted Host with a bare `Invalid Host header` at
request time — localhost does not reproduce it.

Do not remove `lifecycle.ignore_changes` on the image field — without it every
apply silently rolls the image back. tfvars and state stay gitignored.

Defaults that exist for a reason: startup probe `GET /health` with explicit
`timeout_seconds = 5` (Cloud Run's default 1s fails cold Python), public
`run.invoker` for `allUsers` (IAM auth would break the claude.ai connector),
min instances 0.

## 4. First deploy + server-repo push

Push the instantiated server repo (operator approval first). CI
(`build-deploy.yml`) checks out the vault with `VAULT_READ_TOKEN` (Phase 4 —
for the very first deploy either wire that secret first or run the payload
build locally the way the InPlay run did), builds the payload, deploys, then
polls up to 40×10s until the SERVING revision matches the pushed digest and
curls `/health`. A plain `gcloud run deploy` exiting 0 proves nothing — the
poll is the check.

`/health` is the only unauthenticated path; it must be `/health`, not
`/healthz` (Google's frontend intercepts `/healthz` with its own 404).

## 5. Verify

```bash
curl -s https://<hostname>/health
# then, with the secret:
#   https://<hostname>/v/<secret>/mcp  — attach from claude.ai and call glob
```

Every other path 404s. If claude.ai gets `Invalid Host header`, the hostname
missing from `allowed_hosts` is the cause — re-run pass 2.
