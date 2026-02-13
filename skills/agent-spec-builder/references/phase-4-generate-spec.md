# Phase 4: Generate Spec

Produce the specification files. After generating, run post-generation validation checks before proceeding to Phase 5.

---

## Spec Folder Structure

**Single agent:**
```
project-name/
└── spec/
    ├── manifest.yaml        # Entry point for impl-builder
    ├── progress.md          # Handover document
    ├── agent-config.yaml    # Machine-readable config
    └── my-agent.md          # Agent spec
```

**Single team:**
```
project-name/
└── spec/
    ├── manifest.yaml        # Entry point for impl-builder
    ├── progress.md          # Handover document
    └── content-review-loop/
        ├── team.md          # Team overview
        ├── agent-config.yaml # This team's config
        └── agents/
            ├── creator.md   # Agent spec
            └── critic.md    # Agent spec
```

**Nested teams:**
```
project-name/
└── spec/
    ├── manifest.yaml        # Entry point for impl-builder
    ├── progress.md          # Handover document
    └── research-pipeline/   # Root team folder
        ├── team.md
        ├── agent-config.yaml # Root team config (references sub-teams)
        ├── content-refinement/
        │   ├── team.md
        │   ├── agent-config.yaml # Sub-team config
        │   └── agents/
        │       ├── creator.md
        │       └── critic.md
        └── parallel-research/
            ├── team.md
            ├── agent-config.yaml # Sub-team config
            └── agents/
                ├── researcher-a.md
                └── merger.md
```

**Key points:**
- Each team folder is self-contained with its own agent-config.yaml
- Agent specs live in `agents/` subdirectory within each team
- Sub-teams can be processed in parallel by impl-builder
- Use descriptive team names (not stage-1, stage-2)

---

## 3-Level Nesting

For complex systems with 3+ levels (root → phase teams → sub-teams):

```
project-name/
└── spec/
    ├── manifest.yaml
    ├── progress.md
    └── root-pipeline/
        ├── team.md                    # Level 1: root orchestration
        ├── agent-config.yaml          # Lists sub-teams
        ├── research-team/             # Level 2: phase team
        │   ├── team.md               # Documents how it orchestrates children
        │   ├── agent-config.yaml     # Lists sub-teams + direct agents
        │   ├── agents/               # Direct agents at this level
        │   │   ├── synthesizer.md
        │   │   └── blender.md
        │   ├── keyword-loop/         # Level 3: leaf sub-team
        │   │   ├── team.md
        │   │   ├── agent-config.yaml
        │   │   └── agents/
        │   └── analytics-team/       # Level 3: leaf sub-team
        │       ├── team.md
        │       ├── agent-config.yaml
        │       └── agents/
        └── ideation-team/            # Level 2: phase team
            ├── team.md
            ├── agent-config.yaml
            └── agents/
```

**Rules for nested teams:**
- **Every team folder** at every level has its own `team.md` and `agent-config.yaml`
- **Parent team.md** documents orchestration: how it calls children, data flow between levels
- **Parent agent-config.yaml** includes `sub-teams` key listing child folders
- **A team can have both sub-teams AND direct agents** at the same level
- **Patterns are independent at each level** — a fan-in-fan-out parent can contain loop children

---

## Template-to-Instances Pattern

When multiple sub-teams share the same structure but differ in configuration (e.g., 5 platform-specific search loops):

1. **Create a template folder** with generic specs — mark it as "TEMPLATE — not instantiated directly"
2. **Create fully explicit instance folders** for each variant:
   - Each instance's `team.md` has ALL details inlined (not "see template" references)
   - Each instance's `agent-config.yaml` has all values filled in (Apify actor, platform, model)
   - Each instance's agent specs are self-contained — no shared specs between siblings
3. **Manifest lists each instance separately** — not grouped under the template
4. **Rationale:** The impl-builder should implement any instance by reading ONLY that instance's folder. Independent evolution, LLM maintainability, and traceability.

**Anti-pattern:** An instance spec that says "Same as research-loop but for LinkedIn keyword search" — this forces the impl-builder to cross-reference the template, losing context.

---

## Signature File Organization

Each team/sub-team folder gets its own signature definitions:
- DSPy: each team folder produces its own `signatures.py`
- LangGraph: each team folder produces its own `prompts.py`
- **No shared signature files between sibling teams** — even if instances start identical, each gets its own copy
- Agent specs reference their own team's signatures, not a parent or shared location
- **Rationale:** Same as template-to-instances — independent evolution and LLM maintainability

---

## Chunk-to-Spec-File Mapping

In the execution plan (manifest.yaml), every chunk MUST include `spec-files` — the exact spec file paths the impl-builder should read for that chunk:

```yaml
chunks:
  - name: research-loop-module
    stream: research
    description: ...
    spec-files:
      - research-team/research-loop/team.md
      - research-team/research-loop/agent-config.yaml
      - research-team/research-loop/agents/search-agent.md
      - research-team/research-loop/agents/analysis-agent.md
```

This prevents the impl-builder from guessing which files are relevant and ensures it reads exactly the right specs for each unit of work.

---

## Files to Generate

**Root level (spec/):**

| File | Template | Purpose |
|------|----------|---------|
| `manifest.yaml` | `templates/manifest.yaml` | Entry point - hierarchy overview, file list |
| `progress.md` | `templates/progress.md` | Handover between sessions |

**Per team folder:**

| File | Template | Purpose |
|------|----------|---------|
| `team.md` | `templates/team.md` | Team overview and orchestration |
| `agent-config.yaml` | `templates/agent-config.yaml` | This team's configuration |
| `agents/{agent}.md` | `templates/agent.md` | Detailed spec for each agent |

**Critical:**
- `manifest.yaml` must be kept in sync with the spec structure
- Each team folder is self-contained with its own `agent-config.yaml`
- Agent specs go in `agents/` subdirectory within each team folder
- Sub-teams have their own folder with their own config
- After generating these files, run the **Post-Generation Validation Checks** below, then proceed to **Phase 5: Execution Plan**

---

## Post-Generation Validation Checks

**These checks are BLOCKING — do not proceed to Phase 5 until all pass.**

### Check 1: Input/Output Validation Protocol

Trace every agent's inputs and outputs to verify consistency across the pipeline:

1. **For each agent**, list every input field it expects and every output field it produces
2. **Cross-reference upstream→downstream:** For every agent output field, verify the downstream agent lists a matching input field with the **exact same name**
3. **Cross-reference team→agent:** Verify that team-level input fields map to the first agent's inputs with exact field name matches
4. **Cross-reference agent→team:** Verify that the last agent's output fields map to team-level outputs with exact field name matches
5. **Flag mismatches:** Any field name discrepancy (e.g., `similar_creators` vs `creator_lists` vs `creator_list`) is a spec defect — fix before proceeding

**Validation table format (include in progress.md):**

| Field | Team Input | Agent 1 Input | Agent 1 Output | Agent 2 Input | ... | Team Output | Match? |
|-------|-----------|---------------|-----------------|---------------|-----|-------------|--------|

### Check 2: Data Flow Map

Produce a field-level data flow map tracing each piece of data from request to response:

| Data Field | Request Name | Team Input Name | Agent A Name | Agent B Name | Team Output Name | Response Name |
|-----------|-------------|-----------------|-------------|-------------|-----------------|--------------|
| Creator list | `similar_creators` | `similar_creators` | `similar_creators` | `creator_list` ← **MISMATCH** | `creator_list` | `creator_list` |

This catches naming inconsistencies that the I/O validation may miss at boundaries between non-adjacent components. Fix all mismatches before proceeding.

### Check 3: Instance Parity Check (Template-to-Instances only)

When using the template-to-instances pattern:

1. **Count lines/sections** in each instance spec
2. **Compare:** All instances should have equivalent detail levels (within ~20% line count)
3. **Flag imbalance:** If one instance has 600 lines and another has 200 lines, the shorter instance likely has missing sections or under-specified agents
4. **Fix:** Bring all instances to equivalent detail before proceeding

**Parity table format:**

| Instance | Line Count | Sections | Agents | Status |
|----------|-----------|----------|--------|--------|
| youtube-loop | 580 | 8/8 | 3/3 | ✅ |
| linkedin-loop | 210 | 5/8 | 3/3 | ❌ Missing sections |

### Check 4: Model Tier Validation

For each agent, verify the model tier is appropriate for the role:

| Agent | Role | Model Tier | Appropriate? |
|-------|------|-----------|-------------|
| critic-agent | Critic-Reviewer | Flash/Haiku | ⚠️ Critic roles need nuanced judgment — confirm this is intentional |
| router-agent | Router-Classifier | Flash/Haiku | ✅ Simple classification, fast model appropriate |

**Flag when model tier contradicts role guidance:**
- Critic-Reviewer or Planner-Strategist using economy-tier models (Flash, Haiku, Mini)
- Router-Classifier or Transformer-Formatter using premium-tier models (Opus, o1) without justification
- Any mismatch: prompt user "This agent uses [model] but its role ([role]) typically needs [tier]. Confirm this is intentional?"
