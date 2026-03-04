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

## Product References

For Content Creation Workforce, read the product reference file for detailed context on pages, components, user workflows, and common pain points:

```
~/.claude/skills/feature-impl/references/content-workforce.md
```

This reference helps you understand what each Page and Component means when filtering or reviewing features. Read it at the start of each session working on Content Creation Workforce features.

For Inbound and Outbound Sales Workforce, reference files do not exist yet. Use the database properties as the primary context source.

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

**Check if the user wants to filter or group.** If the user mentioned a specific page, component, tag, priority, type, or search term, apply filters. If they want to see features grouped (e.g., "group by component"), use `--group-by`.

**Basic fetch (no filters):**
```bash
~/.claude/skills/feature-impl/scripts/fetch-features.sh <database_id> incomplete
```

**Filtered fetch examples:**
```bash
# Only features for a specific page
~/.claude/skills/feature-impl/scripts/fetch-features.sh <database_id> incomplete --filter-page "/posts/[id]"

# Only image-related issues
~/.claude/skills/feature-impl/scripts/fetch-features.sh <database_id> incomplete --filter-component "Images & Image Generation"

# Only items tagged "slow-loading"
~/.claude/skills/feature-impl/scripts/fetch-features.sh <database_id> incomplete --filter-tag "slow-loading"

# Only bugs
~/.claude/skills/feature-impl/scripts/fetch-features.sh <database_id> incomplete --filter-type "Bug"

# Only high priority items
~/.claude/skills/feature-impl/scripts/fetch-features.sh <database_id> incomplete --filter-priority "High"

# Search by name
~/.claude/skills/feature-impl/scripts/fetch-features.sh <database_id> incomplete --search "carousel"

# Combine filters (e.g. all image-generation issues)
~/.claude/skills/feature-impl/scripts/fetch-features.sh <database_id> incomplete --filter-tag "image-generation"
```

**Grouped fetch examples:**
```bash
# Group incomplete features by component
~/.claude/skills/feature-impl/scripts/fetch-features.sh <database_id> incomplete --group-by component

# Group all bugs by page
~/.claude/skills/feature-impl/scripts/fetch-features.sh <database_id> incomplete --filter-type "Bug" --group-by page

# Group high priority items by component
~/.claude/skills/feature-impl/scripts/fetch-features.sh <database_id> incomplete --filter-priority "High" --group-by component
```

**Available filters:**

| Filter | Flag | Values |
|--------|------|--------|
| Page | `--filter-page` | `/dashboard`, `/posts/[id]`, `/campaigns/[id]`, `/settings/brand-guidelines`, etc. |
| Component | `--filter-component` | `Content Drafting`, `Images & Image Generation`, `Hooks`, `Carousel`, etc. |
| Tag | `--filter-tag` | `slow-loading`, `image-generation`, `formatting`, `ui-alignment`, etc. |
| Priority | `--filter-priority` | `High`, `Medium`, `Low` |
| Type | `--filter-type` | `Feature`, `Bug`, `Improvement`, `UX Issue`, `Performance`, `Data/Accuracy`, `Other` |
| Name search | `--search` | Any text (case-insensitive contains) |

**Grouping options:**

| Flag | Groups By |
|------|-----------|
| `--group-by component` | AI-classified component (functional area) |
| `--group-by type` | Feature, Bug, Improvement, etc. |
| `--group-by page` | App page/route |
| `--group-by priority` | High, Medium, Low |

All filters are optional and can be combined. They AND together with the status filter.

**Presenting results:**

**Without grouping** — present as a table with new columns for summary, component, and tags:

```
| # | ID | Name | Component | Tags | Type | Priority | Status | Page |
|---|----|------|-----------|------|------|----------|--------|------|
| 1 | CCW-042 | Add bulk image upload | Images & Image Generation | image-upload, bulk-actions | Feature | High | Not Started | /posts/[id] |
| 2 | CCW-043 | Slow carousel rendering | Carousel | slow-loading, performance | Performance | Medium | Not Started | /posts/[id] |
```

**With grouping** — present grouped by the specified field:

```
Content Drafting (5 items):
  - CCW-010: Draft editor loses formatting on save
  - CCW-015: Add markdown preview to content tab
  ...

Images & Image Generation (3 items):
  - CCW-042: Add bulk image upload
  - CCW-044: Images don't match brand style
  ...
```

For each item in a group, show the Name, ID, Summary (if available), Type, Priority, and Status.

Note: `ID`, `Component`, `Tags`, `Summary`, `Active Tab`, `Page`, and `Submitted By` may be null for older features (before the AI analysis system was added). Display "-" or "Unclassified" for null values.

If there are no features, let the user know the backlog is empty and ask if they want to check a different product or adjust filters.

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
- **Type:** Feature / Bug / Improvement / UX Issue
- **Priority:** High / Medium / Low
- **Page:** Which app page this relates to (if set)
- **Submitted By:** Email of the submitter (if set)
- **Feature ID:** Internal reference ID (if set)
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
> **Page:** [Page, if set]
> **Submitted By:** [Email, if set]
> **Feature ID:** [ID, if set]
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

**fetch-features.sh** — Query features with optional filtering and grouping
```bash
# Fetch incomplete features from a database
~/.claude/skills/feature-impl/scripts/fetch-features.sh <database_id> [status_filter] [filter_options]

# Fetch a feature's page body (description)
~/.claude/skills/feature-impl/scripts/fetch-features.sh --page <page_id>

# Status filters: all, incomplete (default), not_started, in_progress, completed

# Filter options (can be combined):
#   --filter-page <page>            e.g. "/posts/[id]", "/settings/brand-guidelines"
#   --filter-component <component>  e.g. "Content Drafting", "Images & Image Generation"
#   --filter-tag <tag>              e.g. "slow-loading", "image-generation"
#   --filter-priority <priority>    e.g. "High", "Medium", "Low"
#   --filter-type <type>            e.g. "Feature", "Bug", "Improvement", "UX Issue"
#   --search <text>                 Name search (case-insensitive contains)
#   --group-by <field>              Group by: component, type, page, priority

# Examples:
~/.claude/skills/feature-impl/scripts/fetch-features.sh <db_id> incomplete --filter-component "Images & Image Generation"
~/.claude/skills/feature-impl/scripts/fetch-features.sh <db_id> incomplete --filter-tag "slow-loading"
~/.claude/skills/feature-impl/scripts/fetch-features.sh <db_id> incomplete --filter-type "Bug" --group-by component
~/.claude/skills/feature-impl/scripts/fetch-features.sh <db_id> incomplete --group-by component
```

**update-status.sh** — Update feature status
```bash
~/.claude/skills/feature-impl/scripts/update-status.sh <page_id> "In Progress"
# Valid statuses: "Not Started", "In Progress", "Completed"
```

**reindex-ids.sh** — Assign sequential IDs to all features
```bash
~/.claude/skills/feature-impl/scripts/reindex-ids.sh <database_id> <prefix>

# Prefixes by product:
#   CCW  Content Creation Workforce
#   ISW  Inbound Sales Workforce
#   OSW  Outbound Sales Workforce

# Example: assigns CCW-001, CCW-002, ... sorted by creation date
~/.claude/skills/feature-impl/scripts/reindex-ids.sh 3057fe58-6c3b-8121-9317-e093935fae3b CCW
```
