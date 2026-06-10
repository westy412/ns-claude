# Component Template

## About This Document

This template defines the structure for a **component document** — a detailed description of one major functional part of a product. Components are identified by decomposing the vision document: "in order to deliver this vision to these personas, what functional parts need to exist?" Each component gets its own document following this structure.

**Where it sits in the hierarchy:**
- The **vision document** describes the overall product — what it is, who it's for, why it exists. It sits above all components.
- The **component map** (`components/components.md`) lists all components and their relationships. It routes to individual component documents.
- **This document** describes one component in enough detail to identify sub-components and begin building.
- **Sub-component documents** live below this, in a `sub-components/` folder within this component's directory. They follow a similar structure but scoped to a smaller unit.
- **Entity journeys, look and feel, and data requirements** live at the leaf level — the smallest unit that doesn't decompose further.

**When this document is complete enough**, the component can enter the development workflow (spec generation → implementation). The test: could an agent read this document and produce a spec without needing to ask clarifying questions?

**Who fills this in:** The client-facing and engineering roles together. The client-facing person contributes what the client needs and the business context. The engineering person contributes how to solve it and the technical trade-offs. Sections 1-3 lean client-facing. Section 4-5 lean engineering. Sections 6-9 are shared.

---

# [Project Name] — [Component Name]

> **Vision:** [[vision]]
> **Date:** ___
> **Status:** Collecting | Defined | Ready for build | In build | Complete
> **Owner:** ___
> **Sources:** _[[meetings/YYYY-MM-DD-slug]]_

---

## 1. What Does This Component Do?

_This section needs to be substantial — not a one-liner, but a full description of what this component is, why it exists, and what role it plays in the overall product. Think of it as the "what are you building?" section from the vision document, but scoped to this one component. Someone reading this should understand exactly what this part of the product does without needing to read anything else. The functional purpose should be rich enough that sub-components start to become visible in the narrative — the same way the vision narrative makes components visible._

**Functional purpose:**

_Describe what this component does in detail. What is its job within the overall product? What problem does it solve for the user? How does the user experience it? What does it feel like to use? Don't just say "handles onboarding" — describe the full onboarding experience: what the user sees, what they do, what information they provide, what happens behind the scenes, and what the outcome is when they're done. The richer this description, the easier it is to identify sub-components and user journeys later._

___

**Personas:**

_Which personas from the vision document use this component, and how? Different personas may use the same component in very different ways or have different levels of access. For example, an admin dashboard component is only used by admin personas, while a trading component might be used by all user personas but with different capabilities based on their verification level. Understanding per-persona usage shapes the user journeys and access controls._

| Persona | How they use this component | What they need from it |
|---------|---------------------------|----------------------|
| | _Describe the specific way this persona interacts with this component — what they're trying to do, what their workflow looks like, what matters most to them_ | _The specific outcomes or capabilities this persona needs from this component in order to get value_ |
| | | |

---

## 2. What Needs to Happen?

_The functional requirements. What does the user need to be able to do within this component? These should come from client conversations — the client describes what they want, and we capture it here in structured form. During conversations, the client will describe things non-linearly ("they need to see team performance, and also past trades, oh and other traders' performance on similar trades") — after the conversation, we bucket those into clear requirements._

**Functional requirements:**

_List everything the user needs to be able to do. Each requirement should be specific enough that you could test whether it's been met. "User can see data" is too vague. "User can see the performance history of any team over the last 12 months, broken down by match" is testable. Think about what the user does, what they see, what they can interact with, and what the system does in response._

- ___
- ___
- ___

**Business rules and constraints:**

_Rules that govern how the component behaves. These are non-negotiable behaviours dictated by the business, regulation, or the product's design. For example: "Trades under £10 don't incur commission fees", "Users must complete KYC before their first trade", "Research reports are only visible to the user who created them", "Maximum stake per trade is £10,000." Business rules often come from compliance, commercial decisions, or the client's specific requirements._

- ___
- ___

**Edge cases and error states:**

_What happens when things go wrong or when the user does something unexpected? For example: "What happens if the payment fails mid-trade?", "What happens if the KYC provider's API is down?", "What happens if a user tries to trade on a match that has already started?", "What if two users try to execute opposing trades simultaneously?" Edge cases are often missed in initial conversations and surface during building — but capturing known ones early prevents rework._

- ___
- ___

---

## 3. How Should It Look and Feel?

_The design direction for this component. This isn't about pixel-perfect mockups — it's about establishing the principles and references that guide the design. What should the user feel when they use this component? What existing products set the bar for how this should look and operate? Screen-grabs and links to reference products are valuable here — they communicate design intent far more effectively than written descriptions._

**Design direction:**

_The overall aesthetic and feel. Is this component data-heavy and dense (like a Bloomberg terminal), clean and minimal (like Stripe's dashboard), playful and gamified (like Duolingo), or premium and exclusive (like a private banking app)? The design direction should align with the target persona's expectations and the brand's identity._

___

**Reference products:**

_Specific products or features to study and learn from. Include links and, where possible, screen-grabs. Note what to take from each reference and what to avoid. For example: "Robin Hood's onboarding flow is a good reference for the conversational style, but their payment verification creates a 2-3 day delay that kills momentum — we need to avoid that."_

- ___
- ___

**Key UX principles for this component:**

_Specific principles that should guide every design decision for this component. These should be opinionated and actionable — not generic ("must be user-friendly") but specific ("must feel instant — no loading spinners for core actions, data should appear to load progressively", "must not feel like a form — onboarding should feel conversational, one question at a time", "must feel premium — no clutter, generous whitespace, high-quality data visualisation")._

- ___
- ___

---

## 4. How Are We Going to Solve It?

_The technology approach. This is the crossover point between the client-facing role and the engineering role — it needs both business context (what the client needs, what constraints exist, what budget is available) and technical knowledge (what's feasible, what's the build vs. buy trade-off, what's the cost and complexity). For each major capability within this component, decide whether we're building it from scratch, buying/subscribing to a third-party service, or accessing it via an external API. Document the rationale for each decision so it can be revisited if circumstances change._

| Capability | Build / Buy / Access | Provider / Approach | Rationale |
|-----------|---------------------|-------------------|-----------|
| _A specific capability this component needs — e.g., "real-time sports data", "identity verification", "trade execution engine"_ | _Are we building this ourselves, buying a third-party solution, or accessing an external service via API?_ | _If buying or accessing: which provider and why. If building: what's the high-level approach._ | _Why this decision was made. Include both business rationale ("client has existing relationship with SportsRadar") and technical rationale ("building a real-time sports data pipeline from scratch would take 3 months and cost more than the SportsRadar subscription")_ |
| | | | |

---

## 5. What Data Does It Need?

_Every component consumes, produces, and/or stores data. Understanding the data requirements early is critical because it affects architecture decisions, third-party service selection, and integration with other components. For each data flow, identify where the data comes from, where it goes, and whether it needs to be stored. The distinction between data we access externally (SportsRadar API), data that builds up over time (user trading history), and data we create (research reports) matters because each has different infrastructure requirements._

| Data | Direction | Source / Destination | Notes |
|------|-----------|---------------------|-------|
| _Name the specific data — e.g., "team performance metrics", "user trade history", "KYC verification result"_ | In (consumes) / Out (produces) / Stored | _Where does it come from or go to? External API, another component, user input, internal database_ | _Any important detail: data freshness requirements (real-time vs. daily), volume, sensitivity (PII, financial), retention requirements_ |
| | | | |

---

## 6. Who Can Access It?

_Access control. Which personas can use this component, and what can each one do? Some components are available to all users (e.g., the landing page). Others are restricted by role (e.g., admin dashboard), by verification status (e.g., trading requires completed KYC), or by subscription tier (e.g., premium analytics). Defining access early prevents building features that then need to be locked down, and ensures the user journey accounts for access gates._

| Persona / Role | Access level | Notes |
|---------------|-------------|-------|
| _The persona or role from the vision document_ | _Full access / Limited / Read-only / Admin only / Gated (requires X)_ | _Any conditions: "Only after KYC complete", "Only on premium tier", "Can view but not create"_ |
| | | |

---

## 7. How Do We Know It's Working?

_Component-level success metrics. These are the evals for this component — the measurable outcomes that tell us whether it's doing its job. Success metrics should be specific enough to test against. "Users like the onboarding" is not a metric. "80% of users complete onboarding in a single session without dropping off" is testable. These metrics feed into the overall project success criteria from the vision document, but are scoped to this component._

- [ ] ___
- [ ] ___
- [ ] ___

---

## 8. Dependencies

_What does this component need from other components, and what do other components need from it? Dependencies define the integration points between components — the contracts that must be honoured for the components to work together. Also include external dependencies (third-party services, APIs, data feeds) that this component relies on. If a dependency can be mocked during development (allowing the component to be built in isolation), note that — it affects sequencing._

**What this component needs:**

| Depends on | What we need | Blocking? |
|-----------|-------------|----------|
| _Other component or external service_ | _Specific data, auth token, user state, API endpoint, etc._ | _Yes (can't start without it) / No (can mock it and integrate later)_ |
| | | |

**What other components need from this one:**

_List what this component must provide to other components. These become the interface contracts — the promises this component makes about what it will deliver._

- ___

---

## 9. Priority

_How important is this component relative to others? Must it exist at launch, or can it come later? The priority affects which components get built first and how resources are allocated. Consider: does the product make sense without this component? Is this the differentiator that makes the product special, or is it table stakes? Is this the riskiest component that should be validated first?_

**Must-have at launch?** ___

**Sequencing rationale:**

_Why should this component be built before or after other components? Factors to consider: client urgency ("they need the landing page for investor demo next month"), technical risk ("trading engine is the hardest part — validate it first"), value delivery ("the Bloomberg terminal is the differentiator — build it early to prove the concept"), dependencies ("KYC must exist before trading can go live")._

___

---

## 10. Risks

_Component-specific risks. More granular than the vision-level risks — focused on what could go wrong with this particular component. Think about: how could this component be abused? What data quality issues could affect it? What compliance requirements apply specifically here? What could cause users to lose trust at this point in the product?_

**Abuse vectors:**

_How could this specific component be exploited? For example: KYC component — bots submitting fake identity documents to create verified accounts at scale. Trading component — automated trading bots exploiting data latency to gain unfair advantage. Referral component — fake referral chains to extract rewards._

- ___

**Data risks:**

_What data quality or integrity issues are specific to this component? For example: Bloomberg terminal — data from SportsRadar has a 30-40 second delay, meaning users could make trades based on stale information. What's the acceptable latency? What happens when the data source is unavailable?_

- ___

**Compliance:**

_What industry-specific compliance applies to this component specifically? Some components carry more compliance weight than others — KYC/onboarding has heavy AML requirements, trading has financial regulation, data storage has GDPR implications. Note the specific requirements and standards (SOC2, ISO 27001, PCI-DSS, etc.) that apply to this component._

- ___

**Controls needed:**

_What product-level controls should be built into this component to mitigate the risks above? For example: rate limiting on sign-ups, data freshness indicators on the UI, automated fraud detection on trades, audit logging for compliance. These are product decisions, not just technical ones — they affect the entity journeys and the user experience._

- ___

---

## Sub-Components

_This section is **backfilled** as sub-components are identified and documented. When the component document is first created, this section may be empty or have only rough names from the initial brain dump. List a sub-component as **plain text** until its document exists; once you create `sub-components/[name]/[name].md`, come back and replace the plain text with a shortest-path `[[name]]` link (not a `[[sub-components/name]]` path). This is the routing mechanism — an agent or human reading the component can see all sub-components at a glance and navigate to documented ones._

| Sub-Component | Overview | Status | Link |
|--------------|----------|--------|------|
| _Sub-component name_ | _One-line description of what this sub-component does_ | _Collecting / Defined / Ready for build / In build / Complete_ | _[[name]] once it exists — plain text until then_ |
| | | | |
| | | | |

_If sub-components decompose further into sub-sub-components, they follow the same pattern: the sub-component document gets its own backfilled table linking to its children. The recursion continues until you reach leaf nodes (units small enough to build without further decomposition)._

---

## Diagrams

_Use diagrams inline within the relevant section. Full diagram guide (with all Mermaid and ASCII examples and when-to-use-which table) is in the vision template. Key uses within a component document:_

- **Section 1 (What does it do)** — ASCII tree of sub-component hierarchy
- **Section 2 (What needs to happen)** — Mermaid `graph TD` flowcharts for entity journeys within this component
- **Section 4 (How to solve it)** — Mermaid `graph LR` for data flow between this component and external services
- **Section 5 (Data)** — Mermaid `graph LR` for data flow, or Mermaid `sequenceDiagram` for API call sequences
- **Section 8 (Dependencies)** — Mermaid `graph LR` showing this component's connections to other components

---

## Skeleton: What the Filled-In Document Looks Like

_Below is the expected output structure. Guidance text is removed. Placeholders show where content goes and how much is expected._

```markdown
# [Project Name] — [Component Name]

> **Vision:** [[vision]]
> **Date:** [Date]
> **Status:** [Collecting | Defined | Ready for build | In build | Complete]
> **Owner:** [Client-facing person + Engineering person]

---

## 1. What Does This Component Do?

**Functional purpose:**

[Paragraph 1 — what this component is and what it does. Its role
within the overall product]

[Paragraph 2 — how the user experiences this component. What they
see, what they do, what it feels like]

[Paragraph 3+ — enough detail that sub-components become visible
in the narrative. The richer this is, the easier the next level
of decomposition]

[Inline ASCII tree of sub-components if they're already identified]

**Personas:**

| Persona | How they use this component | What they need from it |
|---------|---------------------------|----------------------|
| [Persona from vision doc] | [Specific usage pattern] | [Specific needs] |
| [Persona from vision doc] | [Specific usage pattern] | [Specific needs] |

---

## 2. What Needs to Happen?

**Functional requirements:**
- [Specific, testable requirement]
- [Specific, testable requirement]
- [Specific, testable requirement]

[Inline Mermaid flowchart of the primary user journey if helpful]

**Business rules and constraints:**
- [Rule with specific conditions]
- [Rule with specific conditions]

**Edge cases and error states:**
- [Scenario → expected behaviour]
- [Scenario → expected behaviour]

---

## 3. How Should It Look and Feel?

**Design direction:** [1-2 sentences on the overall aesthetic]

**Reference products:**
- [Product] — [what to take from it, link if available]
- [Product] — [what works, what to avoid, link if available]

**Key UX principles:**
- [Specific, opinionated principle]
- [Specific, opinionated principle]

---

## 4. How Are We Going to Solve It?

| Capability | Build/Buy/Access | Provider / Approach | Rationale |
|-----------|-----------------|-------------------|-----------|
| [Capability] | [Decision] | [Provider or approach] | [Business + technical reasoning] |
| [Capability] | [Decision] | [Provider or approach] | [Reasoning] |

---

## 5. What Data Does It Need?

| Data | Direction | Source / Destination | Notes |
|------|-----------|---------------------|-------|
| [Data name] | In / Out / Stored | [Source] | [Freshness, volume, sensitivity] |
| [Data name] | In / Out / Stored | [Source] | [Notes] |

---

## 6. Who Can Access It?

| Persona / Role | Access level | Notes |
|---------------|-------------|-------|
| [Role] | [Full / Limited / Gated] | [Conditions] |
| [Role] | [Level] | [Conditions] |

---

## 7. How Do We Know It's Working?

- [ ] [Specific, measurable metric]
- [ ] [Specific, measurable metric]
- [ ] [Specific, measurable metric]

---

## 8. Dependencies

**What this component needs:**

| Depends on | What we need | Blocking? |
|-----------|-------------|----------|
| [Component or service] | [Specific need] | [Yes / No — can mock] |

**What other components need from this one:**
- [Component] needs [specific thing] from us

---

## 9. Priority

**Must-have at launch?** [Yes / No / Nice-to-have]

**Sequencing rationale:** [1-2 sentences on why this should be
built before or after other components]

---

## 10. Risks

**Abuse vectors:**
- [Component-specific abuse risks]

**Data risks:**
- [Data quality/integrity risks]

**Compliance:**
- [Applicable standards and requirements]

**Controls needed:**
- [Product-level controls to mitigate risks]

---

## Sub-Components

| Sub-Component | Overview | Status | Link |
|--------------|----------|--------|------|
| [Name] | [One-line description] | [Status] | [[sub-components/name]] |
```
