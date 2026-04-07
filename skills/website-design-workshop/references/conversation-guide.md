# Conversation Guide

> **When to read:** At the start of a workshop session, before suggesting the next topic to the team member, and when surfacing coverage gaps.

This guide tells the skill what topics to drive the workshop through, in what order, and what angles to surface for the team member to explore with the client. The skill is the **facilitator** -- it names the topic and suggests angles. The team member runs the actual conversation.

---

## Topic Priorities

Topics are split into three tiers. The skill should chase coverage on **Must** topics aggressively, ensure **Should** topics get at least basic coverage, and treat **Opportunistic** topics as catch-as-catch-can (only capture when the client volunteers, never pursue in the abstract).

### Must (chase coverage)

| # | Topic | Routes to |
|---|-------|-----------|
| 1 | Brand identity -- who they are, what they stand for | brand-identity.md |
| 2 | Target audience | brand-identity.md |
| 3 | Brand differentiation (multi-brand only) | brand-identity.md |
| 4 | Color scheme | visual-identity.md |
| 5 | Typography | visual-identity.md |
| 6 | Voice & copywriting style | voice-identity.md |
| 7 | Sitemap (page list & hierarchy) | sitemap.md, pages/ |
| 8 | Per-page detail (sections, key messages, CTAs) | pages/{page}.md |

### Should (cover if relevant)

| # | Topic | Routes to |
|---|-------|-----------|
| 9 | Imagery & visual aesthetic | visual-identity.md |
| 10 | Reference websites | extras.md |
| 11 | Functionality & integrations | extras.md, pages/{page}.md |
| 12 | Navigation structure | sitemap.md (often falls out of sitemap naturally) |

### Opportunistic (capture if mentioned, never pursue)

| # | Topic | Routes to |
|---|-------|-----------|
| 13 | Page-specific layout requirements | pages/{page}.md (e.g. "calendar at bottom") |
| 14 | Responsive / mobile notes | extras.md or pages/{page}.md (only if flagged) |

**Dropped from primary tracking:** Layout preferences in the abstract. Never ask "do you prefer dense or spacious layouts?" -- only capture layout when the client points to a specific requirement.

---

## Recommended Topic Order

The skill should drive topics in roughly this order. It's flexible -- if the team member's input lands on a different topic naturally, follow that thread, but always know what the next gap is.

1. **Brand identity & audience** (1, 2, 3) -- foundation. Everything else hangs off this.
2. **Visual identity start: colors, typography** (4, 5)
3. **Voice & copywriting style** (6)
4. **Sitemap** (7) -- once this is set, page stub files get created in `pages/`
5. **Per-page detail** (8) -- one page at a time, working through the sitemap
6. **Imagery & aesthetic** (9) -- often woven in naturally with visual identity
7. **Functionality, integrations, references** (10, 11)
8. **Navigation** (12) -- often resolved by this point
9. **Coverage review** -- check gaps, loop back as needed

---

## Suggested Opening

When starting a session, present this to the team member:

> "I'll guide us through the topics in priority order. For each one, I'll suggest some angles you could explore with the client -- you don't need to use the exact wording, just have a natural conversation and bring back whatever you get. I'll process it, route it to the right place, and tell you what to tackle next.
>
> We'll start with **brand identity** -- the foundation. Everything else builds on understanding who this brand really is."

Then load the brand identity angles below.

---

## Angles to Explore by Topic

For each topic, the skill offers 3-5 angles the team member could explore. These are conversation starters, not scripts.

---

### 1. Brand Identity -- Who They Are

**Why this matters:** This is the soul of the brand. Without this, every visual and voice decision downstream is arbitrary. Go deep here.

**Angles to explore:**
- What does this brand actually stand for? What are its values?
- What do they want to put out into the world -- what's the bigger purpose?
- If the brand were a person, how would they describe themselves?
- What's the origin story or founding moment? Why does this brand exist?
- What feeling do they want people to walk away with after encountering them?
- What would it mean for this brand to "win" -- what does success look like culturally, not just commercially?

**Routes to:** `brand-identity.md`

---

### 2. Target Audience

**Why this matters:** The brand's voice, visual choices, and page structure all need to land with a specific audience. "Everyone" is not an audience.

**Angles to explore:**
- Who is the primary customer? Be specific -- demographics, psychographics, profession, life stage
- What problem does this brand solve for them?
- What does the audience already believe about the category?
- Where does the audience currently look for solutions? Who are they comparing to?
- What's the audience's emotional state when they arrive at the website?

**Routes to:** `brand-identity.md`

---

### 3. Brand Differentiation (Multi-Brand Only)

**Why this matters:** When a client has multiple brands in a group, each brand needs a clear reason to exist separately. Otherwise, the visual and voice choices blur together.

**Angles to explore:**
- How does this brand sit within the wider group?
- What does this brand do that the sibling brands don't?
- Is the audience overlap deliberate, or are they targeting completely different people?
- If a customer chose this brand over a sibling, what would tip the decision?
- Are there shared elements (color, type, voice) that should hold across the group, and what's unique per brand?

**Routes to:** `brand-identity.md` (and noted in each sibling brand's identity for cross-reference)

---

### 4. Color Scheme

**Why this matters:** Colors carry meaning before any words are read. Get specific (hex codes, named palettes) wherever possible.

**Angles to explore:**
- Are there existing brand colors? Hex codes, Pantone, or just "the orange we use"?
- What feelings should the palette evoke -- warmth, calm, energy, trust, luxury?
- Are there colors to avoid -- competitor associations, cultural concerns, anything that's been ruled out?
- Should the palette feel saturated and bold, or muted and refined?
- How many accent colors do they need beyond the primary?

**Routes to:** `visual-identity.md`

---

### 5. Typography

**Why this matters:** Type does the heavy lifting on personality. Heading style and body style can be very different choices.

**Angles to explore:**
- Are there existing brand fonts or licenses they're committed to?
- Should headings feel impactful and bold, or elegant and refined?
- Serif, sans-serif, or a deliberate mix?
- For body text, what matters more -- maximum readability or distinctive character?
- Any specific typefaces or font references they admire?
- How do they want the type to feel -- editorial, technical, friendly, premium?

**Routes to:** `visual-identity.md`

---

### 6. Voice & Copywriting Style

**Why this matters:** Voice is what the brand sounds like in writing. It's the difference between "Get in touch" and "Drop us a line" and "Schedule a Consultation". Get samples if possible.

**Angles to explore:**
- Formal or conversational? Where on the spectrum?
- Technical jargon or plain language? Does the audience expect industry vocabulary?
- Short punchy sentences, or flowing narrative?
- First person ("we believe") or third person ("the company")?
- What personality should come through -- witty, warm, authoritative, playful, calm?
- Any phrases or words they always use? Any words they refuse to use?
- Can they share a piece of writing that sounds like them?

**Routes to:** `voice-identity.md`

---

### 7. Sitemap -- Pages & Hierarchy

**Why this matters:** This is the spine of the website. As soon as this is established, the skill creates a stub file for each page in `pages/`, and the conversation moves into per-page detail.

**Angles to explore:**
- What pages must the site have?
- Are there sections that need sub-pages (e.g., Services -> individual service pages)?
- How deep should the site go -- 2 levels, 3 levels?
- Is there a blog, news, or content section?
- Any pages that need gated content, login, or restricted access?
- Are any pages must-haves vs nice-to-haves?

**Routes to:** `sitemap.md`. **Trigger:** As soon as the page list is captured, create stub files in `pages/` for each page using the `page.md` template.

---

### 8. Per-Page Detail

**Why this matters:** The sitemap tells you what pages exist; this is where you actually understand what each page is for and what goes on it. This is where most of the volume of the brief lives. Walk through each page individually.

**For each page, angles to explore:**
- What is this page actually for? What should the visitor do or feel after seeing it?
- Who specifically is this page aimed at? (Same as the brand audience or a sub-segment?)
- What are the key messages -- what must the visitor walk away knowing?
- What sections should appear, in what order? Hero, then what?
- What's the primary call-to-action? Are there secondary CTAs?
- Any specific content blocks the client has in mind? Specific copy, headline angles?
- Any layout requirements they've called out (e.g. "image hero", "calendar at the bottom")?
- Any page-specific functionality (forms, embeds, integrations)?

**Routes to:** `pages/{page-name}.md`

---

### 9. Imagery & Visual Aesthetic

**Why this matters:** Photography vs illustration, abstract vs literal, candid vs staged -- all shape how the brand feels visually.

**Angles to explore:**
- Photography-heavy or illustration-based?
- Do they have existing photography or assets to work with?
- Abstract and artistic, or clean and corporate?
- What style of icons -- line icons, filled, custom illustrations, none at all?
- Should images feel candid and human, or polished and editorial?

**Routes to:** `visual-identity.md`

---

### 10. Reference Websites

**Why this matters:** References anchor abstract conversations. "Modern" means nothing; pointing at a specific site means everything.

**Angles to explore:**
- What 2-3 websites do they admire? (Any industry -- the design choices matter more than the category)
- What specifically do they like about each?
- Are there competitor sites they want to differentiate from?
- Any sites that represent what they DON'T want?

**Routes to:** `extras.md`

---

### 11. Functionality & Integrations

**Why this matters:** Forms, e-commerce, booking, CMS, and integrations all shape build complexity and need to be flagged early.

**Angles to explore:**
- Does the site need any forms (contact, booking, application, lead capture)?
- E-commerce requirements?
- Blog or content management needs?
- Third-party integrations -- CRM, analytics, chat, calendars, payment?
- Multi-language requirements?

**Routes to:** `extras.md` for cross-cutting items, `pages/{page}.md` for page-specific functionality.

---

### 12. Navigation Structure

**Why this matters:** Often this resolves itself once the sitemap is clear. Only press if there's anything unusual.

**Angles to explore:**
- Single top nav, mega menu, or something more unusual?
- Should the nav be sticky/fixed?
- What goes in the footer?
- Are there CTAs that need to be always visible (sticky button, banner)?
- How should users flow through the site? Is there an intended journey?

**Routes to:** `sitemap.md` (navigation notes section)

---

## Coverage Gap Detection

After processing each round of input, check coverage against the priority tiers:

- **Must topics:** Are all 8 covered with substantive info? If not, flag the gaps.
- **Should topics:** Have they been touched at all? If not, mention them as candidates for the next round.
- **Opportunistic topics:** Don't track these as gaps -- they only count if the client mentioned them.

When surfacing gaps to the team member, frame as a suggestion + offer:

> "For {brand}, the brand identity and color scheme are looking solid. We still need:
> - **Typography** -- haven't touched character, weight, or any references
> - **Voice** -- nothing yet on tone or sample phrases
> - **Page-by-page** -- sitemap is set, but we haven't dug into the homepage yet
>
> Want to tackle typography next? Here are some angles to explore: ..."
