# Autonomy & Escalation

> **Context:** The fix-or-ask contract for the whole dev-workflow chain. Every point where
> an agent finds a problem — a review finding, a per-phase code-review issue, a verifier
> mismatch, a prober gap — runs this decision: fix it myself, or stop and bring the user in?
> And when I stop, how do I ask? Cite this; don't re-state it.

---

## The one question

**"Can I resolve this from what the user already gave me?"** — the discovery doc, the spec,
and everything said earlier in the conversation. That answer routes everything below.

- **Yes** → branch **A** (fix it autonomously).
- **No** → branch **B** (escalate).

## A. Auto-fix what's resolvable from stated intent

If the finding is a *divergence* from what the source material already decides, fix it — no
interruption. The user already answered; honor the answer.

- **Code diverges from spec** → fix the code. The spec is the truth.
- **Spec correction resolvable from intent** (the discovery doc / conversation settles what
  the spec *should* have said) → fix it, and **write the correction back into the
  spec/discovery — never code-only.** Code-only rots the spec, and with it the
  spec-derived test cases: the spec stays wrong and the tests stay wrong. Patch the source.

## B. Escalate only genuine uncertainty

When the source material genuinely **doesn't decide it** — a real gap, a real contradiction
in stated intent — stop and bring the user in. Don't escalate what you can resolve; don't
guess what you can't.

- **Fire each question once.** On "out of scope / don't know / proceed," log it as a
  known-risk and move on. The gate must never trap the conversation.

## C. How to escalate (comms standard)

This governs the **question you ask the user**, not the document you write. When you escalate:

- **Brevity over walls of text.** One specific, concise question per genuine gap — not a
  questionnaire.
- **Draw it.** When the gap is about structure or a choice between options, sketch an inline
  ASCII diagram so the user can see it and answer in seconds.
- **Self-contained in chat.** Assume the user will NOT open the discovery doc or the spec.
  Every question carries everything needed to answer it right there in the chat — the
  relevant excerpt or decision, the options, the consequence of each. "See §X of the doc"
  is not a question; it's homework. The artifact records the answer; the chat is where the
  question lives.
- **Applies everywhere a skill asks the user to decide** — discovery probes, spec-builder
  gap-fills, review/build escalations.
- **Not the same as showing work for approval.** A propose-gate diff stays *full* — the user
  must see exactly what they're approving. Brevity is for the *question*, never for hiding
  the artifact.

---

## The autonomy dial

The better the front-loading, the more findings branch **A** resolves straight from the spec,
and the less **B** fires. **Spec quality controls the human-interrupt rate everywhere
downstream** — that is the lever the whole methodology pulls.
