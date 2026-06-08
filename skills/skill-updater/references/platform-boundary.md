# Platform Capability Boundary (operational)

> **When to read:** Before applying a change, to classify it as base (author once, both trees) or execution (per-platform), and to map a concrete tool name across platforms.

Distilled base/execution rules for updating skills across the Claude Code and Codex trees. This is the operational cheat-sheet; the canonical, fully-sourced version is `documents/operations/skill-platform-capability-boundary.md` in the cofounder vault — read it when you need provenance or confidence levels.

---

## The one-line boundary

The two platforms have **converged on the skill format** and **diverged on the orchestration runtime**. Skills are a shared open standard (`SKILL.md` + progressive disclosure + `references/`/`scripts/`/`assets/`, published at agentskills.io), so skill *reasoning* is portable as-is. What differs: frontmatter keys, sub-agent spawn/collect tool names, skill-invocation syntax, and one hard structural gap — **Codex has no peer-to-peer agent messaging** (parent-orchestrated only).

---

## BASE — author once, identical in both trees

- All elicitation/reasoning logic: coverage checklists, ask-on-ambiguity classes, pre-mortems, blocking validation gates, force-concreteness rules, scope-out rules, I/O-contract probes, reality-grounding.
- The `SKILL.md` body prose (shared format).
- All `references/` content — phase guides, checklists, doctrine, heuristics.
- `templates/` — spec/progress/output artifacts (neutral).
- Skill philosophy — why file-based prompts, when-to-use, model policy, non-tool-specific examples.

---

## EXECUTION — adapt per platform

| Concern | Claude Code | Codex CLI |
|---|---|---|
| Spawn a sub-agent | `Agent` tool (legacy `Task`), `subagent_type` | `spawn_agent`, `agent_type` |
| Built-in roles | `codebase-researcher`, `web-researcher`, `general-purpose`, `Explore` | `default` / `worker` / `explorer` |
| Collect results | implicit return; background notify | `wait_agent`; worker calls `report_agent_job_result` once |
| Follow-up to a child | `SendMessage` | `send_input` (parent→child) |
| Terminate a child | runtime-managed | `close_agent` |
| **Inter-agent coordination** | `SendMessage` peer mailbox + `blockedBy` task DAG (**experimental**, gated) | parent relays via `send_input` + `progress.md`/`update_plan` |
| Batch fan-out | parallel `Agent` calls | `spawn_agents_on_csv` |
| Skill invocation | `Skill` tool → `skill: "name"` | `$name`, or read the `SKILL.md` path |
| Frontmatter | keeps `allowed-tools` | omits `allowed-tools` (house style); optional `agents/openai.yaml` sidecar |
| Project memory file | `CLAUDE.md` | `AGENTS.md` |

---

## Two design rules (apply to every edit)

1. **Abstraction discipline.** Write base prose in neutral concepts — "delegate to a research sub-agent", "enforce a phase barrier", "the orchestration layer relays context". Confine the exact tool name + invocation to a single fenced "Execution" section. This converts *inline* divergence (the hard-to-sync kind that caused the drift) into *sectioned* divergence (the easy kind). With it, ≥90% of every reasoning skill is byte-identical across trees.

2. **Common denominator.** Claude's peer mesh is experimental and gated (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`); Codex is parent-orchestrated only. The robust model both platforms support is the **star** (parent spawns, relays, collects). Author the base around parent-relay orchestration; treat Claude's peer-mesh as a Claude-only execution enhancement — never a base assumption.
