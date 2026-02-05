# Setup Project

## Meta

| Field | Value |
|-------|-------|
| Name | setup-project |
| Description | Bootstrap a repository with CLAUDE.md and standard conventions |
| Version | 1.0.0 |

## Purpose

Use this skill when:
- Setting up a new repository for Claude Code
- Bootstrapping an existing repo that lacks a CLAUDE.md
- Updating a repo's CLAUDE.md with standard Ways of Working
- **Auditing an existing project** to ensure it has all required sections (Linear IDs, Session Handovers, issue templates)
- A handover failed because project setup was incomplete

Skip this skill when:
- You're just doing quick edits, not full project setup
- The project already has complete CLAUDE.md with all required sections

## Prerequisites

**Linear MCP must be configured.** Before running this skill:
1. Ensure Linear MCP is installed: `claude mcp add linear`
2. Verify it's working: `mcp__linear__list_teams` should return results
3. If not configured, help the user set it up first

## What This Skill Creates

```
repo/
├── CLAUDE.md                           # Project configuration and ways of working
└── .claude/
    └── templates/
        └── linear-issues/
            ├── feature.md
            ├── bug.md
            ├── refactor.md
            └── architecture.md
```

## Workflow

### Phase 1: Explore Codebase

Gather information about the repository:

1. **Check for existing CLAUDE.md** - Read it if exists, categorize each section:

   **Sections to PRESERVE** (project-specific content):
   - Project overview/description/purpose
   - Directory structure/folder layout
   - Tech stack/dependencies/architecture
   - Environment setup/getting started
   - Tips/notes/gotchas
   - API documentation
   - Testing instructions
   - Any project-specific workflow notes (e.g., "always run X before Y")

   **Sections to OVERWRITE** (will be replaced with our standards):
   - Anything about git/commits/branching/version control
   - Anything about Linear/issues/tickets/task tracking
   - Anything about workflow/phases/how work gets done
   - Anything about commit message format
   - Rule hierarchy sections

   **Sections to AUDIT for completeness:**
   - Project Configuration (Linear Team ID, Project ID)
   - Session Handovers section
   - Subagent Usage guidelines

2. **Audit existing setup** - Check what's missing:

   | Check | Location | If Missing |
   |-------|----------|------------|
   | Linear Team ID | CLAUDE.md Project Configuration | Ask user, add it |
   | Linear Project ID | CLAUDE.md Project Configuration | Ask user, add it |
   | Ways of Working section | CLAUDE.md | Add full section |
   | Session Handovers section | CLAUDE.md | Add to Ways of Working |
   | Issue templates | `.claude/templates/linear-issues/` | Create directory and templates |
   | Specs directory | `/specs/` | Note if missing (don't create empty) |

3. **Identify tech stack:**
   - Check for `package.json` (Node.js/JS/TS)
   - Check for `pyproject.toml`, `requirements.txt`, `uv.lock` (Python)
   - Check for `go.mod` (Go)
   - Check for `Cargo.toml` (Rust)
   - Check for `Dockerfile`, `docker-compose.yml`
   - Check for `terraform/`, `*.tf` files
3. **Map directory structure:**
   - Run `ls -la` at root
   - Identify key directories (src/, app/, lib/, tests/, etc.)
   - Note any specs/, docs/, or similar directories
4. **Identify development tools:**
   - Package manager (npm, yarn, pnpm, uv, pip, etc.)
   - Build commands
   - Test commands
   - Lint commands
5. **Identify key patterns:**
   - Read a few key files to understand architecture
   - Note frameworks (Next.js, FastAPI, Express, etc.)
   - Note any existing conventions
6. **Check for related services:**
   - Is this part of a monorepo?
   - Are there references to other services?

### Phase 2: Read Templates

**Before drafting, read all template files:**

```
Use Read tool to read:
1. ~/.claude/skills/setup-project/templates/ways-of-working.md
2. ~/.claude/skills/setup-project/templates/linear-issues/feature.md
3. ~/.claude/skills/setup-project/templates/linear-issues/bug.md
4. ~/.claude/skills/setup-project/templates/linear-issues/refactor.md
5. ~/.claude/skills/setup-project/templates/linear-issues/architecture.md
```

You need the full contents of these files to complete the setup.

### Phase 3: Draft CLAUDE.md

Create or update the CLAUDE.md by combining discovered information with the Ways of Working template.

**For NEW repos (no existing CLAUDE.md):**

Build the CLAUDE.md with this structure:

```markdown
# [Repo Name]

## Repository Purpose

[One paragraph describing what this repo is for]

## Tech Stack

- **Language:** [e.g., TypeScript, Python]
- **Framework:** [e.g., Next.js, FastAPI]
- **Database:** [if applicable]
- **Key Dependencies:** [list major ones]

## Directory Structure

[Tree view of key directories]

## Development Tools

**Package Manager:** [e.g., uv, npm, pnpm]

[Commands for install, dev, test, lint]

## Key Patterns

[Architectural patterns and conventions discovered]

---

[INSERT FULL CONTENTS OF ways-of-working.md HERE]
```

**For EXISTING repos (has CLAUDE.md):**

1. **Preserve** all project-specific sections (overview, directory structure, tech stack, tips, etc.)
2. **Remove** any existing sections about Git, Linear, workflow, commits
3. **Insert** the full Ways of Working template after the project-specific sections
4. The result should have project-specific info at the top, then the Ways of Working section

**Important:** The Ways of Working template includes the Project Configuration section with Linear placeholders. Insert the entire template contents, not a reference to it.

**For EXISTING repos needing updates (partial CLAUDE.md):**

Some repos may have an older or incomplete CLAUDE.md. Run an audit:

1. **Check for missing sections:**

   | Section | How to Check | Action if Missing |
   |---------|--------------|-------------------|
   | Ways of Working | Look for `## Ways of Working` heading | Add full template |
   | Session Handovers | Look for `## Session Handovers` heading | Add section (part of Ways of Working) |
   | Project Configuration | Look for Linear Team ID/Project ID | Ask user for values, add section |
   | Subagent Usage | Look for `## Subagent Usage` heading | Add section (part of Ways of Working) |

2. **Check for outdated sections:**
   - If Ways of Working exists but is missing Session Handovers → Add the section
   - If commit format doesn't match current standard → Update it
   - If Linear workflow states are outdated → Update them

3. **Check for missing files:**

   | File/Directory | Action if Missing |
   |----------------|-------------------|
   | `.claude/templates/linear-issues/feature.md` | Create from template |
   | `.claude/templates/linear-issues/bug.md` | Create from template |
   | `.claude/templates/linear-issues/refactor.md` | Create from template |
   | `.claude/templates/linear-issues/architecture.md` | Create from template |

4. **Report gaps to user:**
   - List what's missing
   - Propose the additions
   - Get approval before making changes

### Phase 4: Get User Approval

Before writing anything:

1. Present the drafted CLAUDE.md to the user
2. Ask if any sections need adjustment
3. Ask for the Linear Team/Project information if not known
4. Only proceed after explicit approval

### Phase 5: Write Files

After approval:

1. **Write CLAUDE.md** to repo root (with Ways of Working content included)

2. **Create `.claude/templates/linear-issues/` directory** in the repo

3. **Write issue templates** - Use the content you read in Phase 2 to write each template to the repo's `.claude/templates/linear-issues/`:
   - `feature.md`
   - `bug.md`
   - `refactor.md`
   - `architecture.md`

### Phase 6: Confirm Setup

Report back to user with a **completeness checklist**:

```
## Setup Complete

### CLAUDE.md
- [x] Project-specific sections (overview, tech stack, directory structure)
- [x] Ways of Working section (full template)
- [x] Session Handovers section
- [x] Project Configuration with Linear Team ID: {{ID}}
- [x] Project Configuration with Linear Project ID: {{ID}}
- [x] Subagent Usage guidelines

### Issue Templates
- [x] .claude/templates/linear-issues/feature.md
- [x] .claude/templates/linear-issues/bug.md
- [x] .claude/templates/linear-issues/refactor.md
- [x] .claude/templates/linear-issues/architecture.md

### Ready for Handovers
- [x] Linear IDs configured (can create/update issues)
- [x] Session Handovers documented (next session knows how to resume)
- [x] Git conventions documented (commits link to Linear)
```

If any items are incomplete, note what the user needs to provide (e.g., "Need Linear Team ID - run `mcp__linear__list_teams` to find it").

## Templates

This skill includes templates in `templates/`:

| Template | Purpose |
|----------|---------|
| `ways-of-working.md` | Standard Ways of Working section for CLAUDE.md |
| `linear-issues/feature.md` | Feature issue template |
| `linear-issues/bug.md` | Bug issue template |
| `linear-issues/refactor.md` | Refactor issue template |
| `linear-issues/architecture.md` | Architecture issue template |

## Critical Rules

### MUST DO

- **Read all template files first** (ways-of-working.md and all linear-issues/*.md)
- Explore the codebase thoroughly before drafting
- Insert the **full contents** of ways-of-working.md into CLAUDE.md
- Get user approval before writing any files
- Include all discovered information (don't skip sections)
- Write all four issue templates to `.claude/templates/linear-issues/`
- Note any sections that need manual completion

### MUST NOT

- Write files without user approval
- Skip reading the template files
- Reference templates instead of inserting their full contents
- Make assumptions about Linear configuration (ask if unknown)
- Skip the Ways of Working section
- Leave placeholder text like "[FILL IN]" without noting it to the user
