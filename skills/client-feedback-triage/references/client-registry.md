# Client Registry

> **When to read:** When a client is listed as "not yet configured", when a new client must be added, or when a credential file cannot be found. Covers every key in `config.json`, the two credential formats, tilde expansion, and the failure each missing piece produces.

The registry is `config.json` at the root of the skill directory. `scripts/triage_read.py clients`
is the only reader the skill body needs — it parses the registry, opens no
connection, and returns one row per client with `configured` and `agent_database`
flags. Everything else in this file is for the person who edits the registry.

---

## The shape

```json
{
  "default_actor_email": "george.westbrook412@gmail.com",
  "default_actor_name": "George Westbrook",
  "clients": {
    "txn": {
      "root": "~/Programming/txn",
      "schema": "txn",
      "admin_credentials": {
        "path": "~/Programming/txn/txn-admin-api/infrastructure/terraform.production.tfvars",
        "format": "hcl-env-vars"
      },
      "agent_database": {
        "path": "~/Programming/txn/txn-agentic-agent/.env",
        "format": "dotenv",
        "tenant_id": null
      }
    },
    "caterer": {
      "root": "~/Programming/caterer",
      "schema": "caterer",
      "admin_credentials": { "path": null, "format": "hcl-env-vars" },
      "agent_database": null
    }
  }
}
```

| Key | Meaning |
|---|---|
| `default_actor_email` | The email `triage_write.py` resolves against `<schema>.user_profiles.email` when `--actor-email` is not given. The actor must have a profile row in every client schema it writes to (EC13) |
| `default_actor_name` | The display name the skill body writes into the triage document header and the payload's `actor`. Document only — the write script never reads it |
| `clients.<key>` | The registry key. Matched **case-insensitively against the exact key**; no prefix match (`TXN` → `txn`; `totaljobs` does not match `total-jobs`) |
| `root` | The client root on this machine. The triage document goes to `<root>/feedback/`; discovery folders to `<root>/specs/`. If `<root>` is absent the document write fails and the session aborts before any database statement (EC22) |
| `schema` | The client's Postgres schema on the admin database. Every admin statement is qualified with it and the allow-list is built from it |
| `admin_credentials.path` | The credential file for the admin database. `null` = **not yet configured** (EC11) |
| `admin_credentials.format` | `hcl-env-vars` or `dotenv` |
| `agent_database` | `null` when the client has no agent database (EC8). Otherwise `{ path, format, tenant_id }` |
| `agent_database.tenant_id` | The value for the kernel's `tenant_id` predicate on `conversations`, or `null` to skip it. TXN sets `null` |

All paths use `~`. The loader expands it (`Path.expanduser()`); write `~`, not an
absolute home path, so the registry is byte-identical across trees and machines.

---

## The two credential formats — same five keys

Both formats expose the **same five keys**: `DATABASE_HOST`, `DATABASE_PORT`,
`DATABASE_NAME`, `DATABASE_USERNAME`, `DATABASE_PASSWORD`. Only the syntax differs.

| Format | Syntax | Example source |
|---|---|---|
| `hcl-env-vars` | Terraform tfvars. The five keys sit **inside** an `env_vars = { … }` map, as `KEY = "value"` | `txn-admin-api/infrastructure/terraform.production.tfvars` |
| `dotenv` | Flat `KEY=value` lines, one per line | `txn-agentic-agent/.env` |

`hcl-env-vars`:

```hcl
env_vars = {
  DATABASE_HOST     = "…"
  DATABASE_PORT     = "…"
  DATABASE_NAME     = "…"
  DATABASE_USERNAME = "…"
  DATABASE_PASSWORD = "…"
}
```

`dotenv`:

```dotenv
DATABASE_HOST=…
DATABASE_PORT=…
DATABASE_NAME=…
DATABASE_USERNAME=…
DATABASE_PASSWORD=…
```

A `format` value outside these two is a configuration error
(`CLIENT_NOT_CONFIGURED`, exit 2). Credentials live only in these local, gitignored
files; there is no secret-manager fallback (Notes K6). A machine without the files
cannot run the skill for that client.

---

## What each missing piece produces

| Condition | Result | Test |
|---|---|---|
| `admin_credentials.path` is `null` | Listed as **"not yet configured"**; cannot be selected. `CLIENT_NOT_CONFIGURED`, exit 2, naming the key. Never fall back to another client's credentials | EC11 |
| `admin_credentials.path` names a file that does not exist | `CREDENTIALS_MISSING`, exit 2, naming the missing path — **before any connection** | EC12 |
| `agent_database` is `null` and the queue carries Lane A items | No agent connection is attempted. Lane A items are presented without transcripts and the user is warned that the registry entry is incomplete. `transcript` refuses the client with `CLIENT_NOT_CONFIGURED` if called | EC8 |
| The argument matches no key | `UNKNOWN_CLIENT`, exit 2, with `known_clients` in the envelope; the skill lists and asks | WE4 |
| `<root>` does not exist | The document write fails; the session aborts before any database statement | EC22 |

`null` path and missing file are **different** failures on purpose: the first says
"nobody has configured this client yet"; the second says "this machine is missing a
file the registry expects".

---

## Adding a client

New client admin pairs are instantiated from `novosapien/admin-api-template` and
`novosapien/admin-panel-template`, so every client carries the same `feedback`,
`feedback_comments`, `user_activity_events`, and `user_profiles` tables in its own
schema and fits this registry without change.

1. Add `clients.<key>` with `root`, `schema`, `admin_credentials`, and
   `agent_database` (`null` if the client has no agent).
2. Point `admin_credentials.path` at the client's admin-api tfvars (or a dotenv file)
   and set `format` to match.
3. If the client has an agent database, point `agent_database.path` at its `.env`,
   set `format`, and set `tenant_id` (or `null`).
4. Make sure the actor (`default_actor_email`) has a `user_profiles` row in the
   client's schema, or every write will fail with `ACTOR_NOT_FOUND` (EC13).
5. Run `scripts/triage_read.py clients` and check the row shows `configured: true`.
6. The change is base content: make it in **both** trees (`~/.claude/skills/…` and
   `~/.codex/skills/…`) so `config.json` stays byte-identical.

**inPlay's schema is `public` (EC17).** `inPlay/inplay-admin-api/supabase/schema.sql:30`
creates `feedback` unqualified, so its registry entry says `"schema": "public"`. That
is correct and permitted: the allow-list is client-schema-relative, and inPlay's
connection reaches only inPlay's own `public`. TXN and inPlay share one Supabase
project — TXN in schema `txn`, inPlay in `public` — which is exactly why the rule is
"the resolved client's schema" and not "never `public`".

Today only `txn` is populated. `inPlay` (schema `public`), `caterer` (schema
`caterer`), and `total-jobs` (schema `totaljobs`) carry `null` credential paths and
are listed as "not yet configured" until filled.
