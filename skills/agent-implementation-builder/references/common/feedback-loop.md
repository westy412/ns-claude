# Feedback Loop: Updating Cheat Sheets

> **Context:** This reference covers updating framework cheat sheets when feedback reveals implementation mistakes. Read this when you receive feedback about generated code.

---

## When to Update

Update the cheat sheet when you receive feedback that:
- Points out an incorrect pattern you used
- Identifies a framework anti-pattern
- Highlights a rule you didn't follow
- Reveals a common mistake

---

## How to Update

1. **Identify the framework** — Which cheat sheet needs updating?
   - `frameworks/langgraph/CHEATSHEET.md`
   - `frameworks/dspy/CHEATSHEET.md`

2. **Categorize the feedback:**
   - **Critical Rule** — Add to "Critical Rules" section
   - **Anti-pattern** — Add to "Anti-Patterns" section with wrong code example
   - **Pattern clarification** — Add to relevant pattern section

3. **Check for contradictions (MANDATORY):**
   Before writing ANY update, read the target file AND related skill files to check if the proposed change contradicts existing content.

   **What to check:**
   - Does the proposed pattern conflict with an existing rule in the same file?
   - Does it conflict with guidance in other skills that reference the same framework?
   - Does it contradict conventions in SKILL.md routing logic?

   **Key cross-references to check:**

   | If updating... | Also check... |
   |----------------|---------------|
   | `frameworks/dspy/CHEATSHEET.md` | `prompt-engineering/references/targets/dspy.md`, SKILL.md DSPy routing |
   | `frameworks/langgraph/CHEATSHEET.md` | `prompt-engineering/references/targets/langgraph.md`, SKILL.md LangGraph routing |
   | Any pattern or rule | The corresponding section in other framework cheat sheets for consistency |

   **If a contradiction is found:** STOP. Present both the existing content and the proposed change to the user. Explain the conflict and ask which should take precedence. Do NOT silently overwrite existing guidance.

   **If no contradiction:** Proceed with the update.

4. **Format the update:**

**For anti-patterns:**
```
### DO NOT: [Description of mistake]

```python
# WRONG
[Code that was incorrectly generated]
```

**Why:** [Explanation of why this is wrong]

**Correct approach:**
```python
# CORRECT
[How it should be done]
```
```

**For critical rules:**
```
### [Number]. [Rule Name]

**CORRECT:**
```python
[Correct code]
```

**WRONG - DO NOT DO THIS:**
```python
[Wrong code]
```

**Why:** [Explanation]
```

5. **Edit the cheat sheet** using the Edit tool.

---

## Example

**Feedback received:**
> "The ToolNode is being created inside the agent function instead of being added to the graph."

**Action taken:**
1. Open `frameworks/langgraph/CHEATSHEET.md`
2. Add to Anti-Patterns section:

```
### DO NOT: Create ToolNode inside agent functions

```python
# WRONG
async def agent(state):
    if response.tool_calls:
        tool_node = ToolNode(tools)  # WRONG - created inside function
        result = await tool_node.ainvoke(...)  # WRONG - manual invocation
```

**Why:** ToolNode is designed to be a graph node. Creating it inside functions bypasses LangGraph's execution model.
```

---

## Mandatory Update Triggers

**Always update the cheat sheet when:**
- [ ] User explicitly says the generated code is wrong
- [ ] A pattern was used incorrectly
- [ ] The code doesn't follow framework best practices
- [ ] A debugging session reveals a systematic issue

**Do not wait for multiple occurrences.** Add to the cheat sheet on first feedback to prevent repetition.
