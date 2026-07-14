---
name: feature-impl
description: "Fetch user feedback and feature requests, select what to work on, review details, then hand off to the discovery skill for exploration. Content Creation Workforce reads from the in-app feedback dashboard (Supabase); Inbound and Outbound Sales Workforce read from Notion."
allowed-tools: Read, Glob, Grep, Task, AskUserQuestion, Write, Edit, Bash, Skill
---

# Feature Implementation Skill

## Purpose

The front door to working on features. Pulls incomplete feedback / feature requests from each product's backlog, helps prioritize and select what to work on, then hands off to the **discovery** skill with full context for exploration and discovery document creation.

**Pipeline:**
```
feature-impl → discovery → spec-builder → implementation
(this skill)   (thinking)   (spec creation)  (code)
```

**This skill handles:**
- Fetching feedback from each product's source (in-app dashboard or Notion)
- Presenting and prioritizing the backlog
- Feature selection and detail review
- Status tracking back in the source
- Context handoff to discovery

**This skill does NOT handle:**
- Discovery conversation (that's the discovery skill)
- Spec creation (that's the spec-builders)
- Implementation (that's the implementation builders)

---

## Data Sources (read this first)

There are **two separate backlog systems**, and the source depends on the product:

| Product | Source | Where it lives | Backed by |
|---------|--------|----------------|-----------|
| **Content Creation Workforce** | **In-app feedback dashboard** | App route `/admin/feedback` | Supabase tables `bug_reports` + `sentry_issues` |
| **Inbound Sales Workforce** | Notion | "Improvements and Features" DB | Notion |
| **Outbound Sales Workforce** | Notion | "Improvements and Features" DB | Notion |

**Content Creation Workforce now collects feedback in-app, not in Notion.** Users submit via the in-app feedback widget, which writes to the Supabase `bug_reports` table; production errors flow into `sentry_issues`. Both surface in the `/admin/feedback` dashboard. The legacy CCW Notion DB is **not synced** to this — historical Notion items are frozen and CCW work should be driven from the dashboard. Inbound/Outbound have no in-app dashboard yet, so they stay on Notion.

The CCW dashboard has **two tabs**, which map to the `--tab` flag on `fetch-feedback.sh`:

| Tab | `--tab` value | Supabase table | What it is |
|-----|---------------|----------------|------------|
| **User Feedback** | `feedback` (default) | `bug_reports` | User-submitted feedback / feature requests, AI-enriched (title, summary, component, tags) |
| **Issues** | `issues` | `sentry_issues` | Production errors ingested from Sentry, with AI enrichment + auto-fix lifecycle |

---

## Prerequisites

### Environment
- **Content Creation Workforce** — needs `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY`. By default these are read from the backend API repo's `.env` (`ns-content-workforce-api/.env`); no extra setup needed when that repo is present locally. Override the location with `--env-file <path>` or `$SUPABASE_ENV_FILE`, or export the two vars directly. Deep-link base is `https://content.novosapien.ai` by default; override with `$FEEDBACK_DASHBOARD_BASE` (e.g. `http://localhost:3400` for local).
- **Inbound / Outbound Sales Workforce** — needs `NOTION_API_KEY` (configured in `~/.claude/settings.json` env vars).

### First-Time Setup (Notion products only)
If the Notion databases for Inbound/Outbound haven't been created yet (`config.json` has null `database_id` values), run the setup script:

```bash
~/.claude/skills/feature-impl/scripts/setup-databases.sh
```

This creates an "Improvements and Features" database inside each product page in Notion. CCW does **not** use this — its source is Supabase.

### Configuration
Product config (sources, page IDs, Notion DB IDs) is stored in:
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

This reference helps you understand what each Page and Component means when filtering or reviewing feedback. Read it at the start of each session working on Content Creation Workforce features.

For Inbound and Outbound Sales Workforce, reference files do not exist yet. Use the database properties as the primary context source.

---

## Workflow

### Phase 0: Prerequisites Check

1. Read config to see each product's source:
```bash
cat ~/.claude/skills/feature-impl/config.json
```

2. Verify credentials for the product you'll work on:
```bash
# CCW (Supabase) — confirm the API .env is reachable (or the vars are exported)
ls ~/Programming/novosapien/ns-content-workforce/ns-content-workforce-api/.env 2>/dev/null && echo "api .env found" || echo "set --env-file or SUPABASE_* vars"

# Inbound / Outbound (Notion)
echo "${NOTION_API_KEY:+set}" || echo "not set"
```

3. For Notion products, if any `database_id` is null, inform the user setup needs to run first and offer to run it.

### Phase 1: Product Selection

Present the three products and ask which one to work on:

> "Which product do you want to work on features for?"
> 1. Content Creation Workforce
> 2. Inbound Sales Workforce
> 3. Outbound Sales Workforce

Use AskUserQuestion to let the user pick. The chosen product determines the source (see Data Sources).

### Phase 2: Fetch Features

**Check if the user wants to filter or group.** If the user mentioned a specific page, component, tag, type, or search term, apply filters. If they want results grouped, use `--group-by`.

#### Content Creation Workforce → `fetch-feedback.sh` (Supabase)

Default tab is `feedback` (user-submitted). Use `--tab issues` for Sentry production errors.

```bash
# Incomplete user feedback (status pending + in_progress)
~/.claude/skills/feature-impl/scripts/fetch-feedback.sh feedback incomplete

# Filter by app page (page_route)
~/.claude/skills/feature-impl/scripts/fetch-feedback.sh feedback incomplete --filter-page "/posts/[id]"

# Filter by type (category)
~/.claude/skills/feature-impl/scripts/fetch-feedback.sh feedback incomplete --filter-type "Bug"

# Filter by AI component
~/.claude/skills/feature-impl/scripts/fetch-feedback.sh feedback incomplete --filter-component "Images & Image Generation"

# Filter by tag
~/.claude/skills/feature-impl/scripts/fetch-feedback.sh feedback incomplete --filter-tag "image-generation"

# Search title/description
~/.claude/skills/feature-impl/scripts/fetch-feedback.sh feedback all --search "carousel"

# Group incomplete feedback by component
~/.claude/skills/feature-impl/scripts/fetch-feedback.sh feedback incomplete --group-by component

# Sentry production issues (Issues tab), incomplete = not fixed/dismissed
~/.claude/skills/feature-impl/scripts/fetch-feedback.sh issues incomplete
~/.claude/skills/feature-impl/scripts/fetch-feedback.sh issues incomplete --group-by status
```

**CCW status filters:**

| Tab | Statuses |
|-----|----------|
| `feedback` | `all`, `incomplete` (default = pending + in_progress), `pending`, `in_progress`, `resolved`, `dismissed` |
| `issues` | `all`, `incomplete` (default = not fixed/dismissed), `pending`, `diagnosing`, `diagnosed`, `fixing`, `fixed`, `failed`, `dismissed` |

**CCW filters (feedback tab):**

| Filter | Flag | Values |
|--------|------|--------|
| Page | `--filter-page` | `page_route`, e.g. `/posts/[id]`, `/nova/[id]`, `/dashboard` |
| Type | `--filter-type` | `Bug`, `UX Issue`, `Performance`, `Data/Accuracy`, `Feature`, `Improvement`, `Other` (lowercased/normalized automatically) |
| Component | `--filter-component` | AI-classified component, e.g. `Images & Image Generation`, `Hooks` |
| Tag | `--filter-tag` | e.g. `slow-loading`, `image-generation` |
| Name search | `--search` | Any text — matches title or description (case-insensitive) |
| Group by | `--group-by` | `component`, `type`, `page`, `status` |

Issues tab supports `--filter-level`, `--filter-project`, `--search` (title), and `--group-by level|project|status|event_type`.

> **Note:** CCW feedback has no `priority` field (that only existed in Notion). The `priority` column comes back `null` — display "-".

#### Inbound / Outbound Sales Workforce → `fetch-features.sh` (Notion)

```bash
# Basic fetch (no filters)
~/.claude/skills/feature-impl/scripts/fetch-features.sh <database_id> incomplete

# Filtered / grouped (same flags as before)
~/.claude/skills/feature-impl/scripts/fetch-features.sh <database_id> incomplete --filter-type "Bug" --group-by component
```

Notion status filters: `all`, `incomplete` (default), `not_started`, `in_progress`, `completed`. Notion filters: `--filter-page`, `--filter-component`, `--filter-tag`, `--filter-priority`, `--filter-type`, `--search`, `--group-by component|type|page|priority`.

**Presenting results:**

**Without grouping** — present as a table:

```
| # | Name | Component | Tags | Type | Status | Page | Submitted By |
|---|------|-----------|------|------|--------|------|--------------|
| 1 | Add bulk image upload | Images & Image Generation | image-upload | feature | pending | /posts/[id] | user@example.com |
| 2 | Slow carousel rendering | Carousel | slow-loading | performance | pending | /posts/[id] | user@example.com |
```

(For Notion products, include `ID` and `Priority` columns too — those fields exist there.)

**With grouping** — present grouped by the specified field:

```
Images & Image Generation (3 items):
  - Add bulk image upload (feature, pending)
  - Images don't match brand style (bug, pending)
  ...
```

For each item, show the Name, Summary (if available), Type, Status, and Page.

Note: `Component`, `Tags`, `Summary`, `Active Tab` may be null for items the AI analysis hasn't classified. Display "-" or "Unclassified" for null values.

If there are no items, let the user know the backlog is empty and ask if they want to check a different product, tab, or adjust filters.

### Phase 3: Feature Selection & Detail Review

Ask the user which item(s) they want to work on.

For each selected item, fetch the full record:

```bash
# CCW (Supabase) — full row incl. description, console_logs, page_context, screenshot_url
~/.claude/skills/feature-impl/scripts/fetch-feedback.sh --detail <id>
# (Sentry issue: add --tab issues)
~/.claude/skills/feature-impl/scripts/fetch-feedback.sh --detail <id> --tab issues

# Inbound / Outbound (Notion) — page body
~/.claude/skills/feature-impl/scripts/fetch-features.sh --page <feature_page_id>
```

Present the full description / context to the user.

Ask if they want to mark it **In Progress**:

```bash
# CCW (Supabase)
~/.claude/skills/feature-impl/scripts/update-feedback-status.sh <id> "in_progress"

# Inbound / Outbound (Notion)
~/.claude/skills/feature-impl/scripts/update-status.sh <page_id> "In Progress"
```

### Phase 4: Handoff to Discovery

Once the user has selected and reviewed an item, prepare the handoff to the **discovery** skill.

**Summarize the context for discovery:**

Present a clear summary to the user that includes:
- **Product:** Which product this belongs to
- **Title:** The item title (or first line of the description if untitled)
- **Type:** Feature / Bug / Improvement / UX Issue / Performance
- **Status:** Current status in the source
- **Page:** Which app page this relates to (`page_route`, if set)
- **Submitted By:** Email of the submitter (if set)
- **Description:** Full description / page body
- **Source URL:** Deep link back to the dashboard item (CCW) or the Notion page (Inbound/Outbound)

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
> **[Title]** ([Type] | [Status])
> **Product:** [Product Name]
> **Page:** [page_route, if set]
> **Submitted By:** [Email, if set]
> **Description:** [Summary of description]
> **Source:** [dashboard deep link or Notion URL]
>
> I'm now handing off to the discovery skill to explore this in depth. The discovery skill will help flesh out the idea and produce a discovery document for spec creation."

---

## Post-Discovery: Status Update

After the discovery skill completes and a discovery document is produced, the user may want to come back to this skill to:

1. Mark the item as resolved/completed in its source (if fully spec'd):
```bash
# CCW (Supabase)
~/.claude/skills/feature-impl/scripts/update-feedback-status.sh <id> "resolved"

# Inbound / Outbound (Notion)
~/.claude/skills/feature-impl/scripts/update-status.sh <page_id> "Completed"
```

2. Pick another item from the backlog and repeat the process.

---

## Anti-Patterns

| Anti-Pattern | Why It's Bad |
|--------------|--------------|
| **Reading CCW from Notion** | CCW feedback now lives in Supabase (`/admin/feedback`). The Notion CCW DB is frozen legacy and won't have recent items. |
| **Skip fetching feedback** | The whole point is to work from the real backlog |
| **Start discovery without handoff** | Use the discovery skill, don't duplicate it |
| **Skip the detail review** | Always fetch the full record before handing off - context matters |
| **Forget to update status** | The source should reflect what's being worked on |

---

## Script Reference

All scripts are in `~/.claude/skills/feature-impl/scripts/`

### Content Creation Workforce (Supabase)

**fetch-feedback.sh** — Query the in-app feedback dashboard (`bug_reports` / `sentry_issues`)
```bash
# List (tab defaults to "feedback")
~/.claude/skills/feature-impl/scripts/fetch-feedback.sh [feedback|issues] [status_filter] [filter_options]

# Full record for one item
~/.claude/skills/feature-impl/scripts/fetch-feedback.sh --detail <id> [--tab feedback|issues]

# Feedback status filters: all, incomplete (default), pending, in_progress, resolved, dismissed
# Issues  status filters: all, incomplete (default), pending, diagnosing, diagnosed, fixing, fixed, failed, dismissed

# Filter options (feedback): --filter-type, --filter-page, --filter-component, --filter-tag, --search, --group-by component|type|page|status
# Filter options (issues):   --filter-level, --filter-project, --search, --group-by level|project|status|event_type

# Credentials: SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY
#   resolved from exported env, --env-file <path>, $SUPABASE_ENV_FILE,
#   or the default ns-content-workforce-api/.env
# Deep-link base: $FEEDBACK_DASHBOARD_BASE (default https://content.novosapien.ai)

# Examples:
~/.claude/skills/feature-impl/scripts/fetch-feedback.sh feedback incomplete --group-by component
~/.claude/skills/feature-impl/scripts/fetch-feedback.sh feedback all --filter-page "/nova/[id]"
~/.claude/skills/feature-impl/scripts/fetch-feedback.sh issues incomplete --group-by status
```

**update-feedback-status.sh** — Update a feedback/issue status
```bash
~/.claude/skills/feature-impl/scripts/update-feedback-status.sh <id> <status> [--tab feedback|issues]
# feedback statuses: pending, in_progress, resolved, dismissed
# issues   statuses: pending, diagnosing, diagnosed, fixing, fixed, failed, dismissed
```

### Inbound / Outbound Sales Workforce (Notion)

**setup-databases.sh** — One-time setup (creates the Notion DBs)
```bash
~/.claude/skills/feature-impl/scripts/setup-databases.sh
```

**fetch-features.sh** — Query Notion features with optional filtering and grouping
```bash
~/.claude/skills/feature-impl/scripts/fetch-features.sh <database_id> [status_filter] [filter_options]
~/.claude/skills/feature-impl/scripts/fetch-features.sh --page <page_id>

# Status filters: all, incomplete (default), not_started, in_progress, completed
# Filter options: --filter-page, --filter-component, --filter-tag, --filter-priority, --filter-type, --search, --group-by component|type|page|priority
```

**update-status.sh** — Update a Notion feature status
```bash
~/.claude/skills/feature-impl/scripts/update-status.sh <page_id> "In Progress"
# Valid statuses: "Not Started", "In Progress", "Completed"
```

**reindex-ids.sh** — Assign sequential IDs to all Notion features
```bash
~/.claude/skills/feature-impl/scripts/reindex-ids.sh <database_id> <prefix>
# Prefixes: ISW (Inbound), OSW (Outbound). CCW is no longer Notion-backed.
```
