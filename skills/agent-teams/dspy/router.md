# Router Pattern

## What It Is

A conditional dispatch pattern where a router agent analyzes input and routes to the appropriate specialized handler. In DSPy, this is implemented using a classifier predictor followed by Python conditionals to invoke the appropriate downstream agent.

## When to Use

- Different input types require different processing
- Specialized handlers for distinct categories
- Classification determines workflow path
- Avoiding "jack of all trades" agents
- Task delegation based on content analysis

## When to Avoid

- All inputs should go through the same pipeline → use **Pipeline** instead
- Multiple perspectives needed on same input → use **Fan-in/Fan-out** instead
- Iterative refinement needed → use **Loop** instead
- Single agent can handle all cases → use **Individual Agent** instead

## Pattern Structure

```
                    ┌─── Handler A ───┐
                    │                 │
START ─── Router ───┼─── Handler B ───┼──── END
                    │                 │
                    └─── Handler C ───┘
```

Key insight: Router CLASSIFIES the input, then Python conditionals DISPATCH to the appropriate handler. Only ONE handler executes per request.

---

## DSPy Implementation

### Code Template

```python
import os
import asyncio
import dspy
from typing import Union, Literal


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
            timeout=120,  # REQUIRED: prevents indefinite hangs
        )
    return _shared_lm


# =============================================================================
# ROUTER SIGNATURE
# =============================================================================
# STRUCTURED OUTPUT RULE: Use typed output fields (bool, int, list[str],
# dict[str, Any]) or Pydantic BaseModel/RootModel as OutputField types.
# NEVER use str fields with JSON parsing instructions.
# See frameworks/dspy/CHEATSHEET.md Critical Rules.

class RouterSignature(dspy.Signature):
    """
    Classify input and determine the appropriate handler.

    === ROUTING LOGIC ===
    Analyze the input and classify it into EXACTLY ONE category:

    - "technical": Technical questions, code issues, implementation details
    - "business": Business strategy, pricing, partnerships, go-to-market
    - "support": Customer issues, bugs, complaints, troubleshooting
    - "general": Everything else that doesn't fit above categories

    === REQUIREMENTS ===
    - Output EXACTLY one of the four categories above
    - Be decisive - pick the BEST match, not a hedge
    - Consider the PRIMARY intent, not secondary aspects
    """
    input_text: str = dspy.InputField(description="The input to classify")
    context: str = dspy.InputField(description="Optional context")

    # Small enum (4 values) - strict Literal is fine with good prompting
    category: Literal["technical", "business", "support", "general"] = dspy.OutputField(
        description="EXACTLY one of: technical, business, support, general"
    )
    confidence: int = dspy.OutputField(description="Confidence 0-100")
    reasoning: str = dspy.OutputField(description="Brief explanation for the classification")


# =============================================================================
# HANDLER SIGNATURES (Specialized Agents)
# =============================================================================

class TechnicalHandlerSignature(dspy.Signature):
    """
    Handle technical questions and implementation issues.

    You are a TECHNICAL SPECIALIST. Focus on:
    - Code solutions
    - Architecture recommendations
    - Technical troubleshooting
    - Implementation details
    """
    input_text: str = dspy.InputField()
    context: str = dspy.InputField()

    response: str = dspy.OutputField(description="Technical response with code if applicable")
    follow_up_needed: bool = dspy.OutputField(description="True if more info needed")


class BusinessHandlerSignature(dspy.Signature):
    """
    Handle business strategy and commercial questions.

    You are a BUSINESS SPECIALIST. Focus on:
    - Strategic recommendations
    - Pricing guidance
    - Partnership considerations
    - Market analysis
    """
    input_text: str = dspy.InputField()
    context: str = dspy.InputField()

    response: str = dspy.OutputField(description="Business-focused response")
    action_items: str = dspy.OutputField(description="Recommended next steps")


class SupportHandlerSignature(dspy.Signature):
    """
    Handle customer support and troubleshooting.

    You are a SUPPORT SPECIALIST. Focus on:
    - Empathetic responses
    - Clear troubleshooting steps
    - Issue resolution
    - Escalation when needed
    """
    input_text: str = dspy.InputField()
    context: str = dspy.InputField()

    response: str = dspy.OutputField(description="Empathetic support response")
    resolution_steps: str = dspy.OutputField(description="Step-by-step resolution")
    escalate: bool = dspy.OutputField(description="True if needs human escalation")


class GeneralHandlerSignature(dspy.Signature):
    """
    Handle general inquiries that don't fit specialized categories.

    You are a GENERALIST. Provide helpful, balanced responses
    for miscellaneous questions.
    """
    input_text: str = dspy.InputField()
    context: str = dspy.InputField()

    response: str = dspy.OutputField(description="Helpful general response")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

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
                print(f"⚠ {agent_name} retry {attempt + 1}, waiting {wait_time}s")
                await asyncio.sleep(wait_time)
            else:
                raise


def validate_category(category: str) -> str:
    """
    Validate category is one of the expected values.

    NOTE: For small enums (3-10 values) like this router, normalization
    should NOT be needed if prompting is good. This function is defensive
    only - if you're hitting the fallback often, improve your signature
    docstring instead of relying on normalization.
    """
    valid = ["technical", "business", "support", "general"]
    category_lower = category.lower().strip()

    if category_lower in valid:
        return category_lower

    # Defensive fallback - should rarely be needed with good prompting
    print(f"⚠ Unexpected category '{category}', defaulting to 'general'")
    return "general"


# =============================================================================
# ROUTER MODULE
# =============================================================================

class RouterModule(dspy.Module):
    """
    Conditional routing to specialized handlers.

    Router classifies input, then dispatches to appropriate handler.
    """

    def __init__(self, shared_lm):
        """
        Initialize router with all handlers.

        Args:
            shared_lm: Singleton LM instance (REQUIRED)
        """
        if shared_lm is None:
            raise ValueError("RouterModule requires a shared_lm instance.")

        self.lm = shared_lm

        # Router uses Predict (classification task)
        self.router = dspy.Predict(RouterSignature)

        # Handlers - each specialized for their domain
        self.technical_handler = dspy.Predict(TechnicalHandlerSignature)
        self.business_handler = dspy.Predict(BusinessHandlerSignature)
        self.support_handler = dspy.Predict(SupportHandlerSignature)
        self.general_handler = dspy.Predict(GeneralHandlerSignature)

        # Inject singleton LM into ALL
        self.router.set_lm(self.lm)
        self.technical_handler.set_lm(self.lm)
        self.business_handler.set_lm(self.lm)
        self.support_handler.set_lm(self.lm)
        self.general_handler.set_lm(self.lm)

    def forward(self, input_text: str, context: str = "", **kwargs):
        """
        Synchronous execution for optimization/testing.
        """
        # Step 1: Classify
        routing = self.router(
            input_text=input_text,
            context=context,
            **kwargs
        )

        category = validate_category(routing.category)

        # Step 2: Dispatch to appropriate handler
        if category == "technical":
            handler_result = self.technical_handler(
                input_text=input_text,
                context=context,
                **kwargs
            )
        elif category == "business":
            handler_result = self.business_handler(
                input_text=input_text,
                context=context,
                **kwargs
            )
        elif category == "support":
            handler_result = self.support_handler(
                input_text=input_text,
                context=context,
                **kwargs
            )
        else:
            handler_result = self.general_handler(
                input_text=input_text,
                context=context,
                **kwargs
            )

        return dspy.Prediction(
            routing=routing,
            category=category,
            confidence=routing.confidence,
            handler_result=handler_result,
        )

    async def aforward(self, input_text: str, context: str = "", **kwargs):
        """
        Async production execution with routing and dispatch.
        """
        import time
        timings = {}

        # Step 1: Classify
        start = time.time()
        routing = await call_with_retry(
            self.router,
            agent_name="router",
            input_text=input_text,
            context=context,
            **kwargs
        )
        category = validate_category(routing.category)
        timings['routing'] = time.time() - start

        # Step 2: Dispatch to appropriate handler
        start = time.time()

        if category == "technical":
            handler_result = await call_with_retry(
                self.technical_handler,
                agent_name="technical_handler",
                input_text=input_text,
                context=context,
                **kwargs
            )
        elif category == "business":
            handler_result = await call_with_retry(
                self.business_handler,
                agent_name="business_handler",
                input_text=input_text,
                context=context,
                **kwargs
            )
        elif category == "support":
            handler_result = await call_with_retry(
                self.support_handler,
                agent_name="support_handler",
                input_text=input_text,
                context=context,
                **kwargs
            )
        else:
            handler_result = await call_with_retry(
                self.general_handler,
                agent_name="general_handler",
                input_text=input_text,
                context=context,
                **kwargs
            )

        timings['handler'] = time.time() - start
        timings['total'] = timings['routing'] + timings['handler']

        return dspy.Prediction(
            routing=routing,
            category=category,
            confidence=routing.confidence,
            handler_result=handler_result,
            timings=timings,
        )


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

async def main():
    shared_lm = get_shared_lm()
    module = RouterModule(shared_lm=shared_lm)

    # Technical query
    result1 = await module.aforward(
        input_text="How do I implement retry logic with exponential backoff in Python?",
        context="Building a production API client"
    )
    print(f"Category: {result1.category} (confidence: {result1.confidence})")
    print(f"Response: {result1.handler_result.response[:200]}...")

    # Business query
    result2 = await module.aforward(
        input_text="Should we offer annual pricing discounts?",
        context="B2B SaaS pricing strategy"
    )
    print(f"Category: {result2.category} (confidence: {result2.confidence})")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## DSPy-Specific Notes

> **Structured Output Rule:** When defining signatures for router and handler agents, use typed DSPy output fields (`bool`, `int`, `list[str]`, `dict[str, Any]`) or Pydantic `BaseModel`/`RootModel` as OutputField types. NEVER use `str` fields with JSON parsing instructions. See `frameworks/dspy/CHEATSHEET.md` Critical Rules.

- **Router uses Predict:** Classification is a straightforward mapping task that doesn't benefit from ChainOfThought reasoning.

- **Python conditionals for dispatch:** After classification, use standard `if/elif/else` to invoke the appropriate handler. DSPy doesn't have a built-in routing construct.

- **Category normalization:** LLMs may output variations of category names. Always normalize with fuzzy matching before dispatching.

- **All handlers share singleton LM:** Even though only one handler runs per request, all must be initialized with `set_lm()` for the singleton pattern.

---

## Key Patterns

### 1. Classification + Dispatch

```python
# Step 1: Classify
routing = await self.router.acall(input_text=input_text)
category = validate_category(routing.category)

# Step 2: Dispatch with Python conditionals
if category == "technical":
    result = await self.technical_handler.acall(...)
elif category == "business":
    result = await self.business_handler.acall(...)
# ...
```

### 2. Category Validation (Defensive Only)

```python
def validate_category(category: str) -> str:
    """
    Validate category - should rarely need the fallback with good prompting.

    NOTE: For small enums (3-10 values), fuzzy matching/normalization is
    NOT recommended. If you're hitting fallbacks often, improve your
    signature docstring instead.
    """
    valid = ["technical", "business", "support", "general"]

    if category.lower() in valid:
        return category.lower()

    # Defensive fallback only
    print(f"⚠ Unexpected category '{category}', defaulting to 'general'")
    return "general"
```

### 3. Confidence-Based Fallback

```python
# Low confidence → use general handler
if routing.confidence < 50:
    category = "general"
```

### 4. Handler Registry Pattern

```python
# Alternative: Use a dict for cleaner dispatch
self.handlers = {
    "technical": self.technical_handler,
    "business": self.business_handler,
    "support": self.support_handler,
    "general": self.general_handler,
}

# Dispatch
handler = self.handlers.get(category, self.general_handler)
result = await handler.acall(...)
```

---

## Variants

### Multi-Level Router

When categories have sub-categories:

```python
async def aforward(self, input_text: str, **kwargs):
    # Level 1: High-level category
    level1 = await self.router_level1.acall(input_text=input_text)

    if level1.category == "technical":
        # Level 2: Technical sub-category
        level2 = await self.router_level2_tech.acall(input_text=input_text)

        if level2.sub_category == "frontend":
            return await self.frontend_handler.acall(...)
        elif level2.sub_category == "backend":
            return await self.backend_handler.acall(...)
        # ...
```

### Router with Fallthrough

When multiple handlers might apply:

```python
async def aforward(self, input_text: str, **kwargs):
    routing = await self.router.acall(input_text=input_text)

    # Primary handler
    primary_result = await self.handlers[routing.primary].acall(...)

    # If primary suggests escalation, try secondary
    if hasattr(primary_result, 'escalate') and primary_result.escalate:
        secondary_result = await self.handlers[routing.secondary].acall(...)
        return dspy.Prediction(
            primary=primary_result,
            secondary=secondary_result,
            escalated=True
        )

    return dspy.Prediction(primary=primary_result, escalated=False)
```

### Router with Pre-Processing

When input needs preparation before routing:

```python
async def aforward(self, raw_input: str, **kwargs):
    # Pre-process: Extract key signals for routing
    preprocessed = await self.preprocessor.acall(raw_input=raw_input)

    # Route based on extracted signals
    routing = await self.router.acall(
        input_text=raw_input,
        extracted_intent=preprocessed.intent,
        extracted_entities=preprocessed.entities,
    )

    # Dispatch with enriched context
    handler = self.handlers[routing.category]
    return await handler.acall(
        input_text=raw_input,
        intent=preprocessed.intent,
        entities=preprocessed.entities,
    )
```

---

## Pitfalls & Best Practices

**Pitfalls:**

- **Over-reliance on normalization** — For small enums (3-10 values), fix your prompting instead of adding fuzzy matching. Normalization is a last resort for large enums (20+ values).

- **Missing default handler** — If category doesn't match any handler, the code fails. Always have a fallback.

- **Over-complex routing** — If you need more than 5-6 categories, consider a two-level router.

- **Routing without confidence** — Low-confidence classifications should go to a general handler.

**Best Practices:**

- **Keep router signature simple** — Router should ONLY classify, not process.

- **Specialized handlers are better** — A focused handler outperforms a generic "do everything" agent.

- **Include reasoning in router** — Having the router explain its choice helps debugging.

- **Log routing decisions** — Track category distribution to identify gaps.

- **Use handler registry for cleaner code:**
  ```python
  handlers = {"a": handler_a, "b": handler_b}
  result = await handlers[category].acall(...)
  ```

---

## Comparison with Other Patterns

| Aspect | Router | Pipeline | Fan-in/Fan-out | Loop |
|--------|--------|----------|----------------|------|
| Flow | Conditional branch | Sequential | Parallel | Cyclical |
| Execution | ONE handler per request | ALL stages | ALL agents | Until condition met |
| Use case | Specialized handling | Transformation | Multi-perspective | Refinement |
| Decision point | Before processing | None | None | After each iteration |
