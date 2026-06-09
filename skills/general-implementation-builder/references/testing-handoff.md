# Testing Handoff (Layer 3 — on clean final review)

> **Context:** The big review is the build-side *static* gate; it does not run the artifact. Running
> it against its spec-derived tests is a separate live-validation stage owned by the typed-testing
> skill. This file is the seam from a clean build to that stage. Read it at the big review, after
> findings are resolved and before you emit the completion promise.

---

## When this fires

After the **big review** is clean (no open FAILs; open items logged as Known-Risks) — the build is
static-complete. Before declaring done, surface the test seed and hand off.

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
is the live gate. Record the outcome in `progress.md`. If typed testing cannot run right now (user
defers, environment unavailable), record that **live testing is owed** (with the surfaced seed) and
emit the completion promise — deferral is non-blocking; skipping silently is not.
