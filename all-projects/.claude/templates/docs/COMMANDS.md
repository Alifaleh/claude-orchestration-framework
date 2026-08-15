# COMMANDS — {{PROJECT_NAME}}

The written-down way to run things. A command documented here is never guessed. Check before
running anything; add every new frequent command in the same session.

All commands run from the workspace root unless stated; always `cd <repo> && …` form.

## Gates (define "done")

_(Per repo, recorded WITH redirection baked in — `cmd > tmp/gates/<name>.log 2>&1` (sh) /
`cmd *> tmp\gates\<name>.log` (PowerShell) — so every runner inherits the evidence diet by
copy-paste. Example: `cd backend && uv run ruff check . && uv run mypy . && uv run pytest > tmp/gates/full.log 2>&1`)_

## Run / develop

_(Dev servers, docker compose, watchers.)_

## Database

_(Migrations, seeds, resets — destructive entries marked ⚠ SIGN-OFF REQUIRED.)_

## Misc

*Last updated: {{DATE}}*
