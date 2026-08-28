#!/usr/bin/env python3
"""Strict zero-leftover grep gate (spec R8 / EC4).

The gate = the FIXED prior-client regex PLUS a per-run generated token set:
  - Template verification: token set = all real prior-client tokens (already in
    the fixed regex).
  - Instantiation verification (the skill's normal use): token set = all `acme`
    variants (`acme`, `Acme`, `ACME`, `acme_member`) PLUS every `default` value
    declared in each template.params.json manifest.

A hit anywhere in tracked files fails the gate: the run STOPS, exact file:line
hits are reported, and the run is NOT marked complete. There is no allowlist for
real residue — the ONLY exclusions are the verified-benign ones from Phase 1
verification (see EXCLUSIONS below), which are structural, not residue.

Verified-benign exclusions (Phase 1 handoff — NOT allowlisting real residue):
  (a) gate-definition strings inside each template's SETUP.md and
      template.params.json (they legitimately quote the tokens they scan FOR);
  (b) base64 integrity-hash substrings in package-lock.json (case-insensitive
      `txn` / `tj` inside sha512 hashes) — coincidental, not identity.
Diagnostic/generated artifacts are excluded from the templates entirely (R8), so
they are also skipped here: before.txt/after.txt, *.tfstate, real tfvars, .env*,
docs-data/ contents, public/vision/, node_modules, .next, .git, .venv, caches.

Usage:
  grep_gate.py --root <repo> [--root <repo2> ...] \
      --tokens acme Acme ACME acme_member [--tokens-from manifest.json ...] \
      [--fixed-regex '<override>'] [--json]

By default the fixed prior-client regex is the one embedded in both manifests.
`--tokens-from <manifest>` extracts every `default` string value from a
template.params.json and adds it to the per-run token set (skips derivation
placeholders like `<set-as-repo-variable>` and empty/structural defaults).

Exit: 0 = zero hits (gate PASS); 1 = one or more hits (gate FAIL); 2 = usage error.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

FIXED_PRIOR_CLIENT_REGEX = (
    r"totaljobs|total-jobs|Total Jobs|TotalJobs|totaljobs_member|"
    r"txn|TXN|txn_member|inplay|inPlay|InPlay|inplay_member|tj-"
)

# Directory / file patterns never scanned (build output, deps, VCS, generated,
# diagnostic, and secret-bearing files excluded from the template per R8).
SKIP_DIRS = {
    "node_modules", ".next", ".git", ".venv", "__pycache__",
    ".pytest_cache", ".ruff_cache", "dist", "build", ".turbo",
}
SKIP_REL_DIRS = {"docs-data", os.path.join("public", "vision")}
SKIP_FILE_NAMES = {"before.txt", "after.txt"}
SKIP_FILE_GLOBS = [
    "*.tfstate", "*.tfstate.backup",
    "terraform.production.tfvars", "terraform.testing.tfvars", "terraform.tfvars",
    ".env", ".env.local", ".env.production",
]
# package-lock.json: only `txn`/`tj` inside base64 sha512 integrity hashes are
# benign. We scan it but drop hits whose match is a token inside an integrity line.
LOCKFILE_NAMES = {"package-lock.json", "uv.lock"}

# Placeholder / structural default values that are NOT residue tokens.
STRUCTURAL_DEFAULTS = {
    "<set-as-repo-variable>", "REPLACE_WITH_", "",
}


def _is_binary(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:1024]
    except OSError:
        return True
    return b"\x00" in chunk


def _skip_file(path: Path, root: Path) -> bool:
    if path.name in SKIP_FILE_NAMES:
        return True
    for pat in SKIP_FILE_GLOBS:
        if path.match(pat):
            return True
    rel = path.relative_to(root)
    parts = set(rel.parts)
    if parts & SKIP_DIRS:
        return True
    rel_str = str(rel)
    for d in SKIP_REL_DIRS:
        if rel_str == d or rel_str.startswith(d + os.sep):
            return True
    return False


def _tokens_from_manifest(manifest_path: Path) -> list[str]:
    data = json.loads(manifest_path.read_text())
    out: list[str] = []

    def walk(node) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "default":
                    _collect_default(v, out)
                else:
                    walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data.get("groups", {}))
    return out


def _collect_default(val, out: list[str]) -> None:
    if isinstance(val, str):
        s = val.strip()
        if not s or s in STRUCTURAL_DEFAULTS:
            return
        if s.startswith("<") and s.endswith(">"):
            return
        if s.startswith("REPLACE_WITH_"):
            return
        out.append(s)
    elif isinstance(val, dict):
        # e.g. colors/fonts objects — the hex/family values are legitimate acme
        # brand defaults and should be replaced, so include them.
        for v in val.values():
            _collect_default(v, out)


_WORD = re.compile(r"\w")


def _smart_boundary(token: str) -> str:
    """Wrap an escaped literal token so it does NOT match when flanked by an
    alphanumeric/underscore on a side where the token itself has a word-char edge.

    This keeps identity residue caught aggressively (`acme` still matches inside
    `acme-admin-panel`, `acme_member`, `acmeVault` — hyphen and the capital V are
    boundaries because the char AFTER 'acme' is not preceded... handled by the
    edge rule) while rejecting substring false positives from common brand
    defaults (`Inter` must not match inside `Internal`; `#ffffff` must not match
    inside `#ffffffab`).

    Edge rule: if the token starts with a word char, require the preceding char
    to be a non-word char (or string start). If it ends with a word char, require
    the following char to be a non-word char (or string end). Non-word edges
    (e.g. `#ffffff` starts with '#', `tj-` ends with '-') get no constraint on
    that side, so they match verbatim. Crucially, a trailing word char followed
    by another word char (Inter+nal) is rejected, but a trailing word char
    followed by a hyphen/underscore/capital-after-lower is a real token break.
    """
    esc = re.escape(token)
    left = r"(?<![\w])" if _WORD.match(token[0]) else ""
    right = r"(?![\w])" if _WORD.match(token[-1]) else ""
    return f"{left}{esc}{right}"


def _build_pattern(fixed_regex: str, identity_tokens: list[str], value_tokens: list[str]) -> re.Pattern:
    # Two token classes:
    #  - identity tokens (acme variants) + the fixed prior-client regex: matched
    #    as SUBSTRINGS (aggressive) — catches acmeVault / acme-admin / acme_member
    #    concatenations, which is the whole point of R8/EC4.
    #  - value tokens (manifest brand/color/font/url defaults): matched with SMART
    #    BOUNDARIES so common values don't false-positive (Inter vs Internal,
    #    #ffffff vs #ffffffab). A residual acme brand value is still caught when it
    #    stands as its own token.
    ident = sorted({re.escape(t) for t in identity_tokens}, key=len, reverse=True)
    vals = sorted({_smart_boundary(t) for t in value_tokens}, key=len, reverse=True)
    alternation = fixed_regex
    for group in (ident, vals):
        if group:
            alternation = alternation + "|" + "|".join(group)
    return re.compile(alternation)


def _line_is_gate_definition(path: Path, root: Path) -> bool:
    """Exclusion (a): gate-definition / mapping docs that legitimately QUOTE the
    tokens they explain. Scoped to specific filenames:
      - template.params.json — the manifest declares the gate token set.
      - SETUP.md — documents the instantiation path incl. the gate command.
      - BRANDING.md (docs/BRANDING.md) — the panel brand-seam MAPPING doc; it
        names the acme vocabulary (`Acme`, `acme_member`) and the acme→brand color
        table to explain the single substitution point. Genericizing it would make
        the mapping doc worse at its job (team-lead approved this exclusion, same
        rationale as SETUP.md/template.params.json).
    Instantiated repos keep these files too, and quoting the fixed prior-client
    regex there is equally benign."""
    name = path.name
    return name in {"template.params.json", "SETUP.md", "BRANDING.md"}


# A base64 integrity hash value: sha512-/sha256- followed by the base64 blob
# (letters, digits, +, /, =). We only forgive a token that falls INSIDE such a
# blob — not merely anywhere on a line that also contains one (N1).
_HASH_VALUE_RE = re.compile(r"sha(?:512|256)-[A-Za-z0-9+/=]+")


def _hit_is_benign_lockfile(line: str, match: str, span: tuple[int, int]) -> bool:
    """Exclusion (b): txn/tj coincidental substring INSIDE a base64 integrity hash
    value in a lockfile. Only the token's actual position is forgiven, so a real
    `txn`/`tj-` elsewhere on the same line is still reported (N1)."""
    if match.lower() not in {"txn", "tj-", "tj"}:
        return False
    start, end = span
    for h in _HASH_VALUE_RE.finditer(line):
        if h.start() <= start and end <= h.end():
            return True
    return False


def scan(roots: list[Path], pattern: re.Pattern) -> list[tuple[str, int, str, str]]:
    hits: list[tuple[str, int, str, str]] = []
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                path = Path(dirpath) / fn
                if _skip_file(path, root):
                    continue
                if _is_binary(path):
                    continue
                gate_def_file = _line_is_gate_definition(path, root)
                is_lockfile = path.name in LOCKFILE_NAMES
                try:
                    text = path.read_text(errors="replace")
                except OSError:
                    continue
                for lineno, line in enumerate(text.splitlines(), 1):
                    for m in pattern.finditer(line):
                        match = m.group(0)
                        if gate_def_file:
                            continue
                        if is_lockfile and _hit_is_benign_lockfile(line, match, m.span()):
                            continue
                        rel = str(path.relative_to(root))
                        hits.append((f"{root.name}/{rel}", lineno, match, line.strip()[:200]))
    return hits


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--root", action="append", required=True, help="Repo root to scan (repeatable)")
    p.add_argument("--tokens", nargs="*", default=[], help="Extra literal tokens to fail on (e.g. acme variants)")
    p.add_argument("--tokens-from", action="append", default=[], help="Extract `default` values from a template.params.json (repeatable)")
    p.add_argument("--fixed-regex", default=FIXED_PRIOR_CLIENT_REGEX, help="Override the fixed prior-client regex")
    p.add_argument("--json", action="store_true", help="Emit hits as JSON")
    args = p.parse_args()

    roots = [Path(r).resolve() for r in args.root]
    for r in roots:
        if not r.is_dir():
            sys.exit(f"ABORT: --root {r} is not a directory")

    # Identity tokens (acme variants) -> aggressive substring match.
    identity_tokens = sorted(set(t for t in args.tokens if t))
    # Manifest defaults (brand colours/fonts/urls/names) -> smart-boundary match.
    value_tokens: list[str] = []
    for mf in args.tokens_from:
        value_tokens.extend(_tokens_from_manifest(Path(mf).resolve()))
    value_tokens = sorted(set(t for t in value_tokens if t and t not in identity_tokens))
    total = len(identity_tokens) + len(value_tokens)

    pattern = _build_pattern(args.fixed_regex, identity_tokens, value_tokens)
    hits = scan(roots, pattern)

    if args.json:
        print(json.dumps(
            {"pass": not hits, "token_count": total,
             "identity_tokens": identity_tokens, "value_tokens": value_tokens,
             "hits": [{"file": f, "line": ln, "match": m, "context": ctx} for f, ln, m, ctx in hits]},
            indent=2,
        ))
    else:
        print(f"[gate] fixed prior-client regex + {len(identity_tokens)} identity + {len(value_tokens)} value token(s)")
        if not hits:
            print(f"[gate] ✅ PASS — 0 hits across {', '.join(r.name for r in roots)}")
        else:
            print(f"[gate] ❌ FAIL — {len(hits)} hit(s). The run is NOT complete; fix each and re-run:")
            for f, ln, m, ctx in hits:
                print(f"    {f}:{ln}: [{m}]  {ctx}")

    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
