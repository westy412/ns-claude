# Run Registry

> **When to read:** `register` mode, and `retro` Phase 0 (locating the sweep queue).

The registry is the cross-run index: one small file, one row per completed run. It is the retro
queue (rows without `retro-done` are owed), the cross-run aggregation index (prior run reports
are reached through it), and nothing else — **pointers + status flags, never copied telemetry**.

---

## Location contract

- The registry lives in a **high-level folder the user chooses** — above any single project or
  spec folder, so it survives individual repos. Ask once per session if the path isn't already
  known from the conversation or the argument; suggest `{user-programming-root}/run-registry.md`
  as the default shape.
- Never hardcode a path in this skill. The user's choice is the contract.
- If the file doesn't exist at the given path, offer to create it from
  [templates/registry.md](../templates/registry.md).

---

## Registry format

One table row per run:

| Run | Spec folder | Declared complete | Status | Retro report |
|-----|-------------|-------------------|--------|--------------|
| YYYY-MM-DD-feature-name | /abs/path/to/specs/YYYY-MM-DD-feature-name/ | YYYY-MM-DD | complete | — |
| YYYY-MM-DD-other-run | /abs/path/... | YYYY-MM-DD | retro-done | feedback/retro-001.md |

- **Run** — the spec-folder name (unique enough; disambiguate with the repo name if needed).
- **Spec folder** — absolute path. The telemetry and the run report live there, not here.
- **Status** — `complete` (registered, retro owed) or `retro-done` (analysed). A lost spec
  folder is recorded as `retro-done (telemetry lost)` so it leaves the queue visibly.
- **Retro report** — path relative to the spec folder once the retro has run.

Below the table, the registry carries a `## Proposals` section (see
[pattern-gate.md](pattern-gate.md)) — the only content the retro writes outside spec folders.

---

## Register procedure

1. **The user declares the run complete — never you.** If you were routed here by `handover` or
   `typed-testing` surfacing "retro owed", *ask*: "Register this run as complete?" and proceed
   only on explicit confirmation.
2. Resolve the spec-folder path from the argument / conversation. Sanity-check it: `spec.md` (or
   `spec/manifest.yaml`) and `progress.md` exist. If the latest `feedback/` artefacts show the
   run is *not* end-to-end complete (e.g. a FAIL verdict with no follow-up, live testing owed),
   say so — the user can still register (their call), but record the gap in the row's Run name
   suffix or a note.
3. Append the row with status `complete`.
4. Confirm to the user: row added, retro owed, and the don't-prune rule below.

---

## Don't-prune rule

**Never prune, archive, or delete a spec folder referenced by a registry row that is not
`retro-done`.** The spec folder holds the only copy of the run's telemetry (no-copied-state
design); pruning it before the retro destroys the signal the whole feedback architecture exists
to collect. Surface this rule whenever registering a run, and treat a missing swept folder as a
lost-telemetry incident (Phase 0).
