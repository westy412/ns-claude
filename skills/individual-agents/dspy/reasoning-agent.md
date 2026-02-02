# Reasoning Agent (dspy.ChainOfThought)

## What It Is

A single-turn LLM call that produces a visible reasoning trace before generating output fields. Extends the basic Predict pattern by automatically adding a `reasoning` field that captures the agent's step-by-step thought process.

## When to Use

- Creative content generation (drafting, writing, synthesis)
- Complex decisions requiring justification
- Tasks where understanding the reasoning helps debugging
- Multi-input synthesis (combining information from multiple sources)
- When output quality matters more than speed
- Tasks where errors are costly and you need to understand why failures occur

## When to Avoid

- Simple extraction or classification — use **Basic Agent** (Predict) instead (faster, cheaper)
- Agent needs conversation history — use **Conversational Agent** (dspy.History) instead
- Agent needs to call external tools — use **Tool Agent** (dspy.ReAct) instead
- High-throughput pipelines where latency matters — use **Basic Agent** instead

## Selection Criteria

- If task is straightforward extraction/classification → **Basic Agent** (faster)
- If you need to understand how the agent reached its conclusion → **Reasoning Agent**
- If building a multi-turn conversation → **Conversational Agent**
- If agent needs external data or actions → **Tool Agent**
- If quality matters more than speed → **Reasoning Agent**

## Inputs / Outputs

**Inputs:**
- Input fields defined in the Signature
- Singleton LM instance (required for concurrency)

**Outputs:**
- `reasoning` field (automatically added by ChainOfThought)
- Output fields defined in the Signature
- Access via `result.reasoning`, `result.field_name`

## Prompting Guidelines

The reasoning trace benefits from explicit guidance:

- Ask for step-by-step thinking in the docstring
- Specify what aspects should be considered during reasoning
- Request justification for decisions
- For creative tasks, encourage exploration of multiple approaches
- Include quality criteria that the reasoning should address

---

## DSPy Implementation

### Signature Definition

```python
import dspy
from typing import List

class ContentCreatorSignature(dspy.Signature):
    """
    Generate personalized outreach content based on lead intelligence.

    === YOUR ROLE IN THE WORKFLOW ===
    You are the CREATION agent in a Creator-Critic loop.

    YOUR JOB: Synthesize all gathered intelligence into compelling, personalized content
    that resonates with the specific lead.

    WORKFLOW CONTEXT:
    - Previous agents have extracted: company info, ICP analysis, persona details
    - Your output will be evaluated by a Critic agent
    - If the Critic finds issues, you may be asked to revise

    === REASONING GUIDANCE ===

    Before generating content, think through:
    1. What specific pain points does this lead likely have?
    2. What tone and style matches their industry and role?
    3. What unique angles can make this message stand out?
    4. How can I demonstrate genuine understanding of their situation?

    SHOW YOUR WORK: Your reasoning will be used to understand your creative decisions
    and improve future generations.

    === QUALITY STANDARDS ===
    - Content must feel personally crafted, not templated
    - Reference specific details from the lead intelligence
    - Avoid generic phrases like "I hope this finds you well"
    - Keep content concise - respect the recipient's time
    """

    # Input fields
    company_analysis: str = dspy.InputField(
        description="Formatted company intelligence from previous agents"
    )
    persona_analysis: str = dspy.InputField(
        description="Analysis of the specific contact person"
    )
    campaign_context: str = dspy.InputField(
        description="Campaign goals and messaging guidelines"
    )

    # Output fields (reasoning is added automatically by ChainOfThought)
    subject_line: str = dspy.OutputField(
        description="Compelling email subject line (max 50 chars)"
    )
    opening_hook: str = dspy.OutputField(
        description="Personalized opening that demonstrates research"
    )
    value_proposition: str = dspy.OutputField(
        description="Clear value proposition tailored to their pain points"
    )
    call_to_action: str = dspy.OutputField(
        description="Specific, low-friction next step"
    )
```

### Module Implementation

```python
import os
import dspy

# ============================================
# SINGLETON LM PATTERN (CRITICAL)
# ============================================
_shared_lm = None

def get_shared_lm():
    """
    Get or create singleton LM instance.

    CRITICAL: Prevents 20x slowdown when running 100+ concurrent workflows.
    """
    global _shared_lm
    if _shared_lm is None:
        _shared_lm = dspy.LM(
            os.getenv("MODEL_NAME", "gemini/gemini-2.5-flash"),
            api_key=os.getenv("GOOGLE_API_KEY"),
            max_parallel_requests=2000,
        )
    return _shared_lm


# ============================================
# REASONING AGENT MODULE
# ============================================
class ContentCreator(dspy.Module):
    """
    Reasoning agent that generates personalized content with visible thought process.

    Uses dspy.ChainOfThought to capture reasoning before output generation.
    """

    def __init__(self, shared_lm):
        """
        Initialize with shared LM instance.

        Args:
            shared_lm: Singleton LM from get_shared_lm(). Required.

        Raises:
            ValueError: If shared_lm is None
        """
        if shared_lm is None:
            raise ValueError(
                "ContentCreator requires a shared_lm instance. "
                "Pass get_shared_lm() to enable connection pooling."
            )

        self.lm = shared_lm

        # Create ChainOfThought predictor (NOT Predict)
        self.creator = dspy.ChainOfThought(ContentCreatorSignature)

        # CRITICAL: Inject singleton LM
        self.creator.set_lm(self.lm)

    def forward(
        self,
        company_analysis: str,
        persona_analysis: str,
        campaign_context: str
    ) -> dspy.Prediction:
        """
        Synchronous forward pass.

        Returns:
            dspy.Prediction with reasoning, subject_line, opening_hook,
            value_proposition, call_to_action fields
        """
        result = self.creator(
            company_analysis=company_analysis,
            persona_analysis=persona_analysis,
            campaign_context=campaign_context
        )

        return result

    async def aforward(
        self,
        company_analysis: str,
        persona_analysis: str,
        campaign_context: str
    ) -> dspy.Prediction:
        """
        Async forward pass for concurrent workflows.
        """
        result = await self.creator.acall(
            company_analysis=company_analysis,
            persona_analysis=persona_analysis,
            campaign_context=campaign_context
        )

        return result


# ============================================
# USAGE EXAMPLE
# ============================================
async def main():
    lm = get_shared_lm()
    creator = ContentCreator(shared_lm=lm)

    result = await creator.aforward(
        company_analysis="Acme Corp is a B2B SaaS company...",
        persona_analysis="John Smith is the VP of Sales...",
        campaign_context="Goal: Book demo calls for our automation platform"
    )

    # Access the reasoning trace
    print("=== Reasoning ===")
    print(result.reasoning)
    print()

    # Access output fields
    print("=== Generated Content ===")
    print(f"Subject: {result.subject_line}")
    print(f"Hook: {result.opening_hook}")
    print(f"Value Prop: {result.value_proposition}")
    print(f"CTA: {result.call_to_action}")
```

### Using Reasoning for Debugging

```python
async def create_with_logging(creator, **inputs):
    """
    Create content and log reasoning for debugging.
    """
    result = await creator.aforward(**inputs)

    # Log reasoning for analysis
    print(f"[DEBUG] Reasoning trace:\n{result.reasoning}")

    # Check if reasoning addressed key concerns
    reasoning_lower = result.reasoning.lower()

    if "pain point" not in reasoning_lower:
        print("[WARN] Reasoning didn't explicitly consider pain points")

    if "tone" not in reasoning_lower:
        print("[WARN] Reasoning didn't consider tone/style")

    return result


async def create_with_quality_check(creator, **inputs):
    """
    Create content and use reasoning to validate quality.
    """
    result = await creator.aforward(**inputs)

    # Use reasoning to catch potential issues
    if "generic" in result.reasoning.lower():
        print("[WARN] Agent noted content may be generic - consider revision")

    if "uncertain" in result.reasoning.lower():
        print("[WARN] Agent expressed uncertainty - may need human review")

    return result
```

### In a Creator-Critic Loop

```python
class CreatorCriticLoop(dspy.Module):
    """
    Loop where ChainOfThought creator is refined by Predict critic.
    """

    def __init__(self, shared_lm):
        if shared_lm is None:
            raise ValueError("shared_lm required")

        self.lm = shared_lm

        # Creator uses ChainOfThought (needs reasoning for creative task)
        self.creator = dspy.ChainOfThought(ContentCreatorSignature)

        # Critic uses Predict (evaluation is a checklist, not creative)
        self.critic = dspy.Predict(CriticSignature)

        # Iteration agent uses Predict (targeted fixes, not creative)
        self.iterator = dspy.Predict(IterationSignature)

        # Inject LM into all predictors
        self.creator.set_lm(self.lm)
        self.critic.set_lm(self.lm)
        self.iterator.set_lm(self.lm)

    async def aforward(self, **inputs) -> dspy.Prediction:
        """
        Run creator-critic loop with max 3 iterations.
        """
        # Initial creation (uses ChainOfThought)
        creation_result = await self.creator.acall(**inputs)
        current_content = {
            "subject_line": creation_result.subject_line,
            "opening_hook": creation_result.opening_hook,
            "value_proposition": creation_result.value_proposition,
            "call_to_action": creation_result.call_to_action
        }

        # Store reasoning for debugging
        creation_reasoning = creation_result.reasoning

        attempts = 0
        while attempts < 3:
            # Critic evaluates (uses Predict - evaluation is a checklist)
            critic_result = await self.critic.acall(
                content=str(current_content),
                **inputs
            )

            if critic_result.is_complete:
                break

            # Iterator improves based on feedback (uses Predict)
            iteration_result = await self.iterator.acall(
                current_content=str(current_content),
                feedback=critic_result.feedback,
                issue_flags=critic_result.issue_flags
            )

            # Update content for next iteration
            current_content = {
                "subject_line": iteration_result.improved_subject,
                "opening_hook": iteration_result.improved_hook,
                "value_proposition": iteration_result.improved_value_prop,
                "call_to_action": iteration_result.improved_cta
            }

            attempts += 1

        return dspy.Prediction(
            content=current_content,
            creation_reasoning=creation_reasoning,
            iterations=attempts
        )
```

### DSPy-Specific Notes

- **Automatic reasoning field:** ChainOfThought adds `reasoning` to the output automatically. Don't define it in the Signature.
- **When to use ChainOfThought:** Creative synthesis, complex decisions, tasks where you need to understand the "why".
- **When NOT to use:** Simple extraction, classification, evaluation checklists. Use Predict instead for these.
- **Token overhead:** Reasoning adds significant tokens. Budget accordingly.
- **Debugging value:** The reasoning trace is invaluable for understanding failures and improving prompts.

---

## Extended Reasoning Patterns

DSPy provides several ways to customize and extend reasoning beyond basic ChainOfThought.

### ChainOfThoughtWithHint

Use when you want to provide guidance that influences the reasoning direction.

```python
import dspy

class GuidedAnalysisSignature(dspy.Signature):
    """Analyze a problem with provided guidance."""
    problem: str = dspy.InputField()
    hint: str = dspy.InputField(description="Guidance to focus the analysis")
    analysis: str = dspy.OutputField()
    recommendation: str = dspy.OutputField()

# ChainOfThoughtWithHint uses the hint to guide reasoning
module = dspy.ChainOfThoughtWithHint(GuidedAnalysisSignature)

result = module(
    problem="Our API response times have increased by 300%",
    hint="Consider database queries, caching, and network latency"
)

print(result.reasoning)      # Auto-added, influenced by hint
print(result.analysis)
print(result.recommendation)
```

**When to use:** When you have domain knowledge that should guide the reasoning but shouldn't constrain the output directly.

### Multiple Custom Reasoning Fields

While you can't rename the auto-added `reasoning` field, you CAN add multiple custom fields that capture different aspects of thinking.

```python
import dspy

class MultiAspectAnalysisSignature(dspy.Signature):
    """
    Analyze a decision through multiple lenses.

    Think through each aspect separately before reaching conclusions.
    """
    context: str = dspy.InputField()
    decision_options: str = dspy.InputField()

    # Custom reasoning-like fields (appear AFTER auto-added 'reasoning')
    pros_analysis: str = dspy.OutputField(
        description="Analysis of advantages for each option"
    )
    cons_analysis: str = dspy.OutputField(
        description="Analysis of disadvantages for each option"
    )
    risk_assessment: str = dspy.OutputField(
        description="Risk analysis for each option"
    )
    final_recommendation: str = dspy.OutputField(
        description="Final recommendation with justification"
    )

module = dspy.ChainOfThought(MultiAspectAnalysisSignature)
result = module(
    context="Migrating to microservices architecture",
    decision_options="Option A: Full migration, Option B: Hybrid, Option C: Stay monolith"
)

# Access all fields
print(result.reasoning)            # Auto-added general reasoning
print(result.pros_analysis)        # Custom field
print(result.cons_analysis)        # Custom field
print(result.risk_assessment)      # Custom field
print(result.final_recommendation) # Custom field
```

**Output order:** `reasoning` (auto) → `pros_analysis` → `cons_analysis` → `risk_assessment` → `final_recommendation`

### Structured Reasoning with Pydantic

For complex, typed reasoning structures, use Pydantic models.

```python
from pydantic import BaseModel, Field
from typing import List
import dspy

class ReasoningStep(BaseModel):
    """Individual step in the reasoning chain."""
    step_number: int = Field(description="Step number in sequence")
    thought: str = Field(description="What is being considered")
    conclusion: str = Field(description="Conclusion from this step")

class StructuredReasoning(BaseModel):
    """Complete structured reasoning output."""
    steps: List[ReasoningStep] = Field(description="Ordered reasoning steps")
    key_assumptions: List[str] = Field(description="Assumptions made")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in conclusion")
    final_answer: str = Field(description="The final answer")

class StructuredReasoningSignature(dspy.Signature):
    """
    Solve problems with explicit structured reasoning.

    Break down your thinking into numbered steps.
    State assumptions explicitly.
    Rate your confidence.
    """
    question: str = dspy.InputField()
    context: str = dspy.InputField()

    # Single Pydantic output containing structured reasoning
    analysis: StructuredReasoning = dspy.OutputField()

module = dspy.ChainOfThought(StructuredReasoningSignature)
result = module(
    question="Should we implement feature X?",
    context="Current system state and constraints..."
)

# Access structured fields
print(f"Steps: {len(result.analysis.steps)}")
for step in result.analysis.steps:
    print(f"  {step.step_number}. {step.thought} → {step.conclusion}")
print(f"Assumptions: {result.analysis.key_assumptions}")
print(f"Confidence: {result.analysis.confidence}")
print(f"Answer: {result.analysis.final_answer}")
```

### Multi-Stage Reasoning Programs

For complex workflows, compose multiple ChainOfThought modules with distinct reasoning phases.

```python
import dspy

class MultiStageReasoner(dspy.Module):
    """
    Multi-stage reasoning with explicit phases.

    Each phase has its own ChainOfThought with focused reasoning.
    """

    def __init__(self, shared_lm):
        if shared_lm is None:
            raise ValueError("shared_lm required")

        self.lm = shared_lm

        # Phase 1: Problem Analysis
        self.analyze = dspy.ChainOfThought(
            "problem -> problem_breakdown: list[str], key_constraints: list[str]"
        )

        # Phase 2: Solution Generation
        self.generate = dspy.ChainOfThought(
            "problem_breakdown: list[str], key_constraints: list[str] -> "
            "candidate_solutions: list[str], evaluation_criteria: list[str]"
        )

        # Phase 3: Solution Evaluation
        self.evaluate = dspy.ChainOfThought(
            "candidate_solutions: list[str], evaluation_criteria: list[str] -> "
            "ranked_solutions: list[str], best_solution: str, justification: str"
        )

        # Inject LM into all modules
        self.analyze.set_lm(self.lm)
        self.generate.set_lm(self.lm)
        self.evaluate.set_lm(self.lm)

    async def aforward(self, problem: str) -> dspy.Prediction:
        # Phase 1: Analyze
        analysis = await self.analyze.acall(problem=problem)

        # Phase 2: Generate solutions
        generation = await self.generate.acall(
            problem_breakdown=analysis.problem_breakdown,
            key_constraints=analysis.key_constraints
        )

        # Phase 3: Evaluate and select
        evaluation = await self.evaluate.acall(
            candidate_solutions=generation.candidate_solutions,
            evaluation_criteria=generation.evaluation_criteria
        )

        # Return comprehensive result with all reasoning traces
        return dspy.Prediction(
            # Reasoning traces from each phase
            analysis_reasoning=analysis.reasoning,
            generation_reasoning=generation.reasoning,
            evaluation_reasoning=evaluation.reasoning,

            # Final outputs
            best_solution=evaluation.best_solution,
            justification=evaluation.justification,
            alternatives=evaluation.ranked_solutions
        )


# Usage
async def main():
    lm = get_shared_lm()
    reasoner = MultiStageReasoner(shared_lm=lm)

    result = await reasoner.aforward(
        problem="Design a scalable authentication system for 10M users"
    )

    print("=== Analysis Phase ===")
    print(result.analysis_reasoning)

    print("\n=== Generation Phase ===")
    print(result.generation_reasoning)

    print("\n=== Evaluation Phase ===")
    print(result.evaluation_reasoning)

    print("\n=== Final Recommendation ===")
    print(f"Best: {result.best_solution}")
    print(f"Why: {result.justification}")
```

### Extended Reasoning Quick Reference

| Pattern | Module | Use Case |
|---------|--------|----------|
| Basic reasoning | `ChainOfThought` | Single-step reasoning before output |
| Guided reasoning | `ChainOfThoughtWithHint` | Reasoning with domain guidance |
| Multi-aspect | Multiple OutputFields | Different reasoning facets |
| Structured | Pydantic model | Typed, validated reasoning |
| Multi-stage | Composed modules | Complex multi-phase workflows |
| Code-based | `ProgramOfThought` | Reasoning via code generation |

---

## Pitfalls & Best Practices

**Pitfalls:**

- **Using ChainOfThought for everything** — Adds unnecessary latency and cost. Reserve for tasks that genuinely benefit from visible reasoning.

- **Not reading the reasoning** — The reasoning trace is there to help you. Use it for debugging, quality checks, and prompt improvement.

- **Defining a `reasoning` field manually** — ChainOfThought adds this automatically. Defining it yourself causes conflicts.

- **Ignoring reasoning quality** — If the reasoning is poor, the output will be poor. Guide reasoning explicitly in the docstring.

- **Forgetting LM injection** — Same as Basic Agent: always use `set_lm(shared_lm)`.

**Best Practices:**

- **Guide the reasoning** — In the docstring, specify what aspects the agent should think through before answering.

- **Use reasoning for quality checks** — Check if reasoning mentions key concerns. Flag outputs where reasoning shows uncertainty.

- **Log reasoning in production** — Store reasoning traces for debugging failed or low-quality outputs.

- **Match predictor to task type:**
  - Creative synthesis → ChainOfThought
  - Evaluation/classification → Predict
  - Data extraction → Predict

- **Keep reasoning focused** — Ask for reasoning about specific aspects, not open-ended "think about everything".

---

## Comparison: Reasoning Agent vs Basic Agent

| Aspect | Basic Agent (Predict) | Reasoning Agent (ChainOfThought) |
|--------|----------------------|----------------------------------|
| Output | Defined fields only | Defined fields + `reasoning` |
| Latency | Lower | Higher |
| Token usage | Minimal | Higher (reasoning tokens) |
| Debuggability | Harder | Easier (visible reasoning) |
| Best for | Extraction, classification | Creative tasks, complex decisions |
| Cost | Lower | Higher |

### When Each Excels

**Basic Agent (Predict):**
- "Extract the industry from this website content" — Clear input → output
- "Classify this lead as A/B/C/D tier" — Checklist evaluation
- "Rank these pain points by relevance" — Sorting task

**Reasoning Agent (ChainOfThought):**
- "Generate a personalized email based on this intelligence" — Creative synthesis
- "Decide whether to continue iterating or accept the current version" — Complex judgment
- "Synthesize insights from company, persona, and campaign context" — Multi-source integration

---

## Source Reference

**Validated against:** `ns-cold-outreach-workforce/src/workflows/message_creation/create_message.py`

Patterns demonstrated:
- CreationAgent uses ChainOfThought (line 60)
- CriticAgent and IterationAgent use Predict (lines 61-62)
- Reasoning used in creator-critic loop (lines 202-431)
