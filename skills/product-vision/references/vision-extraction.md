# Vision Extraction

> **When to read:** When processing a transcript that contains vision-level content — typically the first call with a client, or any conversation that covers what the product is, who it's for, and why it exists.

---

## What to Listen For

Vision-level content in a transcript sounds like:

- **What are you building?** — "We want to build a...", "The idea is...", "What we're trying to create is..."
- **Who is it for?** — "Our target audience is...", "The users would be...", "The kind of person who..."
- **Why?** — "The reason we're doing this is...", "The opportunity is...", "What's happening in the market is..."
- **Revenue** — "The business model is...", "We'd make money by...", "The pricing would be..."
- **Competition** — "Nobody else does...", "The closest thing is...", "What [competitor] does wrong is..."
- **Constraints** — "We have to comply with...", "We're already using...", "The budget is..."
- **Existing state** — "We've already got...", "We built a prototype that...", "There's a waitlist of..."

Clients will NOT speak in the order of the template. They'll jump between topics, go on tangents, and return to earlier points. Extract everything first, then map to sections.

---

## Extraction Process

### Step 1: Read the full transcript

Read the entire transcript before extracting anything. Build a mental model of what was discussed, what level of detail exists, and where the gaps are.

### Step 2: Identify coverage per section

For each of the 8 vision sections, note whether the transcript has:
- **Good coverage** — enough to draft the section with confidence
- **Partial coverage** — some information but gaps remain
- **No coverage** — section wasn't discussed at all

Present this coverage map to the user before starting extraction:

```
Coverage from this transcript:
✅ 1. What are you building? — good coverage
✅ 2. Who are you building it for? — good coverage, 2 personas identifiable
⚠️  3. Why are you building it? — partial, business opportunity mentioned but motivation unclear
⚠️  4. Alternatives — partial, one competitor named
❌ 5. How does it make money? — not discussed
⚠️  6. Constraints — partial, regulatory mentioned briefly
❌ 7. What exists today? — not discussed
❌ 8. Risks — not discussed
```

### Step 3: Extract section by section

Work through each section conversationally:

**For sections with good coverage:**
- Present the extracted content with key quotes from the transcript
- Ask the user to confirm or correct
- Ask if there's anything they'd add from their in-the-room context

**For sections with partial coverage:**
- Present what you found
- Identify the specific gaps
- Ask: "Do you know the answer to this from the conversation, or is it a question for the next call?"

**For sections with no coverage:**
- Flag it explicitly: "This wasn't discussed in the transcript at all."
- Ask: "Do you have a view on this, or should we add it to questions for next time?"

### Step 4: Component identification

If the transcript contains enough vision-level content, attempt to identify the high-level components:

- Read through the "What are you building?" narrative
- Ask: "In order to deliver this vision to these personas, what functional parts need to exist?"
- Propose an initial component list
- Let the user confirm, modify, or expand

**Do NOT create component documents yet.** Just list them in the vision document's Components backfill table with one-line descriptions and "Collecting" status — as **plain text** (no wikilinks until the component docs exist, or a link will dangle).

---

## Template Mapping

The vision template has 8 sections. Here's what goes where:

| Section | What to extract from transcript |
|---------|-------------------------------|
| **1. What are you building?** | The product description. One-liner first, then the full narrative. Look for: what it does, how people use it, what the core experience is, what form factor (web/mobile/platform). Also look for scope boundaries — what it ISN'T. |
| **2. Who are you building it for?** | Personas. Look for: descriptions of the target user, their demographics, what they currently do, what motivates them, what they need vs. want, what frustrates them about current alternatives, what would make them switch. Each distinct user type is a separate persona. |
| **3. Why are you building it?** | Business case. Look for: market opportunity, timing (why now), the client's personal motivation, what happens if they don't build it. |
| **4. What makes this better?** | Competitive positioning. Look for: named competitors, what they do well/badly, how this product is structurally different (not just "better"), any unfair advantages. |
| **5. How does it make money?** | Revenue model. Look for: pricing mechanics, who pays, primary vs. secondary revenue streams. |
| **6. Constraints** | Fixed boundaries. Look for: required tech stack, regulatory requirements, compliance standards (SOC2, ISO 27001, FCA, KYC/AML), existing platform commitments, non-negotiable decisions. |
| **7. What exists today?** | Starting point. Look for: existing systems, user bases, data sets, previous work, branding assets. |
| **8. Risks** | Threats. Look for: abuse potential, data quality concerns, compliance risks, UX risks. Often not discussed directly — extract from implications of other content. |

### Diagrams

When extracting vision content, look for opportunities to propose inline diagrams:
- **Section 1 (What are you building?)** — if the narrative describes a core user loop or how parts connect, propose a Mermaid flowchart
- **Section 2 (Who are you building it for?)** — if there are multiple personas with different paths, propose an ASCII hierarchy
- **Section 4 (Alternatives)** — if the competitive landscape has clear positioning, propose a simple comparison diagram

Don't force diagrams. Only propose them when they'd communicate structure more clearly than text. Reference the vision template's Diagrams section for format guidance.

---

## Common Patterns in First Calls

**The client oversells the vision.** They describe the fully mature product, not the MVP. Extract the full vision but note to the user: "This sounds like the long-term destination. For the initial build, we'll need to scope down — which components are must-have at launch?"

**The client speaks in solutions, not problems.** "We need a dashboard with filters and charts." Push the user to help translate back to problems: "What problem is the dashboard solving? What does the user need to know or decide?"

**Personas are implied, not stated.** The client says "the user" but actually means 2-3 different types of user. If you detect different usage patterns ("some people will just want to..." and "the power users will..."), propose splitting into separate personas.

**Competitive analysis is biased.** The client will describe competitors negatively. That's useful for differentiation but may not be accurate. Flag to the user: "The client says [competitor] doesn't do X — is that actually true? Worth verifying."

---

## Gap Analysis Output

After extraction, produce a clear gap list grouped by section:

```
## Gaps — Questions for Next Call

### Section 2: Who are you building it for?
- We identified the primary persona (trader) but: what about admin users? Who manages the platform?
- What's the expected age range and income level of the target user?

### Section 5: How does it make money?
- Revenue model not discussed at all. Key question: commission per trade, subscription, or hybrid?

### Section 8: Risks
- Not discussed. Suggest asking: "What are you most worried about going wrong? How could users game this?"
```

Each gap should be a specific question, not a vague "need more info." The questions should be ready to ask verbatim in the next call.
