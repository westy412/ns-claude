---
name: sales-deck
description: >-
  Generate a NovoSapien-style client pitch deck: a self-contained, animated,
  brand-grounded HTML slideshow that is PRESENTED (not read) to a senior
  executive. Use when building a pitch, proposal, board deck, vision deck,
  or investor/CEO slideshow for any client. Produces index.html + deck.css +
  deck.js + live pausable diagrams, deployable as its own Vercel project.
argument-hint: "[client name]"
---

> **Invoke with:** `/sales-deck` | **Keywords:** pitch deck, slideshow, client presentation, board deck, CEO pitch, vision deck, proposal deck

Build a high-end, presented-live HTML pitch deck in the NovoSapien house style:
minimal on-slide words, the argument in the presenter's cue cards, on-brand
animated diagrams, and a different layout on every slide. The reference
implementation this style was distilled from is the Totaljobs deck
(`total-jobs-agentic-pitch.vercel.app`); this skill reproduces that end-state
for **any** client.

**Input:** a client (brand + source material), the audience (who it's pitched
to), the presenter (who delivers it), and the ask. See _Inputs_ below.
**Output:** a self-contained deck folder (`index.html`, `deck.css`, `deck.js`,
`visuals-core.js`, one or more diagram files), optionally deployed to Vercel.

## When to Use This Skill

Use when the user wants to build / regenerate a **slide deck or pitch** that
will be shown live to a decision-maker — a CEO/board/investor proposal, a
vision deck, a sales pitch. Trigger words: "pitch deck", "slideshow",
"present to", "board deck", "deck for [client]".

**Skip when:** they want a written document/report (it's read, not presented),
a one-pager, or a deck that must be a native PowerPoint/Google Slides file the
client edits in Office tools — this skill produces an HTML deck (PDF-exportable
via print, but not .pptx).

## The Non-Negotiables (the END STATE — do not re-litigate)

These were converged on through many feedback rounds. Bake them in from the start.

1. **Presented, not read.** Minimal words on the slide; the real argument lives
   in the **speaker-notes cue cards** (press `N`). One claim per slide.
2. **The headline IS the argument** — a sentence with a point of view, never a
   noun label ("AI just reset the board", not "Market Context").
3. **Word budget:** either **≤3 short bullets** OR **~6 concise flank points**;
   sentences roughly **6–16 words**; one **hero stat** per data slide.
4. **NO EM DASHES anywhere** (on slides or in notes). Use commas, colons, periods.
5. **Layout variety** — never two identical layouts back-to-back. Rotate the
   archetypes in `references/layout-archetypes.md`.
6. **On-brand animated diagrams**, pausable (hover + button), with a
   reduced-motion static fallback. **No diagrams on the opening slides**;
   introduce them once the argument has landed.
7. **Brand-grounded** — real logo + exact colours from the client's live site
   or brand assets, wired as CSS variables. Never guess brand colours.
8. **Source-grounded + safe** — only assert what the client actually
   discussed/documented; flag sensitive figures (headcount, spend) in the
   notes, never crassly on-slide.

## Inputs (gather these first; ask only what's missing)

| Input | Why it matters |
|-------|----------------|
| **Client + brand source** | Live site URL or brand assets → real logo + colours |
| **Source material** | Their vault/docs/transcripts → grounds every claim |
| **Audience** | Who it's pitched to (e.g. "the Group CEO") → altitude + tone |
| **Presenter** | Who delivers it → cue cards are written *for them* |
| **The ask** | The close. If undecided, keep it soft and flag it in notes |
| **Output location** | Folder for the deck; whether to deploy to Vercel |

## Generation Workflow

Run as phases; show your work and get a nod before the big build.

1. **Ground the brand** → `references/style-system.md`. Pull the client's real
   logo SVG and exact hex colours; fill the `:root` token block in `deck.css`.
2. **Shape the narrative** → `references/narrative-arc.md`. Map the source
   material onto Problem → Bet → Outcome → Solution (one slide per domain/world)
   → Proof → Economics → soft close. Lead the recommendation early. ~12–15 slides.
3. **Assign layouts** → `references/layout-archetypes.md`. Give each slide an
   archetype; ensure no two neighbours match. Pick which slides earn a diagram.
4. **Scaffold from templates** → copy `templates/*` into the output folder;
   wire `index.html` slides; set the brand tokens; drop in the logo (light/dark).
5. **Write the copy** → `references/copy-discipline.md`. Slides get the bare
   claim; the argument goes in `.snote` cue cards. Run the em-dash check.
6. **Build the diagrams** → `references/animated-diagrams.md`. Clone
   `templates/example-diagram.js` per diagram; register, mount per slide, pause.
7. **Review** → serve locally, walk every slide, confirm the non-negotiables.
8. **Deploy (optional)** → `references/deploy.md`. Self-contained bundle to a
   standalone Vercel project, one URL per client.

## Reference Files

| Topic | File | When to load |
|-------|------|-------------|
| Brand grounding, tokens, gradients, logo swap | [style-system.md](references/style-system.md) | Phase 1 |
| The slide layout archetypes + markup | [layout-archetypes.md](references/layout-archetypes.md) | Phase 3 + 4 |
| The pausable animated-diagram system | [animated-diagrams.md](references/animated-diagrams.md) | Phase 6 |
| Copy rules (presented-not-read, no em dashes, cue cards) | [copy-discipline.md](references/copy-discipline.md) | Phase 5 |
| Narrative arc + source grounding + sensitivity | [narrative-arc.md](references/narrative-arc.md) | Phase 2 |
| Standalone Vercel deploy per client | [deploy.md](references/deploy.md) | Phase 8 |

## Templates

| Template | Purpose |
|----------|---------|
| [index.html](templates/index.html) | Deck skeleton: chrome + one slide per archetype + script includes |
| [deck.css](templates/deck.css) | `:root` brand tokens + all archetype CSS + chrome + print |
| [deck.js](templates/deck.js) | Slide controller: nav, per-slide diagram mount/dispose, notes drawer |
| [visuals-core.js](templates/visuals-core.js) | The pausable mount registry + `makeClock` (copy verbatim) |
| [example-diagram.js](templates/example-diagram.js) | A self-contained diagram to clone per client |

## Output

```
<client>-pitch/
├── index.html          (the deck)
├── deck.css            (brand tokens filled in)
├── deck.js
├── visuals-core.js
├── visuals/            (one file per diagram, cloned from example-diagram.js)
│   └── <client>.js
└── assets/img/         (client logo: light + dark variants)
```

## When to Ask for Feedback

Always check in before:
- Finalising the narrative outline + slide list (Phase 2/3).
- The big scaffold build (Phase 4).
- Deploying to a public URL (Phase 8) — confirm the URL/name; note that
  speaker notes ship in page source (offer password protection if sensitive).
