---
description: Bring the root HANDOFF fully current and confirm the session is safe to close or rotate.
---

When the user types `handoff` (before closing the laptop, rotating a degraded session, or
handing over to a teammate):

1. Rewrite `.claude/HANDOFF.md` in place, fully current: in-flight work (mission/brief IDs,
   done vs pending), per-project one-liners, open decisions waiting on the user, agreements
   and context the next root session needs. Bump the footer date.
2. Sweep for anything captured NOWHERE yet: unprocessed mission reports in `tmp/missions/`,
   uncommitted changes (`git status` here and in touched workspaces), un-relayed
   NEEDS-DECISION items. Fold each into HANDOFF — or state plainly what remains unfinished.
3. Commit this repo (the HANDOFF is part of it).
4. Close with one of exactly two verdicts: "safe to close", or the list of what would be
   lost if closed right now.
