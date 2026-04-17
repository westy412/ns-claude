---
name: cloudrun-deploy
description: Automate deployments to Google Cloud Run using Terraform or gcloud CLI. Handles discovery, configuration, Dockerfile generation, infrastructure setup, and deployment execution. Supports both Secret Manager and plain env vars.
allowed-tools: Read, Glob, Grep, Task, Write, Edit, Bash, AskUserQuestion
---

# Cloud Run Deployment Skill

## Purpose

Automate the deployment of arbitrary services to Google Cloud Run. Supports both **Terraform** (full IaC) and **gcloud CLI** (simpler) deployment methods. Handles the complete workflow from discovery through verification.

**Goal:** Flexible, automated deployments that match user preferences for complexity and security.

---

## When to Use This Skill

Use this skill when:
- Deploying a new service to Google Cloud Run
- Setting up Terraform infrastructure for an existing service
- Migrating a service to Cloud Run
- Creating deployment automation for a project

**Skip this skill when:**
- Deploying to non-GCP platforms (AWS, Azure, etc.)
- Using serverless functions (Cloud Functions) instead of containers
- Service is already deployed and you only need to update code (use existing CI/CD)

---

## Key Principles

1. **Discovery-first** — Gather ALL required information before generating files
2. **Infrastructure as code** — All configuration in Terraform or gcloud CLI
3. **Flexible secrets handling** — User chooses Secret Manager (secure) or plain env vars (simple)
4. **Minimal permissions** — Only grant IAM roles that are needed
5. **Verification required** — Always test deployment before considering complete
6. **Rollback ready** — Every deployment can be reverted

---

## Prerequisites Check (Phase 0)

Before starting any deployment, verify these prerequisites exist:

### GCP Infrastructure

| Requirement | How to Verify | How to Create |
|-------------|---------------|---------------|
| GCP Project | `gcloud projects list` | GCP Console or `gcloud projects create` |
| Billing enabled | GCP Console → Billing | Link billing account to project |
| Terraform service account | `gcloud iam service-accounts list` | See Service Account Setup below |
| Service account key file | File exists locally | `gcloud iam service-accounts keys create` |
| Artifact Registry enabled | `gcloud services list --enabled` | `gcloud services enable artifactregistry.googleapis.com` |
| Cloud Run API enabled | `gcloud services list --enabled` | `gcloud services enable run.googleapis.com` |

### Local Tools

| Tool | Verify | Install |
|------|--------|---------|
| Terraform | `terraform --version` | `brew install terraform` |
| Docker | `docker --version` | `brew install --cask docker` |
| gcloud CLI | `gcloud --version` | `brew install --cask google-cloud-sdk` |

### Service Account IAM Roles

The Terraform service account requires these roles at minimum:

| Role | Purpose |
|------|---------|
| `roles/run.admin` | Create, update, delete Cloud Run services |
| `roles/iam.serviceAccountUser` | Deploy as the runtime service account |
| `roles/artifactregistry.writer` | Push images to Artifact Registry |
| `roles/secretmanager.admin` | Create and manage secrets (if service uses secrets) |

**Commands to grant roles:**
```bash
PROJECT_ID="your-project-id"
SA_EMAIL="terraform-deployer@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/secretmanager.admin"
```

### Docker Authentication

```bash
gcloud auth configure-docker ${REGION}-docker.pkg.dev
```

---

## Phase 1: Information Discovery

**CRITICAL:** Gather ALL information before generating any files.

### 1.1 Service Identity

| Field | Description | Constraints | Required |
|-------|-------------|-------------|----------|
| `service_name` | Unique identifier | Lowercase, hyphens only, max 63 chars, starts with letter | Yes |
| `description` | Human-readable purpose | Free text | No |
| `labels` | Key-value metadata | Lowercase, hyphens, underscores, max 63 chars | No |

### 1.2 GCP Target

| Field | Description | Default |
|-------|-------------|---------|
| `project_id` | GCP project to deploy into | — |
| `region` | Cloud Run region | `europe-west1` |

**Supported Regions:**
```
europe-west1 (Belgium), europe-west2 (London), us-central1 (Iowa),
us-east1 (South Carolina), asia-east1 (Taiwan), australia-southeast1 (Sydney)
```

### 1.3 Source Code Analysis

Analyze the codebase to determine:

| Field | Description | How to Determine |
|-------|-------------|------------------|
| `has_dockerfile` | Dockerfile exists? | Check repo root and common locations |
| `language` | Primary language | File extensions, package files |
| `framework` | Web framework | Import statements, dependencies |
| `package_file` | Dependency manifest | requirements.txt, package.json, go.mod |
| `entry_point` | Start command | Framework conventions |
| `port` | Application port | Check code for app.run(), uvicorn config |
| `build_command` | Build steps | npm run build, go build, etc. |

**Common Entry Points:**

| Framework | Entry Point |
|-----------|-------------|
| FastAPI | `uvicorn main:app --host 0.0.0.0 --port 8080` |
| Flask | `gunicorn --bind :8080 main:app` |
| Express | `node index.js` |
| Go | `./main` |
| Spring Boot | `java -jar app.jar` |

### 1.4 Resource Allocation

| Field | Options | Default | Considerations |
|-------|---------|---------|----------------|
| `memory` | 128Mi–32Gi | 512Mi | LLM calls may need 1Gi+ |
| `cpu` | 1, 2, 4, 6, 8 | 1 | Must increase with memory above 4Gi |
| `timeout_seconds` | 1–3600 | 300 | Long-running tasks need higher values |
| `min_instances` | 0–1000 | 0 | 0 = scale to zero; 1+ = no cold starts |
| `max_instances` | 1–1000 | 10 | Limits cost and downstream pressure |
| `concurrency` | 1–1000 | 80 | Lower for CPU-heavy tasks |

**Memory/CPU Constraints:**

| Memory | Valid CPU |
|--------|-----------|
| 128Mi–512Mi | 1 |
| 512Mi–1Gi | 1 |
| 1Gi–2Gi | 1, 2 |
| 2Gi–4Gi | 1, 2, 4 |
| 4Gi–8Gi | 2, 4, 6, 8 |
| 8Gi–16Gi | 4, 6, 8 |
| 16Gi–32Gi | 4, 6, 8 |

### 1.5 Environment Variables

For each environment variable, capture:

| Field | Description |
|-------|-------------|
| `key` | Variable name |
| `value` | Variable value (or reference to secret) |
| `is_secret` | Should this be stored in Secret Manager? |
| `secret_version` | `latest` or specific version number |

**Classification:**

| Type | Storage Method | Example |
|------|----------------|---------|
| Non-sensitive config | Plain text in Terraform | `LOG_LEVEL=INFO`, `ENV=production` |
| Sensitive credentials | GCP Secret Manager OR plain env vars | API keys, database passwords, tokens |

### 1.5.1 Secrets Management Method

**ASK THE USER:** How should secrets be stored?

| Option | Pros | Cons |
|--------|------|------|
| **Plain Environment Variables** | Simple setup, no extra GCP auth needed, works with gcloud CLI | Secrets visible in Cloud Run console, in terraform state |
| **GCP Secret Manager** | More secure, audit logging, can update without redeploying | Requires additional GCP auth, more complex setup |

**Recommendation:**
- For quick deployments or development: **Plain env vars**
- For production with sensitive data: **Secret Manager**

If user chooses plain env vars:
- Skip `secrets.tf` generation
- Use direct `env { name = "KEY", value = var.value }` in main.tf
- Offer gcloud CLI deploy as simpler alternative to Terraform

### 1.6 Networking & Access Control

| Field | Options | Default |
|-------|---------|---------|
| `ingress` | `all`, `internal`, `internal-and-cloud-load-balancing` | `all` |
| `allow_unauthenticated` | `true`, `false` | `false` |
| `custom_domain` | Domain string or `null` | `null` |
| `vpc_connector` | Connector name or `null` | `null` |
| `vpc_egress` | `all-traffic`, `private-ranges-only` | `private-ranges-only` |

**Access Control Matrix:**

| Scenario | ingress | allow_unauthenticated |
|----------|---------|----------------------|
| Public API (anyone can call) | `all` | `true` |
| Public but authenticated (API key/JWT) | `all` | `true` + app-level auth |
| Internal microservice | `internal` | `false` |
| Behind load balancer | `internal-and-cloud-load-balancing` | `false` |
| Webhook receiver | `all` | `true` |

### 1.7 GCP Service Dependencies

For each GCP service the application needs:

| Service | Required IAM Role(s) | Configuration |
|---------|---------------------|---------------|
| Cloud Firestore | `roles/datastore.user` | Project ID |
| Cloud SQL | `roles/cloudsql.client` | Connection name, VPC connector |
| Cloud Storage | `roles/storage.objectViewer` or `objectAdmin` | Bucket name(s) |
| Cloud Tasks | `roles/cloudtasks.enqueuer` | Queue name, location |
| Pub/Sub | `roles/pubsub.publisher` or `subscriber` | Topic/subscription names |
| Secret Manager | `roles/secretmanager.secretAccessor` | Secret names |
| BigQuery | `roles/bigquery.dataViewer` or `dataEditor` | Dataset(s) |

### 1.8 Health Checks

| Field | Description | Default |
|-------|-------------|---------|
| `startup_probe_path` | HTTP path to check during startup | `/` |
| `startup_probe_initial_delay` | Seconds before first probe | `0` |
| `startup_probe_timeout` | Seconds to wait for response | `1` |
| `startup_probe_period` | Seconds between probes | `3` |
| `startup_probe_failure_threshold` | Failures before marking unhealthy | `1` |
| `liveness_probe_path` | HTTP path for ongoing health checks | None (disabled) |

---

## Phase 2: Generate Artifacts

### Step 1: Create Infrastructure Directory

```bash
mkdir -p infrastructure/
```

### Step 2: Generate Dockerfile (if not present)

If the project doesn't have a Dockerfile, generate one based on the language/framework.

**Templates available in:** `templates/dockerfiles/`

### Step 3: Generate Terraform Files

Generate these files in `infrastructure/`:

| File | Purpose |
|------|---------|
| `main.tf` | Core service definition |
| `variables.tf` | Input variable declarations |
| `terraform.tfvars` | Actual values (gitignored if contains secrets) |
| `secrets.tf` | Secret Manager resources |
| `iam.tf` | Runtime service account and bindings |
| `outputs.tf` | Service URL and other outputs |

**Templates available in:** `templates/terraform/`

### Step 4: Generate Supporting Files

| File | Purpose |
|------|---------|
| `.dockerignore` | Exclude unnecessary files from image |

---

## Phase 3: Deployment Execution

### Deployment Method Choice

**ASK THE USER:** Which deployment method do you prefer?

| Method | When to Use | Pros | Cons |
|--------|-------------|------|------|
| **gcloud CLI** | Quick deploys, simple services | No Terraform auth issues, single command | Less reproducible, no state management |
| **Terraform** | Production, IaC requirements | Version controlled, full state management | Requires `gcloud auth application-default login` |

### Step 1: Build Phase

```bash
# Set variables
PROJECT_ID="your-project-id"
SERVICE_NAME="your-service"
AR_REPO="cloud-run-services"  # Artifact Registry repository name

# Use the git commit SHA as the image tag (immutable per commit).
# DO NOT use :latest — see "Image Tagging Strategy" section for why.
IMAGE_TAG=$(git rev-parse HEAD)
IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/${SERVICE_NAME}:${IMAGE_TAG}"

# IMPORTANT: Always use --platform for Apple Silicon compatibility
docker build --platform linux/amd64 -t ${IMAGE_URL} .

# Push to registry
docker push ${IMAGE_URL}
```

### Step 2a: Deploy with gcloud CLI (Simpler)

```bash
# Read env vars from .env file if available
source .env 2>/dev/null || true

# Deploy with all env vars
gcloud run deploy ${SERVICE_NAME} \
  --image=${IMAGE_URL} \
  --region=${REGION} \
  --platform=managed \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --timeout=300 \
  --concurrency=40 \
  --set-env-vars="KEY1=${VALUE1}" \
  --set-env-vars="KEY2=${VALUE2}" \
  --project=${PROJECT_ID}
```

### Step 2b: Deploy with Terraform (Full IaC)

```bash
cd infrastructure/

# Initialize Terraform (first time or after provider changes)
terraform init

# Preview changes — ALWAYS review this before applying
terraform plan -var-file=terraform.<env>.tfvars -state=terraform.<env>.tfstate
```

**Review the plan output before applying. Verify `0 to destroy`.** Never run `terraform apply -auto-approve` on a service that's already in production — blindly auto-approving a plan that wants to destroy or recreate the service is how outages happen.

```bash
# Only after reviewing the plan:
terraform apply -var-file=terraform.<env>.tfvars -state=terraform.<env>.tfstate
```

**For adding/changing env vars on an existing Cloud Run service** (Option C Hybrid), see the dedicated workflow in ["Operational discipline when modifying env vars on an existing Hybrid-managed service"](#operational-discipline-when-modifying-env-vars-on-an-existing-hybrid-managed-service) below. It covers the plan-review-apply discipline, gitignore requirements, and the image-field comment convention — all critical for avoiding silent rollbacks and security incidents.

### Step 3: Create Secrets (if using Secret Manager)

For each secret identified in discovery:

```bash
echo -n "secret-value" | gcloud secrets create SECRET_NAME --data-file=-
```

---

## Phase 4: Verification

### Step 1: Get Service URL

```bash
SERVICE_URL=$(terraform output -raw service_url)
```

### Step 2: Test Endpoint

```bash
curl ${SERVICE_URL}/health
```

### Step 3: Check Logs

```bash
gcloud run services logs read ${SERVICE_NAME} --region=${REGION} --limit=50
```

### Step 4: Verify CLAUDE.md Documents the Deployment

Once the service is live, the repo's `CLAUDE.md` (at repo root) MUST document the deployment convention so future sessions — human or agent — don't silently revert it. This is the step that prevents `:latest` rot, missing `lifecycle.ignore_changes` blocks, and accidental env var edits via the Cloud Run console.

**Required content in `CLAUDE.md`** (under a "Deployment" heading or equivalent — two subsections):

1. **"Image deployment"** subsection covering:
   - Workflow owns the image (`gcloud run deploy --image=...:<sha>` on push, tagged with `${{ github.sha }}`)
   - Terraform owns env vars and everything else
   - `lifecycle.ignore_changes` on `template[0].containers[0].image` is required — removing it reintroduces the silent rollback bug
   - tfvars pin a SHA, never `:latest`, and why
   - How to force-deploy a specific commit (workflow re-run or `gcloud run services update --image=...:<sha>`)
   - How to roll back (`gcloud run services update-traffic --to-revisions=<prev>=100`)
   - How to check what's actually running (`gcloud run services describe`)

2. **"Updating Environment Variables"** subsection covering:
   - Env vars are managed via Terraform tfvars files — Terraform is the **single source of truth**
   - Do NOT update via Cloud Run console or `gcloud --set-env-vars` (will be reverted on next `terraform apply`)
   - Workflow on push does NOT update env vars — only the image
   - Procedure: edit `terraform.{testing,production}.tfvars` → `cd infrastructure/` → `terraform plan -var-file=...` → `terraform apply -var-file=...`
   - Backend detection note: for local backend, append `-state=terraform.{env}.tfstate`; for GCS backend, omit the `-state=` flag — check `infrastructure/backend.tf` to determine which
   - **Always run `terraform plan` before `apply`** and verify `0 to destroy`

**How to verify:**

```bash
# From repo root — both should return matches
grep -E "^#+.*Image deployment" CLAUDE.md
grep -E "^#+.*Updating Environment Variables" CLAUDE.md
```

**If missing:** Use the template at "Environment Variables Strategy → Option C (Hybrid) → CLAUDE.md deployment section (template)" below. Copy it into the repo's CLAUDE.md with the service name substituted. Commit the CLAUDE.md change in the same PR as the infrastructure work.

### Step 5: Verification Checklist

- [ ] Service URL accessible
- [ ] Health check passing
- [ ] Logs showing expected behavior
- [ ] Environment variables loaded correctly
- [ ] Secrets accessible (if applicable)
- [ ] GCP service dependencies working
- [ ] `CLAUDE.md` contains "Image deployment" and "Updating Environment Variables" subsections (see Step 4 above)

---

## Phase 5: Rollback (if needed)

### Option A: Traffic Shifting (Immediate)

```bash
# List revisions
gcloud run revisions list --service=${SERVICE_NAME} --region=${REGION}

# Shift traffic to previous revision
gcloud run services update-traffic ${SERVICE_NAME} \
    --region=${REGION} \
    --to-revisions=PREVIOUS_REVISION=100
```

### Option B: Terraform Rollback

```bash
# Revert terraform.tfvars to previous image tag
# Then apply
terraform apply -auto-approve
```

### Option C: Emergency Console Override

If automation is broken, Cloud Run services can be updated directly via GCP Console.

---

## Common Patterns & Edge Cases

### Services That Call LLMs

- Higher memory allocation (1Gi+)
- Longer timeout (300s+)
- Concurrency depends on use case:
  - Streaming responses: 40-80 (connections held longer but low CPU)
  - Batch/sync responses: 20-40 (higher CPU per request)
  - With rate-limited APIs: Match to your API tier limits
- Store API keys in Secret Manager
- **Ask user about cold starts** - default is `min_instances = 0` (scale to zero for cost savings), but if cold starts affect UX, user may want `min_instances = 1`

### Services That Process Webhooks

- Must be publicly accessible (`allow_unauthenticated = true`)
- Should verify webhook signatures in application code
- Consider idempotency (same webhook may be delivered multiple times)
- Set appropriate timeout for processing time

### Services That Access Cloud SQL

- Requires VPC connector
- Use Cloud SQL Auth Proxy connection string
- Runtime service account needs `roles/cloudsql.client`

### Services That Need Persistent Connections

- `min_instances >= 1` to prevent complete scale-down
- Connection retry logic in application code
- Consider Cloud Run "always on CPU" allocation

### Multi-Region Deployment

For each additional region:
- Separate Terraform workspace or state file
- Global load balancer to distribute traffic
- Consider data replication for stateful services

---

## Common Issues & Troubleshooting

### Apple Silicon (M1/M2/M3) - Architecture Mismatch

**Error:** `Container manifest type must support amd64/linux`

**Cause:** Docker on Apple Silicon builds ARM images by default, but Cloud Run requires linux/amd64.

**Fix:** Always use the platform flag when building:
```bash
docker build --platform linux/amd64 -t ${IMAGE_URL} .
```

### Service Account Name Too Long

**Error:** `"account_id" doesn't match regexp "^[a-z](?:[-a-z0-9]{4,28}[a-z0-9])$"`

**Cause:** GCP service account IDs must be 6-30 characters. Names like `my-long-service-name-runtime` exceed this.

**Fix:** Use abbreviated service account names:
```hcl
# Instead of:
account_id = "${var.service_name}-runtime"  # Could be 31+ chars

# Use:
account_id = "short-name-runtime"  # Ensure <= 30 chars
```

**Validation Rule:** If `${service_name}-runtime` > 30 chars, abbreviate. Examples:
- `content-workforce-agents-runtime` (31) → `cw-agents-runtime` (17)
- `my-application-service-runtime` (31) → `my-app-runtime` (14)

### Python Projects - Module Not Found

**Error:** `ModuleNotFoundError: No module named 'app'` or similar

**Cause:** Python import paths don't match the container directory structure. Common with `src/` directory layouts.

**Fix:** Set PYTHONPATH in Dockerfile:
```dockerfile
# For projects with src/ directory structure
ENV PYTHONPATH="/app/src"

# Adjust CMD to match:
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
# NOT: CMD ["uvicorn", "src.main:app", ...]
```

**Directory Structure Patterns:**

| Structure | PYTHONPATH | CMD |
|-----------|------------|-----|
| `src/main.py` with `from app.config import ...` | `/app/src` | `uvicorn main:app` |
| `app/main.py` with relative imports | `/app` | `uvicorn app.main:app` |
| `main.py` at root | `/app` | `uvicorn main:app` |

### Docker Push to Artifact Registry Fails with 403 Forbidden

**Error:** `failed to fetch anonymous token: 403 Forbidden`

**Cause:** Docker not authenticated with Artifact Registry.

**Fix:**
```bash
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet
gcloud services enable artifactregistry.googleapis.com --project=${PROJECT_ID}
```

### Terraform "No credentials loaded" Error

**Error:** `No credentials loaded. To use your gcloud credentials, run 'gcloud auth application-default login'`

**Cause:** Terraform can't find GCP credentials.

**Fix (choose one):**
```bash
# Option 1: Interactive login (for local dev)
gcloud auth application-default login

# Option 2: Service account key (for CI/CD)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

### Terraform "invalid_grant" / "reauth related error"

**Error:** `oauth2: "invalid_grant" "reauth related error (invalid_rapt)"`

**Cause:** GCP application-default credentials have expired or need re-authentication.

**Fix:**
```bash
# Re-authenticate with application-default credentials
gcloud auth application-default login
```

**Alternative:** If Terraform auth is problematic, use gcloud CLI deploy instead:
```bash
# This uses your regular gcloud auth, not application-default
gcloud run deploy SERVICE_NAME --image=IMAGE_URL --region=REGION ...
```

**When to use gcloud CLI instead of Terraform:**
- Quick one-off deployments
- Auth issues with Terraform
- Simple services without complex infrastructure
- When you don't need state management

### GitHub Actions Deploys with Empty Secrets

**Issue:** Workflow succeeds but service doesn't work. Logs show `--set-env-vars="API_KEY="` (empty values).

**Cause:** GitHub secrets not configured. The workflow uses `${{ secrets.API_KEY }}` which resolves to empty string if secret doesn't exist.

**Fix:** Add all required secrets to GitHub repo:
1. Go to repo Settings → Secrets and variables → Actions
2. Add each secret listed in the workflow file
3. Re-run the workflow or push a new commit

**Note:** The workflow will "succeed" even with empty secrets because `gcloud run deploy` doesn't validate env var values. The service will start but fail when it tries to use the missing credentials.

### Service URL Changes After Update

**Issue:** The Cloud Run URL can change format between deployments.

**Fix:** After `terraform apply`, always get the current URL and update WEBHOOK_URL:
```bash
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)')
gcloud run services update ${SERVICE_NAME} --region=${REGION} --update-env-vars="WEBHOOK_URL=${SERVICE_URL}"
```

---

## Phase 6: CI/CD Setup (Recommended)

Automate deployments on push to main using GitHub Actions with Workload Identity Federation (WIF) for secure keyless authentication.

**Why this phase is recommended:**
- Manual deployments are error-prone and require local tooling
- WIF provides secure keyless authentication (no service account keys to manage)
- Enables continuous deployment from any machine

**Skip this phase only if:**
- Quick one-off deployment for testing
- Service will be deprecated soon
- Organization doesn't use GitHub

### Why Workload Identity Federation?

- **No stored keys** - No long-lived credentials in GitHub secrets
- **Short-lived tokens** - Credentials auto-rotate
- **More secure** - Keys can't leak because they don't exist

### Workflow Structure

**Two workflows are recommended:**

1. **CI workflow** (`.github/workflows/ci.yml`) — Runs on pull requests targeting `main`. Validates the code builds and passes checks before merge.
2. **Deploy workflow** (`.github/workflows/deploy.yml`) — Runs on push to `main` (i.e., after merge). Builds, pushes, and deploys to Cloud Run.

#### Deploy Workflow Steps (push to main)

1. Checkout code
2. Authenticate to GCP using WIF (keyless)
3. Configure Docker for GCR
4. Build image with `--platform linux/amd64` and tag with git SHA
5. Push image to GCR
6. Deploy to Cloud Run (image only - env vars managed in console)
7. Verify deployment (health check)

### CI Workflow (Pull Request Checks)

Create `.github/workflows/ci.yml` to run build validation on PRs. This catches build failures before they reach `main` and trigger a broken deploy.

**What to include depends on the project:**

| Language | Steps |
|----------|-------|
| **Next.js / Node.js** | Install deps → Lint → Build |
| **Python (FastAPI)** | Install deps → Lint (ruff) → Type check (mypy/pyright, optional) → Test (pytest) |
| **Go** | Lint (golangci-lint) → Test → Build |

#### Example: Next.js CI Workflow

```yaml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - name: Install dependencies
        run: npm ci --legacy-peer-deps

      - name: Lint
        run: npm run lint

      - name: Build
        env:
          # Placeholder values for NEXT_PUBLIC_* vars required at build time
          NEXT_PUBLIC_SUPABASE_URL: https://placeholder.supabase.co
          NEXT_PUBLIC_SUPABASE_ANON_KEY: placeholder
          NEXT_PUBLIC_API_BASE_URL: https://placeholder.example.com
        run: npm run build
```

**Note for Next.js:** `NEXT_PUBLIC_*` variables must be present at build time or the build will fail. Use placeholder values in CI — the real values are only needed for the production deploy.

#### Example: Python (FastAPI) CI Workflow

```yaml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v5

      - name: Install dependencies
        run: uv sync

      - name: Lint
        run: uv run ruff check .

      - name: Test
        run: uv run pytest
```

### Adding a New Repo to Existing WIF

If WIF is already set up for another repo in the same project, add the new repo:

```bash
PROJECT_ID="your-project-id"
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format='value(projectNumber)')
NEW_REPO="owner/new-repo-name"

# 1. Check current attribute condition
gcloud iam workload-identity-pools providers describe github-provider \
  --workload-identity-pool=github-pool \
  --location=global \
  --project=${PROJECT_ID} \
  --format="yaml(attributeCondition)"

# 2. Update provider to allow multiple repos (use OR condition)
gcloud iam workload-identity-pools providers update-oidc github-provider \
  --workload-identity-pool=github-pool \
  --location=global \
  --project=${PROJECT_ID} \
  --attribute-condition="assertion.repository=='existing/repo' || assertion.repository=='${NEW_REPO}'"

# 3. Grant service account permission for new repo
gcloud iam service-accounts add-iam-policy-binding github-actions-deploy@${PROJECT_ID}.iam.gserviceaccount.com \
  --project=${PROJECT_ID} \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-pool/attribute.repository/${NEW_REPO}"
```

### One-Time WIF Setup (New Project)

```bash
PROJECT_ID="your-project-id"
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format='value(projectNumber)')
REPO="owner/repo-name"

# 1. Create dedicated service account for GitHub Actions
gcloud iam service-accounts create github-actions-deploy \
    --display-name="GitHub Actions Deploy" \
    --project=${PROJECT_ID}

# 2. Grant required roles
SA_EMAIL="github-actions-deploy@${PROJECT_ID}.iam.gserviceaccount.com"
for role in roles/run.admin roles/storage.admin roles/iam.serviceAccountUser roles/artifactregistry.writer; do
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="${role}"
done

# 3. Create Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" \
    --location="global" \
    --display-name="GitHub Actions Pool" \
    --project=${PROJECT_ID}

# 4. Create OIDC Provider (--attribute-condition is required)
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
    --location="global" \
    --workload-identity-pool="github-pool" \
    --display-name="GitHub Provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
    --attribute-condition="assertion.repository=='${REPO}'" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --project=${PROJECT_ID}

# 5. Allow GitHub repo to impersonate service account
gcloud iam service-accounts add-iam-policy-binding ${SA_EMAIL} \
    --project=${PROJECT_ID} \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-pool/attribute.repository/${REPO}"
```

### Image Tagging Strategy

**Decide BEFORE writing the workflow** how Docker images will be tagged. This choice affects rollback, reproducibility, and how IaC interacts with deployments.

| Strategy | What | Pros | Cons |
|----------|------|------|------|
| **Immutable SHA tags (recommended)** | Each build is tagged with the git commit SHA only (e.g. `:abc123def`). No `:latest` tag. | Reproducible (deployed image always traces to a commit); easy rollback (deploy a previous SHA); no race conditions; works cleanly with GitOps tooling | Deployment system must know the specific SHA to deploy |
| **`:latest` tag** | Each build is tagged with both `:<sha>` AND `:latest`. Deployment system references `:latest`. | Familiar mental model ("push = latest"); IaC can reference a stable name | **Race conditions** if two pushes finish out of order; harder rollback (must retag); no reproducibility (can't tell which commit produced the deployed image) |

**Recommendation: immutable SHA tags.** Modern Cloud Run deployments and GitOps tools (Flux, ArgoCD) use this pattern. The skill's example workflows in this section all use `${{ github.sha }}` as the tag.

#### Critical trap: don't mix the two strategies

The most dangerous failure mode is **a workflow that uses SHA tags + IaC that references `:latest`**. This silently breaks deploys:

1. Workflow builds and deploys `:<sha>` correctly. New revision is created and serves traffic.
2. IaC (e.g. terraform) has `image = "...:latest"` in its config. Nothing in CI/CD ever updates `:latest`.
3. `:latest` becomes frozen at whatever was last tagged manually (often during initial setup or a one-time bulk push).
4. **Every subsequent `terraform apply` (for any reason — env var changes, scaling tweaks, IAM changes) silently reverts the deployed image to the stale `:latest`**, undoing the workflow's most recent deploy.
5. The bug is invisible — no error, no warning, no failed health check. The new revision boots successfully (it's a working older image), traffic shifts to it, and the latest code is gone.

**Symptoms** that suggest you've fallen into this trap:
- Code changes you pushed don't appear to be running, even though the workflow succeeded
- "Force redeploy" hacks like manually tweaking an env var to push out a new revision
- Mysterious env vars in production with names like `WIRING_UPDATED=true` (someone's workaround)
- Different team members reporting "I deployed this fix days ago and it's still broken"

**If you find yourself in this hybrid state**, fix it ONE of these ways:
- **Add `:latest` push to the workflow** (every build pushes BOTH `:<sha>` AND `:latest`). Eliminates the `terraform apply` rollback. Simple but has race conditions on concurrent pushes — only safe with single-pusher workflows.
- **Tell IaC to ignore the image field**. For terraform, add `lifecycle { ignore_changes = [template[0].containers[0].image] }` to the `google_cloud_run_v2_service` resource. The workflow becomes the sole authority on the image. The `image` field in tfvars is only used on initial create. **This is the recommended fix.** See "Environment Variables Strategy → Option C: Hybrid" below for the full pattern.

### Environment Variables Strategy

**ASK THE USER:** How should environment variables be managed in CI/CD?

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **Console-managed (Recommended for simple setups)** | Set env vars once in Cloud Run console or via initial deploy. CI/CD only updates code. | No GitHub secrets needed, simple workflow, env vars rarely change | Must use console/gcloud to update env vars; no audit trail |
| **GitHub Secrets** | Store all env vars as GitHub secrets, workflow sets them on each deploy via `--set-env-vars` | Env vars version-controlled with deploys (in workflow file) | Duplicate secrets, more complex workflow; secrets are write-only (can't diff or inspect) |
| **Hybrid (Terraform + workflow)** | Terraform manages env vars in tfvars files. Workflow only manages images. Terraform Cloud Run resource has `lifecycle { ignore_changes = [image] }`. | Audit trail via tfvars; `terraform plan` shows env var diffs; workflow stays simple | Requires `ignore_changes` discipline (silent rollback bug if forgotten); `image` field in tfvars is misleading |

**Recommendation: Console-managed for simple setups, Hybrid for setups that already use Terraform.** The console-managed approach is simplest and works well when env vars are stable. The hybrid approach gives you a reviewable audit trail via tfvars at the cost of needing to remember the `ignore_changes` discipline. Avoid GitHub Secrets unless you specifically need every env var change to be linked to a workflow run.

#### Option A: Console-Managed Env Vars (Default)

1. Set env vars once during initial manual deploy via `gcloud run deploy --set-env-vars=...` or the Cloud Run console
2. Manage env vars in Cloud Run console: Service → Edit & Deploy New Revision → Variables & Secrets
3. CI/CD workflow only deploys new images - existing env vars are preserved

**Workflow deploys image only:**
```yaml
- name: Deploy to Cloud Run
  run: |
    # Deploy new image only - env vars managed in Cloud Run console
    gcloud run deploy ${{ env.SERVICE_NAME }} \
      --image ${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.AR_REPO }}/${{ env.SERVICE_NAME }}:${{ github.sha }} \
      --region ${{ env.REGION }} \
      --project ${{ env.PROJECT_ID }} \
      --platform managed
```

#### Option B: GitHub Secrets

If you need env vars to be version-controlled with deployments, add secrets to GitHub (Settings → Secrets → Actions):

**Required secrets (sensitive values from .env):**

| Secret | Description |
|--------|-------------|
| `API_KEY` | Service authentication key |
| `OPENAI_API_KEY` | OpenAI/OpenRouter API key |
| `OPENROUTER_API_KEY` | OpenRouter API key (if separate) |
| `GOOGLE_API_KEY` | Google API key |
| `LANGFUSE_SECRET_KEY` | Langfuse observability key |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key |
| `BACKEND_API_URL` | Backend API endpoint |

**Note:** Non-sensitive config (ENVIRONMENT, models, providers) can be hardcoded in the workflow.

#### Option C: Hybrid — Terraform for env vars, workflow for image

If you want terraform to manage env vars (audit trail via tfvars, `terraform plan` visibility) but the workflow to manage code deploys, this is the cleanest pattern:

1. **Workflow** tags each build with the commit SHA and deploys via `gcloud run deploy --image=...:<sha>` (same workflow as Option A — no `--set-env-vars`)
2. **Terraform** manages everything else on the Cloud Run service: env vars (via dynamic `env` block), scaling, IAM, networking, etc.
3. **Critical**: Terraform's Cloud Run resource MUST exclude the image field from management. Otherwise every `terraform apply` will pull the `image` value from tfvars (typically `:latest`, which the workflow never updates) and silently revert the deployed image.

```hcl
resource "google_cloud_run_v2_service" "service" {
  name     = var.service_name
  location = var.region

  template {
    containers {
      image = var.image  # Only used on initial create — see lifecycle block below

      dynamic "env" {
        for_each = var.env_vars
        content {
          name  = env.key
          value = env.value
        }
      }
      # ... rest of container config ...
    }
    # ... rest of template ...
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  # The container image is managed by the GitHub Actions workflow using the
  # git commit SHA as the tag. Terraform must NOT manage the image field —
  # without this ignore_changes block, every `terraform apply` would silently
  # revert the deployed image to whatever value is in tfvars (e.g. :latest),
  # undoing the workflow's latest deploy.
  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }
}
```

**About the `image` field in tfvars**: It's only used when terraform creates a brand-new service from scratch. After the service exists, the `lifecycle { ignore_changes }` makes terraform leave the image alone. To avoid confusion for future maintainers, add a comment in tfvars or in the resource explaining that changing the `image` field has no effect on existing services — use the workflow or `gcloud run services update --image=...` to change the image.

**Workflow**: Use the same workflow as Option A (image-only deploy via `gcloud run deploy --image=...:<sha>`). Do NOT add `--set-env-vars` — env vars are managed by terraform.

**Updating env vars**: Edit tfvars locally, run `terraform apply`. Because `image` is in `ignore_changes`, the apply will only touch env vars and other infra fields. The deployed image is preserved.

**Rolling back code**: Use `gcloud run services update <service> --image=...:<previous-sha>` (rollback is a workflow concern, not a terraform concern). Or shift traffic via `gcloud run services update-traffic`.

**Pros**:
- Env var changes are reviewable (tfvars + `terraform plan`)
- Workflow stays simple (image only, no env var bookkeeping)
- Clear separation of concerns: terraform owns infra, workflow owns code

**Cons**:
- Requires the `ignore_changes` discipline. Forgetting it triggers the silent rollback bug described in "Image Tagging Strategy → Critical trap"
- The `image` field in tfvars is misleading (looks like it sets the image, actually doesn't after initial create). Mitigate with a comment in the tfvars or main.tf

#### Operational discipline when modifying env vars on an existing Hybrid-managed service

This is the workflow you follow **every time** you need to add, change, or remove an env var on a service that's already deployed with Option C Hybrid. Skipping steps here is how you end up with silent rollbacks, deleted service accounts, and production-down at 2am.

1. **Check working tree is clean and you're on the right branch.** `git status` and `git branch --show-current`. Never start terraform work on a dirty branch or the wrong branch — surprises compound fast.

2. **Edit ONLY the tfvars file(s).** For Option C Hybrid, env vars live in `env_vars = {}` map inside `terraform.testing.tfvars` / `terraform.production.tfvars`. Adding a new env var is a one-line addition to the map. **No `variables.tf` or `main.tf` changes needed** — the `dynamic "env" { for_each = var.env_vars }` block picks up new keys automatically.

3. **Do NOT touch the `image` field.** It's pinned to a specific SHA on purpose. Leave it alone. If you accidentally edit it, `lifecycle.ignore_changes` will save you, but the diff will be confusing in code review.

4. **Run `terraform plan` FIRST — always.** Never `terraform apply` without reviewing the plan. The canonical command:

   ```bash
   cd infrastructure
   terraform plan -var-file=terraform.testing.tfvars -state=terraform.testing.tfstate
   ```

5. **Review the plan output before applying.** Look for:
   - ✅ **`0 to destroy`** — this MUST hold. If terraform wants to destroy anything, STOP and investigate. The #1 source of Cloud Run incidents is a plan with unexpected destroys that nobody reviewed.
   - ✅ Only the env var additions/changes you expected — nothing else on the Cloud Run resource should appear as modified.
   - ✅ The `image` field is NOT in the diff (if it is, your `lifecycle.ignore_changes` is missing or broken — STOP).
   - ⚠️ No unexpected IAM changes, no service account creation/deletion, no state migration errors.
   - ⚠️ If the plan wants to recreate the service (`-/+ destroy and then create replacement`), STOP IMMEDIATELY. Recreating a Cloud Run service changes its URL and breaks every caller.

6. **Only apply if the plan is clean.**
   ```bash
   terraform apply -var-file=terraform.testing.tfvars -state=terraform.testing.tfstate
   ```

7. **Verify on Cloud Run after apply:**
   ```bash
   gcloud run services describe <service-name> \
     --region=<region> --project=<project> \
     --format='value(spec.template.spec.containers[0].env)' \
     | tr ';' '\n' | grep -i <YOUR_NEW_VAR>
   ```

8. **Repeat for production.** Phase 3 is always two applies: testing first, then production. **Never combine them.** Plan testing → review → apply testing → verify → plan production → review → apply production → verify.

9. **Commit the tfvars edits.** Use a specific file add (`git add infrastructure/terraform.testing.tfvars infrastructure/terraform.production.tfvars`), not `git add -A`. Reference the related issue/spec in the commit message.

#### tfvars gitignore: non-negotiable

**`terraform.*.tfvars` MUST be in `.gitignore`** when using Option C Hybrid. These files contain real env var values, which in practice means real API keys, database URLs, secret tokens, etc. Committing them is a security incident.

Canonical `.gitignore` entries for an infrastructure/ directory:

```gitignore
# Terraform
infrastructure/terraform.*.tfvars
infrastructure/terraform.*.tfstate
infrastructure/terraform.*.tfstate.backup
infrastructure/.terraform/
infrastructure/.terraform.lock.hcl

# Keep the example files
!infrastructure/terraform.tfvars.example
```

**Double-check before any commit:**
```bash
git check-ignore -v infrastructure/terraform.testing.tfvars
# Should output the gitignore rule that excludes it. If not, the file WILL get committed.
```

If you discover tfvars have been tracked in the past, `git rm --cached` them, commit the removal, rotate any secrets they contained, and make sure the `.gitignore` rule is in place.

#### Image field comment convention

Because the `image` field in tfvars is misleading (looks like it sets the image, actually ignored after initial create), put a loud comment right next to it so future maintainers don't "fix" it back to `:latest`:

```hcl
# tfvars snippet
# -----------------------------------------------------------------------------
# IMAGE PINNING
# -----------------------------------------------------------------------------
# The image field is IGNORED by terraform after the service is created (see
# lifecycle.ignore_changes in main.tf). Changing this SHA in tfvars has NO
# EFFECT on the deployed service — the image is managed by the GitHub Actions
# workflow using the git commit SHA as the tag.
#
# DO NOT change this back to ":latest" — that re-introduces the silent
# rollback bug (see cloudrun-deploy skill → "Image Tagging Strategy → Critical
# trap").
#
# To roll back: `gcloud run services update <service> --image=...:<previous-sha>`
# -----------------------------------------------------------------------------
image_url = "europe-west1-docker.pkg.dev/PROJECT/REPO/SERVICE:<40-char-sha>"
```

#### CLAUDE.md deployment section (template)

Every repo that deploys to Cloud Run via Option C Hybrid should have a Deployment section in its `CLAUDE.md` that future sessions (human or agent) will read before making terraform changes. Minimum content:

```markdown
## Deployment

This service deploys to Cloud Run via the Option C Hybrid pattern (see the
cloudrun-deploy skill): the GitHub Actions workflow owns the image (SHA-tagged),
Terraform owns everything else (env vars, scaling, IAM).

**Terraform does NOT manage the image field.** The Cloud Run resource has
`lifecycle { ignore_changes = [template[0].containers[0].image] }`. Changing
the `image` field in tfvars has no effect on subsequent applies.

### Updating environment variables

1. Edit `infrastructure/terraform.testing.tfvars` or `terraform.production.tfvars`
2. **Always run `terraform plan` first** and verify `0 to destroy` before applying.
3. Apply:
   ```bash
   terraform apply -var-file=terraform.testing.tfvars -state=terraform.testing.tfstate
   ```
4. Verify on Cloud Run:
   ```bash
   gcloud run services describe <service> --region=<region> \
     --format='value(spec.template.spec.containers[0].env)'
   ```
5. Repeat for production.

### Rollback

- Traffic shift: `gcloud run services update-traffic <service> --to-revisions=<previous>=100`
- Image rollback: `gcloud run services update <service> --image=...:<previous-sha>`

### tfvars are gitignored

`terraform.*.tfvars` contain real secrets and are in `.gitignore`. Do not commit them.
```

### WIF Values for Workflow

These values are **not sensitive** (security comes from the WIF setup itself) and can be hardcoded in the workflow file:

| Value | Format |
|-------|--------|
| `WIF_PROVIDER` | `projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider` |
| `WIF_SERVICE_ACCOUNT` | `github-actions-deploy@PROJECT_ID.iam.gserviceaccount.com` |

### Example Workflow File (Console-Managed Env Vars - Recommended)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]
  workflow_dispatch:  # Allow manual trigger

env:
  PROJECT_ID: your-project-id
  SERVICE_NAME: your-service
  REGION: europe-west1
  AR_REPO: cloud-run-services  # Artifact Registry repository name
  # WIF values - not sensitive, security is in the GCP WIF setup
  WIF_PROVIDER: projects/YOUR_PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider
  WIF_SERVICE_ACCOUNT: github-actions-deploy@your-project-id.iam.gserviceaccount.com

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write  # Required for WIF

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ env.WIF_PROVIDER }}
          service_account: ${{ env.WIF_SERVICE_ACCOUNT }}

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      - name: Configure Docker for Artifact Registry
        run: gcloud auth configure-docker ${{ env.REGION }}-docker.pkg.dev --quiet

      - name: Build and Push Docker image
        run: |
          IMAGE_URL="${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.AR_REPO }}/${{ env.SERVICE_NAME }}:${{ github.sha }}"
          docker build --platform linux/amd64 -t ${IMAGE_URL} .
          docker push ${IMAGE_URL}

      - name: Deploy to Cloud Run
        run: |
          # Deploy new image only - env vars are managed in Cloud Run console
          gcloud run deploy ${{ env.SERVICE_NAME }} \
            --image ${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.AR_REPO }}/${{ env.SERVICE_NAME }}:${{ github.sha }} \
            --region ${{ env.REGION }} \
            --project ${{ env.PROJECT_ID }} \
            --platform managed

      - name: Verify deployment
        run: |
          SERVICE_URL=$(gcloud run services describe ${{ env.SERVICE_NAME }} \
            --region=${{ env.REGION }} \
            --project=${{ env.PROJECT_ID }} \
            --format='value(status.url)')
          echo "Service URL: ${SERVICE_URL}"
          curl -s "${SERVICE_URL}/health" | jq .
```

**Key point:** This workflow does NOT set any `--set-env-vars`. Environment variables are:
1. Set once during initial manual deploy via `gcloud run deploy --set-env-vars=...` sourcing `.env`
2. Managed in Cloud Run console when changes are needed
3. Preserved automatically when deploying new images

### Example Workflow File (GitHub Secrets)

Use this version if you need env vars version-controlled with deployments:

```yaml
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy ${{ env.SERVICE_NAME }} \
            --image ${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.AR_REPO }}/${{ env.SERVICE_NAME }}:${{ github.sha }} \
            --region ${{ env.REGION }} \
            --project ${{ env.PROJECT_ID }} \
            --platform managed \
            --set-env-vars="ENVIRONMENT=production" \
            --set-env-vars="DATABASE_HOST=${{ secrets.DATABASE_HOST }}" \
            --set-env-vars="DATABASE_PASSWORD=${{ secrets.DATABASE_PASSWORD }}" \
            # ... add all required env vars
```

### Multi-Environment Deployments

For deploying to multiple environments (dev, staging, prod), use branch-based or manual triggers with environment-specific configuration.

#### Option A: Branch-Based Environments

| Branch | Environment | Trigger |
|--------|-------------|---------|
| `main` | Production | Push to main |
| `staging` | Staging | Push to staging |
| `develop` | Development | Push to develop |

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main, staging, develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write

    steps:
      - uses: actions/checkout@v4

      - name: Set environment variables
        run: |
          if [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
            echo "ENV=prod" >> $GITHUB_ENV
            echo "PROJECT_ID=myproject-prod" >> $GITHUB_ENV
          elif [[ "${{ github.ref }}" == "refs/heads/staging" ]]; then
            echo "ENV=staging" >> $GITHUB_ENV
            echo "PROJECT_ID=myproject-staging" >> $GITHUB_ENV
          else
            echo "ENV=dev" >> $GITHUB_ENV
            echo "PROJECT_ID=myproject-dev" >> $GITHUB_ENV
          fi

      - id: auth
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets[format('WIF_PROVIDER_{0}', env.ENV)] }}
          service_account: ${{ secrets[format('WIF_SERVICE_ACCOUNT_{0}', env.ENV)] }}

      # ... rest of deployment steps
```

#### Option B: GitHub Environments (Recommended)

Use GitHub Environments for better control, approval gates, and environment-specific secrets.

**Setup:**
1. Go to repo Settings → Environments
2. Create environments: `development`, `staging`, `production`
3. Add environment-specific secrets (WIF_PROVIDER, WIF_SERVICE_ACCOUNT, PROJECT_ID)
4. Add protection rules for production (required reviewers, wait timer)

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        type: choice
        options:
          - development
          - staging
          - production

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment || 'development' }}
    permissions:
      contents: read
      id-token: write

    steps:
      - uses: actions/checkout@v4

      - id: auth
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}

      - uses: google-github-actions/setup-gcloud@v2

      - name: Configure Docker
        run: gcloud auth configure-docker ${{ vars.REGION }}-docker.pkg.dev --quiet

      - name: Build and Push
        run: |
          IMAGE_URL="${{ vars.REGION }}-docker.pkg.dev/${{ secrets.PROJECT_ID }}/${{ vars.AR_REPO }}/${{ vars.SERVICE_NAME }}:${{ github.sha }}"
          docker build --platform linux/amd64 -t ${IMAGE_URL} .
          docker push ${IMAGE_URL}

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy ${{ vars.SERVICE_NAME }} \
            --image ${{ vars.REGION }}-docker.pkg.dev/${{ secrets.PROJECT_ID }}/${{ vars.AR_REPO }}/${{ vars.SERVICE_NAME }}:${{ github.sha }} \
            --region ${{ vars.REGION }} \
            --platform managed \
            --set-env-vars="ENV=${{ github.event.inputs.environment || 'development' }}"
```

#### WIF Setup Per Environment

Each environment needs its own WIF configuration. Run the setup commands once per environment:

```bash
# For each environment (dev, staging, prod)
ENV="prod"  # or "staging" or "dev"
PROJECT_ID="myproject-${ENV}"

# Create service account per environment
gcloud iam service-accounts create github-actions-deploy \
    --display-name="GitHub Actions Deploy (${ENV})" \
    --project=${PROJECT_ID}

# ... rest of WIF setup commands with environment-specific project
```

#### Environment Secrets Matrix

| Secret | Development | Staging | Production |
|--------|-------------|---------|------------|
| `WIF_PROVIDER` | projects/DEV_NUM/... | projects/STG_NUM/... | projects/PROD_NUM/... |
| `WIF_SERVICE_ACCOUNT` | ...@dev.iam... | ...@staging.iam... | ...@prod.iam... |
| `PROJECT_ID` | myproject-dev | myproject-staging | myproject-prod |

#### Environment Variables

| Variable | Development | Staging | Production |
|----------|-------------|---------|------------|
| `SERVICE_NAME` | myservice | myservice | myservice |
| `REGION` | europe-west1 | europe-west1 | europe-west1 |

### Promotion Workflow

For promoting between environments (dev → staging → prod):

```yaml
name: Promote Release

on:
  workflow_dispatch:
    inputs:
      source_env:
        description: 'Source environment'
        required: true
        type: choice
        options: [development, staging]
      target_env:
        description: 'Target environment'
        required: true
        type: choice
        options: [staging, production]
      image_tag:
        description: 'Image tag to promote (git SHA)'
        required: true

jobs:
  promote:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.target_env }}
    permissions:
      contents: read
      id-token: write

    steps:
      - id: auth
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}

      - uses: google-github-actions/setup-gcloud@v2

      - name: Deploy promoted image
        run: |
          # Image already exists in registry from source env build
          gcloud run deploy ${{ vars.SERVICE_NAME }} \
            --image ${{ vars.REGION }}-docker.pkg.dev/${{ secrets.PROJECT_ID }}/${{ vars.AR_REPO }}/${{ vars.SERVICE_NAME }}:${{ github.event.inputs.image_tag }} \
            --region ${{ vars.REGION }} \
            --platform managed
```

---

## Discovery Questions Template

Use these questions to gather information:

```markdown
## Service Identity
- What is the service name? (lowercase, hyphens only)
- Brief description of what the service does?

## GCP Target
- Which GCP project? (use `gcloud projects list` to find)
- Which region? (default: europe-west1)

## Source Code
- Does the project have a Dockerfile?
- What language/framework?
- What port does the application listen on?
- What is the entry point command?

## Resources
- Expected memory needs? (default: 512Mi, LLM services need 1Gi+)
- Should it scale to zero? (cost saving vs cold starts)
- Maximum concurrent requests per instance?

## Environment Variables
- List all required environment variables
- Which ones are secrets? (API keys, passwords, tokens)

## Secrets Management
- How should secrets be stored?
  - Plain environment variables (simpler, visible in console)
  - GCP Secret Manager (more secure, audit logging)

## Deployment Method
- Which deployment method do you prefer?
  - gcloud CLI (simpler, single command)
  - Terraform (full IaC, version controlled)

## CI/CD Environment Variables
- How should env vars be managed in CI/CD?
  - Console-managed (Recommended) - Set once, CI/CD only deploys code
  - GitHub Secrets - Store all env vars in GitHub, set on each deploy

## Access Control
- Should this be publicly accessible?
- Does it need to be behind authentication?
- Does it receive webhooks?

## GCP Dependencies
- Does it access Cloud Storage, Firestore, Cloud SQL, etc.?
- Does it need to call other internal services?
```

---

## Output Files

After running this skill, the following files should exist:

```
project/
├── Dockerfile                 # Container definition
├── .dockerignore             # Build exclusions
├── .github/workflows/
│   └── deploy.yml            # CI/CD workflow (build, push, deploy on git push)
└── infrastructure/           # (if using Terraform)
    ├── main.tf               # Cloud Run service (includes lifecycle.ignore_changes for image)
    ├── variables.tf          # Variable declarations
    ├── terraform.tfvars      # Variable values (gitignored if contains secrets)
    ├── terraform.tfvars.example  # Template for values
    ├── secrets.tf            # Secret Manager (only if chosen)
    ├── iam.tf                # Service account & IAM
    └── outputs.tf            # Service URL, etc.
```

**Note:** There is intentionally no `deploy.sh` script. Manual deploys are done via `git push` to the appropriate branch (which triggers the GitHub Actions workflow) or via `gcloud run deploy --image=...` for emergency deploys. A local `deploy.sh` script would duplicate the workflow's logic and can silently drift out of sync with it.

---

## References

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Terraform Google Provider - Cloud Run](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_v2_service)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [Cloud Run Quotas](https://cloud.google.com/run/quotas)
