# Researcher Agent

## Role Description
Gathers information from multiple sources, explores topics systematically, and synthesizes findings into structured insights. Researchers investigate questions, collect evidence, identify patterns, and produce organized outputs that inform decisions or feed downstream processes.

## When to Use
- The agent needs to explore a topic and return organized findings
- Multiple sources must be consulted, compared, or synthesized
- The output requires evidence, citations, or supporting data
- Information gathering is the primary job, not taking action on findings

## When NOT to Use
- The agent needs to make decisions based on research → Use **Decision Maker** instead
- The task is executing a plan, not investigating → Use **Executor** instead
- The agent needs to have a back-and-forth dialogue to understand requirements → Use **Conversational Assistant** instead
- The output is creative content rather than factual synthesis → Use **Writer** instead

## Selection Criteria
- Is the agent's primary job gathering and organizing information? → Yes = Researcher
- Does it need to act on the findings? → If yes, consider Executor or Decision Maker
- Is the task exploring unknowns vs. executing known steps? → Exploring = Researcher
- Does the output need citations or evidence trails? → Yes strongly suggests Researcher

## Framework Fit
**Primary:** Single-Turn
**Why:** Research tasks typically have defined inputs (topic, sources, constraints) and defined outputs (findings, synthesis, evidence). The researcher doesn't need to negotiate scope or have extended dialogue.
**When to use the other:** Use Conversational when the researcher needs to iteratively refine the research question with the user, or when the scope is genuinely unknown and requires back-and-forth exploration.

## Section-by-Section Guidance

### For Single-Turn Framework:

**`<who_you_are>`**
- Specify the research domain (competitive intelligence, technical research, market analysis, etc.)
- Include methodological strengths: "You excel at synthesizing disparate sources" or "You rigorously separate facts from inferences"
- Avoid generic descriptions; anchor to the specific research context
- If the researcher has access to specific knowledge or expertise, state it here

**`<skill_map>`**
- List research-specific capabilities: source evaluation, pattern recognition, synthesis, comparison
- Include domain skills if applicable (market analysis, technical evaluation, academic research methods)
- Keep to 4-6 skills that directly relate to the research task
- Avoid listing generic skills like "attention to detail"

**`<context>`**
- Explain why this research matters and who consumes it
- Specify what decisions the research informs—this shapes depth and focus
- Include organizational context if it affects what sources are trusted or prioritized
- State any prior research or existing knowledge the agent should build upon

**`<inputs>`**
- Always include: research topic/question, available sources, constraints/scope
- Document each input with: what it is, what information it contains, how to use it
- Be explicit about source boundaries—what the researcher can and cannot access
- Include time constraints, geographic scope, or depth expectations as separate inputs

**`<task>`**
- Structure as sequential steps: understand scope → gather data → organize → synthesize → format
- Always include an explicit synthesis step—don't let the task end at data collection
- Specify what "done" looks like: "Identify 3-5 key patterns" rather than "Research the topic"
- Include a step for acknowledging gaps or limitations in findings

**`<output_format>`**
- Structure outputs to separate raw findings from synthesis (competitor summaries → patterns → insights)
- Always include a "Gaps and Limitations" section to surface uncertainty
- Require citations or evidence markers for factual claims
- Match output structure to how downstream consumers will use the research

**`<important_notes>`**
- Require distinguishing confirmed facts from inferences or speculation
- Mandate explicit acknowledgment when information is unavailable
- Set depth expectations: "Prioritize breadth over depth" or "Deep dive on top 3 competitors"
- Include scope boundaries: what's explicitly out of scope

### For Conversational Framework:

**`<knowledge_scope>`**
- Define what sources and information the researcher can access
- Be explicit about limitations: "You cannot access real-time data" or "You have access to the internal wiki"
- Clarify what types of questions are in vs. out of scope

**`<capabilities>`**
- Emphasize: search, summarize, compare, synthesize, evaluate sources
- Include the ability to ask clarifying questions about research scope
- Note any tools available (web search, database access, document retrieval)

**`<operational_logic>`**
- Define how to handle ambiguous research requests—when to ask for clarification vs. make reasonable assumptions
- Specify how to present findings conversationally while maintaining structure
- Include guidance on iterative refinement: how to narrow or expand scope based on user feedback

**`<communication_style>`**
- Favor clear, evidence-based communication
- Specify how to handle uncertainty: "Present confidence levels" or "Flag speculation explicitly"
- Define how verbose to be—bullet summaries vs. detailed explanations

## Modifier Notes

**If adding Tools:**
- See `modifiers/tool-usage.md` for per-tool documentation patterns
- For each tool, document: what it does, when to use it, parameters, expected responses, error handling
- Web search tools need source evaluation guidance (credibility, recency, authority)
- Database tools need clear query instructions and empty-result handling
- Add a `<tool_usage_guidelines>` section if tools are central to the research

**If using Structured Output:**
- See `modifiers/structured-output.md` for schema design patterns
- Common for research — enables downstream automation and agent-to-agent handoff
- Schema should separate: findings (facts), analysis (inferences), metadata (confidence, sources)
- Include confidence fields to surface uncertainty programmatically
- For agent-to-agent: structure lets you pass findings without reasoning traces if needed

**If adding Memory:**
- See `modifiers/memory.md` for memory implementation patterns
- Rarely needed for single research tasks
- Useful for ongoing research projects where findings accumulate over time
- Store source evaluations to avoid re-evaluating the same sources

## Common Pitfalls
1. **Scope creep** — Researchers explore endlessly without boundaries. Always define explicit scope constraints in inputs and include "stay within these boundaries" in task steps.
2. **Missing source specification** — Assuming the researcher knows what sources to use. Always specify available sources and their priority in inputs.
3. **Hallucinated findings** — Researchers may fabricate plausible-sounding information. Require citations, include "Gaps and Limitations" in output, and add notes distinguishing facts from inferences.
4. **Data dump without synthesis** — Returning raw findings without patterns or insights. The task must include explicit synthesis steps: "Identify patterns" → "Derive insights."
5. **Ambiguous depth** — "Research X" is too vague. Specify depth: "Find 3-5 key points with evidence" or "Comprehensive analysis of top 3 competitors."
