# Team Mode — Dimension Fan-Out

> **When to read:** Phase 2 — spawning the analyzers. Team mode is the default; solo fallback at
> the bottom.

The retro analyzes **by dimension, not by run**: each analyzer takes ONE dimension across ALL
swept runs. Cross-run patterns surface *inside* each dimension naturally — the analyzer that
reads every run's front-load failures is the one positioned to say "discovery missed the same
class of question twice".

---

## The four dimensions

| # | Dimension | Reads (per run, from the Phase-1 manifest) | Attributes toward |
|---|-----------|--------------------------------------------|-------------------|
| 1 | **Front-load failures** | Drift Log `front-load-failure? yes` + `class: spec-bug` rows; mid-build spec amendments; Phase-0 gate escalation rows; review ambiguity findings | `discovery`, `general-spec-builder` / `agent-spec-builder` (probing, force-concreteness, pre-mortem, self-consistency) |
| 2 | **Build friction / rework** | Drift Log `class: code-bug` rows; per-phase review findings; verifier INCORRECT/MISSING matrix rows | `*-implementation-builder` (per-phase loop, phase decomposition, worker briefs via teammate-spawn) |
| 3 | **Gate effectiveness** | `review_verdict` FAIL/WARN counts + what each round caught; verifier matrix vs what reviews passed; `testing_verdict` FAILs that every static gate missed; UNTESTED rows | `review-*-spec`, `*-implementation-verifier`, `typed-testing`, spec test-seed emitters |
| 4 | **Human interruption** | Drift Log `escalated? yes (Branch B)` rows; spec-stage Escalation & Decision Record `branch-B` / `gate-override` rows; gate overrides (Known-Risk); spec-stage escalations when present | the autonomy doctrine ([autonomy-and-escalation.md](autonomy-and-escalation.md) base), Phase-0 gates, escalating skills' Branch-A/B judgement |

Overlap between dimensions is intentional (one Drift Log row can feed 1 and 4) — the lead
dedupes at consolidation; analyzers must not self-censor to avoid overlap.

---

## Spawning

1. Load the `teammate-spawn` skill and use its **research** profile (read-only analyzers
   returning findings — no file ownership, no resumption machinery).
2. Write one brief per dimension to
   `{registry-folder}/teammate-prompts/dev-evolution-retro/dimension-{n}-{name}.md`
   (`{registry-folder}` = the folder containing the registry file from Phase 0). Each brief
   carries:
   - The dimension's row from the table above (scope + reads + attribution targets)
   - The full sweep set: every run's spec-folder path + its Phase-1 manifest
   - An instruction to read [root-causing.md](root-causing.md) (give the absolute path to this
     skill's copy) and apply the attribution doctrine
   - The finding format from `root-causing.md` — verbatim; the consolidation parses it
   - Cross-run instruction: "You see every run. Where the same skill shows the same
     failure-class in more than one run, say so explicitly — name the runs."
   - No-signal instruction: "If your dimension has nothing to read for a run, report 'no signal'
     for that run explicitly — never return silence." (Feeds `dimensions_no_signal` in the report.)
   - Scope fence: findings only; no skill edits, no spec edits, no proposals (proposals are the
     lead's pattern-gate job)
3. Spawn all four in parallel, each with the minimal pointer prompt from `teammate-spawn`'s
   Execution section (it carries the platform spawn mechanics).
4. Collect findings; **review each analyzer's output before accepting** — an unattributed or
   evidence-free finding goes back or gets dropped.

---

## Fan-in (lead's consolidation, Phase 3)

1. Pool all findings; dedupe rows describing the same telemetry evidence (keep the better
   attribution; merge `also-implicated`).
2. Group by **run** → write each run's `feedback/retro-NNN.md` from
   [templates/run-report.md](../templates/run-report.md).
3. Group by **skill × failure-class** → input to the pattern gate
   ([pattern-gate.md](pattern-gate.md)).

---

## Solo fallback

For a small sweep (one run, light telemetry) or when spawning is unavailable: run the four
dimensions **sequentially yourself**, same reads, same finding format, same fan-in. Never skip a
dimension silently — if one has nothing to read (e.g. no escalations anywhere), record "dimension
4: no signal" in the run report.
