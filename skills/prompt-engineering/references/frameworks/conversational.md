# Framework 2: Conversational Agent

## Purpose

For agents that engage in multi-turn, stateful interactions — ongoing dialogue with context tracking, clarification loops, and ambiguity resolution.

---

## When to Use

- Multi-turn dialogue with users
- User-facing assistants with varied capabilities
- Agents that need to ask clarifying questions
- Stateful interactions that build on previous turns
- Open-ended requests where scope emerges through conversation

---

## When NOT to Use

- **Single-turn task with clear output** → Use Single-Turn framework
- **Agent-to-agent communication** → Use Single-Turn framework
- **Processing/transformation task** → Use Single-Turn framework
- **All inputs known upfront, no clarification needed** → Use Single-Turn framework
- **Output is structured data, not dialogue** → Use Single-Turn framework

---

## Selection Criteria

Ask these questions to confirm Conversational is the right fit:

| Question | If Yes → | If No → |
|----------|----------|---------|
| Will there be back-and-forth with a user? | Conversational | Consider Single-Turn |
| Does the agent need to ask clarifying questions? | Conversational | Consider Single-Turn |
| Is persona/tone consistency across turns important? | Conversational | Single-Turn may suffice |
| Will the scope emerge through dialogue? | Conversational | Consider Single-Turn |
| Is this user-facing (not agent-to-agent)? | Conversational | Single-Turn preferred |

**Quick decision:** If the agent needs to maintain context across turns, handle follow-ups, or adapt based on user responses, use Conversational.

---

## Template

```xml
<who_you_are>
[Agent name, role, personality, and relationship to the user. Establishes identity
and primary objectives. What success looks like for this agent.]
</who_you_are>

<tone_and_style>
[Communication register, formality level, verbosity preferences, emotional range,
language patterns. How the agent expresses itself independent of who it is.]
</tone_and_style>

<context>
[Operational environment: where the agent is deployed, platform/channel,
who the users are, any situational constraints or business rules.]
</context>

<inputs>
[Runtime-injected data available to the agent. For each input:]

**[Input Name]**
- What it is: [Clear definition]
- Information included: [List of data points]
- How to use it: [Specific application guidance]

[Examples: user account details, subscription tier, conversation history,
CRM fields, session metadata, previous tickets]
</inputs>

<knowledge_scope>
[What the agent knows: domain expertise, methodologies, reference materials.
What the agent does NOT know: temporal boundaries, capability limits,
topics outside scope. Explicitly stating boundaries prevents hallucination.]
</knowledge_scope>

<capabilities>
[User-facing functions the agent can perform. For tool-using agents, include:]
- Capability name and description
- Available tools/functions with parameters
- When to invoke each tool
- Expected responses and error handling
</capabilities>

<operational_logic>
[How the agent executes tasks and manages conversation:]
- Workflow patterns with conditionals (IF/THEN/ELSE)
- State management across turns
- Information gathering sequences
- Clarification and ambiguity resolution
- Turn-taking norms and conversation repair
</operational_logic>

<examples>
[2-4 few-shot demonstrations showing:]
- Ideal conversation flows
- Tone and response structure
- Edge case handling
- Tool invocation patterns (if applicable)

Format as User/Agent dialogue pairs.
</examples>

<output_format>
[Response structure and formatting requirements:]
- Length guidelines (concise vs. detailed, by situation)
- When to use structure (bullets, numbered lists) vs. prose
- Any structured outputs (summaries, confirmations, handoff notes)
- Consistency rules across turns
</output_format>

<constraints_and_safeguards>
[Positioned last to exploit recency effect. Include:]
- Hard rules and prohibited behaviours
- Safety and ethical boundaries
- Error recovery procedures
- Confirmation checkpoints for critical actions
- Escalation triggers and handoff criteria
- Success criteria (how to know task is complete)
</constraints_and_safeguards>
```

---

## Section Reference

| Section | Purpose | Required |
|---------|---------|----------|
| `<who_you_are>` | Identity, role, objectives | **Required** |
| `<tone_and_style>` | Communication style | **Required** |
| `<context>` | Operational environment | **Required** |
| `<inputs>` | Runtime-injected data | Optional |
| `<knowledge_scope>` | Domain + explicit boundaries | **Required** |
| `<capabilities>` | Functions and tools | **Required** |
| `<operational_logic>` | Workflow and conversation flow | **Required** |
| `<examples>` | Few-shot demonstrations | **Strongly recommended** |
| `<output_format>` | Response structure | Optional |
| `<constraints_and_safeguards>` | Rules and boundaries | **Required** |

---

## Section Details

### `<who_you_are>`

Establishes identity, objectives, and what success looks like. More expansive than the Single-Turn version because conversational agents need a consistent persona across turns.

**Good example:**
```xml
<who_you_are>
You are Maya, a customer success specialist at Acme Software. Your role is to
help customers get maximum value from their subscription. Success means customers
leave the conversation with a clear path forward and feel heard.

You report to the Customer Success team and can escalate to human agents when needed.
</who_you_are>
```

### `<tone_and_style>`

Separated from identity because the same persona might use different tones in different contexts. Define how the agent communicates.

**Good example:**
```xml
<tone_and_style>
- Professional but warm — avoid corporate jargon
- Concise responses (2-3 sentences typical, expand when explaining complex topics)
- Use the customer's name occasionally but not excessively
- Match the customer's energy level — if they're frustrated, acknowledge it first
- Avoid exclamation marks unless the customer uses them
- Use "I" statements ("I can help with that") rather than passive voice
</tone_and_style>
```

### `<context>`

Where the agent operates, who the users are, and situational constraints.

**Good example:**
```xml
<context>
You operate in Acme's live chat widget on the dashboard. Users are existing
customers (not prospects). Most conversations happen during business hours
but the chat is available 24/7.

Users have already authenticated, so you have access to their account details.
Average conversation length is 4-6 turns.
</context>
```

### `<inputs>`

Runtime data injected into the conversation. Unlike Single-Turn, this data may be updated mid-conversation.

**Good example:**
```xml
<inputs>
**User Account**
- What it is: Customer's account information
- Information included: Name, email, subscription tier, account age, recent activity
- How to use it: Personalize responses, check entitlements before suggesting features

**Conversation History**
- What it is: Previous messages in this chat session
- Information included: Full message history with timestamps
- How to use it: Maintain context, avoid asking questions already answered
</inputs>
```

### `<knowledge_scope>`

Critical section. Explicitly state what the agent knows AND what it doesn't. This prevents hallucination.

**Good example:**
```xml
<knowledge_scope>
**What you know:**
- Acme Software product features (as of v3.2)
- Common troubleshooting procedures
- Pricing and subscription tiers
- Integration options with Salesforce, HubSpot, Slack

**What you do NOT know:**
- Future product roadmap (say "I don't have visibility into upcoming features")
- Other customers' data or usage patterns
- Technical implementation details of the backend
- Anything that happened after January 2024
- Custom enterprise configurations (escalate these)
</knowledge_scope>
```

### `<capabilities>`

What the agent can do. For tool-using agents, include tool specifications.

**Good example:**
```xml
<capabilities>
1. **Answer product questions** — Explain features, compare plans, clarify pricing
2. **Troubleshoot issues** — Walk through common fixes, collect diagnostic info
3. **Update account settings** — Change notification preferences, update billing email
   - Tool: `update_account_settings(field, new_value)`
   - Requires confirmation before executing
4. **Create support tickets** — For issues requiring engineering attention
   - Tool: `create_ticket(category, priority, description)`
5. **Escalate to human** — Transfer to live agent when needed
   - Tool: `escalate_to_human(reason)`
</capabilities>
```

### `<operational_logic>`

How the agent manages the conversation. Include conditionals and decision logic.

**Good example:**
```xml
<operational_logic>
**Opening:**
- Greet using the customer's first name
- If they state an issue immediately, acknowledge and address it
- If they just say "hi" or similar, ask how you can help

**Information gathering:**
- Ask one question at a time
- Summarize your understanding before proposing solutions
- If the issue is unclear after 2 attempts, offer to escalate

**Resolution flow:**
- IF issue is in known troubleshooting database → walk through steps
- IF issue requires account changes → confirm before making changes
- IF issue is outside your capabilities → escalate with context

**Closing:**
- Confirm the issue is resolved before closing
- Offer additional help
- Thank the customer
</operational_logic>
```

### `<examples>`

Few-shot examples are essential for conversational agents. Show 2-4 dialogue pairs covering typical flows and edge cases.

**Good example:**
```xml
<examples>
**Example 1: Typical support request**

User: "I can't find where to change my password"
Agent: "I can help with that, Sarah. To change your password, go to Settings > Security >
Change Password. You'll need to enter your current password first. Would you like me to
walk you through each step?"
User: "No that's enough, found it. Thanks!"
Agent: "Great! Is there anything else I can help you with today?"

**Example 2: Ambiguous request**

User: "This thing isn't working"
Agent: "I'm sorry to hear that. To help you quickly, could you tell me which feature
isn't working as expected? For example, is it related to login, reports, or something else?"

**Example 3: Out of scope**

User: "When are you adding Notion integration?"
Agent: "I don't have visibility into the product roadmap, so I can't give you a timeline
on Notion integration. I'd suggest checking our public roadmap at acme.com/roadmap or
submitting a feature request there. Is there something else I can help with?"
</examples>
```

### `<output_format>`

Response structure guidelines. Optional for simple conversational agents.

**Good example:**
```xml
<output_format>
- Keep responses to 1-3 sentences for simple questions
- For troubleshooting, use numbered steps
- When listing options, use bullet points (max 4 options)
- Always end with a question or clear next step during active troubleshooting
- When closing, don't ask a question — make a statement
</output_format>
```

### `<constraints_and_safeguards>`

Rules, boundaries, and verification requirements. **Positioned last to exploit recency effect.**

**Good example:**
```xml
<constraints_and_safeguards>
**Hard rules:**
- Never share one customer's information with another
- Never promise features or timelines you can't confirm
- Never process refunds or billing changes (escalate these)
- Always confirm before making account changes

**Escalation triggers:**
- Customer explicitly asks for a human
- Issue involves billing disputes over $100
- Customer expresses significant frustration (3+ negative messages)
- Issue is outside your documented capabilities

**Success criteria:**
- Customer confirms issue is resolved, OR
- Customer is successfully escalated with full context, OR
- Customer voluntarily ends the conversation satisfied
</constraints_and_safeguards>
```

---

## Design Rationale

### Why 10 Sections?

Each section serves a distinct purpose. While this is more than Single-Turn, conversational agents have more concerns to address (persona consistency, conversation flow, clarification, etc.).

For simpler agents, mark optional sections as "N/A" rather than removing them — this maintains structural consistency.

### Why `<constraints_and_safeguards>` is Last

Research on LLM attention patterns shows a U-shaped curve (primacy-recency effect). Content at the beginning and end receives more weight. Placing constraints last ensures they're highly weighted during generation.

### For Long Prompts

If your prompt exceeds ~800 words, consider:
1. Repeating the most critical constraints at the very end
2. Trimming examples to 2 instead of 4
3. Moving detailed tool specifications to a separate reference document

---

## Common Pitfalls

1. **Missing knowledge boundaries** — Always state what the agent doesn't know
2. **Skipping examples** — Few-shot examples anchor behaviour more than instructions
3. **Overloaded capabilities** — If you have 10+ capabilities, consider specialised agents
4. **Vague operational logic** — Be explicit about conditionals and decision points
5. **Tone/identity confusion** — Separate who the agent is from how they communicate
6. **Missing escalation criteria** — Always define when to hand off to humans

---

## With Structured Output Modifier

Conversational agents can output structured data while maintaining dialogue capabilities. Use this when you need machine-parseable output alongside natural conversation.

### When to Apply

- Confidence scoring for retry/routing logic
- Metadata for logging and analytics
- Agent-to-agent handoff with structured context
- Downstream automation that parses agent responses

### What Changes

**`<output_format>` section becomes required and defines the schema:**

```xml
<output_format>
Return a JSON object for every response:

{
  "message": "Your natural language response to the user",
  "confidence": 0.0-1.0,
  "intent": "question" | "troubleshooting" | "account_change" | "escalation" | "closing",
  "reasoning": "Brief explanation of your approach (1 sentence)",
  "requires_followup": true | false
}

The "message" field contains what the user sees. Other fields are for system use.
</output_format>
```

**`<examples>` section shows structured responses:**

```xml
<examples>
**Example 1: Typical support request**

User: "I can't find where to change my password"
Agent:
{
  "message": "I can help with that, Sarah. Go to Settings > Security > Change Password. Would you like me to walk you through each step?",
  "confidence": 0.95,
  "intent": "troubleshooting",
  "reasoning": "Clear request with known solution path",
  "requires_followup": true
}
</examples>
```

**`<operational_logic>` may include confidence-based rules:**

```xml
<operational_logic>
**Confidence thresholds:**
- confidence >= 0.8: Proceed with response
- confidence 0.5-0.8: Add hedging language, offer to clarify
- confidence < 0.5: Ask clarifying question before responding

**Intent-based routing:**
- IF intent == "escalation" → system routes to human
- IF intent == "account_change" → system requires confirmation step
</operational_logic>
```

### Key Difference from Pure Single-Turn

The agent is still conversational—it maintains context, asks follow-ups, handles ambiguity. The structured output is a *wrapper* around the conversational response, not a replacement for it.

---

## Comparison to Single-Turn

| Concern | Single-Turn | Conversational |
|---------|----------------|----------------|
| Interaction model | Single turn, stateless | Multi-turn, stateful |
| Input handling | Pre-defined, structured | Starting context + gathered through dialogue |
| Conversation flow | N/A | `<operational_logic>` handles turn management |
| Ambiguity | Assumed resolved in inputs | Agent must clarify and recover |
| Tone/Style | Minimal concern | Critical for user experience |
| Examples | Optional | Essential for anchoring dialogue patterns |
| Knowledge boundaries | Less critical (scoped task) | Prevents hallucination across open-ended queries |
