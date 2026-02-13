# Implementation Patterns

> **Context:** This reference covers structural patterns for complex agent systems: template-to-instances, handling nested teams, and 3-level nesting. Read this when implementing systems with multiple similar sub-teams or deeply nested hierarchies.

---

## Handling Nested Teams

For nested teams, use the **execution plan** from manifest.yaml to determine phasing.

If no execution plan exists, process depth-first with parallelization:

1. Read `manifest.yaml` for the execution plan (or fall back to hierarchy)
2. Sub-teams at the same level can be implemented in parallel
3. Parent team waits for all sub-teams to complete
4. Top-level team.py imports and orchestrates sub-teams

**Each sub-team folder is self-contained** - has its own `agent-config.yaml`, can be processed independently.

```
Phase 1 (can run simultaneously):
├── Implement content-refinement/ (complete team)
└── Implement parallel-research/ (complete team)

Phase 2 (after Phase 1 completes):
└── Implement research-pipeline/ top-level (orchestrates sub-teams)
```

In **team mode**, each sub-team can be assigned to a different work stream's teammate. In **single-agent mode**, spawn Task sub-agents for parallel sub-team work.

---

## Template-to-Instances — BLOCKING REQUIREMENT

**CRITICAL: This is NOT optional. Factory functions are FORBIDDEN for template instances.**

When multiple sub-teams share the same structure but differ in configuration (e.g., 5 search loops each targeting a different platform), generate each instance as a **standalone, self-contained module**.

**Pattern recognition:** A generic template spec is referenced by multiple sub-teams. Each sub-team has its own folder with its own `team.md` and `agent-config.yaml`, but the structure (agents, flow, pattern) is identical — only the configuration values differ (API keys, actor names, platform-specific parameters).

### WRONG — Factory Functions (DO NOT DO THIS)

```python
# src/research/research_loop.py
class ResearchLoop(dspy.Module):
    def __init__(self, search_tools, search_instructions, ...):
        # Generic implementation
        pass

def create_linkedin_keyword_loop(flash_lm):
    return ResearchLoop(
        search_tools=[search_linkedin_keyword],
        search_instructions=_LINKEDIN_KEYWORD_SEARCH_INSTRUCTIONS,
        ...
    )

def create_x_trending_loop(flash_lm):
    return ResearchLoop(...)
```

**Why this is wrong:**
- Violates isolation — changing one instance risks breaking others
- Makes debugging harder — error could be in generic class or instance config
- Prevents independent evolution — instances can't diverge over time
- LLM maintaining one instance must understand all instances

### CORRECT — Self-Contained Modules

```
src/research/
├── linkedin_keyword/
│   ├── team.py          # LinkedInKeywordLoop(dspy.Module)
│   ├── signatures.py    # LinkedInKeywordSearchSignature, LinkedInKeywordAnalysisSignature
│   └── __init__.py
├── x_trending/
│   ├── team.py          # XTrendingLoop(dspy.Module)
│   ├── signatures.py    # XTrendingSearchSignature, XTrendingAnalysisSignature
│   └── __init__.py
```

Each instance is FULLY self-contained:
- Own directory
- Own team.py with instance-specific implementation
- Own signatures.py with platform-specific prompts baked into docstrings
- Own __init__.py
- Zero imports from sibling instances
- Can be understood and modified without reading siblings

**If you find yourself writing factory functions, STOP. Generate separate modules instead.**

### Generation Rules

1. Each instance gets its own directory with its own `team.py`, `signatures.py`, agent files — the full set
2. **No shared imports between sibling instances** — each module is fully self-contained
3. If one instance breaks, fixing it should never risk breaking siblings
4. Each module must be understandable in isolation without cross-referencing the template or siblings

### Efficient Generation Approach

1. Read the first instance's spec fully and generate its complete module
2. For subsequent instances, diff against the first: note what changes (actor config, platform name, model parameters) and what stays the same (structure, flow, pattern)
3. Generate each subsequent instance as a standalone copy with its specific values substituted
4. Do NOT create a shared base class or parameterized factory — the duplication is intentional for maintainability

**Why duplication over abstraction:** An LLM maintaining `linkedin-keyword` should read one self-contained module, change it, and not risk breaking `x-trending`. Each instance can diverge independently over time without refactoring shared code.

---

## 3-Level Nesting

For systems with 3+ levels of nesting (root pipeline → phase teams → sub-teams), understand the import and orchestration chain:

**Example: 3-level hierarchy**

```
root pipeline.py                          # Level 1 — imports phase team modules
├── research_team/team.py                 # Level 2 — imports sub-team modules
│   ├── linkedin_keyword/team.py          # Level 3 — contains its own agents
│   ├── x_trending/team.py               # Level 3
│   ├── analytics_team/team.py           # Level 3
│   └── ...
└── ideation_team/team.py                # Level 2 — contains its own agents
```

**Import chain:** `root.forward() → phase_team.forward() → sub_team.forward() → agent.forward()`

```python
# Level 1: root pipeline.py
from src.research_team.team import ResearchPhase
from src.ideation_team.team import IdeationPipeline

class RootPipeline(dspy.Module):
    def __init__(self):
        self.research = ResearchPhase()
        self.ideation = IdeationPipeline()

    async def aforward(self, **inputs):
        research_output = await self.research.aforward(**inputs)
        return await self.ideation.aforward(research=research_output, **inputs)
```

```python
# Level 2: research_team/team.py (fan-in-fan-out orchestrating sub-teams)
from src.research_team.linkedin_keyword.team import LinkedInKeywordLoop
from src.research_team.x_trending.team import XTrendingLoop
from src.research_team.analytics_team.team import AnalyticsTeam

class ResearchPhase(dspy.Module):
    def __init__(self):
        self.linkedin_keyword = LinkedInKeywordLoop()
        self.x_trending = XTrendingLoop()
        self.analytics = AnalyticsTeam()
        # ... more sub-teams

    async def aforward(self, **inputs):
        results = await asyncio.gather(
            self.linkedin_keyword.aforward(**inputs),
            self.x_trending.aforward(**inputs),
            self.analytics.aforward(**inputs),
            return_exceptions=True,
        )
        # Synthesize results...
```

```python
# Level 3: research_team/linkedin_keyword/team.py (loop with its own agents)
class LinkedInKeywordLoop(dspy.Module):
    def __init__(self):
        self.search = dspy.ReAct(SearchSignature, tools=[apify_search])
        self.analysis = dspy.Predict(AnalysisSignature)

    async def aforward(self, **inputs):
        for i in range(max_iterations):
            search_result = await self.search.aforward(**inputs)
            analysis = await self.analysis.aforward(data=search_result)
            if analysis.satisfied:
                break
        return analysis
```

### Mixed-Pattern Guidance

When a parent team orchestrates children that use different patterns (e.g., fan-in-fan-out parent with loop children AND fan-in-fan-out children):

- The parent's `team.py` uses `asyncio.gather()` to run all sub-teams in parallel
- Each sub-team internally uses its own pattern (loops iterate, fan-out teams parallelize)
- The parent does NOT need to know the internal pattern of its children — it only calls `sub_team.aforward()` and receives the output
- Each sub-team is a self-contained `dspy.Module` that hides its internal orchestration
