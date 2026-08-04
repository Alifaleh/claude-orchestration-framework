# {{PROJECT_NAME}} — Onboarding

How a fresh session or human goes from `git clone` of this workspace to a running project.
`/onboard` follows this file top to bottom — keep it current whenever env/setup/launch changes.

## 1. Prerequisites

_(Exact tools + versions. Example: git, docker + compose plugin, uv, node 20 via nvm, gh CLI.)_

## 2. Code repos

Clone every repo in `workspace.yaml` into this workspace directory (paths are relative to the
workspace root). `/onboard` does this automatically.

## 3. Environment files

- Workspace: `cp example.env .env`, then set your git identity (`GIT_USER_NAME`,
  `GIT_USER_EMAIL`, `GITHUB_USERNAME`) and `WORKSPACE_ROLE` (`team_leader` = reviews/merges
  PRs; `team_member` = works via PRs only), plus any keys below.
- _(Per-repo env files: which file to copy where, and which keys need real values. Refer to
  secrets by NAME only — values come from the team lead, never from this repo.)_

## 4. Setup

_(Ordered, copy-pasteable commands from the workspace root. Example:_
```bash
cd backend && uv sync
cd frontend && npm install
```
_)_

## 5. Launch

_(The one blessed way to run the project. Example: `docker compose up -d` from `backend/`, then
`npm run dev` from `frontend/`.)_

## 6. Verify

_(Health checks that prove it's up. Example: `curl -s http://localhost:8000/api/health/` returns
200; frontend at http://localhost:3000 renders the login page.)_

## 7. Common issues

_(Known traps and their fixes — append as they're discovered.)_

*Last updated: {{DATE}}*
