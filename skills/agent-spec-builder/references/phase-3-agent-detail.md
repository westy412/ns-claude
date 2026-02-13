# Phase 3: Agent Detail

Capture enough detail per agent for autonomous implementation. Teams are orchestration logic; agents do the actual work. Agent specs must be detailed enough for the impl-builder to work without guessing.

---

## Skill Loading

**Load skills ONE AT A TIME when you reach this phase:**

1. First, invoke `skill: "individual-agents"` — for agent type selection
   - Use this to determine types for all agents
   - Update progress.md with agent type decisions and rationale
   - Then proceed to prompt configuration for each agent

2. Then, invoke `skill: "prompt-engineering"` — for prompt configuration
   - Use this for framework, role, and modifier selection per agent
   - Update progress.md with prompt config decisions per agent

**Before invoking either skill:** Ensure progress.md has complete Phase 2 results (pattern, agents identified, flow diagram).

**Context check:** If context is becoming large after individual-agents, consider triggering a session handover BEFORE loading prompt-engineering. Progress.md should have enough state for a new session to load prompt-engineering fresh.

**Alternative: Use sub-agents** to offload analysis without consuming your context. See `references/sub-agent-delegation.md` for the full delegation workflow.

---

## Per-Agent Detail Checklist

For each agent, capture the following:

### Purpose (6 items)

| Section | What to Capture |
|---------|-----------------|
| **Goal** | What outcome this agent achieves |
| **Approach** | How it achieves that outcome (high-level method) |
| **Primary Responsibility** | One sentence summary of core job |
| **Key Tasks** | Bulleted list of specific things it does |
| **Success Criteria** | What good output looks like (measurable) |
| **Scope Boundaries** | What this agent does NOT do |

### Framework & Role

Use the `prompt-engineering` skill (invoked above) for selection criteria.

**Framework:** Single-Turn vs Conversational
- Single-Turn: Discrete task, all info upfront, no dialogue
- Conversational: Multi-turn, context across turns, ongoing dialogue

**Role:** One of 8 roles
- Researcher, Critic-Reviewer, Router-Classifier, Creative-Generator
- Planner-Strategist, Summarizer-Synthesizer, Conversational-Assistant, Transformer-Formatter

Include reasoning for each choice.

### LLM Configuration

For each agent, determine the model configuration:

| Setting | Options | Considerations |
|---------|---------|----------------|
| **Provider** | anthropic / openai / google / local | API access, cost, compliance |
| **Model** | claude-3-5-sonnet, gpt-4-turbo, etc. | Capability vs cost tradeoff |
| **Reasoning** | Yes / No | Does this agent need extended thinking? |
| **Temperature** | 0.0 - 1.0 | Lower for consistency, higher for creativity |

**Questions to ask:**
> "Should this agent use a smaller/faster model, or does it need the most capable one?"
> "Does this agent need reasoning capabilities (chain-of-thought, extended thinking)?"
> "Any cost constraints that affect model choice?"

**Default recommendations:**
- **Critic/Reviewer agents:** Higher capability model (needs nuanced judgment)
- **Router/Classifier agents:** Smaller/faster model (simple classification)
- **Creative agents:** May benefit from higher temperature
- **Structured output agents:** Lower temperature for consistency

**Record in agent spec** under LLM Configuration section with reasoning for each choice.

### Modifiers

| Modifier | What to Capture |
|----------|-----------------|
| **Tools** | Each tool: name, purpose, parameters, when to use, response format, error handling |
| **Structured Output** | Schema: field names, types, required/optional, example |
| **Memory** | None / Conversation History / Session State - what persists |
| **Reasoning** | None / CoT / CoV / Step-Back / ToT - which technique, why |

### Inputs & Outputs

For each input/output:
- Name
- Description
- Format
- Source (inputs) / Consumed by (outputs)

### Context Flow

Make explicit: Output of Agent A = Input of Agent B.

- **Upstream:** What agent sends data, what data, what format
- **Downstream:** What agent receives data, what data, what format

### Domain Context

- **Business Context:** What system/product this is part of
- **User Context:** Who interacts (if applicable)
- **Constraints:** Hard rules, compliance, limitations

### Behavioral Requirements

- **Key Behaviors:** Specific behaviors required
- **Edge Cases:** What could go wrong, how to handle
- **What NOT to do:** Explicit constraints

### Examples

At least one example showing:
- Sample input
- Expected output

---

## When to Split an Agent

Watch for signals that one agent is doing too much:
- Too many responsibilities
- Complex decision trees
- Multiple distinct outputs

Help user recognize when to split into multiple agents.

**After each agent:** Update progress document with agent progress checklist.
