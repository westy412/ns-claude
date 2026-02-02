# Creative/Generator Agent

## Role Description
Creates content, generates ideas, and drafts materials based on defined inputs and constraints. Generators produce text, copy, campaigns, code, or other creative outputs. They balance creative expression with brand guidelines, style requirements, and practical constraints to deliver usable content.

## When to Use
- The agent's primary job is to produce content (emails, copy, campaigns, documentation, code)
- You need idea generation, brainstorming, or creative exploration
- The task requires balancing creativity with specific constraints (brand voice, length, format)

## When NOT to Use
- The agent needs to make decisions or choose between options based on criteria → Use [Decision-Maker] instead
- The task is primarily about extracting or transforming existing information → Use [Processor/Transformer] instead
- The agent needs to maintain an ongoing dialogue to gather requirements iteratively → Use [Conversational Assistant] instead

## Selection Criteria
- Is the agent's primary job to produce new content that didn't exist before? → Yes = this role
- Does it need to evaluate, score, or choose between options? → If yes, consider [Decision-Maker]
- Is it transforming input data into a different structure without creative interpretation? → If yes, consider [Processor/Transformer]
- Does the user need to iteratively refine requirements through dialogue? → If yes, consider Conversational framework

## Framework Fit
**Primary:** Single-Turn
**Why:** Most generation tasks have well-defined inputs (topic, style, constraints, examples) and outputs (the content itself). The structured approach ensures all creative requirements are captured upfront.
**When to use the other:** Use Conversational for collaborative writing sessions, iterative brainstorming where the user refines direction through dialogue, or when requirements emerge through back-and-forth exploration.

## Section-by-Section Guidance

### For Single-Turn Framework:

**`<who_you_are>`**
- Define the creative perspective and expertise (e.g., "B2B copywriter," "creative strategist," "technical writer")
- Specify the stylistic approach: how this generator thinks about its craft
- Include attitude toward creativity vs. constraints (e.g., "You prioritize clarity over cleverness" or "You embrace unconventional ideas")
- Avoid generic descriptions like "you are a helpful writer" — be specific about what kind of writer

**`<skill_map>`**
- List creative abilities: persuasive writing, divergent thinking, tone matching, etc.
- Include domain knowledge relevant to the content type (industry expertise, platform knowledge)
- Add technical skills if applicable: SEO, formatting conventions, platform-specific requirements
- Keep focused on skills that directly impact output quality

**`<context>`**
- Explain where this content will be used and by whom
- Specify the downstream audience (who reads the output, not just who requests it)
- Include any workflow context: Is this a first draft? Final output? Part of a larger piece?
- Note if content is sent from someone else's voice (sales rep, CEO) — this critically affects tone

**`<inputs>`**
- Document every variable that affects the creative output: topic, tone, length, audience, constraints
- For each input, explain how it should influence the generation
- Include optional inputs like style examples or reference materials
- Be explicit about which inputs are required vs. optional

**`<task>`**
- Structure as clear steps: research/review → plan → generate → refine
- Specify any required elements (e.g., "include a call to action," "end with a question")
- Include revision or self-check steps if quality matters
- Define success criteria: What makes this output "done"?

**`<output_format>`**
- Provide the exact structure for the output (headers, sections, formatting)
- Specify length constraints with concrete numbers (word counts, character limits)
- Include any required metadata (subject lines, titles, tags)
- For templated content, show the exact format to follow

**`<important_notes>`**
- List what to avoid: banned phrases, topics, claims, competitor mentions
- Include brand guidelines or voice requirements
- Specify any compliance or legal constraints
- Add creative permissions if applicable (e.g., "Include at least one unconventional idea")

### For Conversational Framework:

**`<personality>`**
- Define the collaborative style: encouraging, challenging, neutral
- Specify how to handle creative differences or pushback
- Include how to balance offering ideas vs. asking clarifying questions
- Avoid being sycophantic — creative partners can respectfully push back

**`<communication_style>`**
- Describe how to present ideas: all at once vs. one at a time
- Specify how to ask for feedback: direct questions vs. open-ended
- Include pacing guidance: when to generate vs. when to pause and check in
- Define how verbose or concise to be during collaboration

**`<rules>`**
- Specify when to ask for clarification vs. make reasonable assumptions
- Define how to handle vague briefs: proceed with stated assumptions or require more detail
- Include guidelines for iterating: how many rounds, when to push back on scope
- Note any constraints that apply even in collaborative mode

**`<examples>`**
- Show sample exchanges that demonstrate the collaborative style
- Include examples of handling feedback (positive and negative)
- Demonstrate how to pivot when direction changes
- Show the tone and format of generated content within dialogue

## Modifier Notes

**If adding Tools:**
- See `modifiers/tool-usage.md` for per-tool documentation patterns
- For each tool, document: what it does, when to use it, parameters, expected responses, error handling
- Common creative tools: web search (grounding), template retrieval (style references), constraint checkers (word count, readability)
- Add a `<tool_usage_guidelines>` section to the prompt if tools are central to the task

**If using Structured Output:**
- See `modifiers/structured-output.md` for schema design patterns
- More common than it appears — even creative content often needs metadata
- Use when: confidence scoring, reasoning traces, quality metrics, or inter-agent communication
- Pattern: wrap free-form content in structured envelope: `{"content": "...", "confidence": 0.85, "reasoning": "..."}`
- For agent-to-agent: structure lets you filter what downstream agents see (e.g., pass content but not reasoning)
- Keep the creative content field as free-form text; structure the metadata around it

**If adding Memory:**
- See `modifiers/memory.md` for memory implementation patterns
- Useful for ongoing content projects requiring consistent voice over time
- Store style examples, brand guidelines, and successful past outputs
- Memory helps maintain character/voice consistency across sessions

## Common Pitfalls
1. **Vague style guidance** — "Write well" means nothing. Provide specific attributes (concise, conversational, authoritative) or examples that demonstrate the desired style.
2. **Missing length constraints** — Generators will over-produce without limits. Always specify word counts, character limits, or structural boundaries.
3. **No examples for style** — Few-shot examples anchor style better than descriptions. Include 1-2 examples of the desired output quality and format.
4. **Overconstraining ideation tasks** — For brainstorming, explicitly permit unconventional ideas and state that quantity/variety matters more than polish.
5. **Ignoring voice ownership** — If content is sent from someone else (sales rep, executive), capture their specific voice and communication style, not a generic professional tone.
6. **Missing "don't do" list** — Generators need clear boundaries. Specify banned phrases, forbidden topics, and claims to avoid.
