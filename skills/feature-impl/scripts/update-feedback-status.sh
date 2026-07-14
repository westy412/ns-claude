#!/usr/bin/env bash
set -euo pipefail

# Updates the status of a Content Creation Workforce feedback item in Supabase
# (the in-app /admin/feedback dashboard). Equivalent of update-status.sh, but
# for the bug_reports / sentry_issues tables rather than Notion.
#
# Usage:
#   ./update-feedback-status.sh <id> <status> [--tab feedback|issues] [--env-file <path>]
#
# tab "feedback" (default) -> bug_reports table
#   valid statuses: pending | in_progress | resolved | dismissed
#
# tab "issues" -> sentry_issues table
#   valid statuses: pending | diagnosing | diagnosed | fixing | fixed | failed | dismissed
#   (Note: the dashboard normally drives Sentry status via its own
#    Diagnose/Fix/Dismiss actions; set status directly only for manual triage.)
#
# Credentials: SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY, resolved the same way
# as fetch-feedback.sh (exported env, --env-file, $SUPABASE_ENV_FILE, or the
# default ns-content-workforce-api/.env locations).
#
# Requires: curl, jq

if ! command -v jq &>/dev/null; then
  echo "Error: jq is required but not installed" >&2
  exit 1
fi

read_env_var() {
  local key="$1" file="$2" val
  val=$(grep -E "^[[:space:]]*${key}=" "$file" 2>/dev/null | tail -n1 | cut -d= -f2-)
  val="${val%$'\r'}"
  val="${val%\"}"; val="${val#\"}"
  val="${val%\'}"; val="${val#\'}"
  printf '%s' "$val"
}

resolve_credentials() {
  local env_file="${1:-}"
  if [[ -n "${SUPABASE_URL:-}" && -n "${SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
    return 0
  fi
  if [[ -z "$env_file" ]]; then env_file="${SUPABASE_ENV_FILE:-}"; fi
  if [[ -z "$env_file" ]]; then
    local candidates=(
      "$HOME/Programming/novosapien/ns-content-workforce/ns-content-workforce-api/.env"
      "$PWD/ns-content-workforce-api/.env"
      "$PWD/../ns-content-workforce-api/.env"
      "$PWD/.env"
    )
    local c
    for c in "${candidates[@]}"; do
      if [[ -f "$c" ]]; then env_file="$c"; break; fi
    done
  fi
  if [[ -z "$env_file" || ! -f "$env_file" ]]; then
    echo "Error: could not resolve Supabase credentials." >&2
    echo "Set SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY, or pass --env-file <path>." >&2
    exit 1
  fi
  SUPABASE_URL="$(read_env_var SUPABASE_URL "$env_file")"
  SUPABASE_SERVICE_ROLE_KEY="$(read_env_var SUPABASE_SERVICE_ROLE_KEY "$env_file")"
  if [[ -z "$SUPABASE_URL" || -z "$SUPABASE_SERVICE_ROLE_KEY" ]]; then
    echo "Error: SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not found in $env_file" >&2
    exit 1
  fi
}

# --- Argument parsing ---

ENV_FILE=""
TAB="feedback"
ID=""
STATUS=""
positional=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --tab)      TAB="${2:-}"; shift 2 ;;
    --env-file) ENV_FILE="${2:-}"; shift 2 ;;
    --*) echo "Error: Unknown option '$1'" >&2; exit 1 ;;
    *) positional+=("$1"); shift ;;
  esac
done

ID="${positional[0]:-}"
STATUS="${positional[1]:-}"

if [[ -z "$ID" || -z "$STATUS" ]]; then
  echo "Usage: $0 <id> <status> [--tab feedback|issues] [--env-file <path>]" >&2
  echo "feedback statuses: pending, in_progress, resolved, dismissed" >&2
  echo "issues statuses:   pending, diagnosing, diagnosed, fixing, fixed, failed, dismissed" >&2
  exit 1
fi

case "$TAB" in
  feedback)
    TABLE="bug_reports"
    case "$STATUS" in
      pending|in_progress|resolved|dismissed) ;;
      *) echo "Error: invalid feedback status '$STATUS'" >&2
         echo "Valid: pending, in_progress, resolved, dismissed" >&2; exit 1 ;;
    esac
    ;;
  issues)
    TABLE="sentry_issues"
    case "$STATUS" in
      pending|diagnosing|diagnosed|fixing|fixed|failed|dismissed) ;;
      *) echo "Error: invalid issues status '$STATUS'" >&2
         echo "Valid: pending, diagnosing, diagnosed, fixing, fixed, failed, dismissed" >&2; exit 1 ;;
    esac
    ;;
  *) echo "Error: --tab must be 'feedback' or 'issues'" >&2; exit 1 ;;
esac

resolve_credentials "$ENV_FILE"

response=$(curl -s -X PATCH "${SUPABASE_URL}/rest/v1/${TABLE}?id=eq.${ID}" \
  -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "{\"status\":\"${STATUS}\"}")

if echo "$response" | jq -e 'type == "object" and (has("code") or has("message"))' &>/dev/null; then
  echo "Error updating status:" >&2
  echo "$response" | jq '.' >&2
  exit 1
fi

if [[ "$(echo "$response" | jq 'length')" -eq 0 ]]; then
  echo "Error: no $TABLE row found with id '$ID'" >&2
  exit 1
fi

name=$(echo "$response" | jq -r '.[0].title // .[0].description // "(item)" | if type=="string" and length>60 then .[0:60]+"…" else . end')
echo "Updated \"$name\" ($TABLE) to status: $STATUS"
