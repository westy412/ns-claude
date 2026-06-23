---
name: product-state
description: "Update per-product state.md files in the cofounder vault. Scans git history, Linear issues, and repo health across all Novosapien product repos, then writes operational state snapshots. Use when George wants to refresh product state, check what's happening across products, or before a /cofounder session that needs current product context."
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent, mcp__linear__list_issues, mcp__linear__list_projects, mcp__linear__get_issue
argument-hint: [all | content | inbound | outbound]
---

# /product-state

> **Invoke with:** `/product-state` or `/product-state <product>` | **Keywords:** state, status, product update, what's happening, refresh state
>
> Produces operational state snapshots for Novosapien's three product workforces. Each snapshot answers: "What's happening with this product right now?"

**Input:** Which product(s) to update. Defaults to all three.
**Output:** Updated `state.md` files in `~/Programming/novosapien/cofounder/business/products/<product>/state.md`, committed to git.

---

## Products and their repos

### Content Creation Workforce

**Vault path:** `business/products/content-creation-workforce/state.md`
**Repos root:** `~/Programming/novosapien/ns-content-workforce/`

| Repo | Type | Service name (Cloud Run) |
|---|---|---|
| `ns-content-workforce-agents` | Agent service | `ns-content-agents` |
| `ns-content-workforce-api` | API | `ns-content-api` |
| `ns-content-workforce-app` | Frontend (Next.js) | `ns-content-app` |
| `ns-content-workforce-app-mobile` | Frontend (mobile) | — |
| `ns-content-workforce-idea-agents` | Agent service | `ns-content-idea-agents` |
| `ns-content-workforce-nova-agent` | Agent service | `ns-content-nova-agent` |
| `ns-content-workforce-renderer` | Service (Fastify) | `ns-content-renderer` |
| `ns-content-workforce-simulations` | Service | `ns-content-simulations` |

**Linear projects:** `Content Creation Workforce`, `App - Content Workforce`, `Agents - Content Workforce`

### Inbound Sales Workforce

**Vault path:** `business/products/inbound-sales-workforce/state.md`
**Repos root:** `~/Programming/novosapien/ns-inbound-workforce/`

| Repo | Type | Service name (Cloud Run) |
|---|---|---|
| `ns-inbound-api` | API | `ns-inbound-api` |
| `ns-inbound-application` | Frontend (Next.js) | `ns-inbound-app` |
| `ns-inbound-email-outreach-agents` | Agent service | — |
| `ns-inbound-email-reply-analysis` | Agent service | — |
| `ns-inbound-interaction-analysis` | Agent service | — |
| `ns-inbound-phone-outreach-agents` | Agent service | — |
| `ns-inbound-phone-reply-analysis` | Agent service | — |
| `ns-inbound-research-agents-lead-profile` | Agent service | — |
| `ns-inbound-research-agents-offer` | Agent service | — |
| `ns-inbound-simulation` | Service | `ns-inbound-simulation` |
| `ns-inbound-simulation-app` | Frontend (Next.js) | — |
| `ns-inbound-strategy-agents` | Agent service | — |
| `ns-inbound-strategy-optimization` | Agent service | — |

**Linear projects:** `Inbound Sales Workforce` (and any project matching "Inbound")

### Cold Outreach Workforce

**Vault path:** `business/products/cold-outreach-workforce/state.md`
**Repos root:** `~/Programming/novosapien/ns-outbound-workforce/`

| Repo | Type | Service name (Cloud Run) |
|---|---|---|
| `ns-cold-outreach-api` | API (FastAPI) | `ns-outbound-api` |
| `ns-cold-outreach-app` | Frontend (Next.js) | `ns-outbound-app` |
| `ns-cold-outreach-workforce` | Agent service (FastAPI) | `ns-outbound-workforce` |

**Linear projects:** `API - Cold Outreach Workforce`, `App - Cold Outreach Workforce`, `Agents - Cold Outreach Workforce`

---

## Data collection

For each product, gather three data sources **in parallel** using subagents where possible:

### 1. Git history (last 2 weeks)

Run for every repo in the product:

```bash
git -C <repo_path> log --oneline --since="2 weeks ago" 2>/dev/null
```

Also collect the last commit date per repo (for the repo health table):

```bash
git -C <repo_path> log -1 --format="%ad" --date=short 2>/dev/null
```

And check for branch divergence:

```bash
git -C <repo_path> branch -a --no-merged main 2>/dev/null
```

### 2. Linear issues

Fetch issues updated in the last 2 weeks for the product's Linear projects:

```
mcp__linear__list_issues with:
  team: "Novosapien"
  project: <each project name>
  updatedAt: "-P14D"
  limit: 50
```

Categorise into:
- **Done** (completed in the window)
- **In Progress** (active work)
- **Backlog** with High or Urgent priority (queued)
- **Blocked** or **Cancelled** (risk signals)

### 3. Open PRs (optional, if gh CLI is available)

```bash
gh pr list --repo Novosapien/<repo> --state open --json number,title,headRefName,updatedAt 2>/dev/null
```

---

## Output format

Each `state.md` follows this structure exactly. The file is **not** a `#context` document — it can be overwritten freely without the cofounder vault's approval flow.

```markdown
---
updated: <YYYY-MM-DD>
tags: [product]
summary: Operational state for <Product Name> — last 2 weeks of activity across all repos.
---

# <Product Name> — State

## Pulse

<2-4 sentence executive summary. What's the headline? Is the product actively being developed, stable, or dormant? What's the single most important thing happening? If there's a blocker or risk, lead with it.>

## What shipped (last 2 weeks)

<Group by theme, not by repo. Each theme gets a ### heading. Under each theme:
- What was done (specific commits/PRs, with repo names inline where useful)
- Linear issue IDs (NS-XXXX) where tracked
- Whether the work is deployed to production or only merged to main/testing
- If a theme spans multiple repos, note which ones

Themes should be named for what the work accomplished, e.g.:
- "Sentry observability integration" not "NS-1290 work"
- "Simulation evaluation rewrite" not "ns-inbound-simulation changes"
- "GCP project migration" not "Terraform updates"

If nothing shipped, say so explicitly — "No changes shipped in this period.">

## In flight

<Active work: Linear issues in "In Progress" or "Started" states, open PRs, branches with recent commits that haven't been merged.

Format as a list:
- **NS-XXXX: <title>** — <one-line status: what's done, what remains>
- **PR #N: <title>** (<repo>) — <status>

If nothing is in flight, say "No active work streams.">

## Queued

<High/Urgent priority backlog items from Linear. These are the known next pieces of work.

Format as a list:
- **NS-XXXX: <title>** — <one-line description of what and why>

If the backlog is empty or only has low-priority items, say "No high-priority items queued." and optionally note what the backlog looks like at a glance.>

## Blockers & risks

<Things that are stuck, drifting, or need attention. Sources:
- Linear issues marked blocked
- Repos with no commits in 30+ days that should be active
- Branch divergence between main and testing
- Known bugs without fixes
- Dependencies on external systems or other products
- Stale Linear issues (In Progress but no updates in 2+ weeks)

If nothing is concerning, say "No current blockers." — but still note dormant repos if any exist.>

## Repo health

<Table showing the state of every repo in the product:>

| Repo | Last commit | Commits (2w) | Branch notes |
|---|---|---|---|
| `<repo-name>` | YYYY-MM-DD | N | <any unmerged branches, divergence, or "clean"> |

<Add a one-line note after the table if any repos are notably dormant or if there's a pattern worth flagging.>
```

---

## Execution flow

1. **Parse the argument** to determine which product(s) to update. Map:
   - `all` or no argument → all three products
   - `content` → Content Creation Workforce only
   - `inbound` → Inbound Sales Workforce only
   - `outbound` or `cold` → Cold Outreach Workforce only

2. **Collect data in parallel.** For each product, launch a subagent (or run bash commands in parallel) to:
   - Gather git logs from all repos
   - Gather last-commit dates and branch info from all repos
   - Fetch Linear issues for the product's projects

3. **Synthesise.** For each product:
   - Group git commits by theme (features, fixes, infrastructure, etc.)
   - Cross-reference with Linear issues to determine tracking status
   - Identify what's deployed vs merged-only vs in-progress
   - Flag dormant repos (no commits in 30+ days)
   - Flag stale in-progress issues (no update in 14+ days)

4. **Write the state files.** One per product, to the vault paths listed above. Overwrite the existing file entirely.

5. **Commit to git** from the cofounder vault directory:
   ```bash
   cd ~/Programming/novosapien/cofounder
   git add business/products/*/state.md
   git commit -m "product-state: refresh state.md for <product(s)>"
   ```
   Use `product-state:` prefix for all commits from this skill.

6. **Report to George.** One-line summary per product updated, with the headline from the Pulse section.

---

## Integration with other skills

- **`/cofounder`** loads `state.md` conditionally when conversations touch product-specific operational state. Keeping these files fresh means the cofounder agent can answer "what's happening with X?" without round-tripping to git or Linear.
- **`/weekly-review`** covers a broader scope (all products + personal + strategic). The state files go deeper per-product but narrower in scope. They complement each other — weekly review is the strategic layer, state files are the operational layer.
- **`/project-management`** creates Linear issues. State files consume Linear data but never write to it.

---

## Freshness

These files should be refreshed:
- Before any `/cofounder` session that will discuss product-level operational state
- During or after `/weekly-review` (could be triggered as part of Phase 2)
- On demand when George asks "what's happening with <product>?"
- At minimum weekly — if `updated:` in frontmatter is more than 10 days old, the data is stale

---

## What this skill does NOT do

- Does not edit any other vault files (no README updates, no architecture files, no positioning docs)
- Does not create Linear issues or modify issue state
- Does not deploy code or interact with GCP/Cloud Run
- Does not make judgements about product strategy — it reports operational state, not strategic recommendations
- Does not touch `#context`-tagged files — state.md files are deliberately NOT tagged `#context`
