# Inngest: Improving Existing Workflows

Patterns for enhancing, extending, and optimizing Inngest workflows with advanced coordination, cancellation, and parallel processing.

---

## 1. Wait for Events (`wait_for_event`)

Pause a workflow until an external event arrives. Essential for user interactions, webhook responses, and workflow coordination.

### Basic Wait Pattern

```python
@inngest_client.create_function(
    fn_id="leads/await-reply",
    trigger=inngest.TriggerEvent(event="workflow/await-reply")
)
async def await_reply_workflow(ctx: inngest.Context):
    lead_id = ctx.event.data["lead_id"]

    # Wait for reply event (max 7 days)
    reply_event = await ctx.step.wait_for_event(
        "wait-for-reply",
        event="api/reply-received",
        if_exp=f"async.data.lead_id == '{lead_id}'",
        timeout="7d"
    )

    if reply_event is None:
        # Timeout - no reply received
        await ctx.step.run(
            "handle-no-reply",
            handle_no_response,
            lead_id
        )
    else:
        # Reply received - process it
        await ctx.step.run(
            "process-reply",
            process_lead_reply,
            lead_id,
            reply_event.data
        )
```

### Understanding `if_exp` Syntax

The `if_exp` parameter filters which events satisfy the wait condition.

**Two contexts available:**
- `event` - The original triggering event (started the workflow)
- `async` - The incoming event being evaluated (the one you're waiting for)

```python
# Match on the waiting event's data
if_exp="async.data.lead_id == 'lead-123'"

# Match triggering event against waiting event
if_exp=f"async.data.lead_id == '{ctx.event.data['lead_id']}'"

# Match using the event's own data
if_exp="async.data.order_id == event.data.order_id"

# Complex conditions
if_exp="async.data.status == 'approved' && async.data.amount > 1000"
```

### Dual Event Pattern (Trigger + Wait)

Use this pattern when you need separate events to start a workflow and complete a step:

```python
@inngest_client.create_function(
    fn_id="orders/approval-flow",
    trigger=inngest.TriggerEvent(event="order/needs-approval")
)
async def approval_workflow(ctx: inngest.Context):
    order_id = ctx.event.data["order_id"]

    # Notify approvers
    await ctx.step.run(
        "notify-approvers",
        send_approval_request,
        order_id
    )

    # Wait for approval decision
    decision = await ctx.step.wait_for_event(
        "wait-for-decision",
        event="order/approval-decision",
        if_exp=f"async.data.order_id == '{order_id}'",
        timeout="48h"
    )

    if decision is None:
        await ctx.step.run("escalate", escalate_approval, order_id)
    elif decision.data.get("approved"):
        await ctx.step.run("process-approved", fulfill_order, order_id)
    else:
        await ctx.step.run("process-rejected", reject_order, order_id, decision.data.get("reason"))
```

**Triggering the wait event:**

```python
# Called from an API endpoint when approver makes decision
@router.post("/orders/{order_id}/approve")
async def approve_order(order_id: str, approved: bool, reason: str = None):
    await inngest_client.send(
        inngest.Event(
            name="order/approval-decision",
            data={
                "order_id": order_id,
                "approved": approved,
                "reason": reason
            }
        )
    )
    return {"status": "decision_recorded"}
```

### Multiple Wait Branches (Race Condition)

Wait for any of multiple events:

```python
@inngest_client.create_function(
    fn_id="leads/multi-channel-response",
    trigger=inngest.TriggerEvent(event="workflow/await-response")
)
async def await_multi_channel(ctx: inngest.Context):
    lead_id = ctx.event.data["lead_id"]

    # Wait for email reply
    email_reply = await ctx.step.wait_for_event(
        "wait-email",
        event="api/email-reply",
        if_exp=f"async.data.lead_id == '{lead_id}'",
        timeout="24h"
    )

    if email_reply:
        return await ctx.step.run(
            "process-email",
            process_email_reply,
            lead_id,
            email_reply.data
        )

    # No email - check for phone response
    phone_response = await ctx.step.wait_for_event(
        "wait-phone",
        event="api/call-completed",
        if_exp=f"async.data.lead_id == '{lead_id}'",
        timeout="24h"
    )

    if phone_response:
        return await ctx.step.run(
            "process-phone",
            process_call_response,
            lead_id,
            phone_response.data
        )

    # No response via any channel
    return await ctx.step.run(
        "no-response",
        handle_no_response,
        lead_id
    )
```

---

## 2. Workflow Cancellation

Cancel running workflows when they become irrelevant.

### Basic Cancellation

```python
@inngest_client.create_function(
    fn_id="leads/follow-up",
    trigger=inngest.TriggerEvent(event="workflow/schedule-follow-up"),
    cancel=[
        inngest.Cancel(
            event="lead/converted",
            if_exp="async.data.lead_id == event.data.lead_id"
        )
    ]
)
async def follow_up_workflow(ctx: inngest.Context):
    lead_id = ctx.event.data["lead_id"]

    # This entire workflow cancels if lead/converted fires with matching lead_id
    await ctx.step.sleep("wait-3-days", "3d")

    await ctx.step.run("send-follow-up", send_follow_up_email, lead_id)

    await ctx.step.sleep("wait-7-days", "7d")

    await ctx.step.run("send-second-follow-up", send_second_follow_up, lead_id)
```

### Multiple Cancellation Conditions

```python
@inngest_client.create_function(
    fn_id="campaigns/drip-sequence",
    trigger=inngest.TriggerEvent(event="campaign/start"),
    cancel=[
        # Cancel if user unsubscribes
        inngest.Cancel(
            event="user/unsubscribed",
            if_exp="async.data.user_id == event.data.user_id"
        ),
        # Cancel if user converts
        inngest.Cancel(
            event="user/converted",
            if_exp="async.data.user_id == event.data.user_id"
        ),
        # Cancel if campaign is paused
        inngest.Cancel(
            event="campaign/paused",
            if_exp="async.data.campaign_id == event.data.campaign_id"
        )
    ]
)
async def drip_campaign(ctx: inngest.Context):
    # ... workflow logic
    pass
```

### Cancel vs Wait Decision

| Use Case | Pattern |
|----------|---------|
| Stop workflow entirely | `cancel=[]` |
| Need to handle the event in workflow | `wait_for_event` |
| Don't care about the event data | `cancel=[]` |
| Branch based on event data | `wait_for_event` |

---

## 3. Advanced Concurrency Control

### Throttling External APIs

```python
@inngest_client.create_function(
    fn_id="emails/send-bulk",
    trigger=inngest.TriggerEvent(event="email/send-batch"),
    concurrency=[
        inngest.Concurrency(
            limit=10,
            key="event.data.provider"  # 10 concurrent per email provider
        )
    ],
    throttle=inngest.Throttle(
        limit=100,
        period="1m"  # Max 100 per minute
    )
)
async def send_bulk_email(ctx: inngest.Context):
    # Rate-limited email sending
    pass
```

### Queue Priority with Concurrency Keys

```python
@inngest_client.create_function(
    fn_id="processing/prioritized",
    trigger=inngest.TriggerEvent(event="job/process"),
    concurrency=[
        inngest.Concurrency(limit=50),  # Global limit
        inngest.Concurrency(
            limit=10,
            key="event.data.priority"  # Separate queues per priority
        ),
        inngest.Concurrency(
            limit=5,
            key="event.data.customer_id"  # Fair share per customer
        )
    ]
)
async def process_job(ctx: inngest.Context):
    # High-priority jobs get their own 10 slots
    # Each customer limited to 5 concurrent
    pass
```

### Debouncing Rapid Events

```python
@inngest_client.create_function(
    fn_id="search/index-update",
    trigger=inngest.TriggerEvent(event="content/updated"),
    debounce=inngest.Debounce(
        period="5m",
        key="event.data.document_id"
    )
)
async def update_search_index(ctx: inngest.Context):
    # Only runs once per document per 5 minutes
    # Prevents rapid re-indexing on multiple edits
    pass
```

---

## 4. Fan-Out Pattern

Process multiple items in parallel within a workflow.

### Basic Fan-Out

```python
@inngest_client.create_function(
    fn_id="batch/process-items",
    trigger=inngest.TriggerEvent(event="batch/process")
)
async def batch_processor(ctx: inngest.Context):
    items = ctx.event.data["items"]

    # Process each item as a separate step (parallel execution)
    results = []
    for i, item in enumerate(items):
        result = await ctx.step.run(
            f"process-item-{i}",
            process_single_item,
            item
        )
        results.append(result)

    # Aggregate results
    return await ctx.step.run(
        "aggregate",
        aggregate_results,
        results
    )
```

### Fan-Out with Event Triggers

For large fan-outs, trigger child workflows:

```python
@inngest_client.create_function(
    fn_id="batch/orchestrator",
    trigger=inngest.TriggerEvent(event="batch/start-large")
)
async def orchestrator(ctx: inngest.Context):
    batch_id = ctx.event.data["batch_id"]
    items = ctx.event.data["items"]

    # Fan out: trigger individual workflows
    await ctx.step.run(
        "trigger-workers",
        trigger_worker_workflows,
        batch_id,
        items
    )

    # Wait for completion signal
    completion = await ctx.step.wait_for_event(
        "wait-completion",
        event="batch/all-complete",
        if_exp=f"async.data.batch_id == '{batch_id}'",
        timeout="1h"
    )

    return {"status": "completed", "batch_id": batch_id}


async def trigger_worker_workflows(batch_id: str, items: list):
    events = [
        inngest.Event(
            name="batch/process-single",
            data={
                "batch_id": batch_id,
                "item": item,
                "index": i
            }
        )
        for i, item in enumerate(items)
    ]
    await inngest_client.send(events)


@inngest_client.create_function(
    fn_id="batch/worker",
    trigger=inngest.TriggerEvent(event="batch/process-single"),
    concurrency=[inngest.Concurrency(limit=20)]  # Control parallelism
)
async def worker(ctx: inngest.Context):
    item = ctx.event.data["item"]
    batch_id = ctx.event.data["batch_id"]

    result = await ctx.step.run("process", process_item, item)

    # Track completion (external service aggregates)
    await ctx.step.run(
        "report-completion",
        report_item_complete,
        batch_id,
        result
    )
```

---

## 5. Human-in-the-Loop Workflows

Workflows that pause for human decisions.

### Approval Workflow with Escalation

```python
@inngest_client.create_function(
    fn_id="expenses/approval",
    trigger=inngest.TriggerEvent(event="expense/submitted"),
    cancel=[
        inngest.Cancel(
            event="expense/cancelled",
            if_exp="async.data.expense_id == event.data.expense_id"
        )
    ]
)
async def expense_approval(ctx: inngest.Context):
    expense_id = ctx.event.data["expense_id"]
    amount = ctx.event.data["amount"]
    submitter = ctx.event.data["submitter"]

    # Determine approver based on amount
    approver = await ctx.step.run(
        "get-approver",
        determine_approver,
        amount,
        submitter
    )

    # Notify approver
    await ctx.step.run(
        "notify-approver",
        send_approval_request,
        expense_id,
        approver
    )

    # Wait for decision (24h timeout)
    decision = await ctx.step.wait_for_event(
        "wait-decision",
        event="expense/decision",
        if_exp=f"async.data.expense_id == '{expense_id}'",
        timeout="24h"
    )

    if decision is None:
        # Escalate to manager
        manager = await ctx.step.run("get-manager", get_manager, approver)

        await ctx.step.run(
            "notify-manager",
            send_escalation,
            expense_id,
            manager
        )

        # Wait again with longer timeout
        decision = await ctx.step.wait_for_event(
            "wait-escalated-decision",
            event="expense/decision",
            if_exp=f"async.data.expense_id == '{expense_id}'",
            timeout="48h"
        )

    if decision is None:
        return await ctx.step.run("auto-reject", auto_reject_expense, expense_id)

    if decision.data.get("approved"):
        await ctx.step.run("process-approved", process_approved_expense, expense_id)
    else:
        await ctx.step.run("process-rejected", process_rejected_expense, expense_id, decision.data.get("reason"))

    return {"expense_id": expense_id, "status": "completed"}
```

### Review Queue with Assignment

```python
@inngest_client.create_function(
    fn_id="content/moderation",
    trigger=inngest.TriggerEvent(event="content/flagged")
)
async def moderation_workflow(ctx: inngest.Context):
    content_id = ctx.event.data["content_id"]

    # AI pre-classification
    classification = await ctx.step.run(
        "classify",
        ai_classify_content,
        content_id
    )

    if classification["confidence"] > 0.95:
        # High confidence - auto-action
        return await ctx.step.run(
            "auto-action",
            apply_moderation_decision,
            content_id,
            classification["action"]
        )

    # Needs human review - assign to queue
    await ctx.step.run(
        "queue-for-review",
        add_to_review_queue,
        content_id,
        classification
    )

    # Wait for human decision (SLA: 4 hours)
    decision = await ctx.step.wait_for_event(
        "wait-review",
        event="content/reviewed",
        if_exp=f"async.data.content_id == '{content_id}'",
        timeout="4h"
    )

    if decision is None:
        # SLA breach - escalate
        await ctx.step.run("escalate", escalate_to_senior_mod, content_id)

        decision = await ctx.step.wait_for_event(
            "wait-escalated-review",
            event="content/reviewed",
            if_exp=f"async.data.content_id == '{content_id}'",
            timeout="1h"
        )

    if decision:
        return await ctx.step.run(
            "apply-decision",
            apply_moderation_decision,
            content_id,
            decision.data["action"]
        )

    return {"content_id": content_id, "status": "timeout", "requires_manual_handling": True}
```

---

## 6. Workflow Coordination Patterns

### Sequential Workflow Chain

```python
# Workflow A triggers B on completion
@inngest_client.create_function(
    fn_id="pipeline/stage-1",
    trigger=inngest.TriggerEvent(event="pipeline/start")
)
async def stage_one(ctx: inngest.Context):
    job_id = ctx.event.data["job_id"]

    result = await ctx.step.run("process", process_stage_one, job_id)

    # Trigger next stage
    await inngest_client.send(
        inngest.Event(
            name="pipeline/stage-2",
            data={
                "job_id": job_id,
                "stage_1_result": result
            }
        )
    )

    return result


@inngest_client.create_function(
    fn_id="pipeline/stage-2",
    trigger=inngest.TriggerEvent(event="pipeline/stage-2")
)
async def stage_two(ctx: inngest.Context):
    job_id = ctx.event.data["job_id"]
    stage_1_result = ctx.event.data["stage_1_result"]

    result = await ctx.step.run("process", process_stage_two, job_id, stage_1_result)

    return result
```

### Saga Pattern with Compensation

```python
@inngest_client.create_function(
    fn_id="orders/saga",
    trigger=inngest.TriggerEvent(event="order/place")
)
async def order_saga(ctx: inngest.Context):
    order_id = ctx.event.data["order_id"]
    compensations = []

    try:
        # Step 1: Reserve inventory
        inventory_reservation = await ctx.step.run(
            "reserve-inventory",
            reserve_inventory,
            order_id
        )
        compensations.append(("release-inventory", release_inventory, inventory_reservation))

        # Step 2: Charge payment
        payment = await ctx.step.run(
            "charge-payment",
            charge_customer,
            order_id
        )
        compensations.append(("refund-payment", refund_payment, payment))

        # Step 3: Create shipment
        shipment = await ctx.step.run(
            "create-shipment",
            create_shipment,
            order_id
        )

        return {"status": "completed", "order_id": order_id}

    except Exception as e:
        # Compensate in reverse order
        for step_name, compensation_fn, data in reversed(compensations):
            await ctx.step.run(
                f"compensate-{step_name}",
                compensation_fn,
                data
            )

        raise e
```

---

## 7. Retry Enhancement Patterns

### Idempotency Keys

```python
async def create_payment(order_id: str, amount: float) -> dict:
    """
    Use idempotency key to prevent duplicate payments on retry.
    """
    idempotency_key = f"payment-{order_id}"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.stripe.com/v1/payment_intents",
            headers={
                "Idempotency-Key": idempotency_key,
                "Authorization": f"Bearer {settings.stripe_key}"
            },
            data={
                "amount": int(amount * 100),
                "currency": "usd"
            }
        )
        return response.json()
```

### Checkpoint Pattern

```python
@inngest_client.create_function(
    fn_id="migration/large-dataset",
    trigger=inngest.TriggerEvent(event="migration/start")
)
async def migrate_dataset(ctx: inngest.Context):
    migration_id = ctx.event.data["migration_id"]
    batch_size = 100

    # Get or initialize progress
    progress = await ctx.step.run(
        "get-progress",
        get_migration_progress,
        migration_id
    )

    offset = progress.get("offset", 0)
    total = progress.get("total", 0)

    while offset < total:
        # Process batch
        await ctx.step.run(
            f"process-batch-{offset}",
            process_migration_batch,
            migration_id,
            offset,
            batch_size
        )

        # Save checkpoint
        offset += batch_size
        await ctx.step.run(
            f"checkpoint-{offset}",
            save_migration_progress,
            migration_id,
            offset
        )

    return {"status": "completed", "records_processed": total}
```

---

## 8. Testing Wait Events

### Local Development Testing

```python
# In dev, send events via Inngest dashboard or API
import httpx

async def simulate_reply_received(lead_id: str):
    """Test helper to simulate an incoming reply"""
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:8288/e/test-event-key",
            json={
                "name": "api/reply-received",
                "data": {
                    "lead_id": lead_id,
                    "reply_text": "Test reply",
                    "sentiment": "positive"
                }
            }
        )
```

### Unit Testing Workflows

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_approval_workflow_approved():
    """Test workflow handles approval correctly"""
    mock_ctx = AsyncMock()
    mock_ctx.event.data = {"order_id": "order-123"}

    # Mock wait_for_event to return approval
    mock_ctx.step.wait_for_event.return_value = AsyncMock(
        data={"order_id": "order-123", "approved": True}
    )

    with patch("app.workflows.fulfill_order") as mock_fulfill:
        await approval_workflow(mock_ctx)
        mock_fulfill.assert_called_once_with("order-123")
```
