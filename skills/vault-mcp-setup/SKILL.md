---
description: Stand up a client vault MCP server from vault-mcp-template — instantiate the scaffold, agree the served/denied scope, provision GCP, wire the vault-repo dispatch, deploy, and hand the connector to the client. Use when a client vault needs its MCP server, when onboarding a new client to the claude.ai connector, or to re-run a broken setup. NOT for vault content work (descriptions, product skills) and NOT for the admin panel (use admin-panel-instantiate).
argument-hint: "[client display name or vault repo]"
---

> **Invoke with:** `/vault-mcp-setup` | **Keywords:** vault mcp, mcp server setup, client connector, instantiate vault-mcp-template

Stand up a **client vault MCP server**: a Cloud Run service built from
`vault-mcp-template` that serves a filtered snapshot of the client's vault to
claude.ai over MCP (five tools: `glob`, `grep`, `read`, `links`, `shell`).

The template documents 7 prose steps. The first real run (InPlay, 2026-08-04) hit
a dozen undocumented steps and two CI-breaking traps. This skill is the runbook
that closes those gaps. Follow the phases in order — the ordering constraints are
load-bearing, not stylistic.

## When to Use

- A client vault exists (or is being created with `vault-setup`) and needs its
  MCP server + claude.ai connector.
- A previous setup run failed partway — the phases are safe to re-enter.

**Skip when:**
- Working on vault CONTENT (rules, descriptions, extractions) — that is the
  product skill family's job.
- Setting up the admin panel/portal — use `admin-panel-instantiate`.
- Changing server behavior — edit `vault-mcp-template`, then sync instances.

## Inputs to Elicit First

Ask for these before touching anything. Derive what is derivable; confirm the rest.

| Input | Derivation | Example (InPlay) |
|-------|-----------|------------------|
| `display_name` | prompted | `InPlay` |
| `client_slug` | display name lowercased, spaces→hyphens | `inplay` |
| `vault_repo` | `novosapien/<client_slug>-vault` — confirm it exists | `novosapien/inplay-vault` |
| `service_name` | `<client_slug>-vault-mcp` | `inplay-vault-mcp` |
| `runtime_sa_id` | `<client_slug>-vmcp-runtime`, MUST be ≤30 chars — confirm | `inplay-vmcp-runtime` |
| Scope: what is served | conversation — see the scope reference | `vault/` minus `drafts/**` |
| Scope: what is denied | conversation — deny list entries | `drafts/**` |
| Sibling panel repo | prompted, may be none — for excludeDirs reconciliation | `inplay-admin-panel` |
| Secret policy | one shared secret per client (house default) or per-person | shared |

## Phases

Work through the references in order. Each has its own gates.

| Phase | What | Reference |
|-------|------|-----------|
| 1 | Create the server repo from the template, substitute params, `uv lock`, grep gate + placeholder check | `references/instantiate.md` |
| 2 | Agree scope with the operator, author `.vault-mcp/deny.yml`, dry-run it against the vault's committed tree | `references/scope-and-denylist.md` |
| 3 | GCP: secret, service account, WIF allowlist, terraform (two-pass bootstrap), first deploy | `references/provision-and-deploy.md` |
| 4 | Vault repo: notify workflow + the PAT human gate | `references/vault-wiring.md` |
| 5 | Assemble the connector URL, package the companion skill, hand off to the client | `references/client-handoff.md` |

## Hard Gates (never skip)

1. **`uv lock` BEFORE `grep_gate.py`** — before it: false failure; skipping it:
   false pass.
2. **Placeholder check** — the grep gate scans for client tokens, not `${...}`
   placeholders. Run the separate check in `references/instantiate.md`.
3. **Deny-list dry-run before the first push** — any pattern matching zero
   committed files fails the build closed (EC10b). InPlay hit this with
   `**/.obsidian/**`.
4. **WIF repo allowlist before the first CI deploy** — the new server repo must
   be added to the workload-identity provider condition AND the SA binding, or
   CI auth fails exactly the way InPlay's did.
5. **The PAT is a human step** — a fine-grained PAT cannot be minted by API.
   Stop and ask the operator to mint it; give the exact scope and both
   `gh secret set` targets.
6. **Dispatch wiring LAST** — never wire `notify-mcp.yml` before a valid deny
   list exists in the vault repo, or the first push builds an unfiltered vault.
7. **Human approval before every push and every deploy** — the vault repo and
   the server repo are both production surfaces.

## Out of Scope

- Vault content: description frontmatter, extraction rules, the product skill
  family. Those evolve during vault building, not here.
- The admin panel and its sync (`admin-panel-instantiate`).
- Server feature changes (edit `vault-mcp-template`; sync instances like
  `eb8fd81`/`a4945ea` did).
- Secret rotation tooling and per-person revocation — a shared secret has
  neither; say so at handoff (see `references/client-handoff.md`).

## Execution

Run shell steps directly with the platform's shell tool. Delegate nothing —
this is a sequential runbook with human gates, not a fan-out job. When a step
needs the operator (PAT mint, diff approval, scope decisions), stop and ask;
never proceed on a guess.
