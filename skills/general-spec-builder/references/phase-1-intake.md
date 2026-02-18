# Phase 1: Intake

> **When to read:** At the start of the spec-building process. This phase establishes context, identifies work type, and makes routing decisions.

---

## Step 1: Locate the Discovery Document

Ask the user: "Where is the discovery document?"

- If the user provides a path, read and understand the full document
- If no discovery document exists, suggest running the `discovery` skill first
- Extract: problem statement, solution overview, key decisions, constraints, scope, reference files, open questions

**Record in progress.md:** Discovery document location and a brief summary of its contents.

---

## Step 2: Identify the Project / Repo

Ask the user: "Which repo is this for?" (if not clear from the discovery doc)

- Confirm the `/specs/` directory exists or should be created
- Note the repo name for the Meta section

---

## Step 3: Determine Work Type

Ask yourself: What components does this work involve?

| Component | Signals |
|-----------|---------|
| Backend API | Endpoints, database, authentication, business logic |
| Frontend | UI, components, pages, user interactions |
| Agent | LLM orchestration, prompts, agent coordination |

**Routing decision:**

```
What components are involved?
├── Pure agent (no API/frontend) → Route to agent-spec-builder, exit this skill
├── API/frontend only → Continue with this skill
└── Hybrid (agent + other) → Continue, will hand off agent part in Phase 4
```

If routing to `agent-spec-builder`:
> "This looks like a pure agent system. I'll hand off to the `agent-spec-builder` skill, which specializes in agent design. You can invoke it with the discovery document."

**Record in progress.md:** Work type determination and routing decision with rationale.

---

## Step 4: Skill Discovery

Ask the user: "What skills should the implementation agent load when executing this spec? Are there technology-specific skills (e.g., `backend-api`, `frontend-nextjs`, `cloudrun-deploy`) that would help?"

**Why this matters:** The execution plan assigns skills to each work stream and chunk. Identifying skills early ensures:
- Each chunk in the execution plan has the right skills listed
- The implementing agent (or team of agents) loads appropriate context
- No guessing about which patterns to follow during implementation

**Record in progress.md:** Skills identified, with notes on which components they apply to.

---

## Step 5: Initialize Progress Tracking

If this is a new spec:
1. Create `progress.md` from `templates/progress.md` in a working location
2. Populate with the decisions made so far (work type, routing, skills)
3. Set current phase to "Intake"

If resuming:
1. Read existing `progress.md`
2. Resume from the exact point described in "Resumption Instructions"
3. Do not re-read the discovery document if progress.md already summarizes it

---

## Phase Completion Checklist

Before moving to Phase 2:
- [ ] Discovery document located and read
- [ ] Repo/project identified
- [ ] Work type determined
- [ ] Routing decision made (continue or hand off to agent-spec-builder)
- [ ] Implementation skills identified
- [ ] Progress.md initialized or resumed
