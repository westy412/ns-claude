# Delegation Strategy

> **Context:** This reference covers how work is delegated during implementation. The primary execution model uses **agent team teammates** (via TeamCreate). Teammates can spawn **sub-agents** (via Task tool) for research and focused tasks to avoid polluting their context windows.

---

## Execution Hierarchy

```
Agent Implementation Builder (team lead)
├── Spawns TEAMMATES (via TeamCreate + Task tool with team_name)
│   ├── Each teammate owns a work stream (tools, research, ideation, etc.)
│   ├── Teammates maintain context across phases within their stream
│   └── Teammates can spawn SUB-AGENTS for:
│       ├── codebase-researcher → Explore codebase patterns, find implementations
│       ├── web-researcher → Read API docs, external documentation
│       └── prompt-creator → Generate prompts (edits files directly)
```

**Key distinction:**
- **Teammates** (agent teams): Interactive, persistent context, can message back and forth, the user can see their work. Used for the main implementation work.
- **Sub-agents** (Task tool, no team_name): Fire-and-forget, return results and terminate. Used by teammates for research tasks that would pollute their context.

---

## When to Use Teammates vs Sub-Agents

| Situation | Use | Why |
|-----------|-----|-----|
| Parallel phased work across streams | **Teammates** | Need persistent context, coordination |
| Implementing a file (team.py, tools.py, etc.) | **Teammate does directly** | Needs full context of the stream |
| Reading API documentation | **Sub-agent** (web-researcher) | Large content that would pollute teammate context |
| Exploring codebase patterns | **Sub-agent** (codebase-researcher) | Returns only relevant findings |
| Generating prompts | **Sub-agent** (prompt-creator) | Edits file directly, doesn't return content |

---

## Sub-Agents Available to Teammates

| Sub-Agent | When to Use | What It Does |
|-----------|-------------|--------------|
| `codebase-researcher` | Understanding existing code, finding patterns | Reads and analyzes code files, returns structured findings |
| `web-researcher` | API docs, SDK references, external documentation | Searches web, returns relevant findings with sources |
| `prompt-creator` | Generating prompts for agents | Reads spec + prompt-engineering skill, edits file directly |

### Codebase Researcher Usage

Teammates should use `codebase-researcher` sub-agents when they need to:
- Understand existing patterns in the codebase before writing new code
- Find how similar functionality is implemented elsewhere
- Locate relevant files without reading everything into their own context

```
Task tool:
  subagent_type: codebase-researcher
  prompt: "How are API endpoints structured in src/? What patterns do existing routes follow?"
```

The sub-agent reads files, analyzes patterns, and returns a summary — keeping the teammate's context clean for actual code generation.

### Prompt-Creator Sub-Agent Invocation

When a teammate needs to generate prompts, spawn `prompt-creator` sub-agents:

```
Task tool with subagent_type='prompt-creator'

PROMPT FOR SUB-AGENT:
"You are creating a prompt for the [AGENT_NAME] agent.

STEP 1: INVOKE THE PROMPT-ENGINEERING SKILL
You MUST use the Skill tool to invoke: skill: "prompt-engineering"
This loads the prompt engineering reference files. Do not skip this step.

STEP 2: READ THE REFERENCE FILES
After invoking the skill, read these files:
- agent-patterns/prompt-engineering/frameworks/[framework].md
- agent-patterns/prompt-engineering/roles/[role].md
- agent-patterns/prompt-engineering/modifiers/[each modifier].md

STEP 3: READ THE AGENT SPEC
Read the agent spec file: [path to agents/agent-name.md]
Extract: Purpose, Key Tasks, Inputs, Outputs, Behavioral Requirements, Examples

STEP 4: WRITE THE PROMPT
Using the reference files and agent spec, write the prompt.
Use XML tags to structure sections: <role>, <task>, <context>, <constraints>, <output_format>

STEP 5: EDIT THE FILE DIRECTLY
Use the Edit tool to update [prompts.py path or prompts/agent_name.md path]
Replace the placeholder for [VARIABLE_NAME] with your generated prompt.
Do NOT return the prompt content - edit the file directly.

Prompt config:
- Framework: [single-turn | conversational]
- Role: [role name]
- Modifiers: [list of modifiers]
"
```

**CRITICAL: The sub-agent MUST:**
1. Use Skill tool to invoke `prompt-engineering` skill FIRST
2. Read the framework reference file
3. Read the role reference file
4. Read modifier reference files (if any)
5. Read the agent spec
6. THEN write the prompt following the patterns in the reference files
