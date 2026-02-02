# Change Spec: [Feature Name]

**Date:** YYYY-MM-DD
**Status:** Draft | Under Review | Approved | Implemented
**Priority:** Low | Medium | High | Critical

---

## Request

[Original user request - verbatim or summarized]

**Type:** Feature | Enhancement | Bug Fix | Integration | Performance

---

## Analysis

### Current State

[How the system works now - findings from codebase-researcher]

- **Architecture:** [Brief overview]
- **Relevant files:** [List of files that matter]
- **Current behavior:** [What it does now]

### Research Findings

[What was learned from web-researcher - APIs, libraries, patterns]

- **Recommended approach:** [Chosen solution]
- **Alternatives considered:** [Other options and why not chosen]
- **Documentation:** [Links to relevant docs]

### Impact Assessment

| Metric | Value |
|--------|-------|
| Files affected | X |
| New files | Y |
| New dependencies | Z |
| Risk level | Low / Medium / High |
| Estimated complexity | Simple / Moderate / Complex |

---

## Changes

### New Files

#### `path/to/new/file.py`

**Purpose:** [What this file does]

**Key components:**
- `ClassName`: [purpose]
- `function_name()`: [purpose]

**Depends on:** [Other changes that must complete first]

**Skeleton:**
```python
# Brief code structure (not full implementation)
class NewComponent:
    def __init__(self):
        pass

    def main_method(self):
        pass
```

---

### Modified Files

#### `path/to/existing/file.py`

**Current:** [What it does now]
**After:** [What it will do]
**Reason:** [Why this change is needed]

**Specific changes:**
1. Line ~XX: Add import for `new_module`
2. Line ~YY: Add new function `new_function()`
3. Line ~ZZ: Modify `existing_function()` to call `new_function()`

**Before:**
```python
# Current code snippet
```

**After:**
```python
# Modified code snippet
```

---

### Prompt Changes

#### Agent: [agent-name]

**Current behavior:** [How it behaves now]
**New behavior:** [How it should behave after change]

**Changes to prompt:**
- [ ] Add instruction: `"[new instruction text]"`
- [ ] Modify constraint: `"[old]"` → `"[new]"`
- [ ] Add example: [description of new example]
- [ ] Update output format: [description]

---

### New Tools

#### `tool_name`

**Purpose:** [What the tool does]
**Implementation type:** MCP Server | Existing API | SDK/Library | Custom

| Field | Value |
|-------|-------|
| Documentation | [URL] |
| Package/API | [name] |
| Auth required | Yes / No |

**Input schema:**
```python
class ToolInput(BaseModel):
    param1: str  # Description
    param2: int  # Description
```

**Output schema:**
```python
class ToolOutput(BaseModel):
    result: str  # Description
```

**Error handling:**
| Error | Cause | Handling |
|-------|-------|----------|
| [Error type] | [When it occurs] | [How to handle] |

---

### Dependencies

#### Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| package-name | >=X.Y.Z | [Why needed] |

#### Environment Variables

| Variable | Purpose | How to Obtain |
|----------|---------|---------------|
| `VAR_NAME` | [What it's for] | [Instructions] |

#### External Services

| Service | Purpose | Setup |
|---------|---------|-------|
| [Service] | [Why needed] | [Link or instructions] |

---

## Implementation Order

Tasks must be completed in this order:

1. [ ] Add dependencies (`uv add ...`)
2. [ ] Create new files (in dependency order)
3. [ ] Modify existing files
4. [ ] Update prompts
5. [ ] Update `.env.example`
6. [ ] Test changes

**Dependency graph:**
```
dependencies
    ↓
new files
    ↓
modified files ← prompt changes
    ↓
.env.example
    ↓
testing
```

---

## Testing Checklist

### New Functionality
- [ ] [Test case for new feature 1]
- [ ] [Test case for new feature 2]

### Regression
- [ ] Existing functionality X still works
- [ ] Existing functionality Y still works

### Edge Cases
- [ ] [Edge case 1]
- [ ] [Edge case 2]

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | Low/Med/High | Low/Med/High | [How to address] |

---

## Rollback Plan

If issues occur after implementation:

1. Revert file changes: `git checkout HEAD~1 -- [files]`
2. Remove new dependencies: `uv remove [package]`
3. [Any other rollback steps]

---

## Notes

[Any additional context, decisions made, or things to remember]
