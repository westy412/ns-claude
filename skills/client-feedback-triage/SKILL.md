---
name: client-feedback-triage
description: "Triage a client's open admin panel feedback into buckets of work. Reads every feedback record at review_status New from the client's own Postgres schema, splits it into two lanes (Lane A: agent-reply and conversation feedback grouped by conversation with transcripts from the agent database; Lane B: UI annotations — pins, shapes, freehand, component selects — grouped by route or component), proposes a complete bucket set up front, debates it with the user, writes a dated triage document to <client-root>/feedback/, marks only the selected records with a client-safe templated comment plus an audit row, and ends with one /discovery handoff block per will-do bucket. Never writes review_status. Use for client feedback triage, admin panel feedback review, TXN feedback, agent feedback buckets, UI feedback buckets, or turning open feedback into discovery runs."
argument-hint: '[client]'
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, AskUserQuestion, Write, Edit, Skill
---

# Client Feedback Triage

> **Invoke with:** `/client-feedback-triage [client]` | **Keywords:** feedback triage, admin panel feedback, client feedback, agent feedback buckets, UI feedback, discovery handoff

Reads a client's open admin-panel feedback, splits it into two lanes, proposes buckets, debates them with the user, writes a triage document, and marks the selected records with a comment. It hands off to `/discovery`; it does not run discovery itself.

**Input:** an optional client key — one of the keys in `config.json` (for example `txn`). No argument, or an unknown one, makes the skill list the known clients and ask.
**Output:** `<client-root>/feedback/YYYY-MM-DD-triage.md`, plus one `Triaged YYYY-MM-DD — scheduled` comment and one `comment.created` audit row per selected record.

**Pipeline:**
```
client-feedback-triage → /discovery (one run per "will do" bucket) → spec-builder → implementation
```

## When to Use This Skill

Use this skill when:
- Open feedback has accumulated in a client's admin panel and needs to become scoped work
- You want to batch-review agent-reply feedback by conversation, with the transcript in front of you
- You want to batch-review UI annotation feedback by route or component
- You want a written record of what was picked up this round and why, before any discovery starts

**Skip this skill when:**
- The feedback belongs to an internal Novosapien product (use `feature-impl`)
- You want to think through one idea in depth (use `discovery` directly)
- You need to change a record's status — this skill never writes `review_status`, by design
- The feedback is vault documentation review (`doc_feedback`) — out of scope

## Reference Files

Load one at a time, when the step calls for it.

| Topic | Reference File | When to Load |
|-------|---------------|--------------|
| The record, the six item types, the lane split, conversation keys, agent-DB shapes | [data-model.md](references/data-model.md) | Before the first `list` call, and whenever a record or item needs interpretation |
| Lane A: conversation grouping, transcript use, category buckets, "unthreaded" | [lane-a-agent.md](references/lane-a-agent.md) | When the `list` result contains `agent-message` or `conversation` items |
| Lane B: record presentation, screenshot, components, console logs, route/component buckets | [lane-b-ui.md](references/lane-b-ui.md) | When the `list` result contains `component-select`, `pin`, `shape`, or `freehand` items |
| What is written, what is never written, client visibility, the comment template, the payload | [write-back.md](references/write-back.md) | After approval, before building the `apply` payload |
| Adding a client, the two credential formats, `null` paths | [client-registry.md](references/client-registry.md) | When a client is "not yet configured" or a new client must be added |

**Template:**

| Template | Purpose |
|----------|---------|
| [triage-doc.md](templates/triage-doc.md) | The triage document — load it when writing the document (step 8) |

## Key Principles

1. **Read everything, then propose the whole bucket set** — no per-item discussion before the complete proposal is on the table (R7)
2. **Explicit approval before any write** — the user approves the final bucket set in so many words. Silence is not approval
3. **Document first, database second** — the triage document exists on disk before the first database statement, and is annotated afterwards (R10, EC22)
4. **Never write a status** — `<schema>.feedback` is read-only. Only selected records get a comment; unselected records are left untouched, and "not selected" is not a rejection (R9)
5. **Client-safe text only** — every comment is the byte-exact template. Rationale lives in the document, which the client never sees
6. **The scripts derive, the skill body reads** — conversation keys, "already scheduled", the write set: computed in one place, not re-derived in prose
7. **Say what you do not know** — a missing transcript, an unknown item type, an absent conversation id are stated, never guessed

## Session Flow

| Step | What happens | Reference |
|------|--------------|-----------|
| 1 Resolve | `clients` → match the argument → ask if none/unknown | client-registry.md |
| 2 Read | `list <client>` → records, lanes, "already scheduled" | data-model.md |
| 3 Present | One-line summary per record; the collapsed "already scheduled" section | data-model.md |
| 4 Transcripts | Lane A only; needs the registry gate (`agent_database: true`) and the data gate (a Lane A item exists) | lane-a-agent.md |
| 5 Propose | The complete bucket set across both lanes, five fields each | lane-a-agent.md, lane-b-ui.md |
| 6 Debate | Rename, split, merge, move, decide; `detail` on request | lane-a-agent.md, lane-b-ui.md |
| 7 Approve | Explicit approval of the final set | — |
| 8 Document | Write `<client-root>/feedback/YYYY-MM-DD-triage.md` | templates/triage-doc.md |
| 9 Write | Build the payload, run `apply` | write-back.md |
| 10 Annotate | Add the write result to the document; the handoff blocks are already in it | write-back.md |

### Step by step

Script paths are relative to the skill directory. The Execution section states how to resolve it.

1. **Resolve the client (R1).** Run `scripts/triage_read.py clients`. It reads the registry only and opens no connection. Match the argument **case-insensitively against the exact key** — no prefix match: `TXN` resolves `txn`, `totaljobs` does not resolve `total-jobs` (WE2, WE4). If there is no argument, or `list` returns `UNKNOWN_CLIENT`, show every key from `clients` (or from the envelope's `known_clients`), mark each `configured: false` entry **"not yet configured"**, and ask the user which client (WE3). A "not yet configured" client cannot be selected; say so, name the key, and never fall back to another client's credentials (EC11). Open no connection before the answer.
2. **Read the open feedback (R2).** Run `scripts/triage_read.py list <client>`. Load `data-model.md` for the record shape. `count: 0` is a success: report the empty queue, write no document, run no write, stop (EC9).
3. **Present the queue (R7).** Show one line per record in `created_at` order: the first item's comment, or the `route` when there is nothing to quote (`summariseRow`). Do not render full detail yet. Records with `already_scheduled: true` go in a **collapsed "already scheduled" section**, each with its prior triage date(s) from `prior_triage_comments`. They are out of the default debate set, not out of the session. When the section is non-empty, offer to pull any record back into the debate by id. If **every** record is already scheduled, say the default debate set is empty and offer the pull-back; write no document and run no write unless the user pulls at least one record in (EC21). Records with `feedback_items: []` are listed under **"no items"** (EC10). Items with an unknown `type` are listed as **unclassified**, type printed verbatim (EC6).
4. **Fetch transcripts (Lane A, R5).** Two gates, both must pass: the **registry** — the resolved client has `agent_database: true` in the `clients` output — and the **data** — at least one record in the queue carries a Lane A item. No Lane A item anywhere → no `transcript` call at all, even when `agent_database: true`. Load `lane-a-agent.md`. Run `scripts/triage_read.py transcript <client> <conversation_id>` once per distinct value across all `conversation_keys`. Degrade per the exit-code table below: unreachable → banner and continue (EC4); `found: false` → "transcript not found" (EC5); `truncated: true` → state how many earlier messages were omitted (EC20). When `agent_database` is `false` and Lane A items exist, call nothing, present the items without transcripts, and warn that the registry entry is incomplete (EC8).
5. **Propose the complete bucket set (R7).** Load `lane-a-agent.md` and `lane-b-ui.md`. Across **both** lanes, before any per-item discussion, propose every bucket with **five fields**: `name` (unique within the run), `decision` (`will do` / `not this round`), `rationale`, member record ids, `target` (`agent` / `frontend` / `both` — default `agent` for a Lane A bucket, `frontend` for a Lane B bucket; a prior, not a constraint). A record with items in both lanes appears in both lanes, split by item (WE6, EC23). Unclassified items are discussable but not bucketable.
6. **Debate.** The user renames, splits, merges, moves records, and sets decisions. On request, run `scripts/triage_read.py detail <client> <record_id>` for one record's full detail and comment thread; `found: false` means the id matches no row. `not this round` means exactly that: the record stays open feedback and nothing is written for it. Not selected is not a rejection (R9).
7. **Approve.** Restate the final bucket set in full and ask for explicit approval. Do not proceed on an implicit yes. Any change after approval re-opens the gate.
8. **Write the document (R8).** Load `templates/triage-doc.md`. Path: `<client-root>/feedback/YYYY-MM-DD-triage.md`, machine local date. Create `<client-root>/feedback/` if absent; **fail if `<client-root>` is absent**. If a file for the date exists, append a new dated section; never create a second file (WE13). Confirm the file exists on disk. If it cannot be written — absent root, permission denied, disk full — **abort before any database statement** and report the path that failed (EC22). The handoff blocks (R12) are part of the document, one per `will do` bucket, opening with the literal line `/discovery`.
9. **Write back (R9).** Load `write-back.md`. Build the payload — `date`, `actor` (the display name for the document only: `default_actor.name` from the `clients` output; when the user overrides with `--actor-email`, ask for a display name too), `buckets[]` with `name`, `decision`, `rationale`, `target`, `record_ids` — including the `not this round` buckets, and pipe it to `scripts/triage_write.py apply <client>` on stdin (`--actor-email` to override the registry default). The script writes one comment plus one audit row per record in any `will do` bucket, deduplicated by record id, and nothing for the rest.
10. **Annotate.** Add the result to the document: `written` and `skipped` ids on success, or the failure envelope's `written` / `unwritten` on exit 5 (EC15). Tell the user the document path and that each `will do` block is ready for `/discovery`.

## Script failures — what the skill body does

Every script prints one JSON object to stdout, success or failure. Branch on the exit code, report the `error` string and `message`.

| Exit | `error` | Body behaviour |
|---|---|---|
| 0 | — | Continue. `count: 0` on `list` is the empty queue (EC9) |
| 1 | `UNEXPECTED` | Show the message and stop the step. Do not retry blindly |
| 2 | `UNKNOWN_CLIENT` | Fall through to the client ask, listing `known_clients` (WE4) |
| 2 | `CLIENT_NOT_CONFIGURED` | "This client is not yet configured" — name the key. Never use another client's credentials (EC11). On `transcript`, this means the registry has `agent_database: null` — the body should not have called it (EC8) |
| 2 | `CREDENTIALS_MISSING` | Stop before any connection; name the missing path (EC12) |
| 3 | `ADMIN_DB_UNREACHABLE`, `ADMIN_DB_TIMEOUT` | **Hard stop.** Present nothing. Not a degraded mode (EC18) |
| 4 | `AGENT_DB_UNREACHABLE` | `transcript` only. Stop further transcript calls this session, put the transcript-unavailable banner in the document, continue Lane A on the comments alone. Lane B unaffected (EC4) |
| 5 | `PARTIAL_WRITE` | Stop. Annotate the document with the envelope's `written` and `unwritten` ids. Re-running `apply` over the same payload skips what landed (EC15) |
| 6 | `ACTOR_NOT_FOUND` | Nothing was written. Report the actor email; the actor needs a `user_profiles` row (EC13) |
| 6 | `SCHEMA_VIOLATION` | Stop and report. A statement targeted a table outside the allow-list; nothing executed (EC16) |
| 6 | `MALFORMED_PAYLOAD` | Two cases. (a) The `apply` payload or a CLI id argument the body typed is bad — fix it and re-run. (b) On `transcript`, the stored `conversation_id` on a Lane A item is not a UUID — report it as a malformed stored id and triage that group on the comments alone, like EC5 |

## Output

```
<client-root>/feedback/
└── YYYY-MM-DD-triage.md     header, already-scheduled, Lane A, Lane B, unclassified, no items,
                             buckets (five fields), write result, /discovery blocks
```

Database: one `<schema>.feedback_comments` row and one `<schema>.user_activity_events` row per selected record. Nothing else.

## Execution

This section is the only place platform-specific tool names appear. Everything above is shared with the Codex tree.

- **Skill directory:** `~/.claude/skills/client-feedback-triage/`. Every `scripts/...` path above resolves under it, e.g. `~/.claude/skills/client-feedback-triage/scripts/triage_read.py list txn`.
- **Client argument:** `$ARGUMENTS` (the text after `/client-feedback-triage`). Empty means "list and ask".
- **Run a script:** the `Bash` tool. The scripts are PEP 723 and self-run under `uv` (`/Users/georgewestbrook/.local/bin/uv`), so call them directly; no install step. Parse the JSON on stdout; branch on the exit code.
- **Ask the user** (client choice, pull-backs, debate decisions, the approval gate): the `AskUserQuestion` tool for a fixed choice; a plain question in the conversation for free-form debate. Approval must be an explicit answer.
- **Load a reference or the template:** the `Read` tool on the file under the skill directory.
- **Write and annotate the document:** the `Write` tool to create the file, the `Edit` tool to append a dated section or the write-result annotation.
- **Handoff:** do not invoke `/discovery` from this skill. The user runs it later, once per `will do` block, via the `Skill` tool → `skill: "discovery"` or by typing `/discovery`, pointing it at the block.
