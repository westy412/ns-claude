---
name: [agent-name]
type: [LangGraph: text-agent | message-agent | structured-output-agent | text-tool-agent | message-tool-agent | structured-output-tool-agent] [DSPy: basic-agent | reasoning-agent | conversational-agent | tool-agent | text-agent]
framework: [langgraph | dspy]
reference: agent-patterns/individual-agents/[framework]/[type].md
prompt:
  framework: [single-turn | conversational]
  role: [researcher | critic-reviewer | router-classifier | creative-generator | planner-strategist | summarizer-synthesizer | conversational-assistant | transformer-formatter]
  modifiers: [tools, structured-output, memory, reasoning]
model:
  provider: [anthropic | openai | google | local]
  name: [model-name]
  reasoning: [true | false]
---

# [Agent Name]

## Purpose

### Goal
What outcome this agent achieves.

### Approach
How it achieves that outcome (high-level method/strategy).

### Primary Responsibility
One sentence summary of the core job this agent performs.

### Key Tasks
- Task 1
- Task 2
- Task 3

### Success Criteria
What good output looks like. Measurable where possible.

### Scope Boundaries
What this agent does NOT do. Explicit limits.

## Framework & Role Reasoning

**Framework:** [Single-Turn | Conversational]
**Why:** [Specific signals - e.g., "Receives all info upfront, no dialogue needed, discrete task"]

**Role:** [Role name]
**Why:** [Primary job - e.g., "Creates original content, not transforming existing"]

## LLM Configuration

| Setting | Value | Reasoning |
|---------|-------|-----------|
| **Provider** | [anthropic / openai / google / local] | Why this provider |
| **Model** | [model-name, e.g., claude-3-opus, gpt-4-turbo] | Why this model |
| **Reasoning** | [Yes / No] | Does this agent need extended thinking? |
| **Temperature** | [0.0 - 1.0] | Lower for consistency, higher for creativity |

**Notes:** Any special considerations (cost, latency, compliance)

## Modifiers

### Tools
**Needed:** Yes | No

---

#### Tool Summary Table

| Tool | Purpose | Implementation | Documentation |
|------|---------|----------------|---------------|
| [name] | [what it does] | [mcp-server/api/sdk/custom] | [doc URL] |

---

#### Tool Specifications

For each tool, use the appropriate template below based on implementation type.

**Note:** The spec provides documentation links and simplified examples. The implementation builder will read the actual API docs to create exact schemas. Examples here are for validating understanding with the user, not complete API specifications.

---

### [Tool Name]

**Purpose:** [One sentence description of what this tool does]

**When to use:** [Conditions that trigger this tool call]

**Implementation type:** [mcp-server | existing-api | sdk | custom-function]

---

<!-- Use ONE of the following sections based on implementation type -->

<!-- ============= MCP SERVER ============= -->
#### MCP Server Implementation

| Field | Value |
|-------|-------|
| **Server** | [e.g., `@anthropic/mcp-server-github`] |
| **Tool name** | [tool name within server] |
| **Documentation** | [link to MCP server docs] |

**Configuration:**
```yaml
# Environment variables or config needed
ENV_VAR_NAME: "description"
```

**Example invocation:**
```json
{
  "tool": "tool_name",
  "arguments": {
    "param": "value"
  }
}
```

---

<!-- ============= EXISTING API ============= -->
#### Existing API Implementation

| Field | Value |
|-------|-------|
| **Documentation** | [REQUIRED: link to API docs] |
| **Base URL** | [e.g., `https://api.example.com/v1`] |
| **Endpoint** | [e.g., `GET /videos/{id}/transcript`] |
| **Auth method** | [API key / OAuth / Bearer token / None] |
| **Auth header** | [e.g., `Authorization: Bearer {token}`] |
| **Rate limits** | [e.g., 100 requests/minute] |

**How to get credentials:**
[Instructions for obtaining API keys - signup URL, dashboard location, etc.]

**Request example:**
```http
GET /videos/abc123/transcript HTTP/1.1
Host: api.example.com
Authorization: Bearer sk_xxx
Content-Type: application/json
```

**Response example:**
```json
{
  "transcript": "...",
  "duration": 1234,
  "language": "en"
}
```

**Error codes:**
| Code | Meaning | Handling |
|------|---------|----------|
| 401 | Unauthorized | Check API key |
| 404 | Not found | Return "content not found" |
| 429 | Rate limited | Retry after delay |

**Dependencies:**
```
httpx>=0.24.0
```

---

<!-- ============= SDK/LIBRARY ============= -->
#### SDK/Library Implementation

| Field | Value |
|-------|-------|
| **Package** | [e.g., `youtube-transcript-api`] |
| **Documentation** | [REQUIRED: link to package docs] |
| **Install** | `pip install package-name` |
| **Version** | [version constraints if any] |

**Import:**
```python
from package import ClassName
```

**Key methods:**
```python
# Method signature with description
result = ClassName.method_name(param: type) -> ReturnType
```

**Example usage:**
```python
from youtube_transcript_api import YouTubeTranscriptApi

transcript = YouTubeTranscriptApi.get_transcript(video_id)
# Returns: [{"text": "...", "start": 0.0, "duration": 1.5}, ...]
```

**Common errors:**
| Error | Cause | Handling |
|-------|-------|----------|
| `TranscriptsDisabled` | Video has no captions | Return "transcript unavailable" |
| `VideoUnavailable` | Private/deleted video | Return "video not accessible" |

**Dependencies:**
```
youtube-transcript-api>=0.6.0
```

---

<!-- ============= CUSTOM FUNCTION ============= -->
#### Custom Function Implementation

**Purpose:** [Detailed description of what this function needs to do]

**Algorithm/Logic:**
```
1. [Step 1]
2. [Step 2]
3. [Step 3]
```

**Pseudocode:**
```python
def tool_name(param: type) -> ReturnType:
    # Step 1: ...
    # Step 2: ...
    # Step 3: ...
    return result
```

**Dependencies:**
```
package-name>=1.0.0
```

**Edge cases:**
| Case | Handling |
|------|----------|
| [edge case 1] | [how to handle] |
| [edge case 2] | [how to handle] |

---

#### Tool Parameters

```python
class ToolParams(BaseModel):
    param_name: type = Field(description="What this parameter is for")
    optional_param: Optional[type] = Field(default=None, description="Optional parameter")
```

#### Tool Response

```python
class ToolResponse(BaseModel):
    field_name: type = Field(description="What this field contains")
    # ... other fields
```

**Example response:**
```json
{
  "field_name": "example value"
}
```

---

#### Error Handling

| Error Scenario | Detection | Response |
|----------------|-----------|----------|
| [scenario 1] | [how to detect] | [what to return/do] |
| [scenario 2] | [how to detect] | [what to return/do] |

**Retry strategy:** [None / Retry N times with backoff / etc.]

**Fallback behavior:** [What to do if tool completely fails]

---

<!-- Repeat the above section for each additional tool -->

### Structured Output
**Needed:** Yes | No

If yes, provide the schema:

```python
class OutputSchema(BaseModel):
    field_name: type  # Description, required/optional
```

**Example output:**
```json
{
  "field_name": "example value"
}
```

### Memory
**Type:** None | Conversation History | Session State

If memory needed, what persists:
-

### Reasoning
**Technique:** None | Chain-of-Thought | Chain-of-Verification | Step-Back | Tree-of-Thoughts

If reasoning needed, why:
-

## Inputs

| Input | Description | Format | Source |
|-------|-------------|--------|--------|
| [name] | What it is, what it contains | JSON/text/etc | User/Agent X/etc |

## Outputs

| Output | Description | Format | Consumed By |
|--------|-------------|--------|-------------|
| [name] | What it produces | JSON/text/schema | Agent Y/API/User |

## Context Flow

**Upstream:** (what sends data to this agent)
- [Agent name]: What data, what format

**Downstream:** (what receives data from this agent)
- [Agent name]: What data, what format

## Domain Context

**Business Context:** What system/product this is part of

**User Context:** Who interacts (if applicable)

**Constraints:** Hard rules, compliance, limitations

## Behavioral Requirements

### Key Behaviors
- [Specific behavior 1]
- [Specific behavior 2]

### Edge Cases

| Case | How to Handle |
|------|---------------|
| [case 1] | [handling] |

### What This Agent Should NOT Do
- [constraint 1]
- [constraint 2]

## Examples

### Example 1: [Scenario name]

**Input:**
```
[sample input]
```

**Output:**
```
[sample output]
```

## Notes

Additional context, decisions, considerations.
