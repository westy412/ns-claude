# Progress Tracking & Cross-Session Resumption

> **Context:** This reference covers maintaining progress.md for task tracking and how to resume implementation across sessions. Read this when starting a new session or needing to track implementation progress.

---

## Progress Tracking

Maintain a task list throughout implementation:

```markdown
# [Project Name] - Implementation Progress

## Status

**Current Phase:** Scaffold | Tools | Agents | Prompts | Utils
**Last Updated:** YYYY-MM-DD

## Tasks

| Task | Status | Dependencies | Notes |
|------|--------|--------------|-------|
| team.py scaffold | done | - | |
| tools.py | done | scaffold | |
| Implement creator | done | tools.py | |
| Implement critic | in_progress | tools.py | |
| Prompt: creator | pending | creator impl | |
| Prompt: critic | pending | critic impl | |
| utils.py | pending | - | May not be needed |

## Completed Files

- [x] team.py (scaffold)
- [ ] team.py (full)
- [ ] tools.py
- [ ] prompts.py
- [ ] utils.py

## Notes

[Implementation decisions, issues encountered, etc.]
```

---

## Cross-Session Resumption

Implementation of large systems (10+ agents, nested teams) will span multiple sessions. The `progress.md` file is the mechanism for cross-session continuity.

**How to resume from progress.md:**

1. Read `progress.md` — it contains resumption instructions at the top
2. Check **Current Phase** and **Next Chunk** to know where to pick up
3. Read the **Execution Plan Snapshot** to understand the full build order without re-parsing manifest.yaml
4. Check **Stream Status** for per-stream progress
5. Check **Open Questions / Blockers** for anything needing resolution
6. Read the framework cheatsheet (path is in progress.md Status section)
7. If team mode: re-create the team via `TeamCreate`, create remaining tasks from the Execution Plan Snapshot (only uncompleted chunks), and spawn teammates for streams with remaining work
8. Continue from the **Next Chunk**

**Keeping progress.md current:**

- Update **Current Phase** and **Next Chunk** whenever you move to a new chunk
- Update chunk status in the **Execution Plan Snapshot** (pending → in_progress → done)
- Update **Stream Status** after each chunk completion
- Add entries to **Session Log** at the start and end of each session
- Add blockers to **Open Questions / Blockers** immediately when encountered
- Update progress.md BEFORE ending a session — the next session depends on it
