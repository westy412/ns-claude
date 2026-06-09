# Agent-Reasoning Lane (Phase 3)

> **Context:** Manifest rows that exercise **LLM behaviour** — prompts, routing, generation,
> selection, multi-step reasoning. Output is non-deterministic, so the method shifts: run the
> real agent, then **assert properties, not bytes** — an eval judged against the seed's expected
> output, plus a live type-conformance check per agent.

---

## Running the rows

- **Worked examples (per-agent `## Examples`):** run the real agent with the example's input —
  through the system's actual entry point (graph invocation, agent runner), not a re-prompt of
  the raw model. Capture the full output.
- **Edge cases (per-agent `### Edge Cases` rows):** run the Case's condition and check the
  observed handling against "How to Handle". Edge-case rows are usually judgeable directly
  (did it refuse / default / error as specified?) without a full eval.

One run per row by default. If a verdict is borderline or the row looks flaky, run it 2–3 times
and take the majority — note the flakiness in the report (it is telemetry).

## LLM-judge eval

Judgement of generated output must come from a **fresh context** — the context that ran the agent
is anchored on what it produced. Spawn a judge sub-agent via the Task tool
(`subagent_type: "general-purpose"`), one per row (parallel where independent), with exactly:

```
You are judging one live test of an AI agent. Verdict on faithfulness to the expected
output — not on style.

Requirement under test: {requirement text}
Input given: {input}
Expected output (from the spec): {expected}
Actual output: {actual}

Does the actual output satisfy what the expected output establishes — same decisions, same
required content/fields, same constraints honoured? Surface-level wording differences are
fine; missing/contradicting substance is not.

Return: PASS or FAIL, plus 1-2 sentences naming the specific substance matched or missed.
```

The judge sees only these five elements — no spec folder, no implementation. Judge verdict =
row verdict.

## Live type-conformance check

The agent verifier statically confirmed each agent's **declared type** (the `individual-agents`
taxonomy) matches the spec. This lane proves the *running* agent honours its type's contract —
checked once per agent, from the same runs (no separate execution needed unless a contract
wasn't exercised):

| Declared type | Live contract to observe |
|---------------|--------------------------|
| **LLM** | Produces generated output matching its I/O signature fields |
| **Tool** | Actually invokes its tools (tool calls observable in the trace), returns structured output |
| **Router** | Routes each test input to the branch the spec expects — assert the route taken, not just the final answer |
| **Retriever** | Output is grounded in retrieved context (retrieval step observable; answer cites/uses it) |
| **Subgraph** | Inner graph executes; composite honours the outer I/O signature |
| **Human-in-Loop** | Pauses/interrupts at the spec-defined point instead of proceeding autonomously |

A type-conformance miss (e.g. a Tool agent that answered from its own knowledge without calling
its tool) is a **FAIL** on that agent even if the output text looks right — the behaviour
contract, not the surface answer, is what was specified.

## Recording

Per row: input, actual output (trimmed), judge verdict + reason (or direct edge-case check), and
per agent: the type-conformance result. Failures route in Phase 4 — note for routing that a FAIL
here can be a prompt/impl defect (fix-side) **or** a spec expected-output that's wrong
(spec-defect loopback): the judge's "substance missed" sentence usually tells you which.
