# Inngest Workflow Skill

> **Invoke with:** `/inngest-workflow` | **Keywords:** inngest, ingest, workflow, background jobs, async, event-driven, step functions, FastAPI, Python

A comprehensive guide for creating, improving, and debugging Inngest workflows in Python/FastAPI projects. Use this skill when you need to:
- Create new Inngest workflows or functions
- Add step functions, sleeps, or wait_for_event patterns
- Debug workflow issues or troubleshoot errors
- Implement concurrency, cancellation, or fan-out patterns
- Set up Inngest in a FastAPI project

---

## Purpose

This skill helps you work with Inngest, a durable workflow orchestration platform for building reliable background jobs and event-driven workflows.

## Reference Files

Choose the appropriate reference based on your task:

| Task | Reference File | Description |
|------|----------------|-------------|
| **Create** | [inngest-create.md](./inngest-create.md) | Building workflows from scratch - project setup, function creation, step chaining, event design |
| **Improve** | [inngest-improve.md](./inngest-improve.md) | Enhancing existing workflows - wait_for_event, cancellation, concurrency, fan-out, human-in-the-loop |
| **Debug** | [inngest-debug.md](./inngest-debug.md) | Troubleshooting - dev server, common errors, logging, testing strategies |

> **Maintenance Note**: If any patterns in the reference files are found to be incorrect during implementation, update the corresponding reference file with the correct pattern. This keeps the documentation accurate and prevents future issues.

---

## Core Concepts

### What is Inngest?

Inngest is a **durable workflow orchestration platform** that enables event-driven background job processing with:
- Built-in retries and durability
- Step functions for complex workflows
- Event-driven architecture
- Automatic state management
- Built-in observability

### Key Components

| Component | Description |
|-----------|-------------|
| **Events** | JSON payloads that trigger workflows (e.g., `user/signed-up`, `order/placed`) |
| **Functions** | Code that runs in response to events, containing one or more steps |
| **Steps** | Individual units of work within a function that are durably executed |
| **Client** | The Inngest SDK instance that connects your app to Inngest |

### How Inngest Works

```
Event Sent → Inngest Receives → Matches to Function → Executes Steps → Returns Result
     ↓              ↓                  ↓                    ↓
  JSON payload   Event routing    fn_id + trigger      step.run(), step.sleep(), etc.
```

### Durability & Retry Guarantees

**Step Memoization**: Each step's result is cached. If a function retries:
- Completed steps are **skipped** (results loaded from storage)
- Failed steps are **retried**
- This prevents duplicate operations (e.g., double-charging payments)

**At-Least-Once Execution**: Events are processed at least once. Design steps to be idempotent.

**Automatic Retries**: Functions retry on failure with exponential backoff (default: 3 attempts over ~2 hours).

### Inngest vs Traditional Job Queues

| Feature | Inngest | Celery/RQ |
|---------|---------|-----------|
| **Execution Model** | Event-triggered, step-based | Task-based |
| **State Management** | Automatic, durable | Manual (databases) |
| **Retries** | Per-step, automatic | Per-task, manual config |
| **Observability** | Built-in dashboard | Requires setup (Flower) |
| **Long Delays** | Native `step.sleep()` | Requires ETA/countdown |
| **Event Replay** | Built-in | Not available |
| **Local Development** | Dev server (no infra) | Requires Redis/broker |

---

## Quick Reference

### Step Function Signatures

```python
# step.run()
result = await ctx.step.run("step-id", function, *args)

# step.sleep()
await ctx.step.sleep("sleep-id", "24h")
await ctx.step.sleep("sleep-id", datetime.timedelta(hours=24))

# step.wait_for_event()
event = await ctx.step.wait_for_event(
    "wait-id",
    event="event/name",
    timeout=datetime.timedelta(days=7),
    if_exp="async.data.id == event.data.id"
)
# Returns None on timeout, Event object otherwise
```

### Function Decorator Options

```python
@inngest_client.create_function(
    fn_id="unique/function-id",                    # Required
    trigger=inngest.TriggerEvent(event="name"),   # Required
    retries=5,                                     # Override default retries
    cancel=[                                       # Cancellation events
        inngest.Cancel(
            event="cancel/event",
            if_exp="async.data.id == event.data.id"
        )
    ],
    concurrency=[                                  # Rate limiting
        inngest.Concurrency(
            limit=10,
            key="event.data.user_id"               # Per-user limit
        )
    ]
)
```

### Sending Events

```python
# Single event
await inngest_client.send(
    inngest.Event(name="event/name", data={"key": "value"})
)

# Multiple events
await inngest_client.send([
    inngest.Event(name="event/one", data={...}),
    inngest.Event(name="event/two", data={...})
])
```

### Error Types

```python
from inngest.errors import NonRetriableError, RetryAfterError

# Don't retry this error
raise NonRetriableError("Validation failed")

# Retry after specific duration
raise RetryAfterError("1h", "Rate limited")

# Default behavior: raise Exception for automatic retry
raise Exception("Temporary failure")
```

### Duration Formats

```
"30s"   # 30 seconds
"5m"    # 5 minutes
"2h"    # 2 hours
"7d"    # 7 days
"1w"    # 1 week

# Or use timedelta
datetime.timedelta(seconds=30)
datetime.timedelta(minutes=5)
datetime.timedelta(hours=2)
datetime.timedelta(days=7)
```

### Dev Server Commands

```bash
# Start dev server
npx inngest-cli@latest dev

# Access dashboard
# http://localhost:8288
```

---

## Event Naming Conventions

```
{resource}/{action}
{source}/{resource}-{action}

Examples:
api/new-lead            # External trigger (webhook)
api/reply-received      # External trigger (webhook)
workflow/await-reply    # Internal workflow trigger
workflow/process-reply  # Internal workflow trigger
user/signed-up          # Domain event
order/placed            # Domain event
```

---

## Genie IQ Reference Patterns

The Genie IQ API provides production examples of Inngest patterns:

| Pattern | Description |
|---------|-------------|
| **Folder structure** | Uses `src/app/_inngest/` with dedicated `workflows/` subfolder |
| **Function registry** | Centralized in `inngest.py` with all functions listed |
| **Dual events** | Webhooks send both `api/*` and `workflow/*` events for coordination |
| **wait_for_event** | Uses `if_exp` with lead_id matching for reply detection |
| **Workflow cancellation** | Cancels await_reply when appointment is booked |
| **Conditional branching** | Routes to email or phone workflows based on strategy |

**File locations in Genie IQ:**
- Client: `src/app/_inngest/client.py`
- Registry: `src/app/_inngest/inngest.py`
- Workflows: `src/app/_inngest/workflows/`

---

## Documentation Links

- **Official Docs**: https://www.inngest.com/docs
- **Python SDK**: https://www.inngest.com/docs/sdk/python
- **FastAPI Guide**: https://www.inngest.com/docs/sdk/python/frameworks/fastapi
- **Step Functions**: https://www.inngest.com/docs/functions/steps
- **GitHub**: https://github.com/inngest/inngest-py
