<!--
TEMPLATE RULES — read, then do not copy this comment into the document.

Path:      <client-root>/feedback/YYYY-MM-DD-triage.md   (machine local date)
Create:    <client-root>/feedback/ if absent. Fail if <client-root> is absent (EC22).
Same day:  if the file exists, APPEND a new "## Session …" section under the one H1
           (WE13). Never create a second file for the same date.
Order:     write this document BEFORE the first database statement (WE16, R10).
           If it cannot be written — absent root, permission denied, disk full —
           abort before any database statement and report the path (EC22).
Then:      run `apply`, then fill "## Write-back → Result" (R10, EC15).
Skip:      no document at all when `count: 0` (EC9), or when every record is already
           scheduled and none was pulled back (EC21).
Markers:   [square brackets] = value to fill.  <!-- repeat --> = one copy per thing.
           Drop a subsection that has nothing in it, except "Write-back" and
           "Discovery handoffs" (write "none" there).
Per-record detail: bold labels in the exact `buildFeedbackPrompt` section order —
           Process → Feedback Record → Screenshot → Feedback Items → App State →
           Console Logs → Component IDs (copy-prompt.ts:15). Never a second format.
-->

# Feedback Triage — [Client key] — [YYYY-MM-DD]

## Session [YYYY-MM-DD HH:MM]

| Field | Value |
|---|---|
| Client | `[key]` — schema `[schema]` |
| Actor | [default_actor.name, or the name given on override] |
| Date | [YYYY-MM-DD] (local) |
| Records at `New` | [count] |
| In the debate | [n] |
| Already scheduled | [n] ([k] pulled back) |
| No items | [n] |
| Unclassified items | [n] |
| Transcripts | available / not configured (EC8) / unavailable (EC4) / not needed |

<!-- Transcript status: include exactly one of the two banners when it applies; omit otherwise. -->
> **Transcripts unavailable (EC4).** The agent database was unreachable or timed out.
> No further transcript calls were made this session. Lane A was triaged on the
> comments alone; every conversation group below is marked "transcript unavailable".
> Lane B is unaffected.

> **Registry incomplete (EC8).** `[key]` has `agent_database: null` in `config.json`,
> but the queue carries Lane A items. No agent connection was attempted. Lane A was
> triaged on the comments alone. Add the client's agent database to the registry.

---

### Already scheduled

<!-- Records with already_scheduled: true. Always shown when non-empty, collapsed.
     If EVERY record was already scheduled and at least one was pulled back (EC21),
     open with: "Every open record ([n]) was already scheduled. The default debate set
     was empty; [k] record(s) were pulled back into the debate and are listed below."
     Records not pulled back received no write this session. -->

<details>
<summary>[n] record(s) already scheduled — out of the default debate set</summary>

| Record | Summary | Prior triage | Pulled back |
|---|---|---|---|
| `[id]` | [first item's comment, else route] | [Triaged YYYY-MM-DD — scheduled] [; more] | yes / no |

</details>

---

### Decisions

<!-- One row per bucket, both lanes, five fields. The same five fields repeat in full
     inside each lane section. Bucket names are unique within the run. -->

| # | Bucket | Lane | Decision | Target | Member records |
|---|---|---|---|---|---|
| 1 | [name] | A / B | `will do` / `not this round` | `agent` / `frontend` / `both` | `[id]`, `[id]` |

`not this round` means exactly that. Those records stay open feedback; nothing was
written for them, and they will be presented again next run.

---

### Lane A — agent feedback

<!-- repeat: one block per Lane A bucket -->
#### Bucket: [name]

| Field | Value |
|---|---|
| Decision | `will do` / `not this round` |
| Target | `agent` / `frontend` / `both` |
| Rationale | [why — evidence from the comments and the transcript] |
| Member records | `[id]`, `[id]` |
| Conversations | `[conversation_id]`, `[conversation_id]` / unthreaded |

<!-- repeat: one block per conversation group in the bucket. The "unthreaded" group
     (EC2) is one block titled "Conversation: unthreaded", with each record's own
     line and decision inside it. -->
**Conversation `[conversation_id]`** — transcript: found / not found (EC5) /
unavailable (EC4) / not configured (EC8) / malformed stored id / found, truncated:
[total_messages − 200] earlier messages omitted (EC20)

<!-- Optional transcript excerpt: the flagged reply (messages.id = the item's
     message_id) and the user turn before it. Read content_blocks as well as content. -->
> **[role]** ([created_at]): [content or content_blocks summary]
> **[role]** ([created_at]) `[message id]`: [the flagged reply]

<!-- repeat: per member record — Lane A items only, in `number` order. Records that
     join several groups (EC23) appear in each, with only the items that belong there.
     Then the per-record detail block. -->
- Record `[id]` — item [number] **[Agent reply]** [label] ([slug]) — "[comment or (no comment)]" — message `[message_id]`
- Record `[id]` — item [number] **[Conversation]** — "[comment]"

<!-- per-record detail: see "Per-record detail" at the end; one per record per lane. -->

---

### Lane B — UI annotation feedback

<!-- repeat: one block per Lane B bucket -->
#### Bucket: [name]

| Field | Value |
|---|---|
| Decision | `will do` / `not this round` |
| Target | `frontend` / `agent` / `both` |
| Rationale | [why — route, component, screenshot evidence] |
| Member records | `[id]`, `[id]` |
| Grouped by | route `[route]` / component `[component_id]` / subject |

<!-- repeat: per member record — the per-record detail block below. -->

---

### Unclassified items (EC6)

Informational only. These items carry a `type` this build does not know. The type is
printed verbatim, never mapped onto a known type. They can be discussed; they are not
bucketable and receive no write.

| Record | Item | `type` (verbatim) | Comment |
|---|---|---|---|
| `[id]` | [number] | `[type]` | "[comment]" |

---

### No items (EC10)

Records whose `feedback_items` is `[]`. Included in the read, in neither lane, listed
here so they are not silently lost.

| Record | Route | Page | Submitted by | Created |
|---|---|---|---|---|
| `[id]` | `[route]` | [page_url] | [submitted_by_name] | [created_at] |

---

### Per-record detail

<!-- One block per record that appears in Lane A or Lane B (a record in both lanes
     gets one block, listing all its items). Bold labels, in this exact order,
     mirroring buildFeedbackPrompt (copy-prompt.ts:15). Omit "Screenshot" when
     screenshot_url is null (EC19); omit "Console Logs" when app_state is null or has
     no console_logs; omit "Component IDs" when empty. Never reorder. -->

**Record `[id]`** — [first item's comment, else route]

**Process**
<!-- screenshot_url set: -->
1. Open the screenshot URL and review all numbered annotations
2. Read each feedback item below — they correspond to numbered markers on the screenshot
<!-- screenshot_url null (EC19): replace steps 1–2 with the single step -->
1. Read each feedback item below — this submission carries no screenshot
<!-- always (renumber the steps sequentially, as formatProcess does): -->
3. For component selections, inspect the identified component in the codebase
<!-- only when the record has an agent-message item; else the conversation variant; else omit -->
4. For agent-reply feedback, resolve `message_id` against the agent project's `messages` table and `conversation_id` against its `conversations` table, to read what the agent actually said
4. For conversation feedback, resolve `conversation_id` against the agent project's `conversations` table to read the thread the comment is about
5. Propose fixes for each item, prioritising by impact
6. Implement, test, and summarise changes

**Feedback Record**
- **Submitted by:** [submitted_by_name]
- **Date:** [created_at]
- **Status:** New
- **Page:** [page_url] (route: [route])

**Screenshot**
[screenshot_url]

**Feedback Items**
<!-- all items, sorted by number; comment "" → (no comment) (EC7) -->
1. **[Component Select]** `[component or Unknown component]` — "[comment]"
   - Selector: [selector or (none)]
   - Bounds: [x, y, w, h]
2. **[Pin]** at ([x], [y]) — "[comment]"
3. **[Freehand]** — "[comment]"
4. **[Shape: rectangle|ellipse]** — "[comment]"
   - Bounds: [x, y, w, h]
5. **[Agent reply]** [label] ([slug]) — "[comment or (no comment)]"
   - Message ID: `[message_id]` — query the agent project's `messages` table by id for the reply this feedback is about
   - Conversation ID: `[conversation_id]` — query the agent project's `conversations` table for this id
6. **[Conversation]** — "[comment]"
   - Conversation ID: `[conversation_id]` — query the agent project's `conversations` table for this id; the feedback is about the thread as a whole, not one reply

**App State**
<!-- exactly one of the three conversation lines (EC3); a null app_state → the "not recorded" line
     only — omit the Viewport / User Agent / Scroll lines, there is no snapshot to print -->
- **Conversation ID:** `[uuid]` — query the agent project's `conversations` table for this id; the submitter is `feedback.submitted_by`, which string-equals `conversations.user_id`
- **Conversation ID:** none — no chat was active when this was submitted
- **Conversation ID:** not recorded — this submission predates conversation capture
- Viewport: [w]x[h] @ [dpr]x
- User Agent: [userAgent]
- Scroll: [scrollX], [scrollY]

**Console Logs**
<!-- error/warn only, most recent 30, TWO counts (lane-b-ui.md → Console logs) -->
- `[error]` [message]
- `[warn]` [message]

_[K] older error/warning entries omitted; [M] routine log/info/debug entries omitted. Full buffer is on the feedback record._
<!-- or, when no error/warn entries exist: -->
([N] console entries captured, none at error or warning level)

**Component IDs**
[component_id], [component_id]

---

## Write-back

Document written at [HH:MM] — before the first database statement (R10).

**Payload sent to `apply`** (`scripts/triage_write.py apply [key]`, stdin):

```json
{
  "date": "[YYYY-MM-DD]",
  "actor": "[actor display name]",
  "buckets": [
    { "name": "[name]", "decision": "will do", "rationale": "[rationale]",
      "target": "agent", "record_ids": ["[id]", "[id]"] },
    { "name": "[name]", "decision": "not this round", "rationale": "[rationale]",
      "target": "frontend", "record_ids": ["[id]"] }
  ]
}
```

**Result** <!-- fill after apply; exactly one of the three -->

- exit 0 — written: `[id]`, `[id]` · skipped (same-date comment already present, R10): `[id]` · comment ids: `[feedback_id → comment_id]`
- exit 5 `PARTIAL_WRITE` (EC15) — written: `[id]`, `[id]` · **unwritten:** `[id]`, `[id]` · [message]. Re-run `apply` over the same payload to continue; written records are skipped.
- exit [1|2|3|6] `[error]` — nothing written · [message]

Each written record now carries one `feedback_comments` row reading exactly
`Triaged [YYYY-MM-DD] — scheduled` and one `user_activity_events` row
(`comment.created`, `entity_id` = the comment id). No `review_status` was changed.
Records in `not this round` buckets only, and unclassified items, received nothing.

---

## Discovery handoffs

<!-- repeat: one block per `will do` bucket, in Decisions order. `not this round`
     buckets get no block. The first line of each block is the literal invocation. -->

```
/discovery
```

**Bucket:** [name]
**Rationale:** [rationale]
**Member record ids:** `[id]`, `[id]`
**Target lane:** `agent` / `frontend` / `both`
**Conversation ids (Lane A):** `[conversation_id]`, `[conversation_id]` <!-- omit for a Lane B bucket -->
**Source:** this document, `[<client-root>/feedback/YYYY-MM-DD-triage.md]`, session [HH:MM]

`/discovery` takes no arguments; paste or point it at this block. The discovery run
creates its own `<client-root>/specs/YYYY-MM-DD-<name>/` folder. Triage documents
stay in `<client-root>/feedback/`; spec folders stay in `<client-root>/specs/`.
