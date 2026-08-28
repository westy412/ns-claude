# Grounding Tracing: Extraction Docs vs Transcript

> Trace every substantive claim in the extracted documents back to the source transcript(s). Catch fabrications (claims with no basis) and misattributions (right fact, wrong mouth).

---

## Why This Matters

These documents are client-visible (the vault publishes to the client's portal) and downstream-consumed (specs and builds derive from them). A fabricated "requirement" gets built; a misattributed opinion becomes "the client asked for this." The transcript is the authority — everything else must either trace to it or be visibly marked as inference.

---

## What Counts as a Substantive Claim

Trace each of these; skip template boilerplate and pure structure:

- Stated facts about the client's business, product, data, or market (numbers, percentages, dates, system names)
- Decisions and agreements ("X was agreed", "the flow is Y")
- Requirements and business rules
- Direct quotes (must be verbatim from the transcript)
- Attributed statements ("Jeremy said…", "per the client…")
- Journey steps and acceptance criteria (each encodes claims about what was described)
- Risk/constraint statements presented as known ("VPNs get around IP blocking")

---

## Process

1. **Read all source transcripts first**, building an index of who said what.
2. **Walk each reviewed doc claim by claim** — including tables, diagrams (node labels encode claims), and the graph surfaces in scope (component-map rows, register rows, post-call analysis).
3. **Classify every claim:**

| Class | Meaning | Defect? |
|-------|---------|---------|
| VERBATIM | Word-for-word from the transcript (quotes) | No — verify exactness |
| PARAPHRASE | Faithful restatement of one passage | No |
| SYNTHESIS | Faithful combination of multiple passages | No — cite all passages |
| INFERRED-MARKED | Not in transcript, visibly marked (`(inferred)`, `_[⚠ open…]_`, partially-scoped banner covering it) | No |
| INFERRED-UNMARKED | Not in transcript, reads as fact | **Yes** |
| ABSENT | No transcript basis at all, unmarked | **Yes — fabrication** |
| CONTRADICTED | Transcript says otherwise | **Yes — worst class** |

4. **Check attribution separately.** Two failure modes:
   - **Wrong speaker** — the doc credits a statement to the client when an internal team member said it (or vice versa)
   - **Side confusion** — an internal-side proposal (brainstormed TO the client) written as a client need or request. The client *reacting positively* to a proposal is not the client *requesting* it — that distinction belongs to the assumption audit, but flag it here when the doc states an origin ("the client wants X") the transcript doesn't support.

---

## Output Format

**Traceability summary:**

| Doc | Claims traced | Verbatim/Paraphrase/Synthesis | Inferred-marked | Defects |
|-----|--------------|-------------------------------|-----------------|---------|

**Defect table (every INFERRED-UNMARKED, ABSENT, CONTRADICTED, misattribution):**

| # | Severity | Doc § | Claim (quoted from doc) | Class | Transcript evidence (timestamp/section, or "none") | Suggested fix |
|---|----------|-------|------------------------|-------|---------------------------------------------------|---------------|

**Quote verification:** list every direct quote with exact/inexact verdict.

Severity: **FAIL** for ABSENT, CONTRADICTED, meaning-changing misattribution, inexact direct quote; **WARN** for INFERRED-UNMARKED that is plausible-but-unmarked, minor paraphrase drift.

Note in your report: claims may have been confirmed by the user during the extraction conversation (not in the transcript). Do NOT excuse any claim on that guess — flag it; the lead holds the session record and dispositions it.

---

## Scoring

- **FAIL** — any fabrication (ABSENT), any CONTRADICTED claim, any misattribution that changes meaning, any inexact direct quote
- **WARN** — unmarked inferences, paraphrase drift that softens/hardens meaning
- **PASS** — every substantive claim traces or is marked

End your report with PASS / WARN / FAIL.
