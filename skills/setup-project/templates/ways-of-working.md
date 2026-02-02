## Ways of Working

**This section defines the exact process for autonomous AI-assisted development.** Follow these conventions precisely. They enable agents to work autonomously while maintaining full visibility and control.

---

## Core Philosophy

### The Principle

**Linear is the intersection between AI agents and humans.** All significant work is tracked in Linear with comprehensive context, file references, and progress updates. Git commits are structured so future agents can understand what changed, why, and how.

**Define the work upfront, let the agent execute, review the output.**

### State Persistence

Each session starts fresh. State persists through:

| Mechanism | What It Stores |
|-----------|----------------|
| **Git commits** | Code changes, decision context in commit messages |
| **Git history** | What was done, in what order |
| **Linear issues** | Task progress, blockers, human Q&A |
| **Spec files** | Work breakdown, acceptance criteria, completion status |
| **File system** | Current state of the codebase |

**We do not use session documents.** Read reality (git + Linear + files) each session.

---

## Work Hierarchy

```
SPEC (Big Piece of Work) → Location: /specs/
         │
         │ Breaks into phases
         ▼
LINEAR ISSUE (Phase of Work)
         │
         │ Contains individual
         ▼
TASKS (Individual Actions)
```

| Scope | Artifact | Example |
|-------|----------|---------|
| Large piece of work, multiple components | Spec | "Authentication System" |
| Phase of work, discrete deliverable | Linear Issue | "JWT Refresh Flow" |
| Individual action within a phase | Task checkbox in Linear Issue | "Add refresh endpoint" |

**If a spec exists:** Read it first, find the current Linear issue, work on unchecked tasks.

**If no spec:** Work directly from Linear issues or conversation.

---

## Rule Hierarchy

When guidance conflicts, follow this precedence (highest to lowest):

| Priority | Source | Description |
|----------|--------|-------------|
| 1. User Input | Specs, Linear comments, conversation | Gospel. If user says X, do X. |
| 2. Project Rules | This CLAUDE.md | Contextual. Follow unless user overrides. |
| 3. Global Rules | Skills | Defaults. Follow unless project or user overrides. |

**Higher precedence wins. Do not reconcile contradictions.**

---

## Project Configuration

```
Linear Team: {{TEAM_NAME}}
Linear Team ID: {{TEAM_ID}}

Linear Project: {{PROJECT_NAME}}
Linear Project ID: {{PROJECT_ID}}
```

**Priority Levels:** 1=Urgent, 2=High, 3=Medium, 4=Low

---

## When to Create Linear Issues

**Create a Linear issue when:**
- Building a feature (>30 minutes of work)
- Fixing a bug that affects functionality
- Performing refactoring work
- Making architectural decisions
- Any significant work that needs to be remembered across sessions

**Do NOT create for:**
- Tiny changes (typo fixes, minor tweaks <15 min)
- Quick experiments

---

## Issue Types

Use the appropriate template from `.claude/templates/linear-issues/` when creating issues.

### 1. Feature Issues
**Use for:** New functionality, new endpoints, new capabilities

**Key sections:**
- 🎯 Context & Background - Why is this needed?
- ✅ Objective & Success Criteria - What does done look like?
- 🛠 Technical Approach - How will we implement?
- 📁 Related Files & Documentation - Links to code files, docs, related issues
- 📋 Implementation Steps - Detailed tasks (only what's requested)
- 🧠 Decisions & Trade-offs - Document technical choices (fill during work)
- 🧪 Testing & Verification - How to verify it works
- 📊 Status & Progress - Current state with comments

### 2. Bug Issues
**Use for:** Fixing broken functionality, resolving errors

**Key sections:**
- 🐛 Bug Description - Expected vs actual behavior
- 🔍 Steps to Reproduce - How to trigger the bug
- 🎯 Root Cause Analysis - What's causing it (or "Investigation Needed")
- ✅ Solution & Implementation - How to fix
- 📋 Fix Implementation Steps - Including investigation if needed
- 🧪 Testing & Verification - How to verify fix

### 3. Refactor Issues
**Use for:** Code improvements without adding functionality

**Key sections:**
- 🎯 Context & Motivation - Why refactor?
- 📊 Current State vs Target State - Before/after comparison
- 📋 Migration Plan - Step-by-step refactoring
- ⚠️ Breaking Changes & Risks - What could go wrong

### 4. Architecture Issues
**Use for:** System design, architectural decisions, technical planning

**Key sections:**
- 🎯 Problem Statement - What challenge are we solving?
- 🏗 Proposed Architecture - Design with Mermaid diagrams
- 🤔 Alternatives Considered - Other approaches evaluated
- ✅ Decision Rationale - Why this approach
- 📋 Implementation Phases - Phased rollout

| Scenario | Type | Label |
|----------|------|-------|
| Adding new feature/endpoint | Feature | `["Feature"]` |
| Fixing broken functionality | Bug | `["Bug"]` |
| Improving code structure | Refactor | `["Refactor"]` |
| Designing system architecture | Architecture | `["Architecture"]` |
| Performance optimization | Refactor | `["Improvement"]` |

---

## Linear Workflow States

| State | When to Use |
|-------|-------------|
| **Backlog** | Issue created but not prioritized |
| **To Do** | Ready to be picked up |
| **In Progress** | Actively working on it |
| **In Review** | Code complete, PR created, awaiting review |
| **Done** | Complete and merged |
| **Cancelled** | Won't be completed |

**State Transitions:**
1. **Start work** → `mcp__linear__update_issue({ id: "NS-123", state: "In Progress" })`
2. **Create PR** → `mcp__linear__update_issue({ id: "NS-123", state: "In Review" })`
3. **Merge PR** → `mcp__linear__update_issue({ id: "NS-123", state: "Done" })`

---

## Workflow for Every Task

### Before Starting Work

**If user describes new work:**

1. **Analyze task** - Choose template type (feature/bug/refactor/architecture)

2. **Draft the Linear issue:**
   - **Title:** Brief description (e.g., "Add CSV upload endpoint for leads")
   - **Description:** Full template with all sections filled
   - **Team:** Use Team ID from Project Configuration
   - **Project:** Use Project ID from Project Configuration
   - **Labels:** e.g., `["Feature"]`
   - **Priority:** 1=Urgent, 2=High, 3=Medium, 4=Low

3. **⚠️ Get user approval BEFORE creating issue**
   - Present the draft
   - Ask: "Does this look correct? Any changes needed?"
   - Only proceed after explicit approval

4. **Create Linear issue** using `mcp__linear__create_issue`

5. **Update Linear state to "In Progress"**

**If user asks to work on existing Linear issue:**

1. **Fetch issue** using `mcp__linear__get_issue` with the issue ID
2. **Read full context** from issue description
3. **Update Linear state to "In Progress"** (if not already)

**If working from a spec:**

1. **Read the spec** from `/specs/`
2. **Find current work** in Work Breakdown (first unchecked item)
3. **Read the linked Linear issue** for tasks and context
4. **Find first unchecked task** in the issue

### During Work

**Git Commits:**
- ✅ Commit after each task completion
- ✅ Only commit files that were worked on (use `git add <specific-files>`, NOT `git add -A` or `git add .`)
- ✅ Always reference the Linear issue ID in commit message
- ❌ Do NOT commit unrelated files
- ❌ Do NOT batch commits across multiple tasks

**At milestones, update Linear issue** using `mcp__linear__create_comment`:
- Add progress update
- List what's completed
- Note what's in progress

**Update Linear issue description** when you:
- Discover new context or constraints
- Make technical decisions
- Encounter blockers or issues

### When Blocked

Output the appropriate signal and **stop working**:

| Signal | When to Use |
|--------|-------------|
| `HUMAN_NEEDED:DECISION:[options]` | Need human to choose between options |
| `HUMAN_NEEDED:CLARIFICATION:[question]` | Requirement is unclear |
| `HUMAN_NEEDED:BLOCKED:[dependency]` | External blocker (access, credentials, etc.) |
| `HUMAN_NEEDED:REVIEW:[location]` | Need human review before proceeding |

When outputting a signal:
1. Add a comment to the Linear issue explaining the blocker
2. Stop working - do not continue past the blocker

### When Creating Pull Request

1. Create PR with Linear issue ID in title and description
2. Update Linear state to "In Review"
3. Add PR comment to Linear with link and summary

### When Work is Complete

1. Update Linear state to "Done"
2. Add completion comment with outcome summary
3. If working from spec, check off the Work Breakdown item and commit the spec

---

## Git Management (Agent-Optimized)

**Purpose:** Git history + Linear together form the complete knowledge base for agents. Commits are structured so future agents can quickly understand what changed, why, and how.

### When to Commit

| ✅ DO Commit | ❌ DON'T Commit |
|--------------|-----------------|
| After each task completion | Mid-task before it's working |
| When a task from Linear issue is complete | Incomplete/broken states |
| Before switching to a different task | Unrelated files you didn't work on |
| Only the specific files you changed | Using `git add -A` or `git add .` |

**Rule:** One task = one commit. Always reference the Linear issue ID.

### Commit Message Format (Agent-Parseable)

```
NS-XXX: <action-verb> <what> [<scope>]

WHAT:
- <change 1>
- <change 2>

WHY: <1-2 sentence rationale linking to the goal>

HOW: <key technical approach or decision>

FILES: <list only non-obvious key files, omit if clear from diff>

Linear: <issue-url>
```

| Section | Required | Purpose for Agents |
|---------|----------|-------------------|
| `NS-XXX: <summary>` | ✅ Yes | Quick scan in `git log --oneline` |
| `WHAT:` | ✅ Yes | Bulleted list of concrete changes |
| `WHY:` | ✅ Yes | Context without reading Linear issue |
| `HOW:` | ⚠️ If non-obvious | Technical decisions agents should know |
| `FILES:` | ⚠️ If non-obvious | Key files when diff is large/unclear |
| `Linear:` | ✅ Yes | Deep-dive link for full context |

### Using Git History as Agent Context

**Query git history to understand:**

```bash
# Recent changes to a file
git log --oneline -10 -- src/routes/leads.ts
git show <commit-hash>  # Full message + diff

# What was done for an issue
git log --oneline --grep="NS-123"

# Recent project activity
git log --oneline -20 --since="1 week ago"

# Find commits with technical decisions
git log --all --grep="HOW:" --oneline
```

**Pattern:** Git log for quick scan → `git show` for details → Linear issue for full context

### Git + Linear Relationship

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT KNOWLEDGE FLOW                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   git log --oneline     →    Quick scan of recent work      │
│          ↓                                                   │
│   git show <hash>       →    WHAT/WHY/HOW for specific      │
│          ↓                      commit                       │
│   Linear issue          →    Full context, discussions,     │
│                               related issues, attachments    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Git provides:** What changed, when, key decisions (scannable)
**Linear provides:** Why it was needed, full requirements, discussions, related work (deep context)

### Branch Management

**⚠️ Never change branches or create worktrees without user confirmation.**

**Default assumption:** User is already on the correct branch. Work on current branch unless told otherwise.

**Branch Naming Format:** `<type>/NS-XXX-short-description`

| Type | Use For |
|------|---------|
| `feature/` | New functionality |
| `bugfix/` | Bug fixes |
| `refactor/` | Code improvements |
| `architecture/` | System design changes |
| `chore/` | Config, deps, tooling |

---

## Working with Specs (Primary Entry Point)

**Specs are the entry point for resuming work.** When starting a new context window or resuming work, the spec tells you where you are and what to do next.

Specs live in `/specs/` and define larger pieces of work.

### The Spec → Linear → Git Loop

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS WORK LOOP                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   1. READ SPEC         →  Find current work (first          │
│                            unchecked item in Work Breakdown) │
│          ↓                                                   │
│   2. READ LINEAR       →  Get tasks and context from         │
│                            the linked issue                  │
│          ↓                                                   │
│   3. DO WORK           →  Implement, test, verify            │
│          ↓                                                   │
│   4. UPDATE LINEAR     →  Check off tasks, add comments      │
│          ↓                                                   │
│   5. COMMIT TO GIT     →  With proper message format         │
│          ↓                                                   │
│   6. UPDATE SPEC       →  Check off Work Breakdown item      │
│                            when Linear issue is complete     │
│          ↓                                                   │
│   7. COMMIT SPEC       →  Persist progress for next session  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Starting from a Spec

**When user says "continue the spec" or "work on specs/[name].md":**

1. **Read the spec file**
2. **Check Status** - Should be `in-progress` (update if `draft`)
3. **Load Skills** - Use Skill tool to invoke each skill listed
4. **Read CLAUDE.md** - For project conventions
5. **Check git log** - `git log --oneline -10` to see recent work
6. **Find current work** in Work Breakdown (first unchecked item)
7. **Read the linked Linear issue** for tasks and context
8. **Find first unchecked task** in the issue
9. **Work on it** following all conventions below

### Updating the Spec

**During work:**
- Add notes to the **Notes** section for decisions made

**When a Linear issue is complete:**
- Check off the Work Breakdown item in the spec
- Commit the spec: `git commit specs/[name].md -m "NS-XXX: Mark [chunk] complete in spec"`

**When all work is complete:**
- Update **Status** to `complete`
- Verify all acceptance criteria in the spec
- Run test commands listed in the spec
- Output the **Completion Promise** from the spec
- Commit the final spec update

### Three Things Always Stay in Sync

| Artifact | What to Update | When |
|----------|----------------|------|
| **Linear Issue** | Check off tasks, add comments, update state | After each task |
| **Git** | Commit code changes with proper format | After validated work |
| **Spec** | Check off Work Breakdown, add notes | After Linear issue complete |

---

## Continuing Previous Work

### From a Spec (Preferred)

**When user says "continue the spec" or references a spec file:**

Follow the "Starting from a Spec" workflow above.

### From a Specific Linear Issue

**When user says "continue NS-123" or "work on NS-456":**

1. **Fetch issue from Linear** using `mcp__linear__get_issue`

2. **Check if it's part of a spec:**
   - Look in `/specs/` for a spec that references this issue
   - If found, read the spec for full context

3. **Read full context from Linear:**
   - Context & background
   - Technical approach
   - Implementation steps (what's done, what's remaining)
   - Decisions made
   - Related files
   - Status & progress comments

4. **Continue from where left off:**
   - Don't create new issue
   - Update existing issue as you work
   - Mark tasks complete in issue description
   - Add new comments with progress
   - If part of spec, update spec when issue is complete

---

## Critical Rules

### MUST DO

- ✅ Check if spec exists and read it first (spec is the entry point)
- ✅ Get user approval BEFORE creating Linear issues
- ✅ Only create the Linear issue for the phase you're about to work on (not all phases at once)
- ✅ Create Linear issue for ALL work >30 minutes
- ✅ Fill in ALL template sections with real context and file links
- ✅ Update Linear state as work progresses
- ✅ Update spec when Linear issues are complete (check off Work Breakdown items)
- ✅ Commit after each task completion
- ✅ Only commit files you actually worked on (use `git add <specific-files>`)
- ✅ Include Linear issue ID in EVERY commit message
- ✅ Link to specific files in Linear issues (`[file.ts](src/file.ts)`)
- ✅ Use Mermaid diagrams in architecture issues
- ✅ Be specific in commits and comments (not "fixed bug" but "fixed UTF-8 encoding")
- ✅ Keep Spec, Linear, and Git in sync at all times

### MUST NOT

- ❌ Create all Linear issues upfront (only create for current phase)
- ❌ Create Linear issues without user approval
- ❌ Use `git add -A` or `git add .` (commit only specific files worked on)
- ❌ Skip creating Linear issue for significant work
- ❌ Leave template sections empty
- ❌ Add unnecessary work not requested
- ❌ Use vague commit messages ("fix bug", "update code")
- ❌ Change branches without user confirmation
- ❌ Continue past a blocker without signaling HUMAN_NEEDED
- ❌ Complete a Linear issue without updating the spec
- ❌ Forget to commit after completing a task

---

## Linear MCP Tools Reference

| Action | Tool | Key Parameters |
|--------|------|----------------|
| Create issue | `mcp__linear__create_issue` | title, description, team, project, labels, priority |
| Get issue | `mcp__linear__get_issue` | id |
| Update issue | `mcp__linear__update_issue` | id, state, description |
| Add comment | `mcp__linear__create_comment` | issueId, body |
| List issues | `mcp__linear__list_issues` | team, project, state, assignee |

---

## Codebase Research

When exploring the codebase to understand implementations, patterns, or architecture:

- ✅ **Use `codebase-researcher` agent** - Preferred for thorough code analysis
- ❌ **Avoid `Explore` agent** - Less thorough, prefer codebase-researcher

---

## Principles

1. **Front-load everything.** The more context in the spec/issue, the better the execution.
2. **State lives in Git and Linear.** Not in session documents, not in local files.
3. **Higher precedence wins.** User > Project > Global. No reconciliation.
4. **Commit meaningful units.** Not every file, not arbitrary checkpoints.
5. **Completion means tests pass.** Can't claim done without verification.
6. **When blocked, signal clearly.** `HUMAN_NEEDED` with structured reason.
7. **Review the output, not the process.** Trust the loop, verify the result.
