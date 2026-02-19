# Phase 2: Content Creation

## Purpose

Write all reference files in parallel, then write the SKILL.md routing layer. Produces the complete skill directory.

---

## Team Setup

```
Team name: {framework}-phase2-content
Teammates: N writers (one per reference file) + 1 SKILL.md writer
Model: Opus
```

### Step-by-step

1. `TeamCreate "{framework}-phase2-content"`

2. Create tasks — one per reference file from the topic map, plus one for SKILL.md:
   ```
   # For each reference file:
   TaskCreate:
     subject: "Write {topic-name} reference file"
     description: "Fetch docs at {doc_urls}, extract technical content, write to {output_path}/references/{filename}"
     activeForm: "Writing {topic-name} reference"

   # SKILL.md task (created now but blocked until all writers finish):
   TaskCreate:
     subject: "Write SKILL.md routing layer"
     description: "Read all completed reference files, create SKILL.md with routing table"
     activeForm: "Writing SKILL.md"
   ```
   Set the SKILL.md task as `addBlockedBy` all writer tasks.

3. Use `/teammate-spawn` to generate prompt files for each writer (see templates below)

4. Spawn all N writer teammates in parallel:
   ```
   Task tool:  (call N times in parallel)
     team_name: {framework}-phase2-content
     name: writer-{topic}
     subagent_type: general-purpose
     model: opus
     prompt: |
       You are teammate writer-{topic} on team {framework}-phase2-content.
       Read your full instructions at:
         {project-path}/teammate-prompts/{framework}-phase2-content/writer-{topic}.md
       Follow all steps in order.
   ```

5. Wait for all writers to complete

6. Use `/teammate-spawn` to generate prompt file for the SKILL.md writer

7. Unblock the SKILL.md task, then spawn the SKILL.md writer:
   ```
   Task tool:
     team_name: {framework}-phase2-content
     name: skillmd-writer
     subagent_type: general-purpose
     model: opus
     prompt: |
       You are teammate skillmd-writer on team {framework}-phase2-content.
       Read your full instructions at:
         {project-path}/teammate-prompts/{framework}-phase2-content/skillmd-writer.md
       Follow all steps in order.
   ```

8. Wait for SKILL.md writer to complete
9. `TeamDelete`
10. Clean up: `rm -rf teammate-prompts/{framework}-phase2-content/`

---

## Content Writer Instructions

Each writer receives one topic from the topic map and produces one reference file.

### Writer Workflow

1. **Fetch documentation** — Use `WebFetch` to fetch each assigned doc URL. Extract the technical content.

2. **Extract technical content** — From the fetched docs, extract:
   - API signatures and parameters
   - Code examples (working, copy-paste ready)
   - Configuration options and defaults
   - Common patterns and best practices
   - Gotchas, limitations, and tips

3. **Structure the reference file** — Organize content with:
   - Clear heading hierarchy (H1 title, H2 sections, H3 subsections)
   - Code examples in fenced blocks with language tags
   - Tables for comparison/options/parameters
   - Practical notes and tips
   - No YAML frontmatter (only SKILL.md gets frontmatter)

4. **Write the file** — Write to `{output_path}/references/{filename}`

5. **Report completion** — Message team-lead with a brief summary of what was written

6. **Mark task complete** — TaskUpdate to mark their task as completed

### What Writers Decide

Writers have creative freedom over:
- How to organize subsections within their file
- Which code examples to include (must have at least one per major concept)
- Level of detail for each subtopic
- Internal heading structure

### What Writers Must Include

- All major APIs/features for their assigned topic
- Working code examples (not pseudocode)
- Clear explanations of what each API/feature does
- Parameter tables for functions with multiple parameters

### Content Quality Guidelines

**Do:**
- Use the framework's actual API names and types
- Include import statements in code examples
- Show both basic and advanced usage patterns
- Note default values and optional parameters
- Mention version-specific behavior if relevant

**Don't:**
- Include YAML frontmatter
- Add documentation links section (reviewers add this in Phase 3)
- Copy documentation verbatim — restructure for reference use
- Leave placeholder content ("TODO", "TBD")
- Include content outside the assigned topic scope

---

## SKILL.md Writer Instructions (Phase 2.5)

The SKILL.md writer runs AFTER all content writers complete. They need to know which files exist to create an accurate routing table.

### SKILL.md Writer Workflow

1. **Read all reference files** — Read every file in `{output_path}/references/` to understand what was written

2. **Create SKILL.md** with these sections (see [format-standards.md](./format-standards.md) for detailed format):

   **a. YAML frontmatter:**
   ```yaml
   ---
   name: {framework-name}
   description: {1-2 sentence description of what this skill covers}
   metadata:
     tags: {comma-separated relevant tags}
   ---
   ```

   **b. Title and invoke line:**
   ```markdown
   # {Framework Name}

   > **Invoke with:** `/{framework-name}` | **Keywords:** {relevant keywords}
   ```

   **c. Purpose section** — When to use this skill

   **d. Reference Files routing table:**
   ```markdown
   | Task | Reference File | Description |
   |------|----------------|-------------|
   | **{task}** | [{filename}](./references/{filename}) | {description} |
   ```

   **e. Core Concepts section** — Key concepts from the framework (3-5 paragraphs)

   **f. Quick Reference section** — Most common APIs/patterns at a glance

   **g. Documentation Links** — Links to official docs

3. **Write to** `{output_path}/SKILL.md`

4. **Report completion** — Message team-lead

5. **Mark task complete** — TaskUpdate

---

## Content Writer Teammate Template

Use `/teammate-spawn` with these values for each writer:

```
teammate-name: writer-{topic}
team-name: {framework}-phase2-content
responsibility: Write the {topic} reference file for {framework}
files-owned: |
  - {output_path}/references/{filename}
tasks: |
  1. Fetch these documentation pages using WebFetch:
     {doc_url_1}
     {doc_url_2}
     ... (list all doc URLs for this topic)

  2. Extract all technical content:
     - API signatures and parameters
     - Code examples
     - Configuration options
     - Best practices and patterns

  3. Structure the reference file with:
     - H1 title: "{Framework} -- {Topic Name} Reference"
     - H2 sections for major concepts
     - H3 subsections for details
     - Code examples in fenced blocks with language tags
     - Tables for parameters/options
     - No YAML frontmatter

  4. Write the file to: {output_path}/references/{filename}

  5. Message team-lead with a summary of what you wrote (topics covered, number of code examples)

  6. Mark your task as completed

  Framework: {framework_name}
  Topic: {topic_name}
  Output file: {output_path}/references/{filename}
communication: |
  Send completion summary to team-lead when done.
validation: |
  - File exists at {output_path}/references/{filename}
  - Has clear heading hierarchy (H1, H2, H3)
  - Contains working code examples (at least 1 per major concept)
  - Has parameter/option tables where appropriate
  - No YAML frontmatter
  - No placeholder content (TODO, TBD)
  - Only covers the assigned topic (no scope creep)
```

## SKILL.md Writer Teammate Template

```
teammate-name: skillmd-writer
team-name: {framework}-phase2-content
responsibility: Create the SKILL.md routing layer for {framework}
files-owned: |
  - {output_path}/SKILL.md
reference-files: |
  Read ALL files in {output_path}/references/ before starting.
tasks: |
  1. Read every reference file in {output_path}/references/
  2. Create SKILL.md with these sections:
     a. YAML frontmatter (name, description, tags)
     b. Title with invoke line
     c. Purpose section
     d. Reference Files routing table (one row per reference file)
     e. Core Concepts section (key framework concepts, 3-5 paragraphs)
     f. Quick Reference section (most common APIs/patterns)
     g. Documentation Links section

  3. The routing table must accurately map tasks to the reference files that exist.
     Use this format:
     | Task | Reference File | Description |
     |------|----------------|-------------|

  4. Write to: {output_path}/SKILL.md

  5. Message team-lead with completion summary

  6. Mark your task as completed

  Framework: {framework_name}
  Documentation URL: {doc_url}
  Output file: {output_path}/SKILL.md
communication: |
  Send completion summary to team-lead when done.
validation: |
  - SKILL.md has YAML frontmatter with name, description, tags
  - Has routing table with one entry per reference file
  - Every reference file in the directory appears in the routing table
  - Has Core Concepts section
  - Has Quick Reference section
  - Has Documentation Links section
```
