---
name: changelog
description: "Generate user-facing changelogs from Linear issues and git commits. Use when creating a changelog for any Novosapien product. Scans completed Linear issues and git history across all sub-repos, groups by feature area, and outputs polished markdown."
allowed-tools: Read, Bash, Write, Edit, mcp__linear__list_issues, mcp__linear__get_issue
disable-model-invocation: true
argument-hint: "[start-date end-date]"
---

> **Invoke with:** `/changelog` or `/changelog YYYY-MM-DD YYYY-MM-DD`

## What This Skill Does

Generates a polished, user-facing changelog by scanning completed Linear issues and git commit history across all sub-repos for the current product. Input: optional date range (derived from arguments or prior changelogs). Output: a formatted markdown file saved to `changelogs/YYYY-MM-DD.md` in the coordination repo, with an optional copy step to the app repo.

---

## Product Detection

Map the current directory name to a product:

| Directory pattern | Product |
|---|---|
| `ns-content-workforce` | Content Workforce |
| `ns-inbound-workforce` | Inbound Sales Workforce |
| `ns-cold-outreach` or `ns-outbound-workforce` | Cold Outreach |

If the current directory doesn't match any pattern, ask the user to specify which product they're generating a changelog for before proceeding.

---

## Product → Linear & Repo Mapping

| Product | Linear Projects | Coordination Repo | App Repo | Changelogs Dir |
|---------|----------------|-------------------|----------|----------------|
| Content Workforce | Content Creation Workforce, API - Content Workforce, Agents - Content Workforce, App - Content Workforce | ns-content-workforce | ns-content-workforce-app | changelogs/ |
| Inbound Sales Workforce | Inbound Sales Workforce | ns-inbound-workforce | (inbound app repo) | changelogs/ |
| Cold Outreach | API - Cold Outreach Workforce, App - Cold Outreach Workforce, Agents - Cold Outreach Workforce | ns-outbound-workforce | ns-cold-outreach-app | changelogs/ |

---

## Date Range Logic

Resolve the date range as follows, in order:

1. **Two `$ARGUMENTS` dates** → use them directly as `start_date` and `end_date`
2. **One `$ARGUMENTS` date** → use it as `start_date`, today as `end_date`
3. **No arguments** → scan `changelogs/` for the most recent file (by filename, `YYYY-MM-DD.md`), read its `end_date` frontmatter field → use as `start_date`, today as `end_date`
4. **No prior changelogs exist** → prompt the user for a `start_date` before continuing

---

## Workflow

### Step 1: Detect Product

- Read the current directory name
- Map to product using the table above
- If no match, ask the user which product to use

### Step 2: Determine Date Range

- Follow the date range logic above
- Confirm the resolved date range with the user before proceeding if it was auto-derived

### Step 3: Discover Sub-repos

Scan direct children of the coordination repo for directories containing a `.git/` folder:

```bash
for dir in */; do [ -d "$dir/.git" ] && echo "$dir"; done
```

Only scan direct children — do not recurse deeper.

### Step 4: Collect Git Commits

For each sub-repo discovered:

```bash
git -C <repo> log --oneline --after="<start_date>" --before="<end_date_plus_1>" --all
```

- Extract `NS-XXX` issue references from each commit message (pattern: `NS-\d+`)
- Build a deduplicated set of issue IDs referenced in the date range
- Skip commits with no `NS-XXX` references (these are internal/tooling changes)

### Step 5: Fetch Linear Issues

For each Linear project in the product mapping:

```
mcp__linear__list_issues with:
  project: <project name>
  state: "Done"
  limit: 100
```

- Filter to issues where `completedAt` falls within `[start_date, end_date]` (inclusive)
- For issues needing more detail (description, labels): `mcp__linear__get_issue({ id: "NS-XXX" })`

### Step 6: Merge and Deduplicate

- Cross-reference the NS-XXX references from git commits with the completed Linear issues
- **Linear is the source of truth**: include all completed Linear issues in the date range, even if there are no matching git commits
- Exclude git commits that have no NS-XXX reference and no matching Linear issue
- Build a final list of unique issues to document

### Step 7: Group by Feature Area

Assign each issue to a single feature area based on its title and description. Use existing changelog section names as the primary taxonomy (check prior files in `changelogs/` for established names):

- Content Repurposing
- Image Generation
- Carousel
- Publishing
- Idea Generation
- Nova
- Analytics
- Campaigns
- Documents
- Settings
- Performance & Reliability

Create new area names when an issue clearly doesn't fit existing categories. Place each issue under its single most relevant area — do not duplicate across sections.

### Step 8: Classify Entry Type

Use Linear labels to guide phrasing:

- **`Feature`** → intro paragraph (optional, for major features) + benefit-oriented bullets
- **`Bug`** → "Fixed" phrasing (e.g. "Fixed an issue where…"), grouped under the relevant feature area (not a separate "Bug Fixes" section)
- **`Refactor` / `Improvement`** → enhancement phrasing (e.g. "Improved…", "Faster…")

Write in user-facing, benefit-oriented language. Avoid technical jargon (no database names, API terms, internal component names). Focus on what the user can now do or what problem was solved.

### Step 9: Generate Changelog

- Use the template at `~/.claude/skills/changelog/templates/changelog.md`
- Fill in the frontmatter: title (human-readable date range), `start_date`, `end_date`
- Write sections per feature area, ordered by user impact (most impactful first)
- Save to `changelogs/YYYY-MM-DD.md` (using `end_date` as the filename) in the coordination repo root

### Step 10: Review and Distribute

- Present the full generated changelog to the user for review
- Ask: "Would you like me to add this to the app?"
- If yes:
  1. Copy the markdown file to `<app-repo>/src/app/(authenticated)/whats-new/changelogs/YYYY-MM-DD.md`
  2. Update `<app-repo>/src/app/(authenticated)/whats-new/changelog-data.ts`:
     - Add a new `const rawYYYY_MM_DD = \`...\`` variable with the full markdown content (including frontmatter)
     - Add the new variable to the `rawEntries` array
     - The app reads from this TS file, not the `.md` files directly (client component, no fs access)
- **Do NOT perform any git operations** — the user handles their own git workflow

---

## Output Format

The output uses the template at `~/.claude/skills/changelog/templates/changelog.md`. Key conventions:

- Frontmatter is parsed by the app for display (`title`, `start_date`, `end_date`)
- Feature areas are H2 sections (`## Feature Area Name`)
- Each bullet uses bold title: `- **Title** — User-facing description.`
- Bug fixes go under their feature area section, not a separate section
- Major features may have a short intro paragraph before the bullets

---

## Patterns to Follow

The `weekly-review` and `product-state` skills use similar git/Linear scanning patterns — reference them for conventions on querying multiple sub-repos and merging data sources.
