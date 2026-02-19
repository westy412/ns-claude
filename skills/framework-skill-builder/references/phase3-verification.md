# Phase 3: Verification

## Purpose

Verify all reference files and SKILL.md against official documentation. Fix inaccuracies, fill gaps, ensure consistency, and add documentation link footnotes.

---

## Team Setup

```
Team name: {framework}-phase3-review
Teammates: N+1 reviewers (one per reference file + one for SKILL.md)
Model: Opus
```

### Step-by-step

1. `TeamCreate "{framework}-phase3-review"`

2. Create tasks — one per file to review:
   ```
   # For each reference file:
   TaskCreate:
     subject: "Review {topic-name} reference file"
     description: "Verify {output_path}/references/{filename} against official docs, apply 6-point checklist, fix issues, add doc links"
     activeForm: "Reviewing {topic-name}"

   # For SKILL.md:
   TaskCreate:
     subject: "Review SKILL.md"
     description: "Verify {output_path}/SKILL.md routing table accuracy, core concepts, quick reference"
     activeForm: "Reviewing SKILL.md"
   ```

3. Use `/teammate-spawn` to generate prompt files for each reviewer (see templates below)

4. Spawn all N+1 reviewers in parallel:
   ```
   Task tool:  (call N+1 times in parallel)
     team_name: {framework}-phase3-review
     name: reviewer-{topic}
     subagent_type: general-purpose
     model: opus
     prompt: |
       You are teammate reviewer-{topic} on team {framework}-phase3-review.
       Read your full instructions at:
         {project-path}/teammate-prompts/{framework}-phase3-review/reviewer-{topic}.md
       Follow all steps in order.
   ```

5. Wait for all reviewers to complete
6. `TeamDelete`
7. Clean up: `rm -rf teammate-prompts/{framework}-phase3-review/`

---

## 6-Point Verification Checklist

Every reviewer applies this checklist to their assigned file:

### 1. Accuracy

- All information matches official documentation
- API signatures are correct (parameter names, types, return values)
- Code examples use correct syntax and current API
- No deprecated or removed APIs presented as current
- Default values are accurate

**How to verify:** Fetch the official doc pages for this topic and compare claims.

### 2. Completeness

- All major APIs/features for this topic are covered
- No significant omissions compared to official docs
- Edge cases and limitations are mentioned where relevant

**How to verify:** List the features in the official docs, check each appears in the reference file.

### 3. Code Examples

- Every file has working code examples
- Code examples include import statements
- Code examples use correct syntax for the framework version
- Both basic and advanced usage patterns shown

**How to verify:** Read each code example and verify it would work as written.

### 4. Consistency

- Terminology matches official docs and is consistent across files
- API names are spelled correctly and consistently
- Code style is consistent within and across files

**How to verify:** Check that the same concept uses the same name everywhere.

### 5. Format Standards

- Proper heading hierarchy (H1 for title, H2 for sections, H3 for subsections)
- Code blocks have language tags
- Tables are properly formatted
- No YAML frontmatter in reference files
- No orphaned sections or incomplete content

**How to verify:** Visual scan of the file structure.

### 6. Documentation Links

- File has a "Documentation Links" section at the bottom
- Links point to official documentation pages relevant to this topic
- Links are valid URLs (not broken)

**How to add:** If missing, add this section at the bottom:
```markdown
---

## Documentation Links

- [Page Title](https://docs.example.com/page) - Brief description
- [Page Title](https://docs.example.com/page) - Brief description
```

---

## Reviewer Workflow

Each reviewer follows these steps:

1. **Fetch official documentation** — Use `WebFetch` to fetch the doc URLs associated with their topic (from the topic map). This is their source of truth.

2. **Read the reference file** — Read their assigned file from `{output_path}/references/{filename}`.

3. **Apply 6-point checklist** — Go through each point systematically. Take notes on issues found.

4. **Fix issues** — Edit the file directly to fix any problems:
   - Incorrect API signatures → fix them
   - Missing features → add them
   - Bad code examples → rewrite them
   - Inconsistent terminology → standardize
   - Format problems → fix formatting

5. **Add Documentation Links** — If the file doesn't have a "Documentation Links" section, add one at the bottom with relevant official doc URLs.

6. **Report findings** — Message team-lead with:
   - Number of issues found per checklist point
   - Summary of major fixes applied
   - Any concerns or areas where official docs were unclear

7. **Mark task complete** — TaskUpdate to mark their task as completed.

---

## SKILL.md Reviewer

The SKILL.md reviewer has a modified checklist:

### SKILL.md Specific Checks

1. **Routing table accuracy** — Every reference file in the directory appears in the routing table. No phantom entries pointing to files that don't exist.

2. **YAML frontmatter** — Has name, description, and tags. Description is useful and concise.

3. **Core concepts** — Accurately represents the framework's key concepts. Not too superficial, not too detailed.

4. **Quick reference** — Shows the most commonly needed APIs/patterns. Code examples are correct.

5. **Documentation links** — Points to official documentation homepage and key pages.

6. **Invoke line** — The invoke command and keywords are sensible and match the framework name.

---

## Reference File Reviewer Teammate Template

Use `/teammate-spawn` with these values for each reviewer:

```
teammate-name: reviewer-{topic}
team-name: {framework}-phase3-review
responsibility: Verify the {topic} reference file against official {framework} documentation
files-owned: |
  - {output_path}/references/{filename}
tasks: |
  1. Fetch official documentation using WebFetch:
     {doc_url_1}
     {doc_url_2}
     ... (list all doc URLs for this topic)

  2. Read the reference file: {output_path}/references/{filename}

  3. Apply the 6-point verification checklist:
     a. ACCURACY - All info matches official docs
     b. COMPLETENESS - All major features for this topic are covered
     c. CODE EXAMPLES - Working examples with imports, correct syntax
     d. CONSISTENCY - Terminology consistent with official docs
     e. FORMAT - Proper headings, tables, code blocks, no YAML frontmatter
     f. DOC LINKS - "Documentation Links" section at bottom with official URLs

  4. Fix all issues by editing the file directly

  5. If no "Documentation Links" section exists, add one at the bottom with
     relevant official doc URLs in this format:
     ---
     ## Documentation Links
     - [Page Title](url) - Brief description

  6. Message team-lead with your findings:
     - Issues found per checklist point (count)
     - Summary of major fixes
     - Any concerns

  7. Mark your task as completed

  Framework: {framework_name}
  Topic: {topic_name}
  File: {output_path}/references/{filename}
communication: |
  Send review summary to team-lead when complete.
validation: |
  - All 6 checklist points verified
  - All issues found have been fixed (not just noted)
  - Documentation Links section exists at bottom of file
  - File still has proper structure after edits
```

## SKILL.md Reviewer Teammate Template

```
teammate-name: reviewer-skillmd
team-name: {framework}-phase3-review
responsibility: Verify the SKILL.md routing layer for {framework}
files-owned: |
  - {output_path}/SKILL.md
reference-files: |
  List all files in {output_path}/references/ (needed to verify routing table)
tasks: |
  1. List all files in {output_path}/references/ to know what should be in routing table

  2. Read {output_path}/SKILL.md

  3. Verify:
     a. ROUTING TABLE - Every reference file appears in the table, no phantom entries
     b. YAML FRONTMATTER - Has name, description, tags
     c. CORE CONCEPTS - Accurately represents key framework concepts
     d. QUICK REFERENCE - Shows most common APIs, code examples are correct
     e. DOCUMENTATION LINKS - Points to official docs
     f. INVOKE LINE - Command and keywords are sensible

  4. Fix all issues by editing the file directly

  5. Message team-lead with your findings

  6. Mark your task as completed

  Framework: {framework_name}
  Documentation URL: {doc_url}
  File: {output_path}/SKILL.md
communication: |
  Send review summary to team-lead when complete.
validation: |
  - Routing table matches actual reference files on disk
  - YAML frontmatter is valid and complete
  - No broken references or phantom entries
  - Quick reference code examples are correct
```

---

## After Phase 3

Once all reviewers complete:

1. The skill is verified and ready to use
2. Report final results to the user:
   - Total issues found and fixed across all reviewers
   - Final file count and structure
   - The skill is now invocable via `/{framework-name}`
