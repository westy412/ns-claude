# Rewrite Examples

> **When to load:** You are unsure how a rule looks in practice. Load this file before the rule lists. Worked examples teach the standard faster than rule statements.

Each pair shows one breach and one fix. The fix keeps every fact from the original. No pair drops a caveat, a path, or a flag.

---

## Sentence Length

**Before (41 words, 3 ideas)**
> The migration script reads the config file and then connects to the primary database, and if the connection fails it retries three times before falling back to the read replica, which can cause stale data to appear in the response.

**After**
> The migration script reads the config file. The script then connects to the primary database. If the connection fails, the script retries three times. After three failures, the script falls back to the read replica. The read replica can return stale data.

The fix splits one sentence into five. Each sentence carries one idea. The retry count and the stale-data risk both survive.

---

## Two Instructions in One Sentence

**Before**
> Run `npm install` and then update the `.env` file with your API key before starting the dev server.

**After**
> 1. Run `npm install`.
> 2. Add your API key to the `.env` file.
> 3. Start the dev server.

Three instructions become three numbered steps. The order matches the order the user must follow.

---

## Passive Voice

| Before | After |
|--------|-------|
| The file is written by the handler. | The handler writes the file. |
| An error is thrown when the token expires. | The client throws an error when the token expires. |
| The cache was invalidated during deploy. | The deploy script invalidated the cache. |
| Requests are rate-limited at 100 per minute. | The gateway rate-limits requests at 100 per minute. |

Each fix names the actor. Passive voice hides the actor. A hidden actor costs the reader a guess.

---

## `-ing` Verb Forms

| Before | After |
|--------|-------|
| Installing the package updates the lockfile. | The install command updates the lockfile. |
| Consider adding a retry. | Add a retry. |
| The service is currently failing on cold start. | The service fails on cold start. |
| Before running the migration, back up the database. | Back up the database. Then run the migration. |

Keep `-ing` when the word is a technical name: "streaming response", "logging level", "the polling interval".

---

## Term Drift

**Before**
> The handler validates the payload. The callback then writes to the queue. If the listener fails, the function retries.

The paragraph names one thing four ways. The reader cannot tell if there are four components or one.

**After**
> The handler validates the payload. The handler then writes to the queue. If the handler fails, the handler retries.

Term drift is the most common breach. It is also the most damaging, because it invents components that do not exist.

---

## Bare Referents

**Before**
> The build agent pulls the image from the registry. The registry enforces a rate limit. A cold cache adds about 40 seconds. This is why the pipeline times out.

"This" could point at the rate limit, the cold cache, or both.

**After**
> The build agent pulls the image from the registry. The registry enforces a rate limit. A cold cache adds about 40 seconds. The rate limit and the cold cache together cause the pipeline timeout.

---

## Noun Clusters

| Before | After |
|--------|-------|
| the build agent log configuration file | the config file for the build agent log |
| the user session token refresh handler | the handler that refreshes the session token |
| production database backup retention policy | the retention policy for production database backups |

---

## Stacked Helping Verbs

| Before | After |
|--------|-------|
| This would potentially be able to fail. | This can fail. |
| You might want to consider checking the logs. | Check the logs. |
| It should probably be possible to cache the result. | You can cache the result. |

Do not delete real uncertainty. If the outcome is genuinely unknown, write "this can fail" or "I have not tested this path".

---

## Jargon and Idiom

| Before | After |
|--------|-------|
| We need to circle back on the auth story. | We must decide the auth approach. |
| This is a bit of a rabbit hole. | This path needs more research than the task allows. |
| Let's leverage the existing pipeline. | Use the existing pipeline. |
| The fix is low-hanging fruit. | The fix takes about 10 minutes. |

---

## Full Paragraph Rewrite

**Before (78 words)**
> So basically what's happening here is that the auth middleware is being called before the session is hydrated, which means that when the downstream handler tries to read `req.user` it's getting undefined, and this cascades into the 500 you're seeing. It would probably be worth considering moving the middleware registration after the session setup, though obviously that might have knock-on effects for the routes that don't need sessions at all.

**After (61 words)**
> The auth middleware runs before the session loads. The downstream handler then reads `req.user` and gets `undefined`. The undefined value causes the 500 error.
>
> To fix the error, register the auth middleware after the session setup in `app.ts`.
>
> **Caveat:** routes that do not use sessions will also wait for the session setup. Check `/health` and `/metrics` before you ship the change.

The rewrite keeps `req.user`, `undefined`, `app.ts`, `/health`, and `/metrics` exactly as written. It keeps the caveat and makes it more specific.

---

## Correct Non-Application

The standard must not touch persuasive copy. This landing page line is correct as written:

> Ship faster. Break less. Your engineers get their afternoons back.

Three fragments, no articles, deliberate rhythm. The standard would flatten the line and destroy its purpose. Leave it alone.
