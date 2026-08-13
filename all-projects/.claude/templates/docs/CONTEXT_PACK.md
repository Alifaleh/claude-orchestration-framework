# Context pack — {{PROJECT_NAME}}            *Graph build: n/a · Last updated: {{DATE}}*

<!-- The employee onboarding pack: everything a fresh engineer/verifier/reviewer needs to
start working, in ~1 page. Kept current by the leader — a wrong pack produces defective
onboarding. Rewrite sections in place; keep it tight. -->

## What this is

_(3–5 sentences: what the product is, the stack, where it runs, the current branch and what
main means here.)_

## Read protocol (binding)

_(If the workspace has a graph: `graphify query "<question>" --budget 1500` FIRST — note what
the graph is strong/weak at and that it is commit-anchored (uncommitted changes invisible; on
conflict the working tree wins) → this pack → targeted Grep → whole-file Read last. No graph:
this pack → Grep → Read. Name the ARCHITECTURE.md sections that answer structural questions;
LESSONS.md by grep only.)_

## Module map

_(One line per module/tree: path — what it is, which direction dependencies point, where
shared code lives. The boundary rule in one line.)_

## The commands (verbatim — never guess)

| Purpose | Command |
|---|---|
| Scoped test (ONE module/file) | _(exact command, piped to `tmp/gates/<id>.log`)_ |
| Full test suite | _(exact command)_ |
| Run / develop | _(exact command)_ |
| Lint / typecheck | _(exact command)_ |

## Gates

_(GATE_SCOPED recipe and GATE_FULL recipe, verbatim — full gate is verifier-only; report the
runner's own summary, never a pre-recorded count. UI-verify recipe if the project has UI:
Playwright flow, screenshots to `tmp/screenshots/`, serialized through the verifier.)_

## Binding rules (the 3–5 that bite here)

- _(the project rules that actually catch people, one line each)_

## Current focus

_(What is being built right now, what just shipped, what is next — 3–6 lines, updated as it
changes.)_

## Employee conduct

Report format per your role def · append to `tmp/team/<name>/WORKLOG.md` every beat · never
expand WRITABLE · `exceeds-ability` is rewarded.
