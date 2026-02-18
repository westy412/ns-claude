# Phase 5: Review & Finalize

> **When to read:** After Phase 3 (Construction) is complete, or after Phase 4 (Handoff) if hybrid work was involved. This is the final quality gate before the spec is saved.

---

## Step 1: Read Back the Full Spec

Present the complete spec to the user for review. Walk through each section:

> "Here's the complete spec. Let me walk through it section by section..."

Let the user read and respond. Be ready to make changes.

---

## Step 2: Validation Gates

**These 4 checks are BLOCKING — do not finalize until all pass.**

### Check 1: Stream Ownership

Verify no two work streams write to the same file or directory.

For each file/directory listed in the Work Streams table:
1. List which stream owns it
2. Flag any file that appears in multiple streams
3. If conflict found, resolve by either:
   - Moving the file to one stream
   - Splitting the file into stream-specific files
   - Redefining stream boundaries

| File/Directory | Stream | Conflict? |
|---------------|--------|-----------|
| src/models/ | data | |
| src/api/ | api | |
| src/middleware/ | api | |

**Why:** Two agents editing the same file in parallel causes merge conflicts.

### Check 2: Chunk Sizing

Review each chunk for appropriate scope:

**Too granular (overhead):**
- Single-file chunks that take < 1 hour
- More than 10 chunks for a medium feature
- Individual function-level chunks

**Too large (can't complete):**
- Chunks that span multiple unrelated concerns
- Chunks with > 10 sub-tasks
- Chunks that would take > 8 hours of focused work

**Right-sized:**
- 2-8 hours of focused work per chunk
- 5-8 chunks typical for a medium feature
- Each chunk has a clear, independently verifiable outcome

### Check 3: Acceptance Criteria Verifiability

For each acceptance criterion, ask: "Can this be objectively verified?"

| Criterion | Verifiable? | Fix |
|-----------|-------------|-----|
| "User can log in" | Yes — testable | Keep |
| "System is fast" | No — subjective | Change to: "API response time < 200ms for /auth/login" |
| "Code is clean" | No — subjective | Change to: "Linting clean: `ruff check src/`" |
| "All tests pass: `pytest tests/`" | Yes — command | Keep |

**Good criteria are:**
- Binary (pass/fail, not "kind of")
- Testable (with a command, API call, or clear observation)
- Specific (not vague qualitative statements)

### Check 4: Skill Assignment

Verify every chunk in the execution plan has appropriate skills listed.

For each chunk:
1. Check if `Skills:` field exists
2. If the chunk involves technology-specific work, ensure relevant skills are listed
3. If no skills apply (pure documentation, config, etc.), `Skills: —` is acceptable

| Chunk | Skills Listed | Appropriate? |
|-------|--------------|--------------|
| Database models | backend-api | Yes |
| Auth endpoints | backend-api | Yes |
| Frontend component | — | No — needs frontend skill |

---

## Step 3: User Confirmation

After all validation gates pass:

> "Does this spec accurately capture what we're building? Anything to add or change?"

Make any final adjustments the user requests.

---

## Step 4: Confirm Location and Save

> "I'll save this to `/specs/[name].md`. Good?"

Save the spec file. Update progress.md to mark all sections as complete.

---

## Step 5: Summarize Next Steps

Provide clear guidance on what happens next:

> "Spec saved. Next steps:
> 1. Run the `general-implementation-builder` skill with this spec
> 2. [If hybrid: Run `agent-spec-builder` for the agent component]
> 3. [If Linear integration: Create Linear issues from Execution Plan]"

---

## Phase Completion Checklist

- [ ] Full spec read back to user
- [ ] Stream ownership validated (no conflicts)
- [ ] Chunk sizing validated (not too small, not too large)
- [ ] Acceptance criteria are all verifiable
- [ ] All chunks have appropriate skills assigned
- [ ] User confirmed the spec
- [ ] Spec saved to `/specs/[name].md`
- [ ] Next steps communicated
