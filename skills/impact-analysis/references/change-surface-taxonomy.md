# Change Surface Taxonomy

> **When to read:** Step 2 of every run. Classify each changed element before you trace it.

A surface is the part of a change that other code can see. The surface type decides how far the change travels and how bad a break gets. Classify first. Trace second.

One changed file can hold two surfaces. A route handler that also writes a new column holds an API surface and a schema surface. Record both.

---

## The types

| # | Surface | How to spot it in the diff | Reaches | Severity floor |
|---|---------|---------------------------|---------|----------------|
| 1 | Internal function or private helper | Not exported. No consumer outside the module. | Ring 1 | Low |
| 2 | Exported module API | An `export`, a `__init__.py` entry, a package index, or an `index.ts` | Rings 1 and 3 | Medium |
| 3 | HTTP endpoint contract | A route file, a controller, an OpenAPI file, a request or response type | Rings 1 to 3 | High |
| 4 | Database schema | A migration file, a DDL statement, a model or an ORM class | Rings 1 to 3 | High |
| 5 | Data write path or backfill | An `UPDATE`, an `INSERT`, a delete, a one-off script | Rings 1 and 2 | High |
| 6 | Event, queue, or webhook payload | A publish call, a topic name, a payload type, a webhook handler | Rings 2 and 3 | High |
| 7 | Environment variable, secret, or flag | `process.env`, `os.environ`, a `.env.example`, a Secret Manager key | Rings 2 and 3 | High |
| 8 | Auth, permission, or tenancy rule | A guard, a middleware, a policy, a row-level security rule, a role check | Rings 1 to 3 | Critical |
| 9 | Scheduled job or worker | A cron expression, a scheduler config, a queue consumer | Ring 2 | Medium |
| 10 | Deploy and infrastructure config | A Dockerfile, a Cloud Run config, Terraform, a CI workflow | Ring 2 | High |
| 11 | Shared package or template | A versioned package, a template repo, a generator | Ring 3 | High |
| 12 | Third-party dependency | A lockfile, a version bump, a new SDK client | Rings 1 and 2 | Medium |

The severity floor is a minimum, not a verdict. A finding can score higher. It must not score lower.

---

## What each type means for the trace

**1. Internal function.** Trace the callers inside the repo. Stop at ring 1 once you prove nothing exports it. Check for a dynamic call by string first.

**2. Exported module API.** Ring 1 finds the local callers. Ring 3 finds the other repos. A rename, a signature change, or a removed export breaks every consumer at once.

**3. HTTP endpoint.** Check four things: the path, the request shape, the response shape, and the status and error shapes. A client reads all four. An added required field breaks every existing caller.

**4. Database schema.** Check the deploy order first. The old code and the new schema run together during a deploy. Both must work. See the catalogue.

**5. Data write path.** Ask one question: can this lose data or corrupt it? A write path with no dry run and no backup scores Critical.

**6. Event or queue payload.** Producers and consumers deploy at different times. Messages already in the queue carry the old shape. A consumer must read both shapes.

**7. Environment variable or secret.** A renamed variable fails at start time in every environment that still holds the old name. Check the deploy config, the CI config, and the secret store, not only the code.

**8. Auth or permission rule.** Two failures, and both are Critical. A rule that is too loose exposes data. A rule that is too tight locks users out. Test both directions.

**9. Scheduled job.** Check the schedule, the runtime, and the overlap. A job that now runs longer than its interval will overlap with itself.

**10. Deploy config.** A change here affects every request, not one code path. Check the health check, the memory limit, the timeout, the concurrency, and the minimum instance count.

**11. Shared package or template.** The consumers do not update when you push. Check the version policy. A major bump needs a migration note for each consumer.

**12. Third-party dependency.** Read the changelog between the two versions. A patch bump can still change a default.
