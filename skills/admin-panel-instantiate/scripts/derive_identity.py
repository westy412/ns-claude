#!/usr/bin/env python3
"""Derive the full client identity set from a display name and validate the GCP
service-account id 30-char cap BEFORE any provisioning (spec R6 / EC1).

Derivation chain (spec R6, both manifests):
  display_name -> slug     (lowercase, spaces -> hyphens)
  slug         -> compact  (hyphens stripped)
  compact      == schema (tenant_schema) == member-role stem
  org_token    == display_name with spaces stripped
  member_role  == "<compact>_member"
  member_role_label == "<display_name> Member"
  sa_prefix    -> ALWAYS PROMPTED (no safe derivation)

Runtime service-account ids (GCP caps account_id at 30 chars, [a-z][-a-z0-9]{4,28}[a-z0-9]):
  panel:  <sa_prefix>-panel-runtime      / <sa_prefix>-panel-testing-runtime
  api:    <sa_prefix>-api-runtime        / <sa_prefix>-api-rt-testing

The LONGEST id (<sa_prefix>-panel-testing-runtime) governs the cap. This script
computes every id, checks all of them against the GCP rule, and exits nonzero
with a clear message naming the cap if any id is too long or malformed (EC1).

Usage:
  derive_identity.py --display "Zenith Freight" --sa-prefix zf [--vault-url URL] [--json]
  derive_identity.py --display "Zenith Freight"            # sa_prefix omitted -> reports it must be prompted
"""
from __future__ import annotations

import argparse
import json
import re
import sys

# GCP service account account_id rule: 6-30 chars total, start lowercase letter,
# then 4-28 of [-a-z0-9], end alphanumeric.
SA_ID_RE = re.compile(r"^[a-z](?:[-a-z0-9]{4,28}[a-z0-9])$")
SA_ID_MAX = 30

# Runtime SA id suffixes. These are PINNED to the manifests' runtime_sa_id*
# derivation strings (`<sa_prefix>-panel-runtime`, `<sa_prefix>-panel-testing-runtime`,
# `<sa_prefix>-api-runtime`, `<sa_prefix>-api-rt-testing`). Note the api testing
# suffix is `-api-rt-testing` (NOT `-api-testing-runtime`) — the two sides are
# deliberately asymmetric. Pass --panel-manifest/--api-manifest to read the
# suffixes straight from the manifests instead of trusting these constants; a
# future manifest change to a suffix will then be picked up automatically rather
# than silently diverging from this fallback.
SA_SUFFIXES = {
    "panel_prod": "-panel-runtime",
    "panel_testing": "-panel-testing-runtime",
    "api_prod": "-api-runtime",
    "api_testing": "-api-rt-testing",
}


def suffixes_from_manifests(panel_manifest: str | None, api_manifest: str | None) -> dict:
    """Read runtime-SA suffixes from the manifests' runtime_sa_id*.derivation
    (`<sa_prefix>-...`), overriding the pinned SA_SUFFIXES so a manifest change
    can't silently diverge. Falls back to the constant for any side not supplied
    or any param not found."""
    out = dict(SA_SUFFIXES)
    plan = [
        (panel_manifest, "runtime_sa_id", "panel_prod"),
        (panel_manifest, "runtime_sa_id_testing", "panel_testing"),
        (api_manifest, "runtime_sa_id", "api_prod"),
        (api_manifest, "runtime_sa_id_testing", "api_testing"),
    ]
    for mpath, pname, key in plan:
        if not mpath:
            continue
        try:
            d = json.load(open(mpath))
        except OSError:
            continue
        for group in d.get("groups", {}).values():
            pd = group.get("params", {}).get(pname)
            if pd and isinstance(pd.get("derivation"), str) and "<sa_prefix>" in pd["derivation"]:
                out[key] = pd["derivation"].replace("<sa_prefix>", "")
                break
    return out


def derive_slug(display_name: str) -> str:
    s = display_name.strip().lower()
    s = re.sub(r"\s+", "-", s)
    return s


def derive(display_name: str, sa_prefix: str | None, vault_url: str | None,
           sa_suffixes: dict | None = None) -> dict:
    sa_suffixes = sa_suffixes or SA_SUFFIXES
    slug = derive_slug(display_name)
    compact = slug.replace("-", "")
    org_token = re.sub(r"\s+", "", display_name.strip())
    member_role = f"{compact}_member"
    ident = {
        "display_name": display_name.strip(),
        "slug": slug,
        "compact": compact,
        "tenant_schema": compact,
        "org_token": org_token,
        "member_role": member_role,
        "member_role_label": f"{display_name.strip()} Member",
        "package_name_panel": f"{slug}-admin-panel",
        "package_name_api": f"{slug}-admin-api",
        "service_name_panel": f"{slug}-admin-panel",
        "service_name_api": f"{slug}-admin-api",
        "docs_sync_secret_id": f"{slug}-docs-sync-api-key",
        "vault_repo_url": (vault_url or f"git@github.com:Novosapien/{slug}-vault.git"),
        "sa_prefix": sa_prefix,
        "repo_panel": f"Novosapien/{slug}-admin-panel",
        "repo_api": f"Novosapien/{slug}-admin-api",
    }
    if sa_prefix:
        runtime_sas = {k: f"{sa_prefix}{suf}" for k, suf in sa_suffixes.items()}
        ident["runtime_sas"] = runtime_sas
        # Full-value derived SA params matching the manifests' runtime_sa_id params
        # (default acme-panel-runtime / acme-api-runtime; derivation <sa_prefix>-...).
        # sa_prefix is a derivation INPUT only — it is no longer routed to files[]
        # directly (that caused the bare-`acme` collision with slug/tenant_schema),
        # so the skill substitutes these full values instead.
        ident["runtime_sa_id_panel"] = runtime_sas["panel_prod"]
        ident["runtime_sa_id_panel_testing"] = runtime_sas["panel_testing"]
        ident["runtime_sa_id_api"] = runtime_sas["api_prod"]
        ident["runtime_sa_id_api_testing"] = runtime_sas["api_testing"]
    return ident


def validate_sa_cap(sa_prefix: str, sa_suffixes: dict | None = None) -> list[str]:
    """Return a list of human-readable violations; empty means valid."""
    sa_suffixes = sa_suffixes or SA_SUFFIXES
    violations: list[str] = []
    for key, suf in sa_suffixes.items():
        sa_id = f"{sa_prefix}{suf}"
        if len(sa_id) > SA_ID_MAX:
            violations.append(
                f"{key}: '{sa_id}' is {len(sa_id)} chars — exceeds the GCP "
                f"service-account id cap of {SA_ID_MAX}. Choose a shorter sa_prefix "
                f"(current prefix '{sa_prefix}' is {len(sa_prefix)} chars)."
            )
        elif not SA_ID_RE.match(sa_id):
            violations.append(
                f"{key}: '{sa_id}' does not match the GCP account_id rule "
                f"{SA_ID_RE.pattern} (must start with a lowercase letter, contain "
                f"only [-a-z0-9], and end alphanumeric)."
            )
    return violations


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--display", required=True, help="Client display name (may contain spaces)")
    p.add_argument("--sa-prefix", default=None, help="Runtime SA id prefix — ALWAYS prompted, no safe derivation")
    p.add_argument("--vault-url", default=None, help="Vault repo SSH URL; defaults to git@github.com:Novosapien/<slug>-vault.git")
    p.add_argument("--panel-manifest", default=None, help="Panel template.params.json — read runtime-SA suffixes from it instead of the pinned defaults")
    p.add_argument("--api-manifest", default=None, help="API template.params.json — read runtime-SA suffixes from it instead of the pinned defaults")
    p.add_argument("--json", action="store_true", help="Emit the derived identity as JSON")
    args = p.parse_args()

    if not args.display.strip():
        sys.exit("ABORT: --display must be a non-empty display name.")

    # Suffixes: manifest-derived when a manifest is supplied, else the pinned
    # SA_SUFFIXES (which match the manifests today, per the comment on that dict).
    sa_suffixes = suffixes_from_manifests(args.panel_manifest, args.api_manifest)
    ident = derive(args.display, args.sa_prefix, args.vault_url, sa_suffixes)

    if args.sa_prefix is None:
        # sa_prefix has no safe derivation — the skill must prompt for it.
        if args.json:
            ident["_sa_prefix_status"] = "MISSING — must be prompted (no safe derivation)"
            print(json.dumps(ident, indent=2))
        else:
            _print_table(ident)
            print("\n[sa_prefix] NOT PROVIDED — prompt the operator; there is no safe derivation.")
        sys.exit(2)

    violations = validate_sa_cap(args.sa_prefix, sa_suffixes)
    if violations:
        print("ABORT (EC1): runtime service-account id(s) violate the GCP 30-char cap:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        print(
            "\nNo repos or cloud resources have been created. Re-run with a shorter "
            "--sa-prefix.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.json:
        print(json.dumps(ident, indent=2))
    else:
        _print_table(ident)
        print("\n[sa_prefix] runtime SA ids all within the 30-char GCP cap. OK.")


def _print_table(ident: dict) -> None:
    print("Derived identity (confirm/override each before use):")
    order = [
        "display_name", "slug", "compact", "tenant_schema", "org_token",
        "member_role", "member_role_label", "sa_prefix",
        "repo_panel", "repo_api", "service_name_panel", "service_name_api",
        "docs_sync_secret_id", "vault_repo_url",
    ]
    width = max(len(k) for k in order)
    for k in order:
        v = ident.get(k)
        print(f"  {k.ljust(width)} : {v}")
    if "runtime_sas" in ident:
        print("  runtime service accounts (full-value derived; sa_prefix is a derivation input only):")
        for label, key in (
            ("runtime_sa_id_panel", "runtime_sa_id_panel"),
            ("runtime_sa_id_panel_testing", "runtime_sa_id_panel_testing"),
            ("runtime_sa_id_api", "runtime_sa_id_api"),
            ("runtime_sa_id_api_testing", "runtime_sa_id_api_testing"),
        ):
            v = ident.get(key, "")
            print(f"    {label.ljust(28)} : {v} ({len(v)} chars)")


if __name__ == "__main__":
    main()
