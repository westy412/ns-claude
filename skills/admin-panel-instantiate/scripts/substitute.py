#!/usr/bin/env python3
"""Manifest-driven token substitution for an instantiated repo (spec R6).

Reads a template.params.json manifest and, for each parameter, replaces the
`default` (acme) value with the resolved client value in exactly the files the
manifest lists. Then applies the api template's structural renames
(supabase/acme/ -> supabase/<schema>/, and the 06 verify filename) WITHOUT
substituting the moved apply.py, and leaves noSubstitution / operatorFixed
values untouched.

Substitution order (longest value first) prevents partial-overlap corruption:
`acme_member` is replaced before `acme`; `Acme Member` before `Acme`.

The resolved value map is supplied on the CLI or as a JSON file; the derived
identity from derive_identity.py --json is the source of truth for it. This
script does NOT invent values — it only maps manifest `default` -> provided value
by parameter name.

Usage:
  substitute.py --root <repo> --manifest <repo>/template.params.json \
      --values values.json [--dry-run]

values.json maps each manifest PARAMETER NAME to its resolved value, e.g.:
  {
    "display_name": "Zenith Freight",
    "slug": "zenith-freight",
    "org_token": "ZenithFreight",
    "member_role": "zenithfreight_member",
    "member_role_label": "Zenith Freight Member",
    "tenant_schema": "zenithfreight",
    "package_name": "zenith-freight-admin-api",
    "service_name": "zenith-freight-admin-panel",   # per-manifest; api uses -admin-api
    "sa_prefix": "zf",
    "vault_repo_url": "git@github.com:Novosapien/zenith-freight-vault.git",
    "docs_sync_secret_id": "zenith-freight-docs-sync-api-key",
    "cors_origin_regex": "...zenith-freight-admin-panel...",
    "panel_url_placeholders": "zenith-freight-admin-panel-url",
    "brand_display_name": "Zenith Freight",
    "brand_primary_color": "#0C2577",
    "colors": {...}, "fonts": {...}
  }

Colors/fonts objects: each leaf default value is replaced by the matching leaf in
the provided object (by key path). Brand color substitution in globals.css must
ALSO be applied via the 1:1 map in docs/BRANDING.md — this script substitutes the
literal acme hex values wherever they appear (brand.config.ts + globals.css), but
the ordered globals.css mapping is the skill's responsibility to verify.

--dry-run prints the planned replacements per file; makes no edits.

Exit: 0 on success; nonzero on a missing value for a listed parameter or a
rename collision.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _flatten_default(default, value, pairs: list[tuple[str, str]], key: str | None = None) -> None:
    """Collect (old, new) literal string pairs from a manifest default and its
    resolved value.

    Object defaults (colors/fonts) are substituted KEY-ANCHORED: each leaf yields
    a `<key>: "<old>"` -> `<key>: "<new>"` pair matching the brand.config.ts TS
    idiom. This disambiguates leaves that SHARE a default literal but resolve
    differently (e.g. `background` and `cardBackground` both default '#ffffff' but
    a client may want them to diverge) — a bare-hex replace could not. The
    globals.css hex application is the documented BRANDING.md ordered-map manual
    step, not this bare substitution."""
    if isinstance(default, str):
        old = default.strip()
        if not old:
            return
        if value is None:
            raise KeyError(old)
        if key is not None:
            # Key-anchored form for object leaves (colors/fonts in brand.config.ts).
            pairs.append((f'{key}: "{old}"', f'{key}: "{value}"'))
        else:
            pairs.append((old, str(value)))
    elif isinstance(default, dict):
        if not isinstance(value, dict):
            raise KeyError(f"expected object value for object default {list(default)}")
        for k, dv in default.items():
            _flatten_default(dv, value.get(k), pairs, key=k)


def collect_file_pairs(manifest: dict, values: dict) -> tuple[dict[str, list[tuple[str, str]]], dict]:
    """Return (file -> ordered [(old,new)] pairs, tenant_schema meta).

    Substitution is PER FILE, driven by each parameter's own `files[]`, so params
    routed to DIFFERENT files (display_name -> brand.config.ts; org_token ->
    types.ts) resolve independently even when they share the default literal
    'Acme'.

    That routing alone is NOT sufficient when two params list the SAME file with
    the SAME default literal but DIFFERENT resolved values (e.g. display_name
    'Zenith Freight' and org_token 'ZenithFreight' both routed to users.ts). A
    plain replace would let the first pair consume every 'Acme' and the second
    no-op, and the wrong value would pass the grep gate (it carries no acme
    token). The manifest must not route such a collision; this function DETECTS it
    and HARD-ABORTS (B1) rather than guess which param owns which occurrence.
    """
    # file -> list of (old, new, param) so a collision can name its params.
    per_file_src: dict[str, list[tuple[str, str, str]]] = {}
    schema_meta: dict = {}
    for group in manifest.get("groups", {}).values():
        for pname, pdef in group.get("params", {}).items():
            files = pdef.get("files", [])
            default = pdef.get("default")
            if pname == "tenant_schema":
                schema_meta = pdef  # capture rename/moveOnly/noSubstitution
            # aliasOf: this param inherits the aliased param's VALUE (e.g.
            # brand_display_name aliasOf identity.display_name). If no explicit
            # value was supplied, borrow the aliased one so a future aliasOf param
            # WITH files[] substitutes correctly. Empty-files aliases are skipped
            # below like any provisioning-only param.
            alias = pdef.get("aliasOf")
            if alias and pname not in values:
                aliased_name = alias.rsplit(".", 1)[-1]
                if aliased_name in values:
                    values[pname] = values[aliased_name]
            if not files:
                continue  # provisioning/documentation-only params (e.g. docs_sync_secret_id on panel)
            if isinstance(default, str):
                s = default.strip()
                if not s or s.startswith("<") or s.startswith("REPLACE_WITH_"):
                    continue
            if pname not in values:
                # A listed param with no supplied value is a hard error — a
                # missed substitution would fail the grep gate later.
                raise SystemExit(
                    f"ABORT: manifest parameter '{pname}' has files {files} but no "
                    f"value was supplied in values.json."
                )
            param_pairs: list[tuple[str, str]] = []
            _flatten_default(default, values.get(pname), param_pairs)
            for rel in files:
                for old, new in param_pairs:
                    per_file_src.setdefault(rel, []).append((old, new, pname))

    # B1 collision guard: within a file, the SAME old-string must map to exactly
    # ONE new-string. If two params disagree, abort naming both params + the file.
    per_file: dict[str, list[tuple[str, str]]] = {}
    for rel, triples in per_file_src.items():
        by_old: dict[str, dict[str, list[str]]] = {}
        for old, new, pname in triples:
            by_old.setdefault(old, {}).setdefault(new, []).append(pname)
        for old, news in by_old.items():
            if len(news) > 1:
                detail = "; ".join(
                    f"{sorted(set(pnames))} -> {new!r}" for new, pnames in news.items()
                )
                raise SystemExit(
                    "ABORT (B1 collision): in file '" + rel + "' the literal " + repr(old) +
                    " is routed to conflicting replacements: " + detail + ". Two parameters "
                    "share this file and this default but resolve differently — the manifest "
                    "must not route them together (fix the manifest's files[]; do not guess)."
                )
        # Collapse to unique (old,new) and order longest old-string first to avoid
        # partial-overlap corruption (acme_member before acme; 'Zenith Freight'
        # before 'Zenith').
        pairs = sorted({(old, new) for old, new, _ in triples}, key=lambda p: len(p[0]), reverse=True)
        per_file[rel] = pairs
    return per_file, schema_meta


def apply_substitutions(root: Path, per_file: dict[str, list[tuple[str, str]]],
                        no_substitution: set[str], dry_run: bool) -> list[str]:
    log: list[str] = []
    for rel in sorted(per_file):
        if rel in no_substitution:
            log.append(f"[skip] {rel} (noSubstitution — consumed via settings only)")
            continue
        path = root / rel
        if not path.exists():
            # Manifest may list a file that a given template does not have (the
            # two manifests share param names but differ in files); tolerate.
            log.append(f"[warn] {rel} listed in manifest but not found under {root.name} — skipped")
            continue
        text = path.read_text()
        new_text = text
        applied = []
        for old, new in per_file[rel]:
            if old in new_text and old != new:
                new_text = new_text.replace(old, new)
                applied.append(f"{old!r}->{new!r}")
        if applied:
            if dry_run:
                log.append(f"[dry] {rel}: " + ", ".join(applied))
            else:
                path.write_text(new_text)
                log.append(f"[edit] {rel}: " + ", ".join(applied))
        else:
            log.append(f"[noop] {rel}: no acme defaults present")
    return log


def apply_renames(root: Path, schema_meta: dict, tenant_schema: str, dry_run: bool) -> list[str]:
    """Apply the api template's DDL-directory rename + 06 verify filename rename.
    moveOnly files (apply.py) move with the directory but are NOT substituted."""
    log: list[str] = []
    renames = schema_meta.get("renames", {})
    if not renames:
        return log
    # N2 guard: default base_dir to the directory a file-rename key sits in, so a
    # manifest with a file rename but NO dir-rename key can never raise
    # UnboundLocalError below. If a dir-rename key is present it overrides this.
    base_dir = None
    for k in renames:
        if not k.endswith("/"):
            base_dir = (root / k).parent
            break
    # Directory rename: supabase/acme/ -> supabase/<schema>/
    old_dir_rel = None
    for k in renames:
        if k.endswith("/"):
            old_dir_rel = k.rstrip("/")
            break
    if old_dir_rel:
        old_dir = root / old_dir_rel
        new_dir = root / old_dir_rel.rsplit("/", 1)[0] / tenant_schema
        if old_dir.is_dir():
            if new_dir.exists():
                raise SystemExit(f"ABORT: rename target {new_dir} already exists")
            if dry_run:
                log.append(f"[dry-rename] {old_dir_rel}/ -> {new_dir.relative_to(root)}/")
            else:
                old_dir.rename(new_dir)
                log.append(f"[rename] {old_dir_rel}/ -> {new_dir.relative_to(root)}/")
            base_dir = new_dir
        else:
            base_dir = root / old_dir_rel.rsplit("/", 1)[0] / tenant_schema
            log.append(f"[warn] DDL dir {old_dir_rel}/ not found — may already be renamed")
    if base_dir is None:
        # No dir-rename key AND no file-rename key resolved a base — nothing to do.
        return log
    # 06 verify filename rename inside the (now renamed) directory.
    for k, v in renames.items():
        if k.endswith("/"):
            continue
        old_name = Path(k).name
        new_name = Path(v.replace("<tenant_schema>", tenant_schema)).name
        old_f = base_dir / old_name
        new_f = base_dir / new_name
        if old_f.exists():
            if dry_run:
                log.append(f"[dry-rename] {old_f.relative_to(root)} -> {new_f.relative_to(root)}")
            else:
                old_f.rename(new_f)
                log.append(f"[rename] {old_f.relative_to(root)} -> {new_f.relative_to(root)}")
    if not dry_run:
        move_only = schema_meta.get("moveOnly", [])
        for mo in move_only:
            log.append(f"[moveOnly] {Path(mo).name} moved with the DDL dir, NOT token-substituted (reads settings.tenant_schema)")
    return log


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--root", required=True)
    p.add_argument("--manifest", required=True)
    p.add_argument("--values", required=True, help="JSON file mapping manifest param name -> resolved value")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    root = Path(args.root).resolve()
    manifest = json.loads(Path(args.manifest).read_text())
    values = json.loads(Path(args.values).read_text())

    per_file, schema_meta = collect_file_pairs(manifest, values)
    no_sub = set(schema_meta.get("noSubstitution", []))
    tenant_schema = values.get("tenant_schema", "")

    log: list[str] = []
    # Substitute the manifest-listed files (using each file's own acme path) FIRST,
    # then apply the DDL-directory + 06 filename renames, so the pre-rename paths
    # the manifest lists stay valid during substitution.
    log += apply_substitutions(root, per_file, no_sub, args.dry_run)
    if tenant_schema:
        log += apply_renames(root, schema_meta, tenant_schema, args.dry_run)

    for line in log:
        print(line)
    edits = len([l for l in log if l.startswith('[edit]') or l.startswith('[dry]')])
    total_pairs = sum(len(v) for v in per_file.values())
    print(f"\n[substitute] {root.name}: {edits} file(s) with substitutions; "
          f"{total_pairs} file-scoped token pair(s).")


if __name__ == "__main__":
    main()
