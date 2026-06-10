# Component Extraction

> **When to read:** When processing a transcript that contains component-level content — typically follow-up calls where specific parts of the product are discussed in detail, or the second half of a first call where components are identified.

---

## What to Listen For

Component-level content in a transcript sounds like:

- **Functional detail** — "For the onboarding, we need...", "The dashboard should show...", "When someone wants to trade, they..."
- **How it should work** — "It should feel like...", "Similar to how [product] does it...", "The user clicks X and then sees Y..."
- **Technical approach** — "We could use [service] for that...", "We'd need an API for...", "The data comes from..."
- **Access and roles** — "Only admins can...", "Verified users get...", "Before they've completed KYC they can't..."
- **Risks and abuse** — "What if someone bots...", "The data might be stale...", "We need to comply with..."
- **Priority** — "The most important part is...", "We can't launch without...", "That's a nice-to-have..."

---

## Extraction Process

### Step 1: Check existing state

Before extracting, read:
1. The project's vision document — understand the overall context
2. The component map (`components.md`) — see what components have been identified already
3. Any existing component documents — avoid duplicating work

### Step 2: Identify which components are discussed

A single transcript may cover multiple components. List them:

```
Components discussed in this transcript:
1. Bloomberg Terminal — detailed discussion (functional requirements, data sources, UX)
2. Trading — mentioned briefly (linked to terminal, not discussed in depth)
3. Onboarding/KYC — some detail (compliance requirements, flow described)
```

Present this to the user and confirm: "I see discussion of these 3 components. Want me to extract all three, or focus on the ones with the most coverage?"

### Step 3: Extract per component

For each component with sufficient coverage, work through the 10 template sections conversationally.

**Section mapping — what to extract from the transcript:**

| Section | What to listen for |
|---------|-------------------|
| **1. What does it do?** | Description of the component's purpose, how users interact with it, what role it plays. **Consult the vision document's persona list** — determine which personas use this component and how each one interacts with it differently. The template requires a per-persona table showing usage patterns and needs. |
| **2. What needs to happen?** | Functional requirements ("users need to be able to..."), business rules ("trades under £10 are free"), edge cases ("what if the API is down"). |
| **3. Look and feel** | Design references ("like Bloomberg but modern"), UX principles ("must feel fast"), competitor analysis ("Robin Hood does onboarding like..."). |
| **4. How to solve it** | Build vs. buy vs. access decisions ("we'll use SportsRadar for data"), technology mentions ("we could use Stripe for payments"), rationale discussions. |
| **5. Data** | What data is needed ("team performance stats"), where it comes from ("SportsRadar API"), what's stored ("user research reports"), data freshness requirements. |
| **6. Access** | Who can use this component, role gating, verification requirements, different capability levels per role. |
| **7. Success metrics** | How to measure if this component is working. Often not discussed directly — extract from implications ("if nobody uses the research tool, the terminal has failed"). |
| **8. Dependencies** | References to other components ("the terminal feeds into trading"), external services, data flows between components. |
| **9. Priority** | Must-have vs. nice-to-have, launch requirements, sequencing discussions. |
| **10. Risks** | Abuse vectors, data quality issues, compliance concerns specific to this component. |

### Diagrams

When extracting component content, propose inline diagrams where they add clarity:
- **Section 1 (What does it do?)** — propose an ASCII tree of sub-components if they're emerging from the discussion
- **Section 2 (What needs to happen?)** — propose Mermaid flowcharts for key user/entity flows described in the transcript
- **Section 5 (Data)** — propose a Mermaid data flow diagram if data sources and flows are discussed
- **Section 8 (Dependencies)** — propose a Mermaid graph showing this component's connections to others

Reference the vision template's Diagrams section for format examples and the when-to-use table.

### Step 4: Surface sub-components

As you extract component detail, sub-components will become visible. The client often describes them without naming them: "they need to see team performance, and also historical data, and then there's the AI research bit..."

**Propose sub-component bucketing to the user:**

```
From the discussion about the Bloomberg Terminal, I can see these natural sub-components:
1. Match Browser — browsing/filtering upcoming matches
2. Match Detail — deep-dive into a specific match's data
3. AI Research Partner — conversational analysis tool
4. Research Library — saved reports

Does that match what you heard in the room? Any I've missed or mis-bucketed?
```

**Do NOT create sub-component documents at this stage.** Just list them in the component document's Sub-Components backfill table as **plain text** — one-line descriptions, "Collecting" status, **no wikilinks** (the sub-component docs don't exist yet, so a link would dangle).

---

## Handling Multiple Components Per Call

When a transcript covers multiple components:

1. Process them in order of coverage depth (most detail first)
2. For each component, note cross-references to other components (these become dependencies)
3. After processing all components, review the dependencies — are they consistent?
4. Update the component map (`components.md`) with any new components
5. Backfill the vision document — add any new components to the vision document's Components table with one-line descriptions and current status.

Update the vision document's Components table whenever new components are identified or component statuses change.

---

## When Sub-Components Emerge During Component Extraction

Often the client will naturally go deeper than component level. Signs you're hearing sub-component detail:

- Specific UI elements described ("there's a sidebar with filters and a main area with the data")
- Individual features within a component ("the research tool has a chat interface and can generate reports")
- Distinct data flows within a component ("the match data comes from the API but the user's saved research is separate")

Capture this detail but keep it in notes. Present it to the user as "potential sub-components" and let them decide whether to document them now or in a follow-up session.

---

## Gap Analysis Output

After extracting all components from the transcript:

```
## Component Gaps

### Bloomberg Terminal
- ✅ Sections 1-3: Good coverage
- ⚠️ Section 4 (How to solve it): Data provider discussed but visualisation approach unknown
- ❌ Section 7 (Success metrics): Not discussed
- ⚠️ Section 10 (Risks): Data latency risk mentioned but abuse prevention not discussed

### Onboarding/KYC
- ⚠️ Section 1: Basic purpose clear but detail thin
- ❌ Sections 2-9: Need a dedicated call for this component

### Questions for Next Call
- [Component-specific questions grouped by component]
```
