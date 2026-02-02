# Conversational Agent (dspy.History)

## What It Is

An agent that maintains conversation context across multiple turns using `dspy.History`. Enables multi-turn interactions where each call builds on previous exchanges, essential for iterative refinement loops, dialogue systems, and agents that need memory of prior interactions.

## When to Use

- Iterative refinement loops (creator-critic patterns)
- Multi-turn dialogue systems
- Agents that need to reference previous outputs
- Feedback incorporation workflows
- Any pattern where context accumulates across calls

## When to Avoid

- Single-turn tasks — use **Basic Agent** (Predict) instead
- Tasks requiring external tools — use **Tool Agent** (ReAct) instead
- No conversation context needed — use **Basic Agent** instead
- History would grow too large — consider summarization or windowing

## Selection Criteria

- If each call is independent → **Basic Agent**
- If calls need to reference previous exchanges → **Conversational Agent**
- If you need visible reasoning → combine with **Reasoning Agent** (ChainOfThought)
- If agent needs external data/actions → **Tool Agent**

## Inputs / Outputs

**Inputs:**
- Input fields defined in the Signature
- `dspy.History` object containing prior messages
- Singleton LM instance

**Outputs:**
- Output fields defined in the Signature
- History object should be updated after each call

## Prompting Guidelines

When using history:

- Structure history messages with clear role indicators (`user`, `assistant`)
- Keep history focused — don't accumulate irrelevant context
- Consider summarizing long histories to prevent context overflow
- Use separate history objects for different agent roles in the same workflow
- Include explicit instructions about how to use prior context

---

## Two Patterns: Agent-to-Agent vs User-to-Agent

`dspy.History` supports two distinct conversation patterns:

### 1. Agent-to-Agent Communication

Internal workflows where agents exchange messages programmatically. The "user" and "assistant" roles represent different agents in the system, not actual humans.

**Examples:**
- Creator-Critic loops (critic evaluates creator's output)
- Pipeline stages passing context
- Feedback incorporation workflows

**Characteristics:**
- History is managed by your code
- Messages are structured and predictable
- Often uses separate histories per agent role
- Focus on passing context, not natural dialogue

### 2. User-to-Agent Communication

External-facing chatbots or assistants where a human user interacts with the agent across multiple turns.

**Examples:**
- Customer support chatbots
- Interactive research assistants
- Conversational interfaces

**Characteristics:**
- History reflects actual user messages
- Unpredictable user inputs
- Single shared history for the conversation
- Focus on natural dialogue and helpfulness

---

## DSPy Implementation

### History Basics

```python
import dspy

# Create a history object
history = dspy.History(messages=[])

# Add messages with roles
history.messages.append({
    "role": "user",
    "content": "Please analyze this company: Acme Corp"
})

history.messages.append({
    "role": "assistant",
    "content": "Acme Corp is a B2B SaaS company focused on..."
})

# Pass history to a predictor
class ConversationalSignature(dspy.Signature):
    """Continue the conversation based on history."""
    current_input: str = dspy.InputField()
    history: dspy.History = dspy.InputField()
    response: str = dspy.OutputField()

predictor = dspy.Predict(ConversationalSignature)
result = predictor(
    current_input="What are their main competitors?",
    history=history
)
```

### Pattern 1: User-to-Agent Chatbot

A simple chatbot that maintains conversation with a human user.

```python
import os
import dspy

# Singleton LM (see Basic Agent for full pattern)
_shared_lm = None
def get_shared_lm():
    global _shared_lm
    if _shared_lm is None:
        _shared_lm = dspy.LM(
            os.getenv("MODEL_NAME", "openai/gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
            max_parallel_requests=2000,
        )
    return _shared_lm


class ChatbotSignature(dspy.Signature):
    """
    You are a helpful assistant. Respond to the user's message.

    === CONVERSATION CONTEXT ===
    You have access to the conversation history. Use it to:
    - Remember what the user previously asked
    - Maintain continuity in your responses
    - Reference earlier parts of the conversation when relevant

    === RESPONSE GUIDELINES ===
    - Be helpful and concise
    - Ask clarifying questions if the user's intent is unclear
    - Don't repeat information you've already provided
    """

    user_message: str = dspy.InputField(description="The user's current message")
    history: dspy.History = dspy.InputField(description="Previous conversation")

    response: str = dspy.OutputField(description="Your response to the user")


class Chatbot(dspy.Module):
    """
    User-facing chatbot with conversation memory.

    This pattern is for human-to-agent interaction.
    """

    def __init__(self, shared_lm):
        if shared_lm is None:
            raise ValueError("shared_lm required")

        self.lm = shared_lm
        self.responder = dspy.Predict(ChatbotSignature)
        self.responder.set_lm(self.lm)

        # Single history for the entire conversation
        self.history = dspy.History(messages=[])

    def chat(self, user_message: str) -> str:
        """
        Process a user message and return a response.

        Automatically manages history - just call this for each user turn.
        """
        # Add user message to history
        self.history.messages.append({
            "role": "user",
            "content": user_message
        })

        # Get response
        result = self.responder(
            user_message=user_message,
            history=self.history
        )

        # Add assistant response to history
        self.history.messages.append({
            "role": "assistant",
            "content": result.response
        })

        return result.response

    def reset(self):
        """Clear conversation history to start fresh."""
        self.history = dspy.History(messages=[])


# ============================================
# USAGE: Interactive Chat Loop
# ============================================
def main():
    lm = get_shared_lm()
    bot = Chatbot(shared_lm=lm)

    print("Chatbot ready. Type 'quit' to exit, 'reset' to clear history.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'reset':
            bot.reset()
            print("Conversation reset.\n")
            continue

        response = bot.chat(user_input)
        print(f"Bot: {response}\n")


# Example conversation:
# You: Hi, I'm looking for a good Python web framework
# Bot: I'd recommend FastAPI or Flask. FastAPI is great for APIs with automatic
#      documentation, while Flask is simpler for basic web apps. What's your use case?
# You: I need to build a REST API
# Bot: Based on your need for a REST API, I'd suggest FastAPI. It has built-in
#      support for async, automatic OpenAPI docs, and great type validation with Pydantic.
# You: What about Django?
# Bot: Django REST Framework is also excellent, especially if you need an ORM and
#      admin interface. It's heavier than FastAPI but more batteries-included.
#      Since you mentioned REST API specifically, FastAPI might be faster to get started.
```

### Pattern 2: Agent-to-Agent (Creator-Critic)

The following example shows agent-to-agent communication where the "user" and "assistant" roles represent different agents in an internal workflow, not human users.

### Signature Definition

```python
import dspy
from typing import Literal

class CriticSignature(dspy.Signature):
    """
    Evaluate content quality and provide feedback.

    === YOUR ROLE IN THE WORKFLOW ===
    You are the CRITIC agent in a Creator-Critic-Iteration loop.

    YOUR JOB: Evaluate content against quality criteria and provide
    actionable feedback for improvement.

    === USING CONVERSATION HISTORY ===
    You receive a history of previous evaluations. Use this to:
    - Avoid repeating feedback that was already addressed
    - Track which issues persist across iterations
    - Recognize improvement (or lack thereof)

    === EVALUATION CRITERIA ===
    - Personalization: Does content reference specific lead details?
    - Value proposition: Is the benefit to the recipient clear?
    - Call to action: Is there a specific, low-friction next step?
    - Tone: Does it match the industry and role?
    - Length: Is it concise and respectful of time?

    === OUTPUT REQUIREMENTS ===
    - Set is_complete=True ONLY if ALL criteria pass
    - Provide specific, actionable feedback (not vague suggestions)
    - Use issue_flags to indicate which criteria failed
    """

    # Input fields
    content: str = dspy.InputField(description="Content to evaluate")
    context: str = dspy.InputField(description="Lead and campaign context")
    history: dspy.History = dspy.InputField(description="Previous evaluation exchanges")

    # Output fields
    is_complete: bool = dspy.OutputField(
        description="True if content meets ALL criteria, False otherwise"
    )
    feedback: str = dspy.OutputField(
        description="Specific, actionable feedback for improvement"
    )
    issue_flags: str = dspy.OutputField(
        description="Comma-separated list of failing criteria"
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
    global _shared_lm
    if _shared_lm is None:
        _shared_lm = dspy.LM(
            os.getenv("MODEL_NAME", "gemini/gemini-2.5-flash"),
            api_key=os.getenv("GOOGLE_API_KEY"),
            max_parallel_requests=2000,
        )
    return _shared_lm


# ============================================
# CONVERSATIONAL AGENT MODULE
# ============================================
class CriticAgent(dspy.Module):
    """
    Conversational agent that maintains evaluation history.

    Uses dspy.History to track previous feedback exchanges.
    """

    def __init__(self, shared_lm):
        if shared_lm is None:
            raise ValueError(
                "CriticAgent requires a shared_lm instance. "
                "Pass get_shared_lm() to enable connection pooling."
            )

        self.lm = shared_lm

        # Create predictor (Predict, not ChainOfThought - evaluation is a checklist)
        self.critic = dspy.Predict(CriticSignature)

        # CRITICAL: Inject singleton LM
        self.critic.set_lm(self.lm)

    def forward(
        self,
        content: str,
        context: str,
        history: dspy.History
    ) -> dspy.Prediction:
        """
        Evaluate content with conversation history.

        Args:
            content: Content to evaluate
            context: Lead and campaign context
            history: Previous evaluation exchanges

        Returns:
            dspy.Prediction with is_complete, feedback, issue_flags
        """
        result = self.critic(
            content=content,
            context=context,
            history=history
        )

        return result

    async def aforward(
        self,
        content: str,
        context: str,
        history: dspy.History
    ) -> dspy.Prediction:
        """Async version for concurrent workflows."""
        result = await self.critic.acall(
            content=content,
            context=context,
            history=history
        )

        return result


# ============================================
# HISTORY MANAGEMENT UTILITIES
# ============================================
def create_history() -> dspy.History:
    """Create a fresh history object."""
    return dspy.History(messages=[])


def add_user_message(history: dspy.History, content: str) -> None:
    """Add a user message to history."""
    history.messages.append({
        "role": "user",
        "content": content
    })


def add_assistant_message(history: dspy.History, content: str) -> None:
    """Add an assistant message to history."""
    history.messages.append({
        "role": "assistant",
        "content": content
    })


def format_feedback_for_history(result) -> str:
    """Format critic result for history storage."""
    return (
        f"Evaluation: {'COMPLETE' if result.is_complete else 'NEEDS WORK'}\n"
        f"Issues: {result.issue_flags}\n"
        f"Feedback: {result.feedback}"
    )
```

### Creator-Critic Loop with Separate Histories

```python
class CreatorCriticLoop(dspy.Module):
    """
    Iterative refinement loop with separate history per agent role.

    CRITICAL: Use separate dspy.History objects for each agent to prevent
    cross-contamination of conversation context.
    """

    def __init__(self, shared_lm):
        if shared_lm is None:
            raise ValueError("shared_lm required")

        self.lm = shared_lm

        # Creator uses ChainOfThought (creative task)
        self.creator = dspy.ChainOfThought(CreatorSignature)

        # Critic and Iterator use Predict (evaluation tasks)
        self.critic = dspy.Predict(CriticSignature)
        self.iterator = dspy.Predict(IteratorSignature)

        # Inject LM into all predictors
        self.creator.set_lm(self.lm)
        self.critic.set_lm(self.lm)
        self.iterator.set_lm(self.lm)

    async def aforward(
        self,
        company_analysis: str,
        persona_analysis: str,
        campaign_context: str,
        max_iterations: int = 3
    ) -> dspy.Prediction:
        """
        Run creator-critic loop with history tracking.
        """
        # ============================================
        # CRITICAL: Separate histories per agent role
        # ============================================
        critic_history = dspy.History(messages=[])
        iterator_history = dspy.History(messages=[])

        # Initial creation (no history needed - first turn)
        creation_result = await self.creator.acall(
            company_analysis=company_analysis,
            persona_analysis=persona_analysis,
            campaign_context=campaign_context
        )

        current_content = self._extract_content(creation_result)
        creation_reasoning = creation_result.reasoning

        # Add initial content to histories
        add_user_message(
            critic_history,
            f"Please evaluate this content:\n{self._format_content(current_content)}"
        )
        add_user_message(
            iterator_history,
            f"Initial content to improve:\n{self._format_content(current_content)}"
        )

        attempts = 0
        while attempts < max_iterations:
            # ============================================
            # CRITIC EVALUATION (with history)
            # ============================================
            critic_result = await self.critic.acall(
                content=self._format_content(current_content),
                context=f"{company_analysis}\n\n{persona_analysis}",
                history=critic_history
            )

            # Add critic's response to its history
            add_assistant_message(
                critic_history,
                format_feedback_for_history(critic_result)
            )

            if critic_result.is_complete:
                break

            # ============================================
            # ITERATION (with history)
            # ============================================

            # Add feedback to iterator's history
            add_user_message(
                iterator_history,
                f"Feedback to address:\n{critic_result.feedback}\nIssues: {critic_result.issue_flags}"
            )

            iteration_result = await self.iterator.acall(
                current_content=self._format_content(current_content),
                feedback=critic_result.feedback,
                issue_flags=critic_result.issue_flags,
                history=iterator_history
            )

            # Add iterator's response to its history
            add_assistant_message(
                iterator_history,
                f"Improved content:\n{self._format_content(self._extract_iteration(iteration_result))}"
            )

            # Update content for next iteration
            current_content = self._extract_iteration(iteration_result)

            # Update critic history with new content for next evaluation
            add_user_message(
                critic_history,
                f"Revised content to evaluate:\n{self._format_content(current_content)}"
            )

            attempts += 1

        return dspy.Prediction(
            content=current_content,
            creation_reasoning=creation_reasoning,
            iterations=attempts,
            final_feedback=critic_result.feedback if attempts > 0 else "Accepted on first try"
        )

    def _extract_content(self, result) -> dict:
        """Extract content fields from creation result."""
        return {
            "subject_line": result.subject_line,
            "opening_hook": result.opening_hook,
            "value_proposition": result.value_proposition,
            "call_to_action": result.call_to_action
        }

    def _extract_iteration(self, result) -> dict:
        """Extract content fields from iteration result."""
        return {
            "subject_line": result.improved_subject,
            "opening_hook": result.improved_hook,
            "value_proposition": result.improved_value_prop,
            "call_to_action": result.improved_cta
        }

    def _format_content(self, content: dict) -> str:
        """Format content dict as readable string."""
        return (
            f"Subject: {content['subject_line']}\n"
            f"Opening: {content['opening_hook']}\n"
            f"Value Prop: {content['value_proposition']}\n"
            f"CTA: {content['call_to_action']}"
        )
```

### History Windowing for Long Conversations

```python
def window_history(history: dspy.History, max_messages: int = 10) -> dspy.History:
    """
    Keep only the most recent messages to prevent context overflow.

    Args:
        history: Full history object
        max_messages: Maximum messages to keep

    Returns:
        New history with only recent messages
    """
    if len(history.messages) <= max_messages:
        return history

    # Keep most recent messages
    windowed = dspy.History(
        messages=history.messages[-max_messages:]
    )

    return windowed


def summarize_history(history: dspy.History, summarizer) -> dspy.History:
    """
    Replace old messages with a summary to preserve context efficiently.

    Args:
        history: Full history object
        summarizer: DSPy module that summarizes conversations

    Returns:
        New history with summary + recent messages
    """
    if len(history.messages) <= 6:
        return history

    # Split into old and recent
    old_messages = history.messages[:-4]
    recent_messages = history.messages[-4:]

    # Summarize old messages
    old_text = "\n".join([
        f"{m['role']}: {m['content']}"
        for m in old_messages
    ])

    summary_result = summarizer(conversation=old_text)

    # Create new history with summary + recent
    return dspy.History(messages=[
        {"role": "system", "content": f"Summary of earlier conversation:\n{summary_result.summary}"},
        *recent_messages
    ])
```

### DSPy-Specific Notes

- **Separate histories:** Always use separate `dspy.History` objects for different agent roles in the same workflow.
- **History is an InputField:** Declare it as `history: dspy.History = dspy.InputField()` in your Signature.
- **Message format:** Use `{"role": "user"|"assistant", "content": "..."}` structure.
- **History accumulates:** Remember to add responses to history after each call.
- **Context limits:** Long histories can exceed context windows. Use windowing or summarization.

---

## Pitfalls & Best Practices

**Pitfalls:**

- **Shared history across agents** — Different agents have different roles. Sharing history causes confusion. Use separate history objects.

- **Forgetting to update history** — After each call, add the response to history. Missing updates break the conversation chain.

- **Unbounded history growth** — Long loops can accumulate too much context. Implement windowing or summarization.

- **Wrong message roles** — Using incorrect roles (`user` vs `assistant`) confuses the model about who said what.

- **Storing raw objects** — Convert predictions to strings before adding to history. Raw objects don't serialize well.

**Best Practices:**

- **One history per role** — In a creator-critic loop, the critic has its history, the iterator has its own.

- **Format for clarity** — Structure history messages with clear labels and formatting.

- **Window or summarize** — For loops that might run many iterations, implement history management.

- **Add context to history** — Include relevant context (not just responses) so agents can reference prior state.

- **Use utility functions** — Create helper functions for history operations to ensure consistency.

---

## Comparison: When to Use History

| Scenario | Use History? | Why |
|----------|--------------|-----|
| Single extraction | No | No prior context needed |
| Creator-Critic loop | Yes | Critic needs to track addressed feedback |
| Pipeline stages | No | Each stage is independent |
| Dialogue system | Yes | Must remember conversation |
| Retry after failure | Maybe | Might help model understand what went wrong |

### History vs Passing Previous Output

| Approach | When to Use |
|----------|-------------|
| **dspy.History** | Multi-turn dialogue, iterative refinement, feedback loops |
| **Pass previous output as input** | Pipeline stages, one-way data flow |
| **Both** | Complex workflows where agents both receive data AND need conversation context |

---

## Source Reference

**Validated against:** `ns-cold-outreach-workforce/src/workflows/message_creation/create_message.py`

Patterns demonstrated:
- Separate history objects for critic and iterator (lines 202-210)
- History accumulation in loop (lines 250-280)
- Message formatting for history (lines 300-320)
