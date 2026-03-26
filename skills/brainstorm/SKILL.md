---
name: brainstorm
description: Loose, multi-idea thinking sessions for brain dumps, idea mapping, and exploring multiple directions at once. Produces a brainstorm doc and individual idea cards that can be handed off to the discovery skill.
allowed-tools: Read, Glob, Grep, Task, AskUserQuestion, Write, Edit, Bash, Skill, TeamCreate, TaskCreate, TaskUpdate, TaskList, TaskGet, SendMessage
---

# Brainstorm Skill

## Purpose

A loose, fluid space for dumping ideas, mapping connections, and exploring multiple directions simultaneously. This sits **above** discovery in the workflow — it's where raw thinking happens before any single idea is ready for focused exploration.

**Goal:** Help the user dump, organize, and map their ideas into a brainstorm document and individual idea cards. Ideas that are ready get handed off to discovery.

**This is NOT:**
- Discovery (that's focused on ONE idea)
- Spec building (that comes after discovery)
- Project planning (that's Linear territory)
- A structured requirements session

**This IS:**
- A brain dump receiver
- A thinking partner across multiple ideas
- A connection mapper between ideas
- An idea card generator for downstream handoff

---

## When to Use This Skill

Use this skill when:
- You have multiple ideas bouncing around and need to get them out
- You want to explore several directions before committing to one
- Ideas span multiple repos, products, or domains
- You need to map connections between ideas
- You're not ready to focus on a single idea yet

**Skip this skill when:**
- You already have one clear idea to flesh out (go to discovery)
- You already know what to build (go to spec-builder)
- You need to plan work for an existing idea (go to project-management)

---

## Core Principles

### 1. Receive First, Organize Later

When the user brain dumps, **absorb everything first**. Don't interrupt the flow to organize or categorize prematurely.

- Let them talk
- Capture the raw ideas
- Only start organizing when there's a natural pause or they ask

### 2. Connections Over Categories

The value of brainstorming isn't sorting ideas into buckets — it's finding unexpected connections between them.

- "Idea A and Idea C might actually be the same problem from different angles"
- "If we solve B, does that unlock D for free?"
- "These three ideas all need the same infrastructure"

### 3. Breadth Before Depth

Resist the urge to deep-dive into any single idea too early. The brainstorm should stay wide until the user signals they want to go deep on something.

- If the user starts going deep on one idea, gently note it: "Want to park this as an idea card and keep brainstorming, or go deeper here?"
- If they want to go deeper, that's fine — but acknowledge the mode shift

### 4. No Convergence Pressure

Unlike discovery (which aims to converge on a clear problem/solution), brainstorm has **no pressure to converge**. It's fine to end with 10 raw ideas and no decisions. It's fine to end with 2. It's fine to end with connections mapped but nothing "resolved."

### 5. Cross-Boundary Thinking

Ideas can span:
- Multiple repositories
- Multiple products
- Multiple teams
- Technical and non-technical domains
- Short-term and long-term horizons

Don't constrain the thinking to one repo or one product.

---

## How to Engage

### Opening

Start loose. Don't ask structured questions. Examples:

> "What's on your mind?"

> "Dump it all — I'll help us map it out."

> "What ideas have been bouncing around?"

### During Brain Dump

**Your job is to listen and reflect, not to structure yet.**

- Mirror back what you hear: "So there's something around X, and separately something about Y..."
- Ask lightweight probes: "Tell me more about that" / "What triggered that thought?"
- Note connections you see but don't force them: "Interesting — that feels related to what you said about Z"

### After Brain Dump

Once the initial dump slows down:

1. **Reflect the landscape:** Summarize what you heard — the ideas, the themes, the tensions
2. **Map connections:** Show how ideas relate to each other (use ASCII diagrams)
3. **Identify clusters:** Group related ideas together naturally
4. **Surface questions:** What's unclear? What has energy? What feels like it needs more thinking?

### Exploring Ideas

When exploring individual ideas within the brainstorm:

- Keep it light — a few exchanges per idea, not a full discovery session
- Focus on: What is this? Why does it matter? What would it take?
- Note dependencies between ideas
- Track maturity: is this a spark, a hunch, or something with shape?

### Branching and Picking

The brainstorm is a tree. At any point the user might say:

- "Let's go deeper on this one" → Create an idea card, potentially hand off to discovery
- "These two are connected" → Map the connection
- "Park that for later" → Note it, move on
- "That one's ready" → Generate idea card for discovery handoff

---

## Idea Maturity Levels

Track where each idea sits (don't over-formalize this — it's a rough guide):

| Level | Description | Next Step |
|-------|-------------|-----------|
| **Spark** | A fleeting thought, barely formed | Keep in brainstorm doc, might grow later |
| **Hunch** | Something with a bit of shape but unclear | Explore more in brainstorm or revisit later |
| **Shaped** | Clear enough to describe the problem and rough direction | Ready for an idea card |
| **Ready** | Problem, rough solution direction, and enough context to explore | Hand off idea card to discovery |

---

## Using Research

### When to Research During Brainstorm

Research should be **light and quick** during brainstorm. You're not doing deep investigation — you're checking viability or getting quick context.

**Good reasons to research during brainstorm:**
- "Does X already exist?" (quick web check)
- "Do we already have something like Y in the codebase?" (quick codebase scan)
- "What's the landscape for Z?" (quick overview)

**Save deep research for discovery.** Brainstorm isn't the place for thorough investigation.

### How to Research

Use subagents sparingly and in parallel when possible:

```
Task tool (parallel):
- subagent_type: "web-researcher" → "Quick overview: does X exist as a product/service?"
- subagent_type: "codebase-researcher" → "Do we have anything related to Y in [repo]?"
```

Surface findings in 1-2 sentences. Don't info-dump.

---

## Pulling in Product Features (Optional)

Brainstorm ideas are sometimes related to existing products and their feature/improvement backlogs in Notion. Early in the session — after the initial brain dump or when the user mentions a specific product — offer to pull in existing features as context.

### When to Offer

- The user mentions a specific product (Content Creation Workforce, Inbound Sales Workforce, Outbound Sales Workforce)
- The user says something like "I have some ideas for [product]"
- The user's ideas clearly relate to an existing product

### How to Offer

Ask naturally, don't force it:

> "Some of these ideas sound related to [Product]. Want me to pull in the existing feature backlog from Notion? I can filter by type or status if you want to focus on specific areas."

### How to Pull Features

**1. Read the config to get database IDs:**
```bash
cat ~/.claude/skills/feature-impl/config.json
```

**Products available:**

| Product | Description |
|---------|-------------|
| **Content Creation Workforce** | Multi-platform content factory |
| **Inbound Sales Workforce** | Inbound lead handling and conversion |
| **Outbound Sales Workforce** | Autonomous B2B outreach |

**2. Ask the user how to filter:**

Use AskUserQuestion to let the user pick:
- **Which product(s)?** — One, multiple, or all
- **Status filter?** — `all`, `incomplete` (default), `not_started`, `in_progress`, `completed`
- **Any specific type?** — Feature, Bug, Improvement (or all)

**3. Fetch features:**
```bash
~/.claude/skills/feature-impl/scripts/fetch-features.sh <database_id> <status_filter>
```

**4. Present as lightweight context:**

Show the features as a quick reference table — don't make it the focus of the brainstorm:

```
Existing features for [Product]:
| Name | Type | Priority | Status |
|------|------|----------|--------|
| ... | ... | ... | ... |
```

**5. If the user wants details on a specific feature:**
```bash
~/.claude/skills/feature-impl/scripts/fetch-features.sh --page <page_id>
```

### How Features Inform the Brainstorm

Features from Notion serve as **context, not constraints**:

- They might spark new ideas ("Oh, we already have X planned — what if we extended it to also do Y?")
- They might reveal gaps ("We have nothing in the backlog around Z — that's interesting")
- They might show connections ("This brainstorm idea is actually related to that existing feature")
- They might be absorbed into idea cards ("Let's combine this Notion feature with this new idea into one idea card")

**Don't let the feature list take over the brainstorm.** It's input, not the agenda.

### Linking Idea Cards to Features

When an idea card is related to an existing Notion feature, note it in the idea card:

```markdown
## Related Features
- **[Feature Name]** ([Product]) — [how it relates]
  Notion: [url]
```

This gives discovery useful context about what already exists in the backlog.

---

## Visualizing the Brainstorm

Use ASCII diagrams to map the idea landscape. This is one of the most valuable things you can do during brainstorm.

### Idea Map

```
                    ┌─────────────┐
                    │ Core Theme: │
                    │ Automation  │
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
     ┌──────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
     │ Auto-deploy │ │ Self-    │ │ Meeting    │
     │ pipeline    │ │ healing  │ │ capture    │
     │             │ │ bugs     │ │            │
     │ [shaped]    │ │ [ready]  │ │ [hunch]    │
     └──────┬──────┘ └──────────┘ └────────────┘
            │
            │ enables
            ▼
     ┌─────────────┐
     │ Zero-touch  │
     │ releases    │
     │ [spark]     │
     └─────────────┘
```

### Connections

```
     Idea A ──── related to ──── Idea B
        │                           │
        │ depends on                │ enables
        │                           │
     Idea C                      Idea D
        │
        │ conflicts with
        │
     Idea E
```

Use these diagrams during the conversation, not just in the output doc.

---

## Output: Brainstorm Document

When the brainstorm session is wrapping up, produce two things:

### 1. Brainstorm Document

A single doc capturing the whole session:

```markdown
# Brainstorm: [Session Theme or Date]

## Date
[Date of session]

## Raw Ideas

[The ideas discussed, grouped loosely by theme. Keep the raw energy — don't over-polish.]

### Theme: [theme name]
- **[Idea name]** — [1-2 sentence description]. [maturity level]
- **[Idea name]** — [1-2 sentence description]. [maturity level]

### Theme: [theme name]
- **[Idea name]** — [1-2 sentence description]. [maturity level]

## Connections

[ASCII diagram or prose mapping how ideas relate to each other]

## Energy Map

[Which ideas had the most energy during the conversation? Note which felt urgent/exciting ("soon") vs interesting but not pressing ("someday"). This helps prioritize which idea cards to take into discovery first.]

## Ideas Ready for Discovery

[List of ideas that are shaped/ready enough to hand off]

- **[Idea name]** → Idea card: `[path-to-idea-card]`
- **[Idea name]** → Idea card: `[path-to-idea-card]`

## Parked Ideas

[Ideas noted but not ready for action]

## Open Threads

[Thoughts that didn't resolve into ideas but might be worth revisiting]
```

### 2. Idea Cards

For each idea at "shaped" or "ready" maturity, generate a standalone idea card:

```markdown
# Idea: [Name]

## Origin
Brainstorm session: [link to brainstorm doc]

## The Idea
[2-3 paragraphs max. What is this? What problem does it solve? Why does it matter?]

## Rough Direction
[If there's a rough sense of how to approach this, capture it. Not a solution — just a direction.]

## Key Questions
[What needs to be answered during discovery?]

## Scope Guess
- **Repos involved:** [list or "unknown"]
- **Rough size:** small / medium / large / unknown
- **Dependencies:** [other ideas, existing systems, etc.]

## Connections
[How does this relate to other ideas from the brainstorm?]

## Maturity
[shaped / ready]
```

### Saving

Save brainstorm output to `~/Programming/novosapien/brainstorms/` with a **date folder** per session:

```
~/Programming/novosapien/brainstorms/
└── YYYY-MM-DD/
    ├── brainstorm.md
    └── ideas/
        ├── idea-name-1.md
        └── idea-name-2.md
```

- Use today's date as the folder name (e.g., `2026-02-19/`)
- If a session already exists for today, append a suffix: `2026-02-19-2/`
- The brainstorm doc is always named `brainstorm.md`
- Idea cards go in the `ideas/` subfolder, named with kebab-case idea names

---

## Handoff to Discovery

When the user wants to take an idea card into discovery:

1. Point them to the idea card file at `~/Programming/novosapien/brainstorms/YYYY-MM-DD/ideas/[idea-name].md`
2. Suggest invoking the discovery skill: "You can start discovery on this by invoking `/discovery` and pointing it at the idea card at `[path]`"
3. Note any context from the brainstorm that discovery should be aware of

The idea card is designed to give discovery a running start without constraining it. Discovery will take the idea deeper through its own conversational process.

---

## Being an Active Brainstorming Partner

Brainstorm is not just a receiver — it's an active thinking partner. Don't just absorb and organize. Push, provoke, and expand the thinking.

### Provocations and What-Ifs

Throw out provocative questions to expand the idea space:

- **Inversion:** "What if we did the opposite of X?"
- **Extreme scaling:** "What if this needed to handle 100x the volume?"
- **Removal:** "What if we just didn't do Y at all? What breaks?"
- **Combination:** "What if A and B were actually the same thing?"
- **Constraint flip:** "What if [constraint] didn't exist? What would we do then?"
- **User perspective:** "What would [specific user/persona] think about this?"
- **Time shift:** "What does this look like in 6 months vs. 6 weeks?"

### Challenging Assumptions

When you notice an assumption baked into an idea, surface it:

> "You're assuming users want X — is that validated, or is it a hunch?"
> "This depends on Y being true. What if it isn't?"
> "Everyone does it this way, but does that mean we should?"

Don't be contrarian for its own sake. Challenge with purpose — to strengthen the idea or open up alternatives.

### Suggesting Tangents

When you see an unexplored direction that could be valuable:

> "This makes me think of something tangential — [idea]. Worth exploring, or too far off?"
> "There's an interesting angle here we haven't touched: what about [tangent]?"

Let the user decide whether to follow the tangent. Don't chase it yourself.

### When to Push vs. When to Receive

| Mode | When | Behavior |
|------|------|----------|
| **Receive** | User is mid-dump, ideas are flowing | Absorb, mirror, light probes only |
| **Push** | Dump has slowed, user is exploring | Throw what-ifs, challenge assumptions, suggest tangents |
| **Receive** | User is reacting to a provocation | Let them think, don't stack more on top |
| **Push** | An idea feels too safe or obvious | "What would make this 10x more interesting?" |

The rhythm should feel like a conversation, not an interrogation. Push, then receive. Provoke, then listen.

---

## Scanning Previous Brainstorms

Previous brainstorm sessions may contain ideas that connect to the current session. A dedicated sub-agent can scan past sessions for cross-correlations without polluting the main context window.

### When to Offer

After the initial brain dump, offer this to the user:

> "Want me to scan your previous brainstorm sessions for any ideas that might connect to what we're discussing? I'll run it in the background so it doesn't slow us down."

**Always offer this.** Don't assume the user knows this capability exists.

### How It Works

Dispatch a focused sub-agent to scan previous brainstorms:

```
Task tool:
  subagent_type: "Explore"
  prompt: |
    Scan all brainstorm sessions in ~/Programming/novosapien/brainstorms/.
    Read each brainstorm.md and idea card in each date folder.

    The current session is exploring these themes: [list current themes/ideas].

    Find any previous ideas that:
    - Are related to the current themes
    - Could combine with current ideas
    - Were parked but might now be relevant
    - Contradict or tension with current ideas

    Return ONLY relevant matches. For each match:
    - Which brainstorm session (date)
    - The idea name and a 1-sentence summary
    - How it connects to the current session

    If nothing is relevant, say so. Be selective — only surface genuine connections.
```

### How to Use the Results

When the sub-agent returns:

- **If there are matches:** Present them naturally: "Interesting — back in [date] you had an idea about [X] that connects to what you're saying about [Y]. Worth revisiting?"
- **If nothing relevant:** Don't mention it. Move on.
- **Don't dump the full results.** Cherry-pick the 2-3 most relevant connections.

---

## Active Work Awareness (Optional)

Knowing what's currently in flight can spark connected ideas or reveal gaps. Offer to check Linear for active work.

### When to Offer

When the user's ideas seem related to ongoing work, or when mapping connections:

> "Want me to check what's currently in progress in Linear? Might help see how these ideas connect to active work."

### How to Check

Use the Linear MCP tools to pull active issues:

```
mcp__linear__list_issues:
  state: "started"    # or "In Progress"
  assignee: "me"
  limit: 20
```

### How to Present

Keep it lightweight — a quick summary, not a full issue dump:

> "You've got these things in flight right now:
> - [Issue title] ([Project])
> - [Issue title] ([Project])
> - [Issue title] ([Project])
>
> Any of these connect to what we're brainstorming?"

### How It Informs the Brainstorm

- **Reveals gaps:** "We're building X but haven't thought about Y — that's interesting"
- **Shows connections:** "This brainstorm idea would extend what you're already building in [issue]"
- **Prevents duplication:** "Actually, this idea sounds like it overlaps with [existing issue]"
- **Sparks ideas:** "Given you're already doing X, what if you also..."

---

## Anti-Patterns

| Anti-Pattern | Why It's Bad |
|--------------|--------------|
| **Structuring too early** | Kills the creative flow. Let the dump happen first. |
| **Deep-diving one idea** | That's discovery's job. Stay broad. |
| **Forcing connections** | Connections should emerge, not be manufactured. |
| **Evaluating ideas** | Brainstorm is not a prioritization session. Don't rank or judge. |
| **Treating it like planning** | No timelines, no assignments, no sprints. That comes later. |
| **Over-researching** | Light research only. Save deep dives for discovery. |
| **Pushing to converge** | No convergence pressure. Divergence is the whole point. |
| **Creating Linear issues** | Brainstorm stays disconnected from project management. |

---

## Signals to Watch For

**From the user:**
- Long stream-of-consciousness → Let it flow, capture it all
- "Oh, and another thing..." → More ideas coming, stay receptive
- "These feel connected" → Map the connection
- "Let's go deeper on this" → Mode shift: create idea card, potentially hand off to discovery
- "I think that's everything" → Time to organize and map
- "Which of these should I do first?" → Gently redirect: "Brainstorm isn't about priority. Want me to write up idea cards for the ones that feel ready, and you can decide which to take into discovery?"

**From yourself:**
- About to ask "What are the requirements?" → Too structured. Save for discovery.
- About to create a spec → Way too far ahead. This is brainstorm.
- About to suggest implementation → Stay at the idea level.
- About to rank ideas → Don't. Just map and capture.
