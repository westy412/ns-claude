---
name: website-design-workshop
description: Run website design workshops to capture brand requirements across multiple brands. Guides consultations, extracts key points from voice transcriptions, builds structured brand briefs, and generates Google Stitch prompts per page. Use when planning a website design for a client with one or more brands.
disable-model-invocation: true
argument-hint: "[client-name]"
---

> **Invoke with:** `/website-design-workshop [client-name]` | **Keywords:** website workshop, design consultation, brand brief, stitch prompt, website planning

Guide a website design workshop session for a client with one or more brands (up to 5). Captures requirements through iterative conversation, extracts key points from transcriptions, and produces structured brand briefs with Google Stitch prompts.

**Input:** Client name, brand names, and iterative conversation/transcription dumps
**Output:** Per-brand briefs, discussion logs, Stitch prompts (one per page), and an overall session log

## When to Use This Skill

Use this skill when:
- Running a website design consultation or workshop
- Capturing brand requirements for a new website project
- Processing meeting transcriptions into structured design briefs
- Generating Google Stitch prompts from design requirements

**Skip this skill when:**
- Implementing an already-defined design (use `frontend-design` instead)
- Just need a quick mockup with no consultation process

## Reference Files

Load these just-in-time based on the current phase:

| Topic | Reference File | When to Load |
|-------|---------------|--------------|
| Conversation topics & questions | [conversation-guide.md](references/conversation-guide.md) | At session start and when suggesting topics |
| Processing transcriptions | [extraction-protocol.md](references/extraction-protocol.md) | When user pastes transcription or meeting notes |
| Crafting Stitch prompts | [google-stitch-prompts.md](references/google-stitch-prompts.md) | When generating Stitch prompts for a brand |

## Templates

| Template | Purpose | When to Use |
|----------|---------|-------------|
| [session-log.md](templates/session-log.md) | Overall session log | Created at session start |
| [discussion-log.md](templates/discussion-log.md) | Per-brand discussion log | Created per brand at session start |
| [brand-brief.md](templates/brand-brief.md) | Structured brand brief | Generated when enough data is captured |
| [stitch-prompt.md](templates/stitch-prompt.md) | Individual Stitch prompt | Generated per page per brand |

## Key Principles

1. **Extract, don't interrogate** -- The team member drives the client conversation. This skill processes what comes back, not scripts the meeting.
2. **Continuous extraction** -- Every input gets processed immediately. Key points are extracted, routed to the right brand, and logged.
3. **Track coverage gaps** -- Always know what's been discussed vs what's missing per brand. Surface gaps as suggestions.
4. **One Stitch prompt per page** -- Each page gets its own prompt file. Store in a directory for versioning and iteration.
5. **Build up, don't overwrite** -- Discussion logs are append-only. Brand briefs are progressively refined.

## Session Flow

### Phase 1: Setup

1. Greet the user and ask for the client name (or use `$ARGUMENTS` if provided)
2. Ask how many brands and their names
3. Create the output directory structure:

```
{project}/website-workshop/{client-name}/
├── session-log.md
├── brands/
│   ├── {brand-1}/
│   │   ├── discussion-log.md
│   │   ├── brand-brief.md
│   │   └── stitch-prompts/
│   ├── {brand-2}/
│   │   └── ...
```

4. Initialise session-log.md and per-brand discussion-log.md from templates
5. Load [conversation-guide.md](references/conversation-guide.md) and present suggested talking points

### Phase 2: Conversation & Extraction (iterative)

This phase loops until the user signals they're done:

1. **User provides input** -- transcription, meeting notes, or direct answers
2. **Load [extraction-protocol.md](references/extraction-protocol.md)** and process the input:
   - Extract key points
   - Route each point to the relevant brand(s)
   - Append to the brand's discussion-log.md
   - Append summary to session-log.md
3. **Report what was captured** -- brief summary of extracted points per brand
4. **Surface coverage gaps** -- check what topics are still missing per brand
5. **Suggest next topics** -- based on gaps, suggest what to discuss next

### Phase 3: Brand Brief Generation

When enough data is captured for a brand (or user requests it):

1. Read the brand's discussion-log.md
2. Generate/update brand-brief.md from the [brand-brief.md](templates/brand-brief.md) template
3. Present the brief to the user for review
4. Incorporate feedback

### Phase 4: Stitch Prompt Generation

When a brand brief is solid (or user requests prompts):

1. Load [google-stitch-prompts.md](references/google-stitch-prompts.md)
2. For each page in the brand's sitemap, generate a Stitch prompt
3. Save each prompt to `stitch-prompts/{page-name}-v1.md` using the [stitch-prompt.md](templates/stitch-prompt.md) template
4. Present prompts to the user for review
5. Iterate -- create v2, v3 as needed

## Output Structure

```
{project}/website-workshop/{client-name}/
├── session-log.md              <- Chronological log of everything discussed
├── brands/
│   ├── {brand-1}/
│   │   ├── discussion-log.md   <- Running key points for this brand
│   │   ├── brand-brief.md      <- Structured brief (colors, typography, sitemap, etc.)
│   │   └── stitch-prompts/
│   │       ├── homepage-v1.md
│   │       ├── homepage-v2.md  <- Iterations
│   │       ├── about-v1.md
│   │       └── ...
│   ├── {brand-2}/
│   │   └── ...
│   └── ...up to 5 brands
```

## When to Ask for Feedback

Always ask before:
- Creating the initial directory structure (confirm brand names)
- Finalising a brand brief
- Generating Stitch prompts (confirm which pages to generate for)
