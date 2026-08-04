---
name: new-project
description: Scaffold a new project workspace in All Projects - workspace repo with Claude bundle, docs, onboarding, env config, clean code repo(s), private GitHub remotes, and vault note. Use when the user asks to create/start a new project. Args - project name, component names (e.g. backend frontend), optional --no-remote.
---

# New Project

Scaffold a workspace under `__PROJECTS_ROOT__/<name>/`. Scaffolding is governance
work — the root session runs this directly. Paths below: `FRAMEWORK` =
`__PROJECTS_ROOT__/.claude`, `WS` = the new workspace.

Ask for anything missing (name; components; stack per component) — ONE question at a time.
Names: workspace repo `<name>-workspace`; code repos `<name>-<component>`. All repos PRIVATE.

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
     `CLAUDE_SESSION_ROLE=__MACHINE_ROLE__` (this machine's default role, set at install)
   - `FRAMEWORK/templates/workspace.gitignore` → `WS/.gitignore`
   - `FRAMEWORK/templates/docs/*` → `WS/.claude/docs/` (+ empty `archive/`)
   - `FRAMEWORK/templates/HANDOFF.md` → `WS/.claude/HANDOFF.md` ("Nothing in progress")
   - `FRAMEWORK/templates/workspace-settings.json` → `WS/.claude/settings.json` (SessionStart
     self-onboarding hook)
2. **Claude bundle** (so any clone of the workspace has the full framework):
   - `FRAMEWORK/agents/*.md` → `WS/.claude/agents/`
   - `FRAMEWORK/rules/*.md` → `WS/.claude/rules/`
   - `FRAMEWORK/skills/onboard/` → `WS/.claude/skills/onboard/`
3. **Scratch:** create `WS/tmp/{screenshots,repos,briefs,research,scratch}/` (gitignored).
4. **Workspace repo:** `cd WS && git init && git add -A && git commit` ("Bootstrap <name>
   workspace"). Unless `--no-remote`:
   `gh repo create <name>-workspace --private --source . --push`.
5. **Code repos** — for each component:
   - Unless `--no-remote`: `gh repo create <name>-<component> --private --clone` into
     `WS/<component>/`; with `--no-remote`: `git init WS/<component>`.
   - Stack-appropriate `.gitignore` (NO Claude entries needed — Claude files never exist there).
   - Append `/<component>/` to `WS/.gitignore`; register the repo (name/path/url/branch) in
     `workspace.yaml`; commit the workspace repo.
6. **Vault note:** create `__VAULT_PATH__/01 - Projects/<name>.md` from
   `__VAULT_PATH__/05 - Templates/Project Note.md`; commit the vault.
7. **First CHANGELOG entry** is already in the docs template — confirm the date is today.
8. Report: tree of what was created, repo URLs, and what still needs filling (boundary, gates,
   onboarding specifics).
