# Phase 4: Handoff for Hybrid Work

> **When to read:** Only when the work includes an agent component alongside API/frontend components. Skip this phase if the work is purely API/frontend.

---

## When This Applies

This phase applies when:
- The discovery doc describes both agent AND non-agent components
- The work type was identified as "hybrid" in Phase 1
- The execution plan includes chunks that require agent-specific tooling

---

## Steps

### 1. Complete the Non-Agent Spec Sections

Ensure all API/frontend sections are fully specified in the spec created during Phase 3. The non-agent portions should be ready for implementation by `general-implementation-builder`.

### 2. Mark Agent Chunks in the Execution Plan

In the execution plan, clearly mark any agent-related chunks:

```markdown
- [ ] **Agent system** (requires agent-spec-builder)
  Outcome: Agent system designed and specified.
  Stream: agent
  Skills: agent-spec-builder, agent-impl-builder
  Note: This chunk requires a separate spec via agent-spec-builder.
```

### 3. Tell the User

> "The spec for the API/frontend components is ready. The agent system chunk needs to go through `agent-spec-builder`. You can invoke that skill now, and it will produce the agent-specific spec that sits alongside this one."

### 4. Provide Context for agent-spec-builder

Give the user the context to pass along:

> "When you run agent-spec-builder, point it at the discovery doc and mention that:
> - The agent interacts with [specific API endpoints / data flows]
> - The agent's output goes to [destination]
> - These non-agent components will be built [before/alongside] the agent
> - The agent should consume/produce [specific data formats]"

---

## Sequencing in the Execution Plan

Non-agent components typically go in earlier phases since the agent may depend on them:

```markdown
### Phase 1: API Foundation (parallel)

- [ ] **API endpoint for content storage**
  Stream: api
- [ ] **API endpoint for retrieval**
  Stream: api

### Phase 2: Frontend + Agent (parallel, blocked by Phase 1)

- [ ] **Frontend content display component**
  Stream: frontend
- [ ] **Agent system** (requires agent-spec-builder)
  Stream: agent
```

---

## Phase Completion Checklist

Before moving to Phase 5:
- [ ] Non-agent spec sections complete
- [ ] Agent chunks clearly marked in execution plan
- [ ] User informed about agent-spec-builder handoff
- [ ] Context provided for agent-spec-builder
