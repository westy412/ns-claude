#!/usr/bin/env bash
set -euo pipefail

# Fetches features from a Notion database with optional filtering and grouping.
# Can also fetch the page body (description) for a specific feature.
#
# Usage:
#   ./fetch-features.sh <database_id> [status_filter] [options]
#   ./fetch-features.sh --page <page_id>
#
# status_filter: "all", "incomplete" (default), "not_started", "in_progress", "completed"
#
# Filter options (can be combined, all AND together):
#   --filter-page <page>            Filter by app page (e.g. "/posts/[id]")
#   --filter-priority <priority>    Filter by priority ("High", "Medium", "Low")
#   --filter-type <type>            Filter by type ("Feature", "Bug", "Improvement", etc.)
#   --filter-component <component>  Filter by AI-classified component (e.g. "Content Drafting")
#   --filter-tag <tag>              Filter by tag (e.g. "slow-loading", "image-generation")
#   --search <text>                 Search by name (case-insensitive contains)
#   --group-by <field>              Group results by field: "component", "type", "page", "priority"
#   --page                          Fetch body content of a specific feature page
#
# Requires: NOTION_API_KEY environment variable, jq

NOTION_API="https://api.notion.com/v1"
NOTION_VERSION="2022-06-28"

if [[ -z "${NOTION_API_KEY:-}" ]]; then
  echo "Error: NOTION_API_KEY environment variable is not set" >&2
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "Error: jq is required but not installed" >&2
  exit 1
fi

fetch_page_content() {
  local page_id="$1"

  local response
  response=$(curl -s "$NOTION_API/blocks/$page_id/children?page_size=100" \
    -H "Authorization: Bearer $NOTION_API_KEY" \
    -H "Notion-Version: $NOTION_VERSION")

  echo "$response" | jq '[.results[] | {
    type: .type,
    text: (
      if .type == "paragraph" then
        ([.paragraph.rich_text[]?.plain_text] | join(""))
      elif .type == "heading_1" then
        ([.heading_1.rich_text[]?.plain_text] | join(""))
      elif .type == "heading_2" then
        ([.heading_2.rich_text[]?.plain_text] | join(""))
      elif .type == "heading_3" then
        ([.heading_3.rich_text[]?.plain_text] | join(""))
      elif .type == "bulleted_list_item" then
        ([.bulleted_list_item.rich_text[]?.plain_text] | join(""))
      elif .type == "numbered_list_item" then
        ([.numbered_list_item.rich_text[]?.plain_text] | join(""))
      elif .type == "to_do" then
        ([.to_do.rich_text[]?.plain_text] | join(""))
      elif .type == "code" then
        ([.code.rich_text[]?.plain_text] | join(""))
      else
        null
      end
    )
  } | select(.text != null and .text != "")]'
}

fetch_features() {
  local database_id="$1"
  local status_filter="$2"
  local page_filter="$3"
  local priority_filter="$4"
  local type_filter="$5"
  local search_filter="$6"
  local component_filter="$7"
  local tag_filter="$8"
  local group_by="$9"

  # Build array of filter conditions
  local conditions=()

  # Status condition
  case "$status_filter" in
    all)
      ;; # no status filter
    incomplete)
      conditions+=('{"or":[{"property":"Status","select":{"equals":"Not Started"}},{"property":"Status","select":{"equals":"In Progress"}}]}')
      ;;
    not_started)
      conditions+=('{"property":"Status","select":{"equals":"Not Started"}}')
      ;;
    in_progress)
      conditions+=('{"property":"Status","select":{"equals":"In Progress"}}')
      ;;
    completed)
      conditions+=('{"property":"Status","select":{"equals":"Completed"}}')
      ;;
    *)
      echo "Error: Unknown status filter '$status_filter'" >&2
      echo "Valid options: all, incomplete, not_started, in_progress, completed" >&2
      exit 1
      ;;
  esac

  # Page condition
  if [[ -n "$page_filter" ]]; then
    conditions+=("{\"property\":\"Page\",\"select\":{\"equals\":\"$page_filter\"}}")
  fi

  # Priority condition
  if [[ -n "$priority_filter" ]]; then
    conditions+=("{\"property\":\"Priority\",\"select\":{\"equals\":\"$priority_filter\"}}")
  fi

  # Type condition
  if [[ -n "$type_filter" ]]; then
    conditions+=("{\"property\":\"Type\",\"select\":{\"equals\":\"$type_filter\"}}")
  fi

  # Component condition
  if [[ -n "$component_filter" ]]; then
    conditions+=("{\"property\":\"Component\",\"select\":{\"equals\":\"$component_filter\"}}")
  fi

  # Tag condition (multi_select contains)
  if [[ -n "$tag_filter" ]]; then
    conditions+=("{\"property\":\"Tags\",\"multi_select\":{\"contains\":\"$tag_filter\"}}")
  fi

  # Name search condition
  if [[ -n "$search_filter" ]]; then
    conditions+=("{\"property\":\"Name\",\"title\":{\"contains\":\"$search_filter\"}}")
  fi

  # Build final filter JSON
  local filter_json
  if [[ ${#conditions[@]} -eq 0 ]]; then
    filter_json='{}'
  elif [[ ${#conditions[@]} -eq 1 ]]; then
    filter_json="{\"filter\":${conditions[0]}}"
  else
    local joined
    joined=$(IFS=,; echo "${conditions[*]}")
    filter_json="{\"filter\":{\"and\":[$joined]}}"
  fi

  # Paginate through all results
  local all_results="[]"
  local has_more="true"
  local start_cursor=""

  while [[ "$has_more" == "true" ]]; do
    local request_body="$filter_json"

    # Add pagination cursor if we have one
    if [[ -n "$start_cursor" ]]; then
      request_body=$(echo "$request_body" | jq --arg cursor "$start_cursor" '. + {start_cursor: $cursor}')
    fi

    local response
    response=$(curl -s -X POST "$NOTION_API/databases/$database_id/query" \
      -H "Authorization: Bearer $NOTION_API_KEY" \
      -H "Notion-Version: $NOTION_VERSION" \
      -H "Content-Type: application/json" \
      -d "$request_body")

    local error
    error=$(echo "$response" | jq -r '.object // empty')
    if [[ "$error" == "error" ]]; then
      echo "Error querying database:" >&2
      echo "$response" | jq '.' >&2
      exit 1
    fi

    # Extract results from this page
    local page_results
    page_results=$(echo "$response" | jq '[.results[] | {
      id: .id,
      name: ([.properties.Name.title[]?.plain_text] | join("")),
      status: .properties.Status.select.name,
      type: .properties.Type.select.name,
      priority: .properties.Priority.select.name,
      page: (.properties.Page.select.name // null),
      component: (.properties.Component.select.name // null),
      tags: ([.properties.Tags.multi_select[]?.name] | if length == 0 then null else . end),
      summary: ([.properties.Summary.rich_text[]?.plain_text] | join("") | if . == "" then null else . end),
      active_tab: (.properties."Active Tab".select.name // null),
      page_url: (.properties.URL.url // null),
      submitted_by: (.properties."Submitted By".email // null),
      feature_id: ([.properties.ID.rich_text[]?.plain_text] | join("") | if . == "" then null else . end),
      created: .created_time,
      last_edited: .last_edited_time,
      url: .url
    }]')

    # Merge into accumulated results
    all_results=$(echo "$all_results" "$page_results" | jq -s '.[0] + .[1]')

    # Check for more pages
    has_more=$(echo "$response" | jq -r '.has_more')
    start_cursor=$(echo "$response" | jq -r '.next_cursor // empty')
  done

  # Apply grouping if requested
  if [[ -n "$group_by" ]]; then
    case "$group_by" in
      component)
        echo "$all_results" | jq 'group_by(.component // "Unclassified") | map({
          group: (.[0].component // "Unclassified"),
          count: length,
          items: .
        }) | sort_by(-.count)'
        ;;
      type)
        echo "$all_results" | jq 'group_by(.type) | map({
          group: .[0].type,
          count: length,
          items: .
        }) | sort_by(-.count)'
        ;;
      page)
        echo "$all_results" | jq 'group_by(.page // "No Page") | map({
          group: (.[0].page // "No Page"),
          count: length,
          items: .
        }) | sort_by(-.count)'
        ;;
      priority)
        echo "$all_results" | jq 'group_by(.priority) | map({
          group: .[0].priority,
          count: length,
          items: .
        }) | sort_by(-.count)'
        ;;
      *)
        echo "Error: Unknown group-by field '$group_by'" >&2
        echo "Valid options: component, type, page, priority" >&2
        exit 1
        ;;
    esac
  else
    echo "$all_results"
  fi
}

# --- Argument parsing ---

if [[ "${1:-}" == "--page" ]]; then
  if [[ -z "${2:-}" ]]; then
    echo "Error: --page requires a page_id argument" >&2
    exit 1
  fi
  fetch_page_content "$2"
elif [[ -n "${1:-}" ]]; then
  database_id="$1"
  shift

  # Second positional arg is status filter (if it doesn't start with --)
  status_filter="incomplete"
  if [[ -n "${1:-}" && "${1:0:2}" != "--" ]]; then
    status_filter="$1"
    shift
  fi

  # Parse optional named filters
  page_filter=""
  priority_filter=""
  type_filter=""
  search_filter=""
  component_filter=""
  tag_filter=""
  group_by=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --filter-page)
        page_filter="${2:-}"
        shift 2
        ;;
      --filter-priority)
        priority_filter="${2:-}"
        shift 2
        ;;
      --filter-type)
        type_filter="${2:-}"
        shift 2
        ;;
      --filter-component)
        component_filter="${2:-}"
        shift 2
        ;;
      --filter-tag)
        tag_filter="${2:-}"
        shift 2
        ;;
      --search)
        search_filter="${2:-}"
        shift 2
        ;;
      --group-by)
        group_by="${2:-}"
        shift 2
        ;;
      *)
        echo "Error: Unknown option '$1'" >&2
        echo "Valid options: --filter-page, --filter-priority, --filter-type, --filter-component, --filter-tag, --search, --group-by" >&2
        exit 1
        ;;
    esac
  done

  fetch_features "$database_id" "$status_filter" "$page_filter" "$priority_filter" "$type_filter" "$search_filter" "$component_filter" "$tag_filter" "$group_by"
else
  echo "Usage:" >&2
  echo "  $0 <database_id> [status_filter] [options]    Fetch features from database" >&2
  echo "  $0 --page <page_id>                           Fetch page body content" >&2
  echo "" >&2
  echo "Status filters: all, incomplete (default), not_started, in_progress, completed" >&2
  echo "" >&2
  echo "Filter options:" >&2
  echo "  --filter-page <page>            Filter by app page (e.g. /posts/[id])" >&2
  echo "  --filter-priority <priority>    Filter by priority (High, Medium, Low)" >&2
  echo "  --filter-type <type>            Filter by type (Feature, Bug, Improvement, UX Issue)" >&2
  echo "  --filter-component <component>  Filter by AI component (e.g. Content Drafting, Hooks)" >&2
  echo "  --filter-tag <tag>              Filter by tag (e.g. slow-loading, image-generation)" >&2
  echo "  --search <text>                 Search by name (contains)" >&2
  echo "  --group-by <field>              Group by: component, type, page, priority" >&2
  exit 1
fi
