# Sub-Component Extraction

> **When to read:** When processing a transcript that contains sub-component detail — specific features within a component, entity journeys, data flows, or detailed UX discussions about a particular piece of a component.

---

## What to Listen For

Sub-component content in a transcript sounds like:

- **Specific features within a component** — "Within the terminal, there's the match browser part and then the detail view...", "The research tool needs a chat interface and..."
- **Entity journeys** — "The user goes to the matches, selects one, sees the data, then decides to...", "The agent receives the event and then..."
- **Detailed UX** — "When they click into a match, they should see the team stats at the top, then...", "The filters should include sport, league, date..."
- **Data specifics** — "The team performance data comes from SportsRadar but the user's saved research is stored internally..."
- **Edge cases in detail** — "What if they're looking at a match and it starts while they're researching?", "What if the data feed is 30 seconds behind?"

---

## Extraction Process

### Step 1: Check existing state

Before extracting, read:
1. The parent component document — understand what sub-components have been identified
2. Any existing sub-component documents — avoid duplicating
3. The vision document — keep the overall context in mind

### Step 2: Identify which sub-components are discussed

```
Sub-components discussed in this transcript (within Bloomberg Terminal):
1. Match Browser — detailed (filtering, browsing, match cards)
2. Match Detail — detailed (metrics display, data sources, layout)
3. AI Research Partner — mentioned (chat interface, report generation)
4. Research Library — briefly mentioned
```

### Step 3: Extract per sub-component

For each sub-component with sufficient coverage, work through the 8 template sections.

**Section mapping — what to extract:**

| Section | What to listen for |
|---------|-------------------|
| **1. What does it do?** | Specific purpose within the parent component. Which entities interact with it. Any access restrictions specific to this sub-component. |
| **2. What needs to happen?** | Granular functional requirements. Business rules that apply at this level. Specific edge cases. |
| **3. Entity journeys** | The core of sub-component extraction. Listen for: what triggers the journey (input), what steps the entity takes, what decision points exist, what the successful outcome is. Both user journeys (UI flows) and agent journeys (event processing). |
| **4. Look and feel** | OPTIONAL. Specific design direction for this sub-component. Reference products at the feature level ("the filters should work like Airbnb's"). UX principles. Skip entirely if no UI. |
| **5. Data requirements** | What data flows in, out, and is stored — from the experience perspective. "User puts in a team name, gets back performance data." Not schemas or models. |
| **6. Dependencies** | What this sub-component needs from siblings, parent component, or external services. What siblings need from it. |
| **7. Risks** | Specific risks to this sub-component. Abuse vectors, data quality issues, UX risks. Controls that should be built into the entity journeys. |
| **8. Priority** | Must-have or can come later. Sequencing relative to sibling sub-components. |

---

## Entity Journey Extraction

This is the most important part of sub-component extraction. Entity journeys are the buildable specs — they define exactly what gets implemented.

### Identifying journeys in a transcript

Clients describe journeys implicitly: "So the user goes to the matches page, they can filter by sport, they click on a match, they see all the stats..." This is a journey being described in natural language.

**Extract the journey structure:**

1. **Entity** — who or what is performing the journey? A user type? An agent? Both?
2. **Input / trigger** — what starts this journey? The user clicking something? An event arriving? A scheduled job?
3. **Steps** — what happens in sequence? What decision points exist? What branches?
4. **Outcome** — what is true when the journey completes successfully?
5. **Acceptance criteria** — what specific conditions must hold? These come from both explicit statements ("they need to see the win/loss record") and implicit requirements (if they see team stats, those stats must be current).

### Proposing journeys to the user

After extracting, present the journey with a Mermaid diagram:

```
I've extracted this journey from the transcript:

**Journey: User researches a match**
Entity: User (verified)
Input: User selects a specific match from the match browser
Outcome: User has enough information to decide whether to trade

Steps:
[Mermaid diagram]

Acceptance criteria:
- [ ] Team performance data displayed within 2 seconds of selection
- [ ] Historical data covers at least the current season
- [ ] User can see head-to-head stats for the two teams
- [ ] Data freshness indicator shows when data was last updated

Does this match what you heard? Anything to add or change?
```

### User journeys vs. agent journeys

**User journeys** have a UI component — the user sees something, clicks something, inputs something. The steps involve visual elements and interactions.

**Agent journeys** are event-driven — an event arrives, the agent processes it, produces an output. The steps involve data processing, API calls, and state changes. No UI involved.

**Hybrid journeys** combine both — a user triggers something, an agent does background processing, and the result appears in the UI. For example: "User asks the AI research partner a question → agent queries APIs → agent synthesises an answer → answer appears in the chat interface."

For hybrid journeys, document them as a single journey with clear handoff points between user and agent steps.

### Diagrams in Sub-Components

Entity journeys should always include Mermaid flowcharts (this is already part of the journey format). Beyond journeys, consider:
- **Section 1 (What does it do?)** — ASCII tree if this sub-component has internal structure
- **Section 5 (Data requirements)** — Mermaid data flow if the data picture is complex
- **Section 6 (Dependencies)** — Mermaid graph for sibling relationships

Reference the vision template's Diagrams section for format examples.

---

## When Sub-Components Need Further Decomposition

Sometimes a sub-component is too large to be a leaf node. Signs:

- Multiple distinct entity journeys that don't share state
- The sub-component has its own sub-parts that could be developed independently
- The user describes something that feels like "a product within a product"

If this happens, propose further decomposition:

```
The AI Research Partner feels like it might need its own sub-components:
1. Chat Interface — the conversation UI
2. Data Query Engine — the agent that queries APIs
3. Report Generator — the part that produces saved reports

Should we decompose it further, or keep it as one sub-component with multiple journeys?
```

Let the user decide. If they decompose further, the sub-component gets its own `sub-components/` directory and the recursive template applies.

---

## Backfilling After Extraction

After creating sub-component documents:

1. **Update the parent component's README.md** — add each new sub-component to the Sub-Components backfill table
2. **Add wikilinks** — the sub-component links UP to its parent component `[[../README]]`
3. **Cross-link siblings** — if sub-components depend on each other, add links in their Dependencies sections
4. **Update the components README** — if the component's status changed (e.g., from "Collecting" to "Defined")

---

## Gap Analysis Output

```
## Sub-Component Gaps (Bloomberg Terminal)

### Match Browser
- ✅ Entity journeys: 2 journeys fully defined with acceptance criteria
- ⚠️ Look and feel: Design direction stated but no reference products
- ❌ Data requirements: Filter categories discussed but data sources unknown

### AI Research Partner
- ⚠️ Entity journeys: 1 journey outlined but steps are vague
- ❌ Data requirements: Which APIs does the agent query? Not discussed
- ❌ Risks: No discussion of rate limiting, cost per query, hallucination risk

### Questions for Next Call
- What specific data does the match browser's sport filter use? Is it a fixed list or dynamic from the API?
- How many API queries should the AI research partner be allowed per user per day?
- What happens if the AI research partner gives wrong information and a user trades on it? Liability?
```
