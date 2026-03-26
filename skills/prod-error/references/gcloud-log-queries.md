# GCloud Log Query Reference

> **When to read:** During Step 2 (Retrieve Error Logs) when building log filter queries.

---

## Cloud Run Error Logs

### Basic error query (last 1 hour)

```bash
gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="SERVICE_NAME" AND severity>=ERROR' \
  --limit=20 \
  --format=json \
  --freshness=1h
```

### Widen to 24 hours

```bash
gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="SERVICE_NAME" AND severity>=ERROR' \
  --limit=50 \
  --format=json \
  --freshness=24h
```

### Include warnings

```bash
gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="SERVICE_NAME" AND severity>=WARNING' \
  --limit=30 \
  --format=json \
  --freshness=1h
```

### Search for a specific error message

```bash
gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="SERVICE_NAME" AND textPayload=~"ERROR_TEXT"' \
  --limit=20 \
  --format=json \
  --freshness=24h
```

### JSON payload errors (structured logging)

```bash
gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="SERVICE_NAME" AND jsonPayload.severity="ERROR"' \
  --limit=20 \
  --format=json \
  --freshness=1h
```

---

## Cloud Run Request Logs

Useful for tracing HTTP errors (4xx, 5xx):

```bash
gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="SERVICE_NAME" AND httpRequest.status>=500' \
  --limit=20 \
  --format=json \
  --freshness=1h
```

For 4xx client errors:

```bash
gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="SERVICE_NAME" AND httpRequest.status>=400 AND httpRequest.status<500' \
  --limit=20 \
  --format=json \
  --freshness=1h
```

---

## Error Reporting

GCP Error Reporting groups similar errors together. Useful for seeing error frequency and affected versions:

```bash
# List error groups
gcloud beta error-reporting events list \
  --service="SERVICE_NAME" \
  --format=json \
  --limit=10
```

---

## Useful Format Options

### Compact table output (for initial overview)

```bash
--format="table(timestamp, severity, textPayload.slice(0:120))"
```

### Full JSON (for stack traces and structured data)

```bash
--format=json
```

### Just the log messages

```bash
--format="value(textPayload)"
```

---

## Filter Syntax Quick Reference

| Operator | Example | Meaning |
|----------|---------|---------|
| `=` | `severity=ERROR` | Exact match |
| `!=` | `severity!=INFO` | Not equal |
| `>=` | `severity>=WARNING` | Greater or equal (for severity: WARNING, ERROR, CRITICAL) |
| `=~` | `textPayload=~"timeout"` | Regex match |
| `!~` | `textPayload!~"health"` | Regex not match |
| `AND` | `severity>=ERROR AND ...` | Both conditions |
| `OR` | `severity=ERROR OR severity=CRITICAL` | Either condition |

### Severity Levels (ascending)

`DEFAULT` < `DEBUG` < `INFO` < `NOTICE` < `WARNING` < `ERROR` < `CRITICAL` < `ALERT` < `EMERGENCY`

---

## Filtering Out Noise

Exclude health checks and common non-issues:

```bash
gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="SERVICE_NAME" AND severity>=ERROR AND textPayload!~"health" AND textPayload!~"readiness"' \
  --limit=20 \
  --format=json \
  --freshness=1h
```

---

## Specific Time Range

Instead of `--freshness`, use explicit timestamps:

```bash
gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="SERVICE_NAME" AND severity>=ERROR AND timestamp>="2024-01-15T10:00:00Z" AND timestamp<="2024-01-15T12:00:00Z"' \
  --limit=50 \
  --format=json
```
