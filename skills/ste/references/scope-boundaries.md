# Scope Boundaries

> **When to load:** You cannot tell if the standard applies to the artifact in front of you.

The standard covers technical prose only. This file settles the edge cases.

---

## The Two-Question Test

1. **Is the text prose?**
   Code, identifiers, paths, flags, log lines, error strings, and quoted material are not prose. Stop. The standard does not apply.

2. **Does the text inform or persuade?**
   - **Inform an engineer** → apply the standard.
   - **Persuade a buyer, an investor, or a client** → do not apply the standard.

When both answers point at "apply", apply the standard. When either answer points away, do not.

---

## Per-Artifact Table

| Artifact | Standard applies? | Notes |
|----------|-------------------|-------|
| Chat answer about technical work | Yes | The main case. |
| Engineering explanation | Yes | |
| Implementation plan | Yes | |
| Spec or architecture document | Yes | Prose paragraphs only. Diagrams and tables follow their own conventions. |
| Commit message | Yes | Subject line and body. Keep the *why*. |
| PR description | Yes | |
| Issue or ticket text | Yes | |
| README prose paragraphs | Yes | Prose only. Code blocks, badges, and command examples are untouched. |
| API documentation prose | Yes | Parameter names and types are untouched. |
| Runbook or incident writeup | Yes | Never drop a step, a threshold, or a rollback command. |
| Code comments | Partly | Apply the sentence and verb rules. Match the comment density and idiom of the surrounding file. |
| Docstrings | Partly | Same as code comments. Never change parameter names or types. |
| Test names | No | Follow the framework convention. |
| Error strings and log lines | No | Never edit an error string to satisfy the standard. |
| Marketing or brand copy | No | |
| Website or landing page copy | No | |
| Sales deck, pitch, or proposal | No | |
| Outbound email or case study | No | |
| Investor material | No | |
| Blog post | No | |
| Legal, finance, or commercial document | No | |
| Any client-facing persuasive writing | No | |

---

## Mixed Sessions

One session often mixes both kinds of work. Handle the mix at the paragraph level, not the session level.

- Apply the standard to the technical paragraphs.
- Leave the persuasive paragraphs alone.
- Do not announce the switch. Just write each part correctly.

Example: a session builds a pricing page and also debugs the checkout API. The page copy stays persuasive. The debugging explanation takes the standard.

---

## The Grey Cases

**A technical document with a persuasive introduction.**
The introduction sells the approach. The body explains the approach. Apply the standard to the body. Leave the introduction alone.

**A commit message on a marketing site repo.**
The commit message informs an engineer. Apply the standard. The repo subject does not matter. The reader does.

**A client-facing technical proposal.**
The proposal persuades. Do not apply the standard, unless the client is an engineering team that asked for the technical detail. When in doubt, ask the user.

**An internal RFC that argues for a decision.**
An RFC informs engineers, even when it argues. Apply the standard. A clear argument survives short sentences.

**A code comment that explains a non-obvious trade-off.**
Apply the sentence and verb rules. Do not compress the trade-off into fewer words if the compression loses the reason.

---

## Hard Limits

These limits override every other rule in the standard.

1. **Never rename a real thing.** Identifiers, commands, flags, and paths keep their exact names, however long or awkward.
2. **Never drop a caveat.** A warning, a risk, a precondition, or a required flag stays in, whatever the word count.
3. **Never lose a number.** Thresholds, timeouts, retry counts, ports, and versions stay exact.
4. **Never change quoted text.** Quote what the source said, unedited.
5. **Never trade correctness for simplicity.** If a rule makes a statement wrong or ambiguous, break the rule.
