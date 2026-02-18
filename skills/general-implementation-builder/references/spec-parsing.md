# Spec Parsing

> **Context:** This reference covers how to parse a `/specs/[name].md` file produced by `general-spec-builder` into actionable work items. Read this during Phase 0 before any implementation begins.

---

## Spec File Location

Specs live at `/specs/[name].md` in the repo root. The user provides the path, or you discover it:

```
{repo-root}/specs/
├── auth-system.md
├── content-pipeline.md
└── ...
```

---

## Parsing Order

Parse sections in this order. Each builds on the previous:

1. **Meta** — What type of work, which repo, current status
2. **Skills** — Top-level skills to load before starting
3. **Execution Plan** — The build order (streams, phases, chunks, communication)
4. **Acceptance Criteria** — How to verify completion
5. **Completion Promise** — The signal to emit when done

Overview, Requirements, Architecture, and Reference Files provide context but don't directly drive the work breakdown.

---

## Section: Meta

```markdown
## Meta

| Field | Value |
|-------|-------|
| Type | backend-api / frontend / agent-langgraph / agent-dspy |
| Repo | [repository name] |
| Status | draft / in-progress / complete |
| Created | [date] |
```

**Extract:**
- `Type` — Determines general approach (but skills handle specifics)
- `Repo` — The target repository
- `Status` — If `complete`, nothing to do. If `draft`, warn user it may not be ready

**Action:** If Status is `draft`, ask the user: "This spec is still in draft. Are you sure you want to start implementation?"

---

## Section: Skills

```markdown
## Skills

Load these skills before starting:
- [skill-name-1]
- [skill-name-2]
```

**Extract:** List of skill names.

**Action:** These are loaded by the lead agent during Phase 0 (one at a time, just-in-time). They provide domain patterns for the type of work.

**If skills are listed:** Load the first skill before beginning. Load additional skills as needed during execution.

**If section is empty or missing:** Proceed without domain skills. The spec and its chunks contain the guidance.

---

## Section: Execution Plan

This is the primary section driving implementation. It contains three sub-sections:

### Work Streams Table

```markdown
### Work Streams

| Stream | Responsibility | Owns | Skills |
|--------|---------------|------|--------|
| data | Database models | src/models/, src/auth/ | backend-api |
| api | API endpoints | src/api/, src/middleware/ | backend-api |
```

**Extract per stream:**
- `Stream` — Name (used for teammate names and task assignments)
- `Responsibility` — What this stream handles (goes in teammate prompt)
- `Owns` — Files/directories this stream may edit (enforces ownership)
- `Skills` — Skills the stream's agent should load (passed to teammate prompt)

**Key rule:** No two streams should own the same file. If they do, flag it.

### Phase Sections

```markdown
### Phase 1: [Phase Name]

| Chunk | Stream | Outcome | Depends On |
|-------|--------|---------|------------|
| [chunk-name] | [stream] | [success statement] | — |

**Details:**

- [ ] **[Chunk name]**
  Outcome: [success statement]
  Stream: [stream-name]
  Skills: [skills]
  - [Sub-task 1]
  - [Sub-task 2]
```

**Extract per phase:**
- Phase number and name
- All chunks with: name, stream, outcome, dependencies

**Extract per chunk:**
- Name, stream assignment, outcome statement
- Skills to load (may differ from stream-level skills)
- Sub-tasks (the actual work items)
- Dependencies (which phases or chunks must complete first)
- Linear issue ID if present (e.g., `(NS-101)`)
- Completion status: `- [ ]` = pending, `- [x]` = done

**Phase ordering:** Phases execute sequentially. All chunks within a phase can execute in parallel (across different streams).

### Communication Table

```markdown
### Communication

| From | To | When | What |
|------|----|------|------|
| data | api | After Phase 1 | Model schemas and field types |
```

**Extract per row:**
- Source stream, target stream(s)
- Trigger event (after which phase/chunk)
- What data to communicate

**Action:** Communication rules go into teammate prompts so each stream knows when to send/expect data.

---

## Section: Acceptance Criteria

```markdown
## Acceptance Criteria

- [ ] User can log in with valid credentials
- [ ] All tests pass: `pytest tests/auth/`
- [ ] Linting clean: `ruff check src/`
```

**Extract:** List of verifiable criteria, including any test/lint commands.

**Action:** After all phases complete, verify each criterion. Only output the completion promise when ALL criteria pass.

---

## Section: Completion Promise

```markdown
## Completion Promise

<promise>AUTH_SYSTEM_COMPLETE</promise>
```

**Extract:** The promise string between `<promise>` tags.

**Action:** Output this exact string (wrapped in `<promise>` tags) after all acceptance criteria pass.

---

## Edge Cases

| Situation | How to Handle |
|-----------|---------------|
| Missing Execution Plan | Treat entire spec as a single chunk in a single phase. Single-agent mode. |
| Missing Work Streams | No team mode. Execute phases sequentially as single agent. |
| Missing Communication table | No inter-stream communication needed. |
| Missing Skills section | Proceed without domain skills. |
| Missing Acceptance Criteria | Ask user: "No acceptance criteria defined. How should I verify completion?" |
| Missing Completion Promise | Generate one from the spec title: `[TITLE_UPPER_SNAKE]_COMPLETE` |
| Chunks marked `[x]` (done) | Skip them. Only work on unchecked chunks. |
| Status is `complete` | Nothing to do. Inform user the spec is already complete. |
| Single stream across all phases | Single-agent mode (no team needed). |
