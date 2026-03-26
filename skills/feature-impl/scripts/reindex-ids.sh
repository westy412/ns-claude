#!/usr/bin/env bash
set -euo pipefail

# Assigns sequential IDs to all features in a Notion database.
# Sorts by created_time and assigns IDs like CCW-001, CCW-002, etc.
#
# Usage: ./reindex-ids.sh <database_id> <prefix>
#
# Example:
#   ./reindex-ids.sh 3057fe58-6c3b-8121-9317-e093935fae3b CCW
#   → Assigns CCW-001, CCW-002, ... sorted by creation date
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

if [[ -z "${1:-}" || -z "${2:-}" ]]; then
  echo "Usage: $0 <database_id> <prefix>" >&2
  echo "" >&2
  echo "Prefixes by product:" >&2
  echo "  CCW  Content Creation Workforce" >&2
  echo "  ISW  Inbound Sales Workforce" >&2
  echo "  OSW  Outbound Sales Workforce" >&2
  echo "" >&2
  echo "Example: $0 3057fe58-... CCW" >&2
  echo "  → CCW-001, CCW-002, ..." >&2
  exit 1
fi

DATABASE_ID="$1"
PREFIX="$2"

# Fetch all entries sorted by created_time
echo "Fetching all entries from database..."
response=$(curl -s -X POST "$NOTION_API/databases/$DATABASE_ID/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: $NOTION_VERSION" \
  -H "Content-Type: application/json" \
  -d '{"sorts":[{"timestamp":"created_time","direction":"ascending"}]}')

error=$(echo "$response" | jq -r '.object // empty')
if [[ "$error" == "error" ]]; then
  echo "Error querying database:" >&2
  echo "$response" | jq '.' >&2
  exit 1
fi

# Extract page IDs and names in creation order
entries=$(echo "$response" | jq -r '.results[] | [.id, ([.properties.Name.title[]?.plain_text] | join(""))] | @tsv')

if [[ -z "$entries" ]]; then
  echo "No entries found in database."
  exit 0
fi

total=$(echo "$entries" | wc -l | tr -d ' ')
echo "Found $total entries. Assigning IDs: $PREFIX-001 through $PREFIX-$(printf '%03d' "$total")"
echo ""

counter=0
while IFS=$'\t' read -r page_id name; do
  counter=$((counter + 1))
  new_id=$(printf '%s-%03d' "$PREFIX" "$counter")

  echo "[$new_id] ${name:0:60}"

  update_response=$(curl -s -X PATCH "$NOTION_API/pages/$page_id" \
    -H "Authorization: Bearer $NOTION_API_KEY" \
    -H "Notion-Version: $NOTION_VERSION" \
    -H "Content-Type: application/json" \
    -d "{
      \"properties\": {
        \"ID\": {
          \"rich_text\": [
            {
              \"type\": \"text\",
              \"text\": { \"content\": \"$new_id\" }
            }
          ]
        }
      }
    }")

  update_error=$(echo "$update_response" | jq -r '.object // empty')
  if [[ "$update_error" == "error" ]]; then
    echo "  ERROR: $(echo "$update_response" | jq -r '.message')" >&2
  fi
done <<< "$entries"

echo ""
echo "Done. Assigned $counter IDs ($PREFIX-001 to $(printf '%s-%03d' "$PREFIX" "$counter"))"
