# Extraction Protocol

> **When to read:** Every time the user pastes transcription text, meeting notes, direct answers, or any other input that needs processing.

This protocol defines how to extract structured information from unstructured workshop input and route it to the right files. The skill operates on a **two-layer model**: raw points always go to a per-brand append-only audit log, and curated working documents get progressively refined from those raw points using **multi-file routing**.

---

## Two-Layer Model

| Layer | File(s) | Mode | Purpose |
|-------|---------|------|---------|
| **Raw layer** | `discussion-log.md` (per brand) | Append-only | Audit trail, source of truth, every extracted point lives here |
| **Curated layer** | `brand-identity.md`, `visual-identity.md`, `voice-identity.md`, `sitemap.md`, `pages/{page}.md`, `extras.md` | Progressively refined | Structured working documents -- the current understanding of the brand |

The discussion log is the source of truth. The curated documents are the current view, derived from the raw points. If the curated docs ever feel out of sync, you can trace back to the discussion log.

---

## Processing Steps

When the user provides unstructured input (transcription, notes, brain dump, direct answers):

### Step 1: Read and Understand

Read the full input before extracting anything. Understand:
- Which brand(s) are being discussed
- The flow of conversation (context matters for ambiguous points)
- Whether the speaker is stating preferences, asking questions, or giving background

### Step 2: Extract Key Points

For each meaningful piece of information, extract:
- **The point itself** -- a concise, clear statement of the preference/requirement/decision
- **The brand(s)** -- which brand it applies to (may be multiple, or "all brands")
- **The topic** -- which topic from `conversation-guide.md` it falls under
- **Confidence** -- Decision (firm), Preference (leaning), or Mention (offhand)

Rules:
- Prefer the client's exact words over paraphrasing when the phrasing is specific
- Capture specific values (hex codes, font names, page names, sample phrases) exactly
- Note contradictions or ambiguity -- flag these for follow-up
- Ignore filler, pleasantries, and off-topic discussion
- If a point applies to all brands in the group, note it once and mark as "all brands"

### Step 3: Append to Raw Layer (`discussion-log.md`)

For each extracted point, append to the relevant brand's `discussion-log.md` under the topic heading:

```markdown
### [Topic name]

- [Key point in client's words where possible]
  - **Source:** [Transcription / Meeting notes / Direct answer] - Round [N]
  - **Confidence:** [Decision / Preference / Mention]
  - **Routed to:** [List of curated files updated by this point]
```

The `Routed to` field is the bridge between the two layers -- it tells you which curated files were updated from this point.

### Step 4: Multi-File Route to Curated Layer

This is the critical step. **A single extracted point can update multiple curated documents.** Identify all the curated files affected, and update each one.

**Routing rules:**

| If the point is about... | Update... |
|--------------------------|-----------|
| Who they are, values, story, mission, audience | `brand-identity.md` |
| Differentiation from sibling brands | `brand-identity.md` (and cross-reference siblings) |
| Colors (hex, palette, mood) | `visual-identity.md` (Colors section) |
| Typography (fonts, weight, character) | `visual-identity.md` (Typography section) |
| Imagery, photography, illustration, icons | `visual-identity.md` (Imagery section) |
| Tone of voice, personality, sample phrases | `voice-identity.md` |
| Page list, hierarchy, depth | `sitemap.md` (and create/update page stub files) |
| Content/sections/CTAs/copy direction for a specific page | `pages/{page-name}.md` |
| Page-specific layout requirement ("calendar at bottom") | `pages/{page-name}.md` (Required layout elements) |
| Page-specific functionality | `pages/{page-name}.md` (Page-specific functionality) |
| Cross-cutting functionality (forms, integrations) | `extras.md` (Functionality section) |
| Reference websites or anti-references | `extras.md` (References section) |
| Open questions, contradictions, things to clarify | `extras.md` (Open questions section) |

**Cross-cutting points:** A single point may affect multiple curated files. Examples:

- *"We want to feel premium and understated"* →
  - `brand-identity.md` (positioning/feel)
  - `visual-identity.md` (aesthetic direction notes)
  - `voice-identity.md` (tone notes)
- *"Our audience is overwhelmed founders, so we want to feel calm and reassuring"* →
  - `brand-identity.md` (audience + brand feel)
  - `voice-identity.md` (tone)
  - `visual-identity.md` (aesthetic notes)
- *"The homepage needs a hero with a video and our tagline 'Built for builders'"* →
  - `pages/homepage.md` (sections, copy direction, functionality)
  - `voice-identity.md` (sample tagline -- captures their voice)
- *"We hate corporate stock photography"* →
  - `visual-identity.md` (imagery direction)
  - `extras.md` (anti-references)

When routing, **don't pick one file** -- update all the relevant ones. Note in the discussion log which files were updated so the trail is clear.

### Step 5: Update Sitemap & Page Files

**Sitemap trigger:** If the input establishes or updates the page list, update `sitemap.md` AND create stub files in `pages/` for any new pages using the `page.md` template. Don't wait for a separate phase -- do it as soon as the page list is captured.

**Per-page updates:** When the input talks about a specific page, update that page's file in `pages/`. If the page doesn't exist yet (sitemap not yet established), capture the points in `discussion-log.md` and create the page file when the sitemap is set.

### Step 6: Append Round Summary to `session-log.md`

Add a session-level entry:

```markdown
### Round [N] - [Timestamp or sequence]
**Source:** [Description of input -- "transcription from client meeting", "direct answers", etc.]
**Brands affected:** [Brand 1, Brand 2]
**Curated files updated:**
- [Brand 1]: brand-identity.md, visual-identity.md, pages/homepage.md
- [Brand 2]: voice-identity.md
**Key takeaways:**
- [Brand 1]: [1-2 line summary]
- [Brand 2]: [1-2 line summary]
**Gaps closed:** [Topics that moved from gap to covered]
**New gaps surfaced:** [Any new questions or contradictions]
```

### Step 7: Report Back

Provide a brief summary to the user:
1. Number of key points extracted
2. Which brands received updates
3. Which curated files were updated (per brand)
4. Top 3 remaining gaps per brand
5. Recommended next topic + 3-5 angles to explore (pull from `conversation-guide.md`)

---

## Handling Ambiguity

When the input is unclear:

| Situation | Action |
|-----------|--------|
| Can't tell which brand | Log under "all brands" with a flag, note in `extras.md` Open questions |
| Contradicts earlier point | Log both, mark as "needs resolution" in the curated doc, add to `extras.md` Open questions |
| Vague preference ("something modern") | Log as-is, add follow-up question to `extras.md` Open questions |
| Off-topic or irrelevant | Skip, don't log |
| Multiple people speaking with disagreement | Try to identify the decision-maker's view; note disagreements in `extras.md` Open questions |
| Page mentioned but not yet in sitemap | Log to `discussion-log.md`, hold the per-page detail until sitemap is set, then port over |

---

## Multi-Brand Routing

When the client group has shared requirements across brands:
- Apply the point to **each affected brand's** discussion log AND curated docs
- Mark in each brand's discussion log: `**Shared with:** [Brand A, Brand B]`
- When generating brand briefs, the shared elements will appear in each brief naturally (with cross-reference notes)

---

## Transcription Noise

Voice transcriptions often contain:
- Filler words and false starts -- ignore these
- Misheard words -- use context to infer the correct meaning, flag if unsure
- Incomplete sentences -- capture the intent if clear, skip if not
- Speaker overlap -- separate into distinct points where possible
- Background noise artefacts -- skip

---

## Curated Document Update Patterns

Curated documents are **structured working docs**, not append-only logs. When updating them:

- **Replace placeholder text** the first time a section gets info (e.g., replace `[Description]` with the actual content)
- **Refine existing text** when new info adds detail (don't append; integrate)
- **Note conflicts inline** if a new point contradicts existing content (e.g., `Primary color: navy #1B2A4A [previously suggested gold; client confirmed navy in round 4]`)
- **Keep section structure intact** -- don't remove headings even if a section is empty

The goal is that at any point in the session, reading any curated doc gives the current best understanding of that dimension of the brand.
