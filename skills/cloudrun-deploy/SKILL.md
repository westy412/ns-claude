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
| Container Registry enabled | `gcloud services list --enabled` | `gcloud services enable containerregistry.googleapis.com` |
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
| `roles/storage.admin` | Push images to Container Registry (if using GCR) |
| `roles/artifactregistry.writer` | Push images to Artifact Registry (if using AR) |
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
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/secretmanager.admin"
```

### Docker Authentication

```bash
gcloud auth configure-docker
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
| `region` | Cloud Run region | `europe-west2` |

**Supported Regions:**
```
europe-west2 (London), europe-west1 (Belgium), us-central1 (Iowa),
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
| `deploy.sh` | Orchestration script |

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
IMAGE_URL="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

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

# Preview changes
terraform plan

# Apply changes
terraform apply -auto-approve
```

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

### Step 4: Verification Checklist

- [ ] Service URL accessible
- [ ] Health check passing
- [ ] Logs showing expected behavior
- [ ] Environment variables loaded correctly
- [ ] Secrets accessible (if applicable)
- [ ] GCP service dependencies working

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

### Docker Push to GCR Fails with 403 Forbidden

**Error:** `failed to fetch anonymous token: 403 Forbidden`

**Cause:** Docker not authenticated with Google Container Registry.

**Fix:**
```bash
gcloud auth configure-docker gcr.io --quiet
gcloud services enable containerregistry.googleapis.com --project=${PROJECT_ID}
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

### Environment Variables Strategy

**ASK THE USER:** How should environment variables be managed in CI/CD?

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **Console-managed (Recommended)** | Set env vars once in Cloud Run console or via initial deploy. CI/CD only updates code. | No GitHub secrets needed, simple workflow, env vars rarely change | Must use console/gcloud to update env vars |
| **GitHub Secrets** | Store all env vars as GitHub secrets, workflow sets them on each deploy | Env vars version-controlled with deploys | Duplicate secrets, more complex workflow |

**Recommendation: Console-managed** - Environment variables rarely change, and when they do, updating via Cloud Run console is straightforward. This keeps the workflow simple and avoids duplicating secrets.

#### Option A: Console-Managed Env Vars (Default)

1. Set env vars once during initial manual deploy (via `deploy.sh` or gcloud CLI)
2. Manage env vars in Cloud Run console: Service → Edit & Deploy New Revision → Variables & Secrets
3. CI/CD workflow only deploys new images - existing env vars are preserved

**Workflow deploys image only:**
```yaml
- name: Deploy to Cloud Run
  run: |
    # Deploy new image only - env vars managed in Cloud Run console
    gcloud run deploy ${{ env.SERVICE_NAME }} \
      --image gcr.io/${{ env.PROJECT_ID }}/${{ env.SERVICE_NAME }}:${{ github.sha }} \
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
  REGION: europe-west2
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

      - name: Configure Docker for GCR
        run: gcloud auth configure-docker gcr.io --quiet

      - name: Build and Push Docker image
        run: |
          IMAGE_URL="gcr.io/${{ env.PROJECT_ID }}/${{ env.SERVICE_NAME }}:${{ github.sha }}"
          docker build --platform linux/amd64 -t ${IMAGE_URL} .
          docker push ${IMAGE_URL}

      - name: Deploy to Cloud Run
        run: |
          # Deploy new image only - env vars are managed in Cloud Run console
          gcloud run deploy ${{ env.SERVICE_NAME }} \
            --image gcr.io/${{ env.PROJECT_ID }}/${{ env.SERVICE_NAME }}:${{ github.sha }} \
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
1. Set once during initial manual deploy (via `deploy.sh` sourcing `.env`)
2. Managed in Cloud Run console when changes are needed
3. Preserved automatically when deploying new images

### Example Workflow File (GitHub Secrets)

Use this version if you need env vars version-controlled with deployments:

```yaml
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy ${{ env.SERVICE_NAME }} \
            --image gcr.io/${{ env.PROJECT_ID }}/${{ env.SERVICE_NAME }}:${{ github.sha }} \
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
        run: gcloud auth configure-docker gcr.io --quiet

      - name: Build and Push
        run: |
          IMAGE_URL="gcr.io/${{ secrets.PROJECT_ID }}/${{ vars.SERVICE_NAME }}:${{ github.sha }}"
          docker build --platform linux/amd64 -t ${IMAGE_URL} .
          docker push ${IMAGE_URL}

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy ${{ vars.SERVICE_NAME }} \
            --image gcr.io/${{ secrets.PROJECT_ID }}/${{ vars.SERVICE_NAME }}:${{ github.sha }} \
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
| `REGION` | europe-west2 | europe-west2 | europe-west2 |

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
            --image gcr.io/${{ secrets.PROJECT_ID }}/${{ vars.SERVICE_NAME }}:${{ github.event.inputs.image_tag }} \
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
- Which region? (default: europe-west2)

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
├── infrastructure/           # (if using Terraform)
│   ├── main.tf               # Cloud Run service
│   ├── variables.tf          # Variable declarations
│   ├── terraform.tfvars      # Variable values (gitignored)
│   ├── terraform.tfvars.example  # Template for values
│   ├── secrets.tf            # Secret Manager (only if chosen)
│   ├── iam.tf                # Service account & IAM
│   └── outputs.tf            # Service URL, etc.
└── deploy.sh                 # Deployment script (supports both gcloud and Terraform)
```

**Note:** If user chose gcloud CLI deployment with plain env vars, `infrastructure/` may be minimal or skipped entirely.

---

## References

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Terraform Google Provider - Cloud Run](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_v2_service)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [Cloud Run Quotas](https://cloud.google.com/run/quotas)
