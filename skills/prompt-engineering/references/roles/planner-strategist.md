# Planner/Strategist Agent

## Role Description
Creates plans, breaks down complex goals into actionable steps, and develops strategies for achieving objectives. Planners think ahead, anticipate dependencies, identify risks, and structure work so others can execute it. They transform ambiguous goals into clear roadmaps.

## When to Use
- The agent needs to produce a plan, roadmap, or sequence of steps
- A complex goal must be decomposed into smaller, manageable tasks
- Dependencies between work items need to be identified and mapped
- Strategic options must be generated, compared, and evaluated
- The output will guide future execution by humans or other agents

## When NOT to Use
- The agent will execute the tasks itself → Use **Executor** instead
- The task is to coordinate multiple agents in real-time → Use **Orchestrator** instead
- The work involves generating content or analysis → Use **Generator/Analyst** instead
- The agent needs to make real-time decisions during execution → Use **Router** instead

## Selection Criteria
- Is the agent's primary job to create a plan that others will follow? → Yes = this role
- Does the agent need to break down "what to do" without doing it? → Yes = this role
- Will the output be a structured sequence of steps with dependencies? → Yes = this role
- Does it need to actually execute the steps it identifies? → If yes, use **Executor**
- Does it need to dispatch work to other agents dynamically? → If yes, use **Orchestrator**

## Framework Fit
**Primary:** Single-Turn
**Why:** Planning tasks have clearly defined inputs (goal, constraints, context) and outputs (plan, steps, dependencies). The agent doesn't need to gather information conversationally—it transforms input into structured output.
**When to use the other:** Use Conversational when plans require iterative refinement with stakeholder feedback, when requirements are ambiguous and need clarification dialogue, or when the planning process itself is collaborative.

## Section-by-Section Guidance

### For Single-Turn Framework:

**`<who_you_are>`**
- Emphasize strategic thinking, forward planning, and systematic decomposition
- Include relevant domain expertise (e.g., "software project planning," "business strategy")
- State the planner's orientation toward practicality—plans should be executable, not theoretical
- Avoid making the agent sound like it will execute the plan; it creates plans for others

**`<skill_map>`**
- Task decomposition and work breakdown
- Dependency identification and sequencing
- Effort/complexity estimation
- Risk identification and mitigation planning
- Milestone and success criteria definition
- Keep skills focused on planning activities, not execution activities

**`<context>`**
- Describe who will use the plan (development team, executives, other agents)
- Explain what system, project, or domain the plans address
- Include the planning horizon (sprint-level, project-level, strategic)
- Note any organizational constraints or standards the plans must follow

**`<inputs>`**
- **Goal/Objective**: What needs to be achieved—always include this
- **Constraints**: Resource limits, time boundaries, technical limitations
- **Current State**: Where things are now (starting point for the plan)
- **Context/Background**: Prior decisions, existing systems, team composition
- Document each input with "what it is," "what's included," and "how to use it"

**`<task>`**
- Start with analysis of the goal and constraints
- Include explicit decomposition steps (break goal → milestones → tasks)
- Require dependency mapping between tasks
- Include risk identification as a discrete step
- End with assembling the final plan output
- Be prescriptive about methodology—don't just say "create a plan"

**`<output_format>`**
- Define the structure: milestones, tasks, dependencies, risks, assumptions
- Use tables for task lists (ID, description, effort, dependencies, risks)
- Include a critical path section for complex plans
- Require explicit assumptions and risks sections
- Match detail level to planning horizon (strategic = high-level, operational = specific)

**`<important_notes>`**
- Tasks must be concrete and completable (not "work on X" but "implement X")
- Require explicit dependency declarations for every task
- Define effort estimation scale (e.g., T-shirt sizes with day equivalents)
- Force assumption documentation for any ambiguity
- State that plans should be achievable, not optimistic
- Specify how to handle missing information (flag and assume vs. refuse)

### For Conversational Framework:

**`<who_you_are>`**
- Same strategic orientation as Single-Turn
- Add emphasis on collaborative planning and requirement gathering
- Note ability to refine plans based on feedback

**`<capabilities>`**
- List types of plans the agent can create (project plans, strategies, roadmaps)
- Include ability to explain reasoning behind plan structure
- Mention iterative refinement capabilities

**`<operational_logic>`**
- How to gather requirements when goals are ambiguous
- When to ask clarifying questions vs. make assumptions
- How to present options and get stakeholder input
- Process for incorporating feedback into plan revisions

**`<interaction_patterns>`**
- Initial requirements gathering questions
- How to present draft plans for review
- Handling disagreement about approach or estimates
- Finalizing and confirming the plan

**`<examples>`**
- Show planning conversations, not just final plans
- Demonstrate requirement clarification dialogue
- Include examples of plan revision based on feedback

## Modifier Notes

**If adding Tools:**
- See `modifiers/tool-usage.md` for per-tool documentation patterns
- For each tool, document: what it does, when to use it, parameters, expected responses, error handling
- Common planner tools: calendar/scheduling (timeline feasibility), resource lookups, project management read access
- Add a `<tool_usage_guidelines>` section if tools inform planning decisions

**If using Structured Output:**
- See `modifiers/structured-output.md` for schema design patterns
- Common for planning — plans feed into project management tools (Jira, Linear, Asana)
- Schema should include: tasks, dependencies, estimates, risks, assumptions
- Consider separate schemas for strategic (high-level milestones) vs. operational (detailed tasks)
- For agent-to-agent: executor agents need the task list, not necessarily the planner's reasoning

**If adding Memory:**
- See `modifiers/memory.md` for memory implementation patterns
- Useful for long-running planning projects where context evolves
- Store prior plan versions to track how requirements changed
- Remember stakeholder preferences and past estimation accuracy

## Common Pitfalls
1. **Vague tasks** — Require concrete, completable task descriptions. "Work on authentication" fails; "Implement OAuth login flow" works.
2. **Missing dependencies** — Plans without dependencies are just lists. Require every task (except the first) to declare what it depends on.
3. **Hidden assumptions** — Ambiguous goals lead to assumed requirements. Force explicit assumption documentation in the output format.
4. **Optimism bias** — Plans consistently underestimate. Include buffer guidance or require uncertainty flags on estimates.
5. **No critical path** — For complex plans, identifying the longest dependency chain is essential for timeline accuracy. Include it in the output format.
6. **Confusing planning with execution** — The planner creates the plan; others execute it. If you need the agent to also do the work, use Executor or Orchestrator instead.
