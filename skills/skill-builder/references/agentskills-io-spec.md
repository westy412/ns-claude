# AgentSkills.io Specification Reference

> **When to read:** When the user wants to create an AgentSkills.io-compatible skill, or when generating a portable skill that works across multiple AI tools.

The AgentSkills.io spec is the open standard for agent skills. Claude Code follows this standard and extends it. This reference covers the base standard only.

---

## Directory Structure

A skill is a directory containing at minimum a `SKILL.md` file:

```
skill-name/
├── SKILL.md           # Required - entry point
├── scripts/           # Optional - executable code
├── references/        # Optional - additional documentation
└── assets/            # Optional - static resources (templates, images, data)
```

The directory name **must match** the `name` field in the frontmatter exactly.

---

## Frontmatter Fields

All skills require YAML frontmatter at the top of `SKILL.md`:

```yaml
---
name: skill-name
description: What this skill does and when to use it.
---
```

### Required Fields

| Field | Constraints | Guidelines |
|-------|-------------|------------|
| `name` | 1-64 chars, lowercase letters + numbers + hyphens only | Must match directory name. No consecutive hyphens (`--`). Cannot start or end with hyphen. |
| `description` | 1-1024 chars, non-empty | Describe both WHAT it does and WHEN to use it. Include specific keywords that help agents identify relevant tasks. |

### Optional Fields

| Field | Constraints | Purpose |
|-------|-------------|---------|
| `license` | Free-form string | License name or reference to bundled LICENSE file |
| `compatibility` | 1-500 chars | Environment requirements (intended product, system packages, network access) |
| `metadata` | Map of string keys to string values | Arbitrary additional properties (author, version, tags, etc.) |
| `allowed-tools` | Space-delimited list | Pre-approved tools the skill may use (experimental) |

### Name Validation Rules

```
Valid:
  pdf-processing       ✓  lowercase + hyphens
  data-analysis        ✓  standard format
  code-review          ✓  standard format
  my-skill-v2          ✓  numbers allowed

Invalid:
  PDF-Processing       ✗  uppercase not allowed
  -pdf                 ✗  starts with hyphen
  pdf-                 ✗  ends with hyphen
  pdf--processing      ✗  consecutive hyphens
  my skill             ✗  spaces not allowed
  my_skill             ✗  underscores not allowed
```

### Description Best Practices

Good -- describes what AND when:
```yaml
description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.
```

Poor -- too vague:
```yaml
description: Helps with PDFs.
```

---

## Body Content

The markdown body after frontmatter contains skill instructions. No format restrictions -- write whatever helps agents perform the task effectively.

Recommended sections:
- Step-by-step instructions
- Examples of inputs and outputs
- Common edge cases

The agent loads the entire SKILL.md body when it activates the skill. For large skills, split content into reference files and load them just-in-time.

---

## Optional Directories

### scripts/

Executable code agents can run. Scripts should:
- Be self-contained or clearly document dependencies
- Include helpful error messages
- Handle edge cases gracefully

### references/

Additional documentation agents read when needed:
- Detailed technical references
- Domain-specific knowledge files
- Keep individual files focused -- agents load on demand

### assets/

Static resources:
- Templates (document templates, configuration templates)
- Images (diagrams, examples)
- Data files (lookup tables, schemas)

---

## File Reference Rules

When referencing files from SKILL.md, use relative paths:

```markdown
See [the reference guide](references/REFERENCE.md) for details.
Run the extraction script: scripts/extract.py
```

Keep file references one level deep from SKILL.md. Avoid deeply nested reference chains.

---

## Validation

Use the `skills-ref` library to validate:

```bash
skills-ref validate ./my-skill
```

Checks:
- SKILL.md exists and has valid frontmatter
- `name` field follows naming rules
- `name` matches directory name
- `description` is non-empty and within length limits
- All field constraints are met

---

## Key Differences from Claude Code

AgentSkills.io does NOT support:
- `disable-model-invocation` or `user-invocable` fields
- `context`, `agent`, `model`, `hooks`, or `argument-hint` fields
- `$ARGUMENTS` string substitution
- `!`command`` dynamic context injection
- Subagent execution (`context: fork`)
- Invocation control (who can trigger the skill)

AgentSkills.io has fields Claude Code does NOT require:
- `name` is **required** (Claude Code defaults to directory name)
- `description` is **required** (Claude Code only recommends it)
- `license` and `compatibility` fields
