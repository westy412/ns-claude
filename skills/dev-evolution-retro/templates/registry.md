# Run Registry

> One row per completed run. Maintained by the `dev-evolution-retro` skill: `register` appends
> rows; `retro` sweeps rows without `retro-done` and flips them. **Do not prune, archive, or
> delete a spec folder referenced by a row that is not `retro-done`** — it holds the only copy
> of the run's telemetry.

| Run | Spec folder | Declared complete | Status | Retro report |
|-----|-------------|-------------------|--------|--------------|

## Proposals

> Written by the retro's pattern gate (skill × failure-class across ≥2 runs → proposal; single
> severe finding → flag). Applied only via `skill-updater`. Statuses: `proposed` · `flagged` ·
> `applied (SHAs)` · `dismissed (reason)`.
