# Framework 1: Single-Turn Agent

## Purpose

For agents that perform a discrete, non-interactive task. They receive a defined set of inputs and produce a defined output without back-and-forth conversation.

---

## When to Use

- Single-turn task with clear inputs and outputs
- Agent-to-agent communication in a pipeline
- Processing, transformation, or analysis tasks
- Any task where the scope is fully defined upfront

---

## When NOT to Use

- **Multi-turn dialogue needed** → Use Conversational framework
- **User-facing with varied requests** → Use Conversational framework
- **Agent needs to ask clarifying questions** → Use Conversational framework
- **Scope isn't known upfront** → Use Conversational framework
- **Persona/tone consistency across turns matters** → Use Conversational framework

---

## Selection Criteria

Ask these questions to confirm Single-Turn is the right fit:

| Question | If Yes → | If No → |
|----------|----------|---------|
| Is this a single-turn task? | Single-Turn | Consider Conversational |
| Are all inputs known before the agent runs? | Single-Turn | Consider Conversational |
| Is the output format fixed and predictable? | Single-Turn | Consider Conversational |
| Is this agent-to-agent (not user-facing)? | Single-Turn | Evaluate based on interaction |
| Can the task complete without clarification? | Single-Turn | Consider Conversational |

**Quick decision:** If the agent receives everything it needs upfront and produces a single output without needing to ask questions, use Single-Turn.

---

## Template

```xml
<who_you_are>
[Agent description: who they are, their role, their expertise]
</who_you_are>

<skill_map>
[List of critical skills and aptitudes this agent possesses]
</skill_map>

<context>
[Description of the agent's operational environment, where it sits in the workflow,
what happens before and after it runs]
</context>

<inputs>
[For each input, complete the block below]

**[Input Name]**
- What it is: [Clear definition]
- Information included: [List of data points]
- How to use it: [Specific application in this prompt]
</inputs>

<task>
[Detailed, ordered list of steps the agent must perform]

1. [First step]
2. [Second step]
3. [Continue as needed...]
</task>

<output_format>
[Specific format requirements, schema, or example of expected output]
</output_format>

<important_notes>
[Key constraints, rules, edge-case instructions, things to never do]
</important_notes>
```

---

## Section Reference

| Section | Purpose | Required |
|---------|---------|----------|
| `<who_you_are>` | Agent identity and expertise | Yes |
| `<skill_map>` | Core competencies | Yes |
| `<context>` | Operational environment | Yes |
| `<inputs>` | Runtime data with usage guidance | Yes |
| `<task>` | Step-by-step instructions | Yes |
| `<output_format>` | Expected output structure | Yes |
| `<important_notes>` | Constraints and rules | Yes |

---

## Section Details

### `<who_you_are>`

Establishes the agent's identity and expertise. Keep it concise but specific.

**Good example:**
```xml
<who_you_are>
You are a senior email analyst specializing in B2B sales communication.
You have deep expertise in identifying buying signals, objections, and
sentiment in prospect responses.
</who_you_are>
```

**Avoid:**
- Generic descriptions ("You are a helpful assistant")
- Overly long backstories
- Contradictory traits

### `<skill_map>`

Lists the specific capabilities relevant to the task. Helps the model "activate" relevant knowledge.

**Good example:**
```xml
<skill_map>
- Email sentiment analysis
- B2B sales process understanding
- Objection identification and categorization
- Buying signal detection
</skill_map>
```

### `<context>`

Describes where this agent operates — what comes before it, what comes after, who consumes its output.

**Good example:**
```xml
<context>
You are part of an email reply generation pipeline. You receive prospect
emails and your analysis is used by a downstream Reply Writer agent.
Your output directly influences the tone and strategy of the reply.
</context>
```

### `<inputs>`

Documents each piece of runtime data the agent receives. The "How to use it" field is critical — it tells the agent exactly what to do with each input.

**Good example:**
```xml
<inputs>
**Prospect Email**
- What it is: The email received from the prospect
- Information included: Subject line, body text, sender name
- How to use it: Analyze for sentiment, buying signals, and objections

**Thread History**
- What it is: Previous emails in this conversation thread
- Information included: Up to 5 previous messages with timestamps
- How to use it: Understand conversation context and progression
</inputs>
```

### `<task>`

Numbered steps the agent must follow. Be explicit about order and what each step produces.

**Good example:**
```xml
<task>
1. Read the prospect email and thread history
2. Identify the primary sentiment (positive, negative, neutral, mixed)
3. List any buying signals present (budget mentions, timeline questions, etc.)
4. List any objections or concerns raised
5. Determine the recommended reply strategy
6. Output your analysis in the specified format
</task>
```

### `<output_format>`

Defines exactly what the output should look like. For structured output agents, this might reference a schema. For text agents, provide an example.

**Good example:**
```xml
<output_format>
Return your analysis as follows:

SENTIMENT: [positive/negative/neutral/mixed]
BUYING_SIGNALS:
- [signal 1]
- [signal 2]
OBJECTIONS:
- [objection 1]
- [objection 2]
RECOMMENDED_STRATEGY: [1-2 sentence recommendation]
</output_format>
```

### `<important_notes>`

Constraints, rules, and edge cases. **This section is positioned last intentionally** — the recency effect means LLMs weight content at the end of prompts more heavily.

**Good example:**
```xml
<important_notes>
- If the email is an auto-reply or out-of-office, output SENTIMENT: neutral and
  leave other fields empty
- Never infer sentiment from thread history alone — focus on the current email
- If no buying signals are present, explicitly state "None identified"
- Keep RECOMMENDED_STRATEGY to 2 sentences maximum
</important_notes>
```

---

## Design Rationale

### Why `<important_notes>` is Last

Research on LLM attention patterns shows a U-shaped curve (primacy-recency effect). Content at the beginning and end receives more weight. Placing constraints last ensures they're highly weighted during generation.

### For Long Prompts

If your prompt exceeds ~500 words, consider repeating the most critical constraints at the very end, even if they appear in `<important_notes>`. Example:

```xml
<important_notes>
[Your constraints here]
</important_notes>

CRITICAL: Never output personally identifiable information.
```

---

## Common Pitfalls

1. **Vague inputs** — Each input needs clear "How to use it" guidance
2. **Missing edge cases** — Think through what happens with empty, malformed, or unusual inputs
3. **Ambiguous output format** — If you want a specific structure, show an example
4. **Overloaded task section** — If you have 10+ steps, consider splitting into multiple agents
5. **Forgetting context** — Agents work better when they know where they fit in the workflow

---

## Example: Complete Prompt

```xml
<who_you_are>
You are a data extraction specialist. You excel at pulling structured
information from unstructured text with high accuracy.
</who_you_are>

<skill_map>
- Named entity recognition
- Date and number extraction
- Pattern matching
- Data normalization
</skill_map>

<context>
You process incoming customer support tickets. Your extracted data is
used to route tickets to the appropriate team and set priority levels.
</context>

<inputs>
**Support Ticket**
- What it is: Raw text of a customer support ticket
- Information included: Subject, body, customer email
- How to use it: Extract structured fields as specified in output format
</inputs>

<task>
1. Read the support ticket
2. Extract the customer's name if mentioned
3. Identify the product or service being discussed
4. Determine the issue category (billing, technical, account, other)
5. Assess urgency (high, medium, low) based on language
6. Output in the specified format
</task>

<output_format>
CUSTOMER_NAME: [name or "Unknown"]
PRODUCT: [product name or "Unspecified"]
CATEGORY: [billing/technical/account/other]
URGENCY: [high/medium/low]
SUMMARY: [One sentence summary of the issue]
</output_format>

<important_notes>
- If the ticket is in a language other than English, set CATEGORY to "other"
  and note the language in SUMMARY
- For urgency, words like "urgent", "ASAP", "broken", "can't access" indicate high
- Never guess the customer name from the email address
- If multiple products are mentioned, list the primary one being discussed
</important_notes>
```
