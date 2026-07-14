#!/usr/bin/env bash
set -euo pipefail

# Fetches Content Creation Workforce user feedback from the in-app feedback
# dashboard (Supabase), which backs the app route /admin/feedback.
#
# Two tabs map to two Supabase tables:
#   feedback  -> bug_reports    (user-submitted feedback / feature requests)
#   issues    -> sentry_issues  (production errors ingested from Sentry)
#
# This is the CCW source of truth. The older Notion path (fetch-features.sh)
# is retained only for Inbound/Outbound Sales Workforce, which have no
# in-app dashboard.
#
# Usage:
#   ./fetch-feedback.sh [tab] [status_filter] [options]   # list items
#   ./fetch-feedback.sh --detail <id> [--tab <tab>]       # full record for one item
#
# tab: "feedback" (default, = bug_reports) | "issues" (= sentry_issues)
#
# status_filter (feedback): all | incomplete (default = pending+in_progress)
#                           | pending | in_progress | resolved | dismissed
# status_filter (issues):   all | incomplete (default = not fixed/dismissed)
#                           | pending | diagnosing | diagnosed | fixing | fixed | failed | dismissed
#
# Filter options (feedback tab, all AND together):
#   --filter-type <category>    bug | ux_issue | performance | data_accuracy | feature | improvement | other
#                               (also accepts Title-case: Bug, Feature, "UX Issue", ...)
#   --filter-page <route>       Filter by page_route (e.g. "/posts/[id]", "/nova/[id]")
#   --filter-component <comp>   Filter by AI-classified component
#   --filter-tag <tag>          Filter by tag (tags array contains)
#   --search <text>             Search title/description (case-insensitive contains)
#   --group-by <field>          Group by: component | type | page | status
#
# Filter options (issues tab):
#   --filter-level <level>      Filter by Sentry level (e.g. error, warning)
#   --filter-project <project>  Filter by Sentry project
#   --search <text>             Search title (case-insensitive contains)
#   --group-by <field>          Group by: level | project | status | event_type
#
# Credentials: SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY.
#   Resolved in order:
#     1. Already-exported env vars
#     2. --env-file <path>
#     3. $SUPABASE_ENV_FILE
#     4. First existing default API .env (see CANDIDATE_ENV_FILES below)
#
# Optional: FEEDBACK_DASHBOARD_BASE overrides the deep-link base
#           (default https://content.novosapien.ai).
#
# Requires: curl, jq

DASHBOARD_BASE="${FEEDBACK_DASHBOARD_BASE:-https://content.novosapien.ai}"

if ! command -v jq &>/dev/null; then
  echo "Error: jq is required but not installed" >&2
  exit 1
fi

# --- Credential resolution -------------------------------------------------

read_env_var() {
  # Extract KEY=value from a dotenv file without sourcing it (avoids executing
  # arbitrary lines). Strips surrounding quotes and trailing CR.
  local key="$1" file="$2" val
  val=$(grep -E "^[[:space:]]*${key}=" "$file" 2>/dev/null | tail -n1 | cut -d= -f2-)
  val="${val%$'\r'}"
  val="${val%\"}"; val="${val#\"}"
  val="${val%\'}"; val="${val#\'}"
  printf '%s' "$val"
}

resolve_credentials() {
  local env_file="${1:-}"

  # 1. Already exported.
  if [[ -n "${SUPABASE_URL:-}" && -n "${SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
    return 0
  fi

  # 2/3. Explicit flag, then env override.
  if [[ -z "$env_file" ]]; then
    env_file="${SUPABASE_ENV_FILE:-}"
  fi

  # 4. Default API .env locations.
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
    echo "Set SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY, or pass --env-file <path>," >&2
    echo "or place the ns-content-workforce-api/.env where it can be found." >&2
    exit 1
  fi

  SUPABASE_URL="$(read_env_var SUPABASE_URL "$env_file")"
  SUPABASE_SERVICE_ROLE_KEY="$(read_env_var SUPABASE_SERVICE_ROLE_KEY "$env_file")"

  if [[ -z "$SUPABASE_URL" || -z "$SUPABASE_SERVICE_ROLE_KEY" ]]; then
    echo "Error: SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not found in $env_file" >&2
    exit 1
  fi
}

# PostgREST GET helper. Args after the table are passed verbatim to curl as
# --data-urlencode pairs (so PostgREST filter syntax is encoded correctly).
pgrest_get() {
  local table="$1"; shift
  local args=()
  local p
  for p in "$@"; do args+=(--data-urlencode "$p"); done
  curl -s -G "${SUPABASE_URL}/rest/v1/${table}" \
    -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
    "${args[@]}"
}

# Verify a PostgREST response is a success array, not an error object.
assert_ok() {
  local response="$1"
  if echo "$response" | jq -e 'type == "object" and (has("code") or has("message"))' &>/dev/null; then
    echo "Error querying Supabase:" >&2
    echo "$response" | jq '.' >&2
    exit 1
  fi
}

# Normalise a category to the lowercase DB form (accepts Title-case input).
normalize_category() {
  local c="$1"
  c="$(printf '%s' "$c" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')"
  printf '%s' "$c"
}

# --- bug_reports (feedback tab) -------------------------------------------

BUG_SELECT="id,title,description,category,summary,component,tags,status,page_route,page_url,active_tab,reported_by_email,reported_by_name,created_at,updated_at"

fetch_feedback_list() {
  local status_filter="$1" type_filter="$2" page_filter="$3" \
        component_filter="$4" tag_filter="$5" search_filter="$6" group_by="$7"

  local params=("select=${BUG_SELECT}" "order=created_at.desc")

  case "$status_filter" in
    all) ;;
    incomplete)  params+=("status=in.(pending,in_progress)") ;;
    pending|in_progress|resolved|dismissed) params+=("status=eq.${status_filter}") ;;
    *)
      echo "Error: Unknown feedback status filter '$status_filter'" >&2
      echo "Valid: all, incomplete, pending, in_progress, resolved, dismissed" >&2
      exit 1
      ;;
  esac

  [[ -n "$type_filter" ]]      && params+=("category=eq.$(normalize_category "$type_filter")")
  [[ -n "$page_filter" ]]      && params+=("page_route=eq.${page_filter}")
  [[ -n "$component_filter" ]] && params+=("component=eq.${component_filter}")
  [[ -n "$tag_filter" ]]       && params+=("tags=cs.{${tag_filter}}")
  [[ -n "$search_filter" ]]    && params+=("or=(title.ilike.*${search_filter}*,description.ilike.*${search_filter}*)")

  local response
  response=$(pgrest_get bug_reports "${params[@]}")
  assert_ok "$response"

  # Normalise to a presentation-friendly shape (mirrors the Notion fetch shape
  # so the skill's table/grouping logic stays consistent).
  local normalized
  normalized=$(echo "$response" | jq --arg base "$DASHBOARD_BASE" '[.[] | {
    id: .id,
    name: (.title // (if (.description // "") == "" then "(no description)"
                      else (.description | split("\n")[0] | if length > 80 then .[0:80] + "…" else . end) end)),
    status: .status,
    type: .category,
    priority: null,
    page: .page_route,
    component: .component,
    tags: (.tags | if (. == null or length == 0) then null else . end),
    summary: (.summary | if (. == null or . == "") then null else . end),
    active_tab: .active_tab,
    page_url: .page_url,
    submitted_by: .reported_by_email,
    feature_id: null,
    created: .created_at,
    last_edited: .updated_at,
    url: ($base + "/admin/feedback?tab=bug-reports&id=" + .id)
  }]')

  apply_grouping "$normalized" "$group_by" "feedback"
}

# --- sentry_issues (issues tab) -------------------------------------------

SENTRY_SELECT="id,sentry_issue_id,title,project,environment,level,event_type,status,enrichment_where,enrichment_what,enrichment_impact,sentry_url,fix_session_id,created_at,updated_at"

fetch_issues_list() {
  local status_filter="$1" level_filter="$2" project_filter="$3" \
        search_filter="$4" group_by="$5"

  local params=("select=${SENTRY_SELECT}" "order=created_at.desc")

  case "$status_filter" in
    all) ;;
    incomplete) params+=("status=not.in.(fixed,dismissed)") ;;
    pending|diagnosing|diagnosed|fixing|fixed|failed|dismissed) params+=("status=eq.${status_filter}") ;;
    *)
      echo "Error: Unknown issues status filter '$status_filter'" >&2
      echo "Valid: all, incomplete, pending, diagnosing, diagnosed, fixing, fixed, failed, dismissed" >&2
      exit 1
      ;;
  esac

  [[ -n "$level_filter" ]]   && params+=("level=eq.${level_filter}")
  [[ -n "$project_filter" ]] && params+=("project=eq.${project_filter}")
  [[ -n "$search_filter" ]]  && params+=("title=ilike.*${search_filter}*")

  local response
  response=$(pgrest_get sentry_issues "${params[@]}")
  assert_ok "$response"

  local normalized
  normalized=$(echo "$response" | jq --arg base "$DASHBOARD_BASE" '[.[] | {
    id: .id,
    name: (.title // "(untitled issue)"),
    status: .status,
    type: "sentry",
    level: .level,
    project: .project,
    environment: .environment,
    event_type: .event_type,
    summary: (.enrichment_what // null),
    where: (.enrichment_where // null),
    impact: (.enrichment_impact // null),
    sentry_url: .sentry_url,
    created: .created_at,
    last_edited: .updated_at,
    url: ($base + "/admin/feedback?tab=issues&id=" + .id)
  }]')

  apply_grouping "$normalized" "$group_by" "issues"
}

# --- grouping --------------------------------------------------------------

apply_grouping() {
  local items="$1" group_by="$2" tab="$3"

  if [[ -z "$group_by" ]]; then
    echo "$items"
    return 0
  fi

  local key
  case "$tab:$group_by" in
    feedback:component) key="component" ;;
    feedback:type)      key="type" ;;
    feedback:page)      key="page" ;;
    feedback:status)    key="status" ;;
    issues:level)       key="level" ;;
    issues:project)     key="project" ;;
    issues:status)      key="status" ;;
    issues:event_type)  key="event_type" ;;
    *)
      echo "Error: Unknown group-by '$group_by' for tab '$tab'" >&2
      exit 1
      ;;
  esac

  echo "$items" | jq --arg k "$key" 'group_by(.[$k] // "Unclassified") | map({
    group: (.[0][$k] // "Unclassified"),
    count: length,
    items: .
  }) | sort_by(-.count)'
}

# --- detail mode -----------------------------------------------------------

fetch_detail() {
  local id="$1" tab="$2"
  local table query_tab
  case "$tab" in
    feedback) table="bug_reports"; query_tab="bug-reports" ;;
    issues)   table="sentry_issues"; query_tab="issues" ;;
    *) echo "Error: --tab must be 'feedback' or 'issues'" >&2; exit 1 ;;
  esac

  local response
  response=$(pgrest_get "$table" "select=*" "id=eq.${id}")
  assert_ok "$response"

  if [[ "$(echo "$response" | jq 'length')" -eq 0 ]]; then
    echo "Error: no $table row found with id '$id'" >&2
    exit 1
  fi

  echo "$response" | jq --arg base "$DASHBOARD_BASE" --arg t "$query_tab" \
    '.[0] as $r | $r + {dashboard_url: ($base + "/admin/feedback?tab=" + $t + "&id=" + $r.id)}'
}

# --- Argument parsing ------------------------------------------------------

ENV_FILE=""
TAB="feedback"
DETAIL_ID=""
STATUS_FILTER=""
type_filter=""; page_filter=""; component_filter=""; tag_filter=""
level_filter=""; project_filter=""; search_filter=""; group_by=""

# First pass: pull out --detail and global flags; collect the rest positionally.
positional=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --detail)     DETAIL_ID="${2:-}"; shift 2 ;;
    --tab)        TAB="${2:-}"; shift 2 ;;
    --env-file)   ENV_FILE="${2:-}"; shift 2 ;;
    --filter-type)      type_filter="${2:-}"; shift 2 ;;
    --filter-page)      page_filter="${2:-}"; shift 2 ;;
    --filter-component) component_filter="${2:-}"; shift 2 ;;
    --filter-tag)       tag_filter="${2:-}"; shift 2 ;;
    --filter-level)     level_filter="${2:-}"; shift 2 ;;
    --filter-project)   project_filter="${2:-}"; shift 2 ;;
    --search)           search_filter="${2:-}"; shift 2 ;;
    --group-by)         group_by="${2:-}"; shift 2 ;;
    --*)
      echo "Error: Unknown option '$1'" >&2
      exit 1
      ;;
    *) positional+=("$1"); shift ;;
  esac
done

# Positional args (list mode): [tab] [status_filter]
if [[ ${#positional[@]} -ge 1 ]]; then
  case "${positional[0]}" in
    feedback|issues) TAB="${positional[0]}"; positional=("${positional[@]:1}") ;;
  esac
fi
if [[ ${#positional[@]} -ge 1 ]]; then
  STATUS_FILTER="${positional[0]}"
fi

resolve_credentials "$ENV_FILE"

if [[ -n "$DETAIL_ID" ]]; then
  fetch_detail "$DETAIL_ID" "$TAB"
  exit 0
fi

STATUS_FILTER="${STATUS_FILTER:-incomplete}"

case "$TAB" in
  feedback)
    fetch_feedback_list "$STATUS_FILTER" "$type_filter" "$page_filter" \
      "$component_filter" "$tag_filter" "$search_filter" "$group_by"
    ;;
  issues)
    fetch_issues_list "$STATUS_FILTER" "$level_filter" "$project_filter" \
      "$search_filter" "$group_by"
    ;;
  *)
    echo "Error: tab must be 'feedback' or 'issues' (got '$TAB')" >&2
    exit 1
    ;;
esac
