# Deployment Checklist: {{SERVICE_NAME}}

## Pre-Deployment

### GCP Infrastructure
- [ ] GCP project exists with billing enabled
- [ ] Required APIs enabled (Cloud Run, Container Registry)
- [ ] Terraform service account created with correct permissions
- [ ] Service account key file exists locally
- [ ] Docker authenticated to GCR (`gcloud auth configure-docker`)

### Local Tools
- [ ] Terraform installed (`terraform --version`)
- [ ] Docker installed and running (`docker --version`)
- [ ] gcloud CLI installed (`gcloud --version`)

## Discovery Complete

### Service Identity
- [ ] Service name: `{{SERVICE_NAME}}`
- [ ] GCP project: `{{PROJECT_ID}}`
- [ ] Region: `{{REGION}}`

### Source Code
- [ ] Dockerfile exists or generated
- [ ] Port identified: `{{PORT}}`
- [ ] Entry point confirmed

### Resources
- [ ] Memory: `{{MEMORY}}`
- [ ] CPU: `{{CPU}}`
- [ ] Min instances: `{{MIN_INSTANCES}}`
- [ ] Max instances: `{{MAX_INSTANCES}}`
- [ ] Concurrency: `{{CONCURRENCY}}`
- [ ] Timeout: `{{TIMEOUT_SECONDS}}s`

### Environment Variables
- [ ] All environment variables documented
- [ ] Secrets identified and values obtained
- [ ] Non-secret vars added to terraform.tfvars

### Access Control
- [ ] Ingress setting: `{{INGRESS}}`
- [ ] Allow unauthenticated: `{{ALLOW_UNAUTHENTICATED}}`
- [ ] Custom domain: `{{CUSTOM_DOMAIN}}`

### GCP Dependencies
- [ ] All required IAM roles identified
- [ ] IAM bindings added to iam.tf

## Ready to Deploy

### Build Phase
- [ ] Dockerfile tested locally (`docker build`)
- [ ] Container runs locally (`docker run`)
- [ ] Image pushed to registry (`docker push`)

### Infrastructure Phase
- [ ] Terraform files generated
- [ ] `terraform init` successful
- [ ] `terraform plan` shows expected changes
- [ ] Secrets created in Secret Manager (if applicable)
- [ ] `terraform apply` successful

## Post-Deployment

### Verification
- [ ] Service URL accessible: `{{SERVICE_URL}}`
- [ ] Health check passing
- [ ] Logs showing expected behavior
- [ ] Environment variables loaded correctly
- [ ] Secrets accessible (if applicable)
- [ ] GCP service dependencies working

### Documentation
- [ ] README updated with deployment instructions
- [ ] Environment variables documented
- [ ] Rollback procedure documented

---

## Service Details

| Field | Value |
|-------|-------|
| Service Name | `{{SERVICE_NAME}}` |
| Project ID | `{{PROJECT_ID}}` |
| Region | `{{REGION}}` |
| Service URL | `{{SERVICE_URL}}` |
| Image URL | `{{IMAGE_URL}}` |

## Commands Reference

```bash
# Build and push
docker build -t gcr.io/{{PROJECT_ID}}/{{SERVICE_NAME}}:latest .
docker push gcr.io/{{PROJECT_ID}}/{{SERVICE_NAME}}:latest

# Deploy
cd infrastructure && terraform apply

# Verify
curl {{SERVICE_URL}}/health

# Logs
gcloud run services logs read {{SERVICE_NAME}} --region={{REGION}} --limit=50

# Rollback
gcloud run services update-traffic {{SERVICE_NAME}} --region={{REGION}} --to-revisions=REVISION=100
```
