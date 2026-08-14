---
name: new-project
description: Scaffold a new project workspace in All Projects - workspace repo with Claude bundle, docs, onboarding, env config, clean code repo(s), private GitHub remotes, and vault note. Use when the user asks to create/start a new project. Args - project name, component names (e.g. backend frontend), optional --no-remote.
---

# New Project

Scaffold a workspace under `__PROJECTS_ROOT__/<name>/`. Scaffolding is governance
work — the root session runs this directly. Paths below: `FRAMEWORK` =
`__PROJECTS_ROOT__/.claude`, `WS` = the new workspace.

Ask for anything missing (name; components; stack per component; GitHub owner — an org or the
user's account) — ONE question at a time.
Names: workspace repo `<name>-workspace`; code repos `<name>-<component>`; created under the
chosen owner (`gh repo create <owner>/<repo>`), recorded as `github_org` in `workspace.yaml`.
All repos PRIVATE.

## Steps

1. **Workspace shell.** Create `WS/` and copy templates, filling `{{PROJECT_NAME}}`, `{{DATE}}`
   (today), URLs:
   - `FRAMEWORK/templates/workspace-CLAUDE.md` → `WS/CLAUDE.md` (fill the boundary + gates
     sections for the chosen stack; leave explicit `TODO(project)` markers only where genuinely
     unknowable yet)
   - `FRAMEWORK/templates/ONBOARDING.md` → `WS/ONBOARDING.md` (fill prerequisites/setup/launch
     for the stack as far as known)
   - `FRAMEWORK/templates/workspace.yaml` → `WS/workspace.yaml`
   - `FRAMEWORK/templates/example.env` → `WS/example.env`; also write `WS/.env` with
     `WORKSPACE_ROLE=__MACHINE_ROLE__` (this machine's default role, set at install) and the
     machine's `GIT_USER_NAME`/`GIT_USER_EMAIL`/`GITHUB_USERNAME`
   - `FRAMEWORK/templates/workspace.gitignore` → `WS/.gitignore`
   - `FRAMEWORK/templates/docs/*` → `WS/.claude/docs/` (+ empty `archive/`)
   - `FRAMEWORK/templates/HANDOFF.md` → `WS/.claude/HANDOFF.md` ("Nothing in progress")
   - `FRAMEWORK/templates/workspace-settings.json` → `WS/.claude/settings.json` (SessionStart
     self-onboarding hook)
2. **Claude bundle** (so any clone of the workspace has the full framework):
   - `FRAMEWORK/agents/*.md` → `WS/.claude/agents/`
   - `FRAMEWORK/rules/*.md` → `WS/.claude/rules/`
   - `FRAMEWORK/skills/onboard/` → `WS/.claude/skills/onboard/`
   - `FRAMEWORK/skills/researching/` → `WS/.claude/skills/researching/`
   - `FRAMEWORK/skills/team/` → `WS/.claude/skills/team/` and `FRAMEWORK/skills/finish/` →
     `WS/.claude/skills/finish/` (the orchestrator's execution + closeout machinery)
   - `FRAMEWORK/skills/build-loop/` → `WS/.claude/skills/build-loop/` (recurring-automation
     scaffolding — loops are proposed, never armed without sign-off)
   - `FRAMEWORK/templates/commands/sync.md` → `WS/.claude/commands/sync.md`; create `WS/scripts/`
     (empty — automation scripts land here as the automation-capture rule codifies flows)
   - `FRAMEWORK/scripts/session-pulse.ps1` + `session-pulse.sh` → `WS/.claude/scripts/`
     (the workspace settings hook runs them — deterministic staleness/size notices)
3. **Scratch:** create `WS/tmp/{screenshots,repos,briefs,research,scratch,gates,team}/`
   (gitignored). Fill `WS/.claude/docs/CONTEXT_PACK.md` with everything already known
   (stack, commands, gates, boundary) — it is the employees' onboarding pack.
3b. **Graph (optional):** if the `graphify` CLI is installed, build the code-pass graph once
   real code exists (`graphify <code dirs>` — vendor trees excluded, never the LLM semantic
   extraction) and run `graphify hook install` in each code repo so it refreshes per commit.
4. **Workspace repo:** `cd WS && git init && git add -A && git commit` ("Bootstrap <name>
   workspace"). Unless `--no-remote`:
   `gh repo create <owner>/<name>-workspace --private --source . --push`.
5. **Code repos** — for each component:
   - Unless `--no-remote`: `gh repo create <owner>/<name>-<component> --private --clone` into
     `WS/<component>/`; with `--no-remote`: `git init WS/<component>`.
   - Stack-appropriate `.gitignore` (NO Claude entries needed — Claude files never exist there).
   - Append `/<component>/` to `WS/.gitignore`; register the repo (name/path/url/branch) in
     `workspace.yaml`; commit the workspace repo.
6. **Vault note:** create `__VAULT_PATH__/01 - Projects/<name>.md` from
   `__VAULT_PATH__/05 - Templates/Project Note.md`; commit the vault.
7. **First CHANGELOG entry** is already in the docs template — confirm the date is today.
8. Report: tree of what was created, repo URLs, and what still needs filling (boundary, gates,
   onboarding specifics).
