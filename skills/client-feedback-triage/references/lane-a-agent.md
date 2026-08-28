# Lane A — Agent Feedback

> **When to read:** When the `list` result contains `agent-message` or `conversation` items. Covers grouping by conversation, the transcript fetch and its degradations, category bucketing, and the shared "unthreaded" bucket. The record and item shapes are in `data-model.md`; the document layout is in `templates/triage-doc.md`.

Lane A holds the two item types raised from the console chat: `agent-message` (one
reply, with a `category`) and `conversation` (the thread as a whole). The unit of
triage is the **conversation**: five records about one conversation are one problem.
Only TXN carries Lane A today.

---

## Group by conversation

Use the script-derived `conversation_keys` on each `list` record. Do not re-derive
the key from `app_state` or the items — the rule lives in the script and mirrors the
panel's `conversationKey()` (see `data-model.md` → "Conversation key resolution").

| `conversation_keys` | Where the record's Lane A items go |
|---|---|
| `["<uuid>"]` | The conversation group for that id |
| `["<uuid-1>", "<uuid-2>"]` | **Both** groups. The record joins every conversation its items name, split by item — it is not forced into one (EC23) |
| `[]` with at least one Lane A item | The shared **"unthreaded"** group (EC2) |

**Split by item (WE6, EC23).** A record is not the unit here; its items are. Put each
`agent-message` or `conversation` item under the conversation its own
`conversation_id` names when there is no `app_state.conversation_id`. The record's
Lane B items, if any, go to Lane B. One record can therefore appear in several
places in the document, each time with only the items that belong there.

**The "unthreaded" bucket (EC2).** All records with no conversation key anywhere
share **one** group named "unthreaded". Present it as one section, and give every
record inside it its own line and its own decision. Never merge an unthreaded record
into a real conversation on a guess — the panel's `feedback-rows.ts:27-28` says the
same: a row with neither key threads nowhere. The "unthreaded" group is proposed as a
bucket like any other, so its records can be scheduled; the user may split it.

Present each conversation group as: the conversation id, the member record ids in
`created_at` order, and for each record its Lane A items — `number`, category
`label (slug)` for `agent-message`, the `message_id`, and the comment. An
`agent-message` with `comment: ""` is shown as `(no comment)` and kept: the console's
text field is optional, and the `category` still carries the reporter's meaning (EC7).

---

## Fetch the transcript

**Gate: the registry, then the data.** Call `transcript` only when the resolved
client shows `agent_database: true` in the `clients` output **and** at least one
record in the queue carries a Lane A item. No Lane A item anywhere → no `transcript`
call at all, even for a client with an agent database. A client with
`agent_database: null` never opens an agent connection, even when its records carry
Lane A items. In that case present the Lane A items without transcripts and warn the
user that the client's registry entry is incomplete (EC8). Do not call `transcript`
for such a client — the script refuses with `CLIENT_NOT_CONFIGURED`.

Run `scripts/triage_read.py transcript <client> <conversation_id>` once per distinct
id across all `conversation_keys`. The "unthreaded" group has no id and no transcript.

| Result | What to do |
|---|---|
| `ok: true, found: true` | Read the messages. Show the thread, or the part around the flagged reply, when presenting the group |
| `ok: true, found: false` | Mark the group **"transcript not found"** and triage on the comments alone (EC5). The id is real but no `conversations` row matches; say so, do not guess at a thread |
| `truncated: true` | The most recent 200 messages, in `created_at` ascending order. State that `total_messages − 200` earlier messages were omitted, e.g. "112 earlier messages omitted" for 312 (EC20) |
| exit 4 `AGENT_DB_UNREACHABLE` | The agent database is unreachable or timed out. Stop further `transcript` calls this session, mark **every** conversation group "transcript unavailable", put the transcript-unavailable banner in the document, and continue Lane A on the comments alone. Lane B is unaffected. The session completes (EC4) |
| exit 6 `MALFORMED_PAYLOAD` | The id passed is not a UUID. If the body mistyped it, fix and re-run. If the value came from a Lane A item's stored `conversation_id`, report it as a **malformed stored id** and triage that group on the comments alone, like EC5 — the script refused it before any statement |

**Reading a transcript.** Each message carries `id`, `role`, `content`, `content_blocks`,
`tool_calls`, and `created_at`. Read `content_blocks` as well as `content` — a
structured assistant turn can carry its payload there and show an empty `content`.
`tool_calls` shows what the agent invoked. Anchor an `agent-message` item to the
reply whose `messages.id` equals the item's `message_id`; quote that reply and the
user turn before it. For a `conversation` item, read the thread as a whole.

Transcript text is evidence for the debate and for the document. It is never written
to the client database.

---

## Bucket by category, then by problem

Every `agent-message` carries one of six reporter-picked slugs (`data-model.md` →
"The six category slugs"). Start the proposal from them, then merge across
conversations where the underlying failure is the same.

| Slug | What it usually points at | Default target |
|---|---|---|
| `wrong-answer` | The reply's substance is wrong | `agent` |
| `made-up` | The reply invented a fact, id, or number | `agent` |
| `incomplete` | The reply stopped short or missed part of the ask | `agent` |
| `ignored-data` | The reply ignored data the user supplied or the tools returned | `agent` |
| `tone-format` | Tone, structure, or rendering of the reply | `agent` — but often `frontend` (rendering, markdown, streaming display) |
| `too-slow` | Latency | `agent` — but often `frontend` (streaming, perceived latency) or `both` |

**Rules for the proposal:**

- One conversation with several records is **one** bucket candidate, debated as one
  item (WE8). Its member record ids are every record in the group.
- Two conversations that show the same failure — say, the agent invents order
  numbers in both — may be **one** bucket spanning both. Name the bucket after the
  problem, not the conversation. Member record ids are the union; the handoff block
  lists every conversation id.
- The category is a starting point, not a verdict. It is exactly as reliable as the
  person who filed it. Read the transcript before trusting the slug.
- The default `target` for a Lane A bucket is `agent`. It is a prior, not a
  constraint: a `too-slow` or `tone-format` complaint is often a frontend streaming
  or rendering defect. Set `frontend` or `both` when the transcript says so, and say
  why in the rationale.
- Bucket names are unique within the run. The document and the handoff blocks refer
  to them by name.
- A `conversation` item carries no category. Bucket it by what the comment says and
  what the transcript shows.

**Five fields on every bucket:** `name`, `decision` (`will do` / `not this round`),
`rationale`, member record ids, `target` (`agent` / `frontend` / `both`).

---

## What Lane A does not do

- It does not follow `feedback.submitted_by` → `conversations.user_id` to find a
  submitter's other threads. That route can only produce *candidate* threads, and a
  guessed transcript is worse than the "unthreaded" group's honest silence. The
  per-record briefing still prints, in its conversation pointer line, that
  `feedback.submitted_by` string-equals `conversations.user_id`, because the panel
  format does — that line is true and useful to a human reader.
- It does not label an unknown item type as Lane A. An item whose `type` is not one of
  the six is unclassified — printed verbatim, discussable, not bucketable, no write
  (EC6).
- It does not write anything to the agent database. The agent connection is read-only.

---

## Checklist before the proposal

- [ ] Every record with a Lane A item appears in a conversation group or in
      "unthreaded"; a record with several keys appears in each (EC23)
- [ ] `transcript` was called only when `agent_database: true`; the EC8 warning is
      shown otherwise
- [ ] Every group is marked found / not found / unavailable / truncated (with the
      omitted count) as the script reported
- [ ] Empty `agent-message` comments are shown as `(no comment)`, not dropped (EC7)
- [ ] Every proposed bucket carries all five fields, a unique name, and a `target`
      that the rationale justifies
