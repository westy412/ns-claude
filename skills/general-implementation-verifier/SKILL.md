---
description: Verify a general implementation against its spec. Spawns parallel verification agents to check spec compliance, completeness, and code quality. Produces a consolidated report with actionable findings. Use after general-implementation-builder completes.
disable-model-invocation: true
argument-hint: "[spec-folder-path]"
---

> **Invoke with:** `/general-implementation-verifier` | **Keywords:** verify implementation, check implementation, validate build, post-implementation review

Spawns a team of verification agents that evaluate a completed implementation against its spec. Each agent investigates a different dimension in parallel using `codebase-researcher` sub-agents. Produces a consolidated verification report that can be fed back to the implementation builder to fix issues.

**Input:** Path to a spec folder (`{workforce-root}/specs/YYYY-MM-DD-feature-name/`)
**Output:** `{spec-folder}/feedback/verification-NNN.md` -- actionable report with PASS/WARN/FAIL per criterion

## When to Use This Skill

Use this skill when:
- `general-implementation-builder` has completed (or mostly completed) an implementation
- You want to verify the implementation matches the spec before human review
- You need an actionable report of what's missing or incorrect to feed back for fixes

**Skip this skill when:**
- Verifying an agent implementation (use `agent-implementation-verifier` instead -- future skill)
- The spec hasn't been implemented yet (use `general-implementation-builder` first)
- You only need to review the spec itself (use `review-spec` instead)

## Reference Files

| Topic | Reference File | When to Load |
|-------|---------------|--------------|
| Verification dimensions | [verification-dimensions.md](references/verification-dimensions.md) | When generating teammate prompts -- defines what each agent checks |
| Report format | [report-format.md](references/report-format.md) | When consolidating results into the final report |
| Team orchestration | [team-orchestration.md](references/team-orchestration.md) | When setting up the team and spawning agents |

**Templates:**

| Template | Purpose |
|----------|---------|
| [verification-report.md](templates/verification-report.md) | Output report structure |
| [verifier-teammate.md](templates/verifier-teammate.md) | Teammate prompt template for each verification agent |

## Key Principles

1. **Read-only investigation** -- Verification agents do NOT modify code. They read, analyze, and report.
2. **Spec is the source of truth** -- Every finding references a specific spec requirement or acceptance criterion.
3. **Actionable findings only** -- Each WARN/FAIL must include what's wrong, where, and what needs to change.
4. **Parallel investigation** -- All 3 agents work simultaneously. No dependencies between them.
5. **Codebase-researcher for depth** -- Agents delegate deep code investigation to `codebase-researcher` sub-agents to manage context.
6. **Gate before action** -- Present the report. Do NOT auto-fix. The invoking agent or user decides what to do with it.
7. **Feedback flywheel** -- The report doubles as training data. Classify each requirement outcome (CORRECT/INCORRECT/AMBIGUOUS/MISSING) so review skills can detect recurring spec patterns that cause implementation failures.

## Workflow

### Phase 0: Locate Artifacts

The skill expects a spec folder path. All artifacts live within this folder.

```
{workforce-root}/specs/YYYY-MM-DD-feature-name/
├── discovery.md              ← source requirements and decisions
├── brainstorm.md             ← optional, source ideas
├── spec.md                   ← what was supposed to be built (general specs)
│   OR spec/                  ← what was supposed to be built (agent specs)
├── progress.md               ← SINGLE centralized file: pipeline history, implementation status, commits
├── reviews/
│   └── review-NNN.md         ← pre-implementation review findings
└── feedback/
    └── verification-NNN.md   ← output goes here
```

1. Receive the spec folder path (from `$ARGUMENTS` or from the invoking agent)
2. Locate the spec: `{spec-folder}/spec.md` (general) or `{spec-folder}/spec/manifest.yaml` (agent)
3. Locate the progress file: `{spec-folder}/progress.md`
4. Read both files to understand:
   - What was supposed to be built (spec: requirements, architecture, execution plan, acceptance criteria)
   - What was actually built (progress: stream status, completed files, implementation notes, deviations)
5. Determine the next verification number: count existing files in `{spec-folder}/feedback/verification-*.md` and increment
6. If spec or progress file is missing, stop and report the error

### Phase 1: Spawn Verification Team

Read [team-orchestration.md](references/team-orchestration.md) for the full setup procedure.

**Team composition (3 agents):**

| Agent | Dimension | Summary |
|-------|-----------|---------|
| `spec-compliance-verifier` | Spec Compliance | Every requirement and acceptance criterion is implemented |
| `completeness-verifier` | Completeness | All files, chunks, and phases from the execution plan exist |
| `code-quality-verifier` | Code Quality | Correctness, security, performance, maintainability, error handling |

**Setup sequence:**
1. Load the `teammate-spawn` skill: `Skill tool -> skill: "teammate-spawn"`
2. Read [verification-dimensions.md](references/verification-dimensions.md) to build each agent's task list
3. Generate teammate prompt files using [verifier-teammate.md](templates/verifier-teammate.md)
4. Create team, create tasks, spawn all 3 agents in parallel

Each agent's prompt must include:
- Path to the spec file
- Path to the progress file
- The specific dimension they're evaluating (from verification-dimensions.md)
- Instructions to use `codebase-researcher` sub-agents for deep code investigation
- The findings format they must report back in

### Phase 2: Collect Results

1. Monitor all 3 agents until complete
2. Each agent reports structured findings back via SendMessage
3. Collect all findings

### Phase 3: Consolidate Report

1. Read [report-format.md](references/report-format.md) for the consolidation rules (includes the Spec Traceability Matrix format)
2. Read [verification-report.md](templates/verification-report.md) for the output template
3. Merge findings from all 3 agents into a single report
4. **Build the Spec Traceability Matrix** -- classify each requirement as CORRECT/INCORRECT/AMBIGUOUS/MISSING (see report-format.md)
5. Apply severity rules: any FAIL in any dimension = overall verdict NEEDS FIXES
6. Create `{spec-folder}/feedback/` directory if it doesn't exist
7. Write report to `{spec-folder}/feedback/verification-NNN.md` (incrementing number)
8. Present summary to the invoking agent or user

### Future: Test Verification (Not Yet Implemented)

A 4th agent (`test-verifier`) will be added when the testing infrastructure is in place. It will verify:
- Tests exist where the spec says they should
- Tests pass
- Critical paths have coverage

This is a placeholder -- do not spawn a test verification agent.

## Quick Reference

**Invoke:**
```
/general-implementation-verifier {spec-folder-path}
```

**Spec folder structure:**
```
specs/YYYY-MM-DD-feature-name/
├── spec.md | spec/       ← reads from
├── progress.md           ← reads from
└── feedback/
    └── verification-NNN.md  ← writes to
```

**Verdict values:** `PASS` (all checks pass) | `NEEDS FIXES` (any FAIL exists) | `WARNINGS ONLY` (no FAILs, some WARNs)
