#!/usr/bin/env python3
"""Per-run state tracking + done-probes + remaining-steps checklist (spec R7 / EC2).

The instantiation is a sequence of steps, each with a done-probe and create-if-
absent semantics. This script owns the run's state file so a re-run resumes:
completed steps are kept, and on failure a checklist of remaining steps is
emitted. Steps are also emitted on SUCCESS to surface manual residue (the
deploy-key verification triad, real-tfvars population, founding-admin dashboard
check).

State file: `<run-dir>/.instantiate-state.json` — a map of step-id -> status
("pending" | "done" | "failed") plus a free-form details blob per step. The skill
writes it; done-probes below can also compute status live so a state file lost
between sessions is recoverable from the actual world.

Step ids (execution order):
  inputs, repo_panel, repo_api, substitute_panel, substitute_api, grep_gate,
  wif_binding, sa_panel, sa_api, docs_sync_secret, actions_secrets,
  vault_deploy_key, repo_vars, tfvars_guidance, ddl, deploy_testing,
  deploy_production

Done-probe categories (R7): repo exists, secret exists, SA exists, schema in
pg_namespace, publication rows present, Cloud Run service deployed. The probe
COMMANDS are documented in references/idempotency-and-checklist.md; this script
records/reads their results and renders the checklist.

Usage:
  state.py init --run-dir DIR                          # scaffold pending state
  state.py set  --run-dir DIR --step ID --status done [--detail TEXT]
  state.py get  --run-dir DIR [--step ID]              # print status (all or one)
  state.py checklist --run-dir DIR [--phase success|failure]

`checklist --phase failure` lists every not-done step as a remaining action
(EC2). `--phase success` renders the manual-residue checklist regardless of step
status (the deploy-key triad etc. are always manual verifications).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

STATE_FILE = ".instantiate-state.json"

STEPS = [
    ("inputs", "Collect + derive identity, validate SA cap (EC1)"),
    ("repo_panel", "Create Novosapien/<slug>-admin-panel from template"),
    ("repo_api", "Create Novosapien/<slug>-admin-api from template"),
    ("substitute_panel", "Substitute panel params (colors/fonts key-anchored) + regen package-lock + place brand assets + MANUAL globals.css color map + layout.tsx font swap (before gate)"),
    ("substitute_api", "Substitute api params + rename DDL dir + 06 verify filename"),
    ("grep_gate", "Strict grep gate over both trees — 0 hits (EC4)"),
    ("wif_binding", "Bind both repos to WIF provider + grant workloadIdentityUser"),
    ("sa_panel", "Create panel runtime SAs (<sa_prefix>-panel-runtime / -testing-runtime)"),
    ("sa_api", "Create api runtime SAs (<sa_prefix>-api-runtime / -api-rt-testing)"),
    ("docs_sync_secret", "Create Secret Manager <slug>-docs-sync-api-key (+ -testing), generated value"),
    ("actions_secrets", "gh secret set on PANEL repo only: DOCS_SYNC_API_KEY (build-time) + NEXT_PUBLIC_SUPABASE_ANON_KEY (api mounts docs-sync from Secret Manager, no Actions secret)"),
    ("vault_deploy_key", "Generate vault deploy keypair: private->panel VAULT_DEPLOY_KEY, public->vault repo deploy key"),
    ("repo_vars", "Set repo variables incl. API_URL/API_URL_TESTING and DEPLOY_ENABLED=true"),
    ("tfvars_guidance", "Emit real-tfvars population guidance (manual, gitignored)"),
    ("ddl", "Apply tenant-schema DDL via apply.py --mode all (founding-admin precheck)"),
    ("deploy_testing", "Deploy testing via cloudrun-deploy (or stop at terraform plan in dry-run)"),
    ("deploy_production", "Deploy production via cloudrun-deploy (or stop at terraform plan in dry-run)"),
]
STEP_LABELS = dict(STEPS)

# Manual-residue checklist (always emitted on success AND failure). The deploy-key
# verification triad is from spec Notes; the brand-application items are gate
# PREREQUISITES (they must run during substitute, before the grep gate, or the
# gate flags globals.css/layout.tsx residue); the rest are the R6 secret-partition
# checklist items.
MANUAL_RESIDUE = [
    "BEFORE THE GATE — apply the globals.css color map: substitute.py key-anchors "
    "colors/fonts in brand.config.ts ONLY; the src/app/globals.css `--var: hex` "
    "custom properties are applied by hand per the 1:1 ordered table in "
    "admin-panel-template/docs/BRANDING.md. Skipping this leaves acme hexes in "
    "globals.css and the grep gate WILL flag them.",
    "BEFORE THE GATE — swap the layout.tsx fonts: src/app/layout.tsx loads fonts via "
    "next/font/google imports (not `key: \"value\"`), so the client typeface swap is "
    "a manual edit of the import + loader calls, not a string replace.",
    "Deploy-key triad: private half is the panel repo Actions secret VAULT_DEPLOY_KEY; "
    "public half is a read-only deploy key on the vault repo; the DOCS_SYNC_API_KEY "
    "value is IDENTICAL across all three forms — the PANEL repo's Actions secret "
    "(build-time), the api's Secret Manager secret value (mounted into Cloud Run), "
    "and the generated key. The api has NO DOCS_SYNC_API_KEY Actions secret.",
    "Populate the gitignored real tfvars (terraform.production.tfvars / terraform.testing.tfvars) "
    "on BOTH repos with the shared-project secret VALUES (DATABASE_PASSWORD, SUPABASE_JWT_SECRET, "
    "SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, RESEND_API_KEY). Never commit them.",
    "Confirm the founding-admin email exists in the shared Supabase auth.users "
    "(Dashboard -> Authentication -> Users) BEFORE the DDL 05_bootstrap_admin step, "
    "and set it in 05 (template ships founding-admin@example.com placeholder).",
    "Verify vars.API_URL / vars.API_URL_TESTING point at the deployed api Cloud Run URLs "
    "once the api is live (they gate the panel build + deploy workflows).",
]


def _path(run_dir: str) -> Path:
    return Path(run_dir).resolve() / STATE_FILE


def _load(run_dir: str) -> dict:
    p = _path(run_dir)
    if p.exists():
        return json.loads(p.read_text())
    return {"steps": {}}


def _save(run_dir: str, data: dict) -> None:
    _path(run_dir).write_text(json.dumps(data, indent=2))


def cmd_init(run_dir: str) -> None:
    data = _load(run_dir)
    for sid, _ in STEPS:
        data["steps"].setdefault(sid, {"status": "pending", "detail": ""})
    _save(run_dir, data)
    print(f"[state] initialised {len(STEPS)} steps at {_path(run_dir)}")


def cmd_set(run_dir: str, step: str, status: str, detail: str | None) -> None:
    if step not in STEP_LABELS:
        raise SystemExit(f"ABORT: unknown step '{step}'. Known: {', '.join(STEP_LABELS)}")
    if status not in {"pending", "done", "failed"}:
        raise SystemExit("ABORT: status must be pending|done|failed")
    data = _load(run_dir)
    data["steps"][step] = {"status": status, "detail": detail or data["steps"].get(step, {}).get("detail", "")}
    _save(run_dir, data)
    print(f"[state] {step} -> {status}")


def cmd_get(run_dir: str, step: str | None) -> None:
    data = _load(run_dir)
    if step:
        s = data["steps"].get(step, {"status": "pending", "detail": ""})
        print(f"{step}: {s['status']}" + (f" — {s['detail']}" if s.get("detail") else ""))
        return
    for sid, label in STEPS:
        s = data["steps"].get(sid, {"status": "pending"})
        mark = {"done": "x", "failed": "!", "pending": " "}.get(s["status"], " ")
        print(f"  [{mark}] {sid}: {s['status']} — {label}")


def cmd_checklist(run_dir: str, phase: str) -> None:
    data = _load(run_dir)
    if phase == "failure":
        remaining = [(sid, STEP_LABELS[sid]) for sid, _ in STEPS
                     if data["steps"].get(sid, {}).get("status") != "done"]
        print("## Remaining steps (run kept completed steps; resume here on re-run)\n")
        if not remaining:
            print("- (none — all steps report done; the failure was after the last tracked step)")
        for sid, label in remaining:
            st = data["steps"].get(sid, {}).get("status", "pending")
            print(f"- [ ] **{sid}** ({st}): {label}")
        print("\n## Manual residue (verify regardless)\n")
        for item in MANUAL_RESIDUE:
            print(f"- [ ] {item}")
    else:  # success
        print("## Instantiation complete — manual residue checklist\n")
        for item in MANUAL_RESIDUE:
            print(f"- [ ] {item}")
        done = sum(1 for sid, _ in STEPS if data["steps"].get(sid, {}).get("status") == "done")
        print(f"\n({done}/{len(STEPS)} automated steps recorded done.)")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("init"); pi.add_argument("--run-dir", required=True)
    ps = sub.add_parser("set")
    ps.add_argument("--run-dir", required=True); ps.add_argument("--step", required=True)
    ps.add_argument("--status", required=True); ps.add_argument("--detail", default=None)
    pg = sub.add_parser("get"); pg.add_argument("--run-dir", required=True); pg.add_argument("--step", default=None)
    pc = sub.add_parser("checklist")
    pc.add_argument("--run-dir", required=True); pc.add_argument("--phase", choices=["success", "failure"], default="failure")

    args = p.parse_args()
    if args.cmd == "init":
        cmd_init(args.run_dir)
    elif args.cmd == "set":
        cmd_set(args.run_dir, args.step, args.status, args.detail)
    elif args.cmd == "get":
        cmd_get(args.run_dir, args.step)
    elif args.cmd == "checklist":
        cmd_checklist(args.run_dir, args.phase)


if __name__ == "__main__":
    main()
