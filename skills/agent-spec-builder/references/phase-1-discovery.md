# Phase 1: Discovery

Understand the problem thoroughly before designing. Cover these 8 areas through conversation with the user. Update progress.md with all findings before proceeding to Phase 2.

---

## 1. Problem & Purpose
- What problem does this solve?
- Why does this need an agent (vs traditional code)?
- What does success look like?

## 2. Current State & Constraints
- What exists today?
- Technical constraints (APIs, latency, cost)?
- Organizational constraints (compliance, approvals)?

## 3. Interaction Mode

| Mode | Description | Implications |
|------|-------------|--------------|
| **User-facing** | Human interacts directly | Conversational tone, handle ambiguity, explain reasoning |
| **Autonomous** | Receives request, processes, returns result | Structured I/O, clear error handling, logging |
| **Agent-facing** | Called by another agent/team | Strict schemas, predictable behavior, fast responses |

## 4. Journey Mapping
- User journey (if user-facing)
- Agent journey (decision points, branches)
- System flow (data flow, integrations)

## 5. Inputs & Outputs
- What triggers this agent/team?
- What does it produce?
- Format requirements?

---

## 6. Integrations & Tools

**When you reach this section:** Invoke `skill: "tools-and-utilities"` to load the tool vs utility decision framework.

**Before invoking:** Ensure progress.md is updated with all Discovery findings from Sections 1-5.
**After completing this section:** Update progress.md with all tool decisions, implementation approaches, and dependency information before proceeding to Phase 2.

**Purpose:** Capture enough detail about each tool that the implementation builder can create working code WITHOUT guessing.

**Critical principle:** The impl-builder should NEVER have to invent an API or library. The spec must provide:
- Exact API/library to use
- Link to documentation
- Authentication details
- Example requests/responses

### Step 1: Identify What Tools Are Needed

Ask the user:
- What external data does this agent need to fetch?
- What actions does this agent need to take?
- What systems does it need to integrate with?

### Step 2: For Each Tool, Determine Implementation Approach

| Implementation | When to Use | Key Question |
|----------------|-------------|--------------|
| **MCP Server** | Functionality already exists as MCP server | "Is there an MCP server for this?" |
| **Existing API** | Third-party API available | "What API provides this data/action?" |
| **SDK/Library** | Python library available | "Is there a Python package for this?" |
| **Custom Function** | No existing solution | "What logic needs to be built?" |

### Step 3: Get or Research the Specific Implementation

**Ask the user first:**
> "Do you know what API or library we should use for [tool purpose]?"

**If user knows:** Capture the details (see format below).

**If user doesn't know:** Use web-researcher to find options.

```
Task tool → subagent_type: "web-researcher"
Prompt: "I need to [tool purpose]. Research the best options:
1. Are there any MCP servers that provide this?
2. What APIs are available? (include: base URL, auth method, pricing)
3. What Python libraries can do this? (include: package name, GitHub stars, last updated)
Provide pros/cons for each option with links to documentation."
```

**Present options to user:**
> "I found these options for [tool purpose]:
> 1. **[Option A]** - [pros/cons] - [doc link]
> 2. **[Option B]** - [pros/cons] - [doc link]
> Which would you like to use?"

### Step 4: Capture Full Implementation Details

**For MCP Server:**
- Server name (e.g., `@anthropic/mcp-server-github`)
- Tool name within server
- How to configure (env vars, config file)
- Link to MCP server documentation

**For Existing API:**
- Documentation URL (REQUIRED)
- Base URL
- Endpoint path and HTTP method
- Authentication method (API key, OAuth, none)
- How to obtain credentials
- Rate limits
- Request format with example
- Response format with example
- Error codes and handling
- Pagination (if applicable)

**For SDK/Library:**
- Package name (`pip install X`)
- Documentation URL (REQUIRED)
- Version constraints (if any)
- Import statement
- Key method(s) to use with signatures
- Example usage code
- Common errors and handling

**For Custom Function:**
- What it needs to do (detailed description)
- Input/output format
- Dependencies (packages, other tools)
- Algorithm or pseudocode
- Edge cases to handle

### Step 5: Validate Understanding

Before moving on, confirm with user:
> "For the [tool name] tool, I'll specify:
> - Implementation: [type]
> - Using: [API/library name]
> - Documentation: [link]
> - Auth: [method]
> Does this look correct?"

### Tool Discovery Questions Summary

| Question | Purpose |
|----------|---------|
| What external data/actions are needed? | Identify tool needs |
| Do you know what API/library to use? | Get user input first |
| Should I research options? | Trigger web-researcher |
| Which option do you prefer? | User selects approach |
| How do you authenticate? | Capture auth details |
| Do you have API keys already? | Understand setup needs |

**If unsure about any tool details, ASK the user or RESEARCH before proceeding. Never leave tool specifications vague.**

### Step 6: Aggregate Dependencies

After specifying all tools, compile the project-level dependencies:

**Python Packages:**
- Collect all packages from tool specs
- Include framework packages (langgraph, langchain-anthropic, etc.)
- Note version constraints if specified in docs

**Environment Variables:**
- List all API keys and secrets needed
- Include instructions for obtaining each (signup URL, dashboard location)
- Note which tool/agent requires each variable

**External Services:**
- What services need to be running/available?
- MCP servers that need to be configured
- Databases, message queues, etc.

**Questions to ask:**
> "Do you already have API keys for [service], or do you need to set those up?"
> "Are there any other services this needs to connect to that we haven't discussed?"

**Record in team.md** under the Dependencies section.

---

## 7. Complexity & Reliability
- Expected volume/scale?
- Error tolerance?
- Retry/fallback needs?

## 8. LLM Configuration
- Same model for all agents, or different per agent?
- Provider preferences (Anthropic, OpenAI, Google, local)?
- Reasoning models needed? (for complex decision-making)
- Cost constraints? (affects model choice)
- Latency requirements? (smaller models for speed)
- Any compliance requirements? (data residency, no external APIs)

| Consideration | Questions to Ask |
|---------------|------------------|
| **Uniformity** | All agents same model, or specialized per task? |
| **Provider** | Anthropic, OpenAI, Google, local/self-hosted? |
| **Reasoning** | Need chain-of-thought? Extended thinking? |
| **Cost** | Budget constraints? Token limits? |
| **Latency** | Real-time needs? Async acceptable? |
| **Compliance** | Data privacy? On-prem requirements? |

**After Discovery:** Update progress document with findings.
