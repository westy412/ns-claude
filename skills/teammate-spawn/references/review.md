# Profile: Review

> A sub-agent that **reviews** code or a spec against criteria. Read-mostly; may write a review/findings file. No ownership, no resumption machinery.

Use this for a per-phase code review, a spec-review agent, or any "check X against Y and report" task.

## Fill the template

Template: `templates/teammate-prompt-review.md`. Fields:

| Field | Required | Notes |
|-------|----------|-------|
| Agent name, workflow | Yes | identity |
| What to review | Yes | the files / diff / artifact in scope |
| **Review against** (spec anchor) | Yes | the spec section, acceptance criteria, or standard to judge against |
| What to check | Optional | a focused checklist for this review |
| Reference files | Optional | extra context |
| Output file | Optional | where to write findings, if a file is expected |

## Final response = structured findings

Report a structured verdict, not prose — per finding: location (`file:line`), severity (blocking / warning / nit), what's wrong, the suggested fix. End with an overall **PASS / WARN / FAIL** if the caller expects a gate. This is the review evidence the lead consumes.

No file ownership, no anti-clobber, no Git/Linear resume — a reviewer changes nothing.
