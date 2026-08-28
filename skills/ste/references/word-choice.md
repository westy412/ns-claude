# Word Choice

> **When to load:** You need the plain word for a term, or you want to check a word against the standard.

ASD-STE100 works from an approved dictionary. Each approved word carries one meaning and one part of speech. This file holds the subset that matters for engineering prose.

**Rule:** if a word appears in the "Avoid" column, use the word in the "Use" column instead. If the replacement changes the meaning, keep the original word and keep the meaning.

---

## Verbs

| Avoid | Use |
|-------|-----|
| initiate, commence, kick off | start |
| terminate, cease | stop |
| utilise, utilize, leverage | use |
| facilitate, enable (when it means "let") | let, allow |
| implement (when it means "write") | write, build, add |
| perform, execute (outside a real `exec` call) | do, run |
| attempt | try |
| require | need |
| ascertain, determine | find, check |
| modify, alter | change |
| eliminate, remove entirely | delete, remove |
| verify, validate (outside a real validation step) | check |
| surface, expose (when it means "show") | show |
| encounter | get, find, hit |
| propagate (outside a real propagation) | pass, spread |

---

## Connectives and Prepositions

| Avoid | Use |
|-------|-----|
| prior to, in advance of | before |
| subsequent to, following | after |
| regarding, with regard to, in respect of | about |
| due to the fact that, owing to the fact that | because |
| in order to | to |
| in the event that | if |
| in terms of | (delete, or name the thing) |
| with respect to | for, about |
| additionally, furthermore, moreover | also, and |
| however (mid-sentence) | but (or split the sentence) |
| thus, hence, therefore | so (or split the sentence) |
| whilst | while |
| amongst | among |

---

## Hedges and Fillers

| Avoid | Use |
|-------|-----|
| basically, essentially, fundamentally | (delete) |
| actually, simply, just | (delete) |
| it is worth noting that | (delete, keep the fact) |
| as you can see | (delete) |
| please note that | (delete, or write **Note:**) |
| in general, generally speaking | (delete, or state the exception) |
| relatively, fairly, quite, somewhat | (delete, or give the number) |
| various, several, a number of | give the count |
| robust, comprehensive, seamless | (delete, or state the property) |

Delete a hedge only when the hedge carries no information. Keep real uncertainty. Write "I have not tested this path" instead of deleting the doubt.

---

## Business Jargon

| Avoid | Use |
|-------|-----|
| circle back, touch base | discuss again, ask again |
| align on | agree |
| bandwidth (about people) | time, capacity |
| deep dive | detailed review |
| low-hanging fruit | quick fix |
| move the needle | change the result |
| best-in-class, world-class, enterprise-grade | (delete) |
| production-ready, battle-tested | (delete, or state what you tested) |
| unlock, supercharge | (delete, or name the effect) |
| holistic, end-to-end (as filler) | (delete, or name the range) |

---

## Idiom and Metaphor

Delete idiom. Idiom fails for non-native readers and for automated translation.

| Avoid | Use |
|-------|-----|
| a rabbit hole | a long detour |
| smoke test | a first quick test |
| happy path | the normal case |
| bikeshedding | argument about a small detail |
| the source of truth | the authoritative record |
| under the hood | inside the implementation |
| out of the box | by default |
| a footgun | a dangerous default |

**Exception:** keep the term when it is the real name of a thing in the codebase or the wider ecosystem. "Smoke test" stays if the CI job is called `smoke-test`. Name it once, then reuse that exact name.

---

## Words You Must Never Change

Never substitute a plain word for any of these:

- Identifiers: variable names, function names, class names, type names.
- API names, method names, and endpoint paths.
- Config keys, environment variable names, and CLI flags.
- File paths and directory names.
- Package names and version strings.
- Log lines, error strings, and stack trace content.
- Quoted material from a user, a document, or a third party.
- Established technical terms with a precise meaning: "idempotent", "eventual consistency", "race condition", "memoization", "backpressure".

The last item matters. A precise technical term is shorter and clearer than its plain-word paraphrase. Use the term. Define it once if the reader may not know it.
