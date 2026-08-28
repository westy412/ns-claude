# Assumption Audit: Certainty Honesty in Extraction Docs

> Find every statement whose written certainty exceeds what actually happened in the room. The transcript decides what rung of the ladder a claim sits on; the doc's language must match that rung.

---

## The Certainty Ladder

Classify what the transcript actually contains for each claim, top rung to bottom:

| Rung | What happened in the room | Doc language that matches |
|------|--------------------------|---------------------------|
| 1. Client decision | Explicit agreement ("yes, let's do that", direct instruction) | "agreed", "will", "is", plain fact |
| 2. Client statement of fact | Client stated it about their business/data/market | Plain fact, attributable |
| 3. Client leaning | Endorsement without commitment ("I like that", "probably yes", "I'd rather…") | "direction", "preferred", "leaning" — with the hedge visible |
| 4. Discussed option | Floated and explored, not landed ("could be", "maybe we…") | "option", "candidate", "discussed" |
| 5. Internal-side proposal | Our team suggested it (brainstorm TO the client) | "proposed", "our suggestion" — never a client need |
| 6. Silence | Not in the transcript at all | Marked inference — `(inferred)`, `_[⚠ open…]_` — or absent |

**A defect is any claim written at a higher rung than the transcript supports.** Writing rung-3 as rung-1 ("agreed" when the client said "probably") is the classic extraction failure.

---

## Checks

### 1. Decision inflation
Scan for decision language ("agreed", "will", "must", "is", "the flow is") and verify each against the ladder. Options written as decisions, leanings written as agreements → defect.

### 2. Proposal laundering
Internal-side brainstorms presented as client needs or requests. The client politely reacting ("yeah… makes sense") is rung 3 at best, not a request. Check the personas/needs tables especially — "what they need" entries must trace to client-stated needs, not our pitch.

### 3. Unmarked inference
Synthesis, extrapolated personas, derived metrics, assumed rationale — legitimate content, but only when visibly marked (`(inferred)`, italic caveat note, section banner). Unmarked → defect.

### 4. Status honesty
- **Defined** requires a dedicated deep-dive of that exact scope. A component session does not make its sub-components Defined.
- Partial coverage requires a "partially scoped" banner — and the banner must be true (not pasted over full-confidence prose).
- Statuses must agree everywhere they appear: doc header, components.md row, vision table, meeting frontmatter.

### 5. Acceptance-criteria and metrics honesty
Criteria/metrics derived by the extractor (not stated in the room) must be labelled derived/proposed. Unlabelled derived criteria read as client-validated evals → defect.

### 6. Open-question completeness
Anywhere the doc hedges ("TBD", "not discussed", "exact rules undecided") there should be a register entry + inline marker, or a deliberate reason there isn't. Hedge-without-register → WARN (the uncertainty is invisible to the graph).

### 7. Speaker weight
"The client said/wants" must reflect who actually said it and their standing (sponsor vs client-side support vs internal team). Note where a doc generalises one person's view into "the client's" position on a contested point.

---

## Output Format

**Findings table:**

| # | Severity | Doc § | Claim (quoted) | Written as (rung) | Transcript supports (rung + evidence) | Suggested fix |
|---|----------|-------|----------------|-------------------|---------------------------------------|---------------|

**Status audit:** one row per reviewed doc — status shown, coverage observed, verdict.

**Register audit:** hedges found in docs vs register entries present.

Note in your report: some certainty upgrades may come from the user confirming things during the extraction conversation. Do NOT excuse on that guess — flag and let the lead disposition against the session record.

---

## Scoring

- **FAIL** — a rung-4/5/6 claim written as rung-1/2 (option, proposal, or invention presented as client decision/fact); status inflation (Defined without the deep-dive; missing or false banner)
- **WARN** — rung-3 written as rung-1 where the leaning was strong; unmarked inference; unlabelled derived criteria; hedge-without-register
- **PASS** — every claim's language matches its rung; statuses and banners honest

End your report with PASS / WARN / FAIL.
