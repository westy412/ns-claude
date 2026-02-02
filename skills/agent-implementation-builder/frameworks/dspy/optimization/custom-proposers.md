# Custom Instruction Proposers for GEPA

## Why Custom Proposers Matter

GEPA's default proposer generates generic instruction improvements. For domain-specific workflows, this produces:
- Vague suggestions ("be more specific")
- Missing context (doesn't know your enum values)
- Slow convergence (takes more iterations to find good instructions)

**Custom proposers inject domain knowledge**, enabling:
- Targeted improvements based on actual failure patterns
- Complete enum/category references in proposals
- Faster convergence through informed suggestions
- Parallel proposal generation (7x speedup)

---

## ProposalFn Interface

Custom proposers must implement the `ProposalFn` interface:

```python
from gepa.core.adapter import ProposalFn
from dspy.teleprompt.gepa.gepa_utils import ReflectiveExample

class CustomProposer(ProposalFn):
    """
    Custom instruction proposer for GEPA optimization.
    """

    def __call__(
        self,
        candidate: dict[str, str],
        reflective_dataset: dict[str, list[ReflectiveExample]],
        components_to_update: list[str]
    ) -> dict[str, str]:
        """
        Propose improved instructions for multiple components.

        Args:
            candidate: Current instructions {component_name: instruction_text}
            reflective_dataset: Feedback examples per component
                {component_name: [ReflectiveExample, ...]}
            components_to_update: Which components GEPA wants improved

        Returns:
            Updated instructions {component_name: improved_instruction}
        """
        updated = {}
        for component in components_to_update:
            current = candidate[component]
            feedback = reflective_dataset[component]
            improved = self._improve_instruction(component, current, feedback)
            updated[component] = improved
        return updated
```

---

## ReflectiveExample Structure

GEPA passes feedback as `ReflectiveExample` objects:

```python
ReflectiveExample = {
    "Inputs": {...},           # Original inputs to the module
    "Generated Outputs": {...}, # What the module actually produced
    "Feedback": "...",         # Your metric's feedback string
    "Score": 0.75              # Numeric score
}
```

**Key insight:** You have access to both the actual outputs AND the feedback. Use both to generate targeted improvements.

---

## Signature Design Pattern

The proposer uses DSPy signatures to generate improved instructions. The signature's docstring is critical - it provides all the context the LLM needs.

### Comprehensive Docstring Structure

```python
class GenerateImprovedInstruction(dspy.Signature):
    """
    <who_you_are>
    You are an expert Prompt Architect specializing in DSPy instruction optimization.
    Your goal is to improve agent instructions based on feedback from failed examples.
    </who_you_are>

    ═══════════════════════════════════════════════════════════════════════════════
    SYSTEM ARCHITECTURE & WORKFLOW CONTEXT
    ═══════════════════════════════════════════════════════════════════════════════

    **OVERALL SYSTEM: [Describe the full workflow]**

    STAGE 1: [First stage description]
    ├─ Agent 1: [Name] ← [What it does] ([N] fields)
    ├─ Agent 2: [Name] ← [What it does] ([N] fields)
    └─ Agent 3: [Name] ← [What it does] ([N] fields)

    STAGE 2: [Second stage description]
    └─ ...

    ═══════════════════════════════════════════════════════════════════════════════
    COMPLETE ENUM FIELD REFERENCE
    ═══════════════════════════════════════════════════════════════════════════════

    **AGENT 1: [Name] - [N] ENUM FIELDS**

    1. industry (single-select)
       VALID VALUES: B2B SaaS, B2C Software, Enterprise Software, IT Services,
       Cybersecurity, Marketing Agency, Financial Services, Healthcare Tech,
       [... complete list of all valid values ...]

    2. company_size (single-select)
       VALID VALUES: 1-10, 11-50, 51-200, 201-500, 501-1000, 1000+

    ═══════════════════════════════════════════════════════════════════════════════
    THE STAKES - CONSEQUENCES OF GENERIC VS SPECIFIC
    ═══════════════════════════════════════════════════════════════════════════════

    ❌ If instructions produce GENERIC outputs:
    - industry = "Technology" → Wrong categorization → Bad prioritization
    - Result: Wasted resources, low conversion, brand damage

    ✅ If instructions produce SPECIFIC outputs:
    - industry = "B2B SaaS - Sales Engagement" → Precise match → Right priority
    - Result: Correct prioritization, high conversion

    ═══════════════════════════════════════════════════════════════════════════════
    YOUR TASK
    ═══════════════════════════════════════════════════════════════════════════════

    Given the current instruction and feedback on failures, generate an IMPROVED
    instruction that addresses the specific issues identified.

    REMEMBER: NO LENGTH LIMITS. COMPREHENSIVENESS > BREVITY. THIS IS YOUR ONE SHOT.
    """

    current_instruction: str = dspy.InputField(
        desc="The current instruction being used by this agent"
    )
    feedback_summary: str = dspy.InputField(
        desc="Aggregated feedback from failed examples showing what went wrong"
    )
    component_name: str = dspy.InputField(
        desc="Name of the component being optimized (e.g., 'agent_a.predict')"
    )
    actual_output: str = dspy.InputField(
        desc="The actual outputs produced by the agent (to see failure patterns)"
    )

    improved_instruction: str = dspy.OutputField(
        desc="""Your output is a COMPREHENSIVE IMPROVED INSTRUCTION that will become the
system prompt for a downstream agent. This is your ONE CHANCE to fix the issues
identified in the feedback - there is no iteration, no clarification, no follow-up.

═══════════════════════════════════════════════════════════════════════════════
CRITICAL: ITERATIVE IMPROVEMENT, NOT REPLACEMENT
═══════════════════════════════════════════════════════════════════════════════

**PRESERVE the existing working parts** from current_instruction:
- The agent's understanding of WHERE it fits in the workflow
- Working formatting and structure patterns
- Successful examples and decision trees

**ADD targeted fixes** for the failure patterns identified:
- New guidance for specific error types
- Additional examples showing correct behavior
- Decision trees for ambiguous cases

═══════════════════════════════════════════════════════════════════════════════
REQUIRED XML STRUCTURE
═══════════════════════════════════════════════════════════════════════════════

Organize your instruction using these XML sections:

<role_and_context>
Who the agent is and where it fits in the workflow
</role_and_context>

<input_processing>
How to interpret and validate inputs
</input_processing>

<output_requirements>
Exact format and validation rules for each output field
</output_requirements>

<decision_trees>
Step-by-step logic for ambiguous cases
</decision_trees>

<examples>
Before/after examples showing correct transformations
</examples>

<validation_checklist>
Self-critique steps before outputting
</validation_checklist>

═══════════════════════════════════════════════════════════════════════════════
DEPTH REQUIREMENT
═══════════════════════════════════════════════════════════════════════════════

Each section must be EXHAUSTIVELY detailed:
- NOT: "Generate personalized messages" (too vague)
- YES: Step-by-step process with sub-steps, decision trees, examples, edge cases

Think: "If someone with ZERO context reads this, can they execute PERFECTLY?"
Every section should read like a MANUAL, not a summary.

NO LENGTH LIMITS. COMPREHENSIVENESS > BREVITY. THIS IS YOUR ONE SHOT."""
    )
```

### What to Include in Docstrings

| Section | Purpose | Length |
|---------|---------|--------|
| Who you are | Set proposer LLM's role | 2-3 sentences |
| System architecture | Full workflow context | As needed |
| Enum references | ALL valid values | Complete lists |
| Stakes/consequences | Business impact | 5-10 bullet points |
| Failure patterns | Common mistakes | With examples |
| Theory of mind | Think like downstream agent | 3-5 points |

**Philosophy:** "NO LENGTH LIMITS. COMPREHENSIVENESS > BREVITY."

Production proposer signatures are often **500-2000 lines**. This is intentional - the LLM needs complete context to generate useful improvements.

---

## Output Format Requirements

The `improved_instruction` OutputField must specify the exact format expected. This is critical for consistent, high-quality instruction proposals.

### The Iterative Improvement Philosophy

```
❌ WRONG: Replace the entire instruction
✅ RIGHT: Preserve working parts + Add targeted fixes
```

Your OutputField description should enforce:

1. **Preserve existing context** - Don't lose what's working
2. **Add targeted fixes** - Address specific failure patterns
3. **Use XML structure** - Organize for clarity and parsing
4. **Exhaustive detail** - Manual, not summary

### Required XML Structure

Specify these sections in your OutputField:

```xml
<role_and_context>
Who the agent is and where it fits in the workflow
</role_and_context>

<input_processing>
How to interpret and validate inputs
</input_processing>

<output_requirements>
Exact format and validation rules for each output field
Include ALL valid enum values (complete lists, not "50+ options")
</output_requirements>

<decision_trees>
Step-by-step logic for ambiguous cases
If X then Y, else if Z then W
</decision_trees>

<examples>
Before/after examples showing correct transformations
Include edge cases and failure patterns
</examples>

<validation_checklist>
Self-critique steps before outputting
"Have I checked X? Have I verified Y?"
</validation_checklist>
```

### Depth Requirement

Each section must be exhaustively detailed:

| Too Vague | Correct |
|-----------|---------|
| "Be specific" | "Extract the exact product name, not category. Example: 'Salesforce CRM' not 'CRM software'" |
| "Format correctly" | "Output industry as one of: B2B SaaS, B2C Software, Enterprise Software, IT Services..." |
| "Personalize the message" | "Reference specific pain points from their website. If they mention 'scaling challenges', use that exact phrase..." |

**Philosophy:** "If someone with ZERO context reads this, can they execute PERFECTLY?"

---

## Multi-Signature Routing

Different components may need different proposer strategies:

```python
class RoutedProposer(ProposalFn):
    """
    Route components to specialized signatures.

    - Analysis agents → Simple signature (general improvement)
    - Categorizers → Contextual signature (with category definitions)
    - Rankers → Contextual signature (with ranking criteria)
    """

    def __init__(self, domain_definitions, proposer_lm=None):
        self.domain_definitions = domain_definitions

        # Create dedicated LM for proposing
        self.proposer_lm = proposer_lm or dspy.LM(
            "gemini/gemini-2.5-pro",
            thinking_budget=10000,
            max_tokens=60000
        )

        # Different signatures for different component types
        self.simple_improver = dspy.Predict(GenerateSimpleInstruction)
        self.simple_improver.set_lm(self.proposer_lm)

        self.contextual_improver = dspy.Predict(GenerateContextualInstruction)
        self.contextual_improver.set_lm(self.proposer_lm)

    def _route_component(self, component_name: str):
        """Determine which signature to use."""
        if component_name in ["agent_a.predict", "agent_b.predict"]:
            return "simple"
        elif "categorizer" in component_name or "ranker" in component_name:
            return "contextual"
        else:
            return "simple"  # Default

    def _get_domain_context(self, component_name: str) -> str:
        """Get domain context for contextual components."""
        if "icp_categorizer" in component_name:
            return self._format_all_icps()
        elif "persona_categorizer" in component_name:
            return self._format_all_personas()
        elif "ranker" in component_name:
            return self._format_ranking_criteria()
        return ""
```

---

## Parallel Proposal Execution

Run all component proposals concurrently for massive speedup:

```python
import asyncio
import nest_asyncio
nest_asyncio.apply()  # Enable nested event loops

class ParallelProposer(ProposalFn):
    """
    Propose improvements for all components IN PARALLEL.

    Reduces iteration time from ~14 min (7 × 2 min) to ~2 min.
    """

    async def _propose_for_component_async(
        self,
        component_name: str,
        current_instruction: str,
        feedback_text: str,
        actual_output: str
    ) -> tuple[str, str]:
        """Generate improved instruction for one component."""

        # Route to appropriate signature
        route = self._route_component(component_name)

        if route == "simple":
            result = await self.simple_improver.acall(
                current_instruction=current_instruction,
                feedback_summary=feedback_text,
                component_name=component_name,
                actual_output=actual_output
            )
        else:
            domain_context = self._get_domain_context(component_name)
            result = await self.contextual_improver.acall(
                current_instruction=current_instruction,
                feedback_summary=feedback_text,
                component_name=component_name,
                domain_context=domain_context,
                actual_output=actual_output
            )

        return (component_name, result.improved_instruction)

    def __call__(
        self,
        candidate: dict[str, str],
        reflective_dataset: dict[str, list[ReflectiveExample]],
        components_to_update: list[str]
    ) -> dict[str, str]:
        """
        GEPA interface is synchronous, but we run async internally.
        """

        # Prepare data for each component
        tasks_data = []
        for component in components_to_update:
            current = candidate[component]
            examples = reflective_dataset[component]
            feedback = self._aggregate_feedback(examples)
            outputs = self._extract_outputs(examples)
            tasks_data.append((component, current, feedback, outputs))

        # Run all proposals in parallel
        async def _run_parallel():
            tasks = [
                self._propose_for_component_async(comp, curr, fb, out)
                for comp, curr, fb, out in tasks_data
            ]
            return await asyncio.gather(*tasks, return_exceptions=True)

        results = asyncio.run(_run_parallel())

        # Process results
        updated = {}
        for result in results:
            if isinstance(result, Exception):
                print(f"Proposal failed: {result}")
                continue
            component_name, improved = result
            updated[component_name] = improved

        return updated

    def _aggregate_feedback(self, examples: list[ReflectiveExample]) -> str:
        """Combine feedback from all examples."""
        return "\n".join([
            f"Example {i+1}: {ex.get('Feedback', 'No feedback')}"
            for i, ex in enumerate(examples)
        ])

    def _extract_outputs(self, examples: list[ReflectiveExample]) -> str:
        """Extract actual outputs to show failure patterns."""
        outputs = []
        for i, ex in enumerate(examples):
            generated = ex.get("Generated Outputs", {})
            outputs.append(f"Example {i+1}:\n{generated}")
        return "\n\n".join(outputs)
```

---

## Domain Context Injection

Inject business-specific knowledge into proposals:

```python
class DomainAwareProposer(ProposalFn):
    """
    Inject domain definitions into instruction proposals.
    """

    def __init__(self, all_icps, all_personas, icp_to_personas=None):
        self.all_icps = all_icps
        self.all_personas = all_personas
        self.icp_to_personas = icp_to_personas or {}

    def _format_all_icps(self) -> str:
        """Format all ICP definitions for categorizer context."""
        summaries = []
        for icp in self.all_icps:
            icp_id = icp.get("id", "Unknown")
            icp_text = icp.get("definition", "")
            summaries.append(f"ICP ID: {icp_id}\n{icp_text}")

        return f"Available ICPs ({len(self.all_icps)} total):\n\n" + \
               "\n\n---\n\n".join(summaries)

    def _get_personas_for_icp(self, icp_id: str) -> str:
        """Get only personas that belong to the selected ICP."""
        persona_ids = self.icp_to_personas.get(icp_id, [])
        relevant = [p for p in self.all_personas if p["id"] in persona_ids]

        summaries = []
        for persona in relevant:
            summaries.append(f"Persona ID: {persona['id']}\n{persona['definition']}")

        return f"Personas for ICP {icp_id} ({len(relevant)} total):\n\n" + \
               "\n\n---\n\n".join(summaries)
```

**Why full definitions:**
- Categorizers need ALL options to choose from
- Proposer can't suggest "use ICP-7" if it doesn't know what ICP-7 is
- Complete context enables specific, actionable improvements

---

## Complete Example: Three-Signature Proposer

For a workflow with Creation, Critic, and Iteration agents:

```python
class MessageCreationProposer(ProposalFn):
    """
    Three specialized signatures for message creation workflow.

    - CreationAgent → Focus on voice, personalization, structure
    - CriticAgent → Focus on quality gating, issue detection
    - IterationAgent → Focus on surgical fixes, preservation
    """

    def __init__(self, proposer_lm=None):
        self.proposer_lm = proposer_lm or dspy.LM(
            "gemini/gemini-2.5-pro",
            thinking_budget=5000,
            max_tokens=30000
        )

        # Three specialized improvers
        self.creation_improver = dspy.Predict(GenerateCreationInstruction)
        self.creation_improver.set_lm(self.proposer_lm)

        self.critic_improver = dspy.Predict(GenerateCriticInstruction)
        self.critic_improver.set_lm(self.proposer_lm)

        self.iteration_improver = dspy.Predict(GenerateIterationInstruction)
        self.iteration_improver.set_lm(self.proposer_lm)

    async def _propose_for_component_async(self, component_name, current, feedback, outputs):
        if "creation_agent" in component_name:
            result = await self.creation_improver.acall(
                current_instruction=current,
                feedback_summary=feedback,
                component_name=component_name,
                actual_output=outputs
            )
        elif "critic_agent" in component_name:
            result = await self.critic_improver.acall(
                current_instruction=current,
                feedback_summary=feedback,
                component_name=component_name,
                actual_output=outputs
            )
        elif "iteration_agent" in component_name:
            result = await self.iteration_improver.acall(
                current_instruction=current,
                feedback_summary=feedback,
                component_name=component_name,
                actual_output=outputs
            )
        else:
            # Fallback
            result = await self.creation_improver.acall(
                current_instruction=current,
                feedback_summary=feedback,
                component_name=component_name,
                actual_output=outputs
            )

        return (component_name, result.improved_instruction)

    def __call__(self, candidate, reflective_dataset, components_to_update):
        # Parallel execution (same pattern as above)
        ...
```

---

## Creating Your Own Proposer

### Step 1: Identify Component Types

```python
# List all components in your pipeline
components = [
    "extractor.predict",      # Analysis
    "categorizer.predict",    # Needs category definitions
    "ranker.predict",         # Needs ranking criteria
    "generator.predict",      # Content creation
]

# Group by signature needs
SIMPLE_COMPONENTS = ["extractor.predict", "generator.predict"]
CONTEXTUAL_COMPONENTS = ["categorizer.predict", "ranker.predict"]
```

### Step 2: Define Signatures

Create signatures with comprehensive docstrings for each component type.

### Step 3: Implement Routing

```python
class MyProposer(ProposalFn):
    def _route(self, component_name):
        if component_name in SIMPLE_COMPONENTS:
            return self.simple_improver
        return self.contextual_improver
```

### Step 4: Add Parallel Execution

Use `asyncio.gather()` to run all proposals concurrently.

### Step 5: Test

```python
# Test proposer independently before using in GEPA
proposer = MyProposer(domain_definitions=load_defs())

test_candidate = {"agent_a.predict": "Current instruction..."}
test_dataset = {"agent_a.predict": [mock_reflective_example]}
test_components = ["agent_a.predict"]

result = proposer(test_candidate, test_dataset, test_components)
print(result["agent_a.predict"])  # Should be improved instruction
```

---

## Performance Comparison

| Approach | Time per Iteration | Notes |
|----------|-------------------|-------|
| Sequential default | ~14 min | 7 components × 2 min each |
| Sequential custom | ~14 min | Same time, better quality |
| Parallel custom | ~2 min | 7x speedup via asyncio.gather |

**Always use parallel execution for multi-component workflows.**

---

## Related Documentation

- [Overview](overview.md) - Optimization concepts
- [Metrics](metrics.md) - Designing effective metrics
- [Training Data](data.md) - Preparing training examples
- [GEPA Workflow](gepa-workflow.md) - End-to-end GEPA usage
