# Prober Core

> **Context:** Discovery's job is not to transcribe what the user says — it is to *probe* until
> the idea is concrete enough to spec. This file holds the four probing instruments: the
> model-held Coverage Checklist, the Force-Concreteness reflex, the named Ambiguity Classes, and
> the blocking Pre-Write Validation Gate. Hold the checklist silently through the conversation;
> run the gate before writing `discovery.md`. For *how* and *when* to bring a question to the
> user, this file defers to `autonomy-and-escalation.md` (the fix-or-ask contract) — don't restate it.

---

## The Coverage Checklist (model-held)

A set of load-bearing dimensions the **model tracks silently** — not a form the user fills, not an
interrogation. By the end of discovery each dimension is either *concrete* or *explicitly logged as
a known-risk / out-of-scope*. Coverage is guaranteed without turning the conversation into a survey.

| Dimension | Concrete means… |
|-----------|-----------------|
| **Problem concreteness** | A specific problem with a named sufferer and a real consequence — not "users want X." |
| **I/O contract** | trigger → output → format is pinned: what starts it, what it produces, in what shape. |
| **Scale / volume** | Rough magnitude — how many, how often, how big. Order-of-magnitude is enough. |
| **Failure modes** | What goes wrong, and what should happen when it does. |
| **Explicit out-of-scope** | A non-empty list of what this is deliberately *not* doing. |
| **Edge cases** | The boundary inputs/states the happy path ignores. |

Track which dimensions are still vague. Those are where you probe — depth, not volume.

### Dimension ownership — who resolves a vague dimension

- **User-owned** — the problem, the success measure, scope boundaries (in/out),
  failure *policy* (what SHOULD happen when it goes wrong), and the keystone
  decision. Resolved by **asking** — never by research, inference, or a
  plausible guess. Self-answering a user-owned dimension is this skill's
  defining failure mode.
- **Reality-owned** — data shapes, schemas, existing seams/code, API responses,
  library capabilities. Resolve by probing the real thing (reality-grounding);
  asking the user is usually the wrong move — they'll guess.

Failure modes span both: the *policy* ("silently skip or hard-fail?") is
user-owned; the *mechanics* ("what does the API return on 429?") are reality-owned.

## Force-Concreteness (a reflex)

The moment an answer is abstract, make it concrete **before moving on**:

- "success = users happier" → *"Happier measured how? Give me one number or one before/after."*
- "it handles requests" → *"Walk me through one real request: what comes in, what goes out?"*
- "it should be fast" → *"Fast like 100ms, or fast like not-30-seconds?"*

A worked input→output example, a real number, or a named instance — one of those, every time.
Abstract nouns ("seamless", "robust", "scalable") are a prompt to ask for the concrete thing underneath.

## Ask-on-Ambiguity — the named high-risk classes

Discovery is an interrogation of the *idea* — friendly in tone, relentless in coverage. The bias is
to **ask**: when a high-risk class is silent, contradictory, or user-owned-and-vague, fire the
question. Don't re-ask what's already clearly answered, and fire each question once (the gate's
escape valve) — but "the user was probably clear enough" is never a reason to skip. **Zero questions
on a fresh idea means under-probing, not a clear brief.** The classes most likely to sink a build:

- **The I/O contract** — exact trigger, exact output, exact shape.
- **Data source & shape** — where real data comes from and what it actually looks like (see reality-grounding).
- **Scale / volume / latency** thresholds.
- **Failure & error behavior** — what "wrong" does.
- **Boundaries / ownership** — what's in vs out, who/what else touches this.
- **The keystone decision** — the one choice everything else hangs off.

How you ask follows the escalation comms standard in `autonomy-and-escalation.md` (clause C): one
brief specific question, ASCII-sketch the options when it's structural.

## Reality-Grounding

Probe the *real* systems and data, not imagined ones — the actual API response, the real data shape,
the existing schema/code — not just the docs and not a guess. Most "reality differed from the spec"
failures are preventable right here. When a data contract or integration is in play, ground it
against the real thing (codebase/web research) before it's written down as fact.

**Reuse claims carry a probe obligation.** Any framing that leans on a named existing
capability/seam/asset — "reuse X", "wrap the existing Y", "few-shot on Z", "same gate as W" —
must be probed to a cite (file:symbol) proving the seam exists at the **shape** assumed: a
callable service vs logic inline in a route; a data pool that actually carries the needed
fields; a gate whose fail-mode is stated. Never infer a reusable seam from a code comment or a
sibling's design. If the seam is aspirational, the doc says so explicitly (extract-first note)
instead of asserting it.

## Soft Sequencing

Not a rigid order, but a bias: get the **problem and a measurable definition of success concrete
before** converging on solution detail. Jumping to solution while the problem is still abstract is
discovery's #1 named failure mode. If you notice solutioning early, pull back to the problem once.

---

## The Pre-Write Validation Gate (BLOCKING)

Before writing `discovery.md`, **stop and re-read the conversation as an artifact.** Refuse to pass
thin, unanchored, or internally-inconsistent output. This is a gate, not a question — it runs every
time, after the convergence checkpoint.

**Run the checklist.** For each Coverage Checklist dimension: concrete, or explicitly logged as
known-risk/out-of-scope? Any dimension that is silently vague is a gate failure.

**Pre-mortem.** *"Assume implementation hits a surprise — where did we most likely under-think this?"*
Name the one or two weakest spots. Resolve them, or log them explicitly as Known-Risks. This is the
instrument for the unknown-unknowns the checklist can't enumerate.

**Required outputs present.** The I/O contract, a non-empty out-of-scope list, and a Known-Risks
section all exist. If not, they're gate failures.

**Zero-questions tripwire.** Reaching this gate on a fresh idea with zero user-directed questions
fired (an empty Escalation & Decision Record for this conversation) is a gate FAILURE by
definition — go back, map the checklist, and fire the top ambiguities before writing anything.

**Escape valve (never trap the conversation).** Each gap becomes one follow-up question, asked per
the comms standard — and **fired once.** On "out of scope / don't know / proceed," log it as a
Known-Risk and move on. The gate enforces coverage; it must never loop the user in circles. (This is
clause B of `autonomy-and-escalation.md`: escalate genuine uncertainty, fire each question once.)

Each of these points leaves telemetry: at save time, every fired question, forced concretisation,
and fired-once gap becomes one row in `progress.md`'s **Escalation & Decision Record (spec-stage)**
(type `branch-B`, `prober-force`, or `fired-once`) — the front-load signal the run retro reads.

Only once the gate passes (or every open gap is logged as a Known-Risk) do you write `discovery.md`.
