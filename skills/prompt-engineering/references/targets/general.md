# General Target (Standalone System Prompt)

## What You Produce

A standalone system prompt string using XML-tagged sections. Not tied to any specific agent framework.

## When to Use

- No specific framework chosen yet (prototyping)
- Direct API calls to LLM providers without a framework
- Framework that doesn't have a dedicated target reference (not DSPy or LangGraph)
- General-purpose agent or assistant prompt

## Output Format

A complete XML-tagged prompt string following the chosen framework template:
- **Single-Turn**: `references/frameworks/single-turn.md` (7 sections, 300-600 words)
- **Conversational**: `references/frameworks/conversational.md` (10 sections, 600-1200 words)

No sections are skipped. No escaping needed. No separation of types from prompt. What you write is what gets used as the system message.

## Adaptations

None. All role guidance and modifier patterns apply directly without modification:
- Full `<output_format>` section describing expected output structure
- Reasoning techniques written directly into the prompt text
- Tool descriptions included in the prompt body
- Memory handling instructions in `<operational_logic>` or `<task>`

## Checklist

- [ ] Follows chosen framework template structure (all required sections present)
- [ ] Role-specific guidance applied to each section
- [ ] All selected modifiers incorporated
- [ ] `<output_format>` includes complete schema with examples
- [ ] Constraints placed in final section (recency effect)
- [ ] No TODOs or placeholders remain
- [ ] Reviewed against `references/guidelines/prompt-writing.md` quality checklist
