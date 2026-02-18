# Execution Plan Guide

> **When to read:** During Phase 3 (Construction) when writing the Execution Plan section of the spec. This is the most important reference — it defines the contract between spec-builder and the implementation builder.

---

## What the Execution Plan Defines

The execution plan is the bridge between "what to build" (requirements) and "how to organize the work" (implementation). It enables both single-agent sequential execution and team-based parallel execution.

Four key concepts:

| Concept | What It Is | Analogy |
|---------|-----------|---------|
| **Work Stream** | A group of related chunks owned by one agent | A specialist on the team |
| **Phase** | A sequential barrier; all chunks must complete before the next phase starts | A project milestone |
| **Chunk** | A unit of work within a phase; becomes a task or Linear issue | A work ticket |
| **Communication** | Data that flows between streams after a phase | A handoff meeting |

---

## Work Streams

### What They Are

Work streams group related chunks across phases so the same agent handles them. This matters because each agent has its own context window — an agent that built the database models in Phase 1 already has context when building the API endpoints that use those models in Phase 2.

### How to Define Streams

- Group by area of concern (database, API, frontend, agent)
- Group by file ownership — a stream owns specific files/directories
- **No two streams should write to the same file** (prevents merge conflicts in parallel execution)
- Related tasks that build on each other should be in the same stream
- Each stream lists the **skills** its agent should load

### Format

```markdown
### Work Streams

| Stream | Responsibility | Owns | Skills |
|--------|---------------|------|--------|
| data | Database models and migrations | src/models/, migrations/ | backend-api |
| api | API endpoints and middleware | src/api/, src/middleware/ | backend-api |
| frontend | UI components and pages | src/components/, src/pages/ | frontend-nextjs |
```

### When NOT to Use Streams

Skip work streams when:
- All work is sequential (no parallel phases)
- All chunks touch the same files (can't parallelize safely)
- Simple single-component work

Without streams, a single agent works through phases and chunks sequentially. The execution plan still uses phases and chunks for organization.

---

## Phases

### What They Are

Phases are sequential barriers. Phase 2 starts only after ALL chunks in Phase 1 complete. Within a phase, chunks execute in parallel.

### How to Identify Phases

**Parallel signals — put in the same phase:**
- Different files or directories (no file conflicts)
- No shared state or data dependencies
- Independent test suites
- Different service boundaries

**Sequential signals — put in different phases:**
- Schema/models needed before code that uses them
- API needed before frontend that calls it
- Base infrastructure before features that depend on it
- Shared utilities before code that imports them

### Rule of Thumb

If it can be done in parallel, it should be. Maximize parallelism.

---

## Chunks

### What They Are

Each chunk is a coherent unit of work. In team mode, each becomes a task assigned to a stream's agent. In single-agent mode, the agent works through them sequentially within each phase.

### Chunk Format

```markdown
- [ ] **[Chunk title]**

  Outcome: [What success looks like — 1-2 sentences]
  Stream: [stream-name]
  Skills: [skills to load for this chunk]

  - [Sub-task 1 — describe WHAT, not HOW]
  - [Sub-task 2 — reference patterns to follow]
  - [Sub-task 3 — reference skills to use]
```

### Sizing Guidelines

| Signal | Action |
|--------|--------|
| More than 10 chunks for a medium feature | Consolidate — too granular |
| A chunk with > 10 sub-tasks | Split — too large |
| A chunk that takes < 1 hour | Merge with related chunk |
| A chunk that takes > 8 hours | Split into smaller chunks |
| 5-8 chunks for a medium feature | Good range |

### Sub-task Guidance

Sub-tasks describe **WHAT** needs to happen, not **HOW** to implement it:

| Do | Don't |
|----|-------|
| "Create Pydantic models for carousel JSON output" | "Create `src/app/schemas/carousel.py` with `SlideType` enum" |
| "Follow existing API patterns in the repo" | "Add `POST /api/carousel` in `main.py` at line 45" |
| "Add API endpoint for carousel draft" | "Write system prompt with 500 tokens max" |
| "Use `prompt-engineering` skill for prompts" | "Create `planning.py` with temperature 0.7" |

**Why:** The implementing agent will have full codebase access to discover implementation details, find existing patterns, and make appropriate decisions. The spec provides direction and constraints, not a code walkthrough.

### Chunk-Level Dependencies

Beyond phase barriers, individual chunks can depend on specific other chunks:

```markdown
| Chunk | Stream | Outcome | Depends On |
|-------|--------|---------|------------|
| Auth middleware | api | Endpoints protected | Phase 1 + auth-utilities |
```

Use `Depends On` when:
- A chunk in Phase 2 specifically needs output from one Phase 1 chunk (not all of Phase 1)
- Two chunks in the same phase have an ordering requirement

---

## Communication

### What It Is

When agents work in parallel across streams, they may need to share information at phase boundaries. The communication section defines WHAT needs to be shared, not the exact messages.

### Format

```markdown
### Communication

| From | To | When | What |
|------|----|------|------|
| data | api | After Phase 1 | Model schemas and field types |
| api | frontend | After Phase 2 | Endpoint URLs and response shapes |
| tools | scaffold | After Phase 1 | Tool function signatures and return types |
```

### When Communication Is Needed

- A stream that builds models should tell the endpoints stream about schemas
- A stream that builds tools should tell the agents stream about function signatures
- A stream that builds the API should tell the frontend stream about endpoints

---

## Two Execution Modes

The execution plan supports two modes. The implementation builder decides which to use based on the plan structure.

### Single-Agent Mode

When the plan has no parallel work or all chunks are in one stream:

1. Agent reads the spec
2. Loads skills listed in the Skills section
3. Works through phases sequentially
4. Within each phase, works through chunks in order
5. Verifies acceptance criteria when all phases complete
6. Outputs completion promise

### Team Mode

When the plan has parallel chunks across different streams:

1. Lead agent reads the spec and execution plan
2. Lead creates a team and spawns teammates — one per work stream
3. Lead creates tasks from chunks, with `blockedBy` for phase barriers
4. Teammates claim unblocked tasks, execute them, mark complete
5. Phase barriers auto-enforce: Phase 2 tasks unblock when all Phase 1 tasks complete
6. Teammates communicate between streams as defined in Communication section
7. When all phases complete, lead verifies acceptance criteria
8. Lead shuts down teammates and outputs completion promise

---

## Spec Mutation During Execution

The spec is a **working document**. During execution:

**What gets added:**
- Linear issue IDs get appended to chunk titles: `**Database models** (NS-101)`
- Completed chunks get checked off: `- [x] **Database models** (NS-101)`

**What does NOT change:**
- Requirements
- Architecture decisions
- Acceptance criteria
- Stream definitions

---

## Example: Complete Execution Plan

```markdown
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

- [ ] **User model + token model**

  Outcome: User and RefreshToken tables exist with proper indexes.
  Stream: data
  Skills: backend-api

  - Create User model with bcrypt password hashing
  - Create RefreshToken model for revocation tracking
  - Follow existing model patterns in the repo

- [ ] **Auth utilities**

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

- [ ] **Login and register endpoints**

  Outcome: Users can authenticate with email/password and receive JWT tokens.
  Stream: api
  Skills: backend-api

  - POST /auth/login and POST /auth/register
  - Return access + refresh token pair on success
  - Follow existing API patterns in the repo

- [ ] **Token refresh endpoint**

  Outcome: Users can refresh expired access tokens without re-authenticating.
  Stream: api
  Skills: backend-api

  - POST /auth/refresh with single-use rotation
  - Store refresh tokens in database for revocation tracking

### Communication

| From | To | When | What |
|------|----|------|------|
| data | api | After Phase 1 | Model schemas, utility function signatures |
```
