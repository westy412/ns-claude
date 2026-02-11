# Teammate Guide: Using the Prompt Engineering Skill

You are a teammate tasked with creating one or more agent prompts. This guide tells you exactly how to use the prompt-engineering skill to produce production-ready prompts.

## Step 0: Load the Skill

Before doing anything else, load the prompt-engineering skill:

```
Skill tool -> skill: "prompt-engineering"
```

Confirm to the team lead that you have loaded the skill before proceeding.

## Step 1: Understand Your Assignment

You should have received a specification (see template at the bottom of this file). It contains:

- **Agent name** and purpose
- **Target platform**: DSPy, LangGraph, or General
- **Framework**: Single-Turn or Conversational
- **Role**: One of the 8 roles (Researcher, Critic/Reviewer, Router/Classifier, Creative/Generator, Planner/Strategist, Summarizer/Synthesizer, Conversational/Assistant, Transformer/Formatter)
- **Modifiers**: Which of Tools, Structured Output, Memory, Reasoning apply
- **Agent context**: Inputs, outputs, upstream/downstream agents
- **Domain context** and behavioral requirements

If any of these are missing or unclear, message the team lead to clarify BEFORE starting work.

## Step 2: Read Required Reference Files

Based on your assignment, read these files from the skill's `references/` directory. Use Glob to locate the skill base path if needed: `**/prompt-engineering/SKILL.md`

### Always read:
1. `references/guidelines/prompt-writing.md` — prompt quality guidelines and anti-patterns

### Based on target platform (read ONE):
| Target | File |
|--------|------|
| DSPy | `references/targets/dspy.md` |
| LangGraph | `references/targets/langgraph.md` |
| General | `references/targets/general.md` |

### Based on framework (read ONE):
| Framework | File |
|-----------|------|
| Single-Turn | `references/frameworks/single-turn.md` |
| Conversational | `references/frameworks/conversational.md` |

### Based on role (read ONE):
| Role | File |
|------|------|
| Researcher | `references/roles/researcher.md` |
| Critic/Reviewer | `references/roles/critic-reviewer.md` |
| Router/Classifier | `references/roles/router-classifier.md` |
| Creative/Generator | `references/roles/creative-generator.md` |
| Planner/Strategist | `references/roles/planner-strategist.md` |
| Summarizer/Synthesizer | `references/roles/summarizer-synthesizer.md` |
| Conversational/Assistant | `references/roles/conversational-assistant.md` |
| Transformer/Formatter | `references/roles/transformer-formatter.md` |

### Based on modifiers (read each that applies):
| Modifier | File | When |
|----------|------|------|
| Tools | `references/modifiers/tool-usage.md` | Agent calls external tools or APIs |
| Structured Output | `references/modifiers/output-type.md` | Output parsed by code or other agents |
| Memory | `references/modifiers/memory.md` | Long-term/cross-session state needed |
| Reasoning | `references/modifiers/reasoning.md` | Complex multi-step logic needed |

## Step 3: Write the Prompt

Follow the target-specific instructions from the file you read in Step 2.

### DSPy Target

You produce TWO files:

**File 1: `signatures.py`** (or add to existing)
1. Define the Signature class with an empty docstring (`""""""`)
2. Add all `InputField`s with descriptive `description` parameters
3. Add all `OutputField`s with specific types and `description` parameters
4. Import Pydantic models from `models.py` for complex output types
5. Add a comment noting the recommended predictor type (Predict / ChainOfThought / ReAct)

**File 2: `prompts/{agent_name}.md`**
1. Start with the framework template's XML section structure
2. Apply role-specific guidance for each section
3. SKIP `<output_format>` — typed fields handle output structure
4. ADD `<enum_compliance>` for any Literal/Union output fields
5. ADD `<quality_standards>` and `<anti_patterns>` sections
6. Layer in modifier patterns (adapted per the DSPy target reference)

### LangGraph Target

You produce ONE file: a prompt string for `prompts.py`

1. Follow the framework template's full XML section structure (no sections skipped)
2. Apply role-specific guidance for each section
3. Include complete `<output_format>` with schema and examples
4. **Escape all literal curly braces** as `{{` and `}}`
5. Document template variables `{var_name}` in `<inputs>`
6. Layer in modifier patterns

### General Target

You produce ONE file: a standalone prompt string

1. Follow the framework template's full XML section structure
2. Apply role-specific guidance for each section
3. Include complete `<output_format>`
4. Layer in modifier patterns
5. No special escaping or adaptations needed

## Step 4: Validate

Run through the checklist from your target reference file, plus these universal checks:

- [ ] Prompt follows the chosen framework template structure
- [ ] All required sections present (check framework template)
- [ ] Role-specific guidance applied to each section (check role file)
- [ ] All selected modifiers incorporated (check modifier files)
- [ ] Edge cases covered in constraints section
- [ ] No TODOs or placeholders remain
- [ ] Constraints placed in final section (recency effect)
- [ ] Reviewed against `references/guidelines/prompt-writing.md` quality checklist

## Step 5: Deliver

1. Write the prompt file(s) to the location specified in your assignment
2. Message the team lead with completion status
3. Include any notes about decisions you made, assumptions, or areas of uncertainty

---

## Agent Specification Template

When preparing assignments for teammates, use this format:

```markdown
## Agent: {agent_name}

**Purpose:** {1-2 sentence description of what this agent does}

### Target & Configuration

- **Target Platform:** DSPy | LangGraph | General
- **Framework:** Single-Turn | Conversational
- **Role:** {role name}
- **Modifiers:** {list of applicable modifiers, or "None"}

### Inputs

| Name | Type | Description |
|------|------|-------------|
| {input_name} | {type} | {what it contains and how to use it} |

### Outputs

| Name | Type | Description |
|------|------|-------------|
| {output_name} | {type} | {what downstream systems expect} |

### Agent Context

**Upstream:** {agent name} provides {what data}
**Downstream:** {agent name} expects {what data}
**Workflow Position:** {where in the pipeline, what depends on this agent}

### Domain Context

**Business Context:** {what system this is part of}
**User Context:** {who interacts with this agent, if anyone}

### Behavioral Requirements

**Key Behaviors:**
- {behavior 1}
- {behavior 2}

**Edge Cases:**
- {edge case 1}: {how to handle}
- {edge case 2}: {how to handle}

**What This Agent Should NOT Do:**
- {explicit constraint 1}
- {explicit constraint 2}

### File Locations

**Write prompt to:** {file path}
**Read agent spec from:** {file path, if applicable}
```
