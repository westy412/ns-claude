---
description: Investigate production errors on GCP Cloud Run services. Discovers deployed services, retrieves error logs via gcloud CLI, traces errors to source code, and presents diagnosis with a potential fix. Does NOT write code until the user validates the diagnosis.
disable-model-invocation: true
argument-hint: "[service-name]"
allowed-tools: Bash, Read, Grep, Glob, AskUserQuestion
---

> **Invoke with:** `/prod-error` or `/prod-error my-service-name` | **Keywords:** production error, cloud run, gcloud logs, debug

Investigate production errors on GCP Cloud Run. Finds the error, traces it to code, and presents a fix — but writes nothing until you say so.

**Input:** Optional service name as argument (skips service selection)
**Output:** Text diagnosis with root cause, affected code, and proposed fix

## First-Time Setup

If this is the first run, load and follow [setup.md](references/setup.md) to configure the service account.

The setup is complete when:
- `~/.config/gcloud/service-accounts/` contains a key JSON file
- `gcloud auth activate-service-account` succeeds with that key

## Reference Files

| Topic | Reference File | When to Load |
|-------|---------------|--------------|
| First-time setup | [setup.md](references/setup.md) | On first run or when auth fails |
| Log query syntax | [gcloud-log-queries.md](references/gcloud-log-queries.md) | When building log filter queries |

## Key Principles

1. **Read-only until validated** — No Edit or Write tools. Present findings as text only.
2. **Pre-flight before everything** — Always verify auth and project before querying.
3. **Show, don't assume** — Present the error, the code, and the proposed fix. Let the user decide.
4. **Minimal log window** — Start with the last 1 hour of errors. Widen only if needed.
5. **Trace to code** — An error log is only useful when paired with the exact file and line that caused it.

## Procedure

### Step 0: Pre-Flight Check — Always Activate Service Account

**Always activate the service account**, regardless of what's currently active. User accounts may have expired tokens that fail silently.

```bash
# Find the key file
ls ~/.config/gcloud/service-accounts/*.json 2>/dev/null
```

If no key file exists, load [setup.md](references/setup.md) and guide the user through setup. Stop here until setup is complete.

If a key file exists, activate it:

```bash
gcloud auth activate-service-account --key-file=~/.config/gcloud/service-accounts/<KEY_FILE>.json
```

Then verify the active project:

```bash
gcloud config get-value project 2>/dev/null
```

If no project is set, ask the user which project to use and set it:

```bash
gcloud config set project PROJECT_ID
```

### Step 1: Service Discovery

If `$ARGUMENTS` was provided, use that as the service name and skip to Step 2.

Otherwise, use the `AskUserQuestion` tool to present the known services as numbered options. The user selects which service to investigate.

Services to present as options:

**Content Workforce:**
1. `ns-content-workforce-agents` (europe-west2)
2. `ns-content-workforce-api` (europe-west2)
3. `ns-content-workforce-app` (europe-west2)
4. `ns-content-workforce-idea-agents` (europe-west2)
5. `ns-content-workforce-nova-agent` (europe-west2)
6. `ns-content-workforce-renderer` (europe-west2)

**Cold Outreach:**
7. `ns-cold-outreach-api` (europe-west1)
8. `ns-cold-outreach-app` (europe-west1)
9. `ns-cold-outreach-workforce` (europe-west1)

Present these as `AskUserQuestion` options with each service name as the label and region as the description. Include an "Other" option automatically (provided by the tool) so the user can specify a service not in this list — in that case, fall back to `gcloud run services list` to discover it.

### Step 2: Retrieve Error Logs

Load [gcloud-log-queries.md](references/gcloud-log-queries.md) for query syntax.

**IMPORTANT: Do NOT filter by `severity>=ERROR`.** Many errors in our services are not tagged with ERROR severity — they appear as INFO-level text logs containing error messages, or as HTTP 4xx/5xx responses. Always search broadly and filter client-side.

**Phase 1: Check HTTP error responses (4xx/5xx)**

Start with the last 1 hour:

```bash
gcloud logging read "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"SERVICE_NAME\" AND httpRequest.status>=400" --limit=50 --format=json --freshness=1h 2>/dev/null
```

**Phase 2: Search log text for error patterns**

Search all text logs for error indicators:

```bash
gcloud logging read "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"SERVICE_NAME\"" --limit=500 --format=json --freshness=1h 2>/dev/null | jq -r '.[] | select(.textPayload) | select(.textPayload | test("(?i)(error|exception|traceback|failed|failure|fatal)")) | "\(.timestamp) | \(.textPayload)"'
```

**Phase 3: Widen if needed**

If no errors found in the last hour, widen both queries to 24 hours (`--freshness=24h`). If still nothing, tell the user and ask if they want to check a different time window.

Present a summary of errors found:
- How many errors
- Distinct error types/messages
- Time range of occurrence

If multiple distinct errors exist, ask the user which one to investigate.

### Step 3: Codebase Analysis

Take the selected error (message + stack trace) and trace it to the source code:

1. **Extract identifiers** — Pull file paths, function names, class names, error messages from the log entry
2. **Search the codebase** — Use Grep and Glob to find the relevant source files
3. **Read the code** — Read the files around the error location to understand the context
4. **Identify root cause** — Determine what condition or input caused the error

### Step 4: Present Diagnosis

Present the findings as a structured text report. Use this format:

```
## Production Error Diagnosis

**Service:** [service name]
**Error:** [error message]
**When:** [timestamp or time range]
**Frequency:** [how many times it occurred in the log window]

### Stack Trace
[Relevant portions of the stack trace]

### Root Cause
**File:** [file path]:[line number]
**Function:** [function/method name]

[2-3 sentence explanation of what's causing the error]

### Proposed Fix
[Plain text description of what needs to change and why.
Be specific about which file, which function, and what the change should be.
Do NOT write the actual code yet.]

### Risk Assessment
- **Impact:** [What's affected by this error in production]
- **Fix complexity:** [Simple / Moderate / Complex]
- **Side effects:** [Any potential side effects of the proposed fix]
```

### Step 5: Validation Gate

After presenting the diagnosis, ask the user:

**"Does this diagnosis look correct? Should I implement the proposed fix?"**

- If **YES** — Inform the user that the `allowed-tools` restriction on this skill prevents writing code directly. Tell them to apply the fix in their normal workflow based on the diagnosis above, or start a new conversation to implement it.
- If **NO** — Ask what looks wrong. Re-examine the logs or code based on their feedback. Return to Step 3 or Step 2 as needed.
- If **PARTIALLY** — Ask which parts are correct and which need revision. Iterate on the diagnosis.

## Edge Cases

- **No errors found:** Report that no errors were found in the time window. Suggest checking warnings or widening the window.
- **Error in a dependency (not our code):** Note that the error originates from a third-party library. Trace to where our code calls it and suggest the fix at the call site.
- **Multiple services involved:** If the error spans services (e.g., service A calling service B), note both and investigate the originating service.
- **Auth failure during pre-flight:** Load setup.md and walk through configuration.
