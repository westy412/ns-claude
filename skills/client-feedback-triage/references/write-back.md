# Write-Back

> **When to read:** After the user has approved the final bucket set and the triage document is on disk — before building the `apply` payload. Covers what the skill writes, what it never writes, who can see it, the exact comment text, the write set, actor resolution, the allow-lists, and how to read the `apply` result.

---

## The client can read everything you write

`txn/txn-admin-api/src/app/api/deps.py:173-184` grants the `txn_member` role
`can_view_feedback`, `can_comment`, and `can_update_status`. `txn_member` is the
**client's own users**. Every comment this skill writes, and every status a panel
shows, is visible to them.

Two consequences, both hard constraints:

1. **No model-written text ever reaches a comment.** The comment is the template
   below, byte for byte. Rationale, bucket names, transcripts, and debate notes stay
   in the triage document, which the client never sees.
2. **Nothing is written for a record that was not selected.** A client who sees a
   status or a note on unselected feedback reads it as a verdict. "Not this round"
   is not a verdict, so nothing is written to say it.

---

## The comment template

One template. Store it here; do not retype it elsewhere.

```
Triaged YYYY-MM-DD — scheduled
```

- `YYYY-MM-DD` is the machine's local date — the same date as the document
  filename and the payload's `date`.
- The dash is an **em dash, U+2014** (`—`), with one space on each side. Not a hyphen
  (`-`), not an en dash (`–`). The R2 read matches on the prefix `Triaged `; the
  acceptance test compares the whole string byte for byte.
- Example, verbatim: `Triaged 2026-08-17 — scheduled`

The write script builds the string from `date`. The skill body never composes it.

---

## Which records get written — the membership table (R9)

Buckets hold *items*, but writes target *records*. The write script deduplicates the
write set **by record id before the first statement**, so a record appears in it at
most once, however many buckets its items sit in.

| Record's bucket membership | Write |
|---|---|
| In one or more `will do` buckets | **Exactly one** comment plus one audit row, however many buckets it appears in (WE14, WE6b) |
| In a `will do` bucket **and** a `not this round` bucket | **One** comment plus one audit row. Any scheduled work on the record marks the record (WE6a) |
| Only in `not this round` buckets | **Nothing.** No status, no comment, no audit row (WE15) |
| Only unclassified items (EC6) | **Nothing** |

The mixed case marks the whole record even though only part of it was scheduled. That
is why the "already scheduled" exclusion in the read is soft: on the next run the
record is shown, collapsed, still carrying its un-scheduled items, and can be pulled
back into the debate (WE6a).

Send **every** bucket in the payload, `not this round` included. The script is the
single enforcement point: it writes for `will do` membership and ignores the rest.

---

## The two statements per record

Both run inside **one transaction per record**. If the second fails, the first rolls
back and the record is left untouched (EC14).

```
1. INSERT  <schema>.feedback_comments (feedback_id, user_id, content)
             RETURNING id
   -- user_id  = the resolved actor's id (references auth.users(id))
   -- content  = the template above

2. INSERT  <schema>.user_activity_events
           (actor_user_id, action_type, entity_type, entity_id, metadata)
   -- actor_user_id = the resolved actor's user_profiles.id
   -- action_type   = 'comment.created'
   -- entity_type   = 'feedback_comment'
   -- entity_id     = the id RETURNED by statement 1  ← the COMMENT's id,
   --                 not the feedback record's id
   -- metadata      = {"feedback_id": "<the feedback record's id as a string>"}
```

These four values replicate the admin API's own convention at
`txn/txn-admin-api/src/app/api/routers/comments.py:101-108`. `entity_id` = the
comment id is the non-obvious one; get it wrong and the client-visible activity feed
links to nothing.

**`<schema>.feedback` is never written.** No `UPDATE`, no `review_status`, nothing.
The read allow-list is the only place that table appears.

---

## Actor resolution

The actor is the person the comment and the audit row are attributed to.

| Precedence | Source | Used for |
|---|---|---|
| 1 | `--actor-email <address>` on `triage_write.py apply`, if given | resolved against `<schema>.user_profiles.email` |
| 2 | `default_actor_email` in `config.json` (top level) | same |

The payload's `"actor"` is a **display name for the triage document only**. The write
script never reads it and never resolves an actor from it. The skill body takes it
from `default_actor.name` in the `clients` output (`default_actor_name` in
`config.json`). When the user overrides with `--actor-email`, ask for the display
name too, so the document header and the audit row name the same person.

- **EC13** — the resolved email has no `user_profiles` row in the client schema →
  `ACTOR_NOT_FOUND`, exit 6, **before any write**. `user_activity_events.actor_user_id`
  is a foreign key to `user_profiles(id)`. Report the email; the actor needs a
  profile row in that client's schema.
- The script does not separately verify `auth.users`. A missing row there fails the
  comment insert and rolls the record's transaction back (EC14).

---

## Idempotence — same-date skip vs any-date flag

Two predicates, deliberately different (R10, EC24):

| Where | Predicate | Effect |
|---|---|---|
| The read (`list`, R2) | any comment starting `Triaged ` — **any date** | `already_scheduled: true`; shown collapsed, out of the default debate set |
| The write (`apply`, R10) | a comment whose text **equals** the template for the payload's date, exactly | record **skipped**; listed in `skipped` |

So a run interrupted by a failure can be re-run over the same payload safely: what
landed is skipped, what did not is written. And a record pulled back into the debate
and scheduled again on a **later** date gets a second `Triaged <new-date> — scheduled`
comment (EC24). That is correct — it records that the record was picked up again,
which is the only signal that earlier scheduled work never landed.

---

## Partial write (EC15) — asserted, not demonstrated

Write-back is per-record atomic, not batch atomic (Notes K4). If record 6 of 20 fails:

- the script **stops immediately**, exits **5** `PARTIAL_WRITE`, and the envelope
  carries `written: [...]` (records 1–5) and `unwritten: [...]` (6–20);
- records 1–5 keep their comment and audit row; record 6 rolled back; 7–20 untouched;
- the skill body **annotates the document** with both lists and tells the user;
- re-running `apply` over the same payload skips the 5 already written and continues.

This path is asserted here rather than demonstrated live (Notes K10, Drift 7): TXN
has no separate testing database. It is contained by three things that are tested —
per-record transactions (EC14), the deduplicated write set (R9), and the same-date
skip (R10).

---

## The two allow-lists (R14, EC16, EC17)

Every statement is checked against a hard-coded allow-list of fully-qualified table
names for its connection **before execution**. Not a regex over SQL.

| Connection | Read allow-list | Write allow-list |
|---|---|---|
| Admin | `<schema>.feedback`, `<schema>.feedback_comments`, `<schema>.user_activity_events`, `<schema>.user_profiles` | `<schema>.feedback_comments`, `<schema>.user_activity_events` |
| Agent | `public.conversations`, `public.messages` | *(empty — read-only)* |

- **EC16** — a statement targeting any other table → `SCHEMA_VIOLATION`, exit 6,
  refused before execution. Nothing runs.
- **EC17** — the rule is **client-schema-relative**, not a blanket ban on `public`.
  inPlay's own schema *is* `public` (`inPlay/inplay-admin-api/supabase/schema.sql:30`
  creates `feedback` unqualified), so a run for `inPlay` reads and writes
  `public.feedback_comments` under inPlay credentials and is **permitted**. The danger
  guarded against is a TXN connection reaching inPlay's `public` on the shared
  project — not inPlay using its own schema.
- The admin connection also sets `search_path` to the resolved schema. Both, not
  either: the `search_path` catches anything that slips through; the qualification is
  what the check inspects.
- No migrations, ever. Never run Alembic against the shared project.

---

## Why no status is written at all

`In Progress` means work has actively started. Triage does not start work.

`Dismissed` means rejected. Most unselected feedback is not rejected — it is simply
not this round. Writing `Dismissed` would tell the client something untrue, in a
panel they can read.

The cost is accepted: **the queue never shrinks.** Every run re-reads every open
record. The `Triaged … — scheduled` comment on selected records is the only mechanism
separating "already picked up" from "never seen". Records left alone are re-presented
every run, which is intended — they are still open feedback.

---

## The payload the body sends to `apply`

Built after approval, after the document is on disk. Piped to
`scripts/triage_write.py apply <client>` on stdin. Exactly this shape:

```json
{
  "date": "2026-08-17",
  "actor": "George Westbrook",
  "buckets": [
    { "name": "agent invents order numbers", "decision": "will do",
      "rationale": "…", "target": "agent", "record_ids": ["uuid", "uuid"] },
    { "name": "cosmetic spacing nits", "decision": "not this round",
      "rationale": "…", "target": "frontend", "record_ids": ["uuid"] }
  ]
}
```

| Field | Value |
|---|---|
| `date` | machine local date, `YYYY-MM-DD` — same as the document filename |
| `actor` | display name (document only) — `default_actor.name`, or the name asked for on override |
| `buckets[].name` | unique within the run |
| `buckets[].decision` | `will do` or `not this round` — nothing else |
| `buckets[].rationale` | the bucket's rationale as approved |
| `buckets[].target` | `agent`, `frontend`, or `both` |
| `buckets[].record_ids` | member record ids (may repeat across buckets; the script deduplicates) |

Flags: `--actor-email <address>` overrides the registry actor; `--dry-run` prints
every statement it would issue and issues nothing.

**On success** (exit 0): `{ "ok": true, "written": [...], "skipped": [...],
"comment_ids": { "<feedback_id>": "<comment_id>" } }`. Annotate the document with
`written` and `skipped`.

**On failure**: the envelope `{ "ok": false, "error", "message", "written", "unwritten" }`.
Exit 5 → annotate with `written` / `unwritten` (EC15). Exit 6 `ACTOR_NOT_FOUND` /
`SCHEMA_VIOLATION` / `MALFORMED_PAYLOAD` → nothing was written; report and stop.
