# Tool Usage Modifier

## Purpose

Configures agents to call external tools/functions. Tool-using agents can take actions, retrieve data, or interact with external systems.

---

## When to Add Tools

| Scenario | Add Tools? |
|----------|------------|
| Agent needs external data (API, database) | Yes |
| Agent takes actions (send email, update record) | Yes |
| Agent needs current information (time, weather) | Yes |
| Agent only processes provided input | No |
| Agent only generates content | Usually no |

---

## Prompt Adjustments

### In `<capabilities>` Section

Document each tool with:
- What it does
- When to use it
- Parameters
- Expected response
- Error handling

```xml
<capabilities>
1. **Answer product questions** — From your knowledge

2. **Look up order status** — For real-time order information
   - Tool: `get_order_status(order_id: str)`
   - Use when: Customer asks about their order
   - Returns: Order status, shipping info, estimated delivery
   - Errors: Returns "Order not found" for invalid IDs

3. **Update customer preferences** — Change notification settings
   - Tool: `update_preferences(customer_id: str, preferences: dict)`
   - Use when: Customer wants to change settings
   - Always confirm before calling
   - Returns: Confirmation of updated settings

4. **Escalate to human** — Transfer conversation
   - Tool: `escalate_to_agent(reason: str, context: str)`
   - Use when: Issue exceeds your capabilities or customer requests
   - Include full conversation context
</capabilities>
```

### In `<operational_logic>` Section

Define when and how to use tools:

```xml
<operational_logic>
**Tool usage rules:**
- Always check if you can answer from knowledge before using a tool
- For order lookups, ask for order ID if not provided
- For preference updates, confirm the change with the customer first
- If a tool fails, apologize and try an alternative approach
- Never call escalate_to_agent without telling the customer

**Tool decision flow:**
IF customer asks about their specific order → get_order_status
IF customer asks general order policy questions → answer from knowledge
IF customer wants to change settings → confirm first → update_preferences
IF frustrated OR requests human OR beyond capabilities → escalate_to_agent
</operational_logic>
```

### In `<important_notes>` or `<constraints_and_safeguards>`

Add tool-specific rules:

```xml
<important_notes>
- Never call update_preferences without explicit customer confirmation
- Limit get_order_status to 3 retries if order ID seems wrong
- Always include conversation summary when escalating
- If tools are unavailable/failing, inform customer and offer alternatives
</important_notes>
```

---

## Tool Documentation Patterns

### Minimal (Simple Tools)

```xml
- Tool: `get_time()` — Returns current UTC time
```

### Standard (Most Tools)

```xml
- Tool: `search_products(query: str, limit: int = 10)`
  - Use when: Customer looking for products
  - Returns: List of matching products with names, prices, availability
```

### Comprehensive (Complex/Risky Tools)

```xml
- Tool: `process_refund(order_id: str, amount: float, reason: str)`
  - Use when: Customer requests refund for valid order
  - Parameters:
    - order_id: The order to refund (required)
    - amount: Refund amount in USD (required, must be ≤ order total)
    - reason: Why the refund is being issued (required)
  - Returns: Confirmation with refund ID and processing time
  - Constraints:
    - Maximum refund: $500 (escalate larger amounts)
    - Order must be within 30-day refund window
    - Requires customer confirmation before execution
  - Errors:
    - "Invalid order" — Order ID not found
    - "Refund window expired" — Order too old
    - "Amount exceeds limit" — Reduce amount or escalate
```

---

## Tool Safety Patterns

### Confirmation Before Action

For tools that make changes:

```xml
<operational_logic>
For any tool that modifies data:
1. Explain what you're about to do
2. Ask for explicit confirmation ("Should I proceed?")
3. Only call the tool after receiving "yes" or equivalent
4. Confirm the action was completed
</operational_logic>
```

### Retry and Fallback

```xml
<operational_logic>
If a tool call fails:
1. First failure: Retry once
2. Second failure: Apologize and explain the issue
3. Offer alternatives:
   - For lookups: Ask customer to try again later
   - For actions: Offer to create a support ticket instead
</operational_logic>
```

### Rate Limiting

```xml
<important_notes>
- Maximum 5 tool calls per conversation turn
- If you need more lookups, ask customer to narrow their request
- Batch lookups when possible (use get_orders plural, not multiple get_order)
</important_notes>
```

---

## Framework Implementation

### LangGraph with Tools

```python
from langchain_core.tools import tool

@tool
def get_order_status(order_id: str) -> str:
    """Look up the status of a customer order."""
    # Implementation
    return status

# Bind tools to model
llm_with_tools = self.llm.bind_tools([get_order_status, update_preferences])
```

### DSPy with Tools (ReAct)

```python
import dspy

class CustomerSupport(dspy.Module):
    def __init__(self):
        self.react = dspy.ReAct(
            signature=SupportSignature,
            tools=[get_order_status, update_preferences]
        )
```

---

## Common Pitfalls

1. **Undocumented tools** — Every tool needs clear documentation in the prompt.

2. **Missing confirmation** — Destructive actions need user confirmation.

3. **No error handling** — Define what happens when tools fail.

4. **Tool overuse** — Agents should try to answer from knowledge first.

5. **Unclear parameters** — Be explicit about required vs optional params.

6. **No fallback** — Always have a path when tools are unavailable.

---

## Decision Guide

```
Does the agent need external data or actions?
├── No → Don't add tools
└── Yes
    ├── Data retrieval only?
    │   └── Add lookup tools, no confirmation needed
    └── Takes actions/makes changes?
        └── Add action tools WITH confirmation requirements
```
