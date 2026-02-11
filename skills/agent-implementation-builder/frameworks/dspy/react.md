# DSPy ReAct Module Reference

**When to read this:** Before implementing any tool-using agent in DSPy.

This document covers `dspy.ReAct` — the Reasoning and Acting pattern for agents that dynamically decide which tools to call and when.

---

## Quick Reference

```python
# Basic ReAct setup
react = dspy.ReAct(
    signature=MySignature,       # Signature class or string shorthand
    tools=[tool_func1, tool_func2],  # List of callables or dspy.Tool objects
    max_iters=5                  # Max reasoning-action iterations (default: 20)
)
react.set_lm(shared_lm)         # Inject singleton LM

# Sync call
result = react(question="...")

# Async call
result = await react.acall(question="...")

# Access trajectory (reasoning + tool call history)
print(result.trajectory)
```

---

## When to Use ReAct vs Other Modules

| Scenario | Module | Why |
|----------|--------|-----|
| Agent dynamically chooses tools | `dspy.ReAct` | LLM reasons about which tools to call |
| Fixed/predictable tool sequence | `dspy.Predict` + explicit calls | More control, less overhead |
| No tools needed, simple extraction | `dspy.Predict` | Fastest, cheapest |
| No tools, needs visible reasoning | `dspy.ChainOfThought` | Adds reasoning trace |
| LLM decides params, you execute tools | Hybrid (Predict + manual calls) | Balance of flexibility and control |

**Decision guide:**
- If you know which tools to call at code-time → call tools explicitly in `aforward()`, use Predict/CoT for reasoning
- If the LLM should decide which tools to call → use ReAct
- If the agent needs multiple tool calls with reasoning between them → use ReAct

---

## API Reference

### Constructor

```python
dspy.ReAct(
    signature: type[dspy.Signature] | str,  # Input/output contract
    tools: list[Callable],                   # Tool functions or dspy.Tool objects
    max_iters: int = 20                      # Max reasoning-action iterations
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `signature` | `type[Signature]` or `str` | Required | Defines input/output fields. Can be a class or shorthand like `"question -> answer"` |
| `tools` | `list[Callable]` | Required | Functions the agent can call. Each must have docstrings and type hints. |
| `max_iters` | `int` | 20 | Safety limit on reasoning iterations. Agent stops here even if not done. |

### Methods

| Method | Description |
|--------|-------------|
| `react(...)` / `react.__call__(...)` | Synchronous execution |
| `await react.acall(...)` | Async execution (use with async tools) |
| `react.set_lm(lm)` | Set the LM instance (returns `self` for chaining) |

### Output

```python
result = react(question="...")
result.answer        # Output field from signature
result.trajectory    # List of reasoning steps + tool calls
```

The `trajectory` contains the full history: Thought → Tool Selection → Arguments → Observation for each iteration.

---

## Tool Function Format

Tools are plain Python functions with **docstrings** and **type hints**. DSPy extracts the schema automatically.

### Basic Tool

```python
def search_social_media(query: str, max_results: int = 20) -> str:
    """
    Search social media posts matching a query.

    Args:
        query: Search terms to find relevant posts
        max_results: Maximum number of results to return

    Returns:
        JSON string of matching posts with content and metadata
    """
    # Your implementation here
    client = ApifyClient(token=os.getenv("APIFY_API_TOKEN"))
    run = client.actor(actor_id).call(run_input={"searchTerms": [query], "maxResults": max_results})
    items = client.dataset(run["defaultDatasetId"]).list_items().items
    return json.dumps(items)
```

**Requirements:**
- Type hints on all parameters (required for schema extraction)
- Docstring describing what the tool does (the LLM reads this to decide when to use it)
- Return a string (the observation the LLM sees)

### Async Tool

```python
async def async_search(query: str) -> str:
    """Search the web asynchronously."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/search?q={query}")
        return response.text
```

Async tools work with `acall()`. Use async tools for I/O-bound operations (API calls, database queries).

### Wrapping with dspy.Tool (Optional)

Use `dspy.Tool` when you need custom metadata beyond what docstrings provide:

```python
api_tool = dspy.Tool(
    func=search_social_media,
    name="social_search",                    # Custom name (default: function name)
    desc="Search social media for posts",    # Custom description (default: docstring)
    arg_desc={                               # Custom arg descriptions
        "query": "Keywords to search for",
        "max_results": "Max items to return (default: 20)"
    }
)

react = dspy.ReAct(signature=MySignature, tools=[api_tool], max_iters=5)
```

---

## max_iters Configuration

`max_iters` controls how many reasoning-action cycles the agent can perform.

| Use Case | Recommended max_iters | Reasoning |
|----------|----------------------|-----------|
| Simple single-tool lookup | 3-5 | One tool call + verify |
| Multi-step research | 5-10 | Multiple searches, refinement |
| Complex agentic workflows | 10-15 | Extended reasoning chains |
| Default (if unsure) | 5 | Conservative, prevents cost runaway |

**Cost consideration:** Each iteration is an LLM call. For agents that run in parallel (e.g., 5 search agents), keep `max_iters` low (3-5) to control costs.

**What happens at max_iters:** The agent stops and returns whatever it has. It does NOT raise an error — it returns a best-effort result.

---

## ReAct with Singleton LM

ReAct inherits from `dspy.Module`, so the singleton LM pattern applies:

```python
# In utils.py
_shared_lm = None

def get_shared_lm():
    global _shared_lm
    if _shared_lm is None:
        _shared_lm = dspy.LM(
            "gemini/gemini-2.5-flash",
            api_key=os.getenv("GOOGLE_API_KEY"),
            max_parallel_requests=2000,
            timeout=120,
        )
    return _shared_lm


# In team.py
class SearchTeam(dspy.Module):
    def __init__(self, shared_lm):
        if shared_lm is None:
            raise ValueError("shared_lm required")

        self.lm = shared_lm

        # ReAct agent with tools
        self.search_agent = dspy.ReAct(
            signature=SearchSignature,
            tools=[search_social_media],
            max_iters=5
        )
        self.search_agent.set_lm(self.lm)  # Singleton LM

        # Analysis agent (no tools)
        self.analyzer = dspy.Predict(AnalysisSignature)
        self.analyzer.set_lm(self.lm)
```

---

## Complete Example: Search Agent with Apify Tool

This example shows a search agent that uses an Apify actor as a tool via the ReAct pattern:

```python
import os
import json
import dspy
from apify_client import ApifyClient


# =============================================================================
# TOOL DEFINITION
# =============================================================================

def search_apify_actor(
    search_terms: str,
    max_results: int = 20,
    date_range: str = "past_week"
) -> str:
    """
    Search social media posts using an Apify actor.

    Use this tool to fetch posts matching specific keywords.
    You can adjust search_terms based on what you're looking for,
    increase max_results if you need more data, or change date_range
    to broaden the time window.

    Args:
        search_terms: Comma-separated keywords to search for
        max_results: Maximum number of posts to return (default: 20, max: 50)
        date_range: Time filter - one of: past_day, past_week, past_month

    Returns:
        JSON string containing matching posts with content, author, date, and metrics
    """
    try:
        client = ApifyClient(token=os.getenv("APIFY_API_TOKEN"))
        terms = [t.strip() for t in search_terms.split(",")]

        run = client.actor("curious_coder/linkedin-post-search-scraper").call(
            run_input={
                "searchTerms": terms,
                "maxResults": min(max_results, 50),
                "dateRange": date_range,
            }
        )

        items = client.dataset(run["defaultDatasetId"]).list_items().items
        return json.dumps(items[:max_results], default=str)

    except Exception as e:
        return json.dumps({"error": str(e), "search_terms": search_terms})


# =============================================================================
# SIGNATURE
# =============================================================================

class SearchSignature(dspy.Signature):
    """
    Search for relevant social media content using available tools.

    === YOUR ROLE ===
    You are a Search Agent. Your job is to find relevant social media posts
    by strategically choosing search terms and parameters.

    === STRATEGY ===
    1. Analyze the entity profile and content pillars to craft targeted search terms
    2. Call the search tool with appropriate parameters
    3. If results are thin, try different keyword variations or broader date ranges
    4. If previous feedback is provided, adapt your strategy accordingly

    === CONSTRAINTS ===
    - Keep max_results at 20 unless you need more
    - Prefer specific, targeted searches over broad generic ones
    - Do not exceed 3 tool calls per invocation
    """

    entity_context: str = dspy.InputField(desc="Entity profile and content pillars")
    search_config: str = dspy.InputField(desc="Suggested keywords and date range")
    previous_feedback: str = dspy.InputField(
        desc="Optional feedback from prior search iteration. Empty if first attempt.",
        default=""
    )

    raw_results: str = dspy.OutputField(desc="JSON string of search results")
    search_queries_used: str = dspy.OutputField(desc="Comma-separated list of all search terms used")
    result_count: int = dspy.OutputField(desc="Total number of results found")


# =============================================================================
# AGENT MODULE
# =============================================================================

class SearchAgent(dspy.Module):
    def __init__(self, shared_lm):
        if shared_lm is None:
            raise ValueError("shared_lm required")

        self.react = dspy.ReAct(
            signature=SearchSignature,
            tools=[search_apify_actor],
            max_iters=5  # Conservative: each iter costs an Apify call
        )
        self.react.set_lm(shared_lm)

    async def aforward(self, entity_context: str, search_config: str,
                       previous_feedback: str = "") -> dspy.Prediction:
        return await self.react.acall(
            entity_context=entity_context,
            search_config=search_config,
            previous_feedback=previous_feedback,
        )
```

---

## Anti-Patterns

### DO NOT: Use ReAct for fixed tool sequences

```python
# WRONG: Tool sequence is predictable — ReAct adds unnecessary overhead
react = dspy.ReAct(
    signature="text -> summary",
    tools=[fetch_url, extract_text],  # Always fetch then extract
    max_iters=10
)
```

**Instead:** Call tools explicitly in `aforward()` and use Predict/CoT for reasoning.

### DO NOT: Set max_iters too high for costly tools

```python
# WRONG: Each iteration calls an expensive API
react = dspy.ReAct(
    signature=SearchSignature,
    tools=[apify_search],
    max_iters=20  # 20 Apify calls = expensive
)
```

**Instead:** Use `max_iters=3-5` for tools that cost money or take time.

### DO NOT: Skip docstrings on tool functions

```python
# WRONG: No docstring — LLM can't understand what the tool does
def search(q: str) -> str:
    return api.search(q)
```

**Instead:** Write clear docstrings explaining what the tool does, when to use it, and what it returns.

---

## Related Documentation

- [Tool Agent Pattern](../../../individual-agents/dspy/tool-agent.md) — Full implementation guide for tool-using agents
- [DSPy Cheatsheet](CHEATSHEET.md) — Critical rules and patterns
- [Async Patterns](async-patterns.md) — Running multiple ReAct agents in parallel
