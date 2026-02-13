# Phase 0: Setup

Project initialization and session resumption. This phase establishes the project folder structure and spec directory before any design work begins.

---

## First Actions

1. **Ask the user:**
   - "Are you creating a new project folder, or adding a spec to an existing project?"

2. **If creating new project:**
   - Ask: "What should the project folder be called?"
   - Create: `[project-name]/spec/`
   - Initialize `manifest.yaml` and `progress.md` from templates

3. **If existing project:**
   - Ask: "What's the path to the existing project folder?"
   - Create: `[project-path]/spec/`
   - Initialize `manifest.yaml` and `progress.md` from templates

4. **If resuming work:**
   - Read `spec/progress.md` FIRST — this is the authoritative state document
   - Review: Current Phase, Decisions Made, Discovery Substance, Open Questions, Next Steps
   - Read `spec/manifest.yaml` only if progress.md references spec files that exist
   - DO NOT re-read discovery documents, handover messages, or other source material already summarized in progress.md
   - DO NOT invoke any child skills until you reach a phase that needs them
   - Resume from the exact point described in "Next Steps" and "Resumption Instructions"
   - If progress.md indicates a phase is partially complete, read only the specific child skill needed for that phase

**Do not proceed until the project folder and spec directory are confirmed.**

---

## Directory Structure

```
project-name/
└── spec/
    ├── manifest.yaml      # Entry point - read this first
    ├── progress.md        # Handover tracking
    └── [team-name]/       # Team folder (self-contained)
        ├── team.md
        ├── agent-config.yaml
        └── agents/
            └── [agent].md
```

The progress document tracks:
- Current phase
- Decisions made (with rationale)
- Discovery findings
- Design overview
- Per-agent progress
- Open questions
- Next steps

**Update this document throughout the process.**
