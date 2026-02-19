# Framework Skill Builder - Discovery Document

**Created:** 2026-02-19
**Status:** Ready for spec creation

---

## Problem Statement

Building comprehensive skills for SDKs and frameworks (like LangChain Deep Agents, Next.js, FastAPI, etc.) is currently:

1. **Repetitive** - Each skill requires the same workflow: research docs, structure content, write reference files, verify accuracy
2. **Time-consuming** - Manual research, writing, and verification takes hours per skill
3. **Inconsistent quality** - Without a standardized process, skill quality varies
4. **Doesn't scale** - Can't rapidly build skills for multiple frameworks

**Goal:** Automate the entire skill-building process. User provides a framework name, the skill handles everything else.

---

## Solution Overview

A skill that orchestrates agent teams through a 3-phase process to build complete, verified framework skills automatically.

**Input:** Framework name (e.g., "Next.js", "FastAPI", "LangGraph")

**Output:** Complete skill with SKILL.md + reference files, verified against official docs

**Process:**
```
Upfront Questions
      ↓
Phase 1: Discovery (analyze doc structure)
      ↓
Phase 2: Content Creation (write reference files)
      ↓
Phase 2.5: SKILL.md Creation (write routing layer)
      ↓
Phase 3: Verification (review accuracy + add doc links)
      ↓
Complete verified skill
```

---

## Workflow Architecture

### Upfront Questions Phase

**Purpose:** Gather all necessary info upfront so execution can be fully autonomous.

**Questions:**
1. Framework name (e.g., "Next.js")
2. Confirm documentation URL (auto-found via WebSearch for "{framework} official documentation 2026")
3. Any specific areas to focus on? (optional - e.g., "focus on App Router, skip Pages Router")
4. Confirm output location (default: `/Users/georgewestbrook/.claude/skills/{framework-name}/`)

**Key principle:** Front-load ALL questions. No questions during execution.

**Error handling:**
- If framework name is ambiguous → Ask for clarification
- If docs are behind auth/paywall → Stop, inform user (nothing can be done)
- If docs URL not found → Ask user to provide manually

---

### Phase 1: Discovery Team

**Team:** `{framework}-phase1-discovery`

**Purpose:** Analyze documentation structure and identify topics for reference files.

**Workflow:**
```
1. TeamCreate "{framework}-phase1-discovery"
2. Use /teammate-spawn to generate analyzer prompt file
3. Spawn doc-structure-analyzer (Opus)
4. Wait for completion
5. TeamDelete
```

**Doc Structure Analyzer tasks:**

1. **Find documentation index**
   - Check for `/llms.txt` at docs site (e.g., `https://nextjs.org/llms.txt`)
   - If exists: Parse llms.txt for structured doc listing
   - If not: Read individual doc pages and work out structure manually

2. **Identify topics**
   - Extract major topics from documentation
   - Map relationships between topics
   - Determine which topics reference each other

3. **Group topics into reference files**
   - **Grouping heuristic:** Related concepts that reference each other → one file
   - **Splitting heuristic:** Independent concerns that could be learned separately → separate files
   - Example: "Streaming" and "Persistence" are separate concerns → 2 files
   - Example: "Subagents" includes configuration, patterns, inheritance → 1 file

4. **Output topic map**
   ```
   Reference Files Recommended:
   1. getting-started.md - Installation, basic setup, first example
   2. configuration.md - Config options, environment, deployment
   3. advanced-patterns.md - Best practices, design patterns
   ...

   For each file:
   - Topic name
   - Relevant doc URLs
   - Brief description of scope
   ```

**Deliverable:** Topic map with recommended reference file structure

---

### Phase 2: Content Creation Team

**Team:** `{framework}-phase2-content`

**Purpose:** Write all reference files + SKILL.md routing layer.

**Workflow:**
```
1. TeamCreate "{framework}-phase2-content"
2. For each reference file in topic map:
   - Use /teammate-spawn to generate writer prompt
3. Spawn N writers in parallel (Opus)
4. Wait for all writers to complete
5. Use /teammate-spawn to generate SKILL.md writer prompt
6. Spawn SKILL.md writer (Opus)
7. Wait for SKILL.md completion
8. TeamDelete
```

**Content Writer tasks (per reference file):**

Each writer receives:
- Topic name (e.g., "subagents")
- Relevant doc URLs
- Brief description

Each writer's job:
1. Fetch assigned documentation pages
2. Extract all technical content (APIs, code examples, patterns)
3. Structure the reference file:
   - Clear heading hierarchy
   - Code examples in fenced blocks
   - Tables for comparison/options
   - Practical notes and tips
4. Write to `/Users/georgewestbrook/.claude/skills/{framework-name}/references/{topic}.md`
5. Report completion to team-lead
6. Mark task complete

**Writers decide:**
- How to organize subsections
- Which code examples to include
- Level of detail
- Internal structure

**Writers must include:**
- All major APIs/features for their topic
- Working code examples
- Clear explanations

**SKILL.md Writer tasks (Phase 2.5):**

Runs AFTER all content writers complete.

1. Read all completed reference files
2. Create SKILL.md with:
   - YAML frontmatter (name, description, tags)
   - Routing table pointing to all reference files
   - Core concepts section
   - Quick reference section
   - Documentation links
3. Write to `/Users/georgewestbrook/.claude/skills/{framework-name}/SKILL.md`
4. Report completion
5. Mark task complete

**Why Phase 2.5:** SKILL.md writer needs to know which reference files actually exist to create accurate routing table.

---

### Phase 3: Verification Team

**Team:** `{framework}-phase3-review`

**Purpose:** Verify accuracy and quality of all files.

**Workflow:**
```
1. TeamCreate "{framework}-phase3-review"
2. For each reference file (+ SKILL.md):
   - Use /teammate-spawn to generate reviewer prompt
3. Spawn N reviewers in parallel (Opus)
4. Wait for all reviewers to complete
5. TeamDelete
```

**Reviewer tasks (per reference file):**

Each reviewer receives one file to verify.

**6-point verification checklist:**

1. ✓ **Accuracy** - All info matches official documentation
2. ✓ **Completeness** - All major APIs/features from docs are covered
3. ✓ **Code examples** - Every file has working code examples
4. ✓ **Consistency** - Terminology and patterns consistent across files
5. ✓ **Format standards** - Proper headings, tables, code blocks; no YAML frontmatter in reference files
6. ✓ **Documentation links** - Footnotes section at bottom with relevant official doc URLs

**Reviewer workflow:**
1. Fetch official documentation for their assigned topic
2. Read the reference file
3. Compare and identify issues
4. Edit the file to fix issues
5. Add "Documentation Links" section if missing
6. Report findings to team-lead
7. Mark task complete

**Output:** Verified, enhanced reference files with doc link footnotes.

---

## Team Coordination Details

### Teammate Prompt Generation

**Use `/teammate-spawn` skill** for every teammate in all 3 phases.

For each teammate:
1. Invoke `/teammate-spawn` skill
2. Provide: teammate name, team name, role, tasks, files they'll work on
3. Skill generates structured prompt file at:
   `/Users/georgewestbrook/.claude/teammate-prompts/{team-name}/{teammate-name}.md`
4. Spawn teammate with minimal prompt pointing to the file

### Task Management

Each team has a task list:
- **Phase 1:** Single task (analyze doc structure)
- **Phase 2:** N+1 tasks (N reference files + 1 SKILL.md)
- **Phase 3:** N+1 tasks (N reference files + 1 SKILL.md)

Teammates claim tasks via TaskUpdate (set owner), mark complete when done.

### Model Selection

- **Default:** Opus for all teammates (quality is critical for skill building)
- **Override:** If user specifies a different model in upfront questions, use that

### Skills Loading

- **Teammates do NOT need skills loaded** - work is research and documentation focused

---

## Key Decisions

### 1. Documentation Discovery Strategy

**Primary:** Check for `/llms.txt` at documentation site
**Fallback:** Read individual doc pages and work out structure manually
**Research assist:** Use web-researcher sub-agent if needed

**Rationale:** llms.txt files are designed for AI consumption and provide clean structure. When unavailable, manual analysis is required.

### 2. Topic Grouping Heuristic

**Group together:** Related concepts that reference each other
**Split apart:** Independent concerns that could be learned separately

**Example grouping:** Subagent configuration + patterns + inheritance → one file
**Example splitting:** Streaming vs Persistence → two files

**Rationale:** Conceptual cohesion makes reference files more useful. Users learn related concepts together.

### 3. Three Separate Teams

**Phase 1:** Discovery team
**Phase 2:** Content team
**Phase 3:** Review team

**Rationale:** Clean lifecycle management. Each team deleted when phase completes. Clear boundaries between discovery, creation, and verification.

### 4. SKILL.md Timing (Phase 2.5)

**After content writers complete, before review starts.**

**Rationale:** SKILL.md writer needs to know which reference files exist to create accurate routing table. Can't write it before files exist.

### 5. Scaling Strategy

**Always use 3-phase process regardless of framework size.**
**Agent count scales with reference file count.**

- 2 files → 2 writers, 2 reviewers
- 20 files → 20 writers, 20 reviewers

**Rationale:** Consistent process regardless of scale. Parallelization handles cost efficiently.

---

## Implementation Requirements

### Input Schema

```typescript
{
  framework_name: string,          // e.g., "Next.js", "FastAPI"
  doc_url?: string,                // Optional override (auto-found if not provided)
  focus_areas?: string[],          // Optional (e.g., ["App Router", "Server Components"])
  output_path?: string,            // Optional (defaults to ~/.claude/skills/{framework-name}/)
  model?: string                   // Optional (defaults to "opus")
}
```

### Phase 1 Output Schema

```typescript
{
  framework_name: string,
  documentation_urls: string[],
  llms_txt_found: boolean,
  reference_files: [
    {
      filename: string,            // e.g., "getting-started.md"
      topic: string,                // e.g., "Getting Started"
      doc_urls: string[],          // Relevant doc pages
      description: string          // Brief scope description
    }
  ]
}
```

### Final Output Structure

```
skills/{framework-name}/
├── SKILL.md                      # Routing layer with YAML frontmatter
└── references/
    ├── {topic-1}.md
    ├── {topic-2}.md
    └── {topic-N}.md
```

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Framework name is ambiguous (e.g., "React") | Ask user to clarify |
| Documentation URL not found via WebSearch | Ask user to provide manually |
| Documentation behind auth/paywall | Stop, inform user (cannot proceed) |
| llms.txt not found | Fallback: Manual doc structure analysis |
| Doc pages fail to fetch | Try alternative methods (curl, web-researcher), stop if all fail |
| Writer produces invalid content | Reviewers catch and fix in Phase 3 |
| Reviewer finds major gaps | Edit to fill gaps, report to team-lead |

---

## Success Criteria

A skill is complete when:

✓ SKILL.md exists with:
  - YAML frontmatter (name, description, tags)
  - Routing table to all reference files
  - Core concepts section
  - Quick reference section
  - Documentation links

✓ All reference files exist with:
  - Clear heading hierarchy
  - Working code examples
  - Proper formatting (tables, code blocks)
  - Documentation links footnotes

✓ All files verified by reviewers:
  - Accurate against official docs
  - Complete (all major APIs/features covered)
  - Consistent terminology across files
  - Proper format standards

✓ Skill is ready to invoke via `/{framework-name}`

---

## Reference Files

The following files were consulted during this discovery:

**Skills examined as patterns:**
- `/Users/georgewestbrook/.claude/skills/langchain-deep-agents/SKILL.md` - Routing layer pattern with YAML frontmatter
- `/Users/georgewestbrook/.claude/skills/langchain-deep-agents/references/*.md` - Reference file structure and formatting
- `/Users/georgewestbrook/.claude/skills/inngest-workflow/SKILL.md` - SDK skill pattern
- `/Users/georgewestbrook/.claude/skills/agent-spec-builder/SKILL.md` - Nested references pattern
- `/Users/georgewestbrook/.claude/skills/teammate-spawn/SKILL.md` - Teammate prompt generation pattern

**Process we executed:**
- Built langchain-deep-agents skill from scratch
- Used 6-agent review team to verify accuracy
- Merged with existing deepagents skill
- Split streaming/persistence for proper separation

**Tools/Skills referenced:**
- `/teammate-spawn` - For generating structured teammate prompts
- `TeamCreate` - For team lifecycle management
- `WebSearch` - For finding documentation
- `web-researcher` - For doc discovery fallback

---

## Constraints

**Hard constraints:**
- Documentation must be publicly accessible (no auth/paywall)
- Framework must have official documentation online
- Output location must be writable by the agent

**Preferences:**
- Use Opus for all teammates (can be overridden)
- Default output to `~/.claude/skills/{framework-name}/`
- Parallelize as much as possible

---

## Scope

### In Scope

- Automatic documentation discovery (WebSearch + llms.txt)
- 3-phase agent team orchestration
- Reference file topic detection and grouping
- Content writing with code examples
- Accuracy verification against official docs
- Documentation link footnotes
- SKILL.md routing layer generation
- Format enforcement (headings, tables, code blocks)

### Out of Scope

- Merging with existing skills (assume creating new only)
- User-provided content (docs must be online)
- Non-framework skills (this is specifically for SDK/framework documentation)
- Interactive mid-execution questions (all questions upfront)

### Deferred

- Custom skill templates (use discovered patterns for now)
- Multi-framework skills (one framework at a time)
- Incremental skill updates (build complete skills only)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    UPFRONT QUESTIONS                        │
│  • Framework name                                           │
│  • Confirm doc URL (auto-found via WebSearch)               │
│  • Focus areas (optional)                                   │
│  • Output location                                          │
│  • Model (defaults to Opus)                                 │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              PHASE 1: DISCOVERY TEAM                        │
│  Team: {framework}-phase1-discovery                         │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────┐                   │
│  │  Doc Structure Analyzer (Opus)       │                   │
│  ├──────────────────────────────────────┤                   │
│  │  1. Check llms.txt                   │                   │
│  │  2. Fetch documentation              │                   │
│  │  3. Identify topics                  │                   │
│  │  4. Group by cohesion                │                   │
│  │  5. Output: Topic map                │                   │
│  └──────────────────────────────────────┘                   │
│                                                              │
│  Output: List of N reference files with topics + doc URLs   │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│            PHASE 2: CONTENT CREATION TEAM                   │
│  Team: {framework}-phase2-content                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐       ┌─────────────┐    │
│  │  Writer 1   │  │  Writer 2   │  ...  │  Writer N   │    │
│  │   (Opus)    │  │   (Opus)    │       │   (Opus)    │    │
│  ├─────────────┤  ├─────────────┤       ├─────────────┤    │
│  │ Topic 1     │  │ Topic 2     │       │ Topic N     │    │
│  │ Fetch docs  │  │ Fetch docs  │       │ Fetch docs  │    │
│  │ Write ref   │  │ Write ref   │       │ Write ref   │    │
│  └─────────────┘  └─────────────┘       └─────────────┘    │
│         │                │                      │           │
│         └────────────────┴──────────────────────┘           │
│                          ↓                                   │
│                 (All writers complete)                       │
│                          ↓                                   │
│              ┌────────────────────────┐                      │
│              │  SKILL.md Writer       │                      │
│              │      (Opus)            │                      │
│              ├────────────────────────┤                      │
│              │  1. Read all ref files │                      │
│              │  2. Create routing     │                      │
│              │  3. Write SKILL.md     │                      │
│              └────────────────────────┘                      │
└────────────────────────┬────────────────────────────────────┘
                         ↓
                  TeamDelete Phase 2
                         ↓
┌─────────────────────────────────────────────────────────────┐
│             PHASE 3: VERIFICATION TEAM                      │
│  Team: {framework}-phase3-review                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐      ┌──────────────┐  │
│  │ Reviewer 1   │  │ Reviewer 2   │ ...  │ Reviewer N+1 │  │
│  │   (Opus)     │  │   (Opus)     │      │   (Opus)     │  │
│  ├──────────────┤  ├──────────────┤      ├──────────────┤  │
│  │ Verify ref 1 │  │ Verify ref 2 │      │ Verify       │  │
│  │ 6-pt check   │  │ 6-pt check   │      │ SKILL.md     │  │
│  │ Add doc link │  │ Add doc link │      │              │  │
│  │ Fix issues   │  │ Fix issues   │      │              │  │
│  └──────────────┘  └──────────────┘      └──────────────┘  │
│                                                              │
│  6-Point Verification:                                       │
│  1. Accuracy - matches official docs                        │
│  2. Completeness - all major features covered                │
│  3. Code examples - every file has working examples          │
│  4. Consistency - terminology consistent across files        │
│  5. Format - headings, tables, code blocks proper            │
│  6. Doc links - footnotes with official URLs                 │
└────────────────────────┬────────────────────────────────────┘
                         ↓
                  TeamDelete Phase 3
                         ↓
             ┌───────────────────────┐
             │   SKILL COMPLETE      │
             │  Ready to invoke via  │
             │  /{framework-name}    │
             └───────────────────────┘
```

---

## Content Writer Prompt Pattern

Generated by `/teammate-spawn` skill for each content writer:

```markdown
# Teammate: writer-{topic}

**Team:** {framework}-phase2-content
**Role:** Reference file writer

## Your Task

Write a comprehensive reference file for {framework} at:
  {output-path}/references/{topic}.md

**Topic:** {topic-name}
**Scope:** {topic-description}

### Step 1: Fetch Documentation

Use Bash with curl to fetch these doc pages:
- {doc-url-1}
- {doc-url-2}
...

### Step 2: Extract Technical Content

Extract all:
- API signatures and parameters
- Code examples
- Configuration options
- Best practices
- Common patterns

### Step 3: Structure the Reference File

Organize with:
- Clear heading hierarchy
- Code examples in fenced blocks
- Tables for comparisons/options
- Practical notes and tips

### Step 4: Write the File

Write to: {output-path}/references/{topic}.md

Do NOT include YAML frontmatter (reference files don't have it).

### Step 5: Report Completion

Message team-lead with summary of what was written.

### Step 6: Mark Task Complete

Use TaskUpdate to mark task #{task-number} as completed.
```

---

## Reviewer Prompt Pattern

Generated by `/teammate-spawn` skill for each reviewer:

```markdown
# Teammate: reviewer-{topic}

**Team:** {framework}-phase3-review
**Role:** Reference file accuracy reviewer

## Your Task

Review {output-path}/references/{topic}.md for accuracy.

### Step 1: Fetch Official Documentation

Use Bash with curl to fetch:
- {doc-url-1}
- {doc-url-2}

### Step 2: Read the Reference File

Read {output-path}/references/{topic}.md

### Step 3: Verify 6-Point Checklist

✓ Accuracy - matches official docs
✓ Completeness - all major features covered
✓ Code examples - working examples present
✓ Consistency - terminology consistent
✓ Format - proper headings, tables, code blocks
✓ Doc links - footnotes section present

### Step 4: Fix Issues

Edit the file to fix any issues found.

### Step 5: Add Documentation Links

If missing, add "Documentation Links" section at bottom.

### Step 6: Report Findings

Message team-lead with summary of fixes.

### Step 7: Mark Task Complete

Use TaskUpdate to mark task #{task-number} as completed.
```

---

## Example Execution Flow

**User input:**
> "Build a skill for FastAPI"

**Upfront Questions:**
```
Q: Confirm framework: "FastAPI"
Q: Found docs at https://fastapi.tiangolo.com - correct?
Q: Any focus areas?
A: "No, cover everything"
Q: Output to ~/.claude/skills/fastapi/?
A: "Yes"
```

**Phase 1 Discovery:**
```
TeamCreate "fastapi-phase1-discovery"
Spawn: doc-structure-analyzer
  → Checks https://fastapi.tiangolo.com/llms.txt (not found)
  → Reads docs pages manually
  → Identifies topics: Installation, First Steps, Path Operations,
     Request Body, Query Parameters, Dependencies, Security,
     Deployment, Advanced Features
  → Groups into 6 reference files:
     1. getting-started.md (Installation + First Steps)
     2. routing-and-requests.md (Path Ops + Request Body + Query Params)
     3. dependencies-and-di.md (Dependency Injection system)
     4. security.md (Auth, OAuth2, API keys)
     5. deployment.md (ASGI servers, Docker, production)
     6. advanced-features.md (Background tasks, WebSockets, etc.)
TeamDelete phase1
```

**Phase 2 Content:**
```
TeamCreate "fastapi-phase2-content"
Use /teammate-spawn to create 6 writer prompts
Spawn 6 writers in parallel (Opus)
  → Each fetches their doc pages
  → Each writes their reference file
  → All complete
Use /teammate-spawn to create SKILL.md writer prompt
Spawn SKILL.md writer (Opus)
  → Reads all 6 reference files
  → Creates routing table
  → Writes SKILL.md
TeamDelete phase2
```

**Phase 3 Review:**
```
TeamCreate "fastapi-phase3-review"
Use /teammate-spawn to create 7 reviewer prompts (6 refs + SKILL.md)
Spawn 7 reviewers in parallel (Opus)
  → Each verifies their assigned file
  → Fixes issues
  → Adds doc links
  → All complete
TeamDelete phase3
```

**Output:**
```
skills/fastapi/
├── SKILL.md
└── references/
    ├── getting-started.md
    ├── routing-and-requests.md
    ├── dependencies-and-di.md
    ├── security.md
    ├── deployment.md
    └── advanced-features.md
```

---

## Open Questions for Spec Creation

1. **Doc fetching strategy details** - Should Phase 1 analyzer fetch ALL doc content upfront and pass to Phase 2 writers, or should writers fetch their own docs? (Passing content avoids duplicate fetches but increases context size)

2. **Failure recovery** - If a writer or reviewer fails mid-phase, should the team retry that specific agent or fail the whole phase?

3. **Progress tracking** - Should there be a manifest file tracking which phase is complete, or rely on team/task deletion as the signal?

4. **User visibility** - Should the skill stream progress updates to the user, or run silently until complete?

5. **Reference file templates** - Should writers follow a template structure, or have full creative freedom within the format constraints?

---

## Next Steps

This discovery document is ready for **agent-spec-builder** or **general-spec-builder**.

The spec-builder should:
1. Design the multi-agent system architecture
2. Define the coordinator agent (Framework Skill Builder) behavior
3. Specify teammate prompt templates for each phase
4. Define state management between phases
5. Create implementation plan

Invoke with:
```
/agent-spec-builder
```

Point it at this discovery document to begin specification.
