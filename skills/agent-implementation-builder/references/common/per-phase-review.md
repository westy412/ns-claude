# Per-Phase Review Loop

> **Context:** Don't build all phases then review once at the end — review at every phase
> boundary, while the phase is small and fresh. The flow is `execute → review → fix → … → big
> review`. Read this before spec-driven phases; run it at each phase boundary.

---

## The loop

For each phase, after its chunks complete and before the next phase starts:

1. **Execute** the phase's chunks (the normal work).
2. **Review** — delegate a scoped code review to a sub-agent (below). Scope: *this phase's changed
   files* + *the spec section(s) and acceptance criteria this phase implements* — not the whole
   codebase. The reviewer checks: does the code do what the spec section says; are I/O contracts /
   field names honored; obvious bugs, missing error handling, broken conventions.
3. **Fix** — each finding runs the autonomy rule (`autonomy-and-escalation.md`): Branch A autonomous
   fix incl. spec-write-back; Branch B escalate, fire-once → Known-Risk. Re-review if the fixes were
   substantial. Loop until the phase is clean or open items are logged Known-Risks.
4. **Record** the outcome in `progress.md` (findings + resolutions) — the Layer-4 telemetry the
   retro reads.

Only then move to the next phase.

---

## Scope it tight (proportionality)

The review is scoped to the phase, so it stays cheap — it reads the phase's diff and the matching
spec slice, not the whole tree. For a trivial single-phase spec the loop collapses into just the
**big review**; don't spawn a reviewer per chunk or for a one-file change. Match the review to the
surface the phase touched.

---

## The big review (before completion)

After the final phase, run one aggregate review across the whole change before verifying acceptance
criteria — the cross-phase issues a per-phase review can't see (integration seams, inter-phase
inconsistency, end-to-end contract). Findings run the same autonomy rule. The terminal verifier is
the static half of this; here it's the build-side gate before you emit the completion promise.

On a clean big review, hand off to live validation — see `testing-handoff.md`: surface the spec's
test seed (worked examples, edge cases, tool example-I/O, acceptance criteria) and invoke the
typed-testing skill for the spec folder. Wired — its `testing_verdict` report is the live gate; if
it cannot run now, record that live testing is owed (deferral is non-blocking; silent skipping is not).

---

## Who runs it

- **Single-agent mode:** you run the review yourself.
- **Team mode:** the **lead** runs the phase review at the phase barrier (after the barrier's tasks
  complete, before unblocking the next phase) — one scoped review over the phase's combined output,
  not a per-teammate step.

**Execution (Claude Code):** spawn a `code-reviewer` sub-agent (`Task` / `subagent_type: code-reviewer`) with the scoped file list + spec slice; it returns findings. Typed-testing handoff: invoke via the `Skill` tool → `skill: "typed-testing"` with the spec-folder path.
