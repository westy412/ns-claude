---
name: bug-hunter
description: Adversarial 3-agent bug finding pipeline using team mode. Spawns Hunter, Skeptic, and Referee teammates sequentially with file-based prompts via teammate-spawn pattern. Exploits sycophancy through opposing scoring incentives. Three modes - Quick, Standard, Deep Scan. Use for bug audits, code reviews, or pre-release checks.
disable-model-invocation: true
argument-hint: "[target-path]"
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, Agent, AskUserQuestion, TeamCreate, TeamDelete, TaskCreate, TaskUpdate, TaskGet, TaskList, TaskOutput, SendMessage
---

> **Invoke with:** `/bug-hunter` or `/bug-hunter src/auth/` | **Keywords:** find bugs, bug audit, adversarial review, code review, bug hunt

Three-agent adversarial pipeline for high-fidelity bug detection. Pre-analyzes the repo, suggests a scan mode, then runs Hunter/Skeptic/Referee teammates sequentially with file-based prompts.

**Input:** Target scope (or let pre-analysis suggest)
**Output:** Verified bug report at `bug-reports/{date}-{target}.md`

## When to Use

Use this skill when:
- Running a bug audit before a release
- Code reviewing a module or feature area
- Investigating suspected issues across a codebase section
- Doing a full-repo health check

**Skip this skill when:**
- Quick one-off code review (use `code-reviewer` agent directly)
- Reviewing a specific PR (use `code-reviewer` agent)
- Investigating a single known production error (use `prod-error` skill)

## How It Works

```
Hunter Teammate       Skeptic Teammate       Referee Teammate
(maximize finds)  ->  (disprove finds)   ->  (final verdict)
+1/+5/+10 per bug    +score for disprove    +1 correct / -1 wrong
false positives OK    -2x for wrong dismiss  "ground truth" framing
```

## Scan Modes

| Mode | When | Scope | Pipelines |
|------|------|-------|-----------|
| **Quick** | Targeted check on a known area | Single dir/file, ~5-15 files | 1 pipeline |
| **Standard** | Broader audit of a section | Up to ~30 files | 1 pipeline |
| **Deep Scan** | Full repo audit | Entire repo, auto-partitioned | 1 pipeline per partition |

## Reference Files

| Topic | Reference File | When to Load |
|-------|---------------|--------------|
| Agent prompts | [agent-prompts.md](references/agent-prompts.md) | When reviewing or customizing the adversarial prompts |
| Deep Scan execution | [deep-scan.md](references/deep-scan.md) | Only if Deep Scan mode selected |

## Teammate Prompt Templates

Templates are self-contained — each includes the full adversarial prompt, role, tasks, validation, and workflow. Fill `{{placeholders}}` and write to `teammate-prompts/bug-hunt/`.

| Template | For | Placeholders |
|----------|-----|-------------|
| [hunter-teammate.md](templates/hunter-teammate.md) | Hunter agent | `{{target-files}}`, `{{code-summary}}`, `{{concern-area}}`, `{{report-path}}` |
| [skeptic-teammate.md](templates/skeptic-teammate.md) | Skeptic agent | `{{hunter-report-path}}`, `{{report-path}}` |
| [referee-teammate.md](templates/referee-teammate.md) | Referee agent | `{{hunter-report-path}}`, `{{skeptic-report-path}}`, `{{report-path}}` |

## Key Principles

1. **Fresh context per agent** — Each teammate spawns with no shared context. Prevents bias carryover.
2. **File-based prompts + handoff** — Prompts written to files. Reports written to files. Clean separation.
3. **Sequential pipeline** — Hunter → Skeptic → Referee, one at a time.
4. **Exploit sycophancy** — Each agent's scoring incentive biases them differently. Tension produces truth.
5. **Pre-analyze before committing** — Scan the repo first, suggest the right mode. Don't blindly start.
6. **Teammates verify against code** — Unlike manual copy-paste, teammates READ the actual source.

---

## Phase 1: Pre-Analysis

**If `$ARGUMENTS` is a specific path** (e.g., `src/auth/`): Skip pre-analysis. Count the files — if <=15 suggest Quick, if <=30 suggest Standard. Present suggestion, let user confirm or change.

**Otherwise, scan the repo:**

```bash
# Count source files by directory (top 2 levels)
find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.go" -o -name "*.rs" -o -name "*.java" -o -name "*.rb" \) \
  -not -path "*/node_modules/*" -not -path "*/.venv/*" -not -path "*/dist/*" -not -path "*/__pycache__/*" -not -path "*/.git/*" \
  | head -200
```

```bash
# Get directory structure overview
find . -type d -maxdepth 3 -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/.venv/*" | head -50
```

**Build the pre-analysis summary:**

Identify logical modules by grouping files by top-level directory. Note:
- Module name and path
- File count per module
- Brief purpose (infer from directory/file names)
- Estimated complexity (file count + naming patterns)

**Present to user:**

```
## Pre-Analysis: {repo-name}

Source files: {total} across {module_count} modules
Languages: {breakdown}

| # | Module | Path | Files | Purpose |
|---|--------|------|-------|---------|
| 1 | Auth | src/auth/ | 12 | Authentication, JWT, sessions |
| 2 | API | src/api/ | 18 | REST endpoints, validation |
| 3 | Database | src/db/ | 9 | Models, queries |
| ... | | | | |

**Suggested mode: {mode}**
- Quick — pick a single module to audit
- Standard — audit up to 30 files across selected modules
- Deep Scan — full repo audit ({N} partitions, pipeline per partition)

Which mode would you like? (or specify a target path)
```

**Mode selection rules:**
- Total files <=15 → suggest Quick
- Total files 16-30 → suggest Standard
- Total files >30 → suggest Deep Scan
- User can always override

---

## Phase 2: Execute Based on Mode

### Quick / Standard Mode

Same execution path, just different scope. Quick targets fewer files.

**Step 1: Generate file list**

Based on user's chosen scope. For Standard, if user picks multiple modules, combine their files (cap at ~30).

Read target files and build a brief code summary (paths, key functions, complexity notes).

**Step 2: Setup**

```bash
mkdir -p bug-reports teammate-prompts/bug-hunt
```

```
TeamCreate: name: bug-hunt
TaskCreate: "Hunter: Find all bugs in target scope" (team: bug-hunt)
TaskCreate: "Skeptic: Challenge Hunter's bug reports" (team: bug-hunt)
TaskCreate: "Referee: Final verdict on disputed bugs" (team: bug-hunt)
```

**Step 3: Spawn Hunter**

Read [hunter-teammate.md](templates/hunter-teammate.md). Fill placeholders:
- `{{target-files}}` — file list
- `{{code-summary}}` — code summary
- `{{concern-area}}` — focus area or "general audit"
- `{{report-path}}` — `bug-reports/.hunter-report.md`

Write to `teammate-prompts/bug-hunt/hunter.md`. Spawn in foreground:

```
Agent tool:
  subagent_type: general-purpose
  team_name: bug-hunt
  name: hunter
  description: "Hunt for all bugs"
  prompt: |
    You are teammate "hunter" on team "bug-hunt".
    Read your full instructions at: teammate-prompts/bug-hunt/hunter.md
    Follow all steps. Write your report to the path in your instructions.
```

Verify report exists. Update task to complete.

**Step 4: Spawn Skeptic**

Read [skeptic-teammate.md](templates/skeptic-teammate.md). Fill:
- `{{hunter-report-path}}` — `bug-reports/.hunter-report.md`
- `{{report-path}}` — `bug-reports/.skeptic-report.md`

Write to `teammate-prompts/bug-hunt/skeptic.md`. Spawn in foreground. Verify. Update task.

**Step 5: Spawn Referee**

Read [referee-teammate.md](templates/referee-teammate.md). Fill:
- `{{hunter-report-path}}` — `bug-reports/.hunter-report.md`
- `{{skeptic-report-path}}` — `bug-reports/.skeptic-report.md`
- `{{report-path}}` — `bug-reports/.referee-report.md`

Write to `teammate-prompts/bug-hunt/referee.md`. Spawn in foreground. Verify. Update task.

**Step 6: Compile Final Report**

Read ALL three intermediate reports. Aggregate the full bug details into a single comprehensive report at `bug-reports/DD-MM-YYYY-{target-slug}.md`:

```markdown
# Bug Report: {target}

| Field | Value |
|-------|-------|
| **Date** | DD-MM-YYYY |
| **Mode** | Quick / Standard |
| **Target** | {scope} |
| **Files Analyzed** | {count} |
| **Bugs Reported (Hunter)** | {count} |
| **Bugs Disproved (Skeptic)** | {count} |
| **Verified Bugs (Referee)** | {count} |

---

## Verified Bugs

[For each verified bug, include the FULL details aggregated from all three agents:]

### [BUG-{id}] {title}
- **Location:** `{file}:{line}`
- **Severity:** Critical / Medium / Low
- **Confidence:** High / Medium / Low
- **Code:**
  ```
  {the problematic code snippet from Hunter's report}
  ```
- **Description:** {Hunter's description of the bug}
- **Impact:** {what could go wrong}
- **Skeptic's Analysis:** {what the Skeptic found when checking — accepted or tried to disprove}
- **Referee's Verdict:** {the Referee's final reasoning}

[Order by severity: Critical first, then Medium, then Low]

---

## Dismissed Reports

[For each bug the Referee dismissed:]

| # | Original Claim | Skeptic's Counter | Referee's Ruling |
|---|---------------|-------------------|------------------|
| 1 | {Hunter's claim} | {Skeptic's disproof} | {why it's not a bug} |

---

## Pipeline Summary
- **Hunter:** {score} points, {count} bugs reported
- **Skeptic:** {count} disproved, {count} accepted
- **Referee:** {count} confirmed as real, {count} dismissed
```

**Important:** The final report must be self-contained — a reader should understand each bug without needing the intermediate files.

**Step 7: Present and Confirm**

Present the final report location and a summary of verified bugs to the user.

Ask: **"Are you happy with this report? If so, I'll clean up the intermediate files and keep only the final report."**

- **Yes / happy** — Clean up and proceed to optional fix:
  ```bash
  rm -rf teammate-prompts/bug-hunt/
  rm -f bug-reports/.hunter-report.md bug-reports/.skeptic-report.md bug-reports/.referee-report.md
  ```
  ```
  TeamDelete: bug-hunt
  ```
- **No / adjustments needed** — Discuss what's wrong. The intermediate files are still available for re-examination. Re-run specific agents if needed.
- **Want to review intermediates** — Point them to `bug-reports/.hunter-report.md`, `.skeptic-report.md`, `.referee-report.md` for the raw agent outputs.

### Deep Scan Mode

Read [deep-scan.md](references/deep-scan.md) and follow its procedure.

Deep Scan partitions the repo into logical modules, runs a full Hunter/Skeptic/Referee pipeline per partition, then consolidates all results into a single final report. Same confirmation gate applies — intermediate files are only deleted after the user approves.

---

## When to Ask for Feedback

Always ask before:
- Committing to a scan mode (after pre-analysis)
- Proceeding with Deep Scan partitions (after presenting partition plan)
- Deleting intermediate files (after final report is compiled)

Report progress after:
- Each agent completes (brief status)
- Each partition completes (in Deep Scan mode)

---

## Phase 3: Optional Fix

After the user confirms the report and intermediate files are cleaned up, ask:

**"Would you like me to fix any of these verified bugs?"**

- **Yes** — Work through bugs one at a time, highest severity first. Show fix before applying.
- **No** — Done. Report stands as documentation.
- **Specific bugs** — Fix only the requested ones.
