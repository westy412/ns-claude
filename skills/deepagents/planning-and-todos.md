# Planning & Todos

Built-in `write_todos` tool for structured task decomposition and progress tracking.

## The Core Principle

Deep agents include a planning tool (`write_todos`) borrowed from the Claude Code pattern. It enables agents to break down complex tasks into discrete steps, track progress, and adapt plans as new information emerges. This is a "context engineering hack" — it organizes the approach without executing anything.

## How It Works

The `TodoListMiddleware` injects the `write_todos` tool and system prompt guidance automatically. The agent calls `write_todos` to create, update, and track a structured task list.

```
User: "Research competitor landscape and write a report"
    │
    ▼
Agent calls write_todos([
    {"task": "Research competitor A", "status": "pending"},
    {"task": "Research competitor B", "status": "pending"},
    {"task": "Research competitor C", "status": "pending"},
    {"task": "Synthesize findings", "status": "pending"},
    {"task": "Write final report", "status": "pending"},
])
    │
    ▼
Agent works through tasks, updating status as it goes
```

## write_todos Tool

```python
# The tool replaces the ENTIRE todo list each call
write_todos([
    {"task": "Research topic A", "status": "in_progress"},
    {"task": "Research topic B", "status": "pending"},
    {"task": "Write summary", "status": "pending"},
])
```

**Task statuses:**
- `pending` - Not yet started
- `in_progress` - Currently working on (limit to ONE at a time)
- `completed` - Task finished

**Critical constraint:** `write_todos` is enforced to be called at most **once per model turn**. Since the tool replaces the entire todo list, parallel calls would create ambiguity about which version wins.

## When Agents Should Plan

| Task Complexity | Should Plan? |
|----------------|-------------|
| Simple question / single tool call | No |
| 2-3 step task with clear sequence | Maybe |
| Complex multi-step research | Yes |
| Tasks requiring delegation to sub-agents | Yes |
| Long-running analysis (10+ minutes) | Yes |

## System Prompt Integration

The `TodoListMiddleware` automatically injects guidance on when to use planning. You can augment this with domain-specific planning instructions:

```python
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    system_prompt=(
        "For any research task, ALWAYS create a plan first:\n"
        "1. Break the topic into 3-5 research questions\n"
        "2. Research each question using the researcher subagent\n"
        "3. Synthesize findings into a structured report\n"
        "4. Review the report for accuracy and completeness"
    ),
)
```

## Planning + Sub-Agent Delegation

Planning shines when combined with sub-agent delegation:

```
Agent creates plan:
  1. [in_progress] Research market size → delegate to researcher
  2. [pending] Research competitors → delegate to researcher
  3. [pending] Analyze pricing models → delegate to analyst
  4. [pending] Write final report → delegate to writer

After step 1 completes:
  1. [completed] Research market size
  2. [in_progress] Research competitors → delegate to researcher
  3. [pending] Analyze pricing models
  4. [pending] Write final report
```

## Adaptive Planning

Agents can revise their plans as new information emerges:

```python
# Initial plan
write_todos([
    {"task": "Search for company website", "status": "in_progress"},
    {"task": "Extract company info", "status": "pending"},
    {"task": "Write profile", "status": "pending"},
])

# After discovering the company has multiple subsidiaries:
write_todos([
    {"task": "Search for company website", "status": "completed"},
    {"task": "Extract parent company info", "status": "in_progress"},
    {"task": "Research subsidiary A", "status": "pending"},  # New!
    {"task": "Research subsidiary B", "status": "pending"},  # New!
    {"task": "Write consolidated profile", "status": "pending"},  # Updated!
])
```

## TodoListMiddleware Configuration

```python
from deepagents.middleware.todolist import TodoListMiddleware

# Default: included automatically by create_deep_agent
# Custom configuration:
middleware = TodoListMiddleware(
    system_prompt="Always plan before acting. Break tasks into 3-7 steps.",
)
```

## Planning vs Execution

The planning tool is purely organizational — it doesn't execute anything. This separation is intentional:

| Concern | Tool |
|---------|------|
| Planning | `write_todos` |
| File operations | `write_file`, `read_file`, `ls` |
| Research | Sub-agent with search tools |
| Analysis | Sub-agent with code execution |

## Anti-Patterns

```python
# WRONG: Planning for trivial tasks
# User: "What's the capital of France?"
write_todos([
    {"task": "Look up capital of France", "status": "in_progress"},
    {"task": "Respond to user", "status": "pending"},
])
# Just answer the question directly!

# WRONG: Too granular planning
write_todos([
    {"task": "Open browser", "status": "pending"},
    {"task": "Navigate to Google", "status": "pending"},
    {"task": "Type search query", "status": "pending"},
    {"task": "Click search button", "status": "pending"},
    {"task": "Read first result", "status": "pending"},
    # ... 20 more micro-steps
])
# Keep tasks at a meaningful level of abstraction

# WRONG: Never updating plan status
write_todos([
    {"task": "Research topic", "status": "pending"},
    {"task": "Write report", "status": "pending"},
])
# Agent does all the work but never marks tasks as completed
# User has no visibility into progress

# WRONG: Multiple tasks marked in_progress
write_todos([
    {"task": "Research A", "status": "in_progress"},  # Multiple in_progress!
    {"task": "Research B", "status": "in_progress"},  # Pick one at a time
])

# WRONG: Calling write_todos multiple times in one turn
# The tool replaces the entire list - only the last call wins
```

## Checklist

- [ ] Plan created before starting complex tasks (3+ steps)
- [ ] Tasks at meaningful level of abstraction (not too granular)
- [ ] Only ONE task marked `in_progress` at a time
- [ ] Status updated after each task completion
- [ ] Plan adapted when new information emerges
- [ ] Planning combined with sub-agent delegation for complex work
- [ ] `write_todos` called at most once per model turn
