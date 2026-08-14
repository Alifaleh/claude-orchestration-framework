# Ponytail — lean-code discipline (all sessions)

The ponytail plugin (github.com/DietrichGebert/ponytail) injects its "lazy senior dev" ladder —
does this need to exist → does it already exist here → stdlib → platform-native → installed
dependency → one line → only then write the minimum — into every session (SessionStart) and
into engineer subagents (SubagentStart). It operates WITHIN the engineering standards: its
never-cut list (trust-boundary validation, data-loss error handling, security, accessibility)
matches the security floor. The ladder trims scope, never rigor.

## Levels — switch with `/ponytail <level>`

- `full` (default) — every coding session and engineer beat.
- `ultra` — only when the user asks, or for throwaway scratch scripts; NEVER on a
  security-critical (hard-trigger) surface.
- `lite` — long design sessions where full proves noisy.
- `off` — pure-prose sessions (docs, vault, drafting).
- Machine default: `/ponytail default <level>` (config `~/.config/ponytail/config.json`;
  `%APPDATA%\ponytail\config.json` on Windows). Resolution: env → config file → `full`.

## The features, used professionally

- **`/ponytail-review`** — over-engineering pass on the current diff: a delete-list, applies
  nothing. Leaders run it when a diff smells gold-plated; the reviewer employee carries the
  equivalent criterion on every beat.
- **`/ponytail-audit`** — whole-repo cut-list, ranked biggest-first. Run it when adopting
  legacy code (the adopt-project skill offers it); findings land in BACKLOG.md as candidates,
  report-only — cuts are routed as normal beats, never applied from the audit itself.
- **`ponytail:` markers** — THE sanctioned way to record a deliberate ceiling: the comment
  names the ceiling and the upgrade trigger (`# ponytail: O(n²) scan, fine under 1k rows;
  revisit past 10k`). Ad-hoc TODOs stay banned; a marker with no named trigger is a defect.
- **`/ponytail-debt`** — harvests the markers into a ledger. The finish skill runs it at
  closeout; deltas go to BACKLOG.md.
- **Mode-reset gotcha:** `/ponytail-review` persists mode `review` in the plugin's flag file —
  subagents then receive review-mode text instead of the ladder. After ANY review/audit pass,
  run `/ponytail full` (or the machine default) to restore.
- **Subagent scoping:** `PONYTAIL_SUBAGENT_MATCHER=engineer` (settings `env`) injects the
  ladder only into engineer employees; scout/verifier/reviewer/researcher stay clean. Haiku
  follows the ladder poorly (upstream benchmark) — harmless on transcription briefs, which
  spell out the exact change anyway.
- **Statusline badge:** the plugin nudges once to add a `[PONYTAIL]` badge to the statusline —
  offer it once, respect the answer, never re-raise.
- **Update:** rides the plugin marketplace (`claude plugin marketplace update ponytail`, then
  `/reload-plugins`) — independent of framework versions.
