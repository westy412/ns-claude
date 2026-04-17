#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=== Novosapien Claude Code Setup ==="
echo ""

# Check Claude Code exists
if ! command -v claude &> /dev/null; then
    echo "Warning: 'claude' CLI not found. Install Claude Code first:"
    echo "  https://docs.anthropic.com/en/docs/claude-code"
    echo ""
fi

# Create ~/.claude if it doesn't exist
if [ ! -d "$CLAUDE_DIR" ]; then
    echo "Creating $CLAUDE_DIR..."
    mkdir -p "$CLAUDE_DIR"
fi

# Backup existing agents
if [ -d "$CLAUDE_DIR/agents" ] && [ "$(ls -A "$CLAUDE_DIR/agents" 2>/dev/null)" ]; then
    if [ "$CLAUDE_DIR/agents" != "$SCRIPT_DIR/agents" ]; then
        echo "Backing up existing agents to $CLAUDE_DIR/backups/agents_$TIMESTAMP/"
        mkdir -p "$CLAUDE_DIR/backups/agents_$TIMESTAMP"
        cp -r "$CLAUDE_DIR/agents/"* "$CLAUDE_DIR/backups/agents_$TIMESTAMP/"
    fi
fi

# Backup existing skills
if [ -d "$CLAUDE_DIR/skills" ] && [ "$(ls -A "$CLAUDE_DIR/skills" 2>/dev/null)" ]; then
    if [ "$CLAUDE_DIR/skills" != "$SCRIPT_DIR/skills" ]; then
        echo "Backing up existing skills to $CLAUDE_DIR/backups/skills_$TIMESTAMP/"
        mkdir -p "$CLAUDE_DIR/backups/skills_$TIMESTAMP"
        cp -r "$CLAUDE_DIR/skills/"* "$CLAUDE_DIR/backups/skills_$TIMESTAMP/"
    fi
fi

# Copy agents
echo "Copying agents..."
mkdir -p "$CLAUDE_DIR/agents"
cp -r "$SCRIPT_DIR/agents/"*.md "$CLAUDE_DIR/agents/" 2>/dev/null || true
echo "  Copied $(ls "$SCRIPT_DIR/agents/"*.md 2>/dev/null | wc -l | tr -d ' ') agent definitions"

# Copy skills
echo "Copying skills..."
mkdir -p "$CLAUDE_DIR/skills"
for skill_dir in "$SCRIPT_DIR/skills"/*/; do
    skill_name=$(basename "$skill_dir")
    if [ "$skill_name" = ".DS_Store" ]; then continue; fi
    cp -r "$skill_dir" "$CLAUDE_DIR/skills/"
done
echo "  Copied $(ls -d "$SCRIPT_DIR/skills"/*/ 2>/dev/null | wc -l | tr -d ' ') skills"

# Settings
if [ ! -f "$CLAUDE_DIR/settings.json" ]; then
    echo ""
    echo "No settings.json found. Creating from template..."
    cp "$SCRIPT_DIR/settings.json.example" "$CLAUDE_DIR/settings.json"

    # Prompt for Perplexity API key
    echo ""
    read -rp "Enter your Perplexity API key (or press Enter to skip): " PPLX_KEY
    if [ -n "$PPLX_KEY" ]; then
        if command -v sed &> /dev/null; then
            sed -i.bak "s/<your-perplexity-api-key>/$PPLX_KEY/" "$CLAUDE_DIR/settings.json"
            rm -f "$CLAUDE_DIR/settings.json.bak"
        fi
        echo "  API key set in settings.json"
    else
        echo "  Skipped. Edit ~/.claude/settings.json later to add your key."
    fi
else
    echo ""
    echo "settings.json already exists - not overwriting."
    echo "  Compare with settings.json.example if you want to update your config."
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Install the Perplexity plugin in Claude Code:"
echo "     /install-plugin perplexity@perplexity-mcp-server"
echo ""
echo "  2. If you haven't set your Perplexity API key, edit:"
echo "     ~/.claude/settings.json"
echo ""
echo "  3. Optional: Install additional plugins for full functionality:"
echo "     - Linear MCP (for project-management skill)"
echo "     - Notion API key (for feature-impl skill)"
echo ""
echo "Restart Claude Code to pick up the new agents and skills."
