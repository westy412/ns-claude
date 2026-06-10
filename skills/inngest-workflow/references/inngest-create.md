# Inngest: Creating Workflows from Scratch

Comprehensive guide for setting up Inngest in a Python/FastAPI project with production-ready patterns.

---

## 1. Install Dependencies

```bash
pip install inngest
```

---

## 2. Create the Client

```python
# inngest_client.py
import inngest
import logging
import os

inngest_client = inngest.Inngest(
    app_id="your-app-name",
    logger=logging.getLogger('uvicorn'),
    is_production=os.getenv("ENVIRONMENT") == "production"
)
```

**Environment variables:**
```bash
INNGEST_EVENT_KEY=your-event-key      # For sending events
INNGEST_SIGNING_KEY=your-signing-key  # For webhook verification (production)
ENVIRONMENT=production                 # Production flag
```

---

## 3. Register with FastAPI

```python
# main.py
from fastapi import FastAPI
import inngest.fast_api
from .inngest_client import inngest_client
from .workflows import functions  # List of all workflow functions

app = FastAPI()

# Register Inngest endpoint
inngest.fast_api.serve(app, inngest_client, functions)
```

**Function Registry:**

```python
# workflows/__init__.py or registry.py
from .lead_workflow import lead_workflow
from .follow_up_workflow import follow_up_workflow
from .notification_workflow import notification_workflow

functions = [
    lead_workflow,
    follow_up_workflow,
    notification_workflow,
]
```

---

## 4. Creating Functions with Step Chaining

Steps are the core building blocks. Each step:
- Is **durably executed** (retried on failure)
- Has its result **memoized** (skipped on replay)
- Can **pass data** to subsequent steps

### Basic Step Chaining

```python
from .inngest_client import inngest_client
import inngest

@inngest_client.create_function(
    fn_id="leads/process-new-lead",
    trigger=inngest.TriggerEvent(event="api/new-lead")
)
async def lead_workflow(ctx: inngest.Context):
    lead_id = ctx.event.data["lead_id"]
    lead = ctx.event.data["lead"]

    # Step 1: Create profile (result passed to step 2)
    profile = await ctx.step.run(
        "create-profile",
        create_lead_profile,
        lead,
        lead_id
    )

    # Step 2: Use profile to create personalized offer
    offer = await ctx.step.run(
        "create-offer",
        create_personalized_offer,
        lead_id,
        profile.get("individual_profile"),
        profile.get("company_profile")
    )

    # Step 3: Use both profile and offer to create strategy
    strategy = await ctx.step.run(
        "create-strategy",
        create_outreach_strategy,
        lead_id,
        profile,
        offer
    )

    # Step 4: Execute based on strategy
    first_method = strategy.get("first_method")

    if first_method == "email":
        email_content = await ctx.step.run(
            "create-email",
            create_email_content,
            lead_id,
            profile,
            offer,
            strategy
        )

        await ctx.step.run(
            "send-email",
            send_email,
            lead_id,
            email_content
        )

    elif first_method == "phone":
        call_script = await ctx.step.run(
            "create-call-script",
            create_call_script,
            lead_id,
            profile,
            offer,
            strategy
        )

        await ctx.step.run(
            "initiate-call",
            initiate_phone_call,
            lead_id,
            call_script
        )

    return {
        "status": "completed",
        "lead_id": lead_id,
        "method": first_method
    }
```

### Step Functions Must Return Serializable Data

```python
import httpx

async def create_lead_profile(lead: dict, lead_id: str) -> dict:
    """
    Step functions should:
    - Return dicts, not ORM objects or classes
    - Handle their own errors (or let them bubble for retry)
    - Be idempotent when possible
    """
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{settings.llm_service_url}/create-profile",
            json={"lead": lead, "lead_id": lead_id}
        )
        response.raise_for_status()
        return response.json()  # Returns dict

async def create_personalized_offer(
    lead_id: str,
    individual_profile: dict,
    company_profile: dict
) -> dict:
    """Uses data from previous step"""
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{settings.llm_service_url}/create-offer",
            json={
                "lead_id": lead_id,
                "individual_profile": individual_profile,
                "company_profile": company_profile
            }
        )
        response.raise_for_status()
        return response.json()
```

---

## 5. Retry Configuration

### Default Behavior

Functions retry **3 times** with exponential backoff (~2 hours total).

### Custom Retry Count

```python
@inngest_client.create_function(
    fn_id="api/external-call",
    trigger=inngest.TriggerEvent(event="api/call-external"),
    retries=5  # Override default
)
async def call_external_api(ctx: inngest.Context):
    # Will retry up to 5 times on failure
    pass
```

### Controlling Retry Behavior in Steps

```python
from inngest.errors import NonRetriableError, RetryAfterError

async def process_payment(payment_data: dict) -> dict:
    try:
        result = await payment_gateway.charge(payment_data)
        return {"success": True, "transaction_id": result.id}

    except InvalidCardError as e:
        # Don't retry - card is invalid, retrying won't help
        raise NonRetriableError(f"Invalid card: {e}")

    except RateLimitError as e:
        # Retry after specific duration
        raise RetryAfterError("1h", f"Rate limited by payment gateway")

    except GatewayTimeoutError as e:
        # Let Inngest retry with default backoff
        raise e

    except Exception as e:
        # Unknown error - retry with backoff
        raise e
```

### Error Types Summary

| Error Type | Behavior |
|------------|----------|
| `NonRetriableError` | Stop immediately, no retry |
| `RetryAfterError` | Retry after specified duration |
| Any other `Exception` | Retry with exponential backoff |

---

## 6. Rate Limiting & Concurrency

### Limit Concurrent Executions

```python
@inngest_client.create_function(
    fn_id="api/process-order",
    trigger=inngest.TriggerEvent(event="order/placed"),
    concurrency=[
        inngest.Concurrency(limit=10)  # Max 10 concurrent executions
    ]
)
async def process_order(ctx: inngest.Context):
    # Only 10 instances can run at once across all events
    pass
```

### Per-Key Concurrency (Per-User, Per-Account, etc.)

```python
@inngest_client.create_function(
    fn_id="api/user-action",
    trigger=inngest.TriggerEvent(event="user/action"),
    concurrency=[
        inngest.Concurrency(
            limit=3,
            key="event.data.user_id"  # 3 concurrent per user
        )
    ]
)
async def handle_user_action(ctx: inngest.Context):
    # Each user can have max 3 concurrent executions
    pass
```

### Multiple Concurrency Rules

```python
@inngest_client.create_function(
    fn_id="api/send-notification",
    trigger=inngest.TriggerEvent(event="notification/send"),
    concurrency=[
        inngest.Concurrency(limit=100),  # Global limit
        inngest.Concurrency(
            limit=5,
            key="event.data.user_id"  # Per-user limit
        )
    ]
)
async def send_notification(ctx: inngest.Context):
    # Max 100 total, max 5 per user
    pass
```

---

## 7. Sending Events

### From API Endpoints

```python
from fastapi import APIRouter
from .inngest_client import inngest_client
import inngest

router = APIRouter()

@router.post("/leads")
async def create_lead(lead_data: LeadCreate):
    # Save to database
    async with AsyncSessionLocal() as db:
        lead = Lead(**lead_data.dict())
        db.add(lead)
        await db.commit()
        await db.refresh(lead)
        lead_dict = lead.to_dict()

    # Trigger workflow
    await inngest_client.send(
        inngest.Event(
            name="api/new-lead",
            data={
                "lead_id": str(lead.id),
                "lead": lead_dict,
                "client_id": lead_data.client_id
            }
        )
    )

    return {"lead_id": lead.id, "status": "workflow_triggered"}
```

### Sending Multiple Events

```python
# Send multiple events atomically
await inngest_client.send([
    inngest.Event(name="order/placed", data=order_data),
    inngest.Event(name="inventory/reserved", data=inventory_data),
    inngest.Event(name="notification/send", data={"user_id": user_id, "type": "order_confirmation"})
])
```

### From Within Workflows (Triggering Other Workflows)

```python
@inngest_client.create_function(
    fn_id="leads/initial",
    trigger=inngest.TriggerEvent(event="api/new-lead")
)
async def initial_workflow(ctx: inngest.Context):
    lead_id = ctx.event.data["lead_id"]

    # ... do initial processing ...

    # Trigger follow-up workflow
    await inngest_client.send(
        inngest.Event(
            name="workflow/await-reply",
            data={
                "lead_id": lead_id,
                "follow_up_time": 86400  # 24 hours
            }
        )
    )

    return {"status": "completed"}
```

---

## 8. Multiple Triggers

### Multiple Event Triggers

```python
@inngest_client.create_function(
    fn_id="orders/handle-update",
    trigger=[
        inngest.TriggerEvent(event="order/placed"),
        inngest.TriggerEvent(event="order/updated"),
        inngest.TriggerEvent(event="order/cancelled"),
    ]
)
async def handle_order_event(ctx: inngest.Context):
    event_name = ctx.event.name
    order_id = ctx.event.data["order_id"]

    if event_name == "order/placed":
        await ctx.step.run("process-new", process_new_order, order_id)
    elif event_name == "order/updated":
        await ctx.step.run("process-update", process_order_update, order_id)
    elif event_name == "order/cancelled":
        await ctx.step.run("process-cancel", process_cancellation, order_id)
```

### Cron Triggers (Scheduled)

```python
@inngest_client.create_function(
    fn_id="scheduled/daily-report",
    trigger=inngest.TriggerCron(cron="0 9 * * *")  # 9 AM daily
)
async def daily_report(ctx: inngest.Context):
    await ctx.step.run("generate-report", generate_daily_report)
    await ctx.step.run("send-report", send_report_email)
```

**Cron examples:**
- `"0 9 * * *"` - 9 AM daily
- `"0 0 * * 0"` - Midnight on Sundays
- `"*/15 * * * *"` - Every 15 minutes
- `"0 0 1 * *"` - First day of each month

---

## 9. Sleep & Delays

```python
@inngest_client.create_function(
    fn_id="onboarding/drip-campaign",
    trigger=inngest.TriggerEvent(event="user/signed-up")
)
async def drip_campaign(ctx: inngest.Context):
    user_id = ctx.event.data["user_id"]

    # Send welcome immediately
    await ctx.step.run("welcome-email", send_welcome, user_id)

    # Wait 1 day (durable - survives restarts)
    await ctx.step.sleep("wait-1-day", "1d")

    # Send tips
    await ctx.step.run("tips-email", send_tips, user_id)

    # Wait 3 more days
    await ctx.step.sleep("wait-3-days", "3d")

    # Send feature highlight
    await ctx.step.run("feature-email", send_feature_highlight, user_id)

    return {"status": "completed", "emails_sent": 3}
```

**Duration formats:**
- `"30s"` - 30 seconds
- `"5m"` - 5 minutes
- `"2h"` - 2 hours
- `"7d"` - 7 days
- `datetime.timedelta(hours=24)` - timedelta object

---

## 10. Event Naming Conventions

```
{source}/{resource}-{action}

# External triggers (webhooks, API endpoints)
api/new-lead
api/reply-received
api/appointment-booked

# Internal workflow triggers
workflow/follow-up
workflow/await-reply
workflow/process-reply

# Domain events
user/signed-up
order/placed
payment/completed
```

---

## 11. Project Structure (Genie IQ Pattern)

```
src/app/
├── main.py
├── _inngest/                    # Or workflows/, inngest/, etc.
│   ├── client.py               # Inngest client
│   ├── inngest.py              # Function registry
│   └── workflows/
│       ├── initial/
│       │   ├── workflow.py     # Main workflow function
│       │   └── functions/      # Step functions
│       │       ├── create_profile.py
│       │       ├── create_offer.py
│       │       └── send_email.py
│       ├── follow_up/
│       │   └── workflow.py
│       └── await_reply.py
└── routers/
    └── leads.py                # API endpoints that send events
```

---

## 12. Run Development Server

```bash
# Install CLI
npm install -g inngest-cli

# Start dev server
npx inngest-cli@latest dev
```

**Dashboard:** `http://localhost:8288`

Features:
- Local event triggering
- Real-time execution monitoring
- Event replay
- Function logs
