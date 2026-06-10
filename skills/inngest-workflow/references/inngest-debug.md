# Inngest: Debugging & Troubleshooting

Guide for debugging, testing, and troubleshooting Inngest workflows in development and production.

---

## 1. Development Server

### Starting the Dev Server

```bash
# Install CLI
npm install -g inngest-cli

# Start dev server (connects to your app at localhost:8000)
npx inngest-cli@latest dev

# Specify custom port for your app
npx inngest-cli@latest dev -u http://localhost:3000/api/inngest
```

**Dashboard:** `http://localhost:8288`

### Dev Server Features

| Feature | How to Use |
|---------|------------|
| **Trigger Events** | Event tab → Send Event → paste JSON payload |
| **View Runs** | Runs tab → click any run for step-by-step execution |
| **Replay Failed** | Runs tab → click failed run → Replay button |
| **View Logs** | Each step shows logs and return values |
| **Function List** | Functions tab → see all registered functions |

### Sending Test Events

**Via Dashboard:**
1. Open `http://localhost:8288`
2. Go to "Send Event" or click a function → "Trigger"
3. Enter event payload:
```json
{
  "name": "api/new-lead",
  "data": {
    "lead_id": "test-123",
    "lead": {
      "name": "Test User",
      "email": "test@example.com"
    }
  }
}
```

**Via cURL:**
```bash
curl -X POST http://localhost:8288/e/test-key \
  -H "Content-Type: application/json" \
  -d '{
    "name": "api/new-lead",
    "data": {
      "lead_id": "test-123",
      "lead": {"name": "Test", "email": "test@example.com"}
    }
  }'
```

**Via Python:**
```python
import httpx

async def send_test_event():
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:8288/e/test-key",
            json={
                "name": "api/new-lead",
                "data": {"lead_id": "test-123"}
            }
        )
```

---

## 2. Common Errors & Fixes

### Function Not Found

**Symptom:** Event sent but no function runs.

**Causes & Fixes:**

1. **Function not registered:**
```python
# Check functions list in serve()
inngest.fast_api.serve(app, inngest_client, functions)

# Ensure function is in the list
functions = [
    lead_workflow,      # Is your function here?
    follow_up_workflow,
]
```

2. **Event name mismatch:**
```python
# Trigger event name
await inngest_client.send(inngest.Event(name="api/new-lead", ...))

# Must match exactly
@inngest_client.create_function(
    trigger=inngest.TriggerEvent(event="api/new-lead")  # Same name
)
```

3. **App not synced:**
   - Restart your app after adding new functions
   - Check dev server shows the function in Functions tab

### Step Timeout

**Symptom:** `Step timed out after X seconds`

**Causes & Fixes:**

1. **Long-running operation:**
```python
# Bad: Long operation blocks
async def slow_operation(data):
    # Takes 5+ minutes
    return await some_slow_api_call(data)

# Good: Increase timeout or break into smaller steps
async def slow_operation(data):
    async with httpx.AsyncClient(timeout=300) as client:  # 5 min timeout
        return await client.post(url, json=data)
```

2. **External service slow:**
```python
# Add explicit timeout handling
from inngest.errors import RetryAfterError

async def call_external_api(data):
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, json=data)
            return response.json()
    except httpx.TimeoutException:
        raise RetryAfterError("5m", "External API timeout, retrying later")
```

### NonRetriableError vs Retrying Forever

**Symptom:** Function keeps retrying when it shouldn't.

```python
from inngest.errors import NonRetriableError

async def process_data(data):
    # Validate input - don't retry on bad data
    if not data.get("required_field"):
        raise NonRetriableError("Missing required_field - invalid input")

    # Check preconditions
    record = await get_record(data["id"])
    if record is None:
        raise NonRetriableError(f"Record {data['id']} not found")

    # This can retry on transient failures
    return await external_api.process(record)
```

### Duplicate Executions

**Symptom:** Step runs multiple times.

**Causes & Fixes:**

1. **Step name not unique:**
```python
# Bad: Same step name in loop
for item in items:
    await ctx.step.run("process", process_item, item)  # All named "process"!

# Good: Unique step names
for i, item in enumerate(items):
    await ctx.step.run(f"process-{i}", process_item, item)
```

2. **Non-idempotent operations:**
```python
# Bad: Creates duplicate on retry
async def create_user(data):
    return await db.insert(users, data)

# Good: Idempotent with upsert or check
async def create_user(data):
    existing = await db.get_by_email(data["email"])
    if existing:
        return existing
    return await db.insert(users, data)
```

### wait_for_event Never Resolves

**Symptom:** Workflow stuck waiting, even though event was sent.

**Causes & Fixes:**

1. **`if_exp` mismatch:**
```python
# Waiting for:
await ctx.step.wait_for_event(
    "wait",
    event="api/reply",
    if_exp="async.data.lead_id == 'lead-123'"  # Expects string
)

# Event sent with wrong type:
await inngest_client.send(inngest.Event(
    name="api/reply",
    data={"lead_id": 123}  # Number, not string!
))

# Fix: Ensure types match
data={"lead_id": "lead-123"}  # String
```

2. **Event sent before wait started:**
```python
# Problem: Event sent before workflow reaches wait_for_event

# Solution: Ensure workflow is waiting before sending event
# Check run status in dashboard before sending resolution event
```

3. **Event name mismatch:**
```python
# Check exact match (case-sensitive)
if_exp="async.data.leadId == ..."  # camelCase
# vs
data={"lead_id": ...}  # snake_case
```

### Memory/Payload Too Large

**Symptom:** `Payload too large` or memory errors.

```python
# Bad: Returning large data from step
async def fetch_all_records():
    return await db.get_all()  # Could be millions of records

# Good: Return references, not data
async def fetch_all_records():
    # Store in temp location, return reference
    batch_id = await store_to_temp_storage(records)
    return {"batch_id": batch_id, "count": len(records)}

# Then fetch as needed
async def process_batch(batch_info):
    records = await get_from_temp_storage(batch_info["batch_id"])
    # Process in chunks
```

---

## 3. Logging Best Practices

### Structured Logging

```python
import logging
import json

logger = logging.getLogger("inngest.workflows")

async def process_lead(lead_id: str, lead: dict) -> dict:
    logger.info(
        "Processing lead",
        extra={
            "lead_id": lead_id,
            "lead_email": lead.get("email"),
            "step": "process_lead"
        }
    )

    try:
        result = await do_processing(lead)
        logger.info(
            "Lead processed successfully",
            extra={"lead_id": lead_id, "result_status": result.get("status")}
        )
        return result

    except Exception as e:
        logger.error(
            "Lead processing failed",
            extra={"lead_id": lead_id, "error": str(e)},
            exc_info=True
        )
        raise
```

### Adding Context to All Logs

```python
@inngest_client.create_function(
    fn_id="leads/process",
    trigger=inngest.TriggerEvent(event="api/new-lead")
)
async def lead_workflow(ctx: inngest.Context):
    lead_id = ctx.event.data["lead_id"]
    run_id = ctx.run_id

    # Log workflow start with identifiers
    logger.info(f"Workflow started: lead_id={lead_id}, run_id={run_id}")

    # ... steps ...

    logger.info(f"Workflow completed: lead_id={lead_id}, run_id={run_id}")
```

### Viewing Logs

**Dev Server:**
- Each step shows stdout/stderr in the run details
- Click on a run → expand steps → view output

**Production (Inngest Cloud):**
- Dashboard → Runs → click run → step logs
- Filter by function, status, time range

---

## 4. Testing Strategies

### Unit Testing Step Functions

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_create_profile():
    """Test individual step function"""
    lead = {"name": "Test", "email": "test@example.com"}

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = AsyncMock(
            json=lambda: {"profile_id": "prof-123"},
            raise_for_status=lambda: None
        )

        result = await create_lead_profile(lead, "lead-123")

        assert result["profile_id"] == "prof-123"
        mock_post.assert_called_once()
```

### Integration Testing Workflows

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_lead_workflow_happy_path():
    """Test full workflow execution"""
    # Mock context
    ctx = MagicMock()
    ctx.event.data = {
        "lead_id": "lead-123",
        "lead": {"name": "Test", "email": "test@example.com"}
    }

    # Mock steps to return expected data
    ctx.step.run = AsyncMock(side_effect=[
        {"individual_profile": {}, "company_profile": {}},  # create-profile
        {"offer_text": "Special offer"},                    # create-offer
        {"first_method": "email"},                          # create-strategy
        {"email_content": "Hello..."},                      # create-email
        {"sent": True},                                     # send-email
    ])

    result = await lead_workflow(ctx)

    assert result["status"] == "completed"
    assert result["method"] == "email"
    assert ctx.step.run.call_count == 5
```

### Testing wait_for_event

```python
@pytest.mark.asyncio
async def test_approval_workflow_timeout():
    """Test workflow handles timeout correctly"""
    ctx = MagicMock()
    ctx.event.data = {"order_id": "order-123"}

    # Simulate timeout (returns None)
    ctx.step.wait_for_event = AsyncMock(return_value=None)
    ctx.step.run = AsyncMock()

    await approval_workflow(ctx)

    # Verify escalation was called
    escalation_call = [
        call for call in ctx.step.run.call_args_list
        if "escalate" in str(call)
    ]
    assert len(escalation_call) > 0


@pytest.mark.asyncio
async def test_approval_workflow_approved():
    """Test workflow handles approval correctly"""
    ctx = MagicMock()
    ctx.event.data = {"order_id": "order-123"}

    # Simulate approval event received
    approval_event = MagicMock()
    approval_event.data = {"order_id": "order-123", "approved": True}
    ctx.step.wait_for_event = AsyncMock(return_value=approval_event)
    ctx.step.run = AsyncMock()

    await approval_workflow(ctx)

    # Verify order was fulfilled
    fulfill_calls = [
        call for call in ctx.step.run.call_args_list
        if "fulfill" in str(call) or "approved" in str(call)
    ]
    assert len(fulfill_calls) > 0
```

### End-to-End Testing with Dev Server

```python
import httpx
import asyncio
import pytest

@pytest.mark.asyncio
async def test_full_workflow_e2e():
    """E2E test against running dev server"""
    lead_id = f"test-{int(time.time())}"

    # Trigger workflow
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:8288/e/test-key",
            json={
                "name": "api/new-lead",
                "data": {"lead_id": lead_id, "lead": {"name": "Test"}}
            }
        )

    # Wait for processing
    await asyncio.sleep(5)

    # Verify results (check database, external state, etc.)
    result = await get_lead_status(lead_id)
    assert result["status"] == "processed"
```

---

## 5. Production Debugging

### Inngest Cloud Dashboard

**Finding Failed Runs:**
1. Go to Runs tab
2. Filter by Status: Failed
3. Click run to see step-by-step execution
4. Failed step shows error message and stack trace

**Replaying Failed Runs:**
1. Find failed run
2. Click "Replay" button
3. Run re-executes from the failed step (previous steps are memoized)

### Common Production Issues

**1. Signing Key Mismatch:**
```
Error: Invalid signature
```
- Verify `INNGEST_SIGNING_KEY` matches your Inngest app
- Check environment variable is set correctly

**2. Event Key Issues:**
```
Error: Unauthorized
```
- Verify `INNGEST_EVENT_KEY` is correct
- Check key hasn't been rotated

**3. Function Timeout in Cloud:**
- Free tier: 10 seconds per step
- Paid tier: configurable up to 15 minutes
- Break long operations into multiple steps

### Metrics to Monitor

| Metric | What to Watch |
|--------|---------------|
| **Run Duration** | Sudden increases may indicate issues |
| **Failure Rate** | Spike in failures needs investigation |
| **Queue Depth** | Growing queue = processing can't keep up |
| **Retry Rate** | High retries = flaky dependencies |

---

## 6. Debugging Checklist

### Workflow Not Triggering
- [ ] Function registered in `serve()` call?
- [ ] Event name matches trigger exactly?
- [ ] App synced with Inngest (restart after changes)?
- [ ] Check dev server Functions tab

### Workflow Stuck
- [ ] Check current step in run details
- [ ] Look for `wait_for_event` - waiting for external event?
- [ ] Check `if_exp` syntax and data types
- [ ] Look for sleep steps

### Workflow Failing
- [ ] Check error message in run details
- [ ] Look at step that failed
- [ ] Check if error is retryable or not
- [ ] Verify external services are reachable
- [ ] Check for payload size issues

### Duplicate Processing
- [ ] Step names unique?
- [ ] Operations idempotent?
- [ ] Using idempotency keys for external APIs?

### Performance Issues
- [ ] Too many steps? (each has overhead)
- [ ] Large payloads between steps?
- [ ] External API timeouts?
- [ ] Concurrency limits too low?

---

## 7. Useful Commands

```bash
# Check Inngest CLI version
npx inngest-cli@latest --version

# Start dev server with verbose logging
npx inngest-cli@latest dev --log-level debug

# Check registered functions
curl http://localhost:8288/v1/functions

# Manually trigger event
curl -X POST http://localhost:8288/e/test-key \
  -H "Content-Type: application/json" \
  -d '{"name": "your/event", "data": {}}'

# Check run status (replace with actual run ID)
curl http://localhost:8288/v1/runs/run_01234567890
```

---

## 8. Error Reference

| Error | Cause | Fix |
|-------|-------|-----|
| `Function not found` | Event name mismatch or function not registered | Check trigger event name, verify function in serve() |
| `Step timed out` | Operation took too long | Increase timeout, break into smaller steps |
| `Payload too large` | Step returned too much data | Return references, not large data |
| `Invalid signature` | Signing key mismatch | Check INNGEST_SIGNING_KEY |
| `NonRetriableError` | Intentional failure, won't retry | Check if error condition is correct |
| `RetryAfterError` | Temporary failure, will retry | Verify retry delay is appropriate |
| `Max retries exceeded` | All retries failed | Check underlying cause, increase retries if needed |
