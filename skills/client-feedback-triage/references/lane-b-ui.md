# Lane B — UI Annotation Feedback

> **When to read:** When the `list` result contains `component-select`, `pin`, `shape`, or `freehand` items. Covers how a Lane B record is presented, the screenshot and instruction-block rules, the console-log filter with its two omitted counts, and bucketing by route or component. Item payloads are in `data-model.md`; the document layout is in `templates/triage-doc.md`.

Lane B holds the four annotation types drawn on a screenshot of the page:
`component-select`, `pin`, `shape`, `freehand`. The unit of triage is the **record**:
one submission with a screenshot and four annotations is one artifact. Every client
panel can produce Lane B feedback.

---

## Present a record

Show these, in this order, matching the panel's `buildFeedbackPrompt`
(`txn-admin-panel/src/components/admin/feedback/copy-prompt.ts:15`). The triage
document uses the same order; the debate view may be shorter but must not reorder.

| Field | Rule |
|---|---|
| Submitted by, date | `submitted_by_name`, `created_at` |
| Page | `page_url` with `(route: <route>)` |
| Screenshot | `screenshot_url` — **omit the line entirely when null** (EC19) |
| Items | Each Lane B item in `number` order: the marker `number`, the type label, the type payload, the comment (`(no comment)` when empty) |
| Conversation pointer | The three-state line from `app_state.conversation_id` — see `data-model.md`. Emitted even when null |
| Console logs | Filtered and capped as below |
| Component IDs | `component_ids`, comma-joined, when non-empty |

**Item lines** — the payload each type contributes (`copy-prompt.ts:136-184`):

| Type | Line |
|---|---|
| `component-select` | `` N. **[Component Select]** `component` — "comment" `` then `Selector: …` and `Bounds: [x, y, w, h]` (rounded). `component` null → `Unknown component`; empty selector → `(none)` |
| `pin` | `N. **[Pin]** at (x, y) — "comment"` |
| `shape` | `N. **[Shape: rectangle\|ellipse]** — "comment"` then `Bounds: [x, y, w, h]` |
| `freehand` | `N. **[Freehand]** — "comment"` |

The marker `number` is what ties a comment to its annotation on the screenshot. Keep it
on every line; the reader looks at the screenshot with the numbers in hand.

**The instruction block adapts (EC19).** The document's per-record "Process" block
mirrors `formatProcess` (`copy-prompt.ts:88`):

- `screenshot_url` set → "Open the screenshot URL and review all numbered annotations"
  then "Read each feedback item below — they correspond to numbered markers on the
  screenshot".
- `screenshot_url` null → one line: "Read each feedback item below — this submission
  carries no screenshot". No screenshot line, no reference to markers on an image.
- Then "For component selections, inspect the identified component in the codebase".
- The agent-table lookup step appears only when the record also carries a Lane A item
  (an `agent-message` step, else a `conversation` step, else nothing).
- Then "Propose fixes for each item, prioritising by impact" and "Implement, test, and
  summarise changes".

---

## Console logs — filter, cap, two counts

Source: `formatConsoleLogs`, `copy-prompt.ts:227-261`, cap `MAX_PROMPT_LOGS = 30`
(`:219`). Apply it exactly; do not invent a second format.

1. Take `app_state.console_logs` (up to 100 entries, all levels).
2. Keep only `level` `error` and `warn` — the *notable* entries.
3. If there are none: one line, `(N console entries captured, none at error or warning level)`.
4. Otherwise show the **most recent 30** notable entries, each as `` `[level]` message ``.
5. Report **two** omitted counts, separately, never summed:
   - **dropped past the cap:** `notable − shown` — "`K` older error/warning entries omitted"
   - **routine filtered:** `total − notable` — "`M` routine log/info/debug entries omitted"
   Print each only when it is greater than zero, joined with `; `, followed by
   "Full buffer is on the feedback record."

Worked example (WE10): 14 entries — 3 `error`, 2 `warn`, 9 routine → show 5 lines,
report "0 error/warn dropped past the cap, 9 routine filtered" (the first note is
omitted because it is zero; the second reads "9 routine log/info/debug entries
omitted"). One total would conflate a truncation with a filter.

`app_state` null, or `console_logs` absent or empty → no console section at all.

---

## Bucket by route or by component

Lane B buckets group **records**, by where the problem is:

| Group by | When | Example bucket |
|---|---|---|
| `route` | Several records point at the same page pattern | "challenge page: sidebar overlaps content on `/challenge/[slug]`" |
| an entry in `component_ids` | Several records select or annotate the same component across pages | "`nav-drawer` close button unreachable" |
| the comment's subject | Records on different routes describe one behaviour | "date pickers ignore locale" |

**Rules for the proposal:**

- Bucket by the problem, and name it after the problem. `route` and `component_ids`
  are the two structural hints the data gives; the comments and the screenshot are the
  evidence.
- The default `target` for a Lane B bucket is `frontend`. Override to `agent` or `both`
  when the annotation is really about agent output shown on the page, and say why.
- A record whose items span two problems may join two buckets. The write is per
  record and deduplicated, so this costs nothing at write time (see `write-back.md`).
- A record with both Lane A and Lane B items appears in both lanes, split by item
  (WE6). Its Lane A items are not shown here except as the conversation pointer.
- Bucket names are unique within the run.

**Five fields on every bucket:** `name`, `decision` (`will do` / `not this round`),
`rationale`, member record ids, `target` (`agent` / `frontend` / `both`).

---

## What is not Lane B

- **Unclassified items (EC6).** An item whose `type` is not one of the six known
  types is listed in the document's "unclassified items" section with the type printed
  verbatim. It is not a Lane B item, not bucketable, and receives no write. The panel
  labels it `Unknown` (`item-display.ts:38`); never label it `Shape` or anything else.
- **No items (EC10).** A record whose `feedback_items` is `[]` is listed under "no
  items". It has a route and possibly a screenshot, but no annotation to triage.
- **Lane A items on the same record.** They belong to `lane-a-agent.md`.

---

## Checklist before the proposal

- [ ] Every Lane B record is presented in `buildFeedbackPrompt` order, items sorted by
      `number`
- [ ] The screenshot line is omitted and the instruction block adapted when
      `screenshot_url` is null (EC19)
- [ ] Console logs show only `error`/`warn`, most recent 30, with **two** omitted counts
- [ ] Unclassified items and empty-item records are listed, not bucketed (EC6, EC10)
- [ ] Every proposed bucket carries all five fields, a unique name, and a `target`
      that the rationale justifies
