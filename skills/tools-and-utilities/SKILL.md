---
name: tools-and-utilities
description: Design tools (agent-callable functions) and utility functions (helpers, wrappers). Use when adding functionality that agents will use or shared helper code. Covers input/output design, error handling, and implementation approach.
allowed-tools: Read, Glob, Grep, Task, WebFetch
---

# Tools and Utilities Skill

## Purpose

A design skill for creating tools and utility functions. Helps determine:
- Is this a tool (agent-callable) or a utility function?
- What implementation approach to use?
- How to design inputs, outputs, and error handling?

---

## When to Use This Skill

Use this skill when:
- Adding new tools for agents to call
- Creating utility functions or helper code
- Building wrappers around external services
- Designing shared functionality

**Invoked by:**
- `agent-spec-builder` — When designing tools for new agents
- `agent-improvement-spec` — When adding tools/utilities to existing systems

---

## Key Concepts

### Tool vs Utility Function

| Aspect | Tool | Utility Function |
|--------|------|------------------|
| **Who calls it** | Agent (via LLM) | Other code (not LLM) |
| **Needs description** | Yes (for LLM to understand) | No |
| **Input validation** | Strict (LLM may hallucinate) | Normal |
| **Output format** | Often JSON string | Any Python type |
| **Error handling** | Return error message (don't crash) | Can raise exceptions |

### Decision Tree

```
Does an agent need to decide when to call this?
├── YES → It's a TOOL
│   └── Agent chooses to call based on task
└── NO → It's a UTILITY FUNCTION
    ├── Called by other code unconditionally
    ├── Helper/wrapper functions
    └── Shared logic between agents
```

**Examples:**

| Function | Type | Why |
|----------|------|-----|
| `search_web(query)` | Tool | Agent decides when to search |
| `send_telegram_message(text)` | Tool | Agent decides what to send |
| `parse_telegram_update(data)` | Utility | Always called when update arrives |
| `format_response_for_telegram(text)` | Utility | Always called before sending |
| `get_youtube_transcript(url)` | Tool | Agent decides which videos to fetch |
| `chunk_text(text, max_size)` | Utility | Called by code, not agent decision |

---

## Tool Design

### Step 1: Define Purpose

> "What does this tool enable the agent to do?"

Be specific. One tool = one capability.

**Good:** "Fetch transcript from a YouTube video"
**Bad:** "Handle YouTube stuff" (too vague)

### Step 2: Choose Implementation Approach

| Approach | When to Use | Key Consideration |
|----------|-------------|-------------------|
| **MCP Server** | Functionality exists as MCP server | Check MCP registry first |
| **Existing API** | Third-party API available | Need API docs, auth details |
| **SDK/Library** | Python package available | Need package name, docs |
| **Custom** | No existing solution | Will need to build logic |

**Research if unsure:**

Use web-researcher sub-agent:
```
"Research options for [capability]:
1. Are there MCP servers for this?
2. What APIs are available?
3. What Python libraries exist?
Include: docs URL, auth method, rate limits"
```

### Step 3: Design Input Schema

**Principles:**
- Minimal required parameters
- Clear parameter names
- Sensible defaults where possible
- Validate strictly (LLMs may hallucinate values)

```python
class SearchInput(BaseModel):
    """Input for web search tool."""
    query: str = Field(description="Search query")
    max_results: int = Field(default=5, ge=1, le=20, description="Number of results")
```

**Common patterns:**

| Parameter Type | Example | Notes |
|----------------|---------|-------|
| Required ID | `video_id: str` | No default |
| Optional limit | `max_results: int = 10` | With bounds |
| Optional filter | `language: str = None` | None means "any" |
| Boolean flag | `include_metadata: bool = False` | Default to simpler |

### Step 4: Design Output Format

**For LangGraph tools:** Return JSON string

```python
def search_web(query: str) -> str:
    """Search the web and return results."""
    results = do_search(query)
    return json.dumps({
        "results": results,
        "count": len(results)
    })
```

**Include in output:**
- The requested data
- Metadata (count, status, etc.)
- Error info if failed

### Step 5: Design Error Handling

**Tools should NOT crash.** Return error information instead.

```python
def get_transcript(video_id: str) -> str:
    try:
        transcript = fetch_transcript(video_id)
        return json.dumps({"transcript": transcript, "status": "success"})
    except VideoNotFound:
        return json.dumps({"error": "Video not found", "status": "error"})
    except TranscriptDisabled:
        return json.dumps({"error": "Transcript not available", "status": "error"})
    except Exception as e:
        return json.dumps({"error": str(e), "status": "error"})
```

**Error categories:**

| Category | Example | Handling |
|----------|---------|----------|
| Not found | Video doesn't exist | Return "not found" message |
| Auth failed | Invalid API key | Return auth error (don't expose key) |
| Rate limited | Too many requests | Return "rate limited", maybe retry |
| Invalid input | Bad URL format | Return validation error |
| Service down | API unavailable | Return "service unavailable" |

### Step 6: Write Tool Description

The LLM uses this to decide when to call the tool. Be clear and specific.

```python
@tool
def search_web(query: str) -> str:
    """Search the web for current information.

    Use this when you need:
    - Recent news or events
    - Information that may have changed since training
    - Facts you're uncertain about

    Do NOT use for:
    - Information you already know
    - Historical facts that won't change

    Args:
        query: The search query. Be specific for better results.

    Returns:
        JSON string with search results or error message.
    """
```

---

## Utility Function Design

### Step 1: Define Purpose

> "What code would otherwise be duplicated?"

Utilities extract shared logic.

### Step 2: Design Interface

**Principles:**
- Accept Python types directly (not JSON strings)
- Return Python types directly
- Can raise exceptions (calling code handles them)
- Document parameters and return type

```python
def chunk_text(text: str, max_chars: int = 4000) -> list[str]:
    """Split text into chunks of maximum size.

    Args:
        text: The text to split
        max_chars: Maximum characters per chunk

    Returns:
        List of text chunks

    Raises:
        ValueError: If max_chars < 1
    """
```

### Step 3: Decide on Organization

**How much functionality are you adding?**

| Scope | Organization | When |
|-------|--------------|------|
| **1-2 functions** | Add to existing `utils.py` | Simple helpers, one-off utilities |
| **3-5 related functions** | Own file in team folder | Related functionality, clear grouping |
| **Full integration** | Own module/client class | External service with multiple operations |

---

#### Option A: Add to utils.py (1-2 functions)

For simple, standalone helpers:

```python
# utils.py (existing file)

def format_timestamp(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M")

def truncate_text(text: str, max_len: int = 100) -> str:
    """Truncate text with ellipsis."""
    return text[:max_len] + "..." if len(text) > max_len else text
```

---

#### Option B: Own file (3-5 related functions)

When you have a group of related utilities:

```
src/team-name/
├── team.py
├── tools.py
├── utils.py
└── telegram_utils.py    # New file for Telegram helpers
```

```python
# telegram_utils.py

def parse_telegram_update(data: dict) -> Message | None:
    """Parse incoming Telegram update."""
    ...

def format_for_telegram(text: str) -> str:
    """Format text for Telegram (escape markdown, etc)."""
    ...

def split_long_message(text: str, max_len: int = 4096) -> list[str]:
    """Split message if exceeds Telegram limit."""
    ...
```

---

#### Option C: Full client/integration (many operations)

When building a complete integration with an external service:

```
src/team-name/
├── team.py
├── tools.py
├── utils.py
└── integrations/
    └── telegram.py      # Full Telegram client
```

```python
# integrations/telegram.py

class TelegramClient:
    """Full Telegram integration client."""

    def __init__(self, token: str):
        self.bot = Bot(token)
        self.webhook_url = None

    # --- Sending ---
    async def send_message(self, chat_id: int, text: str) -> bool:
        ...

    async def send_photo(self, chat_id: int, photo_url: str) -> bool:
        ...

    # --- Receiving ---
    def parse_update(self, data: dict) -> Update:
        ...

    def setup_webhook(self, url: str) -> bool:
        ...

    # --- Utilities ---
    def format_message(self, text: str) -> str:
        ...
```

---

#### Decision Questions

Ask these to determine organization:

> "How many functions/methods will this need?"
> "Are they all related to one external service?"
> "Will we need to maintain state (API client, connection)?"
> "Is this a one-time helper or reusable across the codebase?"

| Answer | Organization |
|--------|--------------|
| 1-2 simple functions | Add to utils.py |
| 3+ related functions, no state | Own file |
| External service, needs state/config | Full client class |
| Reusable across multiple teams | `shared/` directory |

---

## Common Patterns

### Wrapper Pattern

Wrap external service with consistent interface:

```python
# utils.py or integrations/telegram.py

class TelegramClient:
    """Wrapper for Telegram Bot API."""

    def __init__(self, token: str):
        self.bot = Bot(token)

    async def send_message(self, chat_id: int, text: str) -> bool:
        """Send message, return success status."""
        try:
            await self.bot.send_message(chat_id=chat_id, text=text)
            return True
        except TelegramError as e:
            logger.error(f"Failed to send: {e}")
            return False

    def parse_update(self, data: dict) -> Message | None:
        """Parse incoming update, return Message or None."""
        # ... parsing logic
```

### Tool Calling Utility Pattern

When a tool needs helper functions:

```python
# tools.py
@tool
def get_youtube_summary(url: str) -> str:
    """Get summary of YouTube video."""
    video_id = extract_video_id(url)  # utility
    transcript = fetch_transcript(video_id)  # utility
    summary = summarize_text(transcript)  # utility (or another agent)
    return json.dumps({"summary": summary})

# utils.py
def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    # ... parsing logic

def fetch_transcript(video_id: str) -> str:
    """Fetch transcript from YouTube."""
    # ... API call
```

### Configuration Pattern

For utilities that need config:

```python
# utils.py
from functools import lru_cache
import os

@lru_cache
def get_telegram_client() -> TelegramClient:
    """Get configured Telegram client (singleton)."""
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    return TelegramClient(token)
```

---

## Spec Output

When using this skill, capture in the spec:

### For Tools

```markdown
#### Tool: [tool_name]

**Purpose:** [What it enables]
**Implementation:** MCP Server | API | SDK | Custom

| Field | Value |
|-------|-------|
| Documentation | [URL] |
| Package/API | [name] |
| Auth | [method] |

**Input:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| param1 | str | Yes | [description] |

**Output:** JSON with [fields]

**Errors:**
| Error | Handling |
|-------|----------|
| [type] | [how to handle] |
```

### For Utilities

```markdown
#### Utility: [function_name]

**Purpose:** [What it does]
**Location:** [where it goes]
**Used by:** [what calls it]

**Signature:**
```python
def function_name(param: type) -> return_type:
```

**Raises:** [exceptions if any]
```

---

## When to Ask for Clarification

**Ask when:**
- Unclear if this should be a tool or utility
- Multiple implementation approaches seem valid
- Error handling requirements unclear
- Unsure about input/output format

**Example:**
> "For Telegram message sending - should this be:
> A) A tool the agent calls when it wants to send a message
> B) A utility that's automatically called after agent generates response
>
> This affects whether the agent controls when messages are sent."

---

## References

- `agent-spec-builder/` — Uses this for new systems
- `agent-improvement-spec/` — Uses this for improvements
- `frameworks/langgraph/CHEATSHEET.md` — LangGraph tool patterns
