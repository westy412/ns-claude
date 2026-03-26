---
name: langchain-mcp-adapters
description: Adapters for integrating MCP tools, resources, and prompts with LangChain and LangGraph agents.
metadata:
  tags: mcp, langchain, langgraph, tools, agents, model-context-protocol
---

# langchain-mcp-adapters

> **Invoke with:** `/langchain-mcp-adapters` | **Keywords:** mcp, langchain, langgraph, mcp tools, mcp adapters, model context protocol, MultiServerMCPClient

Use this skill when building LangChain or LangGraph agents that consume tools, resources, or prompts from MCP (Model Context Protocol) servers. It covers the `langchain-mcp-adapters` Python library, which bridges MCP servers to the LangChain ecosystem.

---

## Purpose

Use this skill when you need to:

- Connect one or more MCP servers to a LangChain or LangGraph agent
- Load MCP tools as LangChain `BaseTool` objects
- Load MCP resources or prompt templates into LangChain workflows
- Configure transports (stdio, HTTP, SSE, WebSocket) and authentication
- Manage stateless vs stateful MCP sessions
- Add middleware (interceptors) to tool calls for logging, caching, auth injection, or state management
- Handle server notifications (progress, logging, elicitation)
- Deploy MCP-powered agents via the LangGraph API Server

This skill does **not** cover writing MCP servers from scratch (see the MCP SDK docs) or general LangGraph concepts unrelated to MCP integration.

## Reference Files

| Task | Reference File | Description |
|------|----------------|-------------|
| **Install the library, write an MCP server, or build a first agent** | [getting-started.md](./references/getting-started.md) | Installation, quick start, writing stdio/HTTP servers, creating agents |
| **Configure MultiServerMCPClient or transport connections** | [client-and-transports.md](./references/client-and-transports.md) | Constructor API, StdioConnection, SSEConnection, StreamableHttpConnection, WebsocketConnection, headers, auth, multi-server setup |
| **Load tools, handle structured/multimodal content, or use tool name prefixing** | [tools.md](./references/tools.md) | `get_tools()`, `load_mcp_tools()`, MCP-to-LangChain conversion, MCPToolArtifact, multimodal content mapping |
| **Load resources or prompt templates from MCP servers** | [resources-and-prompts.md](./references/resources-and-prompts.md) | `get_resources()`, `load_mcp_resources()`, Blob objects, `get_prompt()`, `load_mcp_prompt()`, static vs dynamic resources |
| **Control session lifecycle (stateless vs stateful)** | [sessions.md](./references/sessions.md) | Default stateless behavior, `client.session()` context manager, when to use stateful sessions, `auto_initialize` |
| **Add middleware to tool calls (logging, caching, auth, retries)** | [interceptors.md](./references/interceptors.md) | `ToolCallInterceptor` protocol, `MCPToolCallRequest`, runtime context, `request.override()`, `Command` for state updates, composition order |
| **Handle progress, logging, or elicitation callbacks** | [callbacks-and-notifications.md](./references/callbacks-and-notifications.md) | `Callbacks` dataclass, `on_progress`, `on_logging_message`, `on_elicitation`, `ElicitResult`, server-side reporting |
| **Build agents with LangGraph StateGraph or deploy via LangGraph API Server** | [langgraph-integration.md](./references/langgraph-integration.md) | `create_agent`, `StateGraph` + `ToolNode`, `langgraph.json`, graph factories, complete end-to-end examples |

> **Maintenance Note**: If any patterns in the reference files are found to be incorrect during implementation, update the corresponding reference file with the correct pattern.

---

## Core Concepts

**langchain-mcp-adapters** is a Python library that converts MCP tools, resources, and prompts into LangChain-compatible objects. MCP (Model Context Protocol) defines a standard interface for tool servers; this library acts as the bridge so LangChain and LangGraph agents can call those tools without MCP-specific code in the agent itself.

The central class is `MultiServerMCPClient`. You give it a dictionary mapping server names to connection configurations (transport type, URL or command, optional headers), and it manages the underlying MCP sessions. Call `client.get_tools()` to get a flat list of LangChain `BaseTool` instances from all connected servers. These tools plug directly into `create_agent()` or a LangGraph `StateGraph` with `ToolNode`.

By default, `MultiServerMCPClient` operates statelessly -- each tool invocation creates a fresh MCP session, executes the call, and tears down. This is safe and simple for most use cases. When a server needs to maintain state across calls (transactions, working directories, accumulated context), use `client.session("server_name")` to open a persistent session via an async context manager. All tool calls within that block share the same session.

Tool interceptors provide a middleware layer around tool execution. An interceptor is an async function that receives a request and a handler callback. It can inspect or modify the request (via `request.override()`), call the handler, and inspect or modify the result. Interceptors compose in onion order and support patterns like logging, caching, auth injection, retry logic, permission gating, and LangGraph state updates via `Command`.

The library also supports callbacks for server notifications: progress updates during long-running operations, structured log messages, and elicitation requests where the server asks the client for additional structured input mid-execution. These are configured via the `Callbacks` dataclass passed to the client or to `load_mcp_tools`.

---

## Quick Reference

### Install

```bash
pip install langchain-mcp-adapters langgraph langchain-anthropic
```

### Connect to servers and load tools

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "math": {
        "transport": "stdio",
        "command": "python",
        "args": ["/path/to/math_server.py"],
    },
    "weather": {
        "transport": "http",
        "url": "http://localhost:8000/mcp",
    },
})
tools = await client.get_tools()
```

### Create an agent with MCP tools

```python
from langchain.agents import create_agent

agent = create_agent("openai:gpt-4.1", tools)
result = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
)
```

### Use a stateful session

```python
from langchain_mcp_adapters.tools import load_mcp_tools

async with client.session("math") as session:
    tools = await load_mcp_tools(session)
    # All tool calls share this session
```

---

## Documentation Links

- **GitHub**: https://github.com/langchain-ai/langchain-mcp-adapters
- **Docs**: https://docs.langchain.com/oss/python/langchain/mcp
- **API Reference**: https://reference.langchain.com/python/langchain_mcp_adapters/
