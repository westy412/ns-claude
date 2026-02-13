#!/usr/bin/env bash
set -euo pipefail

# Updates a feature's status in Notion.
#
# Usage: ./update-status.sh <page_id> <status>
# Status values: "Not Started", "In Progress", "Completed"
#
# Requires: NOTION_API_KEY environment variable, jq

NOTION_API="https://api.notion.com/v1"
NOTION_VERSION="2022-06-28"

if [[ -z "${NOTION_API_KEY:-}" ]]; then
  echo "Error: NOTION_API_KEY environment variable is not set" >&2
  exit 1
fi

if [[ -z "${1:-}" || -z "${2:-}" ]]; then
  echo "Usage: $0 <page_id> <status>" >&2
  echo "Status values: \"Not Started\", \"In Progress\", \"Completed\"" >&2
  exit 1
fi

PAGE_ID="$1"
STATUS="$2"

case "$STATUS" in
  "Not Started"|"In Progress"|"Completed") ;;
  *)
    echo "Error: Invalid status '$STATUS'" >&2
    echo "Valid values: \"Not Started\", \"In Progress\", \"Completed\"" >&2
    exit 1
    ;;
esac

response=$(curl -s -X PATCH "$NOTION_API/pages/$PAGE_ID" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: $NOTION_VERSION" \
  -H "Content-Type: application/json" \
  -d "{
    \"properties\": {
      \"Status\": {
        \"select\": {
          \"name\": \"$STATUS\"
        }
      }
    }
  }")

error=$(echo "$response" | jq -r '.object // empty')
if [[ "$error" == "error" ]]; then
  echo "Error updating status:" >&2
  echo "$response" | jq '.' >&2
  exit 1
fi

name=$(echo "$response" | jq -r '[.properties.Name.title[]?.plain_text] | join("")')
echo "Updated \"$name\" to status: $STATUS"
