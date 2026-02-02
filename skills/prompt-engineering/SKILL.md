---
name: prompt-engineering
description: Create system prompts for agents using frameworks (Single-Turn, Conversational), roles (Researcher, Critic, Router, etc.), and modifiers (Tools, Structured Output, Memory, Reasoning). Use when writing agent prompts, structuring prompts for specific roles, or reviewing existing prompts.
allowed-tools: Read, Glob, Grep, Task
---

# Prompt Engineering Skill

## Purpose

Provides system prompt templates and guidance for building agent prompts. Framework-agnostic — the same prompts work with LangGraph, DSPy, or any other agent framework.

---

## When to Use This Skill

Use this skill when:
- Writing system prompts for new agents
- Structuring prompts for specific agent roles (researcher, critic, router, etc.)
- Adding implementation features (tools, structured output, conversation memory)
- Reviewing or improving existing prompts

---

## Selection Criteria

Use this section to determine the right framework, role, and modifiers for an agent. After each selection, validate your choice with the user and explain your reasoning.

---

### Step 1: Choose Framework

The framework determines the prompt's structure and interaction model. There are two options:

| Framework | Core Concept |
|-----------|--------------|
| **Single-Turn** | Discrete task: defined inputs → processing steps → defined output |
| **Conversational** | Multi-turn dialogue: ongoing interaction with context across turns |

#### Quick Decision

```
Is the agent's interaction single-turn or multi-turn?
├── Single-turn (request in → response out, done)
│   └── Single-Turn
└── Multi-turn (back-and-forth dialogue)
    └── Does context need to persist across turns?
        ├── Yes → Conversational
        └── No (independent exchanges) → Single-Turn
```

#### Signals for Single-Turn

Choose Single-Turn when:
- The agent receives all necessary information upfront (no need to gather more through dialogue)
- The task has a clear start and end point
- The output format is predictable and consistent
- The agent doesn't need to ask clarifying questions
- Each invocation is independent (stateless)

**Strong indicators:**
- "Process this data and return X"
- "Classify this input into one of these categories"
- "Transform this from format A to format B"
- "Analyze this and produce a report"
- "Given X, decide Y"

**Examples:**
- Email classifier that routes to departments
- Data transformer converting JSON to XML
- Code reviewer analyzing a PR
- Research synthesizer producing a report from sources
- Router deciding which agent handles a request

#### Signals for Conversational

Choose Conversational when:
- The agent needs to gather information through back-and-forth dialogue
- Users may ask follow-up questions or change direction
- The agent must maintain context across multiple turns
- Tone, personality, and user experience matter
- The scope of the task emerges through conversation

**Strong indicators:**
- "Help the user with..."
- "Guide them through..."
- "Answer questions about..."
- "Chat with users to..."
- "Assist customers who..."

**Examples:**
- Customer support chatbot
- Onboarding assistant that guides users through setup
- Sales advisor that answers product questions
- Technical support that troubleshoots issues interactively
- Personal assistant that manages tasks through dialogue

#### Edge Cases and Nuances

**Agent-to-agent communication:**
- Not automatically Single-Turn—depends on the interaction pattern
- If Agent A sends a request and Agent B responds once → Single-Turn
- If Agent A and Agent B have a back-and-forth negotiation or clarification loop → Conversational
- Ask: "Do these agents need to exchange multiple messages to complete the task?"

**User-facing but single-turn:**
- A user submits a form and gets a response → Single-Turn (despite being user-facing)
- The key question is whether there's dialogue, not who the user is

**Conversational with structured output:**
- An agent can be Conversational (multi-turn dialogue) AND output structured data
- Example: Support chat that returns `{"message": "...", "confidence": 0.9, "intent": "..."}`
- Use Conversational framework + Structured Output modifier
- See `references/frameworks/conversational.md` → "With Structured Output Modifier" section

**Hybrid patterns:**
- Some systems have a Conversational outer agent that dispatches to Single-Turn inner agents
- Choose framework based on the specific agent you're building, not the system as a whole

#### Validation

Before proceeding, confirm the framework choice with the user. Explain which signals led to the recommendation and why this framework fits the agent's interaction pattern. Get explicit confirmation before moving to role selection.

**References:** `references/frameworks/single-turn.md`, `references/frameworks/conversational.md`

---

### Step 2: Choose Role

The role determines which sections to emphasize and provides domain-specific guidance. There are 8 roles.

#### Role Decision Tree

```
What does the agent primarily DO?
├── Gather and synthesize information → Researcher
├── Evaluate/critique work products → Critic/Reviewer
├── Make routing decisions between options → Router/Classifier
├── Create original content (writing, ideas) → Creative/Generator
├── Break down goals into steps/plans → Planner/Strategist
├── Condense content, extract key points → Summarizer/Synthesizer
├── Maintain ongoing dialogue with users → Conversational/Assistant
└── Convert data from one format to another → Transformer/Formatter
```

#### Role Descriptions

**Researcher**
- Primary job: Find, gather, and synthesize information from multiple sources
- Key activities: Searching, reading, comparing, synthesizing, citing
- Output: Findings, analysis, recommendations with sources
- Use when: The agent needs to discover information, not just process what's given

**Critic/Reviewer**
- Primary job: Evaluate work products against standards or criteria
- Key activities: Assessing, identifying issues, categorizing severity, suggesting fixes
- Output: Structured feedback with issues, severity, and recommendations
- Use when: The agent judges quality, correctness, or compliance

**Router/Classifier**
- Primary job: Route input to the right destination OR select a specific category
- Key activities: Analyzing input, matching to categories, selecting a path
- Output: A decision (category, route, next step) with confidence
- Use when: The agent's job is to decide "which one" not "what to do with it"

**Creative/Generator**
- Primary job: Create original content—writing, ideas, drafts
- Key activities: Ideating, drafting, iterating, matching style/tone
- Output: Original content (text, copy, ideas, designs)
- Use when: The agent generates something new, not transforms existing content

**Planner/Strategist**
- Primary job: Break down goals into actionable plans with dependencies
- Key activities: Decomposing, sequencing, identifying dependencies, estimating
- Output: Plans, roadmaps, task lists with structure
- Use when: The agent creates a plan for others to execute (not executes itself)

**Summarizer/Synthesizer**
- Primary job: Condense information while preserving meaning
- Key activities: Extracting key points, reducing volume, identifying themes
- Output: Summaries, key takeaways, condensed versions
- Use when: The goal is to reduce content, not transform its format

**Conversational/Assistant**
- Primary job: Maintain helpful dialogue across multiple turns
- Key activities: Answering, clarifying, guiding, adapting to user needs
- Output: Conversational responses that build on context
- Use when: The agent needs ongoing dialogue with users (not just multi-turn capability)

**Transformer/Formatter**
- Primary job: Convert data from one format or structure to another
- Key activities: Parsing, mapping fields, restructuring, normalizing
- Output: Data in the target format
- Use when: The input and output are the same information in different shapes

#### Disambiguation

When choosing between similar roles, ask these questions:

| Confusion | Clarifying Question | If Yes → | If No → |
|-----------|---------------------|----------|---------|
| Researcher vs Summarizer | Does it need to *find* information, or just condense what's provided? | Researcher | Summarizer |
| Researcher vs Critic | Is the primary output *findings* or *evaluation/judgment*? | Researcher | Critic |
| Critic vs Planner | Does it *evaluate existing work* or *create plans for future work*? | Critic | Planner |
| Creative vs Transformer | Is it *generating new content* or *converting existing content*? | Creative | Transformer |
| Planner vs Router | Does it produce *multi-step plans* or *single routing decisions*? | Planner | Router |
| Summarizer vs Transformer | Is the goal to *reduce volume* or *change format*? | Summarizer | Transformer |
| Any role vs Conversational/Assistant | Is *ongoing dialogue* the primary interaction mode? | Conversational/Assistant | Other role |

#### Common Mistakes

- **Picking Researcher when Summarizer fits**: If all the information is already provided and the agent just needs to condense it, use Summarizer
- **Picking Creative when Transformer fits**: If the agent is reformatting existing content (not creating new ideas), use Transformer
- **Picking Conversational/Assistant for everything user-facing**: A user-facing agent that processes a form submission is Single-Turn, not Conversational
- **Ignoring role combinations**: An agent might be "Researcher that outputs structured data" or "Critic with tools"—the role is the primary job, modifiers add capabilities

#### Validation

Before proceeding, confirm the role choice with the user. Explain what the agent's primary job is, why this role fits, and what sections/guidance it emphasizes. Get explicit confirmation before moving to modifiers.

**Role quick reference:**

| Role | Primary Job | Reference |
|------|-------------|-----------|
| Researcher | Gathers information, synthesizes findings | `references/roles/researcher.md` |
| Critic/Reviewer | Evaluates, provides feedback, identifies issues | `references/roles/critic-reviewer.md` |
| Router/Classifier | Makes decisions, routes to next step | `references/roles/router-classifier.md` |
| Creative/Generator | Writes content, generates ideas, drafts | `references/roles/creative-generator.md` |
| Planner/Strategist | Creates plans, breaks down tasks, sequences steps | `references/roles/planner-strategist.md` |
| Summarizer/Synthesizer | Condenses information, creates summaries | `references/roles/summarizer-synthesizer.md` |
| Conversational/Assistant | Maintains dialogue, handles follow-ups | `references/roles/conversational-assistant.md` |
| Transformer/Formatter | Converts data between formats | `references/roles/transformer-formatter.md` |

---

### Step 3: Choose Modifiers

Modifiers add capabilities to any role. Evaluate each independently—apply any combination that fits.

#### Tools Modifier

**Reference:** `references/modifiers/tool-usage.md`

**When to add tools:**
- The agent needs to retrieve external data (APIs, databases, search)
- The agent takes actions with side effects (send email, update record, create ticket)
- The agent needs real-time information (current time, live status, user account data)
- The agent cannot complete its task with only the information provided in the prompt

**When NOT to add tools:**
- The agent only processes information provided in the inputs
- The agent generates content without needing external data
- All necessary context is passed at invocation time

**If adding tools, consider:**
- Does each tool need user confirmation before execution? (Yes for actions with side effects)
- What happens if the tool fails? (Define fallback behavior)
- How many tool calls are acceptable per turn? (Rate limiting)
- Are there tools the agent should prefer over others? (Ordering/priority)

**Decision tree:**
```
Does the agent need external data or actions?
├── No → Don't add tools
└── Yes
    ├── Read-only data retrieval?
    │   └── Add lookup tools, no confirmation needed
    ├── Actions with side effects?
    │   └── Add action tools WITH confirmation requirements
    └── Both?
        └── Add both, with appropriate confirmation rules for each
```

#### Structured Output Modifier

**Reference:** `references/modifiers/output-type.md`

**When to use structured output:**
- The output is parsed by code (not just read by humans)
- Downstream systems, databases, or APIs consume the output
- Other agents receive the output and need specific fields
- You need machine-readable metadata alongside the main content

**When to use text output:**
- The output is primarily for human consumption
- Format can vary based on content
- The agent is conversational and outputs natural dialogue

**Even text-primary agents may need structured output for:**
- Confidence scores (for retry logic or quality gates)
- Reasoning traces (for debugging or transparency)
- Intent classification (for routing or analytics)
- Metadata (timestamps, sources, categories)

**Pattern for conversational + structured:**
```json
{
  "message": "Natural language response the user sees",
  "confidence": 0.85,
  "intent": "troubleshooting",
  "reasoning": "Brief explanation for system use"
}
```

**Decision tree:**
```
Is the output parsed by code or consumed by other agents?
├── Yes → Structured output
│   ├── Complex structure with multiple fields? → Define full schema
│   └── Simple value (category, yes/no)? → Minimal schema or strict text format
└── No (human consumption only)
    ├── Does the system need metadata (confidence, intent, reasoning)?
    │   ├── Yes → Structured output with message field for human content
    │   └── No → Text output
    └── Does format consistency matter?
        ├── Yes → Define format in <output_format>
        └── No → Minimal format guidance
```

#### Memory Modifier

**Reference:** `references/modifiers/memory.md`

**When to add memory:**
- The agent has multi-turn conversations where context matters
- The agent needs to remember what was said earlier in the session
- User requests build on previous exchanges ("do the same thing for X")
- The agent must avoid re-asking questions already answered

**When NOT to add memory:**
- Each invocation is independent (stateless processing)
- All necessary context is provided in the inputs
- The agent is called once per task with no follow-up

**Memory types:**
- **Conversation history**: Full message log passed each turn (most common for conversational)
- **Session state**: Structured state object tracking workflow progress (for complex multi-step flows)
- **No memory**: Each call is independent, all context in inputs (for Single-Turn)

**Decision tree:**
```
Is each invocation independent with all context in inputs?
├── Yes → No memory needed (stateless)
└── No (multi-turn or context-dependent)
    ├── Simple back-and-forth conversation?
    │   └── Conversation history
    ├── Complex workflow with many steps and states?
    │   └── Session state (structured)
    └── Agent-to-agent with multiple exchanges?
        └── Consider: explicit context passing vs. shared memory
```

#### Reasoning Modifier

**Reference:** `references/modifiers/reasoning.md`

**When to add reasoning:**
- The task involves multi-step logic, math, or complex problem-solving
- High-stakes accuracy is needed (reduce hallucination)
- You need the agent to "show its work" for transparency or debugging
- The problem benefits from exploring multiple solution paths

**When NOT to add reasoning:**
- Simple classification or extraction tasks
- Speed is critical (reasoning adds latency)
- The task is straightforward with obvious answers

**Reasoning techniques (choose based on need):**

| Technique | Use When | Token Overhead |
|-----------|----------|----------------|
| Zero-Shot CoT | General reasoning improvement | Low (+20-50%) |
| Chain-of-Verification | Factual accuracy critical | High (+100-200%) |
| Step-Back Prompting | Complex problems needing abstraction | Moderate (+50-100%) |
| Tree-of-Thoughts | Multiple valid approaches to compare | Very High (+200-400%) |

**Decision tree:**
```
Does the agent need to reason through complex problems?
├── No → Don't add reasoning
└── Yes
    ├── Is factual accuracy critical (high-stakes)?
    │   └── Chain-of-Verification
    ├── Does the problem need higher-level abstraction first?
    │   └── Step-Back Prompting
    ├── Are there multiple valid solution paths to explore?
    │   └── Tree-of-Thoughts
    └── General reasoning improvement needed?
        └── Zero-Shot Chain-of-Thought
```

#### Validation

Before proceeding, confirm modifier choices with the user. For each modifier (Tools, Structured Output, Memory, Reasoning), explain whether it's needed and why. Provide reasoning based on the agent's requirements. Get explicit confirmation before generating the prompt.

---

## Implementation Modifiers

Apply these to any role to add specific capabilities:

| Modifier | Description | Reference |
|----------|-------------|-----------|
| Output Type | Text vs Structured Output (Pydantic models) | `references/modifiers/output-type.md` |
| Tool Usage | Adding tool/function calling | `references/modifiers/tool-usage.md` |
| Memory | Single-turn vs conversation history | `references/modifiers/memory.md` |
| Reasoning | Chain-of-thought, verification, step-back prompting | `references/modifiers/reasoning.md` |

---

## Workflow

### Single Agent

1. **Select framework** — Single-Turn or Conversational based on interaction model
2. **Choose role** — Identify which role template best matches the agent's purpose
3. **Apply modifiers** — Add tools, structured output, or memory as needed
4. **Fill template** — Use the framework template, guided by role-specific advice
5. **Review** — Check against common pitfalls in the framework doc

### Multi-Agent Systems (Parallel Generation)

When building multiple agents at once, use sub-agents for parallel prompt generation:

**Phase 1: Requirements Gathering**
- Identify all agents needed in the system
- For each agent, determine: purpose, inputs, outputs, interactions with other agents
- Map the data flow between agents

**Phase 2: Selection (per agent)**
- Framework: Single-Turn vs Conversational
- Role: Which of the 8 roles fits
- Modifiers: Tools, structured output, memory

**Phase 3: Parallel Generation**

Dispatch a sub-agent for each prompt. Each sub-agent needs comprehensive context to write a complete prompt without further clarification.

**Required information for each sub-agent:**

```
## Agent Specification

**Agent Name:** [name]
**Purpose:** [1-2 sentence description of what this agent does]

## Framework & Role

**Framework:** Single-Turn | Conversational
**Reasoning:** [Why this framework fits - reference specific signals]

**Role:** [role_name]
**Reasoning:** [Why this role fits - what is the primary job]

## Modifiers

**Tools:** Yes | No
- If yes, list each tool:
  - Tool name and purpose
  - Parameters
  - When to use it
  - Expected response format
  - Error handling

**Structured Output:** Yes | No
- If yes, provide the schema:
  - Field names and types
  - Required vs optional fields
  - Example output

**Memory:** None | Conversation History | Session State
- If memory, describe what needs to persist

**Reasoning:** None | Chain-of-Thought | Chain-of-Verification | Step-Back | Tree-of-Thoughts
- If reasoning, specify which technique and why

## Agent Context

**Inputs:**
- [Input 1]: What it is, what it contains, how to use it
- [Input 2]: ...

**Outputs:**
- Format and structure
- What downstream systems expect
- Any validation requirements

**Upstream Agents:** (what sends data to this agent)
- [Agent name]: What data it provides, in what format

**Downstream Agents:** (what receives data from this agent)
- [Agent name]: What data it expects, in what format

## Domain Context

**Business Context:** [What system/product this is part of]
**User Context:** [Who interacts with this agent, if applicable]
**Constraints:** [Any hard rules, compliance requirements, limitations]

## Behavioral Requirements

**Key Behaviors:**
- [Specific behavior 1]
- [Specific behavior 2]

**Edge Cases:**
- [Edge case 1]: How to handle
- [Edge case 2]: How to handle

**What This Agent Should NOT Do:**
- [Explicit constraint 1]
- [Explicit constraint 2]
```

**Sub-agent process:**
1. Read the framework template from `references/frameworks/[framework].md`
2. Read the role guidance from `references/roles/[role].md`
3. Read relevant modifier files from `references/modifiers/`
4. Read prompt engineering guidelines from `references/guidelines/prompt-writing.md`
5. Write the complete prompt using framework template structure
6. Apply role-specific section guidance
7. Incorporate modifier patterns where applicable
8. Return the complete prompt

**Invoking the Prompt-Creator Sub-Agent:**

Use the Task tool with `subagent_type='prompt-creator'` to generate prompts. The sub-agent has access to Read, Glob, and Grep tools and can discover the reference files automatically.

```
Task(
  subagent_type: 'prompt-creator',
  prompt: [full specification below]
)
```

**Reference file structure (relative to skill location):**

```
prompt-engineering/
├── SKILL.md
└── references/
    ├── frameworks/
    │   ├── single-turn.md
    │   └── conversational.md
    ├── roles/
    │   ├── researcher.md
    │   ├── critic-reviewer.md
    │   ├── router-classifier.md
    │   ├── creative-generator.md
    │   ├── planner-strategist.md
    │   ├── summarizer-synthesizer.md
    │   ├── conversational-assistant.md
    │   └── transformer-formatter.md
    ├── modifiers/
    │   ├── tool-usage.md
    │   ├── output-type.md
    │   ├── memory.md
    │   └── reasoning.md
    └── guidelines/
        └── prompt-writing.md
```

**Sub-agent prompt template:**

```markdown
You are a prompt engineering specialist. Create a complete system prompt for an agent using the specification below.

## Step 1: Locate the Skill Files

First, find the prompt engineering skill location:

1. Use Glob to find: `**/prompt-engineering/SKILL.md`
2. Extract the base directory from the result (e.g., if found at `/path/to/prompt-engineering/SKILL.md`, the base is `/path/to/prompt-engineering`)
3. All reference files are relative to this base directory

## Step 2: Read Required Files

Using the base directory, read these files:

**Framework (read ONE based on specification):**
- Single-Turn: `{base}/references/frameworks/single-turn.md`
- Conversational: `{base}/references/frameworks/conversational.md`

**Role (read ONE based on specification):**
- Researcher: `{base}/references/roles/researcher.md`
- Critic/Reviewer: `{base}/references/roles/critic-reviewer.md`
- Router/Classifier: `{base}/references/roles/router-classifier.md`
- Creative/Generator: `{base}/references/roles/creative-generator.md`
- Planner/Strategist: `{base}/references/roles/planner-strategist.md`
- Summarizer/Synthesizer: `{base}/references/roles/summarizer-synthesizer.md`
- Conversational/Assistant: `{base}/references/roles/conversational-assistant.md`
- Transformer/Formatter: `{base}/references/roles/transformer-formatter.md`

**Modifiers (read IF specified):**
- Tools: `{base}/references/modifiers/tool-usage.md`
- Structured Output: `{base}/references/modifiers/output-type.md`
- Memory: `{base}/references/modifiers/memory.md`
- Reasoning: `{base}/references/modifiers/reasoning.md`

**Always read:**
- Prompt Writing Guidelines: `{base}/references/guidelines/prompt-writing.md`

## Step 3: Write the Prompt

1. Use the framework template as your structure
2. Apply role-specific section guidance
3. Incorporate modifier patterns where applicable
4. Follow prompt writing guidelines for quality

## Agent Specification

[Paste the full specification here - see "Required information for each sub-agent" above]

## Output

Return the complete system prompt wrapped in a markdown code block. The prompt should:
- Follow the framework's XML section structure
- Apply all role-specific guidance
- Include all modifiers
- Be production-ready (no placeholders, no TODOs)
```

**Phase 4: Integration**
- Review generated prompts for consistency across the system
- Ensure inter-agent communication formats match (Agent A's output schema = Agent B's expected input)
- Verify structured outputs align with downstream requirements
- Check for conflicting constraints or behaviors between agents
- Validate that all edge cases are covered across the agent chain

---

## Composition: How It All Fits Together

Building a prompt follows this pattern: **Framework + Role + Modifiers**

### Step 1: Start with the Framework Template

The framework provides the XML structure and required sections:

**Single-Turn gives you:**
```
<who_you_are> → <skill_map> → <context> → <inputs> → <task> → <output_format> → <important_notes>
```

**Conversational gives you:**
```
<who_you_are> → <tone_and_style> → <context> → <inputs> → <knowledge_scope> → <capabilities> → <operational_logic> → <examples> → <output_format> → <constraints_and_safeguards>
```

### Step 2: Apply Role Guidance to Each Section

Open the role file and fill each section using the section-by-section guidance:

| Section | Role file tells you... |
|---------|------------------------|
| `<who_you_are>` | What expertise to emphasize, what to avoid |
| `<skill_map>` | Which skills are relevant for this role |
| `<inputs>` | What inputs this role typically needs |
| `<task>` | How to structure the task steps for this role |
| `<output_format>` | What output structure works for this role |
| `<important_notes>` | Role-specific constraints and edge cases |

### Step 3: Layer in Modifiers

If your agent needs tools, structured output, or memory:

1. Read the modifier file for general patterns
2. Check the role file's **Modifier Notes** section for role-specific advice
3. Add the modifier content to the appropriate sections

**Example combinations:**

| Agent | Framework | Role | Modifiers |
|-------|-----------|------|-----------|
| Email analyzer | Single-Turn | Researcher | Structured Output |
| Support chatbot | Conversational | Conversational/Assistant | Tools + Memory |
| Data migrator | Single-Turn | Transformer/Formatter | Structured Output |
| Code reviewer | Single-Turn | Critic/Reviewer | Tools (git, linter) |
| Sales copilot | Conversational | Creative/Generator | Tools + Memory |

### Composition Example

Building a **competitive research agent**:

1. **Framework:** Single-Turn (discrete task, defined inputs/outputs)
2. **Role:** Researcher
3. **Modifiers:** Structured Output (feeds into dashboard)

**Process:**
- Start with Single-Turn template sections
- Fill `<who_you_are>` using Researcher guidance: "Specify research domain, include methodological strengths"
- Fill `<task>` using Researcher guidance: "Structure as: understand scope → gather data → synthesize → format"
- Fill `<output_format>` using Researcher guidance: "Separate raw findings from synthesis, include Gaps and Limitations"
- Add Structured Output: Define Pydantic schema matching the output structure
- Check Researcher Modifier Notes: "Schema should separate findings (facts) from analysis (inferences)"

---

## Prompt Engineering Guidelines

### Structure

**Use XML tags for sections**
Research shows ~15% performance improvement over natural language structure. Use descriptive tag names that match section purpose.

```xml
<who_you_are>...</who_you_are>
<task>...</task>
<output_format>...</output_format>
```

**Position constraints last**
LLMs weight the end of prompts more heavily (recency effect). Put rules, constraints, and "never do X" statements at the end.

**Keep sections focused**
Each section should have one purpose. Don't mix task instructions with output format. Don't mix identity with constraints.

### Content

**Be explicit about knowledge boundaries**
State what the agent **doesn't** know. This prevents hallucination. "You do not have access to X" is more effective than hoping it won't try.

```xml
<knowledge_scope>
You know: [explicit list]
You do NOT know: [explicit list]
When uncertain: Say "I don't have that information" rather than guessing
</knowledge_scope>
```

**Define negative space**
What the agent should NOT do is as important as what it should do. Include explicit constraints.

```xml
<important_notes>
- Never fabricate sources or citations
- Do not answer questions outside your knowledge scope
- If a tool fails, do not retry more than twice
</important_notes>
```

**Use examples for complex behavior**
For conversational agents or nuanced tasks, examples anchor behavior better than abstract instructions. Show 2-3 examples covering different scenarios.

### Writing Style

**Be concise**
Longer prompts increase hallucination rates. Every sentence should earn its place. Cut filler words and redundant explanations.

**Use active, direct language**
- Good: "Return a JSON object with..."
- Bad: "You should try to return a JSON object that contains..."

**Avoid hedging**
- Good: "Always confirm before taking action"
- Bad: "You might want to consider confirming before taking action"

**Number lists and steps**
Numbered steps are easier to follow than prose. Use them for task sequences, rules, and priorities.

### Common Mistakes

| Mistake | Fix |
|---------|-----|
| No knowledge boundaries | Add explicit "you don't know" list |
| Missing edge cases | Add handling for nulls, errors, empty inputs |
| Vague output format | Provide exact structure with examples |
| No fallback behavior | Define what happens when things fail |
| Implicit assumptions | State assumptions explicitly |
| Over-engineering | Start minimal, add complexity only when needed |

### Testing Checklist

Before deploying a prompt:
- [ ] Does it handle empty/null inputs?
- [ ] Does it have explicit knowledge boundaries?
- [ ] Are constraints positioned at the end?
- [ ] Does the output format match what downstream expects?
- [ ] Are all edge cases covered in important_notes?
- [ ] For conversational: are there sufficient examples?
- [ ] For tools: is each tool documented with when/how/errors?

---

## References

- `references/frameworks/` — Base templates (Single-Turn, Conversational)
- `references/roles/` — Role-specific guidance (8 roles)
- `references/modifiers/` — Implementation features (Tools, Structured Output, Memory)
- `references/guidelines/` — Prompt writing techniques and best practices
