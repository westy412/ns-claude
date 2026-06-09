# Code Lane (Phase 3)

> **Context:** Manifest rows that exercise **code** — a feature, app, service, endpoint, CLI,
> UI, or library. The method is direct: run the real thing with the seed's input, observe, and
> compare against the seed's expected output. No mocks, no dry-runs — a mocked pass proves
> nothing about feature-correctness.

---

## Sub-routes

Pick per row by what the code is:

| Artifact | How to run it |
|----------|---------------|
| **CLI / script** | Execute with the row's input (args/stdin/files); capture stdout/stderr/exit code; assert against expected |
| **Service / endpoint** | Launch the real server (dev mode is fine — real code path), hit the endpoint with the row's request, assert status + response body |
| **UI / browser flow** | Launch the app and drive the row's golden path; assert the visible outcome the seed names |
| **Library / module** | Import and call the function with the row's input in a minimal runner; assert the return value |

**Execution surface:** the built-in `run` and `verify` skills are the live-validation surface —
invoke `run` (Skill tool) to launch and drive the app, and `verify` to confirm a change
end-to-end. Fall back to direct Bash execution for simple CLI/library rows where launching the
full app is overkill.

## Acceptance-criteria commands

Run any literal commands the spec's Acceptance Criteria carry (`test`, `lint`, build commands)
**verbatim** — do not substitute a different runner or flags. Each command is one manifest row:
exit 0 (or the stated criterion) = PASS; capture failing output into the report.

## Worked examples vs edge cases

- **Worked examples (WE rows):** the happy-path contract. Input in → exact expected output.
  Compare structurally where the seed gives structured output (JSON fields present + correct),
  byte-exact where it gives literal output.
- **Edge cases (EC rows):** boundaries and failure modes. Run the malformed/empty/limit input
  and assert the **expected handling** — a graceful error, a validation message, a refusal.
  An unhandled crash on an EC row is a FAIL even if the message looks "reasonable".

## Environment honesty

- Run in the project's real environment (its declared setup/install steps). If the environment
  cannot be brought up (missing credentials, external service, cost), record the affected rows
  **UNTESTED** with the reason — never simulate the result.
- Side-effectful rows (writes, sends, deploys): prefer the project's sandbox/staging path if the
  spec names one; if only production exists, **escalate before executing** (autonomy rule —
  outward-facing actions need the user).

## Recording

For each row: record the command/request actually run, observed output (trimmed to the relevant
part), and verdict PASS / FAIL / UNTESTED(reason). Observed-vs-expected goes in the report —
findings route in Phase 4, not mid-lane.
