---
name: framework-skill-builder
description: Build comprehensive skills for any SDK or framework automatically. Orchestrates a 3-phase team process (discovery, content creation, verification) to produce a complete skill with SKILL.md + verified reference files from official documentation.
metadata:
  tags: skill-builder, framework, sdk, documentation, automation, team-orchestration
---

# Framework Skill Builder

> **Invoke with:** `/framework-skill-builder` | **Keywords:** build skill, framework skill, sdk skill, create skill, documentation skill

Automates building complete skills for any SDK or framework. Takes a framework name, discovers documentation, and produces a verified skill through a 3-phase agent team process.

**Input:** Framework name (e.g., "Next.js", "FastAPI", "LangGraph")
**Output:** Complete skill directory with SKILL.md + reference files, verified against official docs

---

## Workflow Overview

```
Upfront Questions  ->  Phase 1: Discovery  ->  Phase 2: Content  ->  Phase 3: Verification  ->  Complete Skill
```

| Phase | Reference File | What Happens |
|-------|----------------|--------------|
| **Upfront Questions** | *(this file)* | Gather framework name, doc URL, focus areas, output path |
| **Phase 1: Discovery** | [phase1-discovery.md](./references/phase1-discovery.md) | Analyze doc structure, identify topics, produce topic map |
| **Phase 2: Content Creation** | [phase2-content-creation.md](./references/phase2-content-creation.md) | Write all reference files in parallel, then write SKILL.md |
| **Phase 3: Verification** | [phase3-verification.md](./references/phase3-verification.md) | Verify all files against official docs, fix issues, add doc links |
| **Format Standards** | [format-standards.md](./references/format-standards.md) | SKILL.md format, reference file format, examples |

---

## Step 1: Upfront Questions

**Gather ALL information before starting execution. No questions during phases.**

### Required Questions

Use `AskUserQuestion` to collect:

**Question 1: Framework name**
- What framework/SDK to build a skill for?
- If ambiguous (e.g., "React" could mean React, React Native, React Router), ask to clarify

**Question 2: Documentation URL**
- Search for the framework's official docs: `WebSearch` for "{framework} official documentation"
- Present the found URL and ask user to confirm or provide correct one
- If docs are behind auth/paywall, STOP and inform user (cannot proceed)

**Question 3: Focus areas** (optional)
- Any specific areas to focus on or skip?
- e.g., "Focus on App Router, skip Pages Router" or "Cover everything"
- Default: Cover everything

**Question 4: Output location**
- Default: `/Users/georgewestbrook/.claude/skills/{framework-name}/`
- Confirm with user or accept override

### Validated Input

After questions, you should have:

```
framework_name: string          # e.g., "FastAPI"
doc_url: string                 # e.g., "https://fastapi.tiangolo.com"
focus_areas: string[] | null    # e.g., ["App Router"] or null (cover everything)
output_path: string             # e.g., "/Users/georgewestbrook/.claude/skills/fastapi/"
```

---

## Step 2: Execute Phases

Execute phases sequentially. Each phase creates a team, does work, and deletes the team before moving on.

### Phase 1: Discovery

**Read:** [phase1-discovery.md](./references/phase1-discovery.md)

Creates team `{framework}-phase1-discovery` with a single doc-structure-analyzer teammate.

**Input:** Framework name, doc URL, focus areas
**Output:** Topic map — list of reference files with topics and doc URLs

### Phase 2: Content Creation

**Read:** [phase2-content-creation.md](./references/phase2-content-creation.md)

Creates team `{framework}-phase2-content` with N parallel writer teammates + 1 SKILL.md writer.

**Input:** Topic map from Phase 1, output path
**Output:** All reference files + SKILL.md written to output path

### Phase 3: Verification

**Read:** [phase3-verification.md](./references/phase3-verification.md)

Creates team `{framework}-phase3-review` with N+1 parallel reviewer teammates.

**Input:** Written files from Phase 2, doc URLs from topic map
**Output:** Verified, enhanced files with documentation link footnotes

---

## Step 3: Completion

After all 3 phases complete:

1. Verify final output structure:
   ```
   skills/{framework-name}/
   ├── SKILL.md
   └── references/
       ├── {topic-1}.md
       ├── {topic-2}.md
       └── {topic-N}.md
   ```

2. Report to user:
   - Number of reference files created
   - Any issues found and fixed during verification
   - The skill is now available via `/{framework-name}`

---

## Phase Transitions

Each phase follows this lifecycle:

```
1. TeamCreate "{framework}-phase{N}-{name}"
2. Create tasks with TaskCreate
3. Use /teammate-spawn to generate prompt files
4. Spawn teammates with Task tool (model: opus)
5. Wait for all teammates to complete
6. TeamDelete
7. Clean up teammate prompt files
8. Proceed to next phase
```

**Critical rules:**
- Always TeamDelete before starting next phase
- Clean up teammate prompts: `rm -rf teammate-prompts/{team-name}/`
- Pass outputs between phases via files or variables (NOT via team context — teams are deleted)
- All teammates use Opus model unless user specified otherwise

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Framework name is ambiguous | Ask user to clarify via AskUserQuestion |
| Documentation URL not found | Ask user to provide manually |
| Documentation behind auth/paywall | STOP — inform user, cannot proceed |
| llms.txt not found | Fallback: manual doc structure analysis (see Phase 1) |
| Doc pages fail to fetch | Try WebFetch, then web-researcher agent; stop if all fail |
| Teammate fails or produces bad output | Reviewers catch in Phase 3; if Phase 1 fails, retry manually |
| Phase 1 produces too many/too few topics | Review topic map before proceeding; adjust if needed |

---

## Success Criteria

A skill is complete when:

- [ ] SKILL.md exists with YAML frontmatter, routing table, core concepts, quick reference
- [ ] All reference files exist with clear headings, code examples, proper formatting
- [ ] All files verified by reviewers (accuracy, completeness, consistency)
- [ ] Documentation links footnotes present in all reference files
- [ ] No YAML frontmatter in reference files (only in SKILL.md)
- [ ] Skill is invocable via `/{framework-name}`
