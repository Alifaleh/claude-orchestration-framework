# Project docs (all workspaces)

Every workspace keeps six docs in `.claude/docs/`: PROJECT, ARCHITECTURE, COMMANDS, CHANGELOG,
LESSONS, BACKLOG (+ `archive/`). They are committed to the workspace repo — they are the team's
shared memory. "The leader" below = whoever governs the change: the project orchestrator, or the
root session on a fast-path task.

**Session start in a workspace:** read the newest ~5 CHANGELOG entries; PROJECT.md on first
visit. As needed: ARCHITECTURE.md's relevant section before structural work; LESSONS.md via grep
when touching a related area — never read it whole; COMMANDS.md before running anything (a
written-down command is never guessed); BACKLOG.md when planning.

**Update in the same session as the change** (the leader writes; workers never edit shared docs —
their reports carry DOC TRIGGERS instead):
- arch/data-flow change → ARCHITECTURE.md
- shipped or decided → dated CHANGELOG.md entry (newest first)
- non-obvious gotcha or subtle bug → LESSONS.md (newest first)
- new frequent command → COMMANDS.md
- scope change → PROJECT.md
- backlog item started or thought of → BACKLOG.md
- a correction, gate change, or boundary decision that should bind future sessions → the
  workspace **CLAUDE.md** (keep it under ~15 KB; overflow detail into ARCHITECTURE/LESSONS)
- env/setup/launch change → **ONBOARDING.md**
- in-progress state changed, mission ended (any STATUS), or session pausing/degrading →
  **`.claude/HANDOFF.md`** (live working state, rewritten in place — a fresh session must be
  able to resume from it alone)
- bump each edited doc's `*Last updated: YYYY-MM-DD*` footer.

**Mission-start reconciliation:** compare `git log` (all repos) since the newest CHANGELOG entry
date; commits or a dirty tree with no doc trail = drift — backfill or flag it before new work.

**Bootstrap/migration trigger** — a project with the six docs at its root, an oversized
(>~15 KB) CLAUDE.md, no CLAUDE.md at all, or Claude files inside a code repo is non-conforming:
run the `adopt-project` skill's doc-migration flow.
