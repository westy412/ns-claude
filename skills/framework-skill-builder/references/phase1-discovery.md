# Phase 1: Discovery

## Purpose

Analyze the framework's documentation structure and produce a **topic map** — a list of recommended reference files with their topics and relevant doc URLs.

---

## Team Setup

```
Team name: {framework}-phase1-discovery
Teammates: 1 (doc-structure-analyzer)
Model: Opus
```

### Step-by-step

1. `TeamCreate "{framework}-phase1-discovery"`
2. Create a single task:
   ```
   TaskCreate:
     subject: "Analyze {framework} documentation structure"
     description: "Check for llms.txt, analyze doc structure, identify topics, group into reference files, output topic map"
     activeForm: "Analyzing {framework} documentation"
   ```
3. Use `/teammate-spawn` to generate prompt file (see template below)
4. Spawn the teammate:
   ```
   Task tool:
     team_name: {framework}-phase1-discovery
     name: doc-structure-analyzer
     subagent_type: general-purpose
     model: opus
     prompt: |
       You are teammate doc-structure-analyzer on team {framework}-phase1-discovery.
       Read your full instructions at:
         {project-path}/teammate-prompts/{framework}-phase1-discovery/doc-structure-analyzer.md
       Follow all steps in order.
   ```
5. Wait for completion
6. Read the topic map output from their message or task update
7. `TeamDelete`
8. Clean up: `rm -rf teammate-prompts/{framework}-phase1-discovery/`

---

## Doc Structure Analyzer Instructions

The analyzer teammate performs these steps:

### 1. Check for llms.txt

Many documentation sites provide an `/llms.txt` file designed for AI consumption.

```
Check: {doc_url}/llms.txt
Also check: {doc_url}/llms-full.txt
```

- **If found:** Parse it for a structured listing of documentation pages. This gives you the complete doc structure without manual analysis.
- **If not found:** Proceed to manual analysis (step 2).

### 2. Discover Documentation Structure

If no llms.txt, analyze the documentation manually:

1. Fetch the documentation homepage/index with `WebFetch`
2. Extract the navigation structure (sidebar, table of contents)
3. Identify all major documentation sections
4. Fetch key pages to understand topic depth

### 3. Identify Topics

Extract all major topics from the documentation:

- Core concepts and getting started
- API references
- Configuration and setup
- Advanced features
- Deployment and production
- Integration patterns

**If focus areas were specified:** Filter topics to only include the requested areas.

### 4. Group Topics into Reference Files

Apply these heuristics:

**Group together:** Related concepts that reference each other heavily
- Example: "Subagent configuration" + "subagent patterns" + "subagent inheritance" = one file (`subagents.md`)
- Example: "Installation" + "basic setup" + "first example" = one file (`getting-started.md`)

**Split apart:** Independent concerns that could be learned separately
- Example: "Streaming" and "Persistence" are separate concerns = two files
- Example: "Authentication" and "Deployment" are independent = two files

**Target:** 5-15 reference files for most frameworks. Fewer for small SDKs, more for large frameworks.

**File naming:** Use kebab-case, descriptive names (e.g., `routing-and-requests.md`, `dependency-injection.md`)

### 5. Output Topic Map

The analyzer must produce output in this format (send via message to team-lead):

```
## Topic Map for {framework}

Documentation URL: {doc_url}
llms.txt found: yes/no

### Reference Files

1. **getting-started.md**
   - Topic: Getting Started
   - Scope: Installation, basic setup, first example
   - Doc URLs:
     - {url1}
     - {url2}

2. **{topic-name}.md**
   - Topic: {Topic Name}
   - Scope: {brief description of what this file covers}
   - Doc URLs:
     - {url1}
     - {url2}

... (repeat for all files)

### Summary
- Total reference files: N
- Total doc pages referenced: M
```

---

## Teammate Prompt Template

Use `/teammate-spawn` with these values:

```
teammate-name: doc-structure-analyzer
team-name: {framework}-phase1-discovery
responsibility: Analyze {framework} documentation structure and produce a topic map for reference file creation
tasks: |
  1. Check for llms.txt at {doc_url}/llms.txt and {doc_url}/llms-full.txt
  2. If no llms.txt, fetch documentation homepage and analyze navigation structure
  3. Identify all major topics in the documentation
  4. Group related topics into reference files (5-15 files target)
  5. For each file: determine filename, topic name, scope description, and relevant doc URLs
  6. Output the complete topic map to team-lead via SendMessage
  7. Mark task as completed

  Grouping rules:
  - Group: Related concepts that reference each other -> one file
  - Split: Independent concerns that could be learned separately -> separate files
  - Use kebab-case filenames (e.g., getting-started.md, routing-and-requests.md)
  {if focus_areas: "Focus areas: {focus_areas}. Only include topics in these areas."}

  Documentation URL: {doc_url}
  Framework: {framework_name}
communication: |
  Send topic map to team-lead when complete.
  Format: See topic map format in your instructions.
validation: |
  - Every reference file has a filename, topic, scope, and at least one doc URL
  - Files are 5-15 in count (unless framework is very small or very large)
  - No duplicate topics across files
  - All major framework features are covered (or filtered by focus areas)
```

---

## Review Before Proceeding

After Phase 1 completes, review the topic map before starting Phase 2:

1. Does the number of files seem reasonable?
2. Are topic groupings logical?
3. Are there any obvious gaps in coverage?
4. Do the doc URLs look correct?

If the topic map looks wrong, you can adjust it manually before passing to Phase 2. You don't need to re-run Phase 1 — just edit the topic map.
