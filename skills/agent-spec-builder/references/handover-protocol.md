# Handover Protocol

When context is getting large, a session is ending, or before loading a new child skill when context is already substantial, follow this protocol to persist state for cold-start resumption.

---

## Mandatory Steps

1. **Update progress.md** with ALL state needed for a cold-start resume:
   - Current phase and exact position within the phase
   - Every decision made, with rationale (not just the choice)
   - Discovery substance — key facts, constraints, and requirements (not just labels)
   - User Q&A — capture important questions asked and user's answers
   - Tool decisions — exact API/library chosen, auth method, documentation links
   - Agent details — types, roles, prompt configs decided so far
   - Flow diagram (ASCII) if one was produced
   - Open questions that still need resolution
   - Exact next steps (which phase, which section, which agent)
   - Which child skill to load next (and ONLY that one)

2. **Verify self-sufficiency:** A new session reading ONLY progress.md (without the original discovery document, handover message, or user conversation) must be able to:
   - Understand the full project context
   - Know every decision made and why
   - Resume work at the exact right point
   - Know which child skill to load next (and ONLY that one)

3. **Tell the user:** "I've saved all progress to progress.md. A new session can resume by invoking the agent-spec-builder skill — it will read progress.md and continue from [exact next step]."

---

## When to Trigger Handover

- Before loading a child skill when context already contains another loaded child skill
- When you notice responses becoming degraded or truncated
- At natural phase boundaries (end of Discovery, end of High-Level Design, etc.)
- When the user indicates they want to pause
