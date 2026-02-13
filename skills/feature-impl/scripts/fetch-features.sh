#!/usr/bin/env bash
set -euo pipefail

# Fetches features from a Notion database, optionally filtered by status.
# Can also fetch the page body (description) for a specific feature.
#
# Usage:
#   ./fetch-features.sh <database_id> [status_filter]
#   ./fetch-features.sh --page <page_id>
#
# status_filter: "all", "incomplete" (default), "not_started", "in_progress", "completed"
# --page: Fetch the body content of a specific feature page
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
  local status_filter="${2:-incomplete}"

  local filter_json
  case "$status_filter" in
    all)
      filter_json='{}'
      ;;
    incomplete)
      filter_json='{
        "filter": {
          "or": [
            { "property": "Status", "select": { "equals": "Not Started" } },
            { "property": "Status", "select": { "equals": "In Progress" } }
          ]
        }
      }'
      ;;
    not_started)
      filter_json='{
        "filter": {
          "property": "Status",
          "select": { "equals": "Not Started" }
        }
      }'
      ;;
    in_progress)
      filter_json='{
        "filter": {
          "property": "Status",
          "select": { "equals": "In Progress" }
        }
      }'
      ;;
    completed)
      filter_json='{
        "filter": {
          "property": "Status",
          "select": { "equals": "Completed" }
        }
      }'
      ;;
    *)
      echo "Error: Unknown status filter '$status_filter'" >&2
      echo "Valid options: all, incomplete, not_started, in_progress, completed" >&2
      exit 1
      ;;
  esac

  local response
  response=$(curl -s -X POST "$NOTION_API/databases/$database_id/query" \
    -H "Authorization: Bearer $NOTION_API_KEY" \
    -H "Notion-Version: $NOTION_VERSION" \
    -H "Content-Type: application/json" \
    -d "$filter_json")

  local error
  error=$(echo "$response" | jq -r '.object // empty')
  if [[ "$error" == "error" ]]; then
    echo "Error querying database:" >&2
    echo "$response" | jq '.' >&2
    exit 1
  fi

  echo "$response" | jq '[.results[] | {
    id: .id,
    name: ([.properties.Name.title[]?.plain_text] | join("")),
    status: .properties.Status.select.name,
    type: .properties.Type.select.name,
    priority: .properties.Priority.select.name,
    created: .created_time,
    last_edited: .last_edited_time,
    url: .url
  }]'
}

# Main
if [[ "${1:-}" == "--page" ]]; then
  if [[ -z "${2:-}" ]]; then
    echo "Error: --page requires a page_id argument" >&2
    exit 1
  fi
  fetch_page_content "$2"
elif [[ -n "${1:-}" ]]; then
  fetch_features "$1" "${2:-incomplete}"
else
  echo "Usage:" >&2
  echo "  $0 <database_id> [status_filter]    Fetch features from database" >&2
  echo "  $0 --page <page_id>                 Fetch page body content" >&2
  echo "" >&2
  echo "Status filters: all, incomplete (default), not_started, in_progress, completed" >&2
  exit 1
fi
