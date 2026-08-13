# Project docs (all workspaces)

Every workspace keeps seven docs in `.claude/docs/`: CONTEXT_PACK, PROJECT, ARCHITECTURE,
COMMANDS, CHANGELOG, LESSONS, BACKLOG (+ `archive/`). They are committed to the workspace
repo — the team's shared memory. CONTEXT_PACK.md is the employees' onboarding pack (~1 page:
what-this-is, read protocol, module map, verbatim commands, gate recipes, binding rules,
current focus) — a wrong pack produces defective onboarding, so it is kept current like code.
"The leader" below = whoever governs the change: the project orchestrator, or the root
session on a fast-path task.

**CRITICAL — query-first read protocol (binds every session and every worker):** in any
workspace that has `.claude/docs/CONTEXT_PACK.md` or `graphify-out/graph.json`, the read
order is: `graphify query "<question>" --budget 1500` (where the graph exists) →
CONTEXT_PACK.md → targeted Grep → whole-file Read, last and least. Grep-crawling the tree
before querying the graph/pack is a protocol violation. The graph never outranks grep
results, tests, or vendor source — it is commit-anchored and blind to uncommitted changes;
on conflict, the working tree wins.

**CRITICAL — graph builds are the CLI's local code pass only** (`graphify <dir>` —
tree-sitter, deterministic, free, no LLM; the CLI installs with `pip install graphifyy`).
Any LLM semantic extraction over docs/PDFs/media fans out subagents and is FORBIDDEN without
the user's explicit per-run approval; vendor trees are always excluded from builds.

**Session start in a workspace:** read CONTEXT_PACK.md, then the newest ~5 CHANGELOG entries;
PROJECT.md on first visit. As needed: ARCHITECTURE.md's relevant section before structural
work; LESSONS.md via grep when touching a related area — never read it whole (on a miss,
grep `archive/`); COMMANDS.md before running anything (a written-down command is never
guessed); BACKLOG.md when planning; INFRASTRUCTURE.md (workspace root, when present) before
touching deployment or production infrastructure — it is the as-built handbook.

**Size hygiene (run before the first work beat of a session):** any `.claude/docs/*.md` over
100 KB or ~1,500 lines → ONE haiku archival beat: move the OLDEST entries verbatim to
`archive/<FILE>-<year>.md` until the live file is back under ~60 KB, always keeping at least
the newest ~30 LESSONS / ~15 CHANGELOG entries; leave one tail line pointing there. Check:
`find .claude/docs -name '*.md' -size +100k` (sh) or
`Get-ChildItem .claude/docs/*.md | Where-Object Length -gt 100KB` (PowerShell). If
`graphify-out/graph.json` is more than ~20 commits behind HEAD, refresh it
(`graphify hook status` should show hooks installed; else rebuild).

**Update in the same session as the change** (the leader writes; employees never touch shared
docs — their reports carry DOC TRIGGERS + PACK flags instead):
- module map, verbatim commands, gate recipes, or current focus changed → **CONTEXT_PACK.md**
- arch/data-flow change → ARCHITECTURE.md
- shipped or decided → dated CHANGELOG.md entry (newest first)
- non-obvious gotcha or subtle bug → LESSONS.md (newest first)
- new frequent command → COMMANDS.md
- a flow run manually for the SECOND time → codify it as a workspace command/skill/hook
  (automation-capture rule) and record it in COMMANDS.md
- infra/deploy topology change → INFRASTRUCTURE.md (workspace root; create it when the project
  runs real infrastructure)
- scope change → PROJECT.md
- backlog item started or thought of → BACKLOG.md
- a correction, gate change, or boundary decision that should bind future sessions → the
  workspace **CLAUDE.md** (keep it under ~15 KB; overflow detail into ARCHITECTURE/LESSONS)
- env/setup/launch change → **ONBOARDING.md**
- in-progress state changed, mission ended (any STATUS), or session pausing/degrading →
  **`.claude/HANDOFF.md`** (live working state, rewritten in place — a fresh session must be
  able to resume from it alone)
- bump each edited doc's `*Last updated: YYYY-MM-DD*` footer.

**Mission-start reconciliation:** compare `git log` (all repos) since the newest CHANGELOG
entry date; commits or a dirty tree with no doc trail = drift — backfill or flag it before
new work.

**Bootstrap/migration trigger** — a project with the docs at its root, an oversized (>~15 KB)
CLAUDE.md, no CLAUDE.md at all, or Claude files inside a code repo is non-conforming: run the
`adopt-project` skill's doc-migration flow.
