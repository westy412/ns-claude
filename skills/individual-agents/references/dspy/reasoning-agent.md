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
- Scoring/evaluation against a rubric — use **Basic Agent** (Predict) instead (evaluation is a checklist, not creative)
- Agent needs conversation history — use **Conversational Agent** (dspy.History) instead
- Agent needs to call external tools — use **Tool Agent** (ChainOfThought + ToolCalls for single-tool, ReAct for multi-tool) instead
- High-throughput pipelines where latency matters — use **Basic Agent** instead

## Predict vs ChainOfThought Decision Table

> **This is one of the most common mistakes.** Getting this wrong wastes tokens (CoT for evaluation) or loses quality (Predict for synthesis). Use this table for every agent.

| Task Type | Predictor | Why | Example |
|-----------|-----------|-----|---------|
| **Creative synthesis** | `ChainOfThought` | Needs to explore, combine, and generate novel output | Expert panel analysis, content drafting, signal blending |
| **Multi-source integration** | `ChainOfThought` | Must reason across diverse inputs to produce coherent output | Combining research from 6 sources into insights |
| **Complex judgment** | `ChainOfThought` | Decision requires weighing trade-offs with visible rationale | "Should we continue iterating or accept current version?" |
| **Scoring / evaluation** | `Predict` | Applying a rubric is a checklist, not creative reasoning | Expert scoring ideas 0.0-1.0 on a dimension |
| **Classification** | `Predict` | Mapping input to a known category | Lead tier classification (A/B/C/D) |
| **Data extraction** | `Predict` | Pulling structured data from unstructured input | Extracting company name, industry from website |
| **Targeted iteration** | `Predict` | Applying specific feedback to improve content | "Fix these 3 issues the critic identified" |

### Expert Panel Pattern (Common Confusion Point)

Expert panels often have BOTH analysis and scoring stages. **Each stage uses a different predictor:**

```
Stage 1: Expert Analysis    → ChainOfThought (creative: generating insights from research)
Stage 2: Idea Drafting      → ChainOfThought (creative: synthesizing ideas from analyses)
Stage 3: Expert Scoring     → Predict        (evaluation: scoring ideas against a rubric)
Stage 4: Refinement         → ChainOfThought (creative: improving ideas based on feedback)
Stage 5: Selection          → Predict        (evaluation: curating final output from scores)
```

**Rule of thumb:** If the agent is *generating new content or insights*, use ChainOfThought. If the agent is *judging existing content against criteria*, use Predict.

## Model Tier Assignment

> **Not all agents need the same model.** Match model capability to task complexity to optimize cost and latency.

| Pattern | Model Tier | Rationale |
|---------|-----------|-----------|
| **Parallel fan-out** (6 experts, 7 research modules) | Flash | Speed + cost at scale; many concurrent calls |
| **Single critical-path synthesis** (signal blending, drafting) | Pro | Quality matters; only 1 call, latency acceptable |
| **Search/analysis loops** (max 3 iterations) | Flash | Volume × iterations = cost multiplier |
| **Final selection/curation** | Pro | High-stakes decision on single call |

### Multi-Model Singleton Pattern

```python
# src/utils/lm.py — Two-tier singleton factory

_flash_lm = None
_pro_lm = None

def get_flash_lm() -> dspy.LM:
    """Fast, high-concurrency — for parallel fan-out operations."""
    global _flash_lm
    if _flash_lm is None:
        _flash_lm = dspy.LM(
            "gemini/gemini-2.5-flash",
            api_key=os.getenv("GOOGLE_API_KEY"),
            max_parallel_requests=2000,  # High for fan-out
            timeout=120,
        )
    return _flash_lm

def get_pro_lm() -> dspy.LM:
    """Powerful reasoning — for complex synthesis operations."""
    global _pro_lm
    if _pro_lm is None:
        _pro_lm = dspy.LM(
            "gemini/gemini-2.5-pro",
            api_key=os.getenv("GOOGLE_API_KEY"),
            max_parallel_requests=100,  # Lower — single critical-path ops
            timeout=120,
        )
    return _pro_lm
```

Then in your pipeline `__init__`:
```python
# Fan-out stages use Flash
self.expert_panel = dspy.ChainOfThought(ExpertPanelSignature)
self.expert_panel.set_lm(flash_lm)      # 6 parallel calls — Flash

# Synthesis stages use Pro
self.idea_drafter = dspy.ChainOfThought(IdeaDrafterSignature)
self.idea_drafter.set_lm(pro_lm)        # 1 critical call — Pro

# Scoring fan-out uses Flash + Predict (evaluation, not creative)
self.expert_scorer = dspy.Predict(ExpertScoringSignature)
self.expert_scorer.set_lm(flash_lm)     # 6 parallel evaluations — Flash + Predict
```

## Selection Criteria

- If task is straightforward extraction/classification → **Basic Agent** (faster)
- If task is scoring/evaluation against a rubric → **Basic Agent** (Predict, not CoT)
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

> **⚠️ CRITICAL: Typed Outputs Only — NEVER Use str + JSON Parsing**
>
> Use typed DSPy output fields (`bool`, `int`, `list[str]`, `dict[str, Any]`) or Pydantic `BaseModel`/`RootModel` as OutputField types. **NEVER use `str` fields with JSON parsing instructions.**

### Wrong vs Right: Structured Output Patterns

```python
# ❌ WRONG — str field with JSON instructions
class BadSignature(dspy.Signature):
    """Score ideas and return results as JSON."""
    ideas: str = dspy.InputField()
    scores: str = dspy.OutputField(
        desc="JSON array of {idea_id, score, reasoning}"  # ← NEVER DO THIS
    )

# ✅ RIGHT — Pydantic model with RootModel for lists
class ExpertScore(BaseModel):
    idea_id: str          # Required — LLM must produce this or retry
    score: float          # Required
    reasoning: str        # Required
    feedback: str         # Required
    strengths: list[str]  # Required
    weaknesses: list[str] # Required

class ExpertScoreList(RootModel[List[ExpertScore]]):
    """List of expert scores, one per idea."""
    pass

class GoodSignature(dspy.Signature):
    """Score ideas on your assigned dimension."""
    ideas: str = dspy.InputField()
    scores: ExpertScoreList = dspy.OutputField(    # ← Pydantic type directly
        desc="List of ExpertScore objects, one per idea."
    )
```

**Why this matters:** DSPy natively handles Pydantic models — it validates types, retries on parse errors, and gives you `.model_dump()` for serialization. String + JSON parsing is fragile, untestable, and throws away DSPy's type system.

**Accessing RootModel data:**
```python
result = await scorer.acall(...)
scores_list = result.scores.root        # .root gives the underlying List[ExpertScore]
scores_dicts = result.scores.model_dump()  # Serializes to List[dict]
```

## Signature Docstring Comprehensiveness Checklist

> **Docstrings are your prompt.** In DSPy, the Signature docstring IS the system prompt. A thin docstring produces thin output. Every production signature MUST have comprehensive docstrings.

### Required Sections (All Production Signatures)

| Section | Purpose | Example Header |
|---------|---------|----------------|
| **ROLE** | What this agent is and where it sits in the pipeline | `=== YOUR ROLE IN THE WORKFLOW ===` |
| **TASK** | Numbered step-by-step instructions for the agent | `=== YOUR TASK ===` |
| **QUALITY STANDARDS** | What "good" looks like — specific, measurable criteria | `=== QUALITY STANDARDS ===` |
| **ANTI-PATTERNS** | What NOT to do — prevent common mistakes | `=== ANTI-PATTERNS ===` |
| **OUTPUT FORMAT** | How outputs should be structured (calibration, scales, etc.) | `=== SCORING CALIBRATION ===` |

### Minimum Docstring Guidance

- **Production signatures:** 20+ lines of docstring. If your docstring is shorter, you're under-specifying.
- **Prototype/test signatures:** 5+ lines acceptable.
- **Every section** should have concrete examples, not abstract instructions.

### Well-Implemented Example (from ExpertScoringSignature)

```python
class ExpertScoringSignature(dspy.Signature):
    """
    You are a content strategy expert scoring draft ideas from a specific evaluative
    dimension. You are one of 6 experts running in parallel, each scoring ALL ideas
    from their assigned perspective.

    === YOUR ROLE IN THE WORKFLOW ===
    You are Stage 3 of a 5-stage Ideation Pipeline:
      Stage 1: Expert Panel — 6 experts analyzed research themes
      Stage 2: Idea Drafter — generated 15-20 content ideas
      Stage 3: YOU — Expert Scoring (6 experts score every idea on their dimension)
      Stage 4: Refinement — will improve ideas using YOUR scores and feedback
      Stage 5: Selection — curates final output using composite scores

    === YOUR TASK ===
    Score EVERY idea on your assigned dimension (0.0-1.0) with:
    - Calibrated scores: 0.5 = average, 0.8+ = strong, below 0.3 = weak
    - Visible reasoning explaining WHY each score was given
    - Specific, actionable feedback for the Refinement agent
    - Strengths and weaknesses from your perspective

    === SCORING CALIBRATION ===
    - 0.0-0.2: Fundamentally misaligned with this dimension
    - 0.3-0.4: Weak — significant issues from this perspective
    - 0.5-0.6: Average — functional but unremarkable
    - 0.7-0.8: Strong — solid alignment with room for improvement
    - 0.9-1.0: Exceptional — standout performance on this dimension

    Do NOT inflate scores. A mediocre idea should get 0.4-0.5, not 0.7.

    === QUALITY STANDARDS ===
    - Score EVERY idea — do not skip any, even weak ones
    - Reasoning must be specific to each idea, not generic boilerplate
    - Feedback must be actionable: "tone is too casual for this entity's professional
      positioning" not "improve brand fit"

    === ANTI-PATTERNS ===
    - Do NOT filter or remove ideas (Selection Agent does that)
    - Do NOT compute composite scores (utility function does that)
    - Do NOT modify ideas (Refinement Agent does that)
    - Do NOT produce vague reasoning
    - Do NOT inflate scores to be "nice"
    """
```

**Why this works:** The agent knows exactly where it sits in the pipeline, what its inputs look like, what "good" output means, and what mistakes to avoid. No ambiguity.

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
            timeout=120,
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

### Structured Outputs with Pydantic Models

For structured outputs with multiple items or nested data, use Pydantic BaseModel directly in OutputFields:

```python
from pydantic import BaseModel, RootModel
from typing import List
import dspy

# Define Pydantic models (simple, no validators)
class OutreachMessage(BaseModel):
    """Single message in an outreach sequence."""
    sequence_number: int
    message: str

# For List outputs, use RootModel (enables proper serialization)
class OutreachSequence(RootModel[List[OutreachMessage]]):
    pass

class CreationAgent(dspy.Signature):
    """
    Create personalized B2B outreach messages for a specific lead.

    Generate a sequence of cold outreach messages that follow the provided
    message skeleton while incorporating specific details about the lead.

    CRITICAL: Must contain ZERO em-dash (—) characters. Use commas/periods instead.
    """

    # Inputs
    lead_name: str = dspy.InputField(description="Name of the lead")
    company_name: str = dspy.InputField(description="Company name")
    context: str = dspy.InputField(description="Lead intelligence and context")
    message_skeleton: str = dspy.InputField(description="Template structure to follow")

    # Outputs - use Pydantic models directly
    response: str = dspy.OutputField(description="Explanation of your approach")
    sequence: OutreachSequence = dspy.OutputField(description="The created message sequence")

# Usage
class MessageCreator(dspy.Module):
    def __init__(self, shared_lm):
        self.creator = dspy.ChainOfThought(CreationAgent)
        self.creator.set_lm(shared_lm)

    async def aforward(self, lead_name: str, company_name: str, context: str, skeleton: str):
        result = await call_with_retry(
            self.creator,
            agent_name="message_creator",
            lead_name=lead_name,
            company_name=company_name,
            context=context,
            message_skeleton=skeleton
        )

        # Access Pydantic model directly
        sequence = result.sequence  # This is an OutreachSequence (RootModel)

        # Convert to dict/list for storage
        sequence_data = sequence.model_dump()  # Returns List[dict]

        # Access individual messages
        for msg in sequence.root:  # RootModel stores data in .root
            print(f"Message {msg.sequence_number}: {msg.message[:50]}...")

        return result
```

**Source Reference:** `ns-cold-outreach-workforce/src/workflows/message_creation/signatures.py:1-114`

**Why Pydantic instead of "output JSON strings":**
- DSPy natively supports Pydantic models in OutputFields
- Type safety and automatic validation
- Clean serialization via `.model_dump()`
- Better IDE support and autocomplete
- No string parsing needed

### Output Validation Philosophy

Pydantic model fields for LLM output should be **required by default**. Do NOT add blanket defaults (`str = ""`, `float = 0.0`) to every field as a safety net. If validation fails because the LLM didn't produce a required field, that's a signal the prompt/description needs fixing — not that the field needs a default.

- **Required fields** (`name: str`) — the LLM must produce this. DSPy retries on validation failure.
- **Optional fields** (`tags: Optional[list[str]] = None`) — genuinely optional supplementary data.
- **Never** use defaults to mask LLM output failures. Empty strings and zero scores flowing through the pipeline cause silent downstream bugs.

Use `list[MyModel]` (via `RootModel[list[MyModel]]`) instead of `list[dict]` for structured list outputs. The Pydantic model gives DSPy the field schema, which it includes in the prompt — the LLM knows exactly what to produce.

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
