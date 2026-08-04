---
name: adopt-project
description: Convert an existing project into a framework workspace - move it into All Projects, strip Claude files out of code repos, synthesize the six docs + CLAUDE.md + ONBOARDING.md from scout evidence, wire GitHub remotes and the vault note. Use when the user asks to adopt/migrate/onboard an existing project (e.g. from an old projects directory), or when a project is non-conforming (docs at root, oversized/missing CLAUDE.md, Claude files inside a code repo).
---

# Adopt Project

Converts a legacy project at any path into a workspace under
`__PROJECTS_ROOT__/<name>/`. Run by the root session; the doc synthesis uses
scouts. `FRAMEWORK` = `__PROJECTS_ROOT__/.claude`.

## Steps

1. **Confirm scope with the user first**: source path, workspace name, which directories become
   separate code repos (e.g. a Django dir and a React dir = two repos; a monolith = one).
   Moving is disruptive — state that venvs/node_modules will be rebuilt, not moved, and that
   absolute paths (docker volumes, IDE configs, cron) may break; get an explicit go.
2. **Workspace shell** exactly as in `new-project` steps 1–3 (templates, bundle, tmp/) — but do
   NOT fill docs yet.
3. **Move the code in.** `git mv`-preserving move of the legacy repo(s) into `WS/<component>/`.
   A legacy project that is one repo containing multiple deployables stays ONE code repo unless
   the user asked to split (splitting is its own mission later). Delete `venv/`,
   `node_modules/`, `__pycache__` before moving; note the rebuild in ONBOARDING.md.
4. **Strip Claude files from code repos**: `git rm` (in the code repo) CLAUDE.md, `.claude/`,
   briefs, any agent/scratch files. Their CONTENT is not lost: fold anything still true into the
   workspace docs in step 6. Commit the code repo ("Move Claude material to workspace").
5. **Scout inventory** (dispatch `scout` agents, parallel, read-only): structure + entry points;
   stack + dependencies + how it runs (docker? manage.py? package.json scripts?); existing docs/
   READMEs/commands; test setup and gates. Facts with file:line citations.
6. **Synthesize docs** (root writes, from scout evidence + any stripped content): the six
   `.claude/docs/` files, `WS/CLAUDE.md` (real boundary + real gates), `ONBOARDING.md` (real
   setup/launch/verify commands), `workspace.yaml` (register each code repo).
7. **Hygiene sweep**: stray root files → `tmp/` or propose deletion (bulk deletions need the
   user's sign-off naming targets).
8. **Remotes**: if the code repo already has a GitHub remote, keep it. Offer to create missing
   PRIVATE remotes (`<name>-workspace`, `<name>-<component>`) and push.
9. **Vault note** from the vault template — include the "adopted from <old path> on <date>"
   fact and key architecture summary.
10. **Verify**: run ONBOARDING.md end-to-end (setup → launch → health checks) before calling the
    adoption done; fix ONBOARDING.md until it's true.
11. Report: what moved where, repos created, docs written, anything that broke and how it was
    handled, what needs the user's attention.
