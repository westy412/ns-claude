# Loop Pattern

## What It Is

An iterative refinement pattern where a Creator agent generates content, a Critic evaluates it, and an Iterator improves it based on feedback. The loop continues until quality criteria are met or max attempts reached. In DSPy, this uses separate `dspy.History` instances to maintain conversation context for each agent role.

## When to Use

- Iterative refinement (draft → feedback → revision)
- Quality gates before completion
- Creator-critic patterns
- Multiple approval conditions needed
- Output must meet specific criteria

## When to Avoid

- Single-pass processing is sufficient → use **Pipeline** instead
- Tasks are independent → use **Fan-in/Fan-out** instead
- Different paths based on input type → use **Router** instead
- No clear termination condition defined

## Loop Structure

```
Creation (once) → [Critic → Iteration] × max N iterations → END
                       ↑________|
```

Key insight: Creation runs ONCE outside the loop. Only Critic and Iterator participate in the loop.

---

## DSPy Implementation

### Code Template

```python
import os
import asyncio
import dspy
from typing import Union, Literal, List
from pydantic import BaseModel


# =============================================================================
# SINGLETON LM FACTORY
# =============================================================================

_shared_lm = None

def get_shared_lm():
    """Get or create singleton LM instance for connection pooling."""
    global _shared_lm
    if _shared_lm is None:
        _shared_lm = dspy.LM(
            os.getenv("MODEL_NAME", "gemini/gemini-2.5-flash"),
            api_key=os.getenv("API_KEY"),
            max_parallel_requests=2000,
        )
    return _shared_lm


# =============================================================================
# SIGNATURES
# =============================================================================

class CreatorSignature(dspy.Signature):
    """
    Create initial content based on requirements.

    === YOUR ROLE IN THE WORKFLOW ===
    You are the CREATOR agent. You generate the initial draft.
    Your output will be evaluated by a Critic and potentially improved by an Iterator.

    === QUALITY STANDARDS ===
    - Follow the provided requirements exactly
    - Be comprehensive but concise
    - Your draft should be production-ready on first attempt
    """
    # Inputs
    requirements: str = dspy.InputField(description="What to create")
    context: str = dspy.InputField(description="Background context")
    history: dspy.History = dspy.InputField(description="Conversation history (empty for first run)")

    # Outputs
    response: str = dspy.OutputField(description="Explanation of your approach")
    draft: str = dspy.OutputField(description="The created content")


class CriticSignature(dspy.Signature):
    """
    Evaluate content quality against criteria.

    === YOUR ROLE IN THE WORKFLOW ===
    You are the CRITIC agent. You evaluate drafts and provide feedback.
    If ALL criteria pass, set completed=True. Otherwise, provide specific feedback.

    === EVALUATION CRITERIA ===
    1. Accuracy - No factual errors or fabrications
    2. Completeness - All requirements addressed
    3. Quality - Meets professional standards

    IMPORTANT: Only set completed=True when ALL criteria pass.
    """
    # Inputs
    requirements: str = dspy.InputField(description="Original requirements")
    current_draft: str = dspy.InputField(description="Draft to evaluate")
    history: dspy.History = dspy.InputField(description="Previous evaluations")

    # Individual completion flags
    accuracy_completed: bool = dspy.OutputField(description="True if no factual errors")
    completeness_completed: bool = dspy.OutputField(description="True if all requirements met")
    quality_completed: bool = dspy.OutputField(description="True if professional quality")

    # Outputs
    response: str = dspy.OutputField(description="Overall assessment")
    feedback: str = dspy.OutputField(description="Specific actionable feedback")
    completed: bool = dspy.OutputField(description="True ONLY if ALL criteria pass")


class IteratorSignature(dspy.Signature):
    """
    Improve content based on critic feedback.

    === YOUR ROLE IN THE WORKFLOW ===
    You are the ITERATOR agent. You improve drafts based on Critic feedback.
    Make targeted improvements - don't rewrite everything.

    === IMPROVEMENT RULES ===
    - Address EVERY piece of feedback
    - Preserve what's already good
    - Make minimal necessary changes
    """
    # Inputs
    requirements: str = dspy.InputField(description="Original requirements")
    current_draft: str = dspy.InputField(description="Current draft to improve")
    critic_feedback: str = dspy.InputField(description="Feedback from Critic")
    accuracy_issue: bool = dspy.InputField(description="True if accuracy needs fixing")
    completeness_issue: bool = dspy.InputField(description="True if completeness needs fixing")
    quality_issue: bool = dspy.InputField(description="True if quality needs fixing")
    history: dspy.History = dspy.InputField(description="Previous iterations")

    # Outputs
    response: str = dspy.OutputField(description="Explanation of improvements made")
    improved_draft: str = dspy.OutputField(description="Improved content")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_creator_output(result) -> str:
    """Format creator output for critic's context."""
    return f"""
# Creator Output
## Approach
{result.response}

## Draft
{result.draft}
"""


def format_critic_output(result) -> str:
    """Format critic output for iterator's context."""
    return f"""
# Critic Evaluation
## Assessment
{result.response}

## Feedback
{result.feedback}

## Status
- Accuracy: {'✓' if result.accuracy_completed else '✗'}
- Completeness: {'✓' if result.completeness_completed else '✗'}
- Quality: {'✓' if result.quality_completed else '✗'}
- Overall: {'APPROVED' if result.completed else 'NEEDS REVISION'}
"""


def format_iterator_output(result) -> str:
    """Format iterator output for critic's next evaluation."""
    return f"""
# Iterator Revision
## Improvements Made
{result.response}

## Revised Draft
{result.improved_draft}
"""


async def call_with_retry(agent, agent_name: str, max_retries: int = 3, **kwargs):
    """Retry agent calls with exponential backoff."""
    import random

    for attempt in range(max_retries):
        try:
            result = await agent.acall(**kwargs)
            return result
        except Exception as e:
            is_rate_limit = "429" in str(e) or "rate limit" in str(e).lower()

            if attempt < max_retries - 1:
                wait_time = 30 if is_rate_limit else (2 ** attempt) * 5
                print(f"⚠ {agent_name} failed on attempt {attempt + 1}, waiting {wait_time}s")
                await asyncio.sleep(wait_time)
            else:
                print(f"✗ {agent_name} failed after {max_retries} attempts")
                raise


# =============================================================================
# LOOP MODULE
# =============================================================================

class LoopModule(dspy.Module):
    """
    Creator-Critic-Iterator loop pattern.

    Creation runs once, then Critic-Iterator loop until approved or max attempts.
    Uses separate dspy.History for each agent role.
    """

    def __init__(self, shared_lm, max_iterations: int = 3):
        """
        Initialize loop module.

        Args:
            shared_lm: Singleton LM instance (REQUIRED)
            max_iterations: Maximum critic-iterator cycles (default: 3)
        """
        if shared_lm is None:
            raise ValueError(
                "LoopModule requires a shared_lm instance. "
                "Pass get_shared_lm() to enable connection pooling."
            )

        self.lm = shared_lm
        self.max_iterations = max_iterations

        # Creator uses ChainOfThought (creative synthesis)
        self.creator = dspy.ChainOfThought(CreatorSignature)

        # Critic and Iterator use Predict (evaluation/targeted fixes)
        self.critic = dspy.Predict(CriticSignature)
        self.iterator = dspy.Predict(IteratorSignature)

        # Inject singleton LM
        self.creator.set_lm(self.lm)
        self.critic.set_lm(self.lm)
        self.iterator.set_lm(self.lm)

    def forward(self, requirements: str, context: str = "", **kwargs):
        """
        Synchronous execution for optimization/testing.

        Simplified: runs creation, one critic pass, one iteration.
        Used for DSPy optimization where full loop isn't needed.
        """
        # Creation phase
        creation_result = self.creator(
            requirements=requirements,
            context=context,
            history=dspy.History(messages=[]),
            **kwargs
        )

        # Single critic pass
        critic_result = self.critic(
            requirements=requirements,
            current_draft=creation_result.draft,
            history=dspy.History(messages=[]),
            **kwargs
        )

        # Single iteration pass (if not completed)
        if not critic_result.completed:
            iteration_result = self.iterator(
                requirements=requirements,
                current_draft=creation_result.draft,
                critic_feedback=critic_result.feedback,
                accuracy_issue=(not critic_result.accuracy_completed),
                completeness_issue=(not critic_result.completeness_completed),
                quality_issue=(not critic_result.quality_completed),
                history=dspy.History(messages=[]),
                **kwargs
            )
            final_draft = iteration_result.improved_draft
        else:
            final_draft = creation_result.draft

        return dspy.Prediction(
            creation=creation_result,
            critic=critic_result,
            final_draft=final_draft,
            approved=critic_result.completed,
        )

    async def aforward(self, requirements: str, context: str = "", **kwargs):
        """
        Async production execution with full loop.

        Includes:
        - Separate histories for Critic and Iterator
        - Full iteration loop up to max_iterations
        - Timing data collection
        """
        import time
        timings = {}

        # =================================================================
        # INITIALIZE SEPARATE HISTORIES
        # =================================================================
        # Each agent maintains its own history where:
        # - Its own outputs are "assistant" messages
        # - Other agents' outputs are "user" messages
        critic_history = dspy.History(messages=[])
        iterator_history = dspy.History(messages=[])

        # =================================================================
        # CREATION PHASE (runs once, outside loop)
        # =================================================================
        start = time.time()
        creation_result = await call_with_retry(
            self.creator,
            agent_name="creator",
            requirements=requirements,
            context=context,
            history=dspy.History(messages=[]),  # Empty history for creation
            **kwargs
        )
        current_draft = creation_result.draft
        timings['creation'] = time.time() - start

        # Add creation output to critic's history as user message
        critic_history.messages.append({
            "role": "user",
            "content": format_creator_output(creation_result)
        })

        # =================================================================
        # CRITIC-ITERATOR LOOP
        # =================================================================
        attempts = 0
        completed = False
        iteration_timings = []

        while not completed and attempts < self.max_iterations:
            iter_start = time.time()

            # ----- CRITIC PHASE -----
            critic_result = await call_with_retry(
                self.critic,
                agent_name=f"critic_iter{attempts + 1}",
                requirements=requirements,
                current_draft=current_draft,
                history=critic_history,
                **kwargs
            )

            # Add critic's output to its own history (as assistant)
            critic_formatted = format_critic_output(critic_result)
            critic_history.messages.append({
                "role": "assistant",
                "content": critic_formatted
            })

            # Check if completed
            if critic_result.completed:
                completed = True
                iteration_timings.append({
                    'iteration': attempts + 1,
                    'phase': 'critic_approved',
                    'time': time.time() - iter_start
                })
                break

            # ----- ITERATOR PHASE -----
            # Add critic's feedback to iterator's history (as user)
            iterator_history.messages.append({
                "role": "user",
                "content": critic_formatted
            })

            iteration_result = await call_with_retry(
                self.iterator,
                agent_name=f"iterator_iter{attempts + 1}",
                requirements=requirements,
                current_draft=current_draft,
                critic_feedback=critic_result.feedback,
                accuracy_issue=(not critic_result.accuracy_completed),
                completeness_issue=(not critic_result.completeness_completed),
                quality_issue=(not critic_result.quality_completed),
                history=iterator_history,
                **kwargs
            )

            # Update current draft
            current_draft = iteration_result.improved_draft

            # Add iterator's output to its own history (as assistant)
            iterator_formatted = format_iterator_output(iteration_result)
            iterator_history.messages.append({
                "role": "assistant",
                "content": iterator_formatted
            })

            # Add iterator's output to critic's history (as user) for next round
            critic_history.messages.append({
                "role": "user",
                "content": iterator_formatted
            })

            iteration_timings.append({
                'iteration': attempts + 1,
                'phase': 'full_cycle',
                'time': time.time() - iter_start
            })

            attempts += 1

        # Calculate totals
        timings['iterations'] = iteration_timings
        timings['total_iterations'] = attempts
        timings['total'] = timings['creation'] + sum(t['time'] for t in iteration_timings)

        return dspy.Prediction(
            creation=creation_result,
            final_draft=current_draft,
            approved=completed,
            iterations_performed=attempts,
            timings=timings,
        )


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

async def main():
    shared_lm = get_shared_lm()
    loop_module = LoopModule(shared_lm=shared_lm, max_iterations=3)

    result = await loop_module.aforward(
        requirements="Write a professional email introducing our B2B SaaS product",
        context="Target audience: VP of Sales at mid-market companies"
    )

    print(f"Approved: {result.approved}")
    print(f"Iterations: {result.iterations_performed}")
    print(f"Final Draft:\n{result.final_draft}")
    print(f"Timings: {result.timings}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## DSPy-Specific Notes

- **ChainOfThought for Creator:** Creative content generation benefits from visible reasoning. Use `dspy.ChainOfThought` for the Creator.

- **Predict for Critic/Iterator:** Evaluation (checklist) and targeted fixes don't need reasoning chains. Use `dspy.Predict` for efficiency.

- **Separate Histories:** Each agent maintains its own `dspy.History` where its outputs are "assistant" messages and others' outputs are "user" messages. This maintains proper conversation structure.

- **History Message Format:**
  ```python
  {"role": "user", "content": "..."}      # Other agent's output
  {"role": "assistant", "content": "..."}  # This agent's output
  ```

- **Cross-Pollination:** Critic sees Iterator's improvements as "user" messages. Iterator sees Critic's feedback as "user" messages. This enables each to build on the other's context.

---

## Key Patterns

### 1. Separate History Initialization

```python
# Each agent role gets its own history
critic_history = dspy.History(messages=[])
iterator_history = dspy.History(messages=[])
```

### 2. History Cross-Referencing

```python
# Critic's output goes to iterator as user message
iterator_history.messages.append({
    "role": "user",
    "content": format_critic_output(critic_result)
})

# Iterator's output goes back to critic as user message
critic_history.messages.append({
    "role": "user",
    "content": format_iterator_output(iteration_result)
})
```

### 3. Multi-Flag Termination

```python
class CriticSignature(dspy.Signature):
    # Individual flags for targeted iteration
    accuracy_completed: bool = dspy.OutputField()
    completeness_completed: bool = dspy.OutputField()
    quality_completed: bool = dspy.OutputField()

    # Master flag - only True when ALL pass
    completed: bool = dspy.OutputField()
```

### 4. Issue Flags for Iterator

```python
# Pass issue flags so Iterator knows what to focus on
iteration_result = await self.iterator.acall(
    accuracy_issue=(not critic_result.accuracy_completed),
    completeness_issue=(not critic_result.completeness_completed),
    quality_issue=(not critic_result.quality_completed),
    ...
)
```

### 5. Safety Counter

```python
MAX_ITERATIONS = 3

while not completed and attempts < MAX_ITERATIONS:
    # Loop logic...
    attempts += 1

# After loop: return whatever we have (approved or best attempt)
```

---

## State Flow

```
Iteration 0 (Creation):
  critic_history: []
  iterator_history: []
  current_draft: "Initial draft from Creator"

Iteration 1:
  critic_history: [
    {role: user, content: "Creator output..."},
    {role: assistant, content: "Critic feedback..."}
  ]
  iterator_history: [
    {role: user, content: "Critic feedback..."},
    {role: assistant, content: "Iterator improvements..."}
  ]
  current_draft: "Improved draft v1"

Iteration 2:
  critic_history: [
    {role: user, content: "Creator output..."},
    {role: assistant, content: "Critic feedback 1..."},
    {role: user, content: "Iterator improvements 1..."},
    {role: assistant, content: "Critic feedback 2..."}
  ]
  ...
  completed: True → EXIT
```

---

## Pitfalls & Best Practices

**Pitfalls:**

- **Single shared history** — Using one history for all agents causes role confusion. Each agent should have its own history.

- **No safety limit** — Missing `max_iterations` check causes infinite loops if completion never triggers.

- **Creator in loop** — Creator should run ONCE outside the loop. Only Critic-Iterator should loop.

- **Overwriting vs appending** — Always APPEND to history, never overwrite previous messages.

**Best Practices:**

- **Separate histories per role** — Critic and Iterator each maintain their own history.

- **Individual + master completion flags** — Track why completion failed (accuracy? completeness?) so Iterator can prioritize.

- **Format outputs for history** — Use formatter functions to create clean, structured history messages.

- **Graceful degradation** — After max iterations, return best attempt even if not approved.

---

## Comparison with Other Patterns

| Aspect | Loop | Pipeline | Router | Fan-in/Fan-out |
|--------|------|----------|--------|----------------|
| Flow | Cyclical | Linear | Branched | Parallel |
| Termination | Condition-based | End of chain | Path completion | All branches done |
| State | Iteratively refined | Accumulated | Path-dependent | Merged |
| Use case | Quality refinement | Transformation | Decision routing | Multi-perspective |
