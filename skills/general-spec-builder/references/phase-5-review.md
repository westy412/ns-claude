# Phase 5: Review & Finalize

> **When to read:** After Phase 3 (Construction) is complete, or after Phase 4 (Handoff) if hybrid work was involved. This is the final quality gate before the spec is saved.

---

## Step 1: Check Completeness with User

Before starting review, ask the user if the spec is finished:

> "I believe the spec is complete. Is there anything else you'd like to add or change before I run the review? Or is it ready for review?"

- If the user has additions or changes → make them, then ask again
- If the user confirms it's ready → proceed to Step 2

**Do not skip this step.** The user may have context that wasn't captured during construction.

---

## Step 2: Invoke `/review-general-spec` Skill

Once the user confirms the spec is ready for review, invoke the `/review-general-spec` skill to perform a comprehensive review of the spec.

Pass the spec file path to the review-general-spec skill. It will run structural checks, trace source material coverage (cross-referencing against the discovery document and any brainstorm/research docs), and perform ambiguity analysis to catch requirements an autonomous agent could misinterpret. The review is automatically saved to the spec's `reviews/` folder.

---

## Step 3: Present Review & Gather Feedback

Present the review results to the user. The review-spec skill produces a summary table of PASS/WARN/FAIL checks.

After presenting the results:

> "Here are the review results. Would you like me to fix any of the issues found, or are there any other changes you'd like to make?"

**Feedback loop:**
- If the user requests changes → make them → re-run `/review-general-spec` → present again
- If the user is satisfied and no FAIL items remain → proceed to Step 4

**Do not proceed past this step until the user confirms the spec is good.**

---

## Step 4: Confirm Location and Save

Save `spec.md` into the existing spec folder created by the discovery skill:

> "I'll save this as `spec.md` in the spec folder at `[workforce-root]/specs/YYYY-MM-DD-feature-name/spec.md`. Good?"

If no spec folder exists, create one following the convention. Update `progress.md` to mark all sections as complete.

---

## Step 5: Handoff to Implementation

After the spec is saved, output a **short, copy-pasteable handoff message** for the next agent. This message must include:

1. **Spec location** — path to the saved spec
2. **Discovery document location** — path to the discovery doc that informed the spec
3. **Skills to load** — list from the spec's Skills section
4. **Implementation skill** — which skill to invoke
5. **Teammate spawn** — if applicable (multi-agent / teammate specs)

### Handoff Message Format

```
Read the spec folder at `[workforce-root]/specs/YYYY-MM-DD-feature-name/`.
The spec is at `spec.md` and the discovery document is at `discovery.md` in the same folder.

Load these skills: [comma-separated list from spec's Skills section]

Then invoke `/general-implementation-builder` to begin implementation.
```

### For Multi-Agent / Teammate Specs

If the spec involves a multi-agent system, agent team, or teammate-based execution (i.e., the execution plan uses team mode with multiple work streams), append:

```
After loading general-implementation-builder, also load the `teammate-spawn` skill for spawning teammates per work stream.
```

### For Hybrid Work

If the spec is hybrid (has agent components alongside API/frontend):

```
Note: The agent component requires a separate spec via `agent-spec-builder`.
```

**Why a direct handoff message?** The user may be running this in a pipeline or handing off to a fresh session. The message ensures the next agent knows exactly what to do without interpretation.

---

## Phase Completion Checklist

- [ ] User confirmed spec is complete (Step 1)
- [ ] `/review-general-spec` skill invoked and review completed
- [ ] Review results presented to user
- [ ] User feedback addressed (loop until satisfied)
- [ ] No FAIL items remaining in review
- [ ] Spec saved to `[spec-folder]/spec.md`
- [ ] Handoff message output with spec path, discovery doc path, skills, and implementation instruction
