# Deep Scan Execution

> **When to read:** Only when the user selects Deep Scan mode.

Deep Scan partitions the entire repo into logical modules and runs a full Hunter→Skeptic→Referee pipeline for each partition. Each partition gets focused context, keeping each agent effective. Results are consolidated into a single final report.

---

## Why Partition

Agents perform best with focused context. A single Hunter trying to analyze 80+ files will:
- Miss bugs in later files as context fills up
- Produce shallow analysis across too many files
- Lose coherence in its reporting

Partitioning to ~15-20 files per chunk keeps each agent sharp and thorough.

---

## Step 1: Build Partitions

Using the module table from pre-analysis, create partitions:

**Rules:**
- Target ~15-20 source files per partition
- Group by logical module (directory structure is usually right)
- If a module has >25 files, split it (e.g., `api/routes` vs `api/middleware`)
- If a module has <5 files, merge with a related module
- Exclude test files, configs, lockfiles, generated code
- Name each partition clearly (e.g., `auth`, `api-routes`, `database`)

**Present partitions to user for approval:**

```
## Deep Scan Partitions

| # | Partition | Path(s) | Files | Notes |
|---|-----------|---------|-------|-------|
| 1 | auth | src/auth/ | 12 | JWT, sessions, middleware |
| 2 | api-routes | src/api/routes/ | 16 | REST endpoints |
| 3 | api-middleware | src/api/middleware/ | 8 | Validation, error handling |
| 4 | database | src/db/ | 14 | Models, queries, migrations |
| 5 | services | src/services/ | 15 | Business logic |
| 6 | workers | src/workers/ | 6 | Background jobs |

Total: 6 partitions, 71 files

Shall I proceed, or adjust any partitions?
```

Wait for user confirmation. They may want to:
- Skip certain partitions
- Merge or split partitions
- Reorder priority (run critical modules first)

---

## Step 2: Setup

```bash
mkdir -p bug-reports/deep-scan teammate-prompts/bug-hunt
```

```
TeamCreate: name: bug-hunt
```

Create one set of tasks per partition:
```
For each partition:
  TaskCreate: "Hunter [{partition-name}]: Find bugs" (team: bug-hunt)
  TaskCreate: "Skeptic [{partition-name}]: Challenge bugs" (team: bug-hunt)
  TaskCreate: "Referee [{partition-name}]: Final verdicts" (team: bug-hunt)
```

Read [agent-prompts.md](../references/agent-prompts.md) if you need to review or customize the adversarial prompts. Otherwise, the teammate templates are self-contained.

---

## Step 3: Execute Pipeline Per Partition

For each partition, **sequentially** run the full pipeline. One partition at a time.

### For partition N:

**Read target files** for this partition. Build code summary.

**Hunter:**
- Read [hunter-teammate.md](../templates/hunter-teammate.md)
- Fill `{{target-files}}` with this partition's files, `{{report-path}}` with `bug-reports/deep-scan/.hunter-{partition-name}.md`
- Write prompt to `teammate-prompts/bug-hunt/hunter-{partition-name}.md`
- Spawn:
```
Agent tool:
  subagent_type: general-purpose
  team_name: bug-hunt
  name: hunter-{partition-name}
  description: "Hunt bugs in {partition-name}"
  prompt: |
    You are teammate "hunter-{partition-name}" on team "bug-hunt".
    Read your full instructions at: teammate-prompts/bug-hunt/hunter-{partition-name}.md
    Follow all steps. Write your report to the path in your instructions.
```
- Verify report. Update task.

**Skeptic:**
- Read [skeptic-teammate.md](../templates/skeptic-teammate.md)
- Fill `{{hunter-report-path}}` with `bug-reports/deep-scan/.hunter-{partition-name}.md`
- Fill `{{report-path}}` with `bug-reports/deep-scan/.skeptic-{partition-name}.md`
- Write prompt to `teammate-prompts/bug-hunt/skeptic-{partition-name}.md`
- Spawn. Verify. Update task.

**Referee:**
- Read [referee-teammate.md](../templates/referee-teammate.md)
- Fill both report paths for this partition
- Fill `{{report-path}}` with `bug-reports/deep-scan/.referee-{partition-name}.md`
- Write prompt to `teammate-prompts/bug-hunt/referee-{partition-name}.md`
- Spawn. Verify. Update task.

**After each partition completes:** briefly report progress to the user:
```
Partition 3/6 (database) complete: 4 bugs found, 1 disproved, 3 verified.
```

### Repeat for all partitions.

---

## Step 4: Consolidate Final Report

Read ALL intermediate reports from `bug-reports/deep-scan/` — hunters, skeptics, and referees for every partition. Aggregate the full bug details into a single self-contained report at:
```
bug-reports/DD-MM-YYYY-deep-scan.md
```

**The final report must be self-contained.** A reader should understand every bug without needing the intermediate files.

**Structure:**

```markdown
# Deep Scan Bug Report: {repo-name}

| Field | Value |
|-------|-------|
| **Date** | DD-MM-YYYY |
| **Mode** | Deep Scan |
| **Partitions** | {count} |
| **Total Files Analyzed** | {count} |
| **Total Bugs Reported** | {count} |
| **Total Bugs Disproved** | {count} |
| **Total Verified Bugs** | {count} |

---

## Summary by Partition

| Partition | Files | Reported | Disproved | Verified | Critical | Medium | Low |
|-----------|-------|----------|-----------|----------|----------|--------|-----|
| auth | 12 | 8 | 3 | 5 | 1 | 3 | 1 |
| api-routes | 16 | 12 | 7 | 5 | 0 | 4 | 1 |
| ... | | | | | | | |
| **Total** | **71** | **35** | **18** | **17** | **3** | **10** | **4** |

---

## All Verified Bugs (Ordered by Severity)

### Critical

#### [BUG-C001] {title} — [{partition}]
- **Location:** `{file}:{line}`
- **Confidence:** High / Medium / Low
- **Code:**
  ```
  {problematic code snippet from Hunter's report}
  ```
- **Description:** {Hunter's description of the bug}
- **Impact:** {what could happen}
- **Skeptic's Analysis:** {what the Skeptic found when checking}
- **Referee's Verdict:** {the Referee's final reasoning}

### Medium
[Same format — full details for every bug]

### Low
[Same format]

---

## Dismissed Reports

| # | Partition | Original Claim | Skeptic's Counter | Referee's Ruling |
|---|-----------|---------------|-------------------|------------------|
| 1 | auth | {Hunter's claim} | {Skeptic's disproof} | {why not a bug} |

---

## Pipeline Summary by Partition

| Partition | Hunter Score | Skeptic Disproved | Skeptic Accepted | Referee Confirmed | Referee Dismissed |
|-----------|-------------|-------------------|------------------|-------------------|-------------------|
| auth | 42 | 3 | 5 | 5 | 0 |
| ... | | | | | |
```

---

## Step 5: Present and Confirm

Present the consolidated report location and overall summary to the user.

Ask: **"Are you happy with this report? If so, I'll clean up the intermediate files and keep only the final report."**

- **Yes / happy** — Proceed to cleanup:
  ```bash
  rm -rf teammate-prompts/bug-hunt/
  rm -rf bug-reports/deep-scan/
  ```
  ```
  TeamDelete: bug-hunt
  ```
  Only the final report at `bug-reports/DD-MM-YYYY-deep-scan.md` remains.

- **No / adjustments needed** — Intermediate files in `bug-reports/deep-scan/` are still available. Discuss what's wrong and re-run specific partitions or agents if needed.

- **Want to review intermediates** — Point them to `bug-reports/deep-scan/` for the raw per-partition agent outputs.

---

## Optimization Notes

**Partition ordering:** If the user indicates priority areas, run those first. Early results may inform whether to continue with remaining partitions.

**Early termination:** If the first 2-3 partitions find zero bugs, ask the user if they want to continue with remaining partitions or stop early.

**Partition parallelism (advanced):** The current design runs partitions sequentially. If team capacity allows, independent partitions COULD run in parallel (each partition's pipeline is independent). However, this uses more resources and is harder to monitor. Only parallelize if the user explicitly requests speed over control.
