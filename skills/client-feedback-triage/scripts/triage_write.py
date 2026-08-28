#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["psycopg[binary]"]
# ///
"""triage_write.py — the WRITE side of the client-feedback-triage skill.

Commands (one JSON document on stdout; failure envelope and exit codes in
`_creds.py`):

    apply <client> [--actor-email <email>] [--dry-run]     <- decisions payload on stdin
    delete-validation-artefact <client> <comment_id> [--dry-run]

What `apply` writes, per record in the deduplicated write set, inside ONE
transaction per record:

    1. INSERT <schema>.feedback_comments (feedback_id, user_id, content) RETURNING id
    2. INSERT <schema>.user_activity_events
              (actor_user_id, action_type, entity_type, entity_id, metadata)
       with action_type 'comment.created', entity_type 'feedback_comment',
       entity_id = the COMMENT id returned by statement 1 (not the feedback id),
       metadata {"feedback_id": "<record id>"}

The comment text is always `COMMENT_TEMPLATE` with the payload date formatted
in — a client-visible, model-free literal. No other text ever reaches a comment.

What `apply` never does: it never writes the `feedback` table, never writes a
status of any kind, never writes for a record that appears only in
`not this round` buckets, and never reads the payload's `actor` display name.

Write allow-list (enforced by the guard before every statement):
`<schema>.feedback_comments`, `<schema>.user_activity_events`. The only reads are
the actor lookup on `<schema>.user_profiles` and the same-date skip check on
`<schema>.feedback_comments`.

`delete-validation-artefact` is the skill's ONLY deletion path. It exists for the
live-validation chunk (C7) to remove its own artefact and is not part of the
triage flow.
"""

from __future__ import annotations

import datetime as _dt
import json
import re
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

# The one comment template. The dash is U+2014 (em dash). Only the date is ever
# formatted in. This literal is also recorded in references/write-back.md.
COMMENT_TEMPLATE = "Triaged {date} — scheduled"

ACTION_TYPE = "comment.created"
ENTITY_TYPE = "feedback_comment"

DECISIONS = ("will do", "not this round")
WRITE_DECISION = "will do"
TARGETS = ("agent", "frontend", "both")

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Placeholders shown in --dry-run params for values only the database can supply.
_DRY_ACTOR_ID = "<actor user_profiles.id>"
_DRY_COMMENT_ID = "<comment id RETURNING from the preceding INSERT>"

# --- SQL. Braces are psycopg.sql placeholders filled by the guard from the
# declared table map; `%s` are value parameters.

_ACTOR_SQL = "SELECT id FROM {user_profiles} WHERE email = %s"

_SAME_DATE_SQL = "SELECT 1 AS present FROM {feedback_comments} WHERE feedback_id = %s AND content = %s LIMIT 1"

_INSERT_COMMENT_SQL = (
    "INSERT INTO {feedback_comments} (feedback_id, user_id, content) VALUES (%s, %s, %s) RETURNING id"
)

_INSERT_AUDIT_SQL = (
    "INSERT INTO {user_activity_events} (actor_user_id, action_type, entity_type, entity_id, metadata) "
    "VALUES (%s, %s, %s, %s, %s::jsonb) RETURNING id"
)

_COMMENT_CONTENT_SQL = "SELECT content FROM {feedback_comments} WHERE id = %s"
_DELETE_AUDIT_SQL = "DELETE FROM {user_activity_events} WHERE entity_type = %s AND entity_id = %s"
_DELETE_COMMENT_SQL = "DELETE FROM {feedback_comments} WHERE id = %s"


def comment_text(date: str) -> str:
    """The exact client-visible comment for a triage date."""
    return COMMENT_TEMPLATE.format(date=date)


# ---------------------------------------------------------------------------
# Payload validation and the deduplicated write set
# ---------------------------------------------------------------------------


def _malformed(message: str) -> creds.TriageError:
    return creds.TriageError("MALFORMED_PAYLOAD", message)


def _canonical_uuid(value: Any, where: str) -> str:
    if not isinstance(value, str):
        raise _malformed(f"{where}: record id must be a UUID string, got {type(value).__name__}")
    try:
        return str(uuid.UUID(value))
    except ValueError as exc:
        raise _malformed(f"{where}: record id {value!r} is not a UUID") from exc


def validate_payload(payload: Any) -> tuple[str, list[dict[str, Any]]]:
    """Check the decisions payload against the Architecture contract.

    Returns `(date, buckets)` with every `record_ids` entry in canonical UUID
    form. Any violation raises MALFORMED_PAYLOAD (exit 6). The `actor` field is
    display-only and is deliberately not read here or anywhere else.
    """
    if not isinstance(payload, dict):
        raise _malformed("payload must be a JSON object")

    date = payload.get("date")
    if not isinstance(date, str) or not _DATE_RE.match(date):
        raise _malformed("'date' must be a string in YYYY-MM-DD form")
    try:
        _dt.date.fromisoformat(date)
    except ValueError as exc:
        raise _malformed(f"'date' {date!r} is not a calendar date") from exc

    buckets = payload.get("buckets")
    if not isinstance(buckets, list) or not buckets:
        raise _malformed("'buckets' must be a non-empty list")

    seen_names: set[str] = set()
    clean: list[dict[str, Any]] = []
    for index, bucket in enumerate(buckets):
        where = f"buckets[{index}]"
        if not isinstance(bucket, dict):
            raise _malformed(f"{where}: bucket must be an object")

        name = bucket.get("name")
        if not isinstance(name, str) or not name.strip():
            raise _malformed(f"{where}: 'name' must be a non-empty string")
        if name in seen_names:
            raise _malformed(f"{where}: bucket name {name!r} is not unique within the payload")
        seen_names.add(name)

        decision = bucket.get("decision")
        if decision not in DECISIONS:
            raise _malformed(f"{where} ({name!r}): 'decision' must be one of {list(DECISIONS)}, got {decision!r}")

        rationale = bucket.get("rationale")
        if not isinstance(rationale, str):
            raise _malformed(f"{where} ({name!r}): 'rationale' must be a string")

        target = bucket.get("target")
        if target not in TARGETS:
            raise _malformed(f"{where} ({name!r}): 'target' must be one of {list(TARGETS)}, got {target!r}")

        record_ids = bucket.get("record_ids")
        if not isinstance(record_ids, list):
            raise _malformed(f"{where} ({name!r}): 'record_ids' must be a list of UUID strings")
        canonical = [_canonical_uuid(rid, f"{where} ({name!r}).record_ids[{i}]") for i, rid in enumerate(record_ids)]

        clean.append(
            {
                "name": name,
                "decision": decision,
                "rationale": rationale,
                "target": target,
                "record_ids": canonical,
            }
        )
    return date, clean


def write_set(buckets: list[dict[str, Any]]) -> list[str]:
    """The deduplicated write set, per R9's membership table, computed BEFORE
    the first statement:

    - a record in one or more `will do` buckets is in the set exactly once,
      however many buckets name it (WE6b), and whether or not it also sits in a
      `not this round` bucket (WE6a);
    - a record only in `not this round` buckets is not in the set (WE15).

    First-seen order is preserved.
    """
    ordered: list[str] = []
    seen: set[str] = set()
    for bucket in buckets:
        if bucket["decision"] != WRITE_DECISION:
            continue
        for record_id in bucket["record_ids"]:
            if record_id not in seen:
                seen.add(record_id)
                ordered.append(record_id)
    return ordered


def _read_payload_from_stdin() -> Any:
    raw = sys.stdin.read()
    if not raw.strip():
        raise _malformed("no payload on stdin (expected the decisions JSON object)")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise _malformed(f"stdin is not valid JSON: {exc}") from exc


def _audit_metadata(record_id: str) -> str:
    return json.dumps({"feedback_id": record_id})


# ---------------------------------------------------------------------------
# apply
# ---------------------------------------------------------------------------


def _render_dry_run(admin: creds.GuardedConnection, records: list[str], text: str, actor_email: str) -> None:
    """Render, without issuing, what `apply` would do. `statements` holds the
    write pair per record in the set — an empty list when the set is empty
    (WE15). The reads that guard the writes (actor lookup, same-date check) are
    listed separately under `preconditions`."""
    preconditions: list[dict[str, Any]] = []
    if records:
        admin.execute(_ACTOR_SQL, [actor_email], tables={"user_profiles": "user_profiles"}, mode="read")
        preconditions.extend(admin.statements)
        admin.statements.clear()
    for record_id in records:
        admin.execute(_SAME_DATE_SQL, [record_id, text], tables={"feedback_comments": "feedback_comments"}, mode="read")
        preconditions.extend(admin.statements)
        admin.statements.clear()
    for record_id in records:
        admin.execute(
            _INSERT_COMMENT_SQL,
            [record_id, _DRY_ACTOR_ID, text],
            tables={"feedback_comments": "feedback_comments"},
            mode="write",
        )
        admin.execute(
            _INSERT_AUDIT_SQL,
            [_DRY_ACTOR_ID, ACTION_TYPE, ENTITY_TYPE, _DRY_COMMENT_ID, _audit_metadata(record_id)],
            tables={"user_activity_events": "user_activity_events"},
            mode="write",
        )
    creds.ok(
        {
            "dry_run": True,
            "statements": list(admin.statements),
            "preconditions": preconditions,
            "write_set": records,
            "actor_email": actor_email,
            "comment_text": text,
        }
    )


def cmd_apply(args: Any) -> None:
    client = creds.resolve_client(args.client)
    # Registry preconditions first (EC11 / EC12), before the payload is read:
    # a "not yet configured" client fails the same way whatever stdin holds.
    creds.read_credential_file(client.admin, client_key=client.key, role="admin")
    registry = creds.load_registry()
    actor_email = args.actor_email or creds.default_actor_email(registry)

    date, buckets = validate_payload(_read_payload_from_stdin())
    text = comment_text(date)
    records = write_set(buckets)  # deduplicated before the first statement (R9)

    with creds.connect_admin(client, dry_run=args.dry_run) as admin:
        if args.dry_run:
            _render_dry_run(admin, records, text, actor_email)
            return

        # An empty write set issues NO statement of any kind (WE15): not even
        # the actor lookup.
        if not records:
            creds.ok({"written": [], "skipped": [], "comment_ids": {}})
            return

        # EC13: the actor must exist BEFORE any write.
        actor_row = admin.execute(
            _ACTOR_SQL, [actor_email], tables={"user_profiles": "user_profiles"}, mode="read"
        ).fetchone()
        if actor_row is None:
            raise creds.TriageError(
                "ACTOR_NOT_FOUND",
                f"no user_profiles row in schema {client.schema!r} for the actor email {actor_email!r}; "
                f"pass --actor-email or fix default_actor_email in config.json",
                actor_email=actor_email,
            )
        actor_id = actor_row["id"]

        written: list[str] = []
        skipped: list[str] = []
        comment_ids: dict[str, str] = {}
        for position, record_id in enumerate(records):
            try:
                with admin.transaction():
                    # R10 same-date skip: the exact template text for this date
                    # already present means a previous run landed this record.
                    present = admin.execute(
                        _SAME_DATE_SQL,
                        [record_id, text],
                        tables={"feedback_comments": "feedback_comments"},
                        mode="read",
                    ).fetchone()
                    if present is not None:
                        skipped.append(record_id)
                        continue
                    comment_row = admin.execute(
                        _INSERT_COMMENT_SQL,
                        [record_id, actor_id, text],
                        tables={"feedback_comments": "feedback_comments"},
                        mode="write",
                    ).fetchone()
                    if comment_row is None:
                        raise RuntimeError("comment insert returned no id")
                    comment_id = comment_row["id"]
                    admin.execute(
                        _INSERT_AUDIT_SQL,
                        [actor_id, ACTION_TYPE, ENTITY_TYPE, comment_id, _audit_metadata(record_id)],
                        tables={"user_activity_events": "user_activity_events"},
                        mode="write",
                    )
                # Committed on leaving the `with` block.
                written.append(record_id)
                comment_ids[record_id] = str(comment_id)
            except Exception as exc:  # noqa: BLE001 - EC14/EC15: stop and report
                # The transaction context already rolled this record back.
                unwritten = records[position:]
                cause = f"{exc.error}: {exc.message}" if isinstance(exc, creds.TriageError) else f"{type(exc).__name__}: {exc}"
                raise creds.TriageError(
                    "PARTIAL_WRITE",
                    f"write stopped at record {record_id} ({len(written)} written, "
                    f"{len(unwritten)} unwritten): {cause}",
                    written=written,
                    unwritten=unwritten,
                    skipped=skipped,
                    comment_ids=comment_ids,
                ) from exc

    creds.ok({"written": written, "skipped": skipped, "comment_ids": comment_ids})


# ---------------------------------------------------------------------------
# delete-validation-artefact
# ---------------------------------------------------------------------------


def cmd_delete_validation_artefact(args: Any) -> None:
    client = creds.resolve_client(args.client)
    try:
        comment_id = str(uuid.UUID(args.comment_id))
    except ValueError as exc:
        raise _malformed(f"comment_id must be a UUID, got {args.comment_id!r}") from exc

    with creds.connect_admin(client, dry_run=args.dry_run) as admin:
        if args.dry_run:
            admin.execute(_COMMENT_CONTENT_SQL, [comment_id], tables={"feedback_comments": "feedback_comments"}, mode="read")
            preconditions = list(admin.statements)
            admin.statements.clear()
            admin.execute(
                _DELETE_AUDIT_SQL,
                [ENTITY_TYPE, comment_id],
                tables={"user_activity_events": "user_activity_events"},
                mode="write",
            )
            admin.execute(_DELETE_COMMENT_SQL, [comment_id], tables={"feedback_comments": "feedback_comments"}, mode="write")
            creds.ok({"dry_run": True, "statements": list(admin.statements), "preconditions": preconditions})
            return

        row = admin.execute(
            _COMMENT_CONTENT_SQL, [comment_id], tables={"feedback_comments": "feedback_comments"}, mode="read"
        ).fetchone()
        if row is None:
            creds.ok(
                {
                    "comment_id": comment_id,
                    "found": False,
                    "deleted": {"user_activity_events": 0, "feedback_comments": 0},
                }
            )
            return
        # Safety: this path deletes only a comment this skill wrote. A comment
        # that does not carry the template prefix is a person's comment.
        if not str(row["content"]).startswith(COMMENT_TEMPLATE.split("{date}")[0]):
            raise _malformed(
                f"comment {comment_id} is not a triage comment (content does not start with the template); refusing to delete"
            )

        with admin.transaction():
            audit_deleted = admin.execute(
                _DELETE_AUDIT_SQL,
                [ENTITY_TYPE, comment_id],
                tables={"user_activity_events": "user_activity_events"},
                mode="write",
            ).rowcount
            comment_deleted = admin.execute(
                _DELETE_COMMENT_SQL, [comment_id], tables={"feedback_comments": "feedback_comments"}, mode="write"
            ).rowcount

    creds.ok(
        {
            "comment_id": comment_id,
            "found": True,
            "deleted": {"user_activity_events": audit_deleted, "feedback_comments": comment_deleted},
        }
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = creds.ArgParser(
        prog="triage_write.py",
        description="Write side of client-feedback-triage: mark selected records with a templated "
        "comment plus an audit row. Emits one JSON document on stdout.",
    )
    # `required=True`: a missing subcommand is a usage error -> UNEXPECTED
    # envelope, exit 1 (via ArgParser.error). `--help` still exits 0.
    sub = parser.add_subparsers(dest="command", required=True)

    p_apply = sub.add_parser("apply", help="apply the decisions payload from stdin")
    p_apply.add_argument("client")
    p_apply.add_argument("--actor-email", dest="actor_email", default=None, help="overrides default_actor_email")
    p_apply.add_argument("--dry-run", action="store_true", help="validate, dedupe, render the statements, issue nothing")

    p_del = sub.add_parser(
        "delete-validation-artefact",
        help="delete one triage comment and its audit row (validation clean-up only)",
    )
    p_del.add_argument("client")
    p_del.add_argument("comment_id")
    p_del.add_argument("--dry-run", action="store_true", help="render the statements, issue nothing")

    args = parser.parse_args()
    handlers = {
        "apply": cmd_apply,
        "delete-validation-artefact": cmd_delete_validation_artefact,
    }
    handlers[args.command](args)


if __name__ == "__main__":
    creds.run_main(main)
