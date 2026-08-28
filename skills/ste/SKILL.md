---
name: ste
description: ASD-STE100 Simplified Technical English writing standard. Apply to technical prose — chat answers about technical work, engineering explanations, implementation plans, specs, architecture documents, commit messages, PR descriptions, issue text, and prose paragraphs in technical documentation. Load at the start of a technical session, or before you write or review technical prose. Does NOT apply to marketing, sales, brand, website, investor, legal, finance, or client-facing persuasive copy.
argument-hint: "[check | off]"
---

> **Invoke with:** `/ste` | **Keywords:** STE, simplified technical english, ASD-STE100, writing standard, plain english, technical writing, controlled language

Controlled writing standard for technical prose. The standard constrains *how* you write. It never constrains *what* you say.

**Input:** Any technical prose you are about to write.
**Output:** The same content, written to ASD-STE100.

## When to Use This Skill

Use this skill when:
- A session starts and the work is technical.
- You write an engineering explanation, an implementation plan, or a spec.
- You write a commit message, a PR description, or issue text.
- You write prose paragraphs inside technical documentation.
- The user asks you to audit prose against the standard.

**Skip this skill when:**
- The work is marketing, brand, website, or sales copy.
- The work is a finance, legal, or commercial document.
- The work is investor material, a blog post, or client-facing persuasive writing.

Those documents need voice, rhythm, and varied sentence length. This standard flattens them.

## Arguments

| Argument | Effect |
|----------|--------|
| (none) | Apply the standard for the rest of the session. |
| `check` | Audit prose against the standard. Audit the previous response, or the text the user supplies. Report each breach, name the rule it breaks, and give a rewrite. Change nothing else. |
| `off` | Stand down. Stop applying the standard until the user invokes the skill again. |

## Scope Test

Answer two questions before you write a paragraph.

1. **Is the text prose?** Code, identifiers, API names, config keys, file paths, flags, log lines, error strings, and quoted material are not prose. The standard never applies to them.
2. **Does the text inform or persuade?** Text that informs an engineer takes the standard. Text that persuades a buyer does not.

Load [scope-boundaries.md](references/scope-boundaries.md) when the answer is not clear.

## The Rules

### Sentences
- Write one idea per sentence. Write one instruction per sentence.
- Instructions: 20 words maximum.
- Descriptions and explanations: 25 words maximum.
- Paragraphs: 6 sentences maximum. One topic per paragraph.
- Do not join two instructions with "and" or a semicolon. Split them.

### Verbs
- Use the active voice. Write "the script writes the file". Do not write "the file is written".
- Use the imperative mood for instructions. Write "Run the migration". Do not write "You should run the migration".
- Use simple tenses only: simple present, simple past, simple future.
- Do not use `-ing` verb forms. The exception is a technical name, for example "streaming" or "logging level".
- Do not stack helping verbs. Write "this fails" or "this can fail". Do not write "this would potentially be able to fail".

### Words
- One word, one meaning. Name a thing once, then reuse that exact name. If you write "the handler", it stays "the handler". It never becomes "the callback" or "the listener".
- Use the plain word. See [word-choice.md](references/word-choice.md).
- Do not use idiom, metaphor, slang, or business jargon.
- Do not open a sentence with a bare "it", "this", or "that" when the referent is more than one sentence away. Name the thing again.

### Structure
- Keep the articles. Write "the config file". Do not write "config file".
- Do not delete words if the deletion makes the sentence ambiguous.
- Noun clusters: 3 words maximum. Write "the log for the build agent". Do not write "the build agent log configuration file".
- Put steps in the order the user must do them.
- Use a list when there is more than one item, option, or step.

### Precision Beats Simplicity
Break any rule above if the rule makes a statement wrong or ambiguous. Correctness comes first. Never drop a warning, a risk, a file path, or a required flag to meet a word limit.

## Pre-Send Check

Run this check on the draft, before you send it. This step is the one that makes the standard hold.

| # | Scan the draft for | Fix |
|---|--------------------|-----|
| 1 | A sentence over 25 words | Split it at the conjunction. |
| 2 | "is", "are", "was", or "were" followed by a past participle | Rewrite in the active voice. Name the actor. |
| 3 | An `-ing` verb form that is not a technical name | Rewrite as an infinitive or a simple tense. |
| 4 | The same thing under two names | Pick one name. Replace every other name. |
| 5 | A sentence that opens with "This", "That", or "It" | Name the thing, unless the referent sits in the previous sentence. |
| 6 | A noun cluster over 3 words | Break it apart with "of" or "for". |

Apply the fixes and send the corrected text. Do not report the check to the user.

## Reference Files

| Topic | Reference File | When to Load |
|-------|---------------|--------------|
| Before and after rewrites | [rewrite-examples.md](references/rewrite-examples.md) | You are unsure how a rule looks in practice. Load this file first. The examples teach faster than the rules. |
| Plain word choices | [word-choice.md](references/word-choice.md) | You need the plain word for a term. |
| Scope edge cases | [scope-boundaries.md](references/scope-boundaries.md) | You cannot tell if the standard applies to the artifact. |

## Key Principles

1. **Constrain the form, never the content** — The standard changes sentence construction. It never removes a caveat, a path, or a flag.
2. **The check beats the rules** — Rules alone hold weakly. The pre-send check holds.
3. **Length is out of scope** — The standard says nothing about response length. Length follows the task.
4. **Never rename a real thing** — Identifiers, commands, flags, and paths keep their exact names.
5. **One term, one thing, every time** — Term drift is the most common breach. It is also the most damaging.
