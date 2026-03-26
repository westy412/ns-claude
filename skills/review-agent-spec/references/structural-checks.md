# Structural Checks: Agent Spec

> 15 structural validation checks for specs produced by `agent-spec-builder`. The spec is a folder containing `manifest.yaml`, `overview.md`, team/agent specs, and optionally shared documents.

---

## Check 1: Required Root Files Present

Read the spec folder. These files MUST exist at the root level:

| File | Required | Purpose |
|------|----------|---------|
| `manifest.yaml` | Yes | Entry point for impl-builder — hierarchy + execution plan |
| `overview.md` | Yes | System-level context, architecture, decisions, reading guide |
| `progress.md` | Yes | Handover document with all decisions |

FAIL if `manifest.yaml` or `overview.md` is missing. WARN if `progress.md` is missing.

---

## Check 2: Manifest Structure

Read `manifest.yaml`. Verify it contains:

| Section | Required | What to check |
|---------|----------|---------------|
| `system.name` | Yes | Non-empty name |
| `system.type` | Yes | One of: single-agent, agent-team, nested-teams |
| `system.description` | Yes | Non-empty description |
| `hierarchy` | Yes | At least one entry matching system type |
| `files` | Yes | Complete list of all spec files |
| `execution-plan.streams` | Yes | At least one stream with `skills` field |
| `execution-plan.phases` | Yes | At least one phase with chunks |

FAIL if any required section is missing or empty.

---

## Check 3: Team Folder Completeness

For each team folder listed in the manifest hierarchy:

| File | Required | Check |
|------|----------|-------|
| `team.md` | Yes | Exists and describes orchestration |
| `agent-config.yaml` | Yes | Exists with valid YAML |
| `agents/*.md` | Yes | At least one agent spec exists |

FAIL if a team folder is missing `team.md` or `agent-config.yaml`.
FAIL if a team has zero agent specs.

---

## Check 4: Manifest-to-Files Sync

Cross-reference the manifest `files` section with actual files on disk:
- FAIL if manifest lists a file that doesn't exist
- FAIL if a spec file exists in the folder but isn't listed in manifest
- All paths in manifest must be relative to spec/

---

## Check 5: Input/Output Consistency

For each agent, trace inputs and outputs through the pipeline:

1. List every agent's input fields and output fields
2. Verify upstream agent outputs match downstream agent inputs (exact field names)
3. Verify team-level inputs map to first agent's inputs
4. Verify last agent's outputs map to team-level outputs

FAIL on any field name mismatch (e.g., `similar_creators` vs `creator_list`).

Produce a validation table:

| Field | Team Input | Agent 1 Input | Agent 1 Output | Agent 2 Input | Team Output | Match? |
|-------|-----------|---------------|-----------------|---------------|-------------|--------|

---

## Check 6: Data Flow Map

Trace each data field from request to response across the full pipeline:

| Data Field | Source | Agent A | Agent B | ... | Final Output | Consistent? |
|-----------|--------|---------|---------|-----|-------------|-------------|

FAIL if any field changes name between adjacent components without explicit transformation.

---

## Check 7: Stream Ownership

Verify no two streams own the same files/directories.
FAIL if any file appears in multiple streams.

---

## Check 8: Chunk Spec-File Mapping

Every chunk in the execution plan MUST include `spec-files`:
- FAIL if any chunk is missing the `spec-files` field
- FAIL if a listed spec-file doesn't exist on disk
- WARN if a chunk's spec-files seem incomplete (e.g., a team chunk that doesn't reference the team.md)

---

## Check 9: Stream Skills Assignment

Every stream MUST have a `skills` field (even if empty `skills: []`):
- FAIL if any stream is missing the `skills` field
- WARN if a team stream doesn't include `prompt-engineering` in skills
- WARN if a tools stream doesn't include `tools-and-utilities` in skills

---

## Check 10: Phase Dependencies

- Chunks in the same phase should be truly parallelizable
- Later phases should depend on earlier ones
- No circular dependencies
- FAIL if dependent chunks are placed in the same phase

---

## Check 11: Agent Spec Completeness

For each `agents/*.md` file, verify it contains:

| Section | What to check |
|---------|---------------|
| Role/purpose | Clear statement of what the agent does |
| Input/Output | Defined fields with types |
| Tools | Listed if applicable, or explicitly "none" |
| Model tier | Specified (economy/standard/premium) |
| Prompt config | Framework, role, modifiers defined |

WARN if any section is thin or missing.

---

## Check 12: Model Tier Appropriateness

For each agent, verify the model tier fits the role:

| Role Type | Expected Tier | Flag if... |
|-----------|--------------|------------|
| Critic-Reviewer, Planner-Strategist | Standard/Premium | Economy tier used |
| Router-Classifier, Transformer-Formatter | Economy/Standard | Premium tier used without justification |

WARN on mismatches — these may be intentional but should be confirmed.

---

## Check 13: Spec Anti-Patterns

| Anti-Pattern | Detection | Status |
|-------------|-----------|--------|
| Code examples in agent specs | Python/JS code blocks showing implementation | FAIL |
| Cross-references between sibling specs | "Same as X but for Y" instead of self-contained | FAIL |
| Missing orchestration in team.md | Team spec doesn't describe how agents connect | FAIL |
| Shared signature files between teams | Multiple teams referencing same signatures file | WARN |
| Template instances not self-contained | Instance specs reference template instead of inlining | FAIL |
| Vague tool definitions | Tool listed without inputs/outputs/purpose | WARN |

---

## Check 14: DSPy Path Validation (DSPy projects only)

If the system uses DSPy (check agent-config.yaml or manifest):

| Rule | Bad | Good | Status |
|------|-----|------|--------|
| No `programs/` wrapper | `src/programs/team_x/` | `src/team_x/` | FAIL |
| No `routes/` wrapper | `src/routes/` | `main.py` | FAIL |
| Orchestration is `team.py` | `program.py`, `pipeline.py` | `team.py` | FAIL |
| Snake_case directories | `content-draft/` | `content_draft/` | FAIL |

---

## Check 15: Instance Parity (Template-to-Instances only)

When the spec uses the template-to-instances pattern:

1. Count lines/sections in each instance spec
2. All instances should have equivalent detail (~20% variance)
3. FAIL if one instance has significantly less content than others

| Instance | Line Count | Sections | Agents | Status |
|----------|-----------|----------|--------|--------|

---

## Summary Table

After running all checks, populate:

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Required root files | | |
| 2 | Manifest structure | | |
| 3 | Team folder completeness | | |
| 4 | Manifest-to-files sync | | |
| 5 | I/O consistency | | |
| 6 | Data flow map | | |
| 7 | Stream ownership | | |
| 8 | Chunk spec-file mapping | | |
| 9 | Stream skills assignment | | |
| 10 | Phase dependencies | | |
| 11 | Agent spec completeness | | |
| 12 | Model tier appropriateness | | |
| 13 | Anti-patterns | | |
| 14 | DSPy path validation | | |
| 15 | Instance parity | | |

Note: Checks 14 and 15 are conditional — skip if not applicable and mark as N/A.
