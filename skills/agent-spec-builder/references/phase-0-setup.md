# Phase 0: Setup

Project initialization and session resumption. This phase establishes the project folder structure and spec directory before any design work begins.

---

## First Actions

1. **Check for existing spec folder:**
   - Ask: "Is there an existing spec folder from the discovery skill, or are we starting fresh?"

2. **If a spec folder exists** (created by discovery or brainstorm skill):
   - The folder is at `[workforce-root]/specs/YYYY-MM-DD-feature-name/`
   - It already contains `discovery.md`, possibly `brainstorm.md`, `feedback/`, and `progress.md`
   - Create the `spec/` subdirectory inside it for the agent spec
   - Create: `[spec-folder]/spec/` with `manifest.yaml` from template
   - **Use the centralized `progress.md`** at the spec folder root — do NOT create a separate progress.md inside `spec/`. Update the existing `progress.md` with agent-spec-builder status.

3. **If starting fresh** (no discovery, or older workflow):
   - Ask: "What's the workforce root and what should we call the spec folder?"
   - Create the full structure: `[workforce-root]/specs/YYYY-MM-DD-feature-name/`
   - Create `spec/` subdirectory with `manifest.yaml` from template
   - Create a single `progress.md` at the spec folder root (NOT inside spec/)
   - Create `feedback/` placeholder

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

### Spec Folder Convention (preferred)

```
[workforce-root]/specs/YYYY-MM-DD-feature-name/
  discovery.md            # From discovery skill (already exists)
  brainstorm.md           # Optional (already exists if applicable)
  progress.md             # SINGLE centralized progress file (ALL skills read/write this)
  feedback/               # Placeholder for implementation verification
  spec/                   # Agent spec folder (YOU CREATE THIS)
    ├── manifest.yaml     # Entry point - read this first
    ├── overview.md       # System context, architecture, decisions (populated in Phase 4)
    └── [team-name]/      # Team folder (self-contained)
        ├── team.md
        ├── agent-config.yaml
        └── agents/
            └── [agent].md
```

**IMPORTANT:** There is ONE progress.md at the spec folder root. Do NOT create a separate progress.md inside `spec/`. All skills in the pipeline (brainstorm, discovery, spec-builder, review, implementation, verification) read and write the same centralized `progress.md`.

### Legacy Structure (if no spec folder exists)

```
project-name/
└── spec/
    ├── manifest.yaml
    ├── overview.md
    ├── progress.md
    └── [team-name]/
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
