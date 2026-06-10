# Root-Causing — the Attribution Doctrine

> **When to read:** Phase 2/3 — every dimension analyzer applies this; the lead applies it again
> when consolidating. This is the analytical core of the retro.

Every finding ends in the same question: **"what skill change would have prevented this?"** A
finding without a skill attribution and a prevention hypothesis is an observation, not a retro
finding.

---

## Rule 1: Failures attribute to skills, never to the user

There is no "the user didn't provide enough information" category. If the user under-specified
and the run suffered for it, the **discovery / spec-builder probing failed** — catching exactly
that is their job (checklists, force-concreteness, blocking gates, pre-mortem). The user being
wrong, vague, or changing their mind is an *input condition* the skill chain is designed to
absorb; when it isn't absorbed, the skill chain owns it.

## Rule 2: Blame flows to the earliest skill that should have caught it

Walk upstream until the first stage whose contract covers the failure:

```
The spec was wrong / incomplete / ambiguous
├── the information existed but was never asked for → discovery (prober gap)
├── it was discussed but never forced concrete → discovery / spec-builder (force-concreteness)
├── it was in the spec but self-contradictory / untestable → spec-builder (self-consistency,
│      test-source emission) AND review-*-spec (it shipped a PASS over it — both implicated)
└── it only became knowable mid-build (genuinely emergent) → no front-load failure; judge how
       the loopback handled it instead (autonomy rule, spec amendment, Drift Log row)

The spec was right, the artifact wasn't
├── caught by per-phase review → builder working as designed (only a finding if it recurs —
│      a *class* of code-bug repeating across phases/runs is a builder-skill gap)
├── caught only by the verifier → per-phase review loop gap (it should converge before the
│      final aggregate)
└── caught only by typed-testing (or by the user, after) → static-gate gap: verifier dimension
       missing, or the spec's test seed didn't force the behaviour (seed-emitter gap)

Tests were wrong / missing
├── no seed to lift → spec-builder test-source emission + review test-derivability (both)
└── seed existed but wrong → spec-builder (the seed is spec content); if testing patched the
       test instead of looping back, typed-testing misapplied the doctrine

The human was interrupted (Branch-B escalation)
├── the answer was derivable from stated intent → the escalating skill's autonomy rule
│      (escalated what Branch A covers)
├── the answer should have been in the spec → front-load failure (walk the first tree)
└── genuinely the user's call (scope change, irreversible action) → correct escalation —
       not a finding; this is the system working
```

The same Drift Log columns drive this mechanically: `front-load-failure? yes` → first tree;
`class: code-bug` → second tree; `class: spec-bug` → first tree; `escalated? yes (Branch B)` →
fourth tree.

## Rule 3: Distinguish the failure from the capture failure

Missing telemetry (no Drift Log rows despite visible rework, no escalation record despite a
clearly interrupted run) attributes to the skill that should have *written the record* — a
capture failure is a skill defect like any other, and it blinds every future retro.

## Rule 4: The system working is not a finding

Correct escalations, spec-defect loopbacks that amended the spec properly, per-phase reviews
catching bugs early — these are the design functioning. Record them (they calibrate the
baseline) but never propose a change to "fix" them.

---

## Finding format

Every analyzer emits findings in this shape (the consolidation and the pattern gate depend on it):

```
- finding: <one sentence, concrete, citing the telemetry row/file>
  run: <registry row name>
  evidence: <file:line / Drift Log row / verdict header field>
  failure-class: front-load-failure | code-bug | spec-bug | gate-miss | escalation-misfire | capture-failure
  skill: <the attributed skill — earliest that should have caught it>
  also-implicated: [<downstream skills that passed it through>]
  prevention: <the specific skill change that would have prevented this>
  severity: low | medium | high
```
