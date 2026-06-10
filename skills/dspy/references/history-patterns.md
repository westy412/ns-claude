# History Patterns

Using `dspy.History` for multi-turn conversations and iterative loops.

## When to Use History

| Scenario | Use History? |
|----------|--------------|
| Single extraction | No |
| Pipeline stages | No (pass data as input) |
| Creator-Critic loop | Yes |
| Dialogue system | Yes |
| Feedback incorporation | Yes |

## Basic Usage

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

## Key Pattern: Separate Histories Per Agent

In multi-agent loops, **each agent role gets its own history**:

```python
class CreatorCriticLoop(dspy.Module):
    async def aforward(self, **inputs):
        # CRITICAL: Separate histories per agent role
        critic_history = dspy.History(messages=[])
        iterator_history = dspy.History(messages=[])

        # Initial creation (no history needed)
        creation_result = await self.creator.acall(**inputs)
        current_content = self._format_content(creation_result)

        # Add initial content to histories
        critic_history.messages.append({
            "role": "user",
            "content": f"Please evaluate this content:\n{current_content}"
        })

        attempts = 0
        while attempts < 3:
            # Critic evaluation (with its own history)
            critic_result = await self.critic.acall(
                content=current_content,
                history=critic_history
            )

            # Add critic's response to its history
            critic_history.messages.append({
                "role": "assistant",
                "content": f"Evaluation: {critic_result.feedback}"
            })

            if critic_result.is_complete:
                break

            # Iterator uses its own history
            iterator_history.messages.append({
                "role": "user",
                "content": f"Feedback to address:\n{critic_result.feedback}"
            })

            iteration_result = await self.iterator.acall(
                current_content=current_content,
                feedback=critic_result.feedback,
                history=iterator_history
            )

            iterator_history.messages.append({
                "role": "assistant",
                "content": f"Improved content:\n{iteration_result.improved}"
            })

            current_content = iteration_result.improved
            attempts += 1

        return current_content
```

## Message Format

```python
# Standard format
history.messages.append({
    "role": "user",      # or "assistant" or "system"
    "content": "Message content here"
})
```

## Utility Functions

```python
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

## History Windowing

For long conversations, prevent context overflow:

```python
def window_history(history: dspy.History, max_messages: int = 10) -> dspy.History:
    """
    Keep only the most recent messages.
    """
    if len(history.messages) <= max_messages:
        return history

    return dspy.History(
        messages=history.messages[-max_messages:]
    )
```

## History Summarization

Replace old messages with a summary:

```python
async def summarize_history(
    history: dspy.History,
    summarizer,
    keep_recent: int = 4
) -> dspy.History:
    """
    Replace old messages with a summary.
    """
    if len(history.messages) <= keep_recent + 2:
        return history

    old_messages = history.messages[:-keep_recent]
    recent_messages = history.messages[-keep_recent:]

    # Summarize old messages
    old_text = "\n".join([
        f"{m['role']}: {m['content']}"
        for m in old_messages
    ])

    summary_result = await summarizer.acall(conversation=old_text)

    return dspy.History(messages=[
        {"role": "system", "content": f"Summary:\n{summary_result.summary}"},
        *recent_messages
    ])
```

## Two Patterns: Agent-to-Agent vs User-to-Agent

### Agent-to-Agent (Internal Workflows)

```python
# "user" and "assistant" represent different agents, not humans
critic_history.messages.append({
    "role": "user",  # This is the content being evaluated
    "content": f"Evaluate this:\n{content}"
})

critic_history.messages.append({
    "role": "assistant",  # This is the critic's response
    "content": f"Feedback: {feedback}"
})
```

### User-to-Agent (Chatbot)

```python
class Chatbot(dspy.Module):
    def __init__(self, shared_lm):
        self.responder = dspy.Predict(ChatbotSignature)
        self.responder.set_lm(shared_lm)
        self.history = dspy.History(messages=[])

    def chat(self, user_message: str) -> str:
        # Add user message
        self.history.messages.append({
            "role": "user",
            "content": user_message
        })

        # Get response
        result = self.responder(
            user_message=user_message,
            history=self.history
        )

        # Add assistant response
        self.history.messages.append({
            "role": "assistant",
            "content": result.response
        })

        return result.response
```

## Anti-Patterns

```python
# WRONG: Shared history across agents
shared_history = dspy.History(messages=[])
critic_result = await self.critic.acall(history=shared_history)
iterator_result = await self.iterator.acall(history=shared_history)  # Contaminated!

# WRONG: Forgetting to update history
result = await self.critic.acall(history=history)
# Missing: history.messages.append(...)

# WRONG: Storing raw objects
history.messages.append({
    "role": "assistant",
    "content": result  # Should be string, not Prediction object
})

# WRONG: Wrong roles
history.messages.append({
    "role": "user",  # Should be "assistant" for agent responses
    "content": agent_response
})
```

## Checklist

- [ ] Separate history per agent role
- [ ] Update history after each call
- [ ] Use string content (not raw objects)
- [ ] Correct roles ("user" vs "assistant")
- [ ] Window or summarize long histories
- [ ] History declared as `dspy.History = dspy.InputField()`
