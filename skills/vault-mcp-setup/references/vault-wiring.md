# Phase 4 — Wire the Vault Repo

> **When to read:** Fourth phase, AFTER the server deploys and a valid deny
> list is committed in the vault repo. Wiring earlier means the first vault
> push builds from a repo with no deny list — which fails closed at best.

The vault repo needs exactly three things. It needs NO GCP access.

---

## 1. The notify workflow

Copy `templates/notify-mcp.yml` from this skill into the vault repo at
`.github/workflows/notify-mcp.yml`, substituting `<client_slug>` (two places:
the dispatch URL and the fallback warning). It fires on every push to `main`
and posts `repository_dispatch: vault-updated` to the server repo, which
rebuilds and redeploys (~5 min push-to-serving).

Behavior encoded in the template — keep it:
- With `MCP_DISPATCH_TOKEN`: strict — a failed dispatch fails the workflow.
- With only a panel PAT fallback: best-effort — warns, stays green.
- With neither: warns loudly and exits 0. The server then serves a frozen
  snapshot (it stamps a staleness notice after 48h).

## 2. The PAT — a human gate, no way around it

A fine-grained PAT cannot be minted through any API. Stop and ask the operator
to create one at github.com → Settings → Developer settings → Fine-grained
tokens:

- **Repository access:** both `novosapien/<client_slug>-vault` and
  `novosapien/<client_slug>-vault-mcp`
- **Permissions:** Contents — Read and write
- Name suggestion: `vault-mcp-pipeline-<client_slug>`; InPlay's has no expiry —
  flag the tradeoff and let the operator choose.

(An existing `vault-mcp-pipeline` PAT can be extended to the new repos instead —
operator's call.)

## 3. Both repo secrets — the same PAT, two names

```bash
gh secret set MCP_DISPATCH_TOKEN --repo novosapien/<client_slug>-vault      --body '<pat>'
gh secret set VAULT_READ_TOKEN   --repo novosapien/<client_slug>-vault-mcp  --body '<pat>'
```

- `MCP_DISPATCH_TOKEN` lets the vault workflow dispatch cross-repo (the default
  `GITHUB_TOKEN` cannot).
- `VAULT_READ_TOKEN` lets the server's CI check the vault out at build time.

## 4. Prove the loop

Trigger once by hand and watch it end to end:

```bash
gh workflow run notify-mcp.yml --repo novosapien/<client_slug>-vault
gh run watch --repo novosapien/<client_slug>-vault-mcp --exit-status <run-id>
```

Success = the server repo's `build-deploy` run goes green INCLUDING its
serving-revision poll, and `/health` answers. Then make a trivial vault edit,
push through the normal gated flow, and confirm the same chain fires on a real
push.
