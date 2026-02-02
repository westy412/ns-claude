# Router/Classifier Agent

## Role Description
Makes decisions and routes inputs to appropriate destinations or categories. Routers analyze incoming data and determine the correct path, category, or handler based on defined criteria. They serve as decision points in workflows, enabling downstream systems to act on structured classifications.

## When to Use
- The agent's job is to categorize input into one of several predefined options
- You need to direct data to different handlers, queues, or workflows
- The output is a decision, not content generation or transformation
- Classification accuracy directly impacts downstream system behavior

## When NOT to Use
- Input requires transformation or generation → Use [Transformer/Processor] instead
- Agent needs to have a back-and-forth conversation → Use [Conversational Agent] instead
- Decision requires multiple steps of reasoning with tool calls → Use [Reasoning Agent] instead
- You need to extract structured data from unstructured input → Use [Extractor/Parser] instead

## Selection Criteria
- Is the agent's primary job to pick from a finite set of options? → Yes = this role
- Does the agent need to generate content beyond the classification? → If yes, consider combining with another role
- Will the output drive automated routing logic? → Yes = this role, and ensure structured output
- Does the decision require external lookups or calculations? → If yes, consider adding tools or using a different role

## Framework Fit
**Primary:** Single-Turn
**Why:** Routing decisions have defined inputs and discrete outputs. The input is always something to classify, the output is always a category/route selection. There is no back-and-forth needed.
**When to use the other:** Conversational framework only applies if the router must interactively clarify ambiguous input with a user before making a decision. This is rare.

## Section-by-Section Guidance

### For Single-Turn Framework:

**`<who_you_are>`**
- Define the agent as a specialist in the specific domain being routed (email routing specialist, intent classifier, support ticket triager)
- Emphasize decision-making expertise and the importance of accurate classification
- Include domain knowledge relevant to the categories (understanding what Sales handles vs Support)
- Avoid generic descriptions; be specific about what this router does and why it matters

**`<skill_map>`**
- Keep skills focused on analysis and classification, not generation
- Include: content analysis, intent recognition, pattern matching, domain understanding
- List skills specific to the content type (email analysis, natural language understanding, ticket categorization)
- Avoid including skills unrelated to the classification task

**`<inputs>`**
- **Content to classify:** Document the primary input (email, message, request, ticket) with its structure
- **Available routes/categories:** This is critical. List every possible route with clear, mutually exclusive descriptions of what belongs in each. Never let the router infer categories.
- **Context (if applicable):** Include conversation history or prior decisions only when needed for disambiguation
- Use the standard format: What it is, Information included, How to use it

**`<task>`**
- Structure as a clear decision process: analyze input → identify key signals → match to category → assess confidence
- Step 1 should always be reading/analyzing the input
- Middle steps should cover the classification logic (what signals to look for, how to match)
- Final step should be producing the output
- Keep it to 4-6 steps; routing decisions should be straightforward

**`<output_format>`**
- Always include the route/category selection as the primary output
- Add CONFIDENCE level (high/medium/low or 0.0-1.0) for downstream fallback logic
- Include brief REASONING to explain the decision (one sentence)
- Consider PRIORITY if the routing system uses it
- Use simple key-value format that's easy to parse programmatically

**`<important_notes>`**
- Define fallback behavior: what happens when no category clearly fits
- Specify tie-breaking rules: when input matches multiple categories, which wins
- List edge cases specific to your domain (auto-replies, profanity, escalation triggers)
- Include any hard rules that override normal classification logic
- State what to do when confidence is low

## Modifier Notes

**If adding Tools:**
- See `modifiers/tool-usage.md` for per-tool documentation patterns (if tools are added)
- Rarely needed; routers typically don't require external data to classify
- Consider tools only if classification requires real-time lookups (VIP status, account verification)
- If you need complex tool workflows, this is probably a different agent type

**If using Structured Output:**
- See `modifiers/structured-output.md` for schema design patterns
- Almost always recommended; routing decisions must be machine-parseable
- Schema pattern: `{"route": "enum", "confidence": "number", "reasoning": "string"}`
- Ensure the enum matches exactly the routes defined in `<inputs>`
- For agent-to-agent: downstream agent only needs the route, not necessarily the reasoning

**If adding Memory:**
- See `modifiers/memory.md` for memory implementation patterns
- Rarely needed; each routing decision is typically independent
- Consider memory only for pattern detection across inputs (repeat escalations from same user)
- Keep memory scope narrow; routers should remain stateless when possible

## Common Pitfalls
1. **Undefined or incomplete categories** — Routers need explicit, exhaustive category lists. Always include a fallback category (OTHER, GENERAL, UNKNOWN) to prevent undefined behavior.
2. **Overlapping category definitions** — Category descriptions must be as mutually exclusive as possible. If "pricing questions" could go to Sales or Support, define which one owns it.
3. **Missing tie-breaking rules** — When input genuinely matches multiple categories, the router needs explicit priority rules. Define these in `<important_notes>`.
4. **No confidence output** — Downstream systems need to know when the router is uncertain. Always include confidence so fallback logic can trigger.
5. **Letting the router generate content** — Routers should classify, not create. If you need explanation beyond brief reasoning, use a separate agent.
6. **Ignoring context for conversational routers** — If the router classifies messages in a conversation, it needs access to history. "Yes" means nothing without knowing the prior question.
