# Reasoning Modifier

## Purpose

Configures agents to produce explicit reasoning traces before final outputs. Reasoning techniques improve accuracy on complex tasks by forcing the model to "show its work."

---

## When to Add Reasoning

| Scenario | Add Reasoning? | Technique |
|----------|----------------|-----------|
| Multi-step logic or math | Yes | Chain-of-Thought |
| High-stakes accuracy needed | Yes | Chain-of-Verification |
| Complex problem requiring abstraction | Yes | Step-Back Prompting |
| Multiple valid solution paths | Yes | Tree-of-Thoughts |
| Simple classification or extraction | No | — |
| Speed is critical | No | — |

**Trade-off:** Reasoning increases accuracy but adds latency and token cost. Use when correctness matters more than speed.

---

## Reasoning Techniques

### 1. Zero-Shot Chain-of-Thought (CoT)

The simplest technique. Add a single phrase to trigger step-by-step reasoning.

**When to use:**
- General reasoning tasks
- Math and logic problems
- When you don't have examples to provide

**Prompt addition:**

```xml
<task>
[Your task description]

Think through this step by step before providing your final answer.
</task>
```

Or simply append: `Let's think step by step.`

**Example output structure:**

```xml
<output_format>
Structure your response as:

## Reasoning
[Step-by-step thinking process]

## Answer
[Final conclusion]
</output_format>
```

---

### 2. Chain-of-Verification (CoVe)

Four-step verification loop that reduces hallucination by up to 23%.

**When to use:**
- Factual accuracy is critical
- Agent tends to hallucinate
- High-stakes decisions
- Claims need to be verifiable

**Prompt addition:**

```xml
<task>
Answer the user's question using this verification process:

1. **Draft Response** — Generate your initial answer based on available information.

2. **Generate Verification Questions** — Create 3-5 specific questions that would verify the accuracy of your draft. These should:
   - Check specific facts or claims
   - Test for logical consistency
   - Validate quantitative information

3. **Answer Verification Questions** — Answer each question independently, treating it as a fresh query without bias from your draft.

4. **Final Verified Response** — Compare verification answers to your draft. Correct any errors, add nuances, and flag remaining uncertainties.
</task>

<output_format>
## Draft Response
[Initial answer]

## Verification Questions
1. [Question 1]
2. [Question 2]
3. [Question 3]

## Verification Answers
1. [Answer 1]
2. [Answer 2]
3. [Answer 3]

## Discrepancies Found
[Any contradictions between draft and verification]

## Final Verified Response
[Corrected answer with confidence indicators]
</output_format>
```

---

### 3. Step-Back Prompting

Two-stage approach: abstract first, then reason. Useful for complex problems that benefit from higher-level orientation.

**When to use:**
- Complex multi-factor problems
- When direct answers miss the bigger picture
- Strategic or architectural decisions
- Optimization problems

**Prompt addition:**

```xml
<task>
Before answering, use this two-stage process:

**Stage 1 — Abstraction:**
Step back and consider: What are the key factors, principles, or constraints that influence this problem? Think at a higher level before diving into specifics.

**Stage 2 — Reasoning:**
Now apply those higher-level insights to reason through the specific problem and arrive at your answer.
</task>

<output_format>
## High-Level Factors
[Key principles, constraints, and considerations]

## Detailed Reasoning
[Applying factors to the specific problem]

## Answer
[Final conclusion]
</output_format>
```

**Example:**
- Question: "How can I speed up this database query?"
- Step-back: "What factors generally affect database query performance?" (indexing, query structure, data volume, hardware, caching)
- Then: Apply those factors to the specific query

---

### 4. Tree-of-Thoughts (ToT)

Explore multiple reasoning paths with explicit evaluation. Most powerful but most expensive.

**When to use:**
- Creative problem-solving
- Multiple valid approaches exist
- Need to compare trade-offs
- Complex puzzles or planning

**Prompt addition:**

```xml
<task>
Use Tree-of-Thoughts reasoning:

1. **Generate Candidates** — Identify 2-3 distinct approaches to solve this problem.

2. **Evaluate Each Path** — For each approach, assess:
   - Feasibility: Can this work? (sure / maybe / impossible)
   - Trade-offs: What are the pros and cons?
   - Confidence: How certain are you in this path?

3. **Select and Develop** — Choose the most promising path(s) and develop them further. If a path leads to a dead end, backtrack and try another.

4. **Final Answer** — Present your best solution with justification for why you chose this path.
</task>

<output_format>
## Candidate Approaches

### Approach A: [Name]
- Description: [What this approach does]
- Feasibility: [sure / maybe / impossible]
- Pros: [Advantages]
- Cons: [Disadvantages]

### Approach B: [Name]
- Description: [What this approach does]
- Feasibility: [sure / maybe / impossible]
- Pros: [Advantages]
- Cons: [Disadvantages]

### Approach C: [Name]
[Same structure]

## Selected Path
[Which approach and why]

## Developed Solution
[Full solution following the selected approach]
</output_format>
```

---

## Prompt Adjustments by Section

### In `<task>` Section

Add the reasoning process as explicit steps:

```xml
<task>
1. Read the input carefully
2. [Reasoning technique steps — see above]
3. Provide your final answer
</task>
```

### In `<output_format>` Section

Define the reasoning trace structure:

```xml
<output_format>
Always include your reasoning before the final answer.

## Reasoning
[Your step-by-step thinking]

## Answer
[Final output]
</output_format>
```

### In `<important_notes>` Section

Add constraints on reasoning quality:

```xml
<important_notes>
- Show your reasoning for every answer
- If you're uncertain at any step, say so
- If your reasoning leads to multiple valid answers, present them with trade-offs
- Never skip to the answer without showing your work
</important_notes>
```

---

## Combining with Other Modifiers

### Reasoning + Structured Output

When you need both reasoning and structured output:

```xml
<output_format>
Return JSON with embedded reasoning:

{
  "reasoning": {
    "steps": ["Step 1...", "Step 2...", "Step 3..."],
    "uncertainties": ["Any points of doubt"]
  },
  "answer": {
    "classification": "category",
    "confidence": 0.0-1.0
  }
}
</output_format>
```

### Reasoning + Tools

For tool-using agents that need to reason about tool selection:

```xml
<task>
Before calling any tool:
1. State what information you need
2. Explain which tool will provide it and why
3. Call the tool
4. Reason about the result before proceeding
</task>
```

---

## Framework Implementation

### LangGraph with Reasoning

```python
# Add reasoning to system prompt
SYSTEM_PROMPT = """
<who_you_are>
You are an analyst who always shows your reasoning.
</who_you_are>

<task>
For every question:
1. Think through the problem step by step
2. State your reasoning explicitly
3. Then provide your answer
</task>
"""

# Or use structured output with reasoning field
class ReasonedAnswer(BaseModel):
    reasoning: list[str]  # List of reasoning steps
    answer: str
    confidence: float
```

### DSPy with Chain-of-Thought

```python
import dspy

class ReasonedClassifier(dspy.Signature):
    """Classify the input with explicit reasoning."""

    input_text: str = dspy.InputField()
    reasoning: str = dspy.OutputField(desc="Step-by-step reasoning process")
    classification: str = dspy.OutputField(desc="Final classification")
    confidence: float = dspy.OutputField(desc="Confidence 0.0-1.0")

# Use ChainOfThought module
cot = dspy.ChainOfThought(ReasonedClassifier)
```

---

## Technique Selection Guide

```
What's your primary concern?

├── Accuracy on factual claims?
│   └── Chain-of-Verification (CoVe)
│
├── Complex multi-step problem?
│   ├── Need to compare approaches?
│   │   └── Tree-of-Thoughts
│   └── Single path is fine?
│       └── Chain-of-Thought
│
├── Problem needs higher-level thinking first?
│   └── Step-Back Prompting
│
├── General reasoning improvement?
│   └── Zero-Shot Chain-of-Thought
│
└── Speed is critical?
    └── Don't add reasoning (or use minimal CoT)
```

---

## Common Pitfalls

1. **Over-engineering simple tasks** — Classification doesn't need Tree-of-Thoughts. Match technique to complexity.

2. **Reasoning without structure** — Give explicit output format or reasoning becomes rambling.

3. **Ignoring the reasoning** — If you ask for reasoning, actually use it. Don't just take the final answer.

4. **Too many verification questions** — 3-5 is optimal for CoVe. More adds latency without proportional benefit.

5. **Skipping to answers** — If the model skips reasoning, add stronger constraints in `<important_notes>`.

6. **Not calibrating confidence** — When using confidence scores, provide calibration guidelines.

---

## Token and Latency Impact

| Technique | Token Overhead | Latency Impact | Accuracy Gain |
|-----------|---------------|----------------|---------------|
| Zero-Shot CoT | +20-50% | Low | Moderate |
| Chain-of-Verification | +100-200% | High | High (up to 23%) |
| Step-Back | +50-100% | Moderate | Moderate-High |
| Tree-of-Thoughts | +200-400% | Very High | High |

**Recommendation:** Start with Zero-Shot CoT. Escalate to more complex techniques only when accuracy demands it.
