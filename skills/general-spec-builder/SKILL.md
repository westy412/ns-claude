---
name: general-spec-builder
description: Transform discovery documents into implementation specs. Handles backend APIs, frontend, features, and products. Routes pure agent work to agent-spec-builder; handles hybrid work (agent + API/frontend) by producing specs for non-agent components then handing off.
allowed-tools: Read, Glob, Grep, Task, AskUserQuestion, Write, Edit
---

# General Spec Builder Skill

## Purpose

Transform a discovery document (from the `brainstorm` skill) into a formal spec that can be executed by the autonomous Ralph loop.

**Goal:** Produce a spec detailed enough for Claude to work through autonomously, with clear work breakdown, acceptance criteria, and completion promise.

**This skill handles:**
- Backend APIs
- Frontend features
- Products (multi-component)
- Features (general)
- Hybrid work (agent + API/frontend)

**This skill routes to `agent-spec-builder` for:**
- Pure agent systems (single agent or agent teams with no API/frontend components)

---

## What a Spec Is

A Spec is for a **big piece of work** that gets broken into smaller chunks:
- Each chunk becomes a Linear issue with its own tasks
- The Spec is a **working document** — it gets updated as work progresses (issue IDs added, checkboxes ticked off)
- Location: `/specs/[name].md` in the repo root

### Spec vs Other Artifacts

| Artifact | Contains | Mutability |
|----------|----------|------------|
| **Spec** | Requirements, architecture, skills to load, work breakdown, acceptance criteria | Updated during work (issue IDs, progress checkmarks) |
| **Linear Issue** | Chunk-level context, tasks, progress comments, Q&A | Updated frequently by agent |
| **Skills** | How to build things (patterns, anti-patterns, standards) | Rarely changes, reusable across projects |
| **CLAUDE.md** | Project-level rules and conventions | Rarely changes |

### What Does NOT Go in a Spec

| Don't Include | Why | Where It Goes |
|---------------|-----|---------------|
| Progress updates | Changes frequently | Linear issue comments |
| Code decisions made during implementation | Discovered during execution | Git commit messages |
| Session state / handover notes | Not used in this workflow | Git + Linear IS the state |
| Detailed code examples | Too granular | Skills or inline during implementation |

---

## When to Use This Skill

Use this skill when:
- You have a discovery document ready from brainstorming
- The work involves APIs, frontend, or general features
- The work is a hybrid (agent system + supporting API/frontend)

**Route to `agent-spec-builder` instead when:**
- The work is purely an agent system with no other components
- The discovery doc describes only agent orchestration, prompts, tools

---

## Input: Discovery Document

This skill expects a discovery document containing:
- Problem statement
- Solution overview
- Key decisions (with rationale)
- Constraints
- Scope (in/out/deferred)
- Context (codebase, integrations)
- Open questions

If no discovery document exists, suggest running the `brainstorm` skill first.

---

## The Spec Template

```markdown
# [Work Title]

## Meta

| Field | Value |
|-------|-------|
| Type | backend-api / frontend / agent-langgraph / agent-dspy |
| Repo | [repository name] |
| Status | draft / in-progress / complete |
| Created | [date] |

## Overview

[What we're building and why. 2-3 paragraphs max.]

## Skills

Load these skills before starting:
- [skill-name-1]
- [skill-name-2]

## Requirements

[The actual requirements. What needs to be true when this is done.]

## Architecture

[Key decisions, patterns to follow, constraints. Optional for simple work.]

## Work Breakdown

<!-- Each item becomes a Linear issue. Add issue IDs when created. -->

- [ ] [Chunk 1 description]
- [ ] [Chunk 2 description]
- [ ] [Chunk 3 description]

## Acceptance Criteria

<!-- For the WHOLE spec, not individual chunks -->

- [ ] [Criterion 1 - must be verifiable]
- [ ] [Criterion 2]
- [ ] All tests pass: `[test command]`
- [ ] Linting clean: `[lint command]`

## Completion Promise

<promise>[UNIQUE_COMPLETION_STRING]</promise>

## Notes

[Design decisions made during work, context discovered, etc.]
```

---

## Section-by-Section Guidance

### Meta

Simple table with key metadata.

| Field | Guidance |
|-------|----------|
| **Type** | Determines which skills are likely needed (see Work Type Variations below) |
| **Repo** | Repository name from discovery doc or user input |
| **Status** | `draft` → `in-progress` → `complete` |
| **Created** | Today's date |

**Status values:**
- `draft` — Still being defined
- `in-progress` — Work has started
- `complete` — All acceptance criteria met

### Overview

2-3 paragraphs maximum. Should answer:
- What are we building?
- Why are we building it?
- What's the context?

**Keep it concise.** The discovery doc has the full thinking; the spec is operational.

### Skills

Explicit list of skills the agent should load before starting work. The agent uses the Skill tool to invoke each one:

```
Use the Skill tool to invoke: skill: "backend-api"
```

**Note:** Some skills may not exist yet. List what SHOULD be loaded; the agent will skip missing ones.

### Requirements

The "what" — what needs to be true when this work is complete.

- Can be prose or bullets
- Should be specific enough that acceptance can be verified
- Transform from discovery doc's "Solution Overview" and "Scope"
- Include both functional and non-functional requirements

**Ask user to validate:** "Here are the requirements I've extracted. Anything missing or wrong?"

### Architecture

**Optional for simple work.** Include when:
- There are key technical decisions to follow
- Specific patterns must be used
- Constraints exist (performance, compatibility, etc.)
- Multiple components need to coordinate

Pull from:
- Discovery doc's "Key Decisions"
- Research findings (codebase patterns, reference projects)
- User input on preferences

### Work Breakdown

**This is the key section for autonomous execution.** Each line item:
- Becomes a Linear issue
- Gets an issue ID added when created (e.g., NS-123)
- Gets checked off when that chunk is complete

**Example progression:**

Initially:
```markdown
## Work Breakdown

- [ ] Core auth endpoints
- [ ] JWT refresh flow
- [ ] Rate limiting
```

After Linear issues created:
```markdown
## Work Breakdown

- [ ] Core auth endpoints (NS-101)
- [ ] JWT refresh flow (NS-102)
- [ ] Rate limiting (NS-103)
```

After first chunk complete:
```markdown
## Work Breakdown

- [x] Core auth endpoints (NS-101)
- [ ] JWT refresh flow (NS-102)
- [ ] Rate limiting (NS-103)
```

**Chunking principles:**
- Each chunk should be a coherent unit of work
- Not too big (should be completable in reasonable time)
- Not too small (each becomes a Linear issue; too many = overhead)
- Should be independently completable
- Should have clear boundaries

**Ask user:** "Does this breakdown make sense? Are chunks the right size?"

### Work Breakdown Structure

Each work breakdown item should include:

1. **Bold title** — What's being built
2. **Outcome statement** — What success looks like (1-2 sentences)
3. **Sub-tasks** — Detailed steps, but outcome-focused not prescriptive

**Structure example:**
```markdown
### [Service/Component Name]

- [ ] **[Chunk title]**

  **Outcome:** [What success looks like - 1-2 sentences]

  - [Sub-task describing WHAT, not HOW]
  - [Reference patterns to follow]
  - [Reference skills to use]
  - [More sub-tasks...]
```

### Sub-task Guidance

Sub-tasks should describe **WHAT** needs to happen, not **HOW** to implement it:

| Do | Don't |
|----|-------|
| "Create Pydantic models for carousel JSON output" | "Create `src/app/schemas/carousel_content.py` with `SlideType` enum" |
| "Follow existing initial_draft agent patterns" | "Create `planning.py` with `PlanningOutput` model, temperature 0.7" |
| "Add API endpoint for carousel draft" | "Add `POST /agents/carousel/draft` in `main.py` at line 45" |
| "Use `prompt-engineering` skill for prompts" | "Write system prompt with 500 tokens max" |

**Why:** The agent executing the work will:
- Have full codebase access to discover implementation details
- Find existing patterns and conventions
- Make appropriate implementation decisions based on context

The spec provides **direction and constraints**, not a code walkthrough.

### Chunk Sizing for AI Agent Execution

When the spec will be executed by an AI agent:

**Group by service/component:**
- Agent Service, Backend API, Frontend as separate chunks
- Related tasks that touch the same codebase area stay together

**Right-size for autonomous work:**
- Each chunk = 2-8 hours of focused work
- 5-8 chunks typical for a medium feature
- Not 20+ granular items (too much overhead)
- Not 2-3 massive items (too hard to track progress)

**Each chunk needs a clear "done" state:**
- The outcome statement defines what success looks like
- Agent can verify completion before moving on

**Good example:**
```markdown
### Agent Service

- [ ] **Carousel content agents**

  **Outcome:** Two new agents that output structured JSON for carousel content creation and iteration.

  **Schemas:**
  - Create Pydantic models for carousel JSON output
  - Define slide type enum with all supported types
  - Define input/output schemas for draft and iteration agents

  **Carousel draft agent:**
  - Create new agent following existing initial_draft agent patterns
  - Use Planning → Research → Creation ↔ Critic workflow
  - Use `prompt-creator` subagent and `prompt-engineering` skill for prompts
  - Reference existing prompts for patterns
  - Add API endpoint
```

**Bad example (too prescriptive):**
```markdown
- [ ] Create `src/app/schemas/carousel_content.py`
- [ ] Define `SlideType` enum with values: COVER, STANDARD_CONTENT...
- [ ] Define `SlideContent` Pydantic model with fields: slide_number (int)...
- [ ] Create `agents/carousel/draft/__init__.py`
- [ ] Create `agents/carousel/draft/planning.py` with PlanningOutput model...
```

**Bad example (too vague):**
```markdown
- [ ] Build carousel agents
- [ ] Add API stuff
- [ ] Make frontend work
```

### Acceptance Criteria

For the **whole spec**, not individual chunks. Must be verifiable — preferably with commands:

```markdown
## Acceptance Criteria

- [ ] User can log in with email/password
- [ ] JWT tokens expire after 1 hour
- [ ] Refresh tokens rotate on use
- [ ] All tests pass: `pytest tests/auth/`
- [ ] Linting clean: `ruff check src/`
```

**Pull from:**
- Discovery doc's success criteria
- Requirements (inverted into verifiable checks)
- Standard quality gates (tests, linting, type checking)

### Completion Promise

A unique string that signals the entire spec is complete. The Ralph loop watches for this.

**Format:** `<promise>[DESCRIPTIVE_NAME]_COMPLETE</promise>`

**Examples:**
- `<promise>AUTH_SYSTEM_COMPLETE</promise>`
- `<promise>USER_ONBOARDING_COMPLETE</promise>`
- `<promise>CONTENT_REPURPOSE_AGENT_COMPLETE</promise>`

**Must be unique within the project.**

### Notes

Accumulates during work:
- Design decisions made
- Context discovered
- Trade-offs chosen
- Anything future readers should know

Initially can be empty or populated with key decisions from the discovery doc that should be preserved.

---

## Work Type Variations

The template is the same for all work types. The differences are:

| Type | Skills Section | Architecture Section | Notes |
|------|----------------|---------------------|-------|
| `backend-api` | backend-api, possibly auth/database | Usually needed | API contracts, database schema |
| `frontend` | frontend-nextjs | Sometimes needed | Component hierarchy, state management |
| `agent-langgraph` | agent-spec-builder, agent-impl-builder | Always needed | Agent types, orchestration pattern |
| `agent-dspy` | agent-spec-builder, agent-impl-builder | Always needed | Pipeline structure, optimization targets |

### Backend API Specifics

**Architecture section should include:**
- API contract overview (key endpoints)
- Database schema or changes
- Authentication/authorization approach
- Error handling patterns

**Work breakdown typically:**
- Database/model setup
- Core endpoints (grouped logically)
- Authentication integration
- Validation and error handling
- Tests

**Research to do:**
- Existing API patterns in the repo
- Database conventions
- Auth patterns already in use

### Frontend Specifics

**Architecture section should include:**
- Component hierarchy
- State management approach
- Routing structure
- Styling conventions

**Work breakdown typically:**
- Component scaffolding
- State management setup
- Individual page/feature components
- Styling and responsiveness
- Tests

**Research to do:**
- Existing component patterns
- Styling conventions (Tailwind? CSS modules?)
- State management patterns in use

### Hybrid Specifics (Agent + API/Frontend)

**Architecture section should include:**
- How agent interacts with other components
- Data flow between agent and API/frontend
- Sequencing (what gets built first)

**Work breakdown:**
- Non-agent components FIRST (agent may depend on them)
- Agent system as a later chunk (handed off to agent-spec-builder)

```markdown
## Work Breakdown

- [ ] API endpoint for content storage
- [ ] API endpoint for retrieval
- [ ] Frontend content display component
- [ ] Agent system (requires agent-spec-builder)
```

---

## How the Spec Fits in the Loop

1. Bootstrap prompt tells agent to read the spec at `{{SPEC_PATH}}`
2. Agent reads spec, loads skills listed
3. Agent looks at Work Breakdown for first unchecked item
4. Agent reads that Linear issue for detailed tasks
5. Agent works through tasks, updating Linear
6. When all tasks in issue done, agent checks off the item in spec and commits
7. Agent moves to next unchecked item
8. When all items checked, agent verifies Acceptance Criteria
9. If all pass, agent outputs Completion Promise wrapped in `<promise></promise>` tags

---

## Workflow

### Phase 1: Intake

1. **Locate the discovery document**
   - Ask user: "Where is the discovery document?"
   - Read and understand the full context

2. **Identify the project/repo**
   - Ask user: "Which repo is this for?" (if not clear from discovery doc)
   - Confirm the `/specs/` directory exists or should be created

3. **Determine work type(s)**

   Ask yourself: What components does this work involve?

   | Component | Signals |
   |-----------|---------|
   | Backend API | Endpoints, database, authentication, business logic |
   | Frontend | UI, components, pages, user interactions |
   | Agent | LLM orchestration, prompts, agent coordination |

   **Routing decision:**
   - Pure agent → Route to `agent-spec-builder`, exit this skill
   - API/frontend only → Continue with this skill
   - Hybrid (agent + other) → Continue, will hand off agent part later

### Phase 2: Research (If Needed)

Before writing the spec, gather context:

**Codebase research** (use `codebase-researcher` subagent):
- What patterns exist in this repo?
- How are similar features structured?
- What conventions should be followed?

**Reference project research** (if user has reference projects):
- Ask: "Are there reference projects I should look at for patterns?"
- Use `codebase-researcher` to examine them
- Extract relevant patterns and conventions

**Web research** (use `web-researcher` subagent):
- API documentation for integrations
- Best practices for specific technologies
- Library/framework patterns

**Parallelize research when possible:**
```
Task tool (parallel):
- subagent_type: "codebase-researcher" → "What patterns exist for API endpoints in this repo?"
- subagent_type: "web-researcher" → "FastAPI best practices for authentication 2026"
```

### Phase 3: Spec Construction

Work through each section WITH the user. Don't fill it out alone.

For each section:
1. Draft based on discovery doc + research
2. Present to user
3. Get feedback and refine
4. Move to next section

Use the Section-by-Section Guidance above for each section.

### Phase 4: Handoff for Hybrid Work

If the work includes an agent component:

1. **Complete the non-agent spec sections** as above
2. **Mark the agent chunk in Work Breakdown** with a note:
   ```markdown
   - [ ] Agent system (requires agent-spec-builder)
   ```
3. **Tell the user:**
   > "The spec for the API/frontend components is ready. The agent system chunk needs to go through `agent-spec-builder`. You can invoke that skill now, and it will produce the agent-specific spec that sits alongside this one."

4. **Provide context for agent-spec-builder:**
   > "When you run agent-spec-builder, point it at the discovery doc and mention that:
   > - The agent interacts with [API endpoints X, Y]
   > - The agent's output goes to [where]
   > - These non-agent components will be built [before/alongside] the agent"

### Phase 5: Review & Finalize

Before saving:

1. **Read back the full spec** to the user
2. **Ask for confirmation:** "Does this spec accurately capture what we're building? Anything to add or change?"
3. **Confirm location:** "I'll save this to `/specs/[name].md`. Good?"
4. **Save the spec**
5. **Summarize next steps:**
   > "Spec saved. Next steps:
   > 1. Create Linear issues from Work Breakdown (or let the agent do it)
   > 2. Run the Ralph loop: `./scripts/ralph.sh specs/[name].md [COMPLETION_PROMISE]`
   > [If hybrid: 3. Run agent-spec-builder for the agent component]"

---

## Example Spec

```markdown
# JWT Authentication System

## Meta

| Field | Value |
|-------|-------|
| Type | backend-api |
| Repo | ns-content-workforce-api |
| Status | in-progress |
| Created | 2026-01-22 |

## Overview

Add JWT-based authentication to the Content Workforce API. Users authenticate
with email/password, receive access and refresh tokens. Access tokens are
short-lived (1 hour), refresh tokens rotate on use.

This is required before we can add user-specific content workspaces.

## Skills

Load these skills before starting:
- backend-api
- authentication

## Requirements

- POST /auth/login accepts email + password, returns access + refresh tokens
- POST /auth/refresh accepts refresh token, returns new token pair
- Refresh tokens are single-use (rotate on use)
- Access tokens expire after 1 hour
- Refresh tokens expire after 7 days
- Failed login attempts are rate limited (5 per minute per IP)
- Passwords are hashed with bcrypt

## Architecture

- Tokens are JWTs signed with RS256
- Refresh tokens stored in database (for revocation)
- Use FastAPI dependency injection for auth middleware
- Auth middleware extracts user from token, adds to request state

## Work Breakdown

### Backend API

- [x] **Core auth endpoints** (NS-101)

  **Outcome:** Users can authenticate with email/password and receive JWT tokens.

  - Create user model with password hashing (bcrypt)
  - Implement login and register endpoints
  - Return access + refresh token pair on success
  - Follow existing API patterns in the repo

- [ ] **JWT refresh flow** (NS-102)

  **Outcome:** Users can refresh expired access tokens without re-authenticating.

  - Implement refresh endpoint
  - Store refresh tokens in database for revocation tracking
  - Implement single-use rotation (invalidate after use)

- [ ] **Rate limiting** (NS-103)

  **Outcome:** Brute force login attempts are blocked.

  - Add rate limiting middleware for auth endpoints
  - Limit to 5 failed attempts per minute per IP
  - Follow existing middleware patterns

## Acceptance Criteria

- [ ] User can log in with valid credentials
- [ ] Invalid credentials return 401
- [ ] Access token works for protected endpoints
- [ ] Refresh token returns new token pair
- [ ] Used refresh token cannot be reused
- [ ] Rate limiting blocks after 5 failed attempts
- [ ] All tests pass: `pytest tests/auth/`
- [ ] Linting clean: `ruff check src/`

## Completion Promise

<promise>AUTH_SYSTEM_COMPLETE</promise>

## Notes

- 2026-01-22: Decided on RS256 over HS256 for token signing to allow
  public key verification by other services later.
- 2026-01-22: Using python-jose for JWT handling per backend-api skill.
```

---

## Anti-Patterns

| Don't | Why |
|-------|-----|
| Copy the entire discovery doc into the spec | Spec is operational, not exploratory |
| Make work breakdown items too granular | Each becomes a Linear issue; too many = overhead |
| Make work breakdown items too large | Should be completable in reasonable time |
| Skip the Architecture section for complex work | Agent needs guidance on patterns |
| Write acceptance criteria that can't be verified | "Works well" is not verifiable |
| Finalize without user confirmation | Spec drives execution; must be right |
| Include progress updates in the spec | That goes in Linear issue comments |
| Include implementation decisions | That goes in Git commit messages |

---

## References

- `DEVELOPMENT-WORKFLOW.md` — Full workflow context and spec template
- `brainstorm` skill — Produces the discovery document this skill consumes
- `agent-spec-builder` skill — Handles pure agent work and hybrid handoffs
- `project-management` skill — Can help create Linear issues from Work Breakdown
