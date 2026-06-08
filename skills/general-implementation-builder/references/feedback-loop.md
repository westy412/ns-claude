# Feedback Loop & Autonomy Rule

> **Context:** How the builder handles any finding about the work in progress — user feedback, a
> per-phase review issue, a verifier mismatch, an I/O-trace divergence. Every finding runs the
> fix-or-escalate decision in `references/autonomy-and-escalation.md`; this file is the builder-side
> application of it. Read it whenever a finding lands.

---

## The decision (every finding runs this)

Run the one question from `references/autonomy-and-escalation.md`: **"Can I resolve this from what
the user already gave me?"** (spec, discovery doc, conversation). It routes to one of two branches.

### Branch A — autonomous fix (resolvable from stated intent)

The finding is a *divergence* from what the source material already decides. Fix it; don't interrupt.

- **Code diverges from the spec** → fix the code. The spec is the truth. Then **sweep** (below).
- **The spec itself is wrong, but the discovery doc / conversation settles what it should say** →
  fix it **and write the correction back into the spec (and discovery if that's the source) — never
  code-only.** Code-only rots the spec and the spec-derived tests: both stay wrong. Patch the source,
  then bring the code into line.

Record every Branch-A fix in `progress.md` (below).

### Branch B — escalate (genuine uncertainty)

The source material genuinely doesn't decide it — a real gap or contradiction in stated intent.
**STOP and bring the user in**, following the comms standard in `references/autonomy-and-escalation.md`
(one brief specific question; ASCII-sketch a choice). **Fire each question once** — on "out of scope /
don't know / proceed," log a Known-Risk in `progress.md` and move on. Never guess; never trap the
conversation.

> **Spec-defect loopback:** a finding that the *spec* is wrong is Branch A if resolvable from intent
> (correct the spec), Branch B if not (escalate, then correct the spec). Either way the correction
> lands in the spec — the build never silently routes around a bad spec.

---

## Sweep for other instances (after any Branch-A code fix)

**If the issue is systematic** (same pattern elsewhere):
1. Search the codebase for all instances of the same pattern.
2. Apply the same fix to ALL qualifying instances.
3. Document the sweep scope in `progress.md`.

This stops the same mistake reappearing in later chunks or phases.

---

## Record in the progress document

Add to the feature folder's `progress.md` → Implementation Notes → Decisions Made:

```markdown
### Decisions Made

- **[date]:** Finding: [what was wrong]. Branch: A (autonomous) / B (escalated).
  Fix: [what changed]. Spec amended? [yes/no — where]. Applied to: [files].
  Rule: [pattern to follow going forward].
```

**Why the progress file:** this skill is technology-agnostic — no framework cheat sheets to update.
Lessons live in the spec-specific progress document so they persist across sessions and are visible to
every stream. This split (autonomous fixes vs escalations) is also the Layer-4 telemetry source.

---

## Relay a correction to other streams (team mode)

If in team mode and a correction affects another stream, the orchestration layer relays it — the parent
collects the correction and forwards it; the base never depends on peer-to-peer messaging. If the
affected stream hasn't started, put the correction in its prompt / state sources; once work resumes,
`progress.md` is the durable source.

**Execution (Claude Code):** the team lead forwards the correction; if the experimental peer mesh is
enabled, `SendMessage` it directly to the active stream.

---

## Mandatory triggers

Run this decision whenever:
- [ ] The user says the generated code is wrong
- [ ] A per-phase review or verifier flags a mismatch
- [ ] An I/O trace finds a field-name / schema divergence
- [ ] A pattern was used incorrectly, or the same mistake appears more than once

**Don't wait for multiple occurrences.** Process on the first finding.
