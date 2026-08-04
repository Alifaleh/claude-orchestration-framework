---
type: project
status: active        # active | paused | done
stack: []             # e.g. [django, react, postgres]
workspace: __PROJECTS_ROOT__/<name>
repos: []             # e.g. [<name>-workspace, <name>-backend, <name>-frontend]
tags: [project]
created: {{DATE}}
---

# {{PROJECT_NAME}}

## What & why

_(2–4 sentences: what this project is, who it serves, why it exists.)_

## Status

_(One short paragraph, updated as things change — current phase, what works, what's next.)_

## Architecture summary

_(The shape in a few lines: components, how they talk, where the boundaries are. Operational
detail lives in the workspace's `.claude/docs/ARCHITECTURE.md` — this is the durable summary.)_

## Key decisions

- {{DATE}} — _(decision and the WHY)_

## Lessons that travel

_(Only lessons that would matter to another project or a future quarter.)_

## Links

- Workspace: `__PROJECTS_ROOT__/<name>`
- Repos: _(GitHub links)_

*Last updated: {{DATE}}*
