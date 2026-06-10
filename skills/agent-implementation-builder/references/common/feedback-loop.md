# Feedback Loop & Autonomy Rule

> **Context:** How the builder handles any finding about the work in progress — user feedback, a
> per-phase review issue, a verifier mismatch, an I/O-trace divergence, a framework-pattern misuse.
> Every finding runs the fix-or-escalate decision in `references/common/autonomy-and-escalation.md`;
> this file is the builder-side application of it. Read it whenever a finding lands.

---

## The decision (every finding runs this)

Run the one question from `references/common/autonomy-and-escalation.md`: **"Can I resolve this from
what the user already gave me?"** (spec, discovery doc, conversation). It routes to one of two branches.

### Branch A — autonomous fix (resolvable from stated intent)

The finding is a *divergence* from what the source material already decides. Fix it; don't interrupt.

- **Code diverges from the spec** → fix the code. The spec is the truth. Then **sweep** (below).
- **The spec itself is wrong, but the discovery doc / conversation settles what it should say** →
  fix it **and write the correction back into the spec (and discovery if that's the source) — never
  code-only.** Code-only rots the spec and the spec-derived tests: both stay wrong. Patch the source,
  then bring the code into line. **Boundary:** a surgical amendment may be applied in place, but
  re-check the spec's validation gates for the touched section; a structural change (agents, teams,
  I/O contracts, scope) re-enters the spec-builder per its Spec Re-Entry contract.

Record every Branch-A fix in `progress.md` (below).

### Branch B — escalate (genuine uncertainty)

The source material genuinely doesn't decide it — a real gap or contradiction in stated intent.
**STOP and bring the user in**, following the comms standard in
`references/common/autonomy-and-escalation.md` (one brief specific question; ASCII-sketch a choice).
**Fire each question once** — on "out of scope / don't know / proceed," log a Known-Risk in
`progress.md` and move on. Never guess; never trap the conversation.

> **Spec-defect loopback:** a finding that the *spec* is wrong is Branch A if resolvable from intent
> (correct the spec), Branch B if not (escalate, then correct the spec). Either way the correction
> lands in the spec — the build never silently routes around a bad spec.

---

## Sweep for other instances (after any Branch-A code fix)

**If the issue is systematic** (same pattern elsewhere):
1. Search the codebase for all instances of the same pattern.
2. Apply the same fix to ALL qualifying instances.
3. Document the sweep scope in `progress.md`.

This stops the same mistake reappearing in later phases or other agents/teams.

---

## Record in the progress document

Every finding that ran the decision gets a row in the spec folder's centralized `progress.md` →
**Drift Log / Spec-Feedback Ledger**:

```markdown
| Phase | Finding | Class | Resolution | Spec amended? | Escalated? | Front-load failure? |
|-------|---------|-------|------------|---------------|------------|---------------------|
| [N] | [what was wrong] | code-bug / spec-bug | [what changed + files] | yes (where) / no | no (Branch A) / yes (Branch B) | yes / no |
```

If the fix also sets a *rule* to follow going forward (a pattern, not a one-off), add it to
Decisions Made — the ledger tracks drift; Decisions Made tracks choices. The ledger (drift +
autonomous-vs-escalated split) is the Layer-4 telemetry source the run retro consolidates.

---

## Also update the framework cheat sheet (framework-generic lessons)

If the lesson is **framework-generic** — a LangGraph/DSPy pattern misuse that would recur in any
build, not a drift specific to this spec — *also* update the relevant cheat sheet
(`references/langgraph/CHEATSHEET.md` / `references/dspy/CHEATSHEET.md`): add or correct the
pattern, with a short why. Cheat-sheet updates **complement the ledger row, never replace it** —
the row is the run's telemetry; the cheat sheet is the cross-run carrier for framework lessons.

---

## Relay a correction to other streams (team mode)

If in team mode and a correction affects another stream, the orchestration layer relays it — the
parent collects the correction and forwards it; the base never depends on peer-to-peer messaging.
If the affected stream hasn't started, put the correction in its prompt / state sources; once work
resumes, `progress.md` is the durable source.

---

## Mandatory triggers

Run this decision whenever:
- [ ] The user says the generated code is wrong
- [ ] A per-phase review or verifier flags a mismatch
- [ ] An I/O trace finds a field-name / schema divergence
- [ ] A pattern was used incorrectly, or the same mistake appears more than once

**Don't wait for multiple occurrences.** Process on the first finding.
