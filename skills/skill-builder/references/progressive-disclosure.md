# Progressive Disclosure Reference

> **When to read:** During Phase 2 (Structure Design) when deciding what goes in SKILL.md vs reference files vs templates.

Progressive disclosure is the core design principle for skills. It ensures agents load only the context they need at each stage, preserving context window budget for the actual work.

---

## Three-Tier Model

```
Tier 1: Metadata (~100 tokens)
  name + description fields
  Loaded at startup for ALL skills
  Agent uses this to decide which skills are relevant

Tier 2: Instructions (<5000 tokens recommended)
  SKILL.md body content
  Loaded when the skill is activated
  Contains routing table, core flow, key principles

Tier 3: Resources (as needed)
  Reference files, templates, scripts
  Loaded only when required during execution
  Each file loaded independently
```

---

## SKILL.md Sizing Guidelines

**Target: under 300 lines.** This is the most loaded file -- every activation reads it entirely.

| What belongs in SKILL.md | What belongs in reference files |
|--------------------------|-------------------------------|
| When to use / skip | Detailed phase instructions |
| Reference files routing table | Specification details |
| Key principles (5-7 bullets) | Extended examples |
| Phase/step overview (brief) | Decision frameworks |
| Quick reference (2-3 examples) | Format standards |
| Routing decisions | Domain-specific knowledge |

**Rule of thumb:** If a section in SKILL.md exceeds 30 lines, it probably belongs in a reference file.

---

## Routing Table Pattern

The routing table is the most important section in SKILL.md. It tells the agent what files exist and when to load them:

```markdown
## Reference Files

| Topic | Reference File | When to Load |
|-------|---------------|--------------|
| Phase 1 details | [phase-1.md](references/phase-1.md) | When starting Phase 1 |
| API conventions | [api-rules.md](references/api-rules.md) | When designing API endpoints |
| Error handling | [errors.md](references/errors.md) | When implementing error handling |
```

Guidelines:
- Every reference file must appear in the routing table
- "When to Load" should be a specific trigger, not "whenever needed"
- Order by typical usage sequence

---

## Reference File Guidelines

### Sizing

| Size | Lines | Use for |
|------|-------|---------|
| Small | 30-80 | Single protocol, short procedure, one decision |
| Medium | 80-150 | Phase guide, topic reference, pattern catalog |
| Large | 150-300 | Comprehensive reference with detailed examples or templates |

Keep files focused on one topic. Length is less important than focus — a 250-line file covering one topic well is better than splitting it artificially into two files that need to be loaded together.

### Focus

Each reference file should cover exactly ONE topic. Signs a file needs splitting:
- Multiple H2 sections that could stand alone
- File exceeds 200 lines
- Agent only needs half the file for most activations

### Format Rules

- **NO YAML frontmatter** -- only SKILL.md gets frontmatter
- Start with H1 title
- Use `> **When to read:**` callout at the top
- Use `---` horizontal rules between H2 sections
- Code blocks with language tags
- Tables for structured data
- End with completion checklist (for process-oriented files)

### Naming Conventions

| Pattern | When to use | Example |
|---------|-------------|---------|
| `phase-N-{name}.md` | Phased workflows | `phase-1-discovery.md` |
| `{topic}.md` | Topic-based references | `api-conventions.md` |
| `{category}/{topic}.md` | Categorized references | `frameworks/langgraph.md` |
| `format-standards.md` | Output format rules | Used by generators |
| `handover.md` | Session resumption | Cross-session skills |

---

## When to Split into Reference Files

**Split when:**
- SKILL.md exceeds 300 lines
- A topic has more than 30 lines of detail
- Content is only needed in specific phases/situations
- Multiple independent topics exist
- The skill has 3+ distinct concerns

**Keep in SKILL.md when:**
- Total content is under 150 lines
- All content is needed on every activation
- Skill is a simple process (< 10 steps)
- Adding reference files adds complexity without benefit

---

## Context Window Consciousness

### Budget Awareness

Skill descriptions consume context at startup (2% of context window, ~16,000 chars fallback). If you have many skills:
- Keep descriptions concise but descriptive
- Use `disable-model-invocation: true` for rarely-used skills (removes from context)

### Just-in-Time Loading

When referencing child skills or reference files:

```markdown
**CONTEXT BUDGET RULE: Load ONE reference file at a time. Read it, use it, then load the next.**
```

This pattern from existing skills prevents context bloat:
1. Read the routing table to know what's available
2. Load only the file needed for the current step
3. Complete the step
4. Load the next file

### Avoid Reference Chains

Keep references one level deep:
```
SKILL.md → references/topic.md     ✓  One level
SKILL.md → references/topic.md → references/sub-topic.md   ✗  Too deep
```

If a reference file needs to reference another file, the agent should return to SKILL.md's routing table to find it.

---

## Template Progressive Disclosure

Templates are loaded when the agent needs to produce output. They follow the same just-in-time principle:

- Templates live in `templates/`
- SKILL.md lists them with their purpose
- Agent reads template only when ready to generate output
- Templates can use placeholders: `[brackets]` or `{{handlebars}}`

---

## Checklist: Is Your Disclosure Structure Right?

- [ ] SKILL.md is under 300 lines
- [ ] Every reference file appears in the routing table
- [ ] Each reference file covers exactly one topic
- [ ] Reference files stay focused on one topic (prefer under 300 lines)
- [ ] "When to Load" triggers are specific, not vague
- [ ] No deeply nested reference chains
- [ ] Templates are separate from reference content
- [ ] The agent can complete its task by loading files one at a time
