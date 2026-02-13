---
name: feature-impl
description: "Fetch feature requests and improvements from Notion product databases. Select features to work on, review their details, then hand off to the discovery skill for exploration. Works with Content Creation Workforce, Inbound Sales Workforce, and Outbound Sales Workforce."
allowed-tools: Read, Glob, Grep, Task, AskUserQuestion, Write, Edit, Bash, Skill
---

# Feature Implementation Skill

## Purpose

The front door to working on features. Pulls incomplete features from Notion databases (one per product), helps prioritize and select which to work on, then hands off to the **discovery** skill with full context for exploration and discovery document creation.

**Pipeline:**
```
feature-impl → discovery → spec-builder → implementation
(this skill)   (thinking)   (spec creation)  (code)
```

**This skill handles:**
- Fetching features from Notion databases
- Presenting and prioritizing the backlog
- Feature selection and detail review
- Status tracking in Notion
- Context handoff to discovery

**This skill does NOT handle:**
- Discovery conversation (that's the discovery skill)
- Spec creation (that's the spec-builders)
- Implementation (that's the implementation builders)

---

## Prerequisites

### Environment
- `NOTION_API_KEY` must be set in environment (configured in `~/.claude/settings.json` env vars)

### First-Time Setup
If databases haven't been created yet (`config.json` has null database_id values), run the setup script:

```bash
~/.claude/skills/feature-impl/scripts/setup-databases.sh
```

This creates an "Improvements and Features" database inside each product page in Notion.

### Configuration
Product and database IDs are stored in:
```
~/.claude/skills/feature-impl/config.json
```

---

## Products

| Product | Description |
|---------|-------------|
| **Content Creation Workforce** | Turn-key content factory for multi-platform content (Substack, YouTube, LinkedIn, TikTok, Twitter/X, Facebook) |
| **Inbound Sales Workforce** | Inbound lead handling and conversion |
| **Outbound Sales Workforce** | Autonomous B2B outreach across email and phone channels |

---

## Workflow

### Phase 0: Prerequisites Check

1. Verify `NOTION_API_KEY` is available:
```bash
echo "${NOTION_API_KEY:+set}" || echo "not set"
```

2. Read config to check database IDs are populated:
```bash
cat ~/.claude/skills/feature-impl/config.json
```

3. If any `database_id` is null, inform the user setup needs to run first and offer to run it.

### Phase 1: Product Selection

Present the three products and ask which one to work on:

> "Which product do you want to work on features for?"
> 1. Content Creation Workforce
> 2. Inbound Sales Workforce
> 3. Outbound Sales Workforce

Use AskUserQuestion to let the user pick.

### Phase 2: Fetch Features

Run the fetch script for the selected product's database:

```bash
~/.claude/skills/feature-impl/scripts/fetch-features.sh <database_id> incomplete
```

This returns all features with status "Not Started" or "In Progress".

**Present the results as a clean table:**

```
| # | Name | Type | Priority | Status |
|---|------|------|----------|--------|
| 1 | Feature name | Feature | High | Not Started |
| 2 | Bug description | Bug | Medium | In Progress |
```

If there are no features, let the user know the backlog is empty and ask if they want to check a different product.

### Phase 3: Feature Selection & Detail Review

Ask the user which feature(s) they want to work on.

For each selected feature, fetch its page body to get the full description:

```bash
~/.claude/skills/feature-impl/scripts/fetch-features.sh --page <feature_page_id>
```

Present the full description content to the user.

Ask if they want to update the feature's status to "In Progress":

```bash
~/.claude/skills/feature-impl/scripts/update-status.sh <page_id> "In Progress"
```

### Phase 4: Handoff to Discovery

Once the user has selected and reviewed a feature, prepare the handoff to the **discovery** skill.

**Summarize the context for discovery:**

Present a clear summary to the user that includes:
- **Product:** Which product this feature belongs to
- **Feature name:** From the Notion database title
- **Type:** Feature / Bug / Improvement
- **Priority:** High / Medium / Low
- **Description:** Full page body content from Notion
- **Notion URL:** Link back to the original feature page

**Then invoke the discovery skill:**

```
Skill tool → skill: "discovery"
```

The discovery skill will take over from here - it handles:
- The thinking partner conversation
- Research (codebase and web)
- Convergence and checkpoint
- Discovery document creation
- Handoff to spec-builders (general-spec-builder or agent-spec-builder)

**Before invoking discovery, tell the user:**

> "Here's the feature context I'll carry into discovery:
>
> **[Feature Name]** ([Type] | [Priority])
> **Product:** [Product Name]
> **Description:** [Summary of page body]
> **Notion:** [URL]
>
> I'm now handing off to the discovery skill to explore this feature in depth. The discovery skill will help flesh out the idea and produce a discovery document for spec creation."

---

## Post-Discovery: Status Update

After the discovery skill completes and a discovery document is produced, the user may want to come back to this skill to:

1. Mark the feature as "Completed" in Notion (if fully spec'd):
```bash
~/.claude/skills/feature-impl/scripts/update-status.sh <page_id> "Completed"
```

2. Pick another feature from the backlog and repeat the process.

---

## Anti-Patterns

| Anti-Pattern | Why It's Bad |
|--------------|--------------|
| **Skip fetching features** | The whole point is to work from the Notion backlog |
| **Start discovery without handoff** | Use the discovery skill, don't duplicate it |
| **Skip the detail review** | Always fetch page body before handing off - context matters |
| **Forget to update status** | Notion should reflect what's being worked on |

---

## Script Reference

All scripts are in `~/.claude/skills/feature-impl/scripts/`

**setup-databases.sh** — One-time setup
```bash
~/.claude/skills/feature-impl/scripts/setup-databases.sh
```

**fetch-features.sh** — Query features
```bash
# Fetch incomplete features from a database
~/.claude/skills/feature-impl/scripts/fetch-features.sh <database_id> [status_filter]

# Fetch a feature's page body (description)
~/.claude/skills/feature-impl/scripts/fetch-features.sh --page <page_id>

# Status filters: all, incomplete (default), not_started, in_progress, completed
```

**update-status.sh** — Update feature status
```bash
~/.claude/skills/feature-impl/scripts/update-status.sh <page_id> "In Progress"
# Valid statuses: "Not Started", "In Progress", "Completed"
```
