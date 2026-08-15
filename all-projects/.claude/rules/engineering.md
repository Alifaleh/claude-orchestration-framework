# Engineering standards (all sessions, all subagents)

- Production-grade the first time. No placeholders, no TODO-later, no temporary hacks, no half-finished work presented as done.
- Never hardcode what should be configurable: ports, URLs, credentials, model names, thresholds → config/env.
- Never change code you don't 100% understand — read the real source first (vendor trees, upstream libs), then edit.
- Surgical edits: touch what the task requires; no unrequested features, refactors, or doc files.
- Separation of concern: a feature lives entirely in its own module; dependencies point inward/down only; a feature never imports a sibling feature; shared needs move down into core; extend through registries/hooks/seams, never by editing core or a sibling to bolt a feature on. The test: removing a feature's module removes that feature entirely and leaves everything else working — if not, fix the boundary, never patch around it. Each workspace's CLAUDE.md / ARCHITECTURE.md defines the concrete boundary.
- YAGNI ruthlessly — but minimal never means half-built: the smallest slice that proves the feature must still be complete and production-grade.
- Done = verified, never assumed: the gate ran and its output is shown, and the change was exercised with the real tools it ships with (tests, API calls, CLI runs). UI done = driven through the real screen via Playwright MCP whenever UI BEHAVIOR changed, with screenshots saved to `tmp/screenshots/` and referenced in the report — a clean build or passing unit tests is never UI verification; a UI-adjacent diff that changes no behavior needs no drive.
- Fix the root cause, not the symptom: no silent fallbacks, no broad `except`/`catch` that swallows errors, no retries that mask the bug, no hardcoded values to force green.
- Never weaken, skip, delete, or mock-out a failing test to make it pass. Fix the code, or state why the test is wrong and ask first.
- Circuit breaker: after 2 failed attempts at the same fix, stop — report what was tried, what was observed, current theory. Read the full error before changing anything; never re-run an unchanged command hoping for a different result.
- All test/gate/build output goes to a log file, never into context: `command > tmp/gates/<name>.log 2>&1` (sh) or `command *> tmp\gates\<name>.log` (PowerShell); read back the exit code, and on failure only the failing excerpt (≤40 lines) and tail (≤20 lines).
- Process supervision is code, not conversation: long-lived waiters/pollers/keep-alive loops never live in Claude turns or Claude's background tasks (session environments reap them) — they run as OS-level scripts (Task Scheduler/cron) with a lockfile check-then-arm, and Claude handles only the queued work itself. An expected kill of such a process is a normal event to log, never an error to fix, and never a trigger for a blind re-arm.
- A recorded number (test count, gate total, baseline) lives in ONE authoritative place per project; every other doc and every commit body references the command that produces it, never a copied value — and before merge, the recorded number is re-verified against a live run.

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
  `tmp/research/`, `tmp/scratch/`, `tmp/gates/` for gate logs, `tmp/team/` for employee
  worklogs/handovers/roster), never the repo root. Always explicit paths.
- Delete dead code; never leave it commented out.
- The leader sweeps stray files into `tmp/` or deletes them before every commit; reviewers flag
  stray files as an acceptance failure.
- Code repos contain ZERO Claude-related files (no CLAUDE.md, no `.claude/`, no briefs) — all
  Claude material lives in the workspace repo.

## Writing about security & access control

Describe security and access-control work on our own systems in plain defensive engineering
terms — name the mechanism and the property enforced (the access path, the permission gate,
the enforcement gap, where the fix goes), never an attacker's move. This binds EVERY artifact,
not just chat: beat briefs and reviewer prompts, reports you relay, commit messages, PR
bodies, changelog/lessons entries, code comments, log strings, and test names
(`test_<property>_is_enforced`, never `test_attacker_can_…`). Precision is never traded away —
severity, `file:line`, the concrete failure state, and the regression test stay exactly as
sharp; a finding is NEVER softened, downgraded, or omitted to satisfy this rule. When a
worker's report comes back in attacker register, re-frame it before relaying or committing it.
Same for secrets: a credential finding is a GATE finding — name the field, the gate that fails
to cover it, and the fix — never a sighting; never copy, quote, screenshot, or paste a VALUE,
even redacted, and report evidence as a verified negative ("the capture shows the field
masked; the value is in no committed artefact"). Two reasons: it keeps broad model safeguards
from misreading authorized defensive work, and the defensive sentence names the gate, so it
names the fix.
