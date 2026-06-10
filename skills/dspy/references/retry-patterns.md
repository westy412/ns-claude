# Retry Patterns

Exponential backoff with rate limit handling for production DSPy workflows.

## The Problem

API calls fail due to:
- Rate limits (429 errors)
- Network issues
- Transient server errors

Without retry logic, a single failure aborts the entire workflow.

## The Pattern

```python
import asyncio
import random
from typing import Any

async def call_with_retry(
    agent,
    agent_name: str,
    max_retries: int = 3,
    base_wait: float = 30.0,
    **kwargs
) -> Any:
    """
    Retry a DSPy agent call with exponential backoff.

    - Rate limit (429): Wait 30 seconds, retry
    - Other errors: Exponential backoff (5s, 10s, 20s)
    - After max_retries: Raise with detailed error message
    """
    for attempt in range(max_retries):
        try:
            result = await agent.acall(**kwargs)
            if attempt > 0:
                print(f"[OK] {agent_name} succeeded on attempt {attempt + 1}")
            return result

        except Exception as e:
            is_rate_limit = "429" in str(e) or "rate limit" in str(e).lower()

            if attempt < max_retries - 1:
                if is_rate_limit:
                    wait_time = base_wait  # Fixed 30s for rate limits
                    print(f"[WARN] {agent_name} hit rate limit on attempt {attempt + 1}")
                else:
                    # Exponential backoff with jitter
                    base_error_wait = (2 ** attempt) * 5  # 5s, 10s, 20s
                    jitter = random.uniform(0, base_error_wait * 0.3)
                    wait_time = base_error_wait + jitter
                    print(f"[WARN] {agent_name} failed: {type(e).__name__}")

                print(f"  Waiting {wait_time:.1f}s before retry...")
                await asyncio.sleep(wait_time)
            else:
                print(f"[ERROR] {agent_name} failed after {max_retries} attempts")
                raise
```

## Usage

```python
class ExtractionPipeline(dspy.Module):
    async def aforward(self, company_name: str, website_content: str):
        # Stage 1: Extract with retry
        result1 = await call_with_retry(
            self.extractor,
            agent_name="data_extractor",
            company_name=company_name,
            website_content=website_content
        )

        # Stage 2: Analyze with retry
        result2 = await call_with_retry(
            self.analyzer,
            agent_name="analyzer",
            extraction=format_output(result1)
        )

        return result2
```

## Retry Strategy

| Error Type | Wait Time | Rationale |
|------------|-----------|-----------|
| Rate limit (429) | Fixed 30s | Respect API limits |
| Transient error (attempt 0) | 5s + jitter | Quick first retry |
| Transient error (attempt 1) | 10s + jitter | Longer wait |
| Transient error (attempt 2) | 20s + jitter | Final attempt |

## Jitter

Jitter prevents thundering herd when multiple workflows retry simultaneously:

```python
base_wait = (2 ** attempt) * 5  # 5, 10, 20 seconds
jitter = random.uniform(0, base_wait * 0.3)  # 0-30% additional random wait
total_wait = base_wait + jitter
```

## Enhanced Version with Logging

```python
import asyncio
import random
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

async def call_with_retry(
    agent,
    agent_name: str,
    max_retries: int = 3,
    base_wait: float = 30.0,
    on_retry: Optional[callable] = None,
    **kwargs
) -> Any:
    """
    Retry DSPy agent calls with exponential backoff.

    Args:
        agent: DSPy predictor to call
        agent_name: Name for logging
        max_retries: Maximum retry attempts
        base_wait: Wait time for rate limits
        on_retry: Optional callback(attempt, error, wait_time)
        **kwargs: Arguments to pass to agent.acall()
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            result = await agent.acall(**kwargs)

            if attempt > 0:
                logger.info(f"{agent_name} succeeded on attempt {attempt + 1}")

            return result

        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            is_rate_limit = "429" in str(e) or "rate limit" in error_str

            if attempt < max_retries - 1:
                if is_rate_limit:
                    wait_time = base_wait
                    logger.warning(
                        f"{agent_name} hit rate limit (attempt {attempt + 1}/{max_retries})"
                    )
                else:
                    base_error_wait = (2 ** attempt) * 5
                    jitter = random.uniform(0, base_error_wait * 0.3)
                    wait_time = base_error_wait + jitter
                    logger.warning(
                        f"{agent_name} failed with {type(e).__name__} "
                        f"(attempt {attempt + 1}/{max_retries})"
                    )

                if on_retry:
                    on_retry(attempt, e, wait_time)

                logger.info(f"Waiting {wait_time:.1f}s before retry...")
                await asyncio.sleep(wait_time)

            else:
                logger.error(
                    f"{agent_name} failed after {max_retries} attempts: {e}"
                )

    raise last_error
```

## Circuit Breaker Pattern (Advanced)

For high-volume systems, combine with circuit breaker:

```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_timeout: float = 60.0):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half-open

    async def call(self, agent, agent_name: str, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "half-open"
            else:
                raise Exception(f"Circuit breaker open for {agent_name}")

        try:
            result = await call_with_retry(agent, agent_name, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.error(f"Circuit breaker opened for {agent_name}")

            raise
```

## Anti-Patterns

```python
# WRONG: No retry logic
result = await self.extractor.acall(
    company_name=company_name,
    website_content=website_content
)  # Single failure aborts workflow

# WRONG: Simple retry without backoff
for i in range(3):
    try:
        result = await self.extractor.acall(**kwargs)
        break
    except:
        pass  # No wait, no logging, hammers the API

# WRONG: Same wait time for all errors
wait_time = 5  # Should be longer for rate limits
```

## Checklist

- [ ] Use exponential backoff (5s, 10s, 20s)
- [ ] Add jitter to prevent thundering herd
- [ ] Longer wait for rate limits (30s)
- [ ] Log failures with attempt counts
- [ ] Include agent name in logs for debugging
- [ ] Set reasonable max_retries (3-5)
