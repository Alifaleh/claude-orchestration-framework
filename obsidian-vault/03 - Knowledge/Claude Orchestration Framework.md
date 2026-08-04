---
type: knowledge
tags: [claude, framework, orchestration]
created: __DATE__
---

# Claude Orchestration Framework

How all projects run. Installed at `__PROJECTS_ROOT__` by the framework distribution repo's
`/setup`.

## The layers

I talk only to the **root session** (launched in `__PROJECTS_ROOT__`). It routes:

- **Inline**: conversation, design, read-only questions, vault writes, tiny edits.
- **Fast path** (single-brief tasks): root writes the brief and dispatches a worker directly.
- **Full mission** (2+ briefs / cross-repo / architecture / risky): root writes a mission file
  and runs it **two-phase**: a plan-mode session in the workspace produces the execution plan
  (`claude -p --permission-mode plan --output-format json`, plan saved, session_id kept); root
  reviews it (user sign-off for any security-floor op); then the SAME session is resumed with
  `--permission-mode bypassPermissions` to execute without prompt stalls. Alternative for live
  supervision: dispatch the **project-orchestrator** agent in-session so permission prompts
  reach me in real time. Either way the orchestrator decomposes, dispatches workers, reviews
  everything, updates docs, and reports back.

Workers: `implementer` (all decision-bearing code), `scout` (recon, read-only), `reviewer`
(gates + Playwright UI checks; stronger-model override for risky diffs), `researcher`
(external/library research). Exact model routing is set at install — see the projects-root
CLAUDE.md. Workers never spawn agents. Nobody at an orchestration layer implements.

## Workspaces

Every project is a **workspace**: a private GitHub repo (`<name>-workspace`) holding CLAUDE.md,
`.claude/` (docs, agent bundle, rules, `/onboard` skill), ONBOARDING.md, `workspace.yaml`
(manifest of code repos), `example.env`/`.env`, gitignored `tmp/`. The actual code lives in
separate **Claude-free** code repos (`<name>-<component>`) nested inside — plus vendor/
reference trees (`kind: vendor` — cloned, read, never edited) and submodule superprojects —
each private under the project's GitHub owner (org or user account).

Team protocol via `.env` `WORKSPACE_ROLE` (`team_leader`/`team_member`; `.env` also carries
the machine's git identity): members work only via feature branch + PR and fix rejected PRs
first; the leader reviews, merges, bumps submodule pins, and triggers deploys — staging
first, always. A new collaborator clones the workspace and runs `/onboard` to get the full
environment cloned, configured, and launched.

Repetition becomes infrastructure: the second manual run of any flow (deploy, migration,
smoke test, release) is codified as a workspace command (`.claude/commands/` wrapping
`scripts/`), skill, or hook, and recorded in COMMANDS.md.

## Memory

- Workspace `.claude/docs/`: PROJECT, ARCHITECTURE, COMMANDS, CHANGELOG, LESSONS, BACKLOG —
  operational memory, committed and shared with the team. The leader-of-the-moment updates them
  (and CLAUDE.md/ONBOARDING.md) in the same session as the change.
- This vault: durable cross-project + personal memory. Main sessions write; subagents emit
  VAULT TRIGGERS. One note per project in `01 - Projects`.

## Key file locations

- Global rules + root protocol: `__PROJECTS_ROOT__/CLAUDE.md`
- Rules: `.claude/rules/` (engineering, project-docs, obsidian-vault, typescript, python)
- Agents: `.claude/agents/` (canonical; copied into each workspace bundle)
- Skills: `new-project`, `adopt-project`, `onboard` in `.claude/skills/`
- Templates: `.claude/templates/`
- Missions: `tmp/missions/` (ledger + per-project mission/report files)
- Settings: `~/.claude/settings.json` (model pin, attribution off, vault access)

## Session replaceability (handoff)

Every session is replaceable at any moment:

- Root keeps `.claude/HANDOFF.md` current (read FIRST at every root session start); workspace
  sessions keep `<ws>/.claude/HANDOFF.md` the same way, and orchestrator missions rewrite it
  at every mission end.
- A degraded session (compacted context, forgotten constraints, repeated questions) says so,
  brings its HANDOFF current, and recommends a fresh session.
- Verbatim resume also exists — `claude --resume <session-id>` per directory, headless
  included — but the handoff file is the primary, model-agnostic mechanism.

## Lessons (from the framework's own smoke tests)

- A gate shaped `python3 -m unittest discover -s tests -v` does not put the repo root on
  `sys.path`; tests must insert it themselves before `from src… import`.
- In HEADLESS runs (`claude -p`), subagents were denied Edit/Write on workspace
  `.claude/docs/` even with Edit in `--allowedTools`; the orchestrator correctly escalated
  `NEEDS-DECISION`. Interactive sessions edit those paths fine. RESOLVED by the two-phase
  protocol: execution runs with `--permission-mode bypassPermissions` after the plan is
  reviewed, so doc writes no longer stall headless missions.

## Adding / adopting projects

- New: `/new-project` — scaffolds workspace + code repos + GitHub remotes + vault note.
- Existing: `/adopt-project` — moves a legacy project in, strips Claude files from code repos,
  synthesizes docs from scout evidence.

*Last updated: __DATE__*
