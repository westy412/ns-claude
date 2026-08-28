---
name: impact-analysis
description: Map the blast radius of a change. Takes a change the user describes, or the diff on a branch, and traces it outward through repo-local callers, runtime and data systems, and downstream consumers. Ranks each risk, then gives verification and rollback steps. Use when the user asks what a change breaks, asks for an impact analysis or a blast radius, or before a change reaches a production system.
allowed-tools: Read, Grep, Glob, Bash, Write, Agent, SendMessage, AskUserQuestion
argument-hint: "[ref | path | change description]"
---

> **Invoke with:** `/impact-analysis "rename the status column to state"` or `/impact-analysis feature/new-auth` | **Keywords:** impact analysis, blast radius, what breaks, downstream effects, change risk, regression risk, ripple effect

Map what a change can break. The skill takes a change you describe, or a diff on a branch, classifies each changed surface, traces the surface outward through three rings, and ranks every risk it finds.

**Input:** `$ARGUMENTS` — a description of a change, or a git ref, a branch, a PR, or a path.
**Output:** A ranked blast radius report in chat. The report also goes to a file when the change belongs to a spec folder.

## When to Use This Skill

Use this skill when:
- The user names a change and asks what it breaks. This is the main case.
- The user asks for an impact analysis or a blast radius.
- The user wants the risk map for a branch, a pull request, or a set of commits.
- An edit touches a production system: a schema, an endpoint, a queue, a secret, an auth rule, or a deploy config.
- A spec is ready to implement and the user wants the risk map first.
- A change is about to reach production, as a release or as a hotfix.

**Skip this skill when:**
- The user hunts for bugs in code that nobody changed → use `bug-hunter`.
- The user investigates a live production error → use `prod-error`.
- The user wants a line-by-line quality review of a diff → use `/code-review`.

## Modes

The skill runs in one of two modes. Read the user request and pick the mode. Do not ask when the request is clear.

| Mode | Trigger | The change surface |
|------|---------|--------------------|
| **described** | The user names or describes a change in words. The change can be planned, in progress, or already made. | The change the user describes, plus the real files it touches |
| **diff** | The user points at a branch, a ref, a commit range, a pull request, or a path | The real diff of that target |

Both modes end in the same place: real code, read from disk. A described change is not a thought experiment. Find the files the change would touch, read them, and trace from there. When you cannot find the code the description names, ask one question and stop.

Bare invocation with no argument means "the work on this branch". Use diff mode against the base branch, and include the uncommitted work.

## Solo or Team

The three rings are independent searches. Run them in parallel when the change earns it.

| Route | When | Who does the tracing |
|-------|------|---------------------|
| **Solo** | The surface holds only internal code, and the change touches 10 files or fewer | You do steps 3 to 5 yourself |
| **Team** | Any of the conditions below is true | Three tracer sub-agents in parallel, then a verifier |

Take the team route when any one of these holds:
- The change touches a production surface: an endpoint, a schema, a data write path, an event payload, a secret, an auth rule, a deploy config, or a shared package.
- The change touches more than 10 files.
- The change spans more than one repository.
- The user asks for a team, a deep analysis, or a thorough analysis.

Decide the route at the end of step 2, not before. The surface types decide it, and you do not know them until you classify.

## Reference Files

| Topic | Reference File | When to Load |
|-------|---------------|--------------|
| The surface types and how each one propagates | [change-surface-taxonomy.md](references/change-surface-taxonomy.md) | Step 2, every run |
| Commands and search patterns for each ring | [tracing-playbook.md](references/tracing-playbook.md) | Steps 3 to 5, every run |
| Known failure patterns per surface | [breaking-change-catalogue.md](references/breaking-change-catalogue.md) | Step 6, every run |
| Risk matrix, confidence labels, rollback questions | [risk-scoring.md](references/risk-scoring.md) | Step 7, every run |

## Teammate Prompt Templates

Team route only. Each template is self-contained. Fill the `{{placeholders}}`, write the result to `{project}/teammate-prompts/impact-analysis/{agent-name}.md`, then spawn the agent against that file.

| Template | Agent | Placeholders |
|----------|-------|-------------|
| [ring1-teammate.md](templates/ring1-teammate.md) | Ring 1, repo-local | `{{change-surface}}`, `{{classified-elements}}`, `{{skill-path}}`, `{{project-path}}` |
| [ring2-teammate.md](templates/ring2-teammate.md) | Ring 2, runtime and data | `{{change-surface}}`, `{{classified-elements}}`, `{{skill-path}}`, `{{project-path}}` |
| [ring3-teammate.md](templates/ring3-teammate.md) | Ring 3, downstream | `{{change-surface}}`, `{{public-surface}}`, `{{known-consumers}}`, `{{skill-path}}`, `{{project-path}}` |
| [verifier-teammate.md](templates/verifier-teammate.md) | Verifier | `{{findings-path}}`, `{{change-surface}}`, `{{project-path}}` |

## Key Principles

1. **Read the code. Do not guess.** Every finding names a file and a line. A finding without evidence is an unknown, not a finding.
2. **Label the confidence.** Mark each finding `confirmed` when you read the consumer, or `suspected` when you infer it.
3. **Three rings, in order.** Never skip a ring in silence. An unchecked ring goes in the Unknowns section with the reason.
4. **Rank by risk, not by ring.** A downstream break outranks a local one when it costs more.
5. **State the deploy order.** Many failures come from the order of the migration and the deploy, not from the code.
6. **Analysis only.** This skill never edits source code. It writes teammate prompt files and, at most, one report file.
7. **Say what you could not check.** A missing check is a result. Silence about it is a defect.

## Procedure

### Step 1 — Establish the change surface

Pick the mode. Then collect the change.

**Described mode.** Restate the change in one sentence, so the user can correct you. Then locate the code:

```bash
rg -n '<THE THING THE USER NAMED>'      # the function, the table, the route, the field
fd '<FILENAME OR PATTERN>'
```

Read the files you find. List them back as the change surface. When the description covers work that does not exist yet, name the files the change must touch and say that the surface is planned, not written.

**Diff mode.** Resolve the target, then collect the diff:

```bash
BASE=$(git merge-base HEAD "$TARGET" 2>/dev/null || echo origin/main)
git diff --stat $BASE
git diff $BASE
git status --porcelain                   # include uncommitted and untracked work
```

A new file is a change. An untracked file is a change.

Report the size of the surface before you continue: the repo, the mode, the file count, and the line count.

### Step 2 — Classify each changed element

Load [change-surface-taxonomy.md](references/change-surface-taxonomy.md). Assign every changed element to a surface type. One element can hold two types. Record both.

The surface type sets the trace path and the severity floor. An internal helper stops at ring 1. A schema change reaches all three rings.

### Steps 3 to 5 — Trace the three rings

**Team route:** spawn the three tracers in parallel now. See "Team Route" below, then continue at step 6 with their merged findings. Do not trace a ring yourself that you gave to a tracer.

**Solo route:** do steps 3, 4, and 5 yourself, in order.

### Step 3 — Ring 1: repo-local

Load [tracing-playbook.md](references/tracing-playbook.md). Find every caller of every changed symbol. Cover imports, re-exports, dynamic references by string, types, tests, fixtures, and config keys.

Read each caller. Decide whether the change breaks it. Record the file and the line.

### Step 4 — Ring 2: runtime and data systems

Trace the change into the systems that run the code:
- The database: schema, migrations, indexes, constraints, row counts, and the deploy order.
- API contracts: routes, request shapes, response shapes, status codes, and error shapes.
- Events, queues, and webhooks: payload shape, topic names, retry behaviour, and idempotency.
- Scheduled jobs and background workers.
- Environment variables, secrets, and feature flags.
- Deploy config: the Dockerfile, the Cloud Run service, Terraform, and the CI pipeline.

### Step 5 — Ring 3: downstream consumers

Find the systems outside this repo that use the changed surface. The playbook holds the discovery commands. Sources, in order of cost:
1. Sibling repos in the same parent directory, for example `~/Programming/{org}/*`.
2. A code search across the GitHub organisation.
3. Published package consumers, for example the `@novosapien` packages.
4. Client apps, MCP servers, vault sync jobs, and external webhook callers.

Do not cache the consumer list. Discover it each run. When discovery fails, ask the user which systems consume this surface, then continue.

### Step 6 — Match the failure patterns

Load [breaking-change-catalogue.md](references/breaking-change-catalogue.md). Check every changed surface against the patterns for its type. The catalogue holds the failure each pattern causes and the check that proves it.

### Step 7 — Score, report, and route the output

Load [risk-scoring.md](references/risk-scoring.md). Score each finding, then write the report in the format below.

**Output routing:**

| Condition | Where the report goes |
|-----------|----------------------|
| The change belongs to a spec folder (`{repo}/specs/YYYY-MM-DD-*/`) | Write `{spec-folder}/impact-analysis.md`, then give a short chat summary |
| A hotfix, or any ad-hoc change with no spec folder | Chat only. Write no file. |

Detect the spec folder in this order: the folder the session already works in; a folder under `specs/` whose name matches the branch name; nothing. Never invent a spec folder. When you find none, keep the report transient.

## Team Route

Four sub-agents. Three trace in parallel. One verifies after them.

```
ring1-local ─┐
ring2-runtime ┼─ parallel ─→ merge ─→ verifier ─→ you score and report
ring3-downstream ─┘
```

1. **Write the prompts.** Fill the three tracer templates with the change surface from step 1 and the classified elements from step 2. Give each tracer the same change surface and a different ring. Write each file to `{project}/teammate-prompts/impact-analysis/{agent-name}.md`.
2. **Spawn all three together**, so they run at the same time. Give each one a name. See Execution.
3. **Merge.** Collect the three reports. Write the combined findings to `{project}/teammate-prompts/impact-analysis/findings.md`. Keep the Checked and Unknowns sections from each tracer. They prove the coverage.
4. **Verify.** When the merge holds any Critical or High finding, fill the verifier template and spawn one verifier against the findings file. Apply its verdicts: a dropped finding leaves the report, a downgraded finding changes level, an unverified finding stays and becomes an unknown.
5. **Own the result.** Read the findings before you accept them. A tracer that reports an empty ring with an empty Checked section did not do the work. Re-run that ring yourself.
6. **Clean up.** Delete the prompt directory when the report is out:
   ```bash
   rm -rf {project}/teammate-prompts/impact-analysis/
   rmdir {project}/teammate-prompts/ 2>/dev/null
   ```

Rules:
- Each tracer owns one ring. Never give two agents the same ring.
- Every tracer is read-only. No tracer edits a file, and no tracer writes to a live system.
- A tracer reports its own Unknowns. Carry every one of them into the report.
- Use the default model for every sub-agent.

## Execution

Spawn each sub-agent with the `Agent` tool. Always pass a `name`. Send the three tracer calls in one message so they run in parallel.

```
Agent:
  name: {agent-name}
  subagent_type: Explore
  description: {3-5 word label}
  prompt: |
    You are {agent-name}.
    Read your full instructions at:
      {project}/teammate-prompts/impact-analysis/{agent-name}.md
    Follow all steps in order.
```

Use `subagent_type: Explore` for the three tracers, because they are read-only searches. Use `general-purpose` for the verifier, because it reads code and returns a judgement. Do not pass `team_name`. Results arrive as task notifications.

## Report Format

```markdown
## Impact Analysis — {repo} / {branch}
{mode} mode · {n} files · {n} lines · {timestamp}

### Verdict
{GO | GO WITH CONDITIONS | STOP}
{One sentence that gives the reason.}

### Critical and High risks
| # | Risk | Surface | Evidence | Confidence |
|---|------|---------|----------|------------|
| 1 | {what breaks, and for whom} | {surface type} | `path:line` | confirmed |

### Blast radius
| Ring | System | Reached through | Risk |
|------|--------|-----------------|------|
| 1 | {file or module} | {the changed symbol} | Medium |
| 2 | {table, endpoint, or queue} | {the changed contract} | High |
| 3 | {repo or client} | {the changed export} | Low |

### Verify before you ship
1. {A command or a check, one per line.}

### Rollback
- Reversible: {yes | no | partly}
- Deploy order: {what must go first}
- To undo: {the steps}

### Unknowns
- {What you could not check, and the reason.}
```

Keep the chat summary to the verdict, the Critical and High rows, and the Unknowns. The file holds the full report.

## When to Ask for Feedback

Ask before:
- A run in described mode where you cannot find the code the description names. Ask once, then stop.
- Any query against a live system that costs money or time, for example a production database count.

Never ask for permission to read code. Read it.
