# Phase 1 — Instantiate the Server Repo

> **When to read:** First phase. Creates `novosapien/<client_slug>-vault-mcp`
> from the template and substitutes every parameter, gated twice.

---

## 1. Create the repo

`vault-mcp-template` is a GitHub template repo (private):

```bash
gh repo create Novosapien/<client_slug>-vault-mcp --private \
  --template Novosapien/vault-mcp-template --clone
```

## 2. Substitute parameters

The manifest is `template.params.json` in the repo root. Substitute every
param's default with the client value in every file the manifest lists.

| Param | Value rule | Notes |
|-------|-----------|-------|
| `display_name` | as elicited | e.g. `InPlay` |
| `client_slug` | lowercase, hyphens | e.g. `inplay` |
| `package_name` | `<client_slug>-vault-mcp` | `pyproject.toml` |
| `vault_repo` | `novosapien/<client_slug>-vault` | |
| `vault_repo_url` | `https://github.com/<vault_repo>` | also inside `.vault-mcp/deny.yml` |
| `service_name` | `<client_slug>-vault-mcp` | |
| `access_secret_id` | `<service_name>-access-secrets` | |
| `runtime_sa_id` | elicited, ≤30 chars | GCP hard cap |
| `egress_network_tag` | `vault-mcp-noegress` | FIXED — shared across clients, never rename |

**Never substitute** the `operatorFixed` values: org `Novosapien`, project
`coral-smoke-430718-p1`, region `us-east1`, AR repo `cloud-run-services`, the
WIF provider/SA, VPC `default`, firewall rule `vault-mcp-deny-all-egress`.

**Never edit** `template.params.json` or `scripts/grep_gate.py` during
substitution — both are self-excluded from the gate and must keep the original
tokens.

The files-touched list per param lives in the manifest itself — read it rather
than trusting a copy here; the manifest is the source of truth.

## 3. Lock, then gate — order is load-bearing

```bash
uv lock                          # pins package_name into uv.lock
python scripts/grep_gate.py      # zero-leftover gate; exit 0 = clean
```

Run the gate BEFORE `uv lock` and it fails on the lockfile (false failure).
Skip `uv lock` and the gate passes with the old name pinned (false pass).

The gate scans for every manifest default, the acme variants, and prior-client
tokens (`inplay`, `txn`, `caterer`, `totaljobs`, `meridian`, ...). Exit 1 =
leftovers listed; fix and re-run.

## 4. Placeholder check (the gate does not do this)

The grep gate scans for client TOKENS, not `${...}` placeholders. A literal
`${vault_repo_url}` survived it in the InPlay run. Always also run:

```bash
grep -rn '\${[a-z_]*}' --include='*' . \
  --exclude-dir=.git --exclude-dir=.venv --exclude=template.params.json \
  --exclude-dir=.github
```

Expect zero hits outside `.github/workflows/` (`${{ ... }}` GitHub expressions
are fine — the pattern above excludes that dir; eyeball anything else).

## 5. Known manifest drift

`template.params.json` may list `infrastructure/secrets.tf` — that file does
not exist; the secret data source lives in `infrastructure/main.tf`. Skip the
entry, don't create the file.

## 6. Commit

One commit, mirroring the InPlay shape
(`3db25ca "Instantiate vault-mcp-template for the InPlay vault"`):

```bash
git add -A && git commit -m "Instantiate vault-mcp-template for the <Display> vault"
```

Run the test suite before moving on: `uv run pytest -q` — expect the template's
full suite green (skips for missing ripgrep are fine locally).

Do NOT push yet if CI would deploy — the WIF allowlist (Phase 3) and the deny
list (Phase 2) must exist first. Push after Phase 3's provisioning, with the
operator's approval.
