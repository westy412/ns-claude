# Update Formats

> **When to read:** When writing changelog entries, component document updates, or architecture notes during a digest.

---

## Changelog Entry Format

Append to the relevant sub-component's `changelog.md`:

```markdown
### YYYY-MM-DD — [Short title]
- **Source:** [Meeting type] ([[meetings/YYYY-MM-DD-slug]])
- **Change:** [What changed and why — plain language, 1-3 sentences]
- **Affects:** [Which entity journeys or sections in the sub-component doc]
- **Status:** Proposed
```

**Status values:**
- `Proposed` — captured from meeting, not yet acted on
- `Accepted` — user confirmed this should be implemented
- `Implemented` — change has been built and shipped
- `Rejected` — decided against after further discussion

**Rules:**
- One entry per finding — don't combine multiple findings into one entry
- Link back to the source meeting via wikilink
- "Affects" should reference specific journeys or sections by name where possible
- Keep "Change" concise — the detail is in the linked meeting transcript

---

## Component / Sub-Component Document Updates

When updating an existing section in a component or sub-component document:

1. **Add to an existing section** — append to the relevant list or paragraph
2. **Source-tag the addition:** `(Source: standup 2026-05-16)` at the end of the added content
3. **Don't rewrite** — add, don't restructure. If a restructure is needed, flag for a focused session.

**Where updates typically go:**

| Finding type | Target section in doc |
|---|---|
| New functional requirement | "What Needs to Happen?" → Functional requirements |
| New business rule | "What Needs to Happen?" → Business rules |
| New edge case | "What Needs to Happen?" → Edge cases |
| UX change | "Look and Feel" or changelog (depending on scope) |
| New data requirement | "Data Requirements" table |
| New dependency | "Dependencies" table |
| New risk | "Risks" |
| Journey modification | Flag for focused session (too complex for inline edit) |

---

## Architecture Notes

When updating architecture documents:

1. **Integration notes** — add to `vault/architecture/integrations/integrations.md` or create a new integration file if substantial
2. **Tech stack decisions** — add to the relevant section in `vault/architecture/`
3. **Open questions** — append to the central `open-questions.md` register at the project root (create it if missing); leave an inline `_[⚠ open — see [[open-questions]] #N]_` marker in the relevant doc

**Format for integration notes:**

```markdown
## [Integration Name]

- **Decision:** [What was decided or is being leaned toward]
- **Source:** [[meetings/YYYY-MM-DD-slug]]
- **Status:** Exploring | Decided | Implemented
- **Components affected:** [[component-1]], [[component-2]]
- **Notes:** [Any additional context]
```

**Format for open questions:**

```markdown
### [Question — one line]
- **Raised:** [[meetings/YYYY-MM-DD-slug]]
- **Context:** [Why this matters, 1-2 sentences]
- **Components affected:** [[component-1]]
```
