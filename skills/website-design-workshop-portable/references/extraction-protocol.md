# Extraction Protocol

> **When to read:** When the user pastes transcription text, meeting notes, or any unstructured input that needs processing.

This protocol defines how to extract structured information from unstructured workshop input and route it to the correct brand documents.

---

## Processing Steps

When the user provides unstructured input (transcription, notes, brain dump):

### Step 1: Read and Understand

Read the full input before extracting anything. Understand:
- Which brand(s) are being discussed
- The flow of conversation (context matters for ambiguous points)
- Whether the speaker is stating preferences, asking questions, or giving background

### Step 2: Extract Key Points

For each meaningful piece of information, extract:
- **The point itself** -- a concise, clear statement of the preference/requirement/decision
- **The topic** -- which category from the conversation guide it falls under
- **The brand** -- which brand it applies to (may be multiple, or "all brands")
- **Confidence** -- is this a firm decision, a preference, or an offhand mention?

Rules:
- Prefer the client's words over paraphrasing when the phrasing is specific
- Capture specific values (hex codes, font names, page names) exactly
- Note contradictions or ambiguity -- flag these for follow-up
- Ignore filler, pleasantries, and off-topic discussion
- If a point applies to all brands in the group, note it once and mark as "all brands"

### Step 3: Route to Brand Documents

For each extracted point:

1. **Append to the brand's discussion-log.md:**

```markdown
### [Topic] - Entry [N]
- [Key point]
- [Key point]
**Source:** [Transcription / Meeting notes] - [Date or sequence number]
**Confidence:** [Decision / Preference / Mention]
```

2. **Append summary to session-log.md:**

```markdown
### Entry [N] - [Timestamp or sequence]
**Source:** [Description of input]
**Brands affected:** [Brand 1, Brand 2]
**Key points:**
- [Brand 1]: [Brief summary of what was captured]
- [Brand 2]: [Brief summary of what was captured]
**Gaps identified:** [Any new gaps or follow-up needed]
```

### Step 4: Update Coverage Status

After routing, update the coverage checklist in each affected brand's discussion log:
- Mark topics as covered, partially covered, or still pending
- Note which topics got new information this round

### Step 5: Report Back

Provide a brief summary to the user:
1. Number of key points extracted
2. Which brands received new information
3. What topics were covered
4. What's still missing (top 3 gaps per brand)
5. Suggested follow-up questions for the next round

---

## Handling Ambiguity

When the input is unclear:

| Situation | Action |
|-----------|--------|
| Can't tell which brand | Log under "all brands" with a flag to clarify |
| Contradicts earlier point | Log both, mark as "needs resolution", flag to user |
| Vague preference ("something modern") | Log as-is, add follow-up question to clarify |
| Off-topic or irrelevant | Skip, don't log |
| Multiple people speaking | Try to identify the decision-maker's view, note disagreements |

---

## Multi-Brand Routing

When the client group has shared requirements across brands:
- Log shared points in each relevant brand's discussion log
- Mark as "shared across [Brand A, Brand B]" so it's clear this wasn't brand-specific
- When generating brand briefs, note which requirements are shared vs unique

---

## Transcription Noise

Voice transcriptions often contain:
- Filler words and false starts -- ignore these
- Misheard words -- use context to infer the correct meaning, flag if unsure
- Incomplete sentences -- capture the intent if clear, skip if not
- Speaker overlap -- separate into distinct points where possible
- Background noise artefacts -- skip
