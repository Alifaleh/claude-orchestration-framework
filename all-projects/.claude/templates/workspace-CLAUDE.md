# {{PROJECT_NAME}} — Workspace Rules

{{ONE_OR_TWO_SENTENCES_WHAT_THIS_PROJECT_IS}}

This is a **workspace repo**: it holds Claude material and team memory. The actual code lives in
the code repos listed in `workspace.yaml` — those repos contain ZERO Claude-related files.

## Session start

0. Read `.claude/HANDOFF.md` FIRST — the previous session's live state; you are its
   replacement. Keep it current as you work (every mission/pause/state change) and bring it
   fully up to date before recommending a fresh session when this one degrades (compacted
   context, forgotten constraints, repeated questions).
1. Read `.env` → `CLAUDE_SESSION_ROLE` (leader/member) — it governs your git flow.
2. `git fetch` this repo and every code repo in `workspace.yaml`; pull fast-forward; surface
   divergence instead of resolving it silently.
3. Read the newest ~5 entries of `.claude/docs/CHANGELOG.md` (PROJECT.md on first visit).
4. **member**: check `gh pr status` — changes-requested PRs get fixed before new work.
   **leader**: check `gh pr list` across the code repos — review, then merge or request changes.
5. Fresh clone / broken environment → run `/onboard`.

## Requirements & verification

- Before starting any new feature or behavior change requested by the user, run the
  `superpowers:brainstorming` skill — collect ALL requirements one question at a time until you
  are sure you know everything they need; the agreed requirements become the SPEC.
- Nothing is "done" until verified with real tools: gates run with output shown; UI driven
  through the real screen via Playwright MCP with screenshots in `tmp/screenshots/` cited as
  evidence.

## Team git flow

- All code work on feature branches; `main` is integration-only for every role.
- **member**: push the branch, `gh pr create`; never merge, never push `main`.
- **leader**: reviews PRs (delegate diff checks to the `reviewer` agent), merges or requests
  changes with concrete comments; self-merges own PRs only after review.
- This workspace repo is direct-commit with pull-rebase (docs are memory, not product).

## Module boundary

_(REQUIRED — the concrete boundary the engineering rule enforces. Example: "each Django app under
`backend/apps/` is a feature module; apps never import each other; shared code lives in
`backend/core/`. Frontend features live in `frontend/src/features/<name>/`; shared UI in
`frontend/src/components/`.")_

## Gates

_(The commands that define "done" here — per code repo. Example:_
- _backend: `cd backend && uv run ruff check . && uv run mypy . && uv run pytest`_
- _frontend: `cd frontend && npx tsc --noEmit && npm run lint`)_

## Critical rules

_(Project-specific rules that bind every session. Kept current: when a correction, gate change,
or boundary decision should stick, it lands here in the same session — keep under ~15 KB,
overflow detail to `.claude/docs/ARCHITECTURE.md` / `LESSONS.md`.)_

## Pointers

- Docs: `.claude/docs/` (PROJECT, ARCHITECTURE, COMMANDS, CHANGELOG, LESSONS, BACKLOG)
- Environment & launch: `ONBOARDING.md` · Repo manifest: `workspace.yaml`
- Scratch: `tmp/` (gitignored) — screenshots/, repos/, briefs/, research/, scratch/

*Last updated: {{DATE}}*
