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

## `create_deep_agent` API Signature

```python
create_deep_agent(
    name: str | None = None,
    model: str | BaseChatModel | None = None,
    tools: Sequence[BaseTool | Callable | dict[str, Any]] | None = None,
    *,
    system_prompt: str | SystemMessage | None = None
) -> CompiledStateGraph
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str \| None` | `None` | Optional name for the agent |
| `model` | `str \| BaseChatModel \| None` | `None` | Model identifier string or `BaseChatModel` instance. Defaults to `claude-sonnet-4-5-20250929` |
| `tools` | `Sequence[BaseTool \| Callable \| dict] \| None` | `None` | Additional tools the agent can use |
| `system_prompt` | `str \| SystemMessage \| None` | `None` | Custom instructions that prepend to the built-in system prompt |

---

## Model Configuration

**Default model:** `claude-sonnet-4-5-20250929`. Use `provider:model` format to switch.

```python
# OpenAI
agent = create_deep_agent(model="openai:gpt-5.2")

# Anthropic (default)
agent = create_deep_agent(model="claude-sonnet-4-5-20250929")

# Azure OpenAI
agent = create_deep_agent(model="azure_openai:gpt-4.1")

# Google Generative AI
agent = create_deep_agent(model="google_genai:gemini-2.5-flash-lite")

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
research_instructions = """You are an expert researcher. Your job is to conduct thorough research, and then write a polished report."""

agent = create_deep_agent(system_prompt=research_instructions)
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

## How It Works

When invoked, a deep agent follows this autonomous loop:

1. **Plans** using `write_todos` to decompose the task
2. **Calls tools** to gather information
3. **Manages context** using file system tools to persist intermediate results
4. **Spawns subagents** via `task` when subtasks benefit from dedicated focus
5. **Synthesizes a final response**

---

## Quickstart Example: Research Agent

```python
import os
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def internet_search(query: str, max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False):
    """Run a web search"""
    return tavily_client.search(query, max_results=max_results,
        include_raw_content=include_raw_content, topic=topic)

research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

## `internet_search`
Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included."""

agent = create_deep_agent(
    tools=[internet_search],
    system_prompt=research_instructions
)

result = agent.invoke({"messages": [{"role": "user", "content": "What is langgraph?"}]})
print(result["messages"][-1].content)
```

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

## Deep Agents CLI

Try Deep Agents from the terminal:

```bash
uv tool install deepagents-cli
deepagents
```

The CLI adds conversation resume, web search, remote sandboxes, persistent memory, custom skills, and human-in-the-loop approval.

---

## Documentation Links

- **Overview:** https://docs.langchain.com/oss/python/deepagents/overview
- **Quickstart:** https://docs.langchain.com/oss/python/deepagents/quickstart
- **Customization:** https://docs.langchain.com/oss/python/deepagents/customization
- **API Reference:** https://reference.langchain.com/python/deepagents/
- **GitHub Repository:** https://github.com/langchain-ai/deepagents
