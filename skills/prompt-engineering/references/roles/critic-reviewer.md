# Critic/Reviewer Agent

## Role Description
Evaluates content, code, or work products against defined standards or criteria. Provides structured feedback identifying issues, categorizing them by severity, and suggesting improvements. Critics ensure quality by applying expertise systematically and delivering actionable assessments.

## When to Use
- Agent needs to evaluate work products (code, writing, designs, plans)
- Feedback must be categorized by severity or importance
- Output should identify specific issues with actionable suggestions

## When NOT to Use
- Agent creates content rather than evaluates it → Use Creator role instead
- Agent transforms input without judgment (e.g., formatting, translation) → Use Transformer role instead
- Agent answers questions about content without assessing quality → Use Researcher role instead

## Selection Criteria
- Is the agent's primary job to judge quality or correctness? → Yes = this role
- Does it need to produce structured feedback with issue categorization? → Yes = this role
- Is the agent creating original work rather than assessing existing work? → If yes, use Creator role
- Does it need to have a back-and-forth discussion about findings? → If yes, consider Conversational framework

## Framework Fit
**Primary:** Single-Turn
**Why:** Review tasks have well-defined inputs (content to evaluate, criteria to apply) and outputs (categorized feedback, verdicts). The evaluation process follows predictable steps that benefit from explicit structure.
**When to use the other:** Use Conversational when the critic must discuss findings with the content creator, negotiate on feedback, or iterate through multiple rounds of revision and re-review.

## Section-by-Section Guidance

### For Single-Turn Framework:

**`<who_you_are>`**
- Define the expertise domain (e.g., "senior code reviewer," "technical editor," "security auditor")
- Specify the standards or perspective applied (e.g., "applies OWASP security guidelines," "evaluates for production readiness")
- Establish the feedback tone: direct, constructive, or encouraging
- Avoid generic descriptions; tie expertise to the specific evaluation context

**`<skill_map>`**
- List domain-specific evaluation skills (e.g., "Python best practices," "API design patterns," "accessibility standards")
- Include meta-skills like "severity assessment" and "actionable feedback formulation"
- Be specific to the review domain rather than listing generic analysis skills
- Typically 4-7 skills that define what the critic can assess

**`<context>`**
- Explain who will receive the feedback and their expertise level
- Describe where in the workflow the review occurs (e.g., pre-merge, draft stage, final check)
- Clarify the goal: catching issues, improving quality, learning, compliance
- Include any organizational standards or team conventions that apply

**`<inputs>`**
- Document the primary content to review (code diff, document draft, design mockup)
- Include evaluation criteria or focus areas if provided separately
- Add any reference materials (style guides, requirements, previous versions)
- Explain how each input should influence the review (e.g., "weight security issues more heavily if Review Focus specifies security")

**`<task>`**
- Start with understanding intent before evaluating execution
- Structure evaluation by dimension (correctness, style, security, etc.) or by content section
- Include explicit steps for severity categorization
- End with synthesis: overall assessment and verdict
- Consider adding a step for positive observations to maintain constructive tone

**`<output_format>`**
- Structure feedback by severity level (Critical, Major, Minor) or category
- Require specific location references (file, line, section, paragraph)
- Include suggestion format alongside issue identification
- Add summary and verdict sections for quick scanning
- Consider including a "Positive Notes" section to balance criticism

**`<important_notes>`**
- Define scope boundaries: what to review, what to ignore (e.g., "focus on changed code only," "don't flag issues covered by automated linters")
- Specify how to handle uncertainty: ask questions vs. flag as potential issue
- Distinguish between objective errors and subjective preferences
- Include tone guardrails: be specific, be actionable, acknowledge what's done well

### For Conversational Framework:

**`<who_you_are>`**
- Same expertise definition as Single-Turn
- Add willingness to discuss and explain feedback rationale
- Include stance on disagreement: when to hold firm vs. acknowledge valid alternatives

**`<tone_and_style>`**
- Critical here: defines how feedback is delivered in dialogue
- Specify direct vs. diplomatic language preferences
- Include how to handle pushback constructively
- Define when to soften feedback vs. when to be firm

**`<capabilities>`**
- List types of review available (code review, architecture review, security audit)
- Include ability to explain reasoning, discuss alternatives, and re-evaluate after changes
- Mention iterative review capability if relevant

**`<operational_logic>`**
- How to handle creator disagreement with feedback
- When to escalate critical issues vs. accept creator's judgment
- How to track what's been discussed and resolved
- Process for re-review after changes

**`<interaction_patterns>`**
- Opening: acknowledge receipt, state review approach
- Feedback delivery: structured even in conversation (by file, by severity)
- Closing: summarize key issues, state next steps
- Follow-up: how to handle questions about feedback

## Modifier Notes

**If adding Tools:**
- See `modifiers/tool-usage.md` for per-tool documentation patterns
- For each tool, document: what it does, when to use it, parameters, expected responses, error handling
- Common critic tools: linter/analyzer execution (back up feedback with automated findings), test execution (verify correctness claims), documentation lookup (cite standards)
- Add a `<tool_usage_guidelines>` section if tools are central to the review process

**If using Structured Output:**
- See `modifiers/structured-output.md` for schema design patterns
- Ideal for CI/CD integration where feedback is parsed programmatically
- Define severity enums explicitly (CRITICAL, MAJOR, MINOR, INFO)
- Include machine-readable verdicts (APPROVE, REQUEST_CHANGES, COMMENT)
- Pattern: `{"verdict": "REQUEST_CHANGES", "issues": [...], "confidence": 0.9, "reasoning": "..."}`
- For agent-to-agent: downstream agents may need only the verdict and issues, not the full reasoning

**If adding Memory:**
- See `modifiers/memory.md` for memory implementation patterns
- Track patterns in creator's work to provide more targeted feedback over time
- Remember resolved issues to avoid re-flagging addressed concerns
- Note creator's preferences for feedback style and adjust accordingly

## Common Pitfalls
1. **Vague feedback without specifics** — Always require exact locations and concrete suggestions; "this could be better" is not actionable
2. **Missing severity categorization** — Not all issues are equal; force explicit priority levels to help creators triage
3. **All negative, no positive** — Include a positive observations section; pure criticism discourages and misses what's working
4. **Scope creep into unrelated issues** — Define boundaries clearly; review what was asked, not everything that could theoretically be improved
5. **Opinion stated as fact** — Distinguish between objective errors ("this will crash") and preferences ("I would prefer this approach")
6. **Evaluating without understanding intent** — Always include a step to understand the goal before critiquing the execution
