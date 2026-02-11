---
name: general-spec-builder
description: Transform discovery documents into implementation specs. Handles backend APIs, frontend, features, and products. Routes pure agent work to agent-spec-builder; handles hybrid work (agent + API/frontend) by producing specs for non-agent components then handing off.
allowed-tools: Read, Glob, Grep, Task, AskUserQuestion, Write, Edit
---

# General Spec Builder Skill

## Purpose

Transform a discovery document (from the `discovery` skill) into a formal spec that can be executed by the autonomous Ralph loop.

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
- You have a discovery document ready from the `discovery` skill
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
- **Reference files** (files consulted during discovery)
- Open questions

If no discovery document exists, suggest running the `discovery` skill first.

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

## Reference Files

<!-- Files consulted during discovery and spec creation. Helps executing agent understand context. -->

**From Discovery:**
- [file paths from discovery document's Reference Files section]

**From Spec Research:**
- [additional files examined during spec creation]

## Execution Plan

<!--
  Phases execute sequentially (Phase 2 starts after Phase 1 completes).
  Chunks within a phase execute in parallel across different agents.
  Work streams group related chunks so the same agent handles them for context continuity.
-->

### Work Streams

| Stream | Responsibility | Owns | Skills |
|--------|---------------|------|--------|
| [stream-name] | [what this stream handles] | [files/directories] | [skills to load] |

### Phase 1: [Name]

| Chunk | Stream | Outcome | Depends On |
|-------|--------|---------|------------|
| [chunk-name] | [stream] | [what success looks like] | — |

**Details:**

- [ ] **[Chunk name]**
  Outcome: [success statement]
  Stream: [stream-name]
  Skills: [skills this chunk's agent should load]
  - [Sub-task 1]
  - [Sub-task 2]

### Phase 2: [Name]

| Chunk | Stream | Outcome | Depends On |
|-------|--------|---------|------------|
| [chunk-name] | [stream] | [what success looks like] | Phase 1 |
| [chunk-name] | [stream] | [what success looks like] | Phase 1 + [specific-chunk] |

### Communication

| From | To | When | What |
|------|----|------|------|
| [stream] | [stream] | After [chunk/phase] | [what to communicate] |

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

### Reference Files

**Required section.** Lists all files that informed this spec, enabling the executing agent to understand context.

**Two sources:**
1. **From Discovery** — Copy the reference files section from the discovery document
2. **From Spec Research** — Add any additional files examined during spec creation

**Format:**
```markdown
## Reference Files

**From Discovery:**
- `src/auth/handlers.py` — Existing auth patterns
- `docs/api-design.md` — API design guidelines

**From Spec Research:**
- `src/middleware/rate_limit.py` — Rate limiting implementation to follow
- `tests/auth/` — Existing auth test patterns
```

**Why this matters:** The agent executing the spec can quickly reference these files to understand patterns, conventions, and context without re-discovering them.

### Execution Plan

**This is the key section for autonomous execution.** It defines:
- **Work streams** — groups of related chunks assigned to the same agent for context continuity
- **Phases** — sequential barriers; all chunks within a phase execute in parallel
- **Chunks** — individual units of work, each becomes a Linear issue
- **Communication** — what agents need to share between streams

**The execution plan enables team-based parallel execution.** When multiple chunks exist within a phase, they can be worked on simultaneously by different agents. Each agent retains context across phases within its work stream.

**Example progression:**

Initially:
```markdown
### Phase 1: Foundation

| Chunk | Stream | Outcome | Depends On |
|-------|--------|---------|------------|
| Database models | data | User and token tables exist | — |
| Auth utilities | api | JWT and password utilities work | — |

- [ ] **Database models**
  Outcome: User and token tables exist with proper indexes.
  Stream: data
  Skills: backend-api
  - Create User model with password hashing
  - Create RefreshToken model
```

After Linear issues created (issue IDs added):
```markdown
- [ ] **Database models** (NS-101)
```

After chunk complete:
```markdown
- [x] **Database models** (NS-101)
```

**Chunking principles:**
- Each chunk should be a coherent unit of work
- Not too big (should be completable in reasonable time)
- Not too small (each becomes a Linear issue; too many = overhead)
- Should be independently completable within its phase
- Should have clear file ownership boundaries (no two streams editing the same file)

**Ask user:** "Does this execution plan make sense? Are the phases and streams right?"

### Execution Plan Structure

Each chunk should include:

1. **Bold title** — What's being built
2. **Outcome statement** — What success looks like (1-2 sentences)
3. **Stream** — Which work stream this belongs to
4. **Skills** — What skills the agent should load for this chunk
5. **Sub-tasks** — Detailed steps, but outcome-focused not prescriptive

**Structure example:**
```markdown
### Phase 1: [Phase Name]

| Chunk | Stream | Outcome | Depends On |
|-------|--------|---------|------------|
| [chunk-title] | [stream] | [success statement] | — |

- [ ] **[Chunk title]**

  Outcome: [What success looks like - 1-2 sentences]
  Stream: [stream-name]
  Skills: [skills to load]

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
### Phase 1: Foundation

| Chunk | Stream | Outcome | Depends On |
|-------|--------|---------|------------|
| Carousel schemas | agent-service | Pydantic models for carousel JSON output | — |
| Carousel tools | agent-service | API integration tools for content sources | — |

- [ ] **Carousel schemas**

  Outcome: Pydantic models for carousel JSON output with all slide types.
  Stream: agent-service
  Skills: backend-api

  - Create Pydantic models for carousel JSON output
  - Define slide type enum with all supported types
  - Define input/output schemas for draft and iteration agents

### Phase 2: Agents (blocked by Phase 1)

| Chunk | Stream | Outcome | Depends On |
|-------|--------|---------|------------|
| Carousel draft agent | agent-service | Draft agent creates carousel content | Phase 1 |

- [ ] **Carousel draft agent**

  Outcome: New agent that outputs structured JSON for carousel content.
  Stream: agent-service
  Skills: agent-teams, individual-agents, prompt-engineering

  - Create new agent following existing initial_draft agent patterns
  - Use Planning → Research → Creation ↔ Critic workflow
  - Use `prompt-creator` subagent and `prompt-engineering` skill for prompts
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

### Phasing Guidance

**How to identify what goes in the same phase (parallel) vs different phases (sequential):**

**Parallel signals — put in the same phase:**
- Different files or directories (no file conflicts)
- No shared state or data dependencies
- Independent test suites
- Different service boundaries (backend vs frontend vs agent)

**Sequential signals — put in different phases:**
- Schema/models needed before code that uses them
- API needed before frontend that calls it
- Base infrastructure before features that depend on it
- Shared utilities before code that imports them

**Chunk-level dependency signals:**
- One chunk produces output another chunk consumes → add explicit `Depends On`
- Two chunks in the same phase but one needs the other's file → add explicit dep OR move to next phase

**Rule of thumb:** If it can be done in parallel, it should be. Maximize parallelism.

### Work Streams

**What:** Work streams group related chunks across phases so the same agent handles them. This matters because each agent has its own context window — an agent that built the database models in Phase 1 already has context when building the API endpoints that use those models in Phase 2.

**How to define streams:**
- Group by area of concern (database, API, frontend, agent)
- Group by file ownership — a stream owns specific files/directories
- **No two streams should write to the same file** (prevents conflicts)
- Related tasks that build on each other should be in the same stream
- Each stream lists the **skills** its agent should load (e.g., backend-api, prompt-engineering)

**Example:**
```markdown
| Stream | Responsibility | Owns | Skills |
|--------|---------------|------|--------|
| data | Database models and migrations | src/models/, migrations/ | backend-api |
| api | API endpoints and middleware | src/api/, src/middleware/ | backend-api |
| frontend | UI components and pages | src/components/, src/pages/ | frontend-nextjs |
```

### Communication Between Streams

Agents in different streams may need to share information:
- A stream that builds models should tell the endpoints stream about the schemas
- A stream that builds tools should tell the agents stream about function signatures
- A stream that builds the API should tell the frontend stream about endpoints

**Define WHAT needs to be communicated, not the exact messages:**
```markdown
### Communication

| From | To | When | What |
|------|----|------|------|
| data | api | After Phase 1 | Model schemas and field types |
| api | frontend | After Phase 2 | Endpoint URLs and response shapes |
```

### When NOT to Use Teams

Teams add coordination overhead. Skip work streams and teams when:
- All work is sequential (no parallel phases)
- All chunks touch the same files (can't parallelize safely)
- Simple single-component work where one agent can handle everything efficiently

This is NOT a hard rule — use judgment. Even 2 parallel chunks can benefit from a team if the chunks are substantial. The key question is: **"Is there genuine parallelism that would save time?"**

When teams aren't warranted, the execution plan still uses phases and chunks but without work streams — a single agent works through them sequentially.

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

**Execution plan:**
- Non-agent components in earlier phases (agent may depend on them)
- Agent system in a later phase (handed off to agent-spec-builder)

```markdown
## Execution Plan

### Phase 1: API Foundation (parallel)

- [ ] **API endpoint for content storage**
  Stream: api
- [ ] **API endpoint for retrieval**
  Stream: api

### Phase 2: Frontend + Agent (parallel, blocked by Phase 1)

- [ ] **Frontend content display component**
  Stream: frontend
- [ ] **Agent system** (requires agent-spec-builder)
  Stream: agent
```

---

## How the Spec Fits in the Loop

### Single-Agent Mode (no parallel phases or teams not warranted)

1. Bootstrap prompt tells agent to read the spec at `{{SPEC_PATH}}`
2. Agent reads spec, loads skills listed
3. Agent reads Execution Plan, works through phases sequentially
4. For each phase, works through chunks in order
5. For each chunk, reads the Linear issue for detailed tasks
6. Agent works through tasks, updating Linear
7. When all tasks in chunk done, agent checks off the item and commits
8. Agent moves to next chunk / next phase
9. When all phases complete, agent verifies Acceptance Criteria
10. If all pass, agent outputs Completion Promise wrapped in `<promise></promise>` tags

### Team Mode (parallel phases with work streams)

1. Lead agent reads the spec and Execution Plan
2. Lead creates a team and spawns teammates — one per work stream
3. Lead creates tasks from chunks, with `blockedBy` for phase barriers
4. Teammates claim unblocked tasks, execute them, mark complete
5. Phase barriers auto-enforce: Phase 2 tasks unblock when all Phase 1 tasks complete
6. Teammates communicate between streams as defined in Communication section
7. When all phases complete, lead verifies Acceptance Criteria
8. Lead shuts down teammates and outputs Completion Promise

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
2. **Mark the agent chunk in Execution Plan** with a note:
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
   > 1. Create Linear issues from Execution Plan (or let the agent do it)
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

## Reference Files

**From Discovery:**
- `src/api/routes.py` — Existing API patterns
- `src/models/user.py` — User model structure

**From Spec Research:**
- `src/middleware/` — Existing middleware patterns
- `src/dependencies/` — FastAPI dependency injection examples

## Execution Plan

### Work Streams

| Stream | Responsibility | Owns | Skills |
|--------|---------------|------|--------|
| data | Database models and auth utilities | src/models/, src/auth/utils.py | backend-api |
| api | API endpoints and middleware | src/api/auth/, src/middleware/ | backend-api |

### Phase 1: Foundation (parallel)

| Chunk | Stream | Outcome | Depends On |
|-------|--------|---------|------------|
| User model + token model | data | Database tables exist with hashing | — |
| Auth utilities | data | JWT signing/verification works | — |

- [x] **User model + token model** (NS-101)

  Outcome: User and RefreshToken tables exist with proper indexes.
  Stream: data
  Skills: backend-api

  - Create User model with bcrypt password hashing
  - Create RefreshToken model for revocation tracking
  - Follow existing model patterns in the repo

- [x] **Auth utilities** (NS-104)

  Outcome: JWT encode/decode and password verification helpers work.
  Stream: data
  Skills: backend-api

  - JWT encode/decode with RS256
  - Password hashing and verification helpers

### Phase 2: Endpoints (parallel, blocked by Phase 1)

| Chunk | Stream | Outcome | Depends On |
|-------|--------|---------|------------|
| Login and register | api | Users can authenticate | Phase 1 |
| Token refresh | api | Users can refresh tokens | Phase 1 |

- [ ] **Login and register endpoints** (NS-102)

  Outcome: Users can authenticate with email/password and receive JWT tokens.
  Stream: api
  Skills: backend-api

  - POST /auth/login and POST /auth/register
  - Return access + refresh token pair on success
  - Follow existing API patterns in the repo

- [ ] **Token refresh endpoint** (NS-105)

  Outcome: Users can refresh expired access tokens without re-authenticating.
  Stream: api
  Skills: backend-api

  - POST /auth/refresh with single-use rotation
  - Store refresh tokens in database for revocation tracking

### Phase 3: Protection (blocked by Phase 2)

| Chunk | Stream | Outcome | Depends On |
|-------|--------|---------|------------|
| Auth middleware + rate limiting | api | Endpoints protected, brute force blocked | Phase 2 |

- [ ] **Auth middleware and rate limiting** (NS-103)

  Outcome: Protected endpoints require valid tokens, brute force blocked.
  Stream: api
  Skills: backend-api

  - Auth middleware extracts user from token via FastAPI dependency injection
  - Rate limiting: 5 failed attempts per minute per IP
  - Follow existing middleware patterns

### Communication

| From | To | When | What |
|------|----|------|------|
| data | api | After Phase 1 | Model schemas, utility function signatures |

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
| Make execution plan chunks too granular | Each becomes a Linear issue; too many = overhead |
| Make execution plan chunks too large | Should be completable in reasonable time |
| Put everything in one phase | Maximize parallelism — if chunks are independent, separate phases |
| Two streams writing to the same file | Causes conflicts in parallel execution |
| Skip the Architecture section for complex work | Agent needs guidance on patterns |
| Write acceptance criteria that can't be verified | "Works well" is not verifiable |
| Finalize without user confirmation | Spec drives execution; must be right |
| Include progress updates in the spec | That goes in Linear issue comments |
| Include implementation decisions | That goes in Git commit messages |

---

## References

- `DEVELOPMENT-WORKFLOW.md` — Full workflow context and spec template
- `discovery` skill — Produces the discovery document this skill consumes
- `agent-spec-builder` skill — Handles pure agent work and hybrid handoffs
- `project-management` skill — Can help create Linear issues from Execution Plan
