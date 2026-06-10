# Tool Agent (dspy.ReAct)

## What It Is

An agent that can reason about and invoke external tools to gather information or take actions. Implements the Reasoning and Acting (ReAct) pattern where the agent iteratively reasons about the situation, decides whether to call a tool, processes results, and continues until it can provide a final answer.

> **Note:** You don't *have* to use ReAct to use tools in DSPy. ReAct is for when you want the **LLM to dynamically decide** which tools to call and when. If your tool sequence is fixed or predictable, you can call tools explicitly in your module's `forward()` method. See [Alternatives to ReAct](#alternatives-to-react) at the end of this document.

## When to Use

- Agent needs to fetch external data (APIs, databases, search)
- Agent needs to perform actions (send email, create record, execute code)
- Tasks requiring information not available in the prompt
- Multi-step workflows that combine reasoning with tool execution
- When you need the agent to dynamically decide what tools to use

## When to Avoid

- All information is in the prompt — use **Basic Agent** (Predict) instead
- No external actions needed — use **Basic Agent** or **Reasoning Agent** instead
- Simple extraction/classification — use **Basic Agent** instead
- Predictable tool sequence — consider explicit orchestration instead of ReAct

## ReAct vs ChainOfThought + Manual Tool Handling

> **This is a critical performance decision.** ReAct makes 5+ LLM calls per invocation (150-300s with Gemini). ChainOfThought + manual tool handling makes 1 LLM call + tool execution (20-40s). Default to ChainOfThought + manual tool handling for single-tool agents.

| Scenario | Approach | Why |
|----------|----------|-----|
| Single tool, predictable use | ChainOfThought + ToolCalls | 1 LLM call, you execute the tool |
| Multiple tools, dynamic selection | ReAct | LLM reasons about which tools to call |
| Multi-step tool chains with reasoning between steps | ReAct | LLM needs to reason about intermediate results |
| Known tool sequence | Explicit orchestration in `aforward()` | No LLM overhead for tool selection |

### Preferred: ChainOfThought + Manual Tool Handling (Single-Tool Agents)

```python
import dspy

class SearchSignature(dspy.Signature):
    """Analyze the entity and decide search parameters."""
    entity_context: str = dspy.InputField()
    search_config: str = dspy.InputField()

    tool_calls: dspy.ToolCalls = dspy.OutputField()
    search_reasoning: str = dspy.OutputField(desc="Why these search terms")

class SingleToolAgent(dspy.Module):
    def __init__(self, shared_lm, search_fn):
        if shared_lm is None:
            raise ValueError("shared_lm required")

        self.tools = {"search": dspy.Tool(search_fn)}
        self.planner = dspy.ChainOfThought(SearchSignature)
        self.planner.set_lm(shared_lm)

    async def aforward(self, entity_context: str, search_config: str) -> dspy.Prediction:
        # 1 LLM call: reason + decide tool params
        plan = await self.planner.acall(
            entity_context=entity_context,
            search_config=search_config,
        )

        # Execute tool directly (no LLM overhead)
        results = []
        for call in plan.tool_calls.tool_calls:
            result = call.execute(functions=self.tools)
            results.append(result)

        return dspy.Prediction(
            raw_results=results,
            search_reasoning=plan.search_reasoning,
        )
```

## Selection Criteria

- If all info is in the prompt → **Basic Agent**
- If you need visible reasoning but no tools → **Reasoning Agent**
- If agent needs external data or actions → **Tool Agent**
- If building conversation flow → **Conversational Agent**
- If tool sequence is fixed → consider Pipeline pattern instead

## Inputs / Outputs

**Inputs:**
- Input fields defined in the Signature
- List of tool functions or `dspy.Tool` objects
- `max_iters` parameter to limit reasoning iterations

**Outputs:**
- Output fields defined in the Signature
- `trajectory` containing the full reasoning and tool call history

> **Structured Output Rule:** Use typed DSPy output fields (`bool`, `int`, `list[str]`, `dict[str, Any]`) or Pydantic `BaseModel`/`RootModel` as OutputField types. NEVER use `str` fields with JSON parsing instructions. See `frameworks/dspy/CHEATSHEET.md` Critical Rules.

## Prompting Guidelines

For ReAct agents:

- Clearly describe what each tool does in its docstring
- Use descriptive parameter names with type hints
- Specify when tools should (and shouldn't) be used
- Set appropriate `max_iters` to prevent runaway loops
- Consider what happens if tools fail or return unexpected results

---

## DSPy Implementation

### Basic Tool Definition

```python
import dspy

# Tools are just Python functions with docstrings and type hints
def search_web(query: str) -> str:
    """
    Search the web for information.

    Args:
        query: Search query string

    Returns:
        Search results as a string
    """
    # Your search implementation
    return f"Search results for '{query}': ..."


def get_weather(city: str) -> str:
    """
    Get current weather for a city.

    Args:
        city: City name

    Returns:
        Weather information
    """
    # Your weather API call
    return f"Weather in {city}: Sunny, 72°F"


def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression.

    Args:
        expression: Math expression to evaluate (e.g., "2 + 2 * 3")

    Returns:
        Result of the calculation
    """
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {e}"
```

### Basic ReAct Agent

```python
import os
import dspy

# ============================================
# SINGLETON LM PATTERN (CRITICAL)
# ============================================
_shared_lm = None

def get_shared_lm():
    global _shared_lm
    if _shared_lm is None:
        _shared_lm = dspy.LM(
            os.getenv("MODEL_NAME", "openai/gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
            max_parallel_requests=2000,
            timeout=120,
        )
    return _shared_lm


# ============================================
# BASIC REACT AGENT
# ============================================
class ResearchAgent(dspy.Module):
    """
    Tool-using agent that can search and calculate.
    """

    def __init__(self, shared_lm):
        if shared_lm is None:
            raise ValueError("shared_lm required")

        self.lm = shared_lm

        # Define tools
        self.tools = [search_web, get_weather, calculator]

        # Create ReAct agent with signature and tools
        self.react = dspy.ReAct(
            signature="question -> answer",
            tools=self.tools,
            max_iters=5  # Limit iterations to prevent runaway
        )

        # Inject singleton LM
        self.react.set_lm(self.lm)

    def forward(self, question: str) -> dspy.Prediction:
        """Synchronous forward pass."""
        result = self.react(question=question)
        return result

    async def aforward(self, question: str) -> dspy.Prediction:
        """Async forward pass for concurrent workflows."""
        result = await self.react.acall(question=question)
        return result


# ============================================
# USAGE
# ============================================
async def main():
    lm = get_shared_lm()
    agent = ResearchAgent(shared_lm=lm)

    result = await agent.aforward(
        question="What is the weather in Tokyo and what is 25 * 17?"
    )

    print(f"Answer: {result.answer}")
    print(f"\nTrajectory:")
    for step in result.trajectory:
        print(f"  {step}")
```

### Custom Signature with ReAct

```python
import dspy
from typing import List

class ResearchSignature(dspy.Signature):
    """
    Research a topic using available tools and provide a comprehensive answer.

    === AVAILABLE TOOLS ===
    - search_web: Search for information online
    - get_company_info: Look up company details
    - calculator: Perform calculations

    === INSTRUCTIONS ===
    1. Break down the question into sub-questions if needed
    2. Use tools to gather relevant information
    3. Synthesize findings into a coherent answer
    4. Cite which tools provided which information

    === QUALITY STANDARDS ===
    - Only state facts you can verify through tools
    - If tools don't return useful info, say so
    - Provide specific, actionable answers
    """

    question: str = dspy.InputField(description="Research question")
    context: str = dspy.InputField(description="Additional context if available")

    answer: str = dspy.OutputField(description="Comprehensive answer")
    sources: List[str] = dspy.OutputField(description="Tools used and what they provided")
    confidence: str = dspy.OutputField(description="How confident: high/medium/low")


class AdvancedResearchAgent(dspy.Module):
    """ReAct agent with custom signature."""

    def __init__(self, shared_lm, tools: list):
        if shared_lm is None:
            raise ValueError("shared_lm required")

        self.lm = shared_lm

        # Create ReAct with custom signature
        self.react = dspy.ReAct(
            signature=ResearchSignature,
            tools=tools,
            max_iters=10
        )

        self.react.set_lm(self.lm)

    async def aforward(self, question: str, context: str = "") -> dspy.Prediction:
        result = await self.react.acall(
            question=question,
            context=context
        )
        return result
```

### Async Tools

```python
import asyncio
import dspy

async def async_search(query: str) -> str:
    """
    Search the web asynchronously.

    Args:
        query: Search query

    Returns:
        Search results
    """
    # Simulate async API call
    await asyncio.sleep(0.1)
    return f"Async results for '{query}': ..."


async def async_database_query(sql: str) -> str:
    """
    Query the database asynchronously.

    Args:
        sql: SQL query to execute

    Returns:
        Query results
    """
    await asyncio.sleep(0.1)
    return f"Database results: [...]"


class AsyncToolAgent(dspy.Module):
    """Agent with async tools."""

    def __init__(self, shared_lm):
        if shared_lm is None:
            raise ValueError("shared_lm required")

        self.lm = shared_lm

        # Async tools work with acall()
        self.react = dspy.ReAct(
            signature="question -> answer",
            tools=[async_search, async_database_query],
            max_iters=5
        )

        self.react.set_lm(self.lm)

    async def aforward(self, question: str) -> dspy.Prediction:
        # MUST use acall() with async tools
        result = await self.react.acall(question=question)
        return result
```

### MCP Tool Integration

DSPy supports Model Context Protocol (MCP) for standardized tool ecosystems.

```python
import asyncio
import dspy
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def create_mcp_agent(shared_lm, server_command: str, server_args: list):
    """
    Create a ReAct agent with MCP tools.

    Args:
        shared_lm: Singleton LM instance
        server_command: Command to start MCP server (e.g., "python")
        server_args: Arguments for the server (e.g., ["mcp_server.py"])

    Returns:
        Configured ReAct agent
    """
    # Configure stdio server
    server_params = StdioServerParameters(
        command=server_command,
        args=server_args,
        env=None
    )

    # Connect to MCP server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize session
            await session.initialize()

            # List and convert tools
            response = await session.list_tools()
            dspy_tools = [
                dspy.Tool.from_mcp_tool(session, tool)
                for tool in response.tools
            ]

            # Create ReAct agent with MCP tools
            react = dspy.ReAct(
                signature="task -> result",
                tools=dspy_tools,
                max_iters=5
            )

            react.set_lm(shared_lm)

            return react


# Usage example
async def main():
    lm = get_shared_lm()

    # Create agent with MCP tools from a local server
    agent = await create_mcp_agent(
        shared_lm=lm,
        server_command="python",
        server_args=["path/to/mcp_server.py"]
    )

    result = await agent.acall(task="Look up the latest sales figures")
    print(result.result)
```

### Using dspy.Tool for Explicit Metadata

```python
import dspy

def complex_api_call(
    endpoint: str,
    method: str = "GET",
    params: dict = None
) -> str:
    """Make an API call."""
    # Implementation
    pass


# Create tool with explicit metadata
api_tool = dspy.Tool(
    complex_api_call,
    name="api_request",
    desc="Make HTTP requests to external APIs. Use for fetching data from services.",
    arg_desc={
        "endpoint": "Full URL of the API endpoint",
        "method": "HTTP method: GET, POST, PUT, DELETE",
        "params": "Optional dictionary of query parameters"
    }
)

# Use in ReAct
react = dspy.ReAct(
    signature="task -> result",
    tools=[api_tool],
    max_iters=5
)
```

### Manual Tool Handling (Advanced)

For fine-grained control over tool execution:

```python
import dspy

class ManualToolSignature(dspy.Signature):
    """Decide which tools to call."""
    question: str = dspy.InputField()
    tools: list[dspy.Tool] = dspy.InputField()
    tool_calls: dspy.ToolCalls = dspy.OutputField()


class ManualToolAgent(dspy.Module):
    """Agent with manual tool execution control."""

    def __init__(self, shared_lm, tools: list):
        if shared_lm is None:
            raise ValueError("shared_lm required")

        self.lm = shared_lm
        self.tools = {t.name: dspy.Tool(t) for t in tools}

        self.planner = dspy.Predict(ManualToolSignature)
        self.planner.set_lm(self.lm)

    async def aforward(self, question: str) -> dspy.Prediction:
        # Get tool call decisions
        response = await self.planner.acall(
            question=question,
            tools=list(self.tools.values())
        )

        # Execute tools manually with custom logic
        results = []
        for call in response.tool_calls.tool_calls:
            try:
                # Custom validation before execution
                if self._is_safe_call(call):
                    result = call.execute(functions=self.tools)
                    results.append({"tool": call.name, "result": result})
                else:
                    results.append({"tool": call.name, "error": "Blocked by safety check"})
            except Exception as e:
                results.append({"tool": call.name, "error": str(e)})

        return dspy.Prediction(
            tool_results=results,
            raw_calls=response.tool_calls
        )

    def _is_safe_call(self, call) -> bool:
        """Custom safety validation for tool calls."""
        # Your safety logic here
        return True
```

### DSPy-Specific Notes

- **Tools are functions:** Define tools as regular Python functions with docstrings and type hints.
- **Automatic schema extraction:** DSPy extracts tool schemas from docstrings and type hints automatically.
- **max_iters is critical:** Set a reasonable limit to prevent infinite loops. 5-10 is typical.
- **Use acall() for async:** When tools are async, you MUST use `acall()` not `__call__()`.
- **Trajectory for debugging:** Access `result.trajectory` to see the full reasoning and tool call sequence.
- **MCP integration:** Use `dspy.Tool.from_mcp_tool()` for MCP-compatible tool servers.

---

## Pitfalls & Best Practices

**Pitfalls:**

- **No max_iters limit** — Without a limit, the agent can loop indefinitely. Always set `max_iters`.

- **Poor tool descriptions** — The agent relies on docstrings to understand tools. Vague descriptions lead to wrong tool choices.

- **Missing type hints** — Without type hints, the agent doesn't know parameter types, causing errors.

- **Sync tools with acall()** — If tools are sync but you use `acall()`, it works but blocks. Use async tools for true concurrency.

- **Tool errors crashing workflow** — Tools can fail. Consider error handling in your tools or the manual approach.

**Best Practices:**

- **Clear tool docstrings** — Describe what the tool does, when to use it, and what it returns.

- **Reasonable max_iters** — Start with 5, increase if needed. Monitor trajectory to tune.

- **Log trajectories** — Store trajectories for debugging and understanding agent behavior.

- **Use async tools** — For I/O-bound operations, async tools improve throughput.

- **Consider manual control** — For production systems, manual tool handling gives you validation and error recovery.

- **Test edge cases** — What happens when tools return errors? Empty results? Unexpected formats?

---

## Comparison: Tool Agent vs Other Patterns

| Aspect | Basic Agent | Reasoning Agent | Tool Agent |
|--------|-------------|-----------------|------------|
| External data | No | No | Yes |
| Reasoning trace | No | Yes | Yes (in trajectory) |
| Iterations | 1 | 1 | Multiple |
| Latency | Lowest | Medium | Highest |
| Use case | Extraction | Complex reasoning | External actions |

### When to Use ReAct vs Explicit Orchestration

| Scenario | Approach |
|----------|----------|
| Dynamic tool selection | ReAct — agent decides which tools |
| Fixed tool sequence | Pipeline — explicit orchestration |
| Uncertain number of tool calls | ReAct — agent decides when done |
| Known number of tool calls | Explicit — more predictable |
| Complex reasoning about tools | ReAct — leverages LLM reasoning |
| Simple tool wiring | Explicit — less overhead |

---

## ReAct vs Other DSPy Modules

| Module | Tools | Reasoning | LLM Calls | Use Case |
|--------|-------|-----------|-----------|----------|
| `Predict` | No | No | 1 | Direct mapping |
| `ChainOfThought` | No | Yes | 1 | Complex reasoning |
| `ChainOfThought` + `ToolCalls` | Yes (manual) | Yes | 1 + tool exec | Single-tool agents (preferred) |
| `ReAct` | Yes (automatic) | Yes | 5+ | Multi-tool dynamic selection |
| `ProgramOfThought` | Code execution | Yes | 1+ | Math/computation |

---

---

## Alternatives to ReAct

You don't always need ReAct to use tools. Here are other approaches:

### Explicit Tool Calls in Orchestration

If you know which tools to call and when, just call them in your module:

```python
import dspy

class ExplicitToolAgent(dspy.Module):
    """
    Agent that calls tools explicitly (not LLM-driven).

    Use this when the tool sequence is predictable.
    """

    def __init__(self, shared_lm):
        if shared_lm is None:
            raise ValueError("shared_lm required")

        self.lm = shared_lm

        # DSPy modules for reasoning
        self.planner = dspy.Predict(PlannerSignature)
        self.synthesizer = dspy.ChainOfThought(SynthesizerSignature)

        self.planner.set_lm(self.lm)
        self.synthesizer.set_lm(self.lm)

    async def aforward(self, question: str) -> dspy.Prediction:
        # Step 1: Plan (LLM decides what to search)
        plan = await self.planner.acall(question=question)

        # Step 2: Execute tools explicitly (NOT LLM-driven)
        search_results = await self.search_api(plan.search_query)
        db_results = await self.query_database(plan.db_query)

        # Step 3: Synthesize results (LLM)
        answer = await self.synthesizer.acall(
            question=question,
            search_results=search_results,
            db_results=db_results
        )

        return answer

    async def search_api(self, query: str) -> str:
        """Call search API directly."""
        # Your API call here
        return f"Search results for: {query}"

    async def query_database(self, query: str) -> str:
        """Query database directly."""
        # Your DB query here
        return f"Database results for: {query}"
```

**When to use explicit orchestration:**
- Tool sequence is fixed (always search, then query DB, then synthesize)
- You want full control over error handling per tool
- Performance matters (no reasoning overhead for tool selection)
- Tools have side effects you want to control carefully

### LLM Decides Tool Parameters, You Execute

A hybrid approach where the LLM decides *what* to do but you control *how*:

```python
class HybridToolAgent(dspy.Module):
    """LLM decides parameters, you execute tools."""

    def __init__(self, shared_lm):
        self.lm = shared_lm

        # LLM decides what to search/query
        self.decider = dspy.Predict(
            "question -> search_query, db_table, db_filter"
        )
        self.decider.set_lm(self.lm)

        # LLM synthesizes results
        self.synthesizer = dspy.ChainOfThought(
            "question, tool_results -> answer"
        )
        self.synthesizer.set_lm(self.lm)

    async def aforward(self, question: str) -> dspy.Prediction:
        # LLM decides parameters
        decision = await self.decider.acall(question=question)

        # You execute with validation
        tool_results = []

        if self._is_valid_query(decision.search_query):
            search_result = await self._safe_search(decision.search_query)
            tool_results.append(f"Search: {search_result}")

        if decision.db_table in self.ALLOWED_TABLES:
            db_result = await self._safe_db_query(
                decision.db_table,
                decision.db_filter
            )
            tool_results.append(f"Database: {db_result}")

        # LLM synthesizes
        return await self.synthesizer.acall(
            question=question,
            tool_results="\n".join(tool_results)
        )

    def _is_valid_query(self, query: str) -> bool:
        """Validate search query before execution."""
        return len(query) > 0 and len(query) < 500

    ALLOWED_TABLES = ["products", "customers", "orders"]
```

### When to Use Each Approach

| Approach | LLM Decides Tools | LLM Decides Params | You Control Execution |
|----------|-------------------|--------------------|-----------------------|
| **ReAct** | Yes | Yes | No (automatic) |
| **Explicit** | No | Maybe | Yes |
| **Hybrid** | No | Yes | Yes |

**Choose ReAct when:**
- You don't know which tools will be needed upfront
- The agent should reason about tool results before deciding next steps
- You want the LLM to handle the complexity

**Choose Explicit when:**
- Tool sequence is predictable
- You need fine-grained error handling
- Performance is critical
- Tools have dangerous side effects

**Choose Hybrid when:**
- LLM should decide *what* to do but not *how*
- You want validation before tool execution
- You need a balance of flexibility and control

---

## Source Reference

**Based on:** DSPy official documentation and community patterns.

Key references:
- DSPy ReAct API: https://dspy.ai/api/modules/ReAct/
- DSPy Tool integration: https://dspy.ai/learn/programming/tools/
- DSPy MCP integration: https://dspy.ai/learn/programming/mcp/
