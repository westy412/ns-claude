# Data Model

> **When to read:** Before the first `list` call of a session, and whenever a record, an item type, a conversation key, or an agent-database column needs interpretation. This is the ground truth the lane references and the triage template build on.

The skill reads one record type — a `feedback` row — and its `feedback_items` JSONB
union. Every rule below is lifted from the client admin panel and the client admin
API, so the triage document says the same thing the panel says. Where a rule has a
source, the source is cited so it can be re-checked.

---

## The feedback record

Source: `txn/txn-admin-api/supabase/txn/01_schema.sql` (`txn.feedback`, `:70-85`).
Every client instantiated from `novosapien/admin-api-template` carries the same
columns in its own schema. inPlay's schema is `public` (`inPlay/inplay-admin-api/supabase/schema.sql:30`) — see EC17 in `write-back.md`.

| Column | Type | Null | Notes |
|---|---|---|---|
| `id` | `uuid` | PK | `gen_random_uuid()` default. The record id used in buckets, the payload, and every write |
| `page_url` | `text` | no | Full URL at submission |
| `route` | `text` | no | Route pattern, e.g. `/challenge/[slug]`. Lane B buckets by it |
| `submitted_by` | `uuid` | yes | FK `auth.users(id)`. String-equals `conversations.user_id` on the agent database (route unused in v1) |
| `submitted_by_name` | `text` | no | Display name captured at submission |
| `feedback_items` | `jsonb` | no | The item union below. May be `[]` — see "no items" (EC10) |
| `component_ids` | `text[]` | yes | `data-component` ids on the page. Lane B buckets by entries here |
| `app_state` | `jsonb` | yes | Page snapshot at submission; carries `conversation_id` and `console_logs`. May be `null` |
| `origin` | `text` | no | Surface label, e.g. `TXN Console`. Default `Challenge Website` |
| `review_status` | `text` | no | CHECK: `New`, `In Progress`, `Resolved`, `Dismissed` (`:80-81`). The skill reads `New` only and **never writes this column** |
| `screenshot_url` | `text` | yes | `null` on agent-side submissions and when capture failed (EC19) |
| `created_at` | `timestamptz` | yes | `now()` default. `list` orders ascending on it |
| `updated_at` | `timestamptz` | yes | Trigger-maintained |

**`app_state` keys** (`txn-admin-panel/src/lib/api/types.ts:180-201`): `pageUrl`,
`route`, `viewportWidth`, `viewportHeight`, `devicePixelRatio`, `scrollX`, `scrollY`,
`userAgent`, `theme`, `queryParams`, `timestamp`, and three optional keys —
`conversation_id` (`string | null`), `console_logs` (up to the 100 most recent
entries), `screenshot_error`. A `console_logs` entry is
`{ level, message, timestamp, stack? }` with `level` in the closed set
`log | info | debug | warn | error` (`types.ts:159-163`). The `list` script emits
`app_state` verbatim from the JSONB and renames nothing, so the stored key
`timestamp` is the key you read.

**Related tables the skill reads** (same schema, `01_schema.sql:46-134`):
`feedback_comments` (`id`, `feedback_id`, `user_id`, `content`, `created_at`),
`user_activity_events` (`id`, `actor_user_id`, `action_type`, `entity_type`,
`entity_id`, `metadata`), `user_profiles` (`id`, `email`, `full_name`, `role`).
What is written to them, and why nothing else is written, lives in `write-back.md`.

---

## The feedback_items union

Source: `txn/txn-admin-panel/src/lib/api/types.ts:64-151`. Items are stored as JSONB,
so a reader must narrow on `type` before it reads a variant field.

**Every item** carries three shared fields:

| Field | Type | Meaning |
|---|---|---|
| `number` | `number` | 1-based marker label rendered on the screenshot. Ties a comment to its annotation. Items are presented in `number` order |
| `type` | `string` | Discriminator. One of the six below, or an unknown value (EC6) |
| `comment` | `string` | The reporter's text. **May be `""` on `agent-message`** — the console's text field is optional on that form and the API rejects a null, so an empty comment is valid data and is never dropped (EC7, `types.ts:109-111`) |

**Per-type payload:**

| `type` | Payload fields | Source line |
|---|---|---|
| `agent-message` | `category` (one of six slugs), `message_id` (agent `messages.id`), `conversation_id` (agent `conversations.id`) | `:112-119` |
| `conversation` | `conversation_id` (agent `conversations.id`, pinned when the form opened). No category, no screenshot | `:125-129` |
| `component-select` | `component` (`string \| null`), `selector`, `bounds` `{x, y, width, height}` | `:71-77` |
| `pin` | `position` `{x, y}` | `:94-97` |
| `shape` | `shapeKind` (`rectangle \| ellipse`), `bounds`, `strokeColor`, `strokeWidth` | `:86-92` |
| `freehand` | `points` `[{x, y}]`, `strokeColor`, `strokeWidth` | `:79-84` |

Stored items also carry `component_id: null` and `selector: null` on every variant
— the API's `model_dump` writes them whether the widget sent them or not
(`types.ts:139-143`). Ignore them on variants that do not own them.

A record whose `feedback_items` is `[]` is included in the read, belongs to neither
lane, and is listed in the document under **"no items"** so it is not silently lost
(EC10).

---

## The lane split

| `feedback_items[].type` | Lane | Unit of triage | Payload |
|---|---|---|---|
| `agent-message` | A | conversation | `category`, `message_id`, `conversation_id` |
| `conversation` | A | conversation | `conversation_id` |
| `component-select` | B | record | `component`, `selector`, `bounds` |
| `pin` | B | record | `position` |
| `shape` | B | record | `shapeKind`, `bounds`, stroke |
| `freehand` | B | record | `points`, stroke |
| anything else | — | unclassified | EC6 — informational only |

A record with items of both kinds appears in **both** lanes, split by item (R3). The
lane is a property of the item, not the record.

**Why the unit differs per lane:** the natural unit follows the data. Five agent
records about one conversation are one problem. One UI record with a screenshot and
four annotations is one artifact.

**Unknown types (EC6).** An item whose `type` is not one of the six is
*unclassified*. Print the type verbatim, never map it onto a known type, never drop
it. Unclassified items are informational: they can be discussed but are not
bucketable and receive no write. The panel does the same: `itemTypeLabel()`
(`txn-admin-panel/src/components/admin/feedback/item-display.ts:38`) returns a
neutral `Unknown`, because an earlier build labelled every unrecognised item `Shape`
— a false claim about the row. Repeating that here would put a false claim in a
client-visible document.

---

## The six category slugs

Source: `AgentMessageCategory`, `txn/txn-admin-panel/src/lib/api/types.ts:30-36`.
Only `agent-message` items carry a `category`; a `conversation` item has none.

| Slug (stored) | Panel label (`item-display.ts:54-61`) |
|---|---|
| `wrong-answer` | Wrong answer |
| `made-up` | Made something up |
| `incomplete` | Incomplete |
| `ignored-data` | Ignored my data |
| `tone-format` | Tone/format |
| `too-slow` | Too slow |

**The category is picked by the reporter in the console form. It is not assigned by
AI.** It is exactly as reliable as the person who filed it. Lane A buckets by slug
as a starting point; a `too-slow` or `tone-format` complaint is often a frontend
streaming or rendering defect, so the bucket's target lane may be `frontend` even
though the item is Lane A.

The slug is the only thing stored — it lives in JSONB with no queryable column
behind it. Present it as `label (slug)`, the way the panel briefing does. An
unrecognised slug is printed verbatim, not replaced (`item-display.ts:71-78`).

---

## Conversation key resolution (Lane A)

Source: `conversationKey()`,
`txn/txn-admin-panel/src/components/admin/feedback/feedback-rows.ts:30-43`. The
`list` script derives the key; the skill body does not re-derive it.

**Order:** `app_state.conversation_id` first, when it is a non-empty string. Otherwise
the item-level `conversation_id` on an `agent-message` or `conversation` item.
Otherwise no key.

**The order matters, and the reason is (R4):** `app_state` carries the conversation
the submission was *made against*, taken from the event payload. Reading the
item-level id first would thread a record into a different conversation than the
one its submission named, if the user switched chats before the POST landed. A
record with neither key threads nowhere and must never be swept into another
conversation by a looser fallback.

Concretely (EC1): `app_state.conversation_id` absent, one `agent-message` item with
a `conversation_id` → thread by the item-level id. `app_state` is checked first and
falls through only when it holds no non-empty string.

**Two fields on every `list` record**, both script-derived:

| Field | Rule |
|---|---|
| `conversation_keys` | The full set of Lane A buckets the record joins. `[app_state.conversation_id]` when that is set. Otherwise every **distinct** item-level `conversation_id` on Lane A items, in item order. Otherwise `[]` |
| `conversation_key` | Panel parity: `conversation_keys[0]`, or `null`. Mirrors `conversationKey()` exactly — the panel needs one key per row for its filter |

**A record can join several buckets (EC23).** A record with two `agent-message`
items carrying **different** `conversation_id` values and no `app_state.conversation_id`
joins **both** conversation buckets, split by item, consistent with R3. It is not
forced into one.

**The "unthreaded" bucket (EC2).** A record with `conversation_keys: []` and at
least one Lane A item belongs to **one** shared bucket named "unthreaded". Each
such record keeps its own decision inside that bucket. Unthreaded records are never
merged into a real conversation. Five records with no key anywhere share that one
bucket.

---

## The three-state conversation id

Source: `formatConversationId()`,
`txn/txn-admin-panel/src/components/admin/feedback/copy-prompt.ts:208-216`, and
`contextConversationId()`, `feedback-rows.ts:58-64`. The distinction between the
last two states is the whole point: reporting one as the other tells the reader
something the data does not say (EC3).

| Reality | Stored | `list` emits | Document line |
|---|---|---|---|
| A chat was open; its id was captured | `"conversation_id": "<uuid>"` | `"app_state": { "conversation_id": "<uuid>", … }` | `Conversation ID: <uuid>` plus the agent-table pointer |
| The widget looked; no chat was open | `"conversation_id": null` | `"app_state": { "conversation_id": null, … }` | `Conversation ID: none — no chat was active when this was submitted` |
| The record predates conversation capture (`undefined`) | key absent | key omitted from `app_state` | `Conversation ID: not recorded — this submission predates conversation capture` |
| `app_state` itself is `null` | `app_state = null` | `"app_state": null` | Treated as `undefined` — the "not recorded" line (EC3) |

The top-level `conversation_key` is `null` in the last three cases unless an
item-level id supplies one. The document renders the pointer even when it is
`null`, so a reader learns there was no chat rather than assuming the field was dropped.

---

## Agent database — nova-kernel 0.4.5 shapes

**Source:** `txn/txn-agentic-agent/.venv/lib/python3.12/site-packages/nova_kernel/persistence/models.py`,
package `nova_kernel-0.4.5.dist-info` (`Version: 0.4.5`), read on 2026-08-17.
The `.venv` path is not version-controlled and a `uv sync` can move it, which is why
the shapes are recorded here. The `transcript` script is built against this table,
not against the `.venv`.

Both tables live in **`public`** on the agent database — nova-kernel calls
`metadata.create_all` on an unqualified declarative base. That database is a
**different host** from the admin database, so there is no collision with inPlay's
`public`. Do not set `search_path` on the agent connection; qualify as
`public.conversations` and `public.messages`. The agent connection is read-only to
this skill.

TXN configures the kernel with `tenant_key=tenant_id` and `id_type=str`
(`txn/txn-agentic-agent/CLAUDE.md:40`), so the tenant column is named `tenant_id`
and the actor/tenant columns are `varchar(255)`, not `uuid`.

**`public.conversations`** (`models.py:129-169`)

| Column | Type | Null | Key | Notes |
|---|---|---|---|---|
| `id` | `uuid` | no | PK | Kernel-minted `uuid4`. This is the value in `app_state.conversation_id` and item-level `conversation_id` |
| `user_id` | `varchar(255)` | no | | Owner. String-equals `feedback.submitted_by` (route unused in v1) |
| `channel` | `varchar(20)` | no | | e.g. `web`, `whatsapp` |
| `title` | `text` | yes | | Conversation title |
| `sdk_session_id` | `text` | yes | | Agent SDK session id for resume |
| `status` | `varchar(20)` | no | | `active` or `archived`; default `active` |
| `tenant_id` | `varchar(255)` | yes | | The tenant column, named by `tenant_key`. **Nullable** — an absent tenant is a null column. TXN's registry sets `tenant_id: null`, so the R5 predicate is unexercised today |
| `created_at` | `timestamptz` | no | | `now()` server default |
| `updated_at` | `timestamptz` | no | | `now()` server default, `onupdate` |

**`public.messages`** (`models.py:171-192`)

| Column | Type | Null | Key | Notes |
|---|---|---|---|---|
| `id` | `uuid` | no | PK | Kernel-minted `uuid4`. This is `message_id` on an `agent-message` item |
| `conversation_id` | `uuid` | no | FK → `conversations.id`, `ON DELETE CASCADE` | The `transcript` filter column |
| `role` | `varchar(20)` | no | | `user`, `assistant`, or `system` |
| `content` | `text` | no | | Message text. Can be empty when the payload sits in `content_blocks` |
| `content_blocks` | `jsonb` | yes | | Structured content blocks. Read it — a structured assistant turn can carry its payload here, and a transcript from `content` alone renders empty rows (R5) |
| `tool_calls` | `jsonb` | yes | | Tool invocations in this message |
| `created_at` | `timestamptz` | no | | `now()` server default. `transcript` orders ascending on it. No `updated_at` on this table |

`transcript` returns `id`, `role`, `content`, `content_blocks`, `tool_calls`, and
`created_at` per message. The `id` is what an `agent-message` item's `message_id`
points at, so the document can mark the flagged reply. When a conversation exceeds 200 messages, the **most
recent 200** are returned in `created_at` ascending order with `truncated: true`
and `total_messages` set, so the document can state how many earlier messages were
omitted.

---

## Lane coverage today

Only TXN carries Lane A. `agent-message` and `conversation` items appear in no
other client's panel, and the other three registered clients (`inPlay`, `caterer`,
`total-jobs`) have no credentials configured yet, so their Lane-B-only path is
verified at registry level rather than against a live database (Notes K5). A
client with `agent_database: null` never opens an agent connection, even when its
records carry Lane A items — see EC8 in `lane-a-agent.md`.

---

## Script-derived fields on `list`

These fields exist on every `list` record and are computed by the read script, so
the grouping and the already-scheduled rules live in one place. The skill body reads
them; it does not recompute them.

| Field | Meaning |
|---|---|
| `conversation_key` | Panel-parity single key, or `null` (rule above) |
| `conversation_keys` | The set of Lane A buckets the record joins (rule above) |
| `already_scheduled` | `true` when the record carries a `feedback_comments` row whose text starts with `Triaged ` — of **any** date (R2). Such records are shown collapsed and excluded from the default debate set, and can be pulled back in |
| `prior_triage_comments` | The text of each such comment, e.g. `Triaged 2026-08-10 — scheduled`, so the collapsed section can state the prior triage date(s) |

The full `list`, `detail`, and `transcript` JSON contracts are fixed in the spec's
Architecture → "Script I/O contracts". Load `lane-a-agent.md` and `lane-b-ui.md` for
how each lane consumes them.
