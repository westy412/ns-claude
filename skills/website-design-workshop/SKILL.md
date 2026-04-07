---
name: website-design-workshop
description: Run structured website design workshops to capture deep brand requirements across multiple brands. Acts as a workshop facilitator -- drives topic order, suggests angles to explore with the client, and progressively builds a comprehensive brand brief covering identity, visual style, voice, sitemap, and per-page detail. Use when planning a website design for a client with one or more brands.
---

> **Invoke with:** `/website-design-workshop` | **Keywords:** website workshop, design consultation, brand brief, brand identity, sitemap, website planning

Facilitate a structured website design workshop for a client with one or more brands (up to 5). The skill drives topic order, suggests questions and angles for the team member to explore with the client, processes whatever they bring back, and progressively builds a comprehensive brand brief.

**Input:** Client name, brand names, and iterative conversation/transcription dumps from the team member's client meetings
**Output:** Per-brand identity working docs (brand identity, visual identity, voice identity), a sitemap, a directory of page detail files, and an aggregate brand brief at the end. Stitch prompts are an optional final step.

## When to Use This Skill

Use this skill when:
- Running a website design consultation or workshop with a client
- Capturing brand requirements for a new website project
- Building a deep brand identity, visual identity, and voice identity for one or more brands
- Mapping a sitemap and detailed page-by-page requirements

**Skip this skill when:**
- Implementing an already-defined design
- Just need a quick mockup with no consultation process
- The brief already exists and you're handing it off to a designer/developer

## Reference Files

Load these just-in-time based on the current phase:

| Topic | Reference File | When to Load |
|-------|---------------|--------------|
| Topic priorities & angles to explore | [conversation-guide.md](references/conversation-guide.md) | At session start, when suggesting the next topic, and when surfacing gaps |
| Multi-file routing & extraction rules | [extraction-protocol.md](references/extraction-protocol.md) | Every time the user pastes transcription, notes, or direct answers |
| Stitch prompt crafting (OPTIONAL) | [google-stitch-prompts.md](references/google-stitch-prompts.md) | Only if the user explicitly asks for Stitch prompts at the end |

## Templates

| Template | Purpose | When to Use |
|----------|---------|-------------|
| [session-log.md](assets/session-log.md) | Session-level chronological log | Created at session start |
| [discussion-log.md](assets/discussion-log.md) | Per-brand raw, append-only audit trail | Created per brand at session start |
| [brand-identity.md](assets/brand-identity.md) | Curated working doc -- who they are, values, story | Created per brand at session start |
| [visual-identity.md](assets/visual-identity.md) | Curated working doc -- colors, typography, imagery | Created per brand at session start |
| [voice-identity.md](assets/voice-identity.md) | Curated working doc -- tone, personality, language | Created per brand at session start |
| [sitemap.md](assets/sitemap.md) | Curated working doc -- the page tree | Created per brand once page list is established |
| [page.md](assets/page.md) | Template for each file in `pages/` | Created per page once sitemap is set |
| [extras.md](assets/extras.md) | Functionality, references, open questions | Created per brand at session start |
| [brand-brief.md](assets/brand-brief.md) | Aggregate brief assembled from all working docs | Generated at the end (Phase 4) |
| [stitch-prompt.md](assets/stitch-prompt.md) | Individual Stitch prompt (OPTIONAL) | Generated only if user requests in Phase 5 |

## Key Principles

1. **Facilitator, not interrogator** -- The skill drives topic order and suggests angles to explore. The team member runs the actual conversation with the client. The skill processes what comes back.
2. **Two-layer model** -- Raw extracted points always go to `discussion-log.md` (append-only audit trail). Curated working docs (`brand-identity.md`, `visual-identity.md`, `voice-identity.md`, etc.) get progressively refined from those raw points. The discussion log is the source of truth; the working docs are the current understanding.
3. **Multi-file routing** -- A single point can land in multiple working docs. "We want to feel premium" might update brand-identity (positioning), visual-identity (aesthetic direction), and voice-identity (tone). Route to all relevant docs.
4. **Drive the order, suggest the angles** -- Don't script exact wording for the team member. Instead, name the next topic and offer 3-5 angles or questions they could explore. Let them have a natural conversation.
5. **Brand identity is the soul** -- Deeply understand who the brand is, what they stand for, what they want to project. This is equal in weight to (or more important than) the visual side.
6. **Sitemap and page-by-page is the centrepiece** -- The bulk of detail lives at the page level. Each page gets its own file in `pages/` with purpose, audience, key messages, sections, CTAs, copy direction, must-haves, and any specified layout requirements.
7. **Layout is captured opportunistically** -- Don't ask about layout in the abstract. Only capture page-specific layout requirements when the client volunteers them ("calendar at the bottom", "image hero").
8. **Stitch is optional** -- The brand brief is the deliverable. Stitch prompts are an optional add-on at the end if the team member wants to spike a design.

## Session Flow

### Phase 1: Setup

1. Ask the user for the client name
2. Ask how many brands and their names (up to 5)
3. Create the output directory structure:

```
{project}/website-workshop/{client-name}/
├── session-log.md
└── brands/
    └── {brand-1}/
        ├── discussion-log.md       # raw, append-only (source of truth)
        ├── brand-identity.md       # curated working doc
        ├── visual-identity.md      # curated working doc
        ├── voice-identity.md       # curated working doc
        ├── sitemap.md              # curated working doc (created early)
        ├── pages/                  # one file per page (populated after sitemap)
        ├── extras.md               # functionality, references, open questions
        └── stitch-prompts/         # empty until Phase 5 (optional)
```

4. Initialise `session-log.md`, and per brand: `discussion-log.md`, `brand-identity.md`, `visual-identity.md`, `voice-identity.md`, `sitemap.md`, `extras.md` -- all from templates with the brand and client name filled in. Leave `pages/` empty for now.
5. Load [conversation-guide.md](references/conversation-guide.md) and present the topic priorities and a recommended starting topic to the team member.

### Phase 2: Structured Conversation Loop (iterative)

The skill drives the topic order. Each loop has two parts: **direct + receive**.

**Skill direction (before each round):**
1. Name the topic to focus on next, based on the priority order in [conversation-guide.md](references/conversation-guide.md) and current coverage gaps
2. Offer 3-5 angles or questions the team member could explore with the client
3. Let the team member know they don't need to follow the exact wording -- just have the conversation and bring back what they get

**Receive and process (after each round):**
1. **Load [extraction-protocol.md](references/extraction-protocol.md)** and process the input
2. **Append raw points** to the relevant brand's `discussion-log.md` (audit trail, never overwritten)
3. **Update curated working docs** -- multi-file routing: each point may update brand-identity.md, visual-identity.md, voice-identity.md, sitemap.md, a specific `pages/{page}.md`, or extras.md. A single point can update several files at once.
4. **Append round summary** to `session-log.md`
5. **Report back briefly:** what was extracted, which docs were updated, and the next recommended topic

The loop continues until all Must-have topics are covered, all Should-have topics have at least basic info, and the team member signals they're done (or moves to brief generation).

### Phase 2.5: Sitemap Trigger

As soon as the team member has discussed the page list and hierarchy, the sitemap is established. At that point:
1. Update `sitemap.md` with the page tree
2. **Create a stub file in `pages/`** for each page using the page.md template, with the page name filled in
3. Subsequent rounds that mention specific pages update the corresponding `pages/{page-name}.md` file

If the sitemap changes later (page added/removed), update `sitemap.md` and create/delete the corresponding page file.

### Phase 3: Coverage Review & Gap Closure

Before generating the brief:
1. Read all curated working docs for the brand
2. Check coverage against the priority list in [conversation-guide.md](references/conversation-guide.md)
3. Surface gaps as suggestions: "For {brand}, the brand identity is solid, but we still need: typography character, voice samples, copy direction for the About page. Want to do another round, or is this enough?"
4. Loop back into Phase 2 if needed

### Phase 4: Brand Brief Generation

When coverage is sufficient and the user confirms:

1. Read all curated working docs for the brand: `brand-identity.md`, `visual-identity.md`, `voice-identity.md`, `sitemap.md`, every file in `pages/`, and `extras.md`
2. Assemble `brand-brief.md` from the brand-brief template by inlining each section
3. Present the brief to the user for review
4. Incorporate feedback by updating the relevant working doc, then regenerating the brief (don't edit `brand-brief.md` directly -- keep it as a generated artefact)

### Phase 5: Stitch Prompts (OPTIONAL)

Only if the user explicitly asks. Stitch is no longer the default end of the workshop -- the brand brief is the deliverable.

If requested:
1. Load [google-stitch-prompts.md](references/google-stitch-prompts.md)
2. Confirm which pages to generate prompts for
3. For each page, generate a Stitch prompt and save to `stitch-prompts/{page-name}-v1.md` using the stitch-prompt template
4. Present prompts to the user for review
5. Iterate -- create v2, v3 as needed

## Output Structure

```
{project}/website-workshop/{client-name}/
├── session-log.md                       # chronological session-level log
└── brands/
    ├── {brand-1}/
    │   ├── discussion-log.md            # raw, append-only audit trail
    │   ├── brand-identity.md            # curated: who, values, story
    │   ├── visual-identity.md           # curated: colors, type, imagery
    │   ├── voice-identity.md            # curated: tone, personality, language
    │   ├── sitemap.md                   # curated: page tree
    │   ├── pages/                       # one file per page
    │   │   ├── homepage.md
    │   │   ├── about.md
    │   │   └── ...
    │   ├── extras.md                    # functionality, references, open questions
    │   ├── brand-brief.md               # generated aggregate (Phase 4)
    │   └── stitch-prompts/              # optional, only if requested (Phase 5)
    │       ├── homepage-v1.md
    │       └── ...
    └── {brand-2}/
        └── ... up to 5 brands
```

## When to Ask for Confirmation

Always ask before:
- Creating the initial directory structure (confirm client name and brand names)
- Establishing the sitemap (confirm page list before creating page stub files)
- Generating the brand brief (confirm coverage is sufficient)
- Generating Stitch prompts (confirm the user wants them, and which pages)
