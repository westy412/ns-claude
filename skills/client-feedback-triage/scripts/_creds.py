#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["psycopg[binary]"]
# ///
"""Shared module for the client-feedback-triage scripts.

This module owns four things and nothing else:

1. The client registry — loading `config.json`, resolving a client argument to a
   `ClientConfig` (case-insensitive exact key match, no prefix match), and the
   `clients` listing rows.
2. Credential loading — parsing the two supported credential formats
   (`hcl-env-vars`, `dotenv`) to the same five keys, and telling a `null` registry
   path (client not configured) apart from a path that is absent on disk
   (credentials missing).
3. The guarded connection — `connect_admin()` / `connect_agent()` return a
   `GuardedConnection` that carries a read allow-list and a write allow-list of
   fully-qualified table names. Every statement runs through
   `GuardedConnection.execute()`, where the caller DECLARES the tables it touches
   and the mode. The guard refuses (SCHEMA_VIOLATION) before execution when any
   declared table is outside the list for that mode. The SQL identifiers are
   built from the same declaration, so the declaration and the statement cannot
   drift.
4. The failure envelope — `fail()`, `ok()`, `run_main()`, and the exit-code map.

`triage_read.py` and `triage_write.py` import this module by inserting their own
directory on `sys.path`. The PEP 723 header is present so the module can also be
run directly for a credential-file check that prints key names only, never values.

Credential VALUES are never printed, logged, or embedded in an error message. Error
messages name paths and key names only.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as _dt
import decimal
import json
import re
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator, Mapping, NoReturn, Sequence

import psycopg
from psycopg import sql
from psycopg.errors import QueryCanceled
from psycopg.rows import dict_row

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# `config.json` sits one level above `scripts/` in BOTH skill trees
# (~/.claude/skills/... and ~/.codex/skills/...), so resolve it relative to
# this file rather than to a hard-coded tree.
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"

CONNECT_TIMEOUT_SECONDS = 10
STATEMENT_TIMEOUT_MS = 30_000
APPLICATION_NAME = "client-feedback-triage"

CREDENTIAL_KEYS: tuple[str, ...] = (
    "DATABASE_HOST",
    "DATABASE_PORT",
    "DATABASE_NAME",
    "DATABASE_USERNAME",
    "DATABASE_PASSWORD",
)
SUPPORTED_FORMATS: tuple[str, ...] = ("hcl-env-vars", "dotenv")

# The admin connection reads these tables inside the resolved client schema...
ADMIN_READ_TABLES: tuple[str, ...] = (
    "feedback",
    "feedback_comments",
    "user_activity_events",
    "user_profiles",
)
# ...and writes only these two.
ADMIN_WRITE_TABLES: tuple[str, ...] = ("feedback_comments", "user_activity_events")

# The agent database (nova-kernel) keeps its tables in `public` on a DIFFERENT
# host. It is read-only to this skill and gets no search_path.
AGENT_SCHEMA = "public"
AGENT_READ_TABLES: tuple[str, ...] = ("conversations", "messages")

# Complete exit-code map (spec: Architecture -> "Exit codes and error strings").
EXIT_CODES: Mapping[str, int] = {
    "UNEXPECTED": 1,
    "CLIENT_NOT_CONFIGURED": 2,
    "CREDENTIALS_MISSING": 2,
    "UNKNOWN_CLIENT": 2,
    "ADMIN_DB_UNREACHABLE": 3,
    "ADMIN_DB_TIMEOUT": 3,
    "AGENT_DB_UNREACHABLE": 4,
    "PARTIAL_WRITE": 5,
    "ACTOR_NOT_FOUND": 6,
    "SCHEMA_VIOLATION": 6,
    "MALFORMED_PAYLOAD": 6,
}

# Per-connection error strings for connect failures and statement timeouts.
# The agent side has no distinct timeout code: the failure policy treats
# "unreachable or timing out" as one condition (EC4).
_UNREACHABLE_ERROR = {"admin": "ADMIN_DB_UNREACHABLE", "agent": "AGENT_DB_UNREACHABLE"}
_TIMEOUT_ERROR = {"admin": "ADMIN_DB_TIMEOUT", "agent": "AGENT_DB_UNREACHABLE"}

_SCHEMA_NAME_RE = re.compile(r"^[a-z_][a-z0-9_]*$")


# ---------------------------------------------------------------------------
# Failure envelope
# ---------------------------------------------------------------------------


class TriageError(Exception):
    """A failure that maps to one row of the exit-code table.

    `error` is the envelope string, `message` the human-readable text, and
    `extra` any additional envelope fields (`apply` adds `written`/`unwritten`).
    """

    def __init__(self, error: str, message: str, **extra: Any) -> None:
        if error not in EXIT_CODES:
            raise ValueError(f"unknown error string {error!r}")
        super().__init__(message)
        self.error = error
        self.message = message
        self.extra = extra

    @property
    def exit_code(self) -> int:
        return EXIT_CODES[self.error]


class SchemaViolation(TriageError):
    """Raised by the guard BEFORE a statement executes (EC16)."""

    def __init__(self, message: str) -> None:
        super().__init__("SCHEMA_VIOLATION", message)


def _json_default(value: Any) -> Any:
    """Serialise the database types the scripts emit: datetime, UUID, Decimal."""
    if isinstance(value, (_dt.datetime, _dt.date, _dt.time)):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, decimal.Decimal):
        return float(value)
    if isinstance(value, (set, frozenset, tuple)):
        return list(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (bytes, memoryview)):
        return bytes(value).decode("utf-8", errors="replace")
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def dumps(payload: Any) -> str:
    """JSON-encode a payload with the shared serialiser. `ensure_ascii=False`
    keeps the em dash in `Triaged YYYY-MM-DD — scheduled` as a literal."""
    return json.dumps(payload, default=_json_default, ensure_ascii=False)


def emit(payload: Mapping[str, Any]) -> None:
    """Print one JSON document to stdout. Every script emits exactly one."""
    sys.stdout.write(dumps(payload))
    sys.stdout.write("\n")
    sys.stdout.flush()


def ok(payload: Mapping[str, Any] | None = None) -> None:
    """Emit the success envelope `{"ok": true, ...payload}`. Does not exit."""
    body: dict[str, Any] = {"ok": True}
    if payload:
        body.update(payload)
    emit(body)


def fail(error: str, message: str, **extra: Any) -> NoReturn:
    """Emit the failure envelope to STDOUT and exit with the mapped code."""
    body: dict[str, Any] = {"ok": False, "error": error, "message": message}
    body.update(extra)
    emit(body)
    sys.exit(EXIT_CODES[error])


def run_main(main: Any) -> NoReturn:
    """Run a script's `main()` under the failure policy.

    - `TriageError` -> its envelope and exit code.
    - Anything else (including psycopg errors that escaped the caller's own
      handling, and KeyboardInterrupt) -> `UNEXPECTED`, exit 1. Never a bare
      traceback.
    - `SystemExit` passes through so `fail()` and `--help` keep their codes.
    """
    try:
        main()
    except TriageError as exc:
        fail(exc.error, exc.message, **exc.extra)
    except SystemExit:
        raise
    except BaseException as exc:  # noqa: BLE001 - the failure policy demands it
        fail("UNEXPECTED", f"{type(exc).__name__}: {exc}")
    sys.exit(0)


class ArgParser(argparse.ArgumentParser):
    """argparse that reports usage errors through the failure envelope.

    Stock argparse prints to stderr and exits 2, which collides with the
    configuration exit code. A usage error is a caller bug, so it maps to
    `UNEXPECTED` (exit 1). `--help` still prints help and exits 0.
    """

    def error(self, message: str) -> NoReturn:  # type: ignore[override]
        raise TriageError("UNEXPECTED", f"usage error: {message} ({self.format_usage().strip()})")


# ---------------------------------------------------------------------------
# Client registry
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CredentialSource:
    """One credential file entry from the registry.

    `path` is `None` when the registry has not been filled in for this client
    (EC11). `raw_path` keeps the `~` form for messages and listings.
    """

    raw_path: str | None
    format: str
    tenant_id: str | None = None

    @property
    def path(self) -> Path | None:
        return Path(self.raw_path).expanduser() if self.raw_path else None


@dataclass(frozen=True)
class ClientConfig:
    """A resolved registry entry."""

    key: str
    raw_root: str
    schema: str
    admin: CredentialSource
    agent: CredentialSource | None

    @property
    def root(self) -> Path:
        return Path(self.raw_root).expanduser()

    @property
    def configured(self) -> bool:
        """`False` when `admin_credentials.path` is null (EC11)."""
        return self.admin.raw_path is not None

    @property
    def has_agent_database(self) -> bool:
        return self.agent is not None

    def listing_row(self) -> dict[str, Any]:
        """The `clients` contract row."""
        return {
            "key": self.key,
            "schema": self.schema,
            "root": self.raw_root,
            "configured": self.configured,
            "agent_database": self.has_agent_database,
        }


def load_registry(path: Path = CONFIG_PATH) -> dict[str, Any]:
    """Load and shape-check `config.json`. Malformed registry -> UNEXPECTED."""
    if not path.exists():
        raise TriageError("UNEXPECTED", f"registry file not found: {path}")
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise TriageError("UNEXPECTED", f"registry file is not valid JSON: {path}: {exc}") from exc
    if not isinstance(registry, dict) or not isinstance(registry.get("clients"), dict):
        raise TriageError("UNEXPECTED", f"registry file must hold a 'clients' object: {path}")
    for required in ("default_actor_email", "default_actor_name"):
        if not isinstance(registry.get(required), str) or not registry[required].strip():
            raise TriageError("UNEXPECTED", f"registry file must hold a non-empty {required!r}: {path}")
    return registry


def _normalise_tenant_id(value: Any) -> str | None:
    """A null, empty, or whitespace-only `tenant_id` means "no tenant predicate".
    Anything else is used as the string the kernel stored (`varchar`)."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _client_from_entry(key: str, entry: Mapping[str, Any]) -> ClientConfig:
    def _require(name: str) -> Any:
        if name not in entry:
            raise TriageError("UNEXPECTED", f"registry entry {key!r} is missing {name!r}")
        return entry[name]

    schema = _require("schema")
    if not isinstance(schema, str) or not _SCHEMA_NAME_RE.match(schema):
        raise TriageError("UNEXPECTED", f"registry entry {key!r} has an invalid schema name")

    admin_raw = _require("admin_credentials")
    if not isinstance(admin_raw, Mapping):
        raise TriageError("UNEXPECTED", f"registry entry {key!r}: 'admin_credentials' must be an object")
    admin = CredentialSource(
        raw_path=admin_raw.get("path"),
        format=str(admin_raw.get("format", "hcl-env-vars")),
    )

    agent_raw = _require("agent_database")
    agent: CredentialSource | None
    if agent_raw is None:
        agent = None
    elif isinstance(agent_raw, Mapping):
        agent = CredentialSource(
            raw_path=agent_raw.get("path"),
            format=str(agent_raw.get("format", "dotenv")),
            tenant_id=_normalise_tenant_id(agent_raw.get("tenant_id")),
        )
    else:
        raise TriageError("UNEXPECTED", f"registry entry {key!r}: 'agent_database' must be an object or null")

    return ClientConfig(
        key=key,
        raw_root=str(_require("root")),
        schema=schema,
        admin=admin,
        agent=agent,
    )


def list_clients(registry: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    """The `clients` contract rows, in registry order. Opens no connection."""
    registry = registry or load_registry()
    return [_client_from_entry(k, v).listing_row() for k, v in registry["clients"].items()]


def resolve_client(arg: str, registry: Mapping[str, Any] | None = None) -> ClientConfig:
    """Resolve a client argument to its registry entry.

    Matching is case-insensitive against the EXACT key (WE2). There is no
    prefix or fuzzy matching (WE4): `totaljobs` does not match `total-jobs`.
    """
    registry = registry or load_registry()
    wanted = (arg or "").strip().casefold()
    if not wanted:
        raise TriageError("UNKNOWN_CLIENT", "no client given", known_clients=list(registry["clients"]))
    for key, entry in registry["clients"].items():
        if key.casefold() == wanted:
            return _client_from_entry(key, entry)
    raise TriageError(
        "UNKNOWN_CLIENT",
        f"client {arg!r} matched no registry key (exact, case-insensitive match only)",
        known_clients=list(registry["clients"]),
    )


def default_actor_email(registry: Mapping[str, Any] | None = None) -> str:
    registry = registry or load_registry()
    return registry["default_actor_email"]


def default_actor(registry: Mapping[str, Any] | None = None) -> dict[str, str]:
    """The `clients` contract's `default_actor {email, name}` object. `email` is
    what the write script resolves against `user_profiles.email`; `name` is the
    display name the skill body puts in the document and the payload's `actor`."""
    registry = registry or load_registry()
    return {"email": registry["default_actor_email"], "name": registry["default_actor_name"]}


# ---------------------------------------------------------------------------
# Credential parsing
# ---------------------------------------------------------------------------


def _unquote(value: str) -> str:
    """Strip one pair of matching surrounding quotes and unescape \\" and \\\\."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        inner = value[1:-1]
        if value[0] == '"':
            inner = inner.replace('\\"', '"').replace("\\\\", "\\")
        return inner
    return value


def parse_hcl_env_vars(text: str) -> dict[str, str]:
    """Parse the `env_vars = { KEY = "value" ... }` map from a Terraform tfvars file.

    Only lines INSIDE the `env_vars` block are read. Blank lines and `#` / `//`
    comment lines are ignored. Whitespace alignment around `=` is tolerated.
    Values are unquoted. The block ends at the first line that is exactly `}`.
    Returns every key found in the block, not only the five credential keys.
    """
    values: dict[str, str] = {}
    inside = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not inside:
            if re.match(r"^env_vars\s*=\s*\{\s*$", line):
                inside = True
            continue
        if line == "}":
            break
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        # A quoted value (with \" escapes) or a bare value; either may be
        # followed by an optional comma and an optional trailing `#` comment.
        match = re.match(
            r'^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*("(?:[^"\\]|\\.)*"|[^#]*?)\s*,?\s*(?:#.*)?$',
            line,
        )
        if not match:
            continue
        values[match.group(1)] = _unquote(match.group(2))
    return values


def parse_dotenv(text: str) -> dict[str, str]:
    """Parse flat `KEY=value` lines. Blank and `#` lines are ignored, an optional
    `export ` prefix is tolerated, and matching surrounding quotes are stripped.
    A ` #` after an unquoted value starts a trailing comment."""
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        key, sep, value = line.partition("=")
        key = key.strip()
        if not sep or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
            continue
        value = value.strip()
        if value and value[0] not in ("'", '"'):
            value = value.split(" #", 1)[0].rstrip()
        values[key] = _unquote(value)
    return values


_PARSERS = {"hcl-env-vars": parse_hcl_env_vars, "dotenv": parse_dotenv}


def read_credential_file(source: CredentialSource, *, client_key: str, role: str) -> dict[str, str]:
    """Read a credential file to the five `DATABASE_*` keys.

    Order of checks, all before any connection:
    1. `path` is null in the registry  -> CLIENT_NOT_CONFIGURED, naming the key (EC11).
    2. The file does not exist on disk -> CREDENTIALS_MISSING, naming the path (EC12).
    3. A required key is absent        -> CREDENTIALS_MISSING, naming path and key.

    Returns only the five keys. Values are never included in any message.
    """
    if source.raw_path is None:
        raise TriageError(
            "CLIENT_NOT_CONFIGURED",
            f"client {client_key!r} is not yet configured: {role} credential path is null in the registry",
        )
    if source.format not in _PARSERS:
        raise TriageError(
            "CLIENT_NOT_CONFIGURED",
            f"client {client_key!r}: {role} credential format {source.format!r} is not supported "
            f"(expected one of {list(SUPPORTED_FORMATS)})",
        )
    path = source.path
    assert path is not None
    if not path.is_file():
        raise TriageError(
            "CREDENTIALS_MISSING",
            f"client {client_key!r}: {role} credential file not found: {path}",
        )
    parsed = _PARSERS[source.format](path.read_text(encoding="utf-8"))
    missing = [k for k in CREDENTIAL_KEYS if not parsed.get(k)]
    if missing:
        raise TriageError(
            "CREDENTIALS_MISSING",
            f"client {client_key!r}: {role} credential file {path} is missing "
            f"{', '.join(missing)}",
        )
    return {k: parsed[k] for k in CREDENTIAL_KEYS}


def credential_key_report(source: CredentialSource) -> dict[str, Any]:
    """Which of the five keys a credential file has. NAMES ONLY, never values.
    Used by the direct-run `check` command for offline verification."""
    if source.raw_path is None:
        return {"path": None, "exists": False, "present": [], "absent": list(CREDENTIAL_KEYS)}
    path = source.path
    assert path is not None
    if not path.is_file():
        return {"path": str(path), "exists": False, "present": [], "absent": list(CREDENTIAL_KEYS)}
    parsed = _PARSERS.get(source.format, parse_dotenv)(path.read_text(encoding="utf-8"))
    present = [k for k in CREDENTIAL_KEYS if parsed.get(k)]
    return {
        "path": str(path),
        "format": source.format,
        "exists": True,
        "present": present,
        "absent": [k for k in CREDENTIAL_KEYS if k not in present],
    }


def _redact(message: str, creds: Mapping[str, str]) -> str:
    """Replace any credential value that appears in a driver message with its
    key name, so a psycopg error can be reported without leaking the value."""
    for key in CREDENTIAL_KEYS:
        value = creds.get(key, "")
        if value and len(value) >= 3:
            message = message.replace(value, f"<{key}>")
    return message


# ---------------------------------------------------------------------------
# Guarded connection
# ---------------------------------------------------------------------------


def split_qualified(name: str) -> tuple[str, str]:
    """`"txn.feedback"` -> `("txn", "feedback")`. Exactly one dot is required:
    every table this skill touches is fully qualified."""
    parts = name.split(".")
    if len(parts) != 2 or not all(parts):
        raise SchemaViolation(f"table name must be fully qualified as schema.table, got {name!r}")
    return parts[0], parts[1]


def table_ref(name: str) -> sql.Identifier:
    """`sql.Identifier(schema, table)` for a fully-qualified name."""
    schema, table = split_qualified(name)
    return sql.Identifier(schema, table)


class _DryRunCursor:
    """What `execute()` returns in dry-run mode: nothing was issued, so there
    are no rows. `rowcount` is -1, psycopg's value for "not executed". Real
    cursors return dict rows (see `_open`), so callers index by column name."""

    rowcount = -1
    description = None

    def fetchone(self) -> None:
        return None

    def fetchall(self) -> list[Any]:
        return []

    def __iter__(self) -> Iterator[Any]:
        return iter(())

    def close(self) -> None:
        return None


@dataclass
class GuardedConnection:
    """A psycopg connection plus the two allow-lists for one database.

    - `name` is `"admin"` or `"agent"`; it selects the error strings.
    - `schema` is the schema `qualify()` prefixes: the client schema for admin,
      `public` for agent.
    - `read_tables` / `write_tables` hold fully-qualified `schema.table` names.
    - `dry_run=True` means `conn` is `None`; `execute()` renders and records
      each statement into `statements` instead of issuing it.
    """

    name: str
    schema: str
    read_tables: frozenset[str]
    write_tables: frozenset[str]
    conn: psycopg.Connection[Any] | None = None
    dry_run: bool = False
    statements: list[dict[str, Any]] = field(default_factory=list)

    # -- naming helpers -----------------------------------------------------

    def qualify(self, table: str) -> str:
        """`"feedback"` -> `"<schema>.feedback"` for this connection."""
        if "." in table:
            return table
        return f"{self.schema}.{table}"

    def allowed(self, mode: str) -> frozenset[str]:
        if mode == "read":
            return self.read_tables
        if mode == "write":
            return self.write_tables
        raise SchemaViolation(f"mode must be 'read' or 'write', got {mode!r}")

    # -- the guard ----------------------------------------------------------

    def check(self, tables: Sequence[str], mode: str) -> list[str]:
        """Refuse BEFORE execution unless every declared table is on the list
        for `mode`. Returns the normalised fully-qualified names."""
        allowed = self.allowed(mode)
        if not tables:
            raise SchemaViolation("a statement must declare at least one table")
        qualified: list[str] = []
        for table in tables:
            name = self.qualify(table)
            split_qualified(name)  # validates the shape
            qualified.append(name)
        refused = [t for t in qualified if t not in allowed]
        if refused:
            raise SchemaViolation(
                f"{self.name} connection: {mode} of {', '.join(refused)} refused; "
                f"allowed for {mode}: {sorted(allowed) or '(none)'}"
            )
        return qualified

    def execute(
        self,
        template: str,
        params: Sequence[Any] | Mapping[str, Any] | None = None,
        *,
        tables: Mapping[str, str],
        mode: str,
        extra: Mapping[str, sql.Composable] | None = None,
    ) -> Any:
        """The ONLY way a statement reaches the database.

        `template` is SQL text with `{name}` placeholders for tables and `%s`
        placeholders for values. `tables` maps each placeholder name to the
        table it stands for — unqualified (`"feedback"`, qualified against this
        connection's schema) or fully qualified (`"public.feedback"`). The guard
        checks every declared table against the `mode` allow-list first, then
        the placeholders are filled with `sql.Identifier(schema, table)` built
        from the SAME declaration. `extra` supplies any non-table composables.

        Returns the cursor (or a `_DryRunCursor` in dry-run mode).
        """
        qualified = self.check(list(tables.values()), mode)
        identifiers = {
            placeholder: table_ref(self.qualify(table)) for placeholder, table in tables.items()
        }
        if extra:
            identifiers.update(extra)
        query = sql.SQL(template).format(**identifiers)

        if self.dry_run or self.conn is None:
            self.statements.append(
                {
                    "connection": self.name,
                    "mode": mode,
                    "tables": qualified,
                    "sql": query.as_string(self.conn),
                    "params": list(params) if isinstance(params, (list, tuple)) else (dict(params) if params else []),
                }
            )
            return _DryRunCursor()

        try:
            cur = self.conn.cursor()
            cur.execute(query, params)
            return cur
        except QueryCanceled as exc:
            raise TriageError(
                _TIMEOUT_ERROR[self.name],
                f"{self.name} database: statement timeout after {STATEMENT_TIMEOUT_MS} ms",
            ) from exc
        except psycopg.OperationalError as exc:
            raise TriageError(
                _UNREACHABLE_ERROR[self.name],
                f"{self.name} database: connection lost during statement: {exc}",
            ) from exc

    # -- transactions / lifecycle ------------------------------------------

    def transaction(self) -> Any:
        """A per-record transaction scope. The connection is opened with
        autocommit=True, so this is the only place BEGIN/COMMIT happen; a
        dry-run yields a no-op scope."""
        if self.dry_run or self.conn is None:
            return contextlib.nullcontext()
        return self.conn.transaction()

    def close(self) -> None:
        if self.conn is not None and not self.conn.closed:
            self.conn.close()

    def __enter__(self) -> "GuardedConnection":
        return self

    def __exit__(self, *_exc: Any) -> None:
        self.close()


def _open(name: str, creds: Mapping[str, str], *, search_path: str | None) -> psycopg.Connection[Any]:
    options = f"-c statement_timeout={STATEMENT_TIMEOUT_MS}"
    if search_path is not None:
        options += f" -c search_path={search_path}"
    try:
        return psycopg.connect(
            host=creds["DATABASE_HOST"],
            port=int(creds["DATABASE_PORT"]),
            dbname=creds["DATABASE_NAME"],
            user=creds["DATABASE_USERNAME"],
            password=creds["DATABASE_PASSWORD"],
            connect_timeout=CONNECT_TIMEOUT_SECONDS,
            application_name=APPLICATION_NAME,
            options=options,
            autocommit=True,
            row_factory=dict_row,  # every row is a dict keyed by column name
        )
    except (psycopg.OperationalError, ValueError) as exc:
        raise TriageError(
            _UNREACHABLE_ERROR[name],
            f"{name} database: connect failed ({CONNECT_TIMEOUT_SECONDS}s timeout, no retry): "
            + _redact(str(exc), creds),
        ) from exc


def connect_admin(client: ClientConfig, *, dry_run: bool = False) -> GuardedConnection:
    """Open the client's ADMIN database.

    Sets `search_path` to the resolved client schema AND builds the admin
    read/write allow-lists in that schema (every statement is also
    schema-qualified through the guard — both, not either). Read-only clients
    such as inPlay (schema `public`) are permitted: the rule is client-schema-
    relative (EC17). Credentials are validated even in dry-run; no connection is
    opened in dry-run.
    """
    creds = read_credential_file(client.admin, client_key=client.key, role="admin")
    schema = client.schema
    guarded = GuardedConnection(
        name="admin",
        schema=schema,
        read_tables=frozenset(f"{schema}.{t}" for t in ADMIN_READ_TABLES),
        write_tables=frozenset(f"{schema}.{t}" for t in ADMIN_WRITE_TABLES),
        dry_run=dry_run,
    )
    if not dry_run:
        guarded.conn = _open("admin", creds, search_path=schema)
    return guarded


def connect_agent(client: ClientConfig, *, dry_run: bool = False) -> GuardedConnection:
    """Open the client's AGENT (nova-kernel) database.

    No `search_path` is set: the kernel tables live in `public` on a different
    host. Read allow-list is `public.conversations` / `public.messages`; the
    write allow-list is EMPTY. A client with `agent_database: null` is refused
    with CLIENT_NOT_CONFIGURED (EC8) before anything else.
    """
    if client.agent is None:
        raise TriageError(
            "CLIENT_NOT_CONFIGURED",
            f"client {client.key!r} has no agent database in the registry (agent_database is null)",
        )
    creds = read_credential_file(client.agent, client_key=client.key, role="agent")
    guarded = GuardedConnection(
        name="agent",
        schema=AGENT_SCHEMA,
        read_tables=frozenset(f"{AGENT_SCHEMA}.{t}" for t in AGENT_READ_TABLES),
        write_tables=frozenset(),
        dry_run=dry_run,
    )
    if not dry_run:
        guarded.conn = _open("agent", creds, search_path=None)
    return guarded


# ---------------------------------------------------------------------------
# Direct run: offline credential check (key NAMES only)
# ---------------------------------------------------------------------------


def _main() -> None:
    parser = ArgParser(
        prog="_creds.py",
        description=(
            "Shared module for the client-feedback-triage scripts. Run directly only to "
            "check a client's registry entry and credential files offline. Prints key "
            "names present/absent — never values. Opens no connection."
        ),
    )
    # `required=True` routes a missing subcommand through ArgParser.error ->
    # the UNEXPECTED usage envelope, exit 1. `--help` still exits 0.
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="report a client's credential key names (no values, no connection)")
    check.add_argument("client")
    args = parser.parse_args()

    client = resolve_client(args.client)
    admin_report = credential_key_report(client.admin)
    agent_report = credential_key_report(client.agent) if client.agent else None
    ok(
        {
            "client": client.key,
            "schema": client.schema,
            "root": str(client.root),
            "root_exists": client.root.is_dir(),
            "configured": client.configured,
            "admin": admin_report,
            "agent_database": agent_report,
            "admin_read_tables": sorted(f"{client.schema}.{t}" for t in ADMIN_READ_TABLES),
            "admin_write_tables": sorted(f"{client.schema}.{t}" for t in ADMIN_WRITE_TABLES),
            "agent_read_tables": sorted(f"{AGENT_SCHEMA}.{t}" for t in AGENT_READ_TABLES) if client.agent else [],
        }
    )


if __name__ == "__main__":
    run_main(_main)
