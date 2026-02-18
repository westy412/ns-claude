# Handover Protocol

> **When to read:** When context is getting large, a session is ending, or the user pauses work. Follow this protocol to persist state for cold-start resumption.

---

## When to Trigger Handover

- When you notice responses becoming degraded or truncated
- At natural phase boundaries (end of Research, end of Construction, etc.)
- When the user indicates they want to pause
- Before a large context-consuming operation (e.g., loading extensive research results)

---

## Mandatory Steps

### 1. Update progress.md

Save ALL state needed for a cold-start resume:

- **Current phase** and exact position within the phase
- **Every decision made**, with rationale (not just the choice)
- **Discovery summary** — key facts, constraints, requirements
- **Research findings** — patterns found, reference files identified
- **User Q&A** — important questions asked and user's answers
- **Spec sections completed** — which sections are written, which are pending
- **Open questions** that still need resolution
- **Exact next steps** — which phase, which section

### 2. Verify Self-Sufficiency

A new session reading ONLY progress.md (without the discovery document or user conversation) must be able to:

- Understand the full project context
- Know every decision made and why
- Resume work at the exact right point
- Not need to re-ask the user questions already answered

### 3. Tell the User

> "I've saved all progress to progress.md. A new session can resume by invoking the `general-spec-builder` skill — it will read progress.md and continue from [exact next step]."

---

## What Makes a Good Handover

**Good:** "Phase 3, completed Meta + Overview + Skills + Requirements sections. Architecture section is next. User confirmed they want RS256 for JWT signing. Research found existing middleware patterns at `src/middleware/`. Next step: Draft Architecture section using research findings."

**Bad:** "Working on the spec. Some sections done. Need to continue."

---

## Resumption from progress.md

When a new session starts:

1. Read `progress.md` FIRST — this is the authoritative state document
2. Review: Current Phase, Decisions Made, Spec Sections Completed, Next Steps
3. Resume from the exact point described in "Resumption Instructions"
4. DO NOT re-read the discovery document if progress.md already summarizes it
5. DO NOT re-ask questions already answered in the User Q&A Log
