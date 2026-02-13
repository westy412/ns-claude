# Phase 2: High-Level Design

Evaluate the discovered problem and map the rough system outline. This phase determines whether you need a single agent or a team, and if a team, which coordination pattern to use.

---

## First Decision: Single Agent or Agent Team?

```
Can one agent with tools handle this?
├── YES → Single agent (multiple tools + long system prompt)
└── NO → Agent team
    └── Can one team handle this?
        ├── YES → Single team
        └── NO → Nested teams (teams of teams)
```

**Single agent signals:**
- One clear responsibility
- Tools can handle all external needs
- No complex coordination needed

**Agent team signals:**
- Multiple distinct responsibilities
- Different specialists needed
- Complex coordination/handoffs

## Detail Level by Scope

| Building | Details to Capture |
|----------|-------------------|
| Single agent | Role + inputs + outputs |
| Agent team | Role + inputs + outputs + names of potential agents |
| Agent system (teams of teams) | Overall output + what each team does + agents within |

---

## Pattern Selection

**When you reach this phase:** Invoke `skill: "agent-teams"` to load the pattern selection criteria.

**Before invoking:** Ensure progress.md has complete Discovery findings (all 8 areas) and the single-agent-vs-team decision.
**After completing pattern selection:** Update progress.md with the chosen pattern, rationale, agents identified, and flow diagram before proceeding to Phase 3.

Work WITH the user to select the pattern based on their coordination needs:

| Pattern | Key Signal |
|---------|------------|
| **Pipeline** | Sequential stages, each depends on previous |
| **Router** | Dynamic dispatch based on input |
| **Fan-in-fan-out** | Parallel independent work, then aggregation |
| **Loop** | Iterative refinement with feedback |

## Output Format

- **Terminal:** ASCII art diagram only
- **File:** Both Mermaid AND ASCII art

## Nested Systems Approach

1. Start high level (overall system purpose, outputs)
2. Go more granular (what does each team do?)
3. Work back up (fill in agents within teams)
4. Can be iterative / somewhat simultaneous

**After High-Level Design:** Update progress document with design overview and agents identified.
