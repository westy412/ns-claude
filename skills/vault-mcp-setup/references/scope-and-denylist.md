# Phase 2 — Scope and the Deny List

> **When to read:** Second phase. What the server serves is a CLIENT-FACING
> decision — agree it in conversation before writing the deny list.

---

## The scope conversation

Ask the operator, concretely per vault:

1. **What is the content root?** The payload root is `<vault-repo>/vault/`
   (`VAULT_SUBDIR` in `scripts/build_payload.py`). Anything at the repo root is
   already outside scope. If the client vault keeps content at the repo root
   (newer vaults do), flag it — the template assumes `vault/` and the payload
   build must be checked against the real layout before Phase 3.
2. **What must clients never see?** Usual candidates: `drafts/**`, `private/**`,
   internal session logs. InPlay's answer: deny `drafts/**` only; `meetings/`
   and `components/**/sessions/` deliberately SERVED.
3. **Is there a sibling admin panel?** Its `brandConfig.vault.excludeDirs`
   (e.g. `inplay-admin-panel/scripts/sync-vault.ts`) is a SEPARATE exclusion
   list. Nothing reconciles the two — read it out to the operator and record
   the intended relationship in the deny file's comments.

## The file

`.vault-mcp/deny.yml`, committed in the **vault repo** (not the server repo —
the server repo's copy is only the seed to copy across).

```yaml
# What the MCP server must never serve. gitignore (gitwildmatch) semantics:
# a directory pattern denies its whole subtree.
deny:
  - drafts/**
allow_empty: false
```

- Schema: exactly two keys — `deny` (list of non-empty strings) and optional
  `allow_empty` (bool, default false). Anything else is rejected.
- Dialect: gitignore/gitwildmatch (`pathspec`). This is DELIBERATELY different
  from the `glob` tool's dialect — do not unify them.

## Fails-closed states — all eight

The build refuses to run on any of: file missing · file empty · malformed YAML ·
not a mapping · no `deny:` key · unknown top-level key · `deny: []` without
`allow_empty: true` · **any pattern matching zero committed files**.

That last one (EC10b) is the trap: a plausible pattern like `**/.obsidian/**`
fails the build when the vault gitignores those files — matched against the
COMMITTED tree, not the working tree. InPlay hit exactly this.

## Dry-run before anything is pushed

From a checkout of the vault repo at `origin/main`:

```bash
# every deny pattern must match at least one committed file
git ls-files | python3 -c "
import sys, yaml, pathspec
cfg = yaml.safe_load(open('.vault-mcp/deny.yml'))
files = [l.strip() for l in sys.stdin]
for pat in cfg['deny']:
    spec = pathspec.PathSpec.from_lines('gitignore', [pat])
    n = sum(1 for f in files if spec.match_file(f))
    print(('OK  ' if n else 'ZERO-MATCH  ') + f'{pat}: {n} files')
"
```

Any `ZERO-MATCH` line means the build will fail closed — fix the pattern or
drop it before committing.

## What is excluded regardless

Two classes are stripped BEFORE the deny list is consulted (never rely on the
deny list for these, and never try to re-include them):

- Secrets: `.env*`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.keystore`,
  `id_rsa*`, `id_ed25519*`, `*credentials*.json`, `*.tfstate`
- Junk: images, `*.pyc`, `.DS_Store`, `*.lock`

## Commit

The deny file is committed to the vault repo with the operator's diff approval
(vault pushes are gated like any other). Do NOT wire the notify workflow yet —
that is Phase 4, after the server exists.
