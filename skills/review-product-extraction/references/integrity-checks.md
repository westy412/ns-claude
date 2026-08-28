# Integrity Checks: Mechanical Verification of Extraction Docs

> Verify the mechanics: exact values, exact quotes, internal consistency across the doc set, and knowledge-graph conventions. Errors here are objective — a number is right or it isn't.

---

## 1. Values vs Transcript

Every number, date, count, percentage, duration, and threshold in the docs, verified against the transcript:

- Counts and quantities (data points, base sizes, percentages, "~26", "1.9M")
- Timelines and dates (build windows, meeting dates, "18 months")
- Latencies/limits stated as facts ("~15s", "90% effective")
- Ranges — a transcript "100 or 200" written as "100–200" is fine; "200+" is not

| # | Doc § | Doc value | Transcript value (evidence) | Verdict |
|---|-------|-----------|----------------------------|---------|

## 2. Names and Entities

People, companies, products, systems: spelled correctly, attributed correctly, consistently referenced (one canonical form per entity across the doc set). Check speaker names against the transcript's own spellings.

## 3. Direct Quotes

Every quoted string in the docs located in the transcript and compared word-for-word. Ellipses allowed; silent rewording is not. List each quote: exact / trimmed-faithfully / altered.

## 4. Cross-Doc Consistency

The doc set must not disagree with itself:

- Parent component doc vs sub-component docs (same flows, same rules, same tier language)
- Overview rows (components.md, vision table, Sub-Components tables) vs the doc they summarise
- Statuses identical everywhere the same artifact is described
- Dependency claims symmetric (if A says it needs B, B's "what others need from this one" should agree when both exist)
- Open-question markers point at the right register numbers; register "Answer belongs in" points at real docs/sections

## 5. Knowledge-Graph Conventions

- **Wikilinks resolve** — run the vault's `scripts/check-wikilinks.py` if present; otherwise scan `[[links]]` against existing file stems (exclude `.obsidian/`, skill directories). Broken links break the client portal → FAIL.
- Shortest-path link form (`[[name]]`, never `[[../name]]` or `[[dir/name]]`)
- Not-yet-documented items referenced as plain text, not dangling links
- `> **Up:**` footer present and correct; `Sources:` headers name real meeting files
- Backfill completeness: every doc created appears in its parent's routing table

## 6. Meeting-File Integrity

- Filename `YYYY-MM-DD-<slug>.md`; date matches the date stated inside the transcript
- Frontmatter complete: `date`, `type`, `scope`, `status`, `extracted-to`
- `status` truthful (`extracted` only if extraction + post-call analysis happened)
- `extracted-to` lists every doc created/updated by that meeting — no more, no less
- Post-call analysis rows match what actually exists on disk

## 7. Template Conformance

Reviewed docs contain their template's required sections (vision 8, component 10, sub-component 8 + journeys split 3a/3b). Missing sections or invented section structures → flag.

## 8. Publishing Safety

Vault publishing rules (per the vault's CLAUDE.md): root-level markdown is client-visible; `private/`, `templates/`, `drafts/` are excluded; `brand/` is public. Flag anything in the reviewed set that looks misplaced (internal-only notes in client-visible docs, review material outside `private/`).

---

## Output Format

One table per check section (formats above), then:

**Summary:** checks run / passed / failed, with every failed item carrying doc §, evidence, and suggested fix.

---

## Scoring

- **FAIL** — wrong value, altered quote, misattributed name, broken wikilink, contradiction between docs, untruthful meeting frontmatter
- **WARN** — inconsistent entity naming, asymmetric dependencies, missing Up/Sources conventions, template deviations, misplaced-content suspicions
- **PASS** — all checks clean

End your report with PASS / WARN / FAIL.
