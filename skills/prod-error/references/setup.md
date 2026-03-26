# First-Time Setup: GCP Service Account

> **When to read:** On first run of `/prod-error` or when authentication fails during pre-flight.

This guide walks through creating a service account with the minimum permissions needed to investigate production errors on Cloud Run.

---

## Step 1: Create the Service Account

Run this in the terminal (replace `PROJECT_ID` with your GCP project):

```bash
gcloud iam service-accounts create claude-prod-error \
  --display-name="Claude Prod Error Investigator" \
  --project=PROJECT_ID
```

This creates a service account named `claude-prod-error@PROJECT_ID.iam.gserviceaccount.com`.

---

## Step 2: Grant Required Roles

Four roles are needed:

```bash
PROJECT_ID="your-project-id"
SA_EMAIL="claude-prod-error@${PROJECT_ID}.iam.gserviceaccount.com"

# Manage Cloud Run services (read + update env vars)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

# Read logs
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/logging.viewer"

# Read error reports (optional, for Error Reporting integration)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/errorreporting.viewer"
```

### Role Summary

| Role | Purpose | Access Level |
|------|---------|-------------|
| `roles/run.admin` | List services, revisions, update env vars | Read + Write |
| `roles/logging.viewer` | Read Cloud Logging entries | Read-only |
| `roles/errorreporting.viewer` | Read Error Reporting groups | Read-only |

---

## Step 3: Download the Key

```bash
mkdir -p ~/.config/gcloud/service-accounts

gcloud iam service-accounts keys create \
  ~/.config/gcloud/service-accounts/claude-prod-error.json \
  --iam-account="${SA_EMAIL}"
```

Verify the key was created:

```bash
ls -la ~/.config/gcloud/service-accounts/claude-prod-error.json
```

---

## Step 4: Activate and Test

Activate the service account:

```bash
gcloud auth activate-service-account --key-file=~/.config/gcloud/service-accounts/claude-prod-error.json
```

Set the default project:

```bash
gcloud config set project $PROJECT_ID
```

Test that it works:

```bash
gcloud run services list --format="table(metadata.name, region)" 2>/dev/null
```

If you see your services listed, setup is complete.

---

## Multiple Projects

If you work across multiple GCP projects, you can create named configurations:

```bash
# Create a config for each project
gcloud config configurations create project-a
gcloud config set project project-a-id
gcloud auth activate-service-account --key-file=~/.config/gcloud/service-accounts/claude-prod-error.json

gcloud config configurations create project-b
gcloud config set project project-b-id
gcloud auth activate-service-account --key-file=~/.config/gcloud/service-accounts/claude-prod-error.json

# Switch between them
gcloud config configurations activate project-a
```

The `/prod-error` skill will use whichever configuration is currently active.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `PERMISSION_DENIED` on logs | Verify `roles/logging.viewer` is granted to the SA |
| `Could not find service account` | Check the SA email matches your project ID |
| `Key file not found` | Re-run Step 3 to download the key |
| `gcloud not found` | Install the gcloud CLI: `brew install google-cloud-sdk` |
| Auth keeps expiring | You're likely using user auth — switch to the SA key with `gcloud auth activate-service-account` |
