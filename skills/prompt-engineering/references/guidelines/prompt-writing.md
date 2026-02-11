# Prompt Writing Guidelines

Detailed techniques for writing effective agent system prompts. Use this alongside framework templates, role guidance, and modifiers to produce complete, high-quality prompts.

---

## Core Principles

### 1. Explicit Over Implicit

Never assume the model will infer correctly. State everything explicitly.

**Bad:**
```xml
<who_you_are>
You are a helpful assistant.
</who_you_are>
```

**Good:**
```xml
<who_you_are>
You are a senior customer support specialist at Acme Software.
Your primary goal is helping customers resolve issues on the first contact.
You have deep knowledge of the product, including common troubleshooting steps
and feature limitations.
</who_you_are>
```

### 2. Constrain the Solution Space

Narrower constraints produce more consistent behavior. The model performs better when it knows exactly what's expected.

**Bad:**
```
Analyze the input and provide feedback.
```

**Good:**
```
Analyze the input for:
1. Grammatical correctness (flag errors with line numbers)
2. Clarity (identify ambiguous phrases)
3. Conciseness (suggest cuts for verbose sections)

Do NOT evaluate:
- Content accuracy (that's handled elsewhere)
- Formatting (handled by automated tools)
```

### 3. Negative Space is as Important as Positive Space

State what the agent should NOT do. This prevents scope creep and reduces hallucination.

**Always include:**
- Knowledge boundaries (what it doesn't know)
- Capability limits (what it can't do)
- Behavioral restrictions (what it shouldn't attempt)

### 4. Sequence Matters (Primacy-Recency Effects)

LLMs exhibit the **serial position effect** from cognitive science: items at the beginning and end of sequences receive more attention than items in the middle.

**Primacy Effect (Beginning):**
- Initial information receives more cognitive processing
- Serves as an anchor/reference point for interpreting subsequent content
- Use for: Role definition, identity, primary objective
- These establish the cognitive framework for everything that follows

**Recency Effect (End):**
- Final information remains most accessible in working memory
- Has outsized influence on behavior
- Use for: Critical constraints, output format reinforcement, "never do X" rules
- Put your most important rules at the very end

**Recommended Section Ordering:**

```
1. Role/Identity (primacy - establishes cognitive framework)
2. Objective/Purpose
3. Context/Background information
4. Inputs documentation
5. Task instructions (potentially with examples)
6. Output format specification
7. Constraints and guardrails (recency - reinforces boundaries)
```

**Why this order works:**
- **Position 1-2**: The model "becomes" the role first, then understands its mission. Everything else is interpreted through this lens.
- **Position 3-5**: Core task content goes in the middle. This is fine—the model processes it in context of the established role.
- **Position 6-7**: Output format and constraints at the end ensure they're "freshest" when generating the response. These are what the model is actively referencing as it produces output.

**For long prompts (500+ words):**
Repeat the single most critical constraint at the absolute end, even if it appears earlier:

```xml
</constraints_and_safeguards>

CRITICAL: Never output customer data to logs.
```

### 5. Examples Anchor Behavior

For complex or nuanced behavior, examples are more effective than abstract instructions. The model pattern-matches on examples.

**When to use examples:**
- Conversational agents (show dialogue patterns)
- Complex output formats (show the exact structure)
- Subjective judgment tasks (show what "good" looks like)
- Edge case handling (show how to handle unusual inputs)

---

## Section-by-Section Techniques

### Identity Sections (`<who_you_are>`, `<role>`)

**Purpose:** Establish identity, expertise, and objectives.

**Techniques:**

1. **Name the expertise domain specifically**
   - "Senior Python developer specializing in async patterns" not "programmer"
   - "B2B sales strategist focused on mid-market SaaS" not "sales helper"

2. **Include relationship to user/system**
   - "You report to the Operations team and support the Sales team"
   - "Your output feeds into the Report Generator agent"

3. **Define success**
   - "Success means the user leaves with a clear, actionable path forward"
   - "A successful analysis identifies all critical issues with no false negatives"

4. **Avoid personality traits for Single-Turn agents**
   - Personality matters for Conversational agents
   - For Single-Turn, focus on expertise and objectives, not personality

**Anti-patterns:**
- Generic descriptions ("You are a helpful AI")
- Overloaded identity (too many roles/responsibilities)
- Personality without purpose (traits that don't affect behavior)

### Skill/Capability Sections (`<skill_map>`, `<capabilities>`)

**Purpose:** Activate relevant knowledge and define what the agent can do.

**Techniques:**

1. **Be domain-specific**
   - "Python async/await patterns" not "programming"
   - "OWASP Top 10 security vulnerabilities" not "security knowledge"

2. **Link skills to task requirements**
   - Only list skills that will be used in this prompt
   - Each skill should have a corresponding use in the task

3. **For tools, document completely**
   - Name and purpose
   - Parameters with types
   - When to use (and when not to)
   - Expected response format
   - Error handling

**Anti-patterns:**
- Padding with irrelevant skills
- Listing generic abilities ("communication", "problem-solving")
- Undocumented tool usage

### Context Sections (`<context>`, `<environment>`)

**Purpose:** Situate the agent in its operational environment.

**Techniques:**

1. **Describe the workflow position**
   - "You run after the data ingestion step and before the report generator"
   - "Users access you via the mobile app during checkout"

2. **Identify stakeholders**
   - Who provides input? Who consumes output?
   - What are their expertise levels?

3. **State business constraints**
   - "Responses must comply with GDPR"
   - "We never share customer data across accounts"

4. **Define temporal context when relevant**
   - "You operate during US business hours"
   - "Data reflects the state as of the last nightly sync"

**Anti-patterns:**
- Irrelevant business context
- Missing stakeholder information
- Assuming context is obvious

### Input Sections (`<inputs>`)

**Purpose:** Document what data the agent receives and how to use it.

**Techniques:**

1. **Use the three-part format for each input:**
   ```
   **[Input Name]**
   - What it is: [Clear definition]
   - Information included: [List of data points]
   - How to use it: [Specific application in this prompt]
   ```

2. **Handle missing data explicitly**
   - "If company_size is not provided, do not infer it"
   - "If thread_history is empty, treat this as the first message"

3. **Specify data quality expectations**
   - "Email may be invalid; validate format before using"
   - "JSON should match schema X; fail gracefully if malformed"

4. **Document relationships between inputs**
   - "user_preferences overrides default_settings where conflicts exist"
   - "thread_history provides context for interpreting current_message"

**Anti-patterns:**
- Undocumented inputs
- Missing "how to use it" guidance
- No handling for edge cases (null, empty, malformed)

### Task Sections (`<task>`, `<operational_logic>`)

**Purpose:** Define the sequence of operations.

**Techniques:**

1. **Use numbered steps for sequential operations**
   ```
   1. Parse the input JSON
   2. Validate required fields are present
   3. Check business rules against the config
   4. Generate the output in the specified format
   ```

2. **Include decision points**
   ```
   4. Determine next action:
      - IF validation fails → Return error with specifics
      - IF all rules pass → Proceed to step 5
      - IF ambiguous → Flag for human review
   ```

3. **Separate phases for complex tasks**
   ```
   ## Phase 1: Data Gathering
   1. ...
   2. ...

   ## Phase 2: Analysis
   3. ...
   4. ...
   ```

4. **State the termination condition**
   - When is the task complete?
   - What triggers an exit before completion?

**Anti-patterns:**
- Prose paragraphs instead of numbered steps
- Missing decision points (what happens if X?)
- No clear end state

### Output Sections (`<output_format>`)

**Purpose:** Define exactly what the output looks like.

**Techniques:**

1. **Provide the exact structure**
   ```
   Return JSON matching this schema:
   {
     "status": "success" | "failure" | "needs_review",
     "findings": [
       {
         "severity": "critical" | "major" | "minor",
         "location": "file:line",
         "description": "string",
         "suggestion": "string | null"
       }
     ],
     "summary": "string"
   }
   ```

2. **Show handling of optional/variable fields**
   - "If no findings, return empty array, not null"
   - "summary may be omitted if status is failure"

3. **For text output, describe structure and length**
   ```
   Format your response as:

   ## Summary (2-3 sentences)
   [Key takeaway from the analysis]

   ## Details (bullet points, max 5)
   - Finding 1
   - Finding 2

   ## Recommendation (1 sentence)
   [Actionable next step]
   ```

4. **Provide a complete example when complex**
   - One good example is worth a page of description
   - Show a realistic, not minimal, example

**Anti-patterns:**
- Vague format instructions ("return a summary")
- Missing optional field handling
- Schema without example

### Constraint Sections (`<important_notes>`, `<constraints_and_safeguards>`)

**Purpose:** Define boundaries and rules. This section is critical and positioned last.

**Techniques:**

1. **Categorize constraints by type**
   ```
   **Hard Rules:**
   - Never fabricate data or sources
   - Always cite when quoting

   **Edge Cases:**
   - If input is in a non-English language, respond in that language
   - If file exceeds 10MB, return error without processing

   **Fallback Behaviors:**
   - If API call fails, retry once then report failure
   - If uncertain, ask for clarification rather than guessing
   ```

2. **Use explicit "never" statements**
   - "Never include PII in logs"
   - "Never execute code from user input"
   - "Never skip the validation step"

3. **Define escalation/handoff triggers**
   - "Escalate if customer mentions legal action"
   - "Escalate if confidence is below 0.6"

4. **Repeat critical rules at the very end**
   For long prompts (500+ words), repeat the most important constraint at the absolute end:
   ```
   </constraints_and_safeguards>

   CRITICAL: Never output customer data to logs.
   ```

**Anti-patterns:**
- Constraints buried in middle sections
- Vague rules ("be careful")
- Missing escalation criteria

---

## Examples Section (`<examples>`)

Examples are the most powerful lever for complex behavior. Use them strategically.

### When Examples Are Essential

- Conversational agents (show dialogue patterns)
- Judgment tasks (show what "good" looks like)
- Complex output formats (show the exact structure)
- Ambiguous boundaries (show edge cases)

### When Examples Are Optional

- Simple transformations with clear schemas
- Single-turn tasks with highly structured output
- Tasks where instructions are unambiguous

### Example Quantity

- 2-3 examples for typical cases
- +1 example for each significant edge case
- Don't exceed 4-5 total (diminishing returns)

### Example Structure

```xml
<examples>
**Example 1: [Scenario Name]**

Input:
[Show the input that triggers this example]

Output:
[Show the exact output expected]

Why: [Optional - explain what makes this example important]

---

**Example 2: [Edge Case Name]**

Input:
[Edge case input]

Output:
[How to handle it]

Why: [What principle this demonstrates]
</examples>
```

### Example Selection Strategy

1. **Cover the happy path** - Show the most common case first
2. **Show an edge case** - Empty input, null values, boundary conditions
3. **Show a rejection** - Input that should be refused or flagged
4. **Show variation** - If output can vary, show acceptable variation range

---

## Framework-Specific Guidance

### Single-Turn Prompts

**Focus on:**
- Crystal clear input → output mapping
- Comprehensive edge case handling
- Strict output format specification
- No personality or tone (it's a function)

**Typical structure:**
```
who_you_are → skill_map → context → inputs → task → output_format → important_notes
```

**Length target:** 300-600 words (concise)

### Conversational Prompts

**Focus on:**
- Consistent persona across turns
- Conversation flow and repair
- Clarification strategies
- Examples that show multi-turn patterns

**Typical structure:**
```
who_you_are → tone_and_style → context → inputs → knowledge_scope → capabilities → operational_logic → examples → output_format → constraints_and_safeguards
```

**Length target:** 600-1200 words (room for examples and nuance)

---

## Quality Checklist

Run through this before finalizing any prompt:

### Structure
- [ ] XML tags used for all sections
- [ ] Constraints positioned at the end
- [ ] Each section has a single focused purpose
- [ ] Sections appear in logical order

### Content
- [ ] Identity is specific (not generic)
- [ ] Knowledge boundaries are explicit ("you don't know X")
- [ ] All inputs documented with "how to use"
- [ ] Task steps are numbered and sequential
- [ ] Decision points have branches
- [ ] Output format is exact (schema or example)
- [ ] Negative constraints included ("never do X")

### Robustness
- [ ] Empty/null input handling defined
- [ ] Malformed input handling defined
- [ ] Failure/error behavior defined
- [ ] Escalation criteria defined (for conversational)

### For Conversational
- [ ] Tone and style described
- [ ] Examples show dialogue patterns
- [ ] Clarification strategy defined
- [ ] Session opening/closing patterns defined

### For Tools
- [ ] Each tool fully documented
- [ ] Confirmation requirements specified
- [ ] Error handling per tool
- [ ] Rate limiting mentioned if relevant

### For Structured Output
- [ ] Complete schema provided
- [ ] Optional field handling specified
- [ ] Example output included
- [ ] Validation rules mentioned

---

## Common Patterns

### Pattern: Confidence Scoring

Add confidence metadata to enable retry logic:

```xml
<output_format>
{
  "result": { ... },
  "confidence": 0.0-1.0,
  "reasoning": "1-sentence explanation"
}

Confidence guidelines:
- 0.9+: High confidence, no ambiguity
- 0.7-0.9: Moderate confidence, minor ambiguity
- 0.5-0.7: Low confidence, significant ambiguity
- <0.5: Very low, consider asking for clarification
</output_format>
```

### Pattern: Graceful Degradation

Handle partial failures without complete failure:

```xml
<important_notes>
If a tool call fails:
1. Retry once with same parameters
2. If still fails, continue without that data
3. Note the missing data in the output
4. Do NOT fail the entire task for a single tool failure
</important_notes>
```

### Pattern: Explicit Rejection

Define when to refuse a request:

```xml
<constraints>
Reject the request if:
- Input contains personally identifiable information
- Request asks for legal/medical advice
- Content promotes harm

When rejecting, explain why and suggest an alternative.
</constraints>
```

### Pattern: Structured Error Responses

Standardize error handling:

```xml
<output_format>
On success:
{ "status": "success", "result": { ... } }

On error:
{
  "status": "error",
  "error_code": "INVALID_INPUT" | "TOOL_FAILURE" | "AMBIGUOUS_REQUEST",
  "error_message": "Human-readable explanation",
  "recoverable": true | false
}
</output_format>
```

---

## Anti-Patterns to Avoid

### 1. The "Kitchen Sink" Prompt
**Problem:** Trying to make the agent do everything
**Fix:** Narrow the scope. Split into multiple specialized agents.

### 2. The "Clever" Prompt
**Problem:** Relying on subtle implications or wordplay
**Fix:** Be explicit and literal. Models don't appreciate cleverness.

### 3. The "Trust Me" Prompt
**Problem:** Assuming the model will "figure it out"
**Fix:** Define every edge case. Explicit beats implicit.

### 4. The "Wall of Text" Prompt
**Problem:** Long paragraphs of prose instructions
**Fix:** Use numbered lists, XML structure, and whitespace.

### 5. The "Moving Target" Prompt
**Problem:** Conflicting or ambiguous instructions
**Fix:** Review for contradictions. Have one authoritative section per topic.

### 6. The "Optimistic" Prompt
**Problem:** No handling for failures, errors, or edge cases
**Fix:** Add explicit handling for every thing that could go wrong.

---

## Testing a Prompt

### Manual Testing Checklist

1. **Happy path:** Does it produce correct output for typical input?
2. **Empty input:** What happens with null, empty string, empty array?
3. **Malformed input:** What happens with invalid JSON, wrong types?
4. **Edge cases:** Boundary conditions, unusual values?
5. **Adversarial input:** What happens if someone tries to break it?
6. **Consistency:** Run the same input 5 times. Is output consistent?

### Questions to Ask

- "If I gave this prompt to a new team member, would they understand what to do?"
- "Have I covered every branch of the decision tree?"
- "What's the worst thing this agent could output? How do I prevent it?"
- "If this agent fails, how will I know? How will I recover?"

---

## Integration with Frameworks and Roles

When writing a prompt:

1. **Start with the framework template** (`single-turn.md` or `conversational.md`)
   - Copy the section structure
   - Use the section order as specified

2. **Apply role-specific guidance** (from `roles/[role].md`)
   - Read the "Section-by-Section Guidance"
   - Apply advice for each section

3. **Layer in modifiers** (from `modifiers/`)
   - Check if Tools, Structured Output, Memory, or Reasoning apply
   - Read the modifier file for integration patterns
   - Check the role file's "Modifier Notes" for role-specific advice
   - Use this quick placement guide:

   **Tools** — Add tool documentation to `<capabilities>` or within `<task>`. Include: name, purpose, parameters, when to use, expected response, error handling. Specify confirmation requirements for actions with side effects.

   **Structured Output** — Define exact schema in `<output_format>`. Include field types, required vs optional, and an example output. For conversational + structured: wrap the natural language response in JSON with metadata fields (confidence, intent, reasoning).

   **Memory** — Add context handling to `<inputs>` (conversation history or session state). Include guidance on using previous context in `<operational_logic>`. Add rules for what to remember vs forget.

   **Reasoning** — Add reasoning instructions to `<task>` based on the technique:
   - Chain-of-Thought: "Think through this step by step before providing your answer"
   - Chain-of-Verification: Draft answer → generate verification questions → answer them → revise
   - Step-Back: Abstract the problem first, then reason from the abstraction
   - Tree-of-Thoughts: Generate 2-3 candidate approaches, evaluate each, select the best

   Update `<output_format>` to include reasoning trace structure. Add constraints about showing work in `<important_notes>`.

4. **Run through this checklist**
   - Verify all required sections are complete
   - Check for anti-patterns
   - Validate length is within budget

The result should be a complete prompt that follows the framework structure, applies role expertise, and incorporates any modifiers.

---

## Target-Specific Notes

When writing prompts for specific targets, keep these differences in mind. For full details, see `references/targets/`.

### DSPy

- The prompt content lives in a separate markdown file (`prompts/{agent_name}.md`) that gets loaded into the signature's docstring at runtime
- Use XML tags for section structure (same as other targets) — they work fine in docstrings
- **Skip `<output_format>`** — output structure is defined by typed `OutputField` declarations and Pydantic models in `signatures.py`
- **Add `<enum_compliance>`** for any constrained-value output fields — list valid values explicitly
- Field descriptions on `InputField`/`OutputField` are part of the compiled prompt — make them specific and actionable
- Aim for 20+ lines of substantive prompt content; brief prompts produce poor results in DSPy
- Reasoning is an architectural choice (Predict vs ChainOfThought), not prompt text — don't add "think step by step"

### LangGraph

- **Escape all literal curly braces** as `{{` and `}}` — LangGraph uses `{variable}` for template variables
- JSON examples in `<output_format>` need escaped braces: `{{"key": "value"}}`
- Document template variables `{var_name}` in the `<inputs>` section
- Full XML-section structure applies — no sections skipped
- Reasoning techniques are written directly into the prompt text (unlike DSPy)

### General

- Standard XML-section structure with no special considerations
- No escaping needed, no type system integration
- What you write is what gets used as the system message
