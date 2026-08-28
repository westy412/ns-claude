# Tracing Playbook

> **When to read:** Steps 3 to 5 of every run. These are the commands that find the consumers.

Three rings. Work outward. Record the command you ran for each ring, so an unchecked ring is visible.

---

## Ring 1 — repo-local

Get the changed symbols first:

```bash
BASE=$(git merge-base HEAD @{upstream} 2>/dev/null || echo origin/main)
git diff --name-only $BASE
git diff $BASE -- '*.ts' '*.tsx' '*.py' | grep -E '^[-+].*(export |def |class |function |const )' | sort -u
```

Then find the callers of each symbol:

```bash
rg -n --hidden -g '!node_modules' -g '!.git' '\b<SYMBOL>\b'
rg -n "from ['\"].*<MODULE>" ; rg -n "import .*<MODULE>"
rg -n "['\"]<SYMBOL>['\"]"        # dynamic call, string key, or registry entry
```

Cover these, and say so when one finds nothing:
- Direct callers and re-exports.
- Dynamic references by string: a registry, a router table, a config key, a DI container.
- Type references and generics.
- Tests and fixtures that assert the old behaviour.
- Config keys and constants that name the changed thing.

A rename with a string reference is the most common miss. Always grep the old name as a bare string.

---

## Ring 2 — runtime and data systems

**Database**
```bash
fd -t f -e sql . | rg -i 'migration|schema'
rg -n -i 'create table|alter table|drop column|add column|not null|unique|index'
rg -n '<TABLE_NAME>'              # every reader and writer of the table
```
For a schema change, state the row count risk. A lock on a large table is an outage.

**API contracts**
```bash
rg -n -g '*openapi*' -g '*swagger*' '<PATH>'
rg -n "(get|post|put|patch|delete)\(['\"]<PATH>"
```

**Events, queues, and webhooks**
```bash
rg -n -i 'publish|emit|enqueue|send_message|topic|inngest|pubsub'
rg -n '<TOPIC_OR_EVENT_NAME>'     # find the producer and every consumer
```

**Scheduled jobs**
```bash
rg -n -i 'cron|schedule|scheduler|every\(' 
gcloud scheduler jobs list 2>/dev/null
```

**Environment variables and secrets**
```bash
rg -n 'process\.env\.<VAR>|os\.environ\[.<VAR>|getenv\(.<VAR>'
rg -n '<VAR>' -g '*.yaml' -g '*.yml' -g '*.tf' -g '.env*' -g 'Dockerfile*' -g '.github/**'
gcloud secrets list 2>/dev/null
```
A variable must exist in the code, the deploy config, and the secret store. Check all three.

**Deployed services**
```bash
gcloud run services list --format='value(metadata.name,status.url)' 2>/dev/null
gcloud run services describe <SERVICE> --format=yaml 2>/dev/null | rg -i 'env|secret|image|concurrency|timeout'
```
When `gcloud` is not authenticated, do not stop. Record the gap as an unknown.

---

## Ring 3 — downstream consumers

Discover the consumers each run. Do not keep a cached list.

**Sibling repos** — repos sit under a shared parent, for example `~/Programming/{org}/{repo}`:
```bash
PARENT=$(cd "$(git rev-parse --show-toplevel)/.." && pwd)
fd -t d -d 2 '^\.git$' "$PARENT" -H -x dirname {} \;
rg -n '<SYMBOL_OR_PACKAGE>' "$PARENT" -g '!node_modules' -g '!.git' -l
```

**Organisation code search**
```bash
gh search code '<SYMBOL>' --owner <ORG> --limit 30
gh api /orgs/<ORG>/repos --paginate -q '.[].name'
```

**Published packages** — a consumer pins a version, so it breaks on its next install, not on your push:
```bash
rg -n '"<PACKAGE_NAME>"' "$PARENT" -g 'package.json' -g '!node_modules'
```

**Other consumer classes to check by name:** client apps and front ends, MCP servers, vault sync jobs, admin panels, external webhook callers, and Claude skills that call the changed command.

When every discovery path fails, ask the user one question: which systems consume this surface? Then continue with the answer.

---

## Evidence rules

- A finding cites `path:line`. A claim with no path is an unknown.
- Read the consumer before you call it broken. A grep hit is a lead, not a finding.
- Record the ring you skipped and the reason. An empty Unknowns section on a partial run is a defect.
