---
name: vault-setup
description: Scaffold a new client project vault with Quartz docs-as-code, product-manager skills, and the full knowledge graph skeleton. Creates the repo, configures deployment, and copies in project-scoped skills.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
argument-hint: "[project-name]"
---

> **Invoke with:** `/vault-setup` or `/vault-setup [project-name]`

Scaffolds a new client project vault — a Quartz-powered Obsidian vault that auto-deploys as a docs site. Creates the GitHub repo, directory structure, product-manager skill suite, and deployment pipeline.

## What It Creates

```
[project-name]-vault/
├── .github/
│   └── workflows/
│       └── deploy.yml               ← GitHub Pages auto-deploy on push to main
├── .claude/
│   └── skills/                       ← Project-scoped product skills
│       ├── product-manager/
│       │   ├── SKILL.md
│       │   ├── references/
│       │   │   └── project-structure.md
│       │   └── templates/
│       │       ├── project-readme.md
│       │       └── meeting.md
│       ├── product-vision/
│       │   ├── SKILL.md
│       │   ├── references/
│       │   │   └── vision-extraction.md
│       │   └── templates/
│       │       └── vision.md
│       ├── product-component/
│       │   ├── SKILL.md
│       │   ├── references/
│       │   │   └── component-extraction.md
│       │   └── templates/
│       │       └── component.md
│       └── product-sub-component/
│           ├── SKILL.md
│           ├── references/
│           │   └── sub-component-extraction.md
│           └── templates/
│               └── sub-component.md
├── vault/                            ← Content root (Quartz content directory)
│   ├── index.md                      ← Project landing page
│   ├── vision.md                     ← Vision document (empty template)
│   ├── components/
│   │   └── components.md             ← Component map
│   ├── architecture/
│   │   ├── architecture.md           ← Architecture entry point
│   │   └── integrations/
│   │       └── integrations.md       ← Third-party integrations
│   ├── meetings/                     ← Meeting transcripts
│   └── drafts/                       ← Work-in-progress documents
├── CLAUDE.md                         ← Project-level Claude Code instructions
├── quartz.config.ts                  ← Quartz site configuration
├── quartz.layout.ts                  ← Quartz layout (copied from Quartz template)
├── package.json                      ← Quartz dependencies
├── tsconfig.json                     ← TypeScript config
└── .gitignore
```

## Setup Flow

### Step 1: Gather inputs

Ask the user for:
- **Project name** — lowercase, hyphen-separated (e.g., "inplay", "txn", "meridian"). Used for the repo name (`[name]-vault`), Quartz config, and directory names.
- **Client name** — display name for the project landing page (e.g., "InPlay", "TXN Sports", "Meridian Insurance").
- **Google Drive link** — optional. If provided, added to the project landing page.
- **Parent directory** — where to create the vault. Default: `/Users/georgewestbrook/Programming/` or ask.

If a project name was passed as an argument, use it and ask for the remaining inputs.

### Step 2: Create GitHub repo

```bash
gh repo create Novosapien/[name]-vault --private --clone
```

This creates the repo on GitHub and clones it locally.

### Step 3: Set up Quartz

Quartz 4 is a static site generator that builds an Obsidian vault into a website.

**Clone method:** Clone the Quartz template repo into a temporary location, then copy the Quartz framework files (everything except the content directory) into the project repo:

```bash
# Clone Quartz template
git clone --depth 1 https://github.com/jackyzha0/quartz.git /tmp/quartz-template

# Copy Quartz framework files into the project
cp -r /tmp/quartz-template/quartz/ [project-dir]/quartz/
cp /tmp/quartz-template/package.json [project-dir]/
cp /tmp/quartz-template/tsconfig.json [project-dir]/
cp /tmp/quartz-template/quartz.layout.ts [project-dir]/

# Clean up
rm -rf /tmp/quartz-template
```

Then write the customised `quartz.config.ts` using the template in `templates/quartz.config.ts.template`, replacing:
- `__PAGE_TITLE__` → project display name (e.g., "InPlay Vault")
- `__PAGE_TITLE_SUFFIX__` → ` | [Project Name]`
- `__BASE_URL__` → `novosapien.github.io/[name]-vault`

### Step 4: Write content skeleton

Create the vault content structure inside `vault/`:

1. **`vault/index.md`** — from the `project-readme.md` template, filled in with project name, client name, Google Drive link, and status set to "Discovery"
2. **`vault/vision.md`** — empty vision template (from product-vision skill template)
3. **`vault/components/components.md`** — empty component map
4. **`vault/architecture/architecture.md`** — empty architecture entry point
5. **`vault/architecture/integrations/integrations.md`** — empty integrations page
6. **`vault/meetings/`** — empty directory (add `.gitkeep`)
7. **`vault/drafts/`** — empty directory (add `.gitkeep`)

### Step 5: Copy skills

Copy the product-manager skill suite from `~/.claude/skills/` into `.claude/skills/` in the project:

```bash
cp -r ~/.claude/skills/product-manager [project-dir]/.claude/skills/
cp -r ~/.claude/skills/product-vision [project-dir]/.claude/skills/
cp -r ~/.claude/skills/product-component [project-dir]/.claude/skills/
cp -r ~/.claude/skills/product-sub-component [project-dir]/.claude/skills/
```

### Step 6: Write CLAUDE.md

Write a project-level CLAUDE.md using the template in `templates/claude-md.md.template`, replacing `__PROJECT_NAME__` and `__CLIENT_NAME__`.

### Step 7: Write deployment config

1. Write `.github/workflows/deploy.yml` from the template
2. Write `.gitignore`

### Step 8: Install and verify

```bash
cd [project-dir]
npm install
npx quartz build  # Verify it builds
```

### Step 9: Initial commit and push

```bash
git add -A
git commit -m "vault-setup: scaffold [project-name] vault"
git push -u origin main
```

### Step 10: Enable GitHub Pages

```bash
gh api repos/Novosapien/[name]-vault/pages -X POST -f "build_type=workflow"
```

Report the site URL: `https://novosapien.github.io/[name]-vault/`

### Step 11: Report

Tell the user:
- Repo URL
- Site URL
- What skills are available
- What to do next (usually: drop a vision call transcript and run `/product-vision`)

## Templates

| Template | Purpose |
|----------|---------|
| [quartz.config.ts.template](templates/quartz.config.ts.template) | Quartz site configuration with placeholders |
| [deploy.yml.template](templates/deploy.yml.template) | GitHub Actions deployment workflow |
| [claude-md.md.template](templates/claude-md.md.template) | Project-level CLAUDE.md |
| [gitignore.template](templates/gitignore.template) | .gitignore for vault repos |
| [architecture.md.template](templates/architecture.md.template) | Architecture entry point skeleton |
| [components.md.template](templates/components.md.template) | Component map skeleton |
