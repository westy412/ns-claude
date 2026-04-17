# Novosapien Claude Code Configuration

Shared agents and skills for the Novosapien team's Claude Code setup.

## What's Included

### Agents (11)
Custom agent definitions that extend Claude Code with specialised subagents:

| Agent | Purpose |
|-------|---------|
| `agent-spec-writer` | Write agent specification files from validated decisions |
| `agent-type-advisor` | Analyse agents and propose implementation type selections |
| `b2b-website-copywriter` | B2B copywriting for websites, blogs, landing pages |
| `code-reviewer` | Code quality, security, and best practices review |
| `codebase-researcher` | Explore and analyse codebases for patterns and architecture |
| `docs-creator` | Create/update documentation for agent repositories |
| `prompt-config-advisor` | Propose prompt configurations (framework, role, modifiers) |
| `prompt-creator` | Generate production-ready system prompts from specifications |
| `prompt-optimizer` | Optimise existing prompts |
| `team-spec-writer` | Write team-level spec files (team.md, agent-config.yaml) |
| `web-researcher` | Web research via Perplexity tools |

### Skills (38)
Skill directories providing domain knowledge and workflows. See `skills/*/SKILL.md` for each skill's documentation.

Key skill categories:
- **Agent building**: agent-spec-builder, agent-implementation-builder, agent-teams, individual-agents, agent-pattern-discovery
- **Spec building**: general-spec-builder, general-implementation-builder, review-agent-spec, review-general-spec
- **Frameworks**: dspy, langchain-deep-agents, langchain-mcp-adapters, inngest-workflow, remotion-best-practices
- **Prompts**: prompt-engineering, skill-builder, framework-skill-builder
- **Workflow**: discovery, brainstorm, teammate-spawn, research-orchestrator
- **DevOps**: cloudrun-deploy, setup-project, bug-hunter, prod-error
- **Product**: feature-impl, project-management, product-process-documentation, weekly-review, mobile-pwa-migration

---

## Setup

### Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and authenticated
- A [Perplexity API key](https://www.perplexity.ai/settings/api) (required for the `web-researcher` agent)

### Quick Setup

1. **Clone this repo** somewhere convenient:
   ```bash
   git clone https://github.com/westy412/ns-claude.git ~/ns-claude-config
   ```

2. **Run the setup script**:
   ```bash
   cd ~/ns-claude-config
   bash setup.sh
   ```

   The script will:
   - Back up your existing `~/.claude/agents/` and `~/.claude/skills/` if they exist
   - Copy agents and skills to `~/.claude/`
   - Create `~/.claude/settings.json` from the template (if you don't already have one)
   - Prompt you for your Perplexity API key

3. **Install required plugins** (run these in Claude Code):
   ```
   /install-plugin perplexity@perplexity-mcp-server
   ```

### Manual Setup

If you prefer to set things up yourself:

1. **Copy agents and skills**:
   ```bash
   cp -r agents/ ~/.claude/agents/
   cp -r skills/ ~/.claude/skills/
   ```

2. **Create your settings.json**:
   ```bash
   cp settings.json.example ~/.claude/settings.json
   ```
   Then edit `~/.claude/settings.json` and replace `<your-perplexity-api-key>` with your actual key.

3. **Install the Perplexity plugin** from within Claude Code:
   ```
   /install-plugin perplexity@perplexity-mcp-server
   ```

---

## Required MCP Integrations

### Perplexity (Required)
The `web-researcher` agent and several skills depend on Perplexity for web search.

- **Plugin**: `perplexity@perplexity-mcp-server` (from `perplexityai/modelcontextprotocol`)
- **API Key**: Set `PERPLEXITY_API_KEY` in your `settings.json` env block
- **Tools provided**: `perplexity_search`, `perplexity_ask`, `perplexity_research`, `perplexity_reason`

### Optional Integrations

These are used by specific skills and can be added later:

| Integration | Used By | Setup |
|-------------|---------|-------|
| **Notion** | `feature-impl` skill | Add `NOTION_API_KEY` to settings.json env |
| **Linear** | `project-management` skill | Install Linear MCP plugin |

---

## Updating

To pull the latest agents and skills:

```bash
cd ~/ns-claude-config
git pull
bash setup.sh
```

The setup script backs up your existing config before overwriting.

---

## Adding Your Own

- **Agents**: Add `.md` files to `agents/` following the existing frontmatter format
- **Skills**: Add directories to `skills/` with a `SKILL.md` file

To contribute back, commit and push to this repo.

## What's NOT in This Repo

The following are personal/local and excluded via `.gitignore`:
- `settings.json` (contains API keys)
- Keybindings, statusline scripts, commands
- Plugin cache and install state
- Session data, history, debug logs
- Teams (local team prompts)
