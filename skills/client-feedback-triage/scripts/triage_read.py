#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["psycopg[binary]"]
# ///
"""triage_read.py — the READ side of the client-feedback-triage skill.

Commands (all output is one JSON document on stdout; see `_creds.py` for the
failure envelope and the exit-code map):

    clients                                   registry listing, no connection
    list <client> [--dry-run]                 open feedback records for a client
    detail <client> <record_id> [--dry-run]   one record plus its comment thread
    transcript <client> <conversation_id> [--dry-run]
                                              a conversation from the agent database

This script performs no write of any kind. Every statement goes through the
guarded executor in `_creds.py`, which checks the declared tables against the
connection's READ allow-list before execution:

    admin : <schema>.feedback, <schema>.feedback_comments,
            <schema>.user_activity_events, <schema>.user_profiles
    agent : public.conversations, public.messages

`--dry-run` renders every statement the command would issue, opens no
connection, and emits `{"ok": true, "dry_run": true, "statements": [...]}`.

`conversation_key` / `conversation_keys` / `already_scheduled` /
`prior_triage_comments` are derived HERE, not in the skill body, so the grouping
rule and the already-scheduled rule live in one place (spec: Architecture ->
Script I/O contracts, `list`).
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path
from typing import Any

# `_creds.py` lives beside this file in both skill trees. No bytecode cache:
# a `scripts/__pycache__/` would break the byte-identical `diff -r scripts/`
# between the two trees.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _creds as creds  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# A record is "already scheduled" when it carries a comment starting with this
# prefix, of ANY date (R2). The write side owns the full template.
TRIAGE_COMMENT_PREFIX = "Triaged "

# Lane A item types: these carry an item-level `conversation_id`.
LANE_A_TYPES = frozenset({"agent-message", "conversation"})

# Most recent N messages per transcript (R5, EC20).
TRANSCRIPT_LIMIT = 200

# The `feedback` columns the `list`/`detail` record object carries, verbatim.
# `prior_triage_comments` is aggregated from the LEFT JOIN on feedback_comments.
# Braces in this text are psycopg.sql placeholders, filled by the guard from
# the declared table map — so no literal `{}` may appear in the SQL itself.
_RECORD_SELECT = """
SELECT f.id, f.route, f.page_url, f.submitted_by, f.submitted_by_name, f.origin,
       f.created_at, f.screenshot_url, f.component_ids, f.app_state, f.feedback_items,
       COALESCE(
         array_agg(c.content ORDER BY c.created_at, c.id) FILTER (WHERE c.id IS NOT NULL),
         ARRAY[]::text[]
       ) AS prior_triage_comments
FROM {feedback} f
LEFT JOIN {feedback_comments} c
       ON c.feedback_id = f.id AND starts_with(c.content, %s)
"""

# The ONLY place the panel's status column is filtered: open records are the
# ones at 'New'. Ordered oldest first, id as a deterministic tiebreaker.
_LIST_SQL = _RECORD_SELECT + """
WHERE f.review_status = 'New'
GROUP BY f.id
ORDER BY f.created_at ASC, f.id ASC
"""

# `detail` fetches by id and applies no status filter.
_DETAIL_RECORD_SQL = _RECORD_SELECT + """
WHERE f.id = %s
GROUP BY f.id
"""

_DETAIL_COMMENTS_SQL = """
SELECT c.id, c.user_id, p.full_name AS author_name, c.content, c.created_at
FROM {feedback_comments} c
LEFT JOIN {user_profiles} p ON p.id = c.user_id
WHERE c.feedback_id = %s
ORDER BY c.created_at ASC, c.id ASC
"""

_CONVERSATION_EXISTS_SQL = "SELECT id FROM {conversations} WHERE id = %s"
_CONVERSATION_EXISTS_TENANT_SQL = "SELECT id FROM {conversations} WHERE id = %s AND tenant_id = %s"
# One statement for both the page and the total: `count(*) OVER ()` is computed
# before LIMIT applies, so `total_messages` and the rows come from the same
# snapshot. Most recent first at the database, reversed in Python so the output
# reads forwards (EC20). `id` breaks ties on equal timestamps.
_MESSAGES_SQL = """
SELECT id, role, content, content_blocks, tool_calls, created_at,
       count(*) OVER () AS total_messages
FROM {messages}
WHERE conversation_id = %s
ORDER BY created_at DESC, id DESC
LIMIT %s
"""


# ---------------------------------------------------------------------------
# Derivations (the grouping rule lives here)
# ---------------------------------------------------------------------------


def conversation_keys(app_state: Any, feedback_items: Any) -> list[str]:
    """Every Lane A bucket a record joins (R4, EC23), mirroring the panel's
    `conversationKey()` order (`feedback-rows.ts:30`):

    1. `app_state.conversation_id` when it is a non-empty string -> that alone.
       It carries the conversation the submission was MADE AGAINST; reading
       the item first could thread the record into a chat the user switched
       to before the POST landed.
    2. Otherwise every distinct non-empty item-level `conversation_id` on an
       `agent-message` / `conversation` item, in item order.
    3. Otherwise `[]` (the shared "unthreaded" bucket when Lane A items exist).
    """
    if isinstance(app_state, dict):
        from_app_state = app_state.get("conversation_id")
        if isinstance(from_app_state, str) and from_app_state:
            return [from_app_state]
    keys: list[str] = []
    for item in feedback_items or []:
        if not isinstance(item, dict) or item.get("type") not in LANE_A_TYPES:
            continue
        item_key = item.get("conversation_id")
        if isinstance(item_key, str) and item_key and item_key not in keys:
            keys.append(item_key)
    return keys


def shape_record(row: dict[str, Any]) -> dict[str, Any]:
    """The `list`/`detail` record object. `app_state` and `feedback_items` are
    emitted verbatim from JSONB (a null `app_state` stays `null`; a missing
    `conversation_id` key stays missing — EC3). Nothing is renamed."""
    feedback_items = row["feedback_items"] if row["feedback_items"] is not None else []
    keys = conversation_keys(row["app_state"], feedback_items)
    prior = list(row.get("prior_triage_comments") or [])
    return {
        "id": row["id"],
        "route": row["route"],
        "page_url": row["page_url"],
        "submitted_by": row["submitted_by"],
        "submitted_by_name": row["submitted_by_name"],
        "origin": row["origin"],
        "created_at": row["created_at"],
        "screenshot_url": row["screenshot_url"],
        "component_ids": list(row["component_ids"]) if row["component_ids"] is not None else [],
        "app_state": row["app_state"],
        "feedback_items": feedback_items,
        "conversation_key": keys[0] if keys else None,
        "conversation_keys": keys,
        "already_scheduled": bool(prior),
        "prior_triage_comments": prior,
    }


def _require_uuid(value: str, what: str) -> str:
    """Validate an id argument BEFORE any statement (Drift 13): a non-UUID
    would otherwise reach Postgres as a type error. Returns the canonical form."""
    try:
        return str(uuid.UUID(value))
    except (ValueError, AttributeError, TypeError) as exc:
        raise creds.TriageError(
            "MALFORMED_PAYLOAD", f"{what} must be a UUID, got {value!r}"
        ) from exc


def _dry_run_result(*connections: creds.GuardedConnection) -> None:
    statements: list[dict[str, Any]] = []
    for connection in connections:
        statements.extend(connection.statements)
    creds.ok({"dry_run": True, "statements": statements})


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_clients(_args: Any) -> None:
    """Registry listing. Reads config.json only; opens no connection."""
    registry = creds.load_registry()
    creds.ok({"default_actor": creds.default_actor(registry), "clients": creds.list_clients(registry)})


def cmd_list(args: Any) -> None:
    client = creds.resolve_client(args.client)
    with creds.connect_admin(client, dry_run=args.dry_run) as admin:
        cur = admin.execute(
            _LIST_SQL,
            [TRIAGE_COMMENT_PREFIX],
            tables={"feedback": "feedback", "feedback_comments": "feedback_comments"},
            mode="read",
        )
        if args.dry_run:
            _dry_run_result(admin)
            return
        records = [shape_record(row) for row in cur.fetchall()]
    # An empty queue is a success (EC9): count 0, records [], exit 0.
    creds.ok(
        {
            "client": client.key,
            "schema": client.schema,
            "count": len(records),
            "records": records,
        }
    )


def cmd_detail(args: Any) -> None:
    client = creds.resolve_client(args.client)
    record_id = _require_uuid(args.record_id, "record_id")
    with creds.connect_admin(client, dry_run=args.dry_run) as admin:
        cur = admin.execute(
            _DETAIL_RECORD_SQL,
            [TRIAGE_COMMENT_PREFIX, record_id],
            tables={"feedback": "feedback", "feedback_comments": "feedback_comments"},
            mode="read",
        )
        if args.dry_run:
            admin.execute(
                _DETAIL_COMMENTS_SQL,
                [record_id],
                tables={"feedback_comments": "feedback_comments", "user_profiles": "user_profiles"},
                mode="read",
            )
            _dry_run_result(admin)
            return
        row = cur.fetchone()
        if row is None:
            # An unknown id is not an error (Drift 11).
            creds.ok({"found": False, "record": None, "comments": []})
            return
        record = shape_record(row)
        comments_cur = admin.execute(
            _DETAIL_COMMENTS_SQL,
            [record_id],
            tables={"feedback_comments": "feedback_comments", "user_profiles": "user_profiles"},
            mode="read",
        )
        comments = [
            {
                "id": c["id"],
                "user_id": c["user_id"],
                "author_name": c["author_name"],
                "content": c["content"],
                "created_at": c["created_at"],
            }
            for c in comments_cur.fetchall()
        ]
    creds.ok({"found": True, "record": record, "comments": comments})


def cmd_transcript(args: Any) -> None:
    client = creds.resolve_client(args.client)
    conversation_id = _require_uuid(args.conversation_id, "conversation_id")
    # `connect_agent` refuses with CLIENT_NOT_CONFIGURED when the registry has
    # `agent_database: null` (EC8, Drift 10) — the skill body must not call
    # `transcript` for such a client, and this script refuses if it does.
    tenant_id = client.agent.tenant_id if client.agent is not None else None
    with creds.connect_agent(client, dry_run=args.dry_run) as agent:
        if tenant_id is not None:
            exists_cur = agent.execute(
                _CONVERSATION_EXISTS_TENANT_SQL,
                [conversation_id, tenant_id],
                tables={"conversations": "conversations"},
                mode="read",
            )
        else:
            exists_cur = agent.execute(
                _CONVERSATION_EXISTS_SQL,
                [conversation_id],
                tables={"conversations": "conversations"},
                mode="read",
            )
        if args.dry_run:
            agent.execute(
                _MESSAGES_SQL, [conversation_id, TRANSCRIPT_LIMIT], tables={"messages": "messages"}, mode="read"
            )
            _dry_run_result(agent)
            return
        if exists_cur.fetchone() is None:
            # EC5: a degradation, not an error.
            creds.ok(
                {
                    "conversation_id": conversation_id,
                    "found": False,
                    "total_messages": 0,
                    "truncated": False,
                    "messages": [],
                }
            )
            return
        rows = agent.execute(
            _MESSAGES_SQL, [conversation_id, TRANSCRIPT_LIMIT], tables={"messages": "messages"}, mode="read"
        ).fetchall()
        # A conversation with no messages yields no rows, hence no window count.
        total = int(rows[0]["total_messages"]) if rows else 0
    # Fetched newest-first (the most recent N); reversed so the thread reads
    # forwards in created_at ascending order (EC20).
    rows.reverse()
    messages = [
        {
            "id": m["id"],
            "role": m["role"],
            "content": m["content"],
            "content_blocks": m["content_blocks"],
            "tool_calls": m["tool_calls"],
            "created_at": m["created_at"],
        }
        for m in rows
    ]
    creds.ok(
        {
            "conversation_id": conversation_id,
            "found": True,
            "total_messages": total,
            "truncated": total > TRANSCRIPT_LIMIT,
            "messages": messages,
        }
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = creds.ArgParser(
        prog="triage_read.py",
        description="Read-only access to a client's open feedback and agent transcripts. "
        "Emits one JSON document on stdout; never writes.",
    )
    # `required=True`: a missing subcommand is a usage error -> UNEXPECTED
    # envelope, exit 1 (via ArgParser.error). `--help` still exits 0.
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("clients", help="list the registry entries (no connection)")

    p_list = sub.add_parser("list", help="open feedback records for a client, oldest first")
    p_list.add_argument("client")
    p_list.add_argument("--dry-run", action="store_true", help="render the statements, issue nothing")

    p_detail = sub.add_parser("detail", help="one record by id, with its full comment thread")
    p_detail.add_argument("client")
    p_detail.add_argument("record_id")
    p_detail.add_argument("--dry-run", action="store_true", help="render the statements, issue nothing")

    p_tx = sub.add_parser("transcript", help="a conversation's messages from the agent database")
    p_tx.add_argument("client")
    p_tx.add_argument("conversation_id")
    p_tx.add_argument("--dry-run", action="store_true", help="render the statements, issue nothing")

    args = parser.parse_args()
    handlers = {
        "clients": cmd_clients,
        "list": cmd_list,
        "detail": cmd_detail,
        "transcript": cmd_transcript,
    }
    handlers[args.command](args)


if __name__ == "__main__":
    creds.run_main(main)
