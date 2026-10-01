# Testing Handoff (Layer 3 — on clean final review)

> **Context:** The big review and the implementation verifier are the build's *static* gates;
> neither runs the artifact. Running it against its spec-derived tests is a separate live-validation
> stage owned by the typed-testing skill. This file is the seam from a statically clean build to
> that stage — step 3 of the builder's Completion sequence. Read it after the verifier's report has
> no open FAIL, before the acceptance-criteria table.

---

## When this fires

After the **verifier's** report has no open FAIL (fixes applied; open items logged as Known-Risks) —
the build is static-complete. Surface the test seed and hand off.

## Surface the seed tests

The spec already carries the test seed (the spec-builders and tools-and-utilities emit it). Collect
it for the handoff — don't re-derive it:

- **Worked examples** — the spec's Test Sources / per-agent Examples (happy-path input → expected output).
- **Edge cases** — the spec's Edge Cases tables (boundaries, empty/malformed inputs, failure modes).
- **Tool example-I/O + error cases** — each tool's Example I/O table + error test cases.
- **Acceptance criteria** — the spec's verifiable criteria (incl. any test/lint commands).
- **Review test-seeds** — any `reviews/review-NNN-testseed.md` the spec review emitted.

If the spec is missing a seed a requirement needs (no example/edge case to lift), that is a
spec-quality gap — run the autonomy rule (`autonomy-and-escalation.md`): resolve from intent, else
escalate one question / log a Known-Risk. Do not invent tests the spec doesn't ground.

## Hand off to typed testing

Hand off the spec folder to the typed-testing skill: `-> typed-testing {spec-folder-path}`. It routes
by artifact type (code → run/endpoints/browser; agent tools → input→assert-output; agent reasoning →
evals / LLM-judge) and runs the seed as live tests.

**Wired — invoke it now.** Invoke the typed-testing skill for the spec folder with the surfaced
seed. It lifts the seed into a test manifest, routes each row by artifact type, runs the artifact
live, and writes `feedback/testing-NNN.md` with a machine-readable `testing_verdict` — that verdict
is the live gate. Record the outcome in `progress.md`.

## Evidence that counts

- **Exercise each shipped artifact the way its consumer does.** A package entry point, a stylesheet,
  an endpoint, or a UI is imported, compiled, rendered, or called through the real consumer path. A
  build, a copy, or a text check is not evidence.
- **A CI gate that cannot run exits non-zero, or you remove it.** A green skip is never a PASS.
- **A "deployed" criterion closes on one end-to-end worked example on the deployed environment.** A
  health probe alone does not close it.

## Deferral

Typed testing is never one option among alternatives: it runs, or it is deferred.

- Run every row that can run now. Defer only the rows that need an environment you do not have.
- If typed testing cannot run right now (user defers, environment unavailable), record that **live
  testing is owed**, with the surfaced seed and the rows it covers.
- A human checklist, a live walkthrough, or an in-spec live phase is the **deferral form** of typed
  testing, never a replacement for it. Record it as deferred testing with an owner. Its rows close
  only on recorded PASS evidence.
- Deferral does not block the session. It does block the completion promise: each owed row stays
  open in the acceptance-criteria table, and the run ends `builder-complete`, not `complete`.
  Skipping silently is never allowed.
