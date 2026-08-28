# Breaking Change Catalogue

> **When to read:** Step 6 of every run. Check each changed surface against the patterns for its type.

Each row holds a pattern, the failure it causes, and the check that proves the failure. A pattern match is a lead. The check turns the lead into a finding.

---

## Database schema

| Pattern | The failure | The check |
|---------|-------------|-----------|
| Drop or rename a column | Old code reads a column that no longer exists. Every request that touches it fails during the deploy window. | Grep the column name across every repo. Confirm no running version reads it. |
| Add a `NOT NULL` column with no default | The migration fails on a table with rows, or existing writes fail. | Check the row count. Confirm a default exists, or the write path sets the value. |
| Add an index on a large table | The migration locks the table. Requests time out. | Check the row count and the engine. Postgres needs `CREATE INDEX CONCURRENTLY`. |
| Remove or rename an enum value | Rows hold the old value. Reads fail on parse. | Query the distinct values in the column before you drop one. |
| Change a column type | The cast fails, or the value truncates in silence. | Check the widest existing value. |
| Add a unique constraint | Duplicate rows already exist. The migration fails midway. | Count the duplicates first. |
| Migrate and deploy in the wrong order | The new code meets the old schema, or the old code meets the new schema. | State the required order. An additive change deploys the schema first. A destructive change deploys the code first. |
| A migration with no down path | A rollback is impossible. | Confirm a reverse migration exists, or mark the change irreversible. |

## API contract

| Pattern | The failure | The check |
|---------|-------------|-----------|
| Remove or rename a response field | The client reads `undefined`. It fails now or later, and often in silence. | Grep the field name in every client repo. |
| Add a required request field | Every existing caller fails validation. | Confirm the field is optional, or confirm every caller sends it. |
| Tighten validation | Traffic that worked yesterday now returns a 4xx. | Check the real inputs in the logs, not the test fixtures. |
| Change the error shape or the status code | Client error handling stops matching. Retries change behaviour. | Grep the client for the status code and the error key. |
| Change a default value | Callers that omit the field get new behaviour and no warning. | List the callers that omit the field. |
| Change pagination or ordering | The client pages through the wrong rows. | Check every caller that reads a list. |
| Change a path with no version | Old clients get a 404. | Confirm the old path still answers, or confirm no old client exists. |

## Events, queues, and webhooks

| Pattern | The failure | The check |
|---------|-------------|-----------|
| Change a payload shape | Messages already in the queue carry the old shape. The consumer fails on them. | Confirm the consumer reads both shapes, or confirm the queue is empty. |
| Deploy the producer before the consumer | The consumer receives a shape it cannot read. | State the deploy order. The consumer goes first. |
| Rename a topic or an event | The producer publishes into the void. No error appears. | Grep the old topic name across every repo. |
| Change retry or idempotency behaviour | A handler runs twice and doubles the effect. | Confirm the handler is idempotent for the new path. |
| Add work to a hot handler | The handler runs slower, the queue backs up, and the lag grows. | Check the message rate against the new runtime. |

## Environment, secrets, and flags

| Pattern | The failure | The check |
|---------|-------------|-----------|
| Rename a variable | The service fails at start time in every environment that holds the old name. | Check the code, the deploy config, the CI config, and the secret store. |
| Add a required variable | The deploy succeeds locally and fails in production. | Confirm the value exists in every environment. |
| Change a flag default | Every user gets the new path at once. | Confirm the rollout is staged. |
| Rotate a secret | Any service that holds the old value fails. | List every consumer of the secret. |

## Auth, permission, and tenancy

| Pattern | The failure | The check |
|---------|-------------|-----------|
| Widen a rule | Data leaks across users or tenants. This scores Critical. | Test as a user who must not see the data. |
| Tighten a rule | Real users lose access. | Test as a user who must keep the access. |
| Change a tenant filter | One tenant reads another tenant's rows. | Read every query on the changed path for the tenant clause. |
| Change a token, a session, or a claim | Live sessions break. Users log out at once. | Confirm the old token still validates during the deploy. |

## Data write paths

| Pattern | The failure | The check |
|---------|-------------|-----------|
| An `UPDATE` or a `DELETE` with no tight `WHERE` clause | The statement rewrites the whole table. | Read the clause. Run a `SELECT COUNT(*)` with the same clause first. |
| A backfill with no batch and no resume | The script times out midway and leaves partial data. | Confirm the script batches and can resume. |
| A one-off script with no dry run | A mistake is unrecoverable. | Confirm a dry-run mode and a backup exist. |

## Deploy, infrastructure, and dependencies

| Pattern | The failure | The check |
|---------|-------------|-----------|
| Change a timeout, memory, or concurrency setting | Requests fail under load and pass in a test. | Compare the new limit against the real peak. |
| Change a health check | The deploy never turns healthy, or it turns healthy too early. | Confirm the path and the start period. |
| Change the minimum instance count to zero | Cold starts add seconds to the first request. | Confirm the caller tolerates the latency. |
| A major version bump | A default changed, or an API was removed. | Read the changelog between the two versions. |
| A lockfile change with no explicit intent | A transitive package changed under you. | Diff the lockfile for packages you did not name. |
