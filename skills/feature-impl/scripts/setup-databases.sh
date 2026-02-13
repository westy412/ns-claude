#!/usr/bin/env bash
set -euo pipefail

# Creates "Improvements and Features" databases in each Notion product page.
# Reads product page IDs from config.json and writes back the generated database IDs.
#
# Usage: ./setup-databases.sh
# Requires: NOTION_API_KEY environment variable, jq

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../config.json"
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

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Error: config.json not found at $CONFIG_FILE" >&2
  exit 1
fi

create_database() {
  local page_id="$1"
  local product_name="$2"

  local response
  response=$(curl -s -X POST "$NOTION_API/databases" \
    -H "Authorization: Bearer $NOTION_API_KEY" \
    -H "Notion-Version: $NOTION_VERSION" \
    -H "Content-Type: application/json" \
    -d "{
      \"parent\": { \"type\": \"page_id\", \"page_id\": \"$page_id\" },
      \"title\": [
        {
          \"type\": \"text\",
          \"text\": { \"content\": \"Improvements and Features\" }
        }
      ],
      \"properties\": {
        \"Name\": {
          \"title\": {}
        },
        \"Status\": {
          \"select\": {
            \"options\": [
              { \"name\": \"Not Started\", \"color\": \"red\" },
              { \"name\": \"In Progress\", \"color\": \"yellow\" },
              { \"name\": \"Completed\", \"color\": \"green\" }
            ]
          }
        },
        \"Type\": {
          \"select\": {
            \"options\": [
              { \"name\": \"Feature\", \"color\": \"blue\" },
              { \"name\": \"Bug\", \"color\": \"red\" },
              { \"name\": \"Improvement\", \"color\": \"purple\" }
            ]
          }
        },
        \"Priority\": {
          \"select\": {
            \"options\": [
              { \"name\": \"High\", \"color\": \"red\" },
              { \"name\": \"Medium\", \"color\": \"yellow\" },
              { \"name\": \"Low\", \"color\": \"gray\" }
            ]
          }
        }
      }
    }")

  local db_id
  db_id=$(echo "$response" | jq -r '.id // empty')

  if [[ -z "$db_id" ]]; then
    echo "Error creating database for $product_name:" >&2
    echo "$response" | jq '.' >&2
    return 1
  fi

  echo "$db_id"
}

echo "Setting up Improvements and Features databases..."
echo ""

product_count=$(jq '.products | length' "$CONFIG_FILE")
tmp_config=$(mktemp)
cp "$CONFIG_FILE" "$tmp_config"

for i in $(seq 0 $((product_count - 1))); do
  name=$(jq -r ".products[$i].name" "$CONFIG_FILE")
  page_id=$(jq -r ".products[$i].page_id" "$CONFIG_FILE")
  existing_db_id=$(jq -r ".products[$i].database_id" "$CONFIG_FILE")

  if [[ "$existing_db_id" != "null" && "$existing_db_id" != "" && "$existing_db_id" != "<generated>" ]]; then
    echo "[$name] Already has database ID: $existing_db_id - skipping"
    continue
  fi

  echo "[$name] Creating database in page $page_id..."
  db_id=$(create_database "$page_id" "$name")
  echo "[$name] Created database: $db_id"

  tmp_config_next=$(mktemp)
  jq ".products[$i].database_id = \"$db_id\"" "$tmp_config" > "$tmp_config_next"
  mv "$tmp_config_next" "$tmp_config"
done

cp "$tmp_config" "$CONFIG_FILE"
rm -f "$tmp_config"

echo ""
echo "Setup complete. Database IDs written to config.json"
