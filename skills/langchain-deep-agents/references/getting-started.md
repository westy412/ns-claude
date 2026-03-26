# LangChain Deep Agents SDK -- Getting Started Reference

## Installation

```bash
pip install deepagents
# or
uv add deepagents
```

---

## Creating Your First Agent

The primary entry point is `create_deep_agent`, which returns a compiled LangGraph `CompiledStateGraph`.

```python
from deepagents import create_deep_agent

agent = create_deep_agent()
result = agent.invoke({"messages": [{"role": "user", "content": "Research LangGraph and write a summary"}]})
print(result["messages"][-1].content)
```

---

## `create_deep_agent` Full API Signature

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model: str | BaseChatModel | None = None,
    tools: Sequence[BaseTool | Callable | dict] | None = None,
    *,
    system_prompt: str | SystemMessage | None = None,
    middleware: Sequence[AgentMiddleware] = (),
    subagents: list[SubAgent | CompiledSubAgent] | None = None,
    skills: list[str] | None = None,
    memory: list[str] | None = None,
    response_format: ResponseFormat | None = None,
    context_schema: type[Any] | None = None,
    checkpointer: Checkpointer | None = None,
    store: BaseStore | None = None,
    backend: BackendProtocol | BackendFactory | None = None,
    interrupt_on: dict[str, bool | InterruptOnConfig] | None = None,
    debug: bool = False,
    name: str | None = None,
    cache: BaseCache | None = None,
) -> CompiledStateGraph
```

## Parameter Guide

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `model` | `str \| BaseChatModel` | `claude-sonnet-4-5-20250929` | LLM to use (must support tool calling) |
| `tools` | `Sequence[...]` | `[]` | Custom tools added to built-in tools |
| `system_prompt` | `str \| SystemMessage` | `None` | Prepended to BASE_AGENT_PROMPT |
| `middleware` | `Sequence[AgentMiddleware]` | `()` | Custom middleware added after defaults |
| `subagents` | `list[SubAgent \| CompiledSubAgent]` | `None` | Specialized agents for delegation |
| `skills` | `list[str]` | `None` | Filesystem paths to skill directories |
| `memory` | `list[str]` | `None` | Filesystem paths to memory files |
| `checkpointer` | `Checkpointer` | `None` | State persistence (required for HITL) |
| `store` | `BaseStore` | `None` | Cross-thread persistent storage |
| `backend` | `BackendProtocol \| BackendFactory` | `StateBackend` | Filesystem operation backend |
| `interrupt_on` | `dict[str, ...]` | `None` | Per-tool HITL approval config |
| `debug` | `bool` | `False` | Enable debug logging |
| `name` | `str` | `None` | Agent name for observability |

---

## Model Configuration

**Default model:** `claude-sonnet-4-5-20250929`. Use `provider:model` format to switch.

```python
# Anthropic (default)
agent = create_deep_agent(model="claude-sonnet-4-5-20250929")

# OpenAI
agent = create_deep_agent(model="openai:gpt-5.2")

# Google Generative AI
agent = create_deep_agent(model="google_genai:gemini-2.5-flash-lite")

# Azure OpenAI
agent = create_deep_agent(model="azure_openai:gpt-4.1")

# AWS Bedrock
agent = create_deep_agent(
    model="anthropic.claude-3-5-sonnet-20240620-v1:0",
    model_provider="bedrock_converse"
)

# HuggingFace
agent = create_deep_agent(
    model="microsoft/Phi-3-mini-4k-instruct",
    model_provider="huggingface",
    temperature=0.7,
    max_tokens=1024
)
```

### Using `init_chat_model` for Fine-Grained Control

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-5", temperature=0.5)
agent = create_deep_agent(model=model)
```

**Critical:** Deep agents require an LLM that supports tool calling. Models without tool-calling support will fail.

---

## Adding Custom Tools

Pass plain Python callables with docstrings and type hints -- they are auto-converted to tools.

```python
import os
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query, max_results=max_results,
        include_raw_content=include_raw_content, topic=topic
    )

agent = create_deep_agent(tools=[internet_search])
```

> **Tip:** Document custom tools in the system prompt too -- the agent performs better when it knows when and how to use each tool.

---

## System Prompts

Deep agents have a built-in system prompt covering planning, file system tools, and subagents. Custom system prompts **prepend** to this -- they do not replace it.

```python
# GOOD: Focus on domain-specific behavior
agent = create_deep_agent(
    system_prompt=(
        "You are a financial research analyst. "
        "When researching companies, always check SEC filings first. "
        "Write structured reports with sections: Overview, Financials, Risks."
    ),
)

# BAD: Duplicating built-in instructions
agent = create_deep_agent(
    system_prompt=(
        "You have access to a filesystem. Use write_file to save files. "
        "You can create todos with write_todos..."  # Already in BASE_AGENT_PROMPT
    ),
)
```

---

## Built-in Tools

Every deep agent automatically has these tools (do not pass them in `tools`):

| Tool | Category | Purpose |
|------|----------|---------|
| `write_todos` | Planning | Task planning and decomposition |
| `ls` | File System | List directory contents |
| `read_file` | File System | Read a file |
| `write_file` | File System | Write content to a file |
| `edit_file` | File System | Edit an existing file |
| `glob` | File System | Pattern-based file search |
| `grep` | File System | Content search across files |
| `execute` | Shell | Run shell commands (sandboxed) |
| `task` | Orchestration | Spawn a subagent for a delegated subtask |

---

## Invocation Patterns

```python
# Synchronous
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Analyze this dataset"}]},
    config={"configurable": {"thread_id": "thread-123"}}
)

# Streaming (recommended for long-running tasks)
for event in agent.stream(
    {"messages": [{"role": "user", "content": "Write a research report"}]},
    config={"configurable": {"thread_id": "thread-123"}},
    stream_mode="updates",
):
    print(event)

# Async
result = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "Research competitors"}]},
    config={"configurable": {"thread_id": "thread-123"}}
)
```

## Async Usage

> **Important**: `async_create_deep_agent` does **not exist** in deepagents 0.4.x.
> `create_deep_agent` is **synchronous** and returns a `CompiledStateGraph`.
> The returned graph supports async invocation via `ainvoke` and `astream`.

```python
from deepagents import create_deep_agent

# create_deep_agent is SYNCHRONOUS — no await needed
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[search_web],
)

# But the returned graph supports async invocation
result = await agent.ainvoke({"messages": [...]})

# And async streaming
async for event in agent.astream({"messages": [...]}, stream_mode="updates"):
    process(event)
```

---

## How It Works

When invoked, a deep agent follows this autonomous loop:

1. **Plans** using `write_todos` to decompose the task
2. **Calls tools** to gather information
3. **Manages context** using file system tools to persist intermediate results
4. **Spawns subagents** via `task` when subtasks benefit from dedicated focus
5. **Synthesizes a final response**

---

## Production Example

```python
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.checkpoint.postgres import PostgresSaver

@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    return "search results..."

agent = create_deep_agent(
    model=init_chat_model("anthropic:claude-sonnet-4-20250514"),
    tools=[search_web],
    system_prompt=(
        "You are an expert research assistant. "
        "Always write findings to the filesystem and create a structured report."
    ),
    checkpointer=PostgresSaver.from_conn_string("postgresql://..."),
    name="research-agent",
    debug=False,
)
```

---

## Default Middleware Stack (Verified: deepagents 0.4.1)

When you call `create_deep_agent()`, the following middleware is automatically attached:

1. **FilesystemMiddleware** (`deepagents.middleware.filesystem`) - File operations
2. **SubAgentMiddleware** (`deepagents.middleware.subagents`) - Sub-agent delegation via `task` tool
3. **SummarizationMiddleware** (`deepagents.middleware.summarization`) - Context compression for long conversations
4. **MemoryMiddleware** (`deepagents.middleware.memory`) - Memory file management
5. **PatchToolCallsMiddleware** (`deepagents.middleware.patch_tool_calls`) - Fixes interrupted tool call history

Conditionally added:
- **SkillsMiddleware** (`deepagents.middleware.skills`) - When `skills` argument is provided

> **Note**: `TodoListMiddleware`, `HumanInTheLoopMiddleware`, and `LLMToolSelectorMiddleware` do **not exist** in deepagents 0.4.x.

---

## Deep Agents CLI

Try Deep Agents from the terminal:

```bash
uv tool install deepagents-cli
deepagents
```

The CLI adds conversation resume, web search, remote sandboxes, persistent memory, custom skills, and human-in-the-loop approval.

---

## Environment Variables

| Variable | When Needed |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic models (default) |
| `OPENAI_API_KEY` | OpenAI models |
| `TAVILY_API_KEY` | Tavily search |
| `GOOGLE_API_KEY` | Google GenAI models |
| `AZURE_OPENAI_*` | Azure OpenAI models |

---

## Anti-Patterns

```python
# WRONG: No thread_id in config
result = agent.invoke({"messages": [...]})  # No persistence across turns

# WRONG: Recreating agent per request
def handle_request(message):
    agent = create_deep_agent(...)  # Expensive! Create once, reuse
    return agent.invoke({"messages": [message]})

# WRONG: Using invoke for long-running tasks
result = agent.invoke(...)  # Blocks until complete, no visibility

# CORRECT: Stream for long tasks
for event in agent.stream(..., stream_mode="updates"):
    process(event)

# NOTE: create_deep_agent is SYNCHRONOUS but returns a graph that supports async
agent = create_deep_agent(...)  # Sync creation
result = await agent.ainvoke(...)  # Async invocation works fine
async for event in agent.astream(...):  # Async streaming works fine
    process(event)
```

## Checklist

- [ ] Model explicitly specified (don't rely on default)
- [ ] `system_prompt` focuses on domain behavior, not tool instructions
- [ ] `checkpointer` configured for production (PostgresSaver/AsyncPostgresSaver)
- [ ] `thread_id` passed in config for every invocation
- [ ] Streaming used for long-running agent tasks
- [ ] `create_deep_agent` used (sync) — graph supports async via `ainvoke`/`astream`
- [ ] Agent created once and reused across requests

---

## Built-in Tools vs Backend Methods

**What the agent calls** (tool names):
- `write_todos`, `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`, `execute`, `task`

**What backends implement** (BackendProtocol methods):
- `ls_info()`, `read()`, `write()`, `edit()`, `glob_info()`, `grep_raw()`
- Async variants: `als_info()`, `aread()`, `awrite()`, `aedit()`, `aglob_info()`, `agrep_raw()`

The middleware layer translates between tool calls and backend methods. When implementing custom backends, use the BackendProtocol method names.

---

## MCP Server Integration (langchain-mcp-adapters)

Connect your Deep Agent to MCP servers using `langchain-mcp-adapters`:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

# 1. Configure MCP servers
config = {
    "my-backend": {
        "transport": "sse",
        "url": "http://localhost:8000/mcp/sse",
        "headers": {
            "X-API-Key": "your-api-key",
        },
    },
}

# 2. Create and enter MCP client (context manager)
client = MultiServerMCPClient(config)
await client.__aenter__()

# 3. Load tools from all servers
mcp_tools = client.get_tools()  # Returns list[BaseTool]

# Or from specific server
backend_tools = client.get_tools(server_name="my-backend")

# 4. Pass to agent
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=mcp_tools,
)

# 5. Cleanup on shutdown
await client.__aexit__(None, None, None)
```

### FastAPI Lifespan Pattern

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    client = MultiServerMCPClient(config)
    await client.__aenter__()
    mcp_tools = client.get_tools()

    agent = create_deep_agent(tools=mcp_tools, ...)
    app.state.agent = agent
    app.state.mcp_client = client

    yield

    # Shutdown
    await client.__aexit__(None, None, None)

app = FastAPI(lifespan=lifespan)
```

---

## Documentation Links

- **Overview:** https://docs.langchain.com/oss/python/deepagents/overview
- **Quickstart:** https://docs.langchain.com/oss/python/deepagents/quickstart
- **Customization:** https://docs.langchain.com/oss/python/deepagents/customization
- **API Reference:** https://reference.langchain.com/python/deepagents/
- **GitHub Repository:** https://github.com/langchain-ai/deepagents
