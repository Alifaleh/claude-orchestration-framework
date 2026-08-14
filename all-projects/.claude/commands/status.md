---
description: Progress report across all projects — state, in-flight work, blockers, and an estimated finish per project.
---

When the user types `status` (or asks for a progress report):

1. Enumerate the projects: workspace directories here (directories containing `.claude/`),
   cross-checked against the root HANDOFF's Projects section.
2. Collect per project — more than ~3 active projects → dispatch one `scout` per project in
   parallel and synthesize their reports; fewer → read directly:
   - workspace `.claude/HANDOFF.md` (in-flight, next steps)
   - newest ~5 entries of `.claude/docs/CHANGELOG.md` (recent velocity)
   - `BACKLOG.md` Now/Next (what remains)
   - open PRs (`gh pr list`) where the project has remotes
   - this project's lines in `tmp/missions/LEDGER.md`
   - where `LOOP.md` exists: loop health — last-run age from the `loop-run-log.md` tail,
     open `## High Priority` escalations in `STATE.md`
3. Report ONE block per project:
   - **State** — one sentence: live/building/paused, and what changed lately.
   - **In flight** — missions, briefs, branches right now, or "nothing".
   - **Blockers** — open decisions, failing gates, NEEDS-DECISION items.
   - **Estimate** — remaining Now/Next volume against recent cadence, stated as a range WITH
     its basis ("4 backlog items at ~2/week → ~2 weeks"). No data → say "no basis to
     estimate". Never invent a date; an estimate without a basis is a guess and is labeled
     as one.
4. End with one cross-project line: what needs the user's decision today, and where the next
   hour of attention buys the most.
