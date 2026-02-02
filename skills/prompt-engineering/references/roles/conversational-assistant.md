# Conversational/Assistant Agent

## Role Description
Maintains dialogue with users across multiple turns, handling follow-ups, clarifications, and evolving requests. Conversational assistants are user-facing agents that must balance helpfulness with appropriate boundaries, manage ambiguity gracefully, and maintain consistent persona throughout the interaction.

## When to Use
- The agent will have back-and-forth exchanges with a user over multiple turns
- The agent needs to remember and reference earlier parts of the conversation
- The agent must handle clarifications, follow-up questions, or evolving requests
- User experience and tone matter as much as the information delivered

## When NOT to Use
- Single-turn question answering with no follow-up expected → Use Answerer/Expert instead
- Processing data and returning structured results → Use Processor/Transformer instead
- Autonomous task execution without user interaction → Use Orchestrator or Executor instead

## Selection Criteria
- Is the agent's primary job to interact with humans in dialogue? → Yes = this role
- Will the conversation span multiple turns with context dependencies? → Yes = this role
- Does the agent need to handle "I meant something else" or "what about X"? → Yes = this role
- Is the output a processed result rather than a conversation? → If yes, consider Processor/Transformer

## Framework Fit
**Primary:** Conversational
**Why:** Multi-turn dialogue is the defining characteristic. The agent must maintain state, remember context, handle turn-taking, and adapt responses based on conversation flow.
**When to use the other:** Almost never. If you have a "single-turn assistant" that processes a request and returns a result without follow-up, it's actually a Processor or Answerer wearing an assistant costume.

## Section-by-Section Guidance

### For Conversational Framework:

**`<who_you_are>`**
- Define the agent's identity and relationship to the user (support rep, advisor, helper)
- Establish personality traits that affect interaction style (patient, efficient, warm)
- Specify what success looks like from this agent's perspective
- Avoid: Lengthy backstories or capabilities lists (those go elsewhere)

**`<tone_and_style>`**
- Define communication style along key dimensions: formal/casual, concise/detailed, warm/neutral
- Specify how to handle emotional moments (frustration, confusion, excitement)
- Set expectations for response length and structure in conversational context
- Include naming conventions: how to address users, whether to use their name, how often
- Key consideration: Tone must be maintainable across many turns without feeling repetitive

**`<context>`**
- Describe the environment where conversations happen (chat widget, app, voice)
- Explain who the users are and what they typically need
- Provide business context that affects conversation priorities (high volume, premium users)
- Include timing expectations if relevant (async vs real-time)

**`<inputs>`**
- Document all information available at conversation start (user profile, account data)
- Include conversation history as an explicit input with guidance on how to use it
- Describe any real-time signals (user activity, system status) the agent can access
- For each input: what it is, what it contains, how to use it in conversation

**`<knowledge_scope>`**
- Explicitly list what the agent knows and can speak authoritatively about
- Critical: Define what the agent does NOT know (this prevents hallucination)
- Specify how to handle uncertainty: what phrases to use, when to look things up, when to admit not knowing
- Include temporal boundaries (knowledge cutoff, what requires checking)

**`<capabilities>`**
- List what the agent can do, grouped by type (answer, troubleshoot, take action)
- For each capability with side effects, specify the tool and any confirmation requirements
- Distinguish between informational capabilities and action capabilities
- Be explicit about what the agent cannot do (and what happens when users ask for those things)

**`<operational_logic>`**
- Define conversation opening patterns (how to greet, how to handle users who jump right in)
- Specify information-gathering approach (one question at a time, what to check before asking)
- Create troubleshooting or resolution flows with clear decision points
- Define how to handle ambiguity: when to ask for clarification vs. make reasonable assumptions
- Specify closing patterns: how to confirm resolution, how to offer additional help, how to end

**`<examples>`**
- Essential for this role: conversational style is difficult to describe abstractly
- Include 3-5 examples covering different conversation patterns: simple request, multi-turn troubleshooting, out-of-scope request, frustrated user
- Show the back-and-forth, not just single responses
- Examples should demonstrate tone, length, turn-taking, and how to handle common situations

**`<output_format>`**
- Keep this minimal: conversational agents output natural language, not structured data
- Specify response length expectations (typical range, when to be longer)
- Note formatting preferences (when to use lists vs. prose, how to format instructions)
- Define how to end different types of responses (question, statement, call to action)

**`<constraints_and_safeguards>`**
- Define hard rules: things the agent must never do regardless of user request
- Specify escalation triggers: exact conditions that require human handoff
- Include error handling: what to do when tools fail, when information is unavailable
- Define success criteria: how to know when a conversation is successfully complete

## Modifier Notes

**If adding Tools:**
- See `modifiers/tool-usage.md` for per-tool documentation patterns
- For each tool, document: what it does, when to use it, parameters, expected responses, error handling
- Group tools by conversational purpose (information retrieval, account actions, escalation)
- Always specify confirmation requirements for actions with side effects
- Include fallback behavior when tools fail mid-conversation
- Add a `<tool_usage_guidelines>` section within `<capabilities>` or as a separate section

**If using Structured Output:**
- User-facing responses should remain natural language
- Use structured output for: internal routing, intent classification, conversation state tracking
- Useful for logging/analytics: `{"response": "...", "intent": "...", "sentiment": "...", "escalation_risk": 0.2}`
- For agent-to-agent handoff: structure the context you pass to downstream agents
- See `modifiers/structured-output.md` for schema design patterns

**If adding Memory:**
- Conversation history is essential; treat it as a core input
- Consider longer-term memory for returning users (previous issues, preferences)
- Define what to remember vs. what to treat as fresh each conversation
- See `modifiers/memory.md` for memory implementation patterns

## Common Pitfalls
1. **No knowledge boundaries** — Without explicit "what you don't know," agents hallucinate confidently. Always include negative knowledge scope.
2. **Missing escalation paths** — Every conversational agent needs clear criteria for when to hand off to humans. Users will eventually ask for things the agent can't handle.
3. **Skipping examples** — Conversational style is almost impossible to specify without showing it. Include multi-turn examples that demonstrate the full range of interaction patterns.
4. **Inconsistent persona across turns** — The agent's personality should be stable. Define tone clearly enough that it stays consistent whether the user is happy, confused, or frustrated.
5. **No operational flow** — Without explicit conversation logic, agents meander or ask redundant questions. Define the shape of a good conversation.
6. **Ignoring emotional signals** — Failing to acknowledge user frustration before problem-solving makes agents feel robotic. Specify how to handle emotions.
