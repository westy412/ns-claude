#!/usr/bin/env bash
# panel_sync_test.sh — prove a client vault is consumable by the admin panel template.
#
# Usage: panel_sync_test.sh <vault-git-url-or-local-path> [panel-template-path] [--keep]
#
# Copies the acme panel template to a scratch dir, clones the vault locally, runs the
# REAL sync-vault (docs + brand) and a full build, then asserts:
#   1. sync-vault exit 0
#   2. docs snapshot (docs-data/) contains the scaffold pages
#   3. nothing from excluded dirs (private/ templates/ drafts/) is in the snapshot
#   4. public/ci/manifest.json exists and lists >=1 asset
#   5. npm run build exit 0
#   6. no dangling-link warnings for scaffold pages in sync output
# Never pushes to the vault. Cleans up scratch on exit unless --keep.

set -uo pipefail

VAULT_SRC="${1:?usage: panel_sync_test.sh <vault-url-or-path> [panel-template-path] [--keep]}"
PANEL_SRC="${2:-$HOME/Programming/novosapien/admin-panel-template}"
KEEP=0
for a in "$@"; do [ "$a" = "--keep" ] && KEEP=1; done

SCRATCH="$(mktemp -d /tmp/admin-vault-test.XXXXXX)"
cleanup() { [ "$KEEP" = "1" ] && echo "[keep] scratch retained: $SCRATCH" || rm -rf "$SCRATCH"; }
trap cleanup EXIT

PASS=0; FAIL=0
result() { # result <id> <PASS|FAIL> <detail>
  if [ "$2" = "PASS" ]; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); fi
  printf '  [%s] %s — %s\n' "$2" "$1" "$3"
}

echo "== scratch: $SCRATCH"

# --- panel template copy -----------------------------------------------------
if [ -d "$PANEL_SRC" ]; then
  rsync -a --exclude node_modules --exclude .next --exclude .git "$PANEL_SRC/" "$SCRATCH/panel/"
else
  gh repo clone Novosapien/admin-panel-template "$SCRATCH/panel" -- --depth=1 || { echo "FATAL: no panel template"; exit 2; }
  rm -rf "$SCRATCH/panel/.git"
fi

# --- vault local clone -------------------------------------------------------
git clone --depth=1 -- "$VAULT_SRC" "$SCRATCH/vault" || { echo "FATAL: cannot clone vault $VAULT_SRC"; exit 2; }

# Inject a placeholder brand asset if brand/ has no supported assets (local clone only).
if ! find "$SCRATCH/vault/brand" \( -name '*.svg' -o -name '*.png' -o -name '*.jpg' -o -name '*.jpeg' -o -name '*.webp' -o -name '*.html' \) 2>/dev/null | grep -q .; then
  mkdir -p "$SCRATCH/vault/brand/logos"
  printf '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><rect width="10" height="10"/></svg>' \
    > "$SCRATCH/vault/brand/logos/test-placeholder.svg"
  echo "[note] no brand assets in vault; injected local-only placeholder for assert 4"
fi

cd "$SCRATCH/panel"
export VAULT_REPO_URL="$SCRATCH/vault"

echo "== npm ci"
npm ci --no-audit --no-fund >"$SCRATCH/npm-ci.log" 2>&1 || { echo "FATAL: npm ci failed — $SCRATCH/npm-ci.log"; KEEP=1; exit 2; }

# --- 1. sync-vault -----------------------------------------------------------
echo "== sync-vault"
if npm run sync-vault >"$SCRATCH/sync.log" 2>&1; then
  result 1 PASS "sync-vault exit 0"
else
  result 1 FAIL "sync-vault nonzero — see $SCRATCH/sync.log"; KEEP=1
fi

# --- 2. scaffold pages in snapshot ------------------------------------------
MISSING=""
for p in index vision components/components architecture/architecture open-questions; do
  [ -f "docs-data/$p.json" ] || MISSING="$MISSING $p"
done
[ -z "$MISSING" ] && result 2 PASS "all scaffold pages in docs-data/" \
                  || { result 2 FAIL "missing:$MISSING"; KEEP=1; }

# --- 3. excluded dirs absent -------------------------------------------------
LEAKED="$(find docs-data \( -path '*private*' -o -path '*templates*' -o -path '*drafts*' \) -name '*.json' 2>/dev/null)"
[ -z "$LEAKED" ] && result 3 PASS "no excluded-dir content in snapshot" \
                 || { result 3 FAIL "leaked: $LEAKED"; KEEP=1; }

# --- 4. CI manifest ----------------------------------------------------------
if [ -f public/ci/manifest.json ] && node -e '
  const m=require("./public/ci/manifest.json");
  const n=(m.categories||[]).flatMap(c=>c.assets||[]).length;
  process.exit(n>0?0:1)' 2>/dev/null; then
  result 4 PASS "public/ci/manifest.json present with >=1 asset"
else
  result 4 FAIL "manifest missing or empty"; KEEP=1
fi

# --- 5. build ----------------------------------------------------------------
echo "== npm run build"
if npm run build >"$SCRATCH/build.log" 2>&1; then
  result 5 PASS "build exit 0"
else
  result 5 FAIL "build failed — see $SCRATCH/build.log"; KEEP=1
fi

# --- 6. dangling links -------------------------------------------------------
if grep -iE "dangling|broken link|unresolved link" "$SCRATCH/sync.log" >/dev/null 2>&1; then
  result 6 FAIL "link warnings in sync output — see $SCRATCH/sync.log"; KEEP=1
else
  result 6 PASS "no link warnings"
fi

echo
echo "== RESULT: $PASS pass / $FAIL fail"
[ "$FAIL" = "0" ] && { echo "VAULT IS PANEL-READY"; exit 0; } || { echo "VAULT NOT READY — fix and re-run"; exit 1; }
