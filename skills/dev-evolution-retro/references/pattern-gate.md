# Pattern Gate — Cross-Run Aggregation & Proposals

> **When to read:** Phase 4 — after the per-run reports are written.

One run is noise; the cross-run signal is what compounds. A skill-change proposal fires only on a
**pattern**, and a proposal is never applied here — it is handed to `skill-updater`, which has
its own propose-gate and the human's approval in front of every edit.

---

## Aggregation

1. **Evidence set = this sweep's findings + every prior run report** reachable through the
   registry (`retro-done` rows → their `feedback/retro-NNN.md` paths). Read the prior reports'
   `retro_verdict` headers and Findings tables — no other state exists, by design.
2. **Match key = `skill × failure-class`** (the categories from
   [root-causing.md](root-causing.md)'s finding format — never free-text similarity). Two
   findings match when the same skill is attributed the same failure-class; the `prevention`
   text refines the proposal but does not define the match.
3. Count matches **per run, not per finding** — five front-load failures in one run is one run's
   worth of evidence, not five.

## The gate

| Condition | Action |
|-----------|--------|
| Same `skill × failure-class` in **≥ 2 runs** | **Proposal fires** — write a skill-updater feedback row |
| Single run, severity `high` | **Flag** — recorded and surfaced, explicitly *not* a proposal; it arms the pattern (a second run converts it) |
| Single run, severity low/medium | Recorded in the run report only; arms the pattern |
| The system working (correct escalations, clean loopbacks) | Never a proposal — baseline calibration only (root-causing Rule 4) |

## Proposal format

A proposal is a structured `skill-updater` input row:

```
- target skill(s): <skill> (both trees)
  change: <the specific change — derived from the matched findings' `prevention` hypotheses>
  failure-class: <the matched class>
  evidence: <run A — file/row> · <run B — file/row>   (every run in the pattern, cited)
  severity: <highest in the pattern>
  status: proposed
```

## Recording & handoff

1. Append proposals and flags to the registry's `## Proposals` section (status: `proposed` /
   `flagged`; later `applied (skill-updater commit SHAs)` or `dismissed (reason)`). This is the
   only content the retro writes outside spec folders.
2. Surface everything to the user: proposals with their evidence runs, flags, and any
   capture-failure findings (telemetry gaps blind the next retro — worth fixing first).
3. For each proposal the user approves, hand off to `skill-updater` with the row as its
   structured feedback (invocation mechanics: SKILL.md → Sub-Agent Delegation). **Never edit a
   skill from this skill** — even for a one-line fix.
4. Update the registry proposal rows when skill-updater lands the change (commit SHAs in the
   status). If approval happens in a later session, the next sweep's Phase 0 reconciles proposal
   statuses against landed skill-updater commits. Either way the next sweep knows the pattern was addressed and can watch for recurrence
   *after* the fix — a pattern that survives its fix is a failed prevention hypothesis, which is
   itself a finding.
