---
name: product-process-documentation
description: Create comprehensive process documentation for Novosapien products. Use when building internal documentation that describes what a product is, its components, and how it works. Triggers on requests to document products, create process docs, or generate system overviews for Agent Teams, APIs, or Frontends. Produces Markdown documentation suitable for human team members and AI agents to understand complete systems.
---

# Product Process Documentation

Create internal process documentation for Novosapien products through bottom-up investigation and synthesis.

## Process Overview

```
Phase 1: Discovery & Document Setup
    ↓
Phase 2: Parallel Component Investigation (sub-agents)
    ↓
Phase 3: Synthesis
    ↓
Phase 4: Delivery
```

---

## Phase 1: Discovery & Document Setup

### Step 1.1: Repository Discovery

Ask the user:

> "What repositories make up [Product Name]? For each repository, provide:
> - Repository name/path
> - What it's for (brief description)
> - Type: Agent Team, API, or Frontend"

**Do not proceed until you have the complete list.**

Example response:
```
- `/path/to/content-engine-api` — Main backend API — API
- `/path/to/content-ideation-agents` — Idea generation team — Agent Team
- `/path/to/content-creation-agents` — Content drafting team — Agent Team  
- `/path/to/content-frontend` — User dashboard — Frontend
```

### Step 1.2: Create Main Document File

Create the main document file at a known path (e.g., `/home/user/[product-name]-process-documentation.md`).

Initialize with this structure, filling in component placeholders based on discovered repositories:

```markdown
# [Product Name] - Process Documentation

## System Overview
[To be completed after synthesis]

## High-Level Process Architecture
[To be completed after synthesis]

## Human Touchpoints
[To be completed after synthesis]

---

## Components

### [Repo 1 Name] ([Type])
<!-- SUB-AGENT: Investigate [repo-path] as [Type] -->
[Placeholder - awaiting sub-agent investigation]

### [Repo 2 Name] ([Type])
<!-- SUB-AGENT: Investigate [repo-path] as [Type] -->
[Placeholder - awaiting sub-agent investigation]

[Continue for all repositories...]

---

## Cross-Component Data Flow
[To be completed after synthesis]

## Quick Reference
[To be completed after synthesis]
```

Record the **file path** — you will provide this to each sub-agent.

---

## Phase 2: Parallel Component Investigation

### Step 2.1: Spawn Sub-Agents

For each repository, **spawn a sub-agent** with the following:

1. **Task type:** `codebase-researcher`
2. **Repository path:** The specific repo to investigate
3. **Component type:** Agent Team, API, or Frontend
4. **Output file path:** The main document file path created in Phase 1
5. **Section identifier:** Which section of the document to write to (e.g., "### Content Ideation Agents (Agent Team)")
6. **Template:** The appropriate template for the component type (copy from Templates section below)
7. **Investigation instructions:** The specific investigation instructions for that component type (copy from Investigation Instructions below)

**Sub-agent prompt structure:**

```
You are investigating a codebase to produce process documentation.

REPOSITORY: [path]
COMPONENT TYPE: [Agent Team / API / Frontend]
OUTPUT FILE: [main document path]
SECTION TO WRITE: [section header to replace]

INVESTIGATION INSTRUCTIONS:
[Paste relevant investigation instructions for this component type]

TEMPLATE TO USE:
[Paste relevant template]

TASK:
1. Investigate the repository following the investigation instructions
2. Build documentation using the provided template
3. Replace the placeholder section in the output file with your completed documentation
4. Return confirmation when complete
```

### Step 2.2: Wait for All Sub-Agents

All sub-agents run in parallel. Wait for all to complete before proceeding to Phase 3.

---

## Investigation Instructions by Component Type

### For Agent Team Repositories (LangGraph / DSPy)

**Step 1: Identify the framework**
- Look for `from langgraph` imports → LangGraph
- Look for `import dspy` or `from dspy` → DSPy

**Step 2: Find the orchestration entry point**
- LangGraph: Look for `StateGraph`, `Graph`, or `workflow` definitions
  - Search: `grep -r "StateGraph\|\.add_node\|\.add_edge" --include="*.py"`
- DSPy: Look for `dspy.Module` subclasses or pipeline definitions
  - Search: `grep -r "dspy.Module\|dspy.ChainOfThought\|dspy.Predict" --include="*.py"`

**Step 3: Map the agent flow**
- LangGraph: Trace `.add_node()` and `.add_edge()` calls to understand sequence
- DSPy: Trace the `forward()` method to understand pipeline stages
- Document: What triggers each agent? What does each agent trigger next?

**Step 4: Find all agents**
- Look for classes/functions registered as nodes (LangGraph) or modules (DSPy)
- Common patterns:
  - Classes with `Agent`, `Node`, `Processor` in name
  - Functions decorated or registered in the graph

**Step 5: Extract agent purposes from prompts**
- Prompts are typically in Python files as:
  - Multi-line strings (triple quotes)
  - String variables named `prompt`, `system_prompt`, `instructions`, `template`
  - f-strings with placeholders
  - `dspy.Signature` definitions (DSPy)
- Search: `grep -r "prompt\|instructions\|system_message" --include="*.py"`
- Read the prompt to understand what the agent does — this is the source of truth for purpose

**Step 6: Identify inputs and outputs**
- Look at function signatures and return types
- Look at state objects being passed (LangGraph: typically a TypedDict or Pydantic model)
- Look at `dspy.InputField` and `dspy.OutputField` (DSPy)

**Step 7: Determine architecture pattern**
- Linear: Nodes connected in sequence (A → B → C)
- Loop: Presence of cycles, `while` conditions, or edges back to earlier nodes
- Conditional: Presence of `add_conditional_edges()` (LangGraph) or branching logic
- Hybrid: Combination of above

**Step 8: Find termination conditions**
- Look for: `END` node connections, break conditions, success/failure states
- What causes the workflow to complete?

---

### For API Repositories (FastAPI)

**Step 1: Find the main application**
- Look for `FastAPI()` instantiation
- Common locations: `main.py`, `app.py`, `app/__init__.py`, `src/main.py`
- Search: `grep -r "FastAPI()" --include="*.py"`

**Step 2: Find all routers**
- Look for `APIRouter()` instantiation and `app.include_router()` calls
- Common locations: `routes/`, `routers/`, `api/`, `endpoints/`
- Search: `grep -r "APIRouter\|include_router" --include="*.py"`

**Step 3: Document all endpoints**
- Look for decorators: `@app.get`, `@app.post`, `@router.get`, `@router.post`, etc.
- For each endpoint, document:
  - Method and path
  - Purpose (from function name, docstring, or logic)
  - Request parameters/body (from function signature, Pydantic models)
  - Response structure (from return type hints, response_model)

**Step 4: Find data models**
- Look for Pydantic models: `class X(BaseModel)`
- Common locations: `models/`, `schemas/`, `types/`
- Search: `grep -r "BaseModel\|SQLModel" --include="*.py"`
- Document: Model name and what it represents (1 sentence)

**Step 5: Find database tables**
- Look for SQLAlchemy/SQLModel table definitions
- Search: `grep -r "Table\|__tablename__\|SQLModel" --include="*.py"`
- Document: Table name and what it stores (1 sentence)

**Step 6: Identify external integrations**
- Look for: HTTP clients (`httpx`, `requests`), SDK imports, API keys in config
- Common patterns: `client.get()`, `requests.post()`, service-specific imports
- Document: What external services does this API connect to?

---

### For Frontend Repositories (Next.js)

**Step 1: Identify the router type**
- `app/` directory → App Router (Next.js 13+)
- `pages/` directory → Pages Router
- Check `next.config.js` for configuration

**Step 2: Map all pages/routes**
- App Router: Each `page.tsx` or `page.js` in `app/` is a route
  - `app/dashboard/page.tsx` → `/dashboard`
  - `app/projects/[id]/page.tsx` → `/projects/:id`
- Pages Router: Each file in `pages/` is a route
  - `pages/dashboard.tsx` → `/dashboard`
  - `pages/projects/[id].tsx` → `/projects/:id`

**Step 3: Document each page**
- For each page, examine the component to determine:
  - Purpose: Why does this page exist?
  - What's displayed: Key information/components shown
  - User actions: Buttons, forms, interactions available
- Look at component imports to understand what's rendered

**Step 4: Identify user flows**
- Trace navigation: Look for `<Link>`, `router.push()`, `redirect()`
- What are the main journeys? (e.g., Login → Dashboard → Create Project → View Project)
- Document the primary paths through the application

**Step 5: Understand state management**
- Look for:
  - React Context: `createContext`, `useContext`
  - Zustand: `create()` from zustand
  - Redux: `createSlice`, `configureStore`
  - React Query/SWR: `useQuery`, `useSWR`
  - Local state: `useState` patterns
- Document: How does data flow through the frontend?

**Step 6: Find API connections**
- Look for `fetch()`, `axios`, API route calls
- Common locations: `lib/`, `services/`, `api/`, hooks with `use` prefix
- Document: What backend endpoints does this frontend call?

---

## Phase 3: Synthesis

Once all sub-agents have completed and the component sections are filled in, complete the remaining sections:

### 3.1: System Overview

Write 3-5 sentences covering:
- What does this system do? (one sentence summary)
- What are the main inputs? (what does a user/system provide to start?)
- What are the main outputs? (what does the system produce?)
- What is the overall architecture type? (based on component architectures)

### 3.2: High-Level Process Architecture

Create a visual or textual representation showing:
- How components connect to each other
- Data flow between components
- Key decision points
- Entry and exit points

Example format:
```
User Input → [Frontend] → [API] → [Agent Team 1] → [Agent Team 2] → [API] → [Frontend] → User Output
                              ↓
                        [Database]
```

Or for more complex flows, use ASCII diagrams showing branches and loops.

### 3.3: Human Touchpoints

List every place where a human interacts with the system:
- **Input provision:** Where do humans provide data, briefs, feedback?
- **Decision points:** Where do humans make choices that affect flow?
- **Review/approval:** Where do humans review outputs before proceeding?
- **Override capability:** Where can humans intervene in automated processes?

### 3.4: Cross-Component Data Flow

Document how data moves between components:
- What data does the frontend send to the API?
- What data does the API send to agent teams?
- What data flows between agent teams?
- What data returns to the user?

### 3.5: Quick Reference

Create a summary table:

| Component | Type | Purpose |
|-----------|------|---------|
| [Name] | Agent Team | [One sentence] |
| [Name] | API | [One sentence] |
| [Name] | Frontend | [One sentence] |

---

## Phase 4: Delivery

Output the complete Markdown document.

---

## Templates

### Template A: Agent Team

```markdown
# [Agent Team Name]

## Purpose
[What this team accomplishes as a unit — 1-2 sentences]

## Architecture Type
[Linear / Loop / Conditional / Hybrid]

## Termination Conditions
[What triggers completion — be specific]

## Inputs
[What the team receives to begin work — list key data]

## Outputs  
[What the team produces — list key outputs]

## Process Flow

[ASCII diagram or step-by-step description showing how agents interact]

Example:
```
Input → [Agent 1] → [Agent 2] → Decision Point
                                    ↓ Yes → [Agent 3] → Output
                                    ↓ No  → [Agent 4] → Loop back to Agent 2
```

## Agents

### [Agent 1 Name]
- **Purpose:** [What this agent does — extracted from its prompt]
- **Inputs:** [What it receives]
- **Outputs:** [What it produces]

### [Agent 2 Name]
- **Purpose:** [What this agent does — extracted from its prompt]
- **Inputs:** [What it receives]
- **Outputs:** [What it produces]

[Continue for all agents...]
```

---

### Template B: API

```markdown
# [API Name]

## Purpose
[What this API serves — 1-2 sentences]

## Endpoints

### [METHOD] [/path]
- **Purpose:** [What this endpoint does]
- **Request:** [Key parameters or body fields]
- **Response:** [Key response fields]

### [METHOD] [/path]
- **Purpose:** [What this endpoint does]
- **Request:** [Key parameters or body fields]
- **Response:** [Key response fields]

[Continue for all significant endpoints...]

## Data Models

| Model | Description |
|-------|-------------|
| [ModelName] | [What it represents — 1 sentence] |
| [ModelName] | [What it represents — 1 sentence] |

## Tables

| Table | Description |
|-------|-------------|
| [table_name] | [What it stores — 1 sentence] |
| [table_name] | [What it stores — 1 sentence] |

## External Integrations

- **[Service Name]:** [What it's used for]
- **[Service Name]:** [What it's used for]
```

---

### Template C: Frontend

```markdown
# [Frontend Name]

## Purpose
[What this interface enables — 1-2 sentences]

## Pages

### [Page Name] (`/route`)
- **Purpose:** [Why this page exists]
- **What's Displayed:** [Key information shown]
- **User Actions:** [What the user can do]

### [Page Name] (`/route`)
- **Purpose:** [Why this page exists]
- **What's Displayed:** [Key information shown]
- **User Actions:** [What the user can do]

[Continue for all significant pages...]

## User Flows

**[Flow Name]** (e.g., "Create New Campaign")
1. User starts at [page]
2. User [action]
3. System [response]
4. User navigates to [page]
5. [Continue...]

**[Flow Name]**
1. ...

## State Management

[Describe how data flows through the frontend — what state management approach is used, how data is fetched and cached, how components share data]
```

---

## Guidelines

### Level of Detail

- **Descriptive, not exhaustive** — reader should understand system without reading code
- **High-level for large systems** — don't document every helper function
- **Agent purposes from prompts** — the prompt is the source of truth
- **Schemas: names and descriptions only** — no full field definitions

### What to Include vs. Skip

**Include:**
- All agents that perform meaningful work
- All endpoints that serve the product (not health checks, metrics)
- All user-facing pages
- Key data models that flow through the system
- External service integrations

**Skip:**
- Utility functions
- Internal helper endpoints
- Boilerplate/layout components
- Generated code
- Test files

### Architecture Patterns Reference

| Pattern | Indicators | Example |
|---------|------------|---------|
| Linear | Sequential edges, no loops | A → B → C → D → Output |
| Loop | Back-edges, while conditions | A → B → C → (condition) → B |
| Conditional | Branching edges, if/else | A → B → [if X] → C / [else] → D |
| Hybrid | Multiple patterns combined | Linear with conditional branches and iteration loops |

---

## Example Output (Condensed)

For reference, here is a condensed example of what good documentation looks like:

```markdown
# Cold Outreach Workforce - Process Documentation

## System Overview
The Cold Outreach Workforce automates B2B cold outreach by analyzing companies, profiling individuals, qualifying leads against ICPs, and generating personalized message sequences. 

**Inputs:** Lead information (name, company, title, website URL)
**Outputs:** Lead intelligence report + personalized outreach sequence
**Architecture:** Linear with conditional branching (qualified leads proceed to message generation)

## High-Level Process Architecture

```
Lead Input → [Lead Qualification Team] → Decision Gate
                                              ↓
                        ICP/Persona D? → Skip (no messages)
                        ICP/Persona A-C? → [Message Generation Team] → Output
```

## Human Touchpoints
- **Input:** User provides lead list via frontend or API
- **Review:** User reviews generated messages before sending
- **Override:** User can manually adjust lead grades

## Components

### Lead Qualification Team (Agent Team)
**Purpose:** Analyze company and individual to determine ICP/Persona fit
**Architecture:** Linear
**Termination:** All 8 analysis steps complete OR grade D assigned

**Agents:**
- **WhatTheySell** — Extracts company offerings from website
- **WhoTheySellTo** — Identifies target customer profile
- **PersonaPainPointAnalysis** — Profiles individual's role and pain points
- **ICPCategorizer** — Matches company to ICP categories
- **ICPRanker** — Grades ICP fit (A/B/C/D)
- **PersonaCategorizer** — Matches individual to buyer personas
- **PersonaRanker** — Grades persona fit (A/B/C/D)

### Message Generation Team (Agent Team)
**Purpose:** Generate personalized outreach sequence
**Architecture:** Loop (critic-iteration cycle, max 2 iterations)
**Termination:** All 6 quality criteria pass OR 2 iterations complete

**Agents:**
- **CreationAgent** — Generates initial message sequence
- **CriticAgent** — Evaluates against 6 quality dimensions
- **IterationAgent** — Refines based on critic feedback

[API and Frontend sections would follow...]

## Quick Reference

| Component | Type | Purpose |
|-----------|------|---------|
| Lead Qualification Team | Agent Team | Analyze and grade leads |
| Message Generation Team | Agent Team | Create personalized outreach |
| Outreach API | API | Orchestrate workflow, store results |
| Outreach Dashboard | Frontend | User interface for lead management |
```