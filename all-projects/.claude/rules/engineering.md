# Engineering standards (all sessions, all subagents)

- Production-grade the first time. No placeholders, no TODO-later, no temporary hacks, no half-finished work presented as done.
- Never hardcode what should be configurable: ports, URLs, credentials, model names, thresholds → config/env.
- Never change code you don't 100% understand — read the real source first (vendor trees, upstream libs), then edit.
- Surgical edits: touch what the task requires; no unrequested features, refactors, or doc files.
- Separation of concern: a feature lives entirely in its own module; dependencies point inward/down only; a feature never imports a sibling feature; shared needs move down into core; extend through registries/hooks/seams, never by editing core or a sibling to bolt a feature on. The test: removing a feature's module removes that feature entirely and leaves everything else working — if not, fix the boundary, never patch around it. Each workspace's CLAUDE.md / ARCHITECTURE.md defines the concrete boundary.
- YAGNI ruthlessly — but minimal never means half-built: the smallest slice that proves the feature must still be complete and production-grade.
- Done = verified, never assumed: the gate ran and its output is shown, and the change was exercised with the real tools it ships with (tests, API calls, CLI runs). UI done = driven through the real screen via Playwright MCP with screenshots saved to `tmp/screenshots/` and referenced in the report — a clean build or passing unit tests is never UI verification.
- Fix the root cause, not the symptom: no silent fallbacks, no broad `except`/`catch` that swallows errors, no retries that mask the bug, no hardcoded values to force green.
- Never weaken, skip, delete, or mock-out a failing test to make it pass. Fix the code, or state why the test is wrong and ask first.
- Circuit breaker: after 2 failed attempts at the same fix, stop — report what was tried, what was observed, current theory. Read the full error before changing anything; never re-run an unchanged command hoping for a different result.

## Clean architecture & reuse

- Functions and modules stay small and single-purpose; a file that's grown past one clear
  responsibility gets split, not extended.
- Rule of three before abstracting; when you do abstract, shared code moves DOWN into core/shared
  — never sideways into a sibling feature.
- Composition over inheritance; explicit interfaces/contracts at every seam.
- No copy-paste duplication across features: the second copy is a smell, the third is a bug.
- A boundary is real only if the unit behind it can be understood and tested in isolation.

## Project hygiene

- The repo tree stays clean. Every throwaway artifact — scratch scripts, debug output,
  screenshots, cloned reference repos, briefs, research dumps, one-off test files — goes in the
  workspace's gitignored `tmp/` (`tmp/screenshots/`, `tmp/repos/`, `tmp/briefs/`,
  `tmp/research/`, `tmp/scratch/`), never the repo root. Always explicit paths.
- Delete dead code; never leave it commented out.
- The leader sweeps stray files into `tmp/` or deletes them before every commit; reviewers flag
  stray files as an acceptance failure.
- Code repos contain ZERO Claude-related files (no CLAUDE.md, no `.claude/`, no briefs) — all
  Claude material lives in the workspace repo.
