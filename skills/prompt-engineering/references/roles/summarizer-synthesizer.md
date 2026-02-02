# Summarizer/Synthesizer Agent

## Role Description
Condenses information and creates summaries from single or multiple sources. This role distills large or complex inputs into key points, preserving essential meaning while reducing volume. Synthesizers go further by identifying themes, agreements, and contradictions across multiple documents.

## When to Use
- The agent needs to reduce content volume while preserving meaning
- Multiple sources must be combined into a unified view
- The task is extracting key points, decisions, or action items
- Someone needs to understand content without reading the full source

## When NOT to Use
- The task requires generating new content or ideas → Use **Creator/Writer** instead
- The agent needs to evaluate quality or correctness → Use **Evaluator/Critic** instead
- The task involves answering questions about content → Use **Researcher** instead
- The output requires significant analysis or recommendations → Use **Analyst** instead

## Selection Criteria
- Is the primary job reducing content while preserving meaning? → Yes = this role
- Does it need to identify themes across multiple sources? → Yes = Synthesizer variant of this role
- Does it need to add new analysis or recommendations? → If yes, consider **Analyst** instead
- Does it need to answer specific questions about the content? → If yes, consider **Researcher** instead
- Is the output a new creative piece inspired by the source? → If yes, consider **Creator/Writer** instead

## Framework Fit
**Primary:** Single-Turn
**Why:** Summarization has clearly defined inputs (content to condense) and outputs (summary in specified format). The task is discrete and deterministic—same content should produce consistent summaries.
**When to use the other:** Conversational is rarely appropriate. Consider it only if the user needs to iteratively refine the summary through back-and-forth dialogue, but even then, a Single-Turn agent called multiple times is usually cleaner.

## Section-by-Section Guidance

### For Single-Turn Framework:

**`<who_you_are>`**
- Emphasize the domain context—a meeting summarizer needs different expertise than a research synthesizer
- Include the judgment criteria: what makes a good summary in this context
- Avoid generic descriptions; specify what "good" means for this summarization task
- Keep brief (2-3 sentences)—the skill is straightforward, context matters more

**`<skill_map>`**
- Core skills: information extraction, prioritization, concise writing
- Add domain skills if relevant (e.g., "technical terminology" for engineering docs)
- For synthesizers, include: cross-document analysis, theme identification, contradiction detection
- Keep to 4-6 skills; summarization is focused work

**`<context>`**
- Explain who will read the summary and why—this drives what to prioritize
- Specify the use case: executive briefing vs. detailed reference vs. notification
- Include any domain context that affects what's "important" in the source material
- This section often matters more than `<who_you_are>` for summarizers

**`<inputs>`**
- **Always include:** The content to summarize (document, transcript, etc.)
- **Always include:** Target length or depth level (brief/standard/detailed)
- **Optional:** Focus areas or topics to prioritize
- **Optional:** What to exclude or de-prioritize
- For synthesizers: explain how multiple documents are provided and identified
- Document the format of source material (transcript with timestamps, raw text, etc.)

**`<task>`**
- Structure as sequential steps: read → identify key elements → extract → structure → write
- Be explicit about prioritization: what elements are must-have vs. nice-to-have
- For meeting summaries: decisions and action items typically come first
- For research synthesis: specify the order of theme identification, agreement/disagreement, gaps
- Include a final step for length/format compliance

**`<output_format>`**
- Specify exact structure with headers and sections
- Include length limits (word counts or line counts per section)
- Use templates with placeholders showing exactly what goes where
- For multi-source synthesis: show how to attribute information to sources
- Be prescriptive—summarizers need clear structural constraints

**`<important_notes>`**
- Specify what must never be omitted (decisions, action items, key dates)
- Specify what should always be excluded (small talk, tangents, redundancy)
- Include attribution rules: how to reference sources, speakers, or documents
- Add tone requirements if relevant (formal, casual, urgent)
- State the cardinal rule: don't add information not in the source material

## Modifier Notes

**If adding Tools:**
- See `modifiers/tool-usage.md` for per-tool documentation patterns (if tools are added)
- Rarely needed—summarization works from provided content
- Exception: retrieval tools if agent needs to fetch source documents
- Never add tools for "enhancing" summaries with external information

**If using Structured Output:**
- See `modifiers/structured-output.md` for schema design patterns
- Excellent fit for summaries that feed into databases, dashboards, or downstream agents
- Schema pattern: `{"summary": "...", "action_items": [...], "decisions": [...], "key_points": [...]}`
- Use arrays for repeating structures (action items, themes, sources)
- For agent-to-agent: structure lets you pass action items without the full summary

**If adding Memory:**
- See `modifiers/memory.md` for memory implementation patterns
- Useful for progressive summarization (e.g., daily standup summaries that track ongoing items)
- Store previous summaries to maintain context on recurring topics
- Track what's been "resolved" vs. "still open" across sessions

## Common Pitfalls
1. **No length target specified** — Always define output length; without it, summaries vary wildly. Specify word counts, bullet limits, or section lengths.
2. **Proportional reduction fallacy** — Summaries should prioritize what matters, not shrink everything equally. Be explicit about what's high-priority vs. omittable.
3. **Lost attribution in synthesis** — When combining multiple sources, always require source tracking. Show the format for attribution in `<output_format>`.
4. **Hidden contradictions** — When sources disagree, the summary must surface it, not hide it. Explicitly instruct that contradictions are valuable signal.
5. **Accidental interpretation** — Summarizers extract and condense; they don't analyze or recommend. If you need analysis, use the Analyst role instead.
6. **Missing the point** — For meeting summaries, decisions and action items are the deliverable—everything else is context. Prioritize accordingly.
