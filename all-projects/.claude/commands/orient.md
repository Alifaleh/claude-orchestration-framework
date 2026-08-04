---
description: Re-ground this session — who it is, what this place is, what's in flight, what's next.
---

When the user types `orient` (any time — after compaction, after a break, or when the session
feels lost):

1. Re-read the role-detection section of the CLAUDE.md at this directory's root and state
   your role plainly (at the All Projects root: the ROOT ORCHESTRATOR — a judgment engine
   that routes, reviews, and governs; it never implements project code).
2. Read `.claude/HANDOFF.md` (the previous session's brain dump — you are its replacement),
   the tail of `tmp/missions/LEDGER.md`, and the age of `.claude/last-update-check`.
3. Reconcile HANDOFF against reality: `git status`/`git log` here, unprocessed mission
   reports in `tmp/missions/`. Flag drift instead of papering over it.
4. Report, short: who you are · framework version (`.claude/VERSION`) · in-flight work ·
   open decisions waiting on the user · update-check status · the ONE next action you
   recommend. Then wait — do not start work the user didn't ask for.
