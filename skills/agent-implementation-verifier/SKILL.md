---
description: Verify an agent implementation against its spec. Spawns parallel verification agents to check spec compliance, completeness, framework-specific patterns, and code quality. Produces a consolidated report with actionable findings and spec traceability. Use after agent-implementation-builder completes.
disable-model-invocation: true
argument-hint: "[spec-folder-path]"
---

> **Invoke with:** `/agent-implementation-verifier` | **Keywords:** verify agent, check agent implementation, validate agent build, agent post-implementation review

Spawns a team of verification agents that evaluate a completed agent implementation against its spec. Each agent investigates a different dimension in parallel using `codebase-researcher` sub-agents. Produces a consolidated verification report with spec traceability that feeds the feedback flywheel.

**Input:** Path to a spec folder (`{workforce-root}/specs/YYYY-MM-DD-feature-name/`)
**Output:** `{spec-folder}/feedback/verification-NNN.md` -- actionable report with PASS/WARN/FAIL per criterion

## When to Use This Skill

Use this skill when:
- `agent-implementation-builder` has completed (or mostly completed) an agent implementation
- You want to verify the agent implementation matches the spec before human review
- You need an actionable report of what's missing or incorrect to feed back for fixes

**Skip this skill when:**
- Verifying a general (non-agent) implementation (use `general-implementation-verifier` instead)
- The spec hasn't been implemented yet (use `agent-implementation-builder` first)
- You only need to review the spec itself (use `review-agent-spec` instead)

## Reference Files

| Topic | Reference File | When to Load |
|-------|---------------|--------------|
| Verification dimensions | [verification-dimensions.md](references/verification-dimensions.md) | When generating teammate prompts -- defines what each agent checks |
| DSPy framework checks | [framework-checks-dspy.md](references/framework-checks-dspy.md) | When framework is DSPy -- load for framework-compliance-verifier agent only |
| LangGraph framework checks | [framework-checks-langgraph.md](references/framework-checks-langgraph.md) | When framework is LangGraph -- load for framework-compliance-verifier agent only |
| Report format | [report-format.md](references/report-format.md) | When consolidating results into the final report |
| Team orchestration | [team-orchestration.md](references/team-orchestration.md) | When setting up the team and spawning agents |

**Templates:**

| Template | Purpose |
|----------|---------|
| [verification-report.md](templates/verification-report.md) | Output report structure |
| [verifier-teammate.md](templates/verifier-teammate.md) | Teammate prompt template for each verification agent |

## Key Principles

1. **Read-only investigation** -- Verification agents do NOT modify code. They read, analyze, and report.
2. **Spec folder is the source of truth** -- `manifest.yaml` + `agent-config.yaml` + agent spec files define what must exist.
3. **Framework-aware verification** -- Checks bifurcate based on DSPy vs LangGraph. Load the correct framework reference file.
4. **Actionable findings only** -- Each WARN/FAIL must include what's wrong, where, and what needs to change.
5. **Parallel investigation** -- All 4 agents work simultaneously. No dependencies between them.
6. **Codebase-researcher for depth** -- Agents delegate deep code investigation to `codebase-researcher` sub-agents to manage context.
7. **Gate before action** -- Present the report. Do NOT auto-fix.
8. **Feedback flywheel** -- Classify each requirement outcome (CORRECT/INCORRECT/AMBIGUOUS/MISSING) so review skills detect recurring spec patterns.

## Workflow

### Phase 0: Locate Artifacts

The skill expects a spec folder path. Agent specs use a folder structure (not a single file).

```
{workforce-root}/specs/YYYY-MM-DD-feature-name/
├── spec/                    ← agent spec folder
│   ├── manifest.yaml        ← entry point, execution plan
│   ├── overview.md          ← architecture, decisions
│   ├── {team}/
│   │   ├── team.md          ← team orchestration spec
│   │   ├── agent-config.yaml ← agent types, frameworks, models
│   │   └── agents/
│   │       └── {agent}.md   ← per-agent spec
├── progress.md              ← what was actually built
└── feedback/
    └── verification-NNN.md  ← output goes here
```

1. Receive the spec folder path (from `$ARGUMENTS` or from the invoking agent)
2. Locate the manifest: `{spec-folder}/spec/manifest.yaml`
3. Locate the progress file: `{spec-folder}/progress.md`
4. Read `manifest.yaml` to understand the system hierarchy, file list, and execution plan
5. Read `agent-config.yaml` to determine the framework (DSPy or LangGraph)
6. Read the progress file to understand what was actually built
7. Determine the next verification number: count existing files in `{spec-folder}/feedback/verification-*.md`
8. If manifest or progress file is missing, stop and report the error

### Phase 1: Spawn Verification Team

Read [team-orchestration.md](references/team-orchestration.md) for the full setup procedure.

**Team composition (4 agents):**

| Agent | Dimension | Summary |
|-------|-----------|---------|
| `spec-compliance-verifier` | Spec Compliance | Agent types, model configs, prompt configs, I/O signatures match spec |
| `completeness-verifier` | Completeness | All framework-specific files exist, all phases produced outputs |
| `framework-compliance-verifier` | Framework Compliance | DSPy or LangGraph patterns, anti-patterns, team orchestration, data flow |
| `code-quality-verifier` | Code Quality | Correctness, security, performance, maintainability, error handling |

**Setup sequence:**
1. Load the `teammate-spawn` skill: `Skill tool -> skill: "teammate-spawn"`
2. Read [verification-dimensions.md](references/verification-dimensions.md) to build each agent's task list
3. Determine framework from `agent-config.yaml` and include the correct framework checks reference:
   - DSPy: include content from [framework-checks-dspy.md](references/framework-checks-dspy.md) in the framework-compliance-verifier's prompt
   - LangGraph: include content from [framework-checks-langgraph.md](references/framework-checks-langgraph.md)
4. Generate teammate prompt files using [verifier-teammate.md](templates/verifier-teammate.md)
5. Create team, create tasks, spawn all 4 agents in parallel

### Phase 2: Collect Results

1. Monitor all 4 agents until complete
2. Each agent reports structured findings back via SendMessage
3. Collect all findings

### Phase 3: Consolidate Report

1. Read [report-format.md](references/report-format.md) for the consolidation rules
2. Read [verification-report.md](templates/verification-report.md) for the output template
3. Merge findings from all 4 agents into a single report
4. **Build the Spec Traceability Matrix** -- classify each requirement as CORRECT/INCORRECT/AMBIGUOUS/MISSING
5. Apply severity rules: any FAIL in any dimension = overall verdict NEEDS FIXES
6. Create `{spec-folder}/feedback/` directory if it doesn't exist
7. Write report to `{spec-folder}/feedback/verification-NNN.md` (incrementing number)
8. Present summary to the invoking agent or user

### Future: Test Verification (Not Yet Implemented)

A 5th agent (`test-verifier`) will be added when the testing infrastructure is in place.

## Quick Reference

**Invoke:**
```
/agent-implementation-verifier {spec-folder-path}
```

**Spec folder structure:**
```
specs/YYYY-MM-DD-feature-name/
├── spec/                 ← reads from (manifest.yaml, agent-config.yaml, agent specs)
├── progress.md           ← reads from
└── feedback/
    └── verification-NNN.md  ← writes to
```

**Verdict values:** `PASS` (all checks pass) | `NEEDS FIXES` (any FAIL exists) | `WARNINGS ONLY` (no FAILs, some WARNs)
