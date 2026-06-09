# Agent-Tools Lane (Phase 3)

> **Context:** Manifest rows that exercise an **agent tool or utility** — a deterministic
> function with a defined I/O contract (the tools-and-utilities spec emitted its Example I/O and
> Errors tables as the seed). Tools are the deterministic seams of an agent system: test them
> like functions, not like agents.

---

## Happy-path rows (Example I/O — `T#` rows)

For each row: **call the tool with the row's input, assert the output.**

1. Invoke the tool the way the system invokes it — import and call the tool function directly,
   or call it through the framework's tool-invocation harness if direct import isn't practical.
   Use the row's input verbatim (it is real, probed data — the spec grounded it).
2. Compare the return against the row's expected output:
   - **Structured returns (JSON):** assert the fields the seed specifies — present, correct
     type, correct value. Extra fields the seed doesn't mention are not a FAIL.
   - **Exact-value returns:** byte/value-exact match.
3. Verdict per row: PASS / FAIL / UNTESTED(reason).

## Error rows (Errors table — Error | Trigger | Expected Return)

Each error row is a real assertion: **trigger the failing condition, assert the error return.**

- Reproduce the Trigger (bad input, missing field, unauthorized call — whatever the row names).
- Assert the tool returns the **expected error shape** (the structured error the spec defines)
  — **never an unhandled crash**. An uncaught exception on an error row is a FAIL even if the
  exception text resembles the expected message: the contract is a returned error, not a crash.

## Live calls and external dependencies

- Tools that wrap real APIs: call the real API where credentials/sandbox allow — the seed's
  values came from probing it, so the comparison is meaningful. Non-deterministic fields in live
  responses (timestamps, IDs): assert presence and shape, not value.
- If a live call is not possible (no credentials, cost, rate limits): record the row
  **UNTESTED** with the reason and move on — do not stub the API and call it a pass. If that
  leaves a Requirement wholly untested, surface it (autonomy rule: escalate or Known-Risk).

## Recording

Per row: the exact call made, the actual return (trimmed), and the verdict. Failures carry both
expected and observed returns so Phase 4 can route them (tool bug vs spec's expected-return
wrong → spec-defect loopback).
