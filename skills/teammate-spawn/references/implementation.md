# Profile: Implementation

> A worker that **edits files** and owns a stream. The heavy profile — ownership safety, resumption, and structured reporting all apply.

Use this when the sub-agent writes or changes code inside a defined ownership boundary as part of a phased build.

## Fill the template

Template: `templates/teammate-prompt-implementation.md`. Fields:

| Field | Required | Notes |
|-------|----------|-------|
| Agent name, workflow/team | Yes | identity |
| Responsibility | Yes | what this stream does |
| **Spec anchor** | Yes | the spec section(s) this worker implements — it validates its output against this and reports deviations |
| Files owned | Yes | the ownership boundary (no two workers own the same file) |
| Skills / context | Optional | domain patterns the worker must apply |
| **State sources** | Optional | `progress.md`, Linear IDs, Git conventions — supply these so a re-spawned worker resumes from reality, not memory. Omit for a fresh one-shot build. |
| Tasks | Yes | the chunks, with enough detail to act |
| Validation | Optional | checklist before marking a task done |

## Operating model (baked into the template)

- Stay inside the ownership boundary; request out-of-boundary changes from the lead rather than making them.
- **Do not revert or overwrite others' edits** — the worker is not alone in the codebase.
- Resume from the state sources when supplied, not from conversation memory.

## Final response = review evidence

The worker's final response is what the per-phase review reads. It must report: what it completed (per task), **every file changed**, how each task validated against the spec anchor (and any deviation), context/skills it read, checkpoint updates, and blockers.
