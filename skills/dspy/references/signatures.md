# Signatures

In DSPy, the **Signature docstring IS the prompt**. Quality docstrings = quality outputs.

## The Core Principle

DSPy compiles the signature docstring directly into the LLM call. There's no separate prompt file - the docstring is your prompt engineering surface.

## Docstring Structure

```python
class DataExtractor(dspy.Signature):
    """
    Extract company intelligence from website content.

    === YOUR ROLE IN THE WORKFLOW ===
    You are the FIRST analysis agent in a 7-stage pipeline.

    YOUR JOB: Extract comprehensive company information from website content.
    Your output becomes the foundation that all downstream agents build upon.

    WORKFLOW OVERVIEW:
    Stage 1: YOU (DataExtractor) -> Extract company offerings
    Stage 2: CustomerAnalyzer -> Identify target customers
    Stage 3: Categorizer -> Match to predefined categories
    Stage 4: Ranker -> Assign quality tier (A/B/C/D)

    CRITICAL: Everything downstream depends on YOUR accuracy.

    === ENUM FIELD COMPLIANCE ===

    **WHY THIS MATTERS:**
    Your output is parsed by downstream systems that perform EXACT STRING MATCHING.
    If you output ANY value not in the valid options list, the workflow may fail.

    **REQUIREMENTS:**
    - Output EXACTLY one of the listed valid options
    - DO NOT output variations (e.g., "SaaS" instead of "B2B SaaS")
    - DO NOT output synonyms (e.g., "Consulting" instead of "IT Services")
    - If uncertain, use "Other" or "Unknown" - these are ALWAYS safer

    ENUM FIELD: industry
    VALID VALUES: B2B SaaS, B2C Software, Enterprise Software, IT Services, Other, Unknown

    === QUALITY STANDARDS ===
    - All claims must be traceable to the provided website content
    - No fabrication - only extract what's explicitly stated
    - Be specific - choose the MOST SPECIFIC category that applies
    """

    # Input fields
    company_name: str = dspy.InputField()
    website_content: str = dspy.InputField()

    # Output fields
    overview: str = dspy.OutputField(description="2-3 sentence company overview")
    industry: Union[Literal[...], str] = dspy.OutputField(description="See VALID VALUES above")
```

## Key Sections to Include

### 1. Role Context
Tell the agent where it sits in the workflow and what depends on its output.

```python
"""
=== YOUR ROLE IN THE WORKFLOW ===
You are the CRITIC agent in a Creator-Critic-Iteration loop.

YOUR JOB: Evaluate content against quality criteria and provide
actionable feedback for improvement.
"""
```

### 2. Enum Compliance (when applicable)
For fields with constrained values, be explicit about requirements.

```python
"""
=== ENUM FIELD COMPLIANCE ===

ENUM FIELD: pricing_model
VALID VALUES: Subscription, Usage-based, One-time, Freemium, Contact Sales, Unknown

Output EXACTLY one of these values. DO NOT paraphrase or use synonyms.
"""
```

### 3. Quality Standards
Define what "good" looks like.

```python
"""
=== QUALITY STANDARDS ===
- Content must feel personally crafted, not templated
- Reference specific details from the lead intelligence
- Avoid generic phrases like "I hope this finds you well"
- Keep content concise - respect the recipient's time
"""
```

### 4. Anti-Patterns (optional but valuable)
Tell the agent what NOT to do.

```python
"""
=== ANTI-PATTERNS (DO NOT DO) ===
- DO NOT use em-dash (—) characters anywhere
- DO NOT start with "I noticed that..."
- DO NOT include company boilerplate about yourself
"""
```

## Field Descriptions

Field descriptions provide additional guidance:

```python
overview: str = dspy.OutputField(
    description="2-3 sentence company overview based on website content"
)
industry: Literal[...] = dspy.OutputField(
    description="Industry category - must be EXACTLY one of the valid values"
)
```

## Anti-Patterns

```python
# WRONG: Brief docstring
class DataExtractor(dspy.Signature):
    """Extract company info."""  # Too brief - poor outputs

    company_name: str = dspy.InputField()
    industry: str = dspy.OutputField()  # No validation guidance

# WRONG: No field descriptions
class DataExtractor(dspy.Signature):
    """..."""
    company_name: str = dspy.InputField()  # What is this?
    output: str = dspy.OutputField()  # What format?
```

## Signature vs Prompt File

| Aspect | DSPy Signature | Separate Prompt File |
|--------|----------------|---------------------|
| Location | Docstring in signatures.py | prompts.py or similar |
| Compilation | Direct into LLM call | Manual injection |
| Optimization | DSPy can optimize | Manual tuning only |
| Type safety | OutputField types enforced | No enforcement |

## Checklist for Good Signatures

- [ ] Docstring explains role in workflow
- [ ] Enum fields have VALID VALUES listed
- [ ] Quality standards defined
- [ ] Anti-patterns included if relevant
- [ ] All InputFields have descriptions
- [ ] All OutputFields have descriptions
- [ ] Types are specific (not just `str` when Literal or Pydantic model is better)
