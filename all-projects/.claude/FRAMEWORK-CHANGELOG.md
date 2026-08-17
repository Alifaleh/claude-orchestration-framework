# Framework Changelog

The framework's version lives in `.claude/VERSION` (semver: MAJOR = breaking protocol change,
MINOR = new capability/rule, PATCH = fix/wording). Every entry below records WHAT changed and
the ordered **Upgrade steps** a session must apply to move an existing install to that version.

## Update protocol (read when told to "update the framework")

1. Get the distribution repo's latest state (clone/pull) and read its `VERSION` and this
   changelog.
2. Compare with the local `.claude/VERSION`. Same → nothing to do. Local NEWER → stop and tell
   the user (local changes were never pushed).
3. Apply the **Upgrade steps of every version between local and latest, in order, one version
   at a time** — never blind-overwrite the whole tree (local machine state like
   `.claude/HANDOFF.md` and per-machine settings must survive). Steps touching EXISTING
   workspaces are dispatched to workers as per-workspace briefs (haiku for spelled-out
   surgery, opus for judgment-bearing steps; parallel — workspace trees are disjoint), each
   result reviewed before the version is declared applied. A version whose steps introduce a
   new tool, plugin, or CLI dependency → OFFER the install to the user first (one question;
   always ask before system-level installs); declined or failed → record it in HANDOFF and
   continue — the framework must degrade gracefully without it.
4. After the last step: write the new version to `.claude/VERSION`, re-sync every existing
   workspace's `.claude` bundle (agents/rules/onboard skill), commit the All Projects repo,
   and — if this machine maintains the distribution repo — commit and push the change there.

## Release protocol (when changing the framework locally)

Any framework change (CLAUDE.md, rules, agents, skills, templates, hooks) = bump
`.claude/VERSION`, add an entry here (changes + upgrade steps), sync workspace bundles, commit,
and push the distribution repo. No unversioned framework edits.

---

## 4.0.1 — 2026-08-18

The ~250k leader-carriage restriction is removed (user decision, 2026-08-18): no numeric
carriage target and no auto-compact override anywhere in the framework. The session-lifecycle
discipline is unchanged — state on disk at decision time, /clear at boundaries always safe,
compaction a safety net — only the 250k ceiling and its mechanical backstop are gone.

- **Settings:** `CLAUDE_CODE_AUTO_COMPACT_WINDOW` deleted from
  `settings/settings-fragment.json` (auto-compact returns to the client default).
- **Docs:** carriage-target text removed from `all-projects/CLAUDE.md` (session lifecycle
  paragraph), `all-projects/.claude/agents/project-orchestrator.md` (leader-hygiene
  sentence), and the team skill (leader-hygiene block + the session-close carriage audit
  flag).

**Upgrade steps:**
1. Delete the `CLAUDE_CODE_AUTO_COMPACT_WINDOW` key from the `env` block of
   `~/.claude/settings.json`.
2. Re-sync the workspace `.claude` bundle (CLAUDE.md, project-orchestrator agent, team
   skill) from this repo.
3. Write `4.0.1` to `.claude/VERSION`.

## 4.0.0 — 2026-08-17

Machine work leaves the agent loop. Measured trigger (2026-08-17): a week's allowance 83%
gone in 30 hours — three parallel orchestrator marathons at 280–335k avg carried context,
~25 gate invocations per ~20-line beat, 48–144 md files/day/project, 9 escalations in one
wave with a 1-hour halt on a routine write-grant. Cost identity: spend = calls × carried
context; these changes move tests to hooks, batch ceremony to wave boundaries, and
pre-authorize routine grants — checks change WHEN and WHO, never WHETHER.

- **Test-gate hook pair (new `scripts/test-gate.py` + `scripts/stop-gate.py`; settings.json
  PostToolUse `Edit|Write|NotebookEdit` + Stop entries):** every edit runs the project's
  test slice per `.claude/gates.json` (template: `skills/team/templates/gates.json` —
  ordered glob rules, `{file}` placeholder, `"slice": null` opt-out). Green = silent
  exit 0, zero tokens. Red = the failing tail fed back, and a fresh red slice blocks
  "done" (30-min freshness, 2-block self-disarm, per-session state — one session's red
  never blocks another). No gates.json = hook inert.
- **Test frequency ladder + weight tiers (`rules/engineering.md`; evidence diet in the
  orchestrator rules):** per-edit slice (hook) < per-beat GATE_SCOPED < per-wave GATE_FULL
  launched by the verifier in the BACKGROUND — the wave closes only on green — < milestone
  battery/full mutation/paid evals. Tiers LIGHT/STANDARD/TRIGGER-2 mirror model routing;
  trigger-2 keeps full weight per beat. UI done = a headless Playwright SPEC passing; an
  agent-driven browser drive only for flows with no spec yet — and that beat writes the
  spec.
- **STANDING RULINGS (brief template; team skill; engineer def):** briefs pre-authorize
  routine grants (new test files beside changed code, lang/i18n keys, tmp/ writes,
  additions inside WRITABLE trees) — used and logged in the report, never halted on.
- **Escalation batching (foreman def; orchestrator rules):** BLOCKING parks that beat while
  the wave's other beats continue — the orchestrator is interrupted mid-wave only when the
  WHOLE wave stops; every other escalation batches into the wave report.
- **Artifact diet (engineer def; `rules/project-docs.md`):** per-beat WORKLOG dropped — the
  beat report is the record; doc writes batch at wave boundaries with ONE dated CHANGELOG
  entry per wave; LESSONS only for a gotcha that would change a future action.
- **MCP diet (`rules/project-docs.md`):** disable MCP servers the workspace's work doesn't
  use — server schemas ride every API call's context.
- **Burn visibility (`token-report.py --yesterday-summary`; session-pulse):** one cached
  line at session start — yesterday's total tokens + top project.

Upgrade steps:
1. Pull; sync the rule/agent/skill/template text changes into existing workspaces'
   `.claude` bundles (text-level; per-machine settings survive).
2. Copy `test-gate.py` + `stop-gate.py` + updated `token-report.py` + session-pulse into
   `.claude/scripts/`; merge the PostToolUse + Stop hook entries into settings.json in
   that machine's existing hook style.
3. Per project: create `.claude/gates.json` from the template with the project's REAL
   slice commands (`"slice": null` where no fast per-file run exists); verify with one
   edit — green is silent, red shows the tail.
4. Restart or /clear sessions to load the hooks; wave-boundary doc cadence and STANDING
   RULINGS apply from the next wave.

## 3.9.0 — 2026-08-16

Plan diet: a scope gate at plan time. Measured trigger: asked post-hoc, an orchestrator
identified 2.5–3 cuttable days in a plan's remaining 4–5 — half the remaining spend was fat
that quality never needed, surfaced only because the user asked after execution had started.
Scope was gated at code time (lean-code ladder) and at execution (criteria, reviews) but
never at plan time, where scope is decided; execution agents are correctly forbidden from
re-scoping, so plan fat gets built.

- **Plan diet (project-orchestrator.md PLAN phase; team skill pre-flight):** every plan
  opens by naming its DELIVERABLE — the few measurable properties that define quality for
  the delivery. Every beat carries a rough cost (beats or days) and one line naming the
  DELIVERABLE property or mission/SPEC decision it serves; an item that can't name one is
  FAT — cut to BACKLOG.md with its cost and re-entry trigger before the plan is presented.
  Fat smells, cut on sight: speculative robustness (retry/batching/tuning/limit work for
  failures nobody measured while a working baseline path exists) · duplicate affordance (a
  second path to an action already reachable in a click or two) · requirement inflation (a
  mechanism was needed; a feature grew around it) · bundled cleanup (dead-code deletion or
  refactors riding a delivery plan). Verification is the one exception: a redundant-looking
  gate is FLAGGED with a one-line risk note and cut only by the user's explicit decision —
  checks never loosen. Never-cut floor: trust-boundary validation, data-loss handling,
  security, accessibility, anything the user explicitly asked for. Cut ITEMS, never
  completeness — what stays is built production-grade. The plan shown for approval carries
  per-beat costs + the cut list, so the user adjudicates with prices visible. Desk-tested
  against the measured case: all six post-hoc cuts classify under the smells, with the
  redundant second live run correctly landing in the verification exception.

**Upgrade steps:**

1. Sync the `.claude` bundle into each workspace: `agents/project-orchestrator.md`,
   `skills/team/SKILL.md`.
2. Any in-flight plan: run the diet ONCE against its remaining work and present the cut
   list (costs + BACKLOG destinations) to the user before dispatching the next wave.

## 3.8.0 — 2026-08-16

Leader-spend fix + crew modes. A 3-day marathon orchestrator session measured at 56% of its
project's weighted token spend (1,471 leader turns · 3.82M output tokens · ~383k average
carried context · never cleared). Causes in evidence order: a project doc ordering the leader
to never idle (358 notification wakes, each converted to work at top-tier pricing × 383k
carriage), the leader acting as bookkeeper/message bus (281 Edits + 86 SendMessages in the
leader), pre-3.7.0 architecture for the session's whole life, carriage never reset. 3.8.0
makes leader dormancy law and adds user-controlled execution fan-out.

- **Dormancy is law (project-orchestrator.md, team skill):** between wave dispatch and wave
  report the orchestrator is DORMANT. A notification that is not the awaited wave report
  (grandchild hires/completions, intermediate stops) ends the turn immediately — no status
  writes, no spot-reads, no "while I'm awake" work. The stalled-foreman backstop (one
  SendMessage) stays the only exception. Supremacy line: project docs scope WHAT to build,
  never the leader's turn discipline — an always-on-leader clause in a project doc is a
  defect to flag and fix, never to obey.
- **Plan-by-path dispatch (team skill, foreman.md):** the wave dispatch carries the plan file
  PATH + wave heading — never the pasted section. The foreman's FIRST action is reading that
  wave section from disk as verbatim law; a missing or ambiguous heading → STOP and escalate.
  Its report cites the plan path + heading.
- **Liveness off the leader (project-orchestrator.md):** in-wave liveness = the foreman's
  foreground dispatches plus bounded report-file polls for SendMessage continuations;
  cross-session liveness = an OS-level script proposed via BACKLOG with user sign-off —
  never a leader wake loop. Dry-run finding (supersedes 3.7.0's blocking-TaskOutput
  guidance): TaskOutput is unavailable inside subagents, and child completions notify the
  root session only — a nested orchestrator dispatches its foreman FOREGROUND, always.
- **Bookkeeping at boundaries (team skill):** HANDOFF/roster/ledger updates at wave
  boundaries + user decisions only — never per event (measured: per-event updates produced
  281 leader Edits in one session). Session-close audit adds: leader Edit/Write count grossly
  exceeding wave count = bookkeeping drift.
- **Crew modes (templates/example.env + workspace-CLAUDE.md, team skill, foreman.md,
  session-pulse.sh/.ps1):** `CREW_MODE=<solo|duo|full>` in the workspace `.env` (config, not
  a secret); absent or unknown = `solo`. solo = ONE engineer lane, serial beats, ONE combined
  top-tier review per wave over non-hard-trigger diffs (criteria still ticked per beat) ·
  duo = ≤2 file-disjoint lanes, same review batching · full = 3–5 lanes, per-beat reviews +
  T-light batching (the 3.7.0 behavior). Hard-trigger beats keep top-tier engineer + per-beat
  review in EVERY mode — security-critical work is never crew-scoped. Verifier/scout/
  researcher unchanged. Switched ONLY on the user's ask, via
  `sed -i 's/^CREW_MODE=.*/CREW_MODE=<new>/' .env` (or `echo CREW_MODE=<new> >> .env` when
  absent) — never by shell-printing `.env`. The session pulse surfaces the mode only when set
  and non-default (the pulse also fires on UserPromptSubmit; absence = documented default).

**Upgrade steps:**

1. Sync the `.claude` bundle into each workspace: `agents/foreman.md`,
   `agents/project-orchestrator.md`, `skills/team/SKILL.md`, `scripts/session-pulse.sh` +
   `.ps1`, `templates/example.env`, `templates/workspace-CLAUDE.md`.
2. Append `CREW_MODE=solo` to each workspace `.env` (`echo CREW_MODE=solo >> .env`) and add
   the CREW_MODE block to its `example.env`.
3. RESTART any long-lived orchestrator session started before 3.8.0 — a running context
   carries the old rules at full carriage; nothing lands in a running session.
4. Audit project CLAUDE.md files for always-on-leader clauses (never-idle mandates, hourly
   leader liveness loops); rewrite them to dormant-until-report with foreman/OS-level
   liveness before the next session.

## 3.7.0 — 2026-08-15

Calibration layer: same output quality, less waiting and fewer tokens. A wave-scoped foreman
takes the per-beat management load off the orchestrator, employees keep their context across
beats instead of re-onboarding, a routing-floor hook makes the model-alias mandate mechanical,
and verification is right-sized to what each beat actually risks.

- **Foreman (new `agents/foreman.md`):** a wave-scoped execution lead — orchestrator(0) →
  foreman(1) → employees(2), inside the documented nesting limit. The orchestrator writes the
  plan with per-beat acceptance criteria, dispatches ONE foreman per wave (sonnet; top tier
  when the wave carries a hard-trigger beat) with the plan section verbatim, then goes
  dormant. The foreman briefs roster employees (criteria copied verbatim — it authors none),
  pipelines beats and reviews, runs fix rounds 1–3 against the same live engineer, and
  escalates round-4 promotions and any requirement ambiguity instead of guessing. Its wave
  report carries per-beat reviewer verdicts VERBATIM, gate exit codes + `tmp/gates/` log
  paths, files touched, `AUTOMATION:` flags, escalations, and the wave's duration + dispatch
  count — paraphrased quality claims are invalid. Waves of ≥2 beats route through a foreman;
  a single-beat wave dispatches the employee directly. Waiting discipline (dry-run finding):
  a nested agent is NOT re-invoked when its children complete — the foreman dispatches
  foreground when the next action depends on one child, and collects overlapping background
  children with blocking `TaskOutput`; it never stops its turn mid-wave to "wait". The
  leader-side backstop: a foreman notification without its wave report = stalled wave →
  one SendMessage resumes it.
- **Employee continuity (hire once, continue by message):** employees are LIVE background
  agents, not spawn-per-beat. Hired ONCE at first need; every later beat and every fix round
  is a SendMessage continuation of the same living agent — project understanding is read
  exactly once. A fresh Agent dispatch for an already-hired name is a protocol violation.
  Rosters record each employee's live agent ID. Approaching the ~150-message checkpoint an
  employee writes its HANDOVER checkpoint, retires, and a successor is rehired FROM the
  checkpoint — continuity by disk when context is full, by SendMessage until then.
- **Routing-floor gate (PreToolUse deny hook on Agent):** new `scripts/routing-floor.py`
  (python stdlib, fail-open on malformed input, test battery beside it) denies any Agent
  dispatch that names NO `model` and whose `subagent_type` is not in the pinned-model set
  (scout, verifier, reviewer, researcher, engineer, foreman, and the built-in pinned types).
  An unset model silently inherits the root session's model — on top-tier sessions a 10×-cost
  accident, measured live at 184 such dispatches in one session. The deny message names the
  routing floor and the fix (re-dispatch with an explicit `model:` alias).
- **Verification right-sizing (same properties, fewer invocations):** GATE_FULL runs once
  per WAVE (verifier-run, gates wave acceptance; GATE_SCOPED per beat unchanged). Light
  beats — ≤~50 changed lines, single module, no hard-trigger surface, scoped gate green —
  share ONE combined review pass per wave, criteria still ticked per beat; standard and
  hard-trigger beats keep per-beat review. Debugging with certain reproduction in a single
  module is ONE dispatch (diagnose → written cause + failing test → fix; the cause artifact
  precedes the fix in the report); the separate diagnosis beat stays for uncertain
  reproduction or cross-module bugs. A fresh test-writer is dispatched only for
  hard-trigger/cross-module invariants — routine beats write their tests FIRST in-beat,
  order visible in the report. UI drives (Playwright) are required when UI BEHAVIOR changed,
  not for any UI-adjacent diff.
- **Carriage discipline:** COMMANDS.md records gate commands WITH redirection baked in
  (`cmd > tmp/gates/<name>.log 2>&1`) so the evidence diet travels by copy-paste; the brief
  template and engineer def carry the ~150-message CHECKPOINT clause; the orchestrator gains
  a read budget (bulk reading >3 files or >500 lines of raw material is collection —
  delegate to a scout/researcher).

**Upgrade steps** (from 3.6.0), on each installed machine:
1. Copy `agents/foreman.md` from the distribution tree into the install's `.claude/agents/`.
   Agent definitions load at session start — the `foreman` type is dispatchable from the
   NEXT session onward, not the one applying this upgrade.
2. Copy `scripts/routing-floor.py` and `scripts/test-routing-floor.py` into
   `.claude/scripts/`; run the battery once (`python .claude/scripts/test-routing-floor.py`)
   and expect all green. Same python dependency note as 3.6.0 step 2 (already satisfied on
   machines that applied it).
3. Merge the second `hooks.PreToolUse` group (matcher `Agent` → routing-floor.py) from the
   distribution `settings.json` into the install's `.claude/settings.json`, preserving the
   existing `Bash|PowerShell` security-floor group; verify the file still parses.
4. Replace with the 3.7.0 copies: `agents/project-orchestrator.md`, `agents/engineer.md`,
   `rules/engineering.md`, `skills/team/SKILL.md`, `skills/team/templates/ROSTER.md`,
   `templates/brief.md`, `templates/docs/COMMANDS.md`.
5. Update the root protocol `CLAUDE.md` to the 3.7.0 copy — three changed paragraphs: the
   model-alias paragraph (routing-floor hook sentence), the debugging paragraph
   (one-dispatch form), and the evidence-diet paragraph (GATE_FULL per WAVE).
6. Existing workspace ROSTER.md files gain the `agent id` column on their next team session
   (the template now carries it; no retroactive edit needed — `—` marks not-yet-hired).
7. Write `3.7.0` to `.claude/VERSION`.

## 3.6.0 — 2026-08-15

Automation-adoption layer: sessions notice a capability gap or a repeated manual flow and
build the right Claude Code artifact for it — plus a mechanical enforcement floor under the
sign-off rules.

- **Security-floor gate (PreToolUse deny hook):** new `scripts/security-floor.py` (python
  stdlib only, single process, ~55ms), wired in `settings.json` `hooks.PreToolUse` with
  matcher `Bash|PowerShell`. It enforces the sign-off rule mechanically for the unambiguous
  shapes: force-pushes, `DROP TABLE|DATABASE|SCHEMA`, `TRUNCATE`, `DELETE FROM` without
  `WHERE`, `gh repo delete`, recursive deletes targeting paths outside tmp/scratchpad, and
  commands that print `.env` values. A denied command exits 2 with a one-line reason naming
  the sign-off rule; after the user's explicit sign-off the session re-runs the IDENTICAL
  command prefixed `CLAUDE_SIGNED_OFF=1` — a transcript-visible two-step, never a rephrase.
  The gate fails open on malformed hook input by design: it is a backstop under the rules,
  and availability outranks a backstop. Rules stay the primary control; the hook makes the
  floor deterministic under permission auto-mode.
- **`skill-finder` skill — vetted community-skill adoption:** registry search with a
  mandatory vetting pipeline: provenance gate (`rawFileUrl` host must be
  `raw.githubusercontent.com` AND its owner/repo must match the claimed namespace),
  full-content review checklist (purpose match; no fetch-and-execute, no credential access,
  no prompt-injection shapes, no obfuscated payloads; `scripts/` excluded by default), then
  **transcribe-don't-adopt**: the installed skill is authored by us from the reviewed
  content, with our own ≤25-word description — a poisoned description is persistent
  injection that survives a one-time review. Workspace-local installs only, provenance line
  in the workspace CHANGELOG, and no registry CLI execution ever.
- **`claude-code-map` skill — need→feature routing:** the decision table mapping observed
  repetition/friction to the native feature (command, skill, hook, agent, MCP, loop,
  permission tuning, statusline, settings edit), the creation policy (create-then-report
  for workspace-scoped commands/skills/agents; user sign-off for hooks running new code,
  anything global, MCP servers, armed loops), the audit procedure, and the currency rule
  (no local feature inventory — stale by construction; fetch official docs or dispatch the
  guide agent on demand).
- **Automation-audit anchors:** the audit has deterministic firing points instead of a
  repetition detector (repetition is semantic; hooks never call an LLM). `adopt-project`
  step 6 and the `finish` skill's closeout sweep run it and write the marker; `team` beat
  reports and one-off dispatch reports flag manual flows run ≥2× with `AUTOMATION:`; the
  automation-capture rule in `CLAUDE.md` routes skill gaps through `skill-finder` and
  everything else through the `claude-code-map` table. The session pulse (`.sh` + `.ps1`
  workspace branch) nudges when `.claude/automation-audit` is absent or older than 30 days
  — the marker stores the date as file CONTENT (`YYYY-MM-DD`; mtime does not survive
  clone), and the nudge rides the existing 4-hour cooldown.

**Upgrade steps** (from 3.5.0), on each installed machine:
1. Copy the two new skill directories from the distribution tree into the install's
   `.claude/skills/`: `skill-finder/` and `claude-code-map/`.
2. Dependency check for the gate: it needs python ≥3.8 on PATH (stdlib only). Machines where
   only `python3` resolves use `python3` in the hook command. No python at all → OFFER the
   install to the user first (per the update protocol); declined → skip step 3, record in
   HANDOFF — the sign-off rules remain the control and the framework degrades gracefully.
3. Copy `scripts/security-floor.py` into `.claude/scripts/`; merge the `hooks.PreToolUse`
   block from the distribution `settings.json` into the install's `.claude/settings.json`,
   preserving existing hook groups; verify the file still parses before moving on.
4. Replace `.claude/scripts/session-pulse.sh` and `session-pulse.ps1` with the 3.6.0 copies
   (same wiring; the workspace branch adds the automation-audit staleness check). Workspace
   bundles carrying their own pulse copies are re-synced as per-workspace briefs per the
   update protocol.
5. Marker semantics — no pre-seeding: `.claude/automation-audit` is written by the first
   audit (adopt-project step 6 or the finish sweep). Until then the pulse nudges "never run"
   at most once per 4-hour window per workspace; that nudge is the intended adoption path,
   not an error.
6. Write `3.6.0` to `.claude/VERSION`.

## 3.5.0 — 2026-08-15

- **1-hour prompt-cache TTL pinned:** `env.ENABLE_PROMPT_CACHING_1H = "1"` joins the settings
  fragment. Subscription sessions default to the 1-hour cache TTL but silently drop to 5
  minutes whenever usage credits draw; the pin keeps the long TTL. Orchestrator sessions are
  exactly the shape that loses on the short TTL — long-lived leaders with multi-minute waits
  between turns (subagents working) re-read a large stable prefix every turn; a cache miss
  re-bills that prefix at full input weight, a hit at 0.1×.

**Upgrade steps** (from 3.4.0), on each installed machine:
1. Merge into `~/.claude/settings.json`: `env.ENABLE_PROMPT_CACHING_1H = "1"` (preserve
   existing env keys; verify the file still parses). Takes effect on NEW sessions.
2. Write `3.5.0` to `.claude/VERSION`.

## 3.4.0 — 2026-08-15

Context-window settings hardening. Current top models carry the 1M window natively and
included — since March 2026 there is no >200k pricing premium and no 200k variant left to
choose — so the real levers are removing a live bug surface and braking runaway session
carriage:

- **`[1m]` model suffixes are banned.** On natively-1M models the suffix buys no context and
  arms a live client bug (anthropics/claude-code#79337, open through 2.1.233): on Max-plan
  installs a suffixed model either blocks the session behind a bogus "requires usage
  credits" prompt or SILENTLY swaps the running session onto a different 1M model. The
  Fable-tier setup mapping now fills `__MODEL__` with plain `"claude-fable-5"`; the root
  protocol's Session lifecycle paragraph records the ban.
- **Global auto-compact backstop:** `env.CLAUDE_CODE_AUTO_COMPACT_WINDOW = "250000"` joins
  the settings fragment, sitting just above the leader ritual's ~250k carriage target —
  disciplined sessions never hit it; runaway marathons get mechanically braked (measured on
  the maintainer's machine: sessions averaging ~500k context per message were 44% of a
  month's weighted token spend). A deliberate deep design session raises it per-session with
  `/autocompact`. Auto-compaction firing in a leader session is a ritual miss (state
  belonged on disk + /clear), never a rescue.
- **`CLAUDE_CODE_SUBAGENT_MODEL` is banned** (root protocol alias paragraph +
  project-orchestrator): the env var silently overrides even explicit per-dispatch `model:`
  aliases, defeating the routing table and the alias mandate.

**Upgrade steps** (from 3.3.0), on each installed machine:
1. Edit `~/.claude/settings.json`: strip any `[1m]` suffix from the `model` value
   (`"claude-fable-5[1m]"` → `"claude-fable-5"` — same window either way; skip if the key is
   absent); merge `env.CLAUDE_CODE_AUTO_COMPACT_WINDOW = "250000"` preserving existing env
   keys; verify the file still parses before moving on. If `CLAUDE_CODE_SUBAGENT_MODEL` is
   set anywhere (settings env, shell profile, hooks) → remove it.
2. Re-apply the 3.4.0 block edits to PROJECTS/CLAUDE.md, copying from the distribution tree:
   the `CLAUDE_CODE_SUBAGENT_MODEL` sentence at the end of the alias paragraph; the
   auto-compact-backstop + suffix-ban sentences at the end of the Session lifecycle
   paragraph. Re-apply the machine's tier swaps where those paragraphs carry them.
3. DISPATCH the standard per-workspace bundle re-sync for the updated
   `agents/project-orchestrator.md` — one haiku brief per workspace, parallel, each result
   reviewed.
4. Fable-tier installs — relay a one-minute user check: open `/model` and look at the Fable
   row; if it shows "Requires usage credits", headless `claude -p` runs on that model bill
   credits SILENTLY (no consent prompt exists there) — pin `--model opus` (or another
   included model) on headless and scheduled runs. Record the outcome in HANDOFF.
5. Write `3.4.0` to `.claude/VERSION`; note in HANDOFF that the settings changes take effect
   on NEW sessions.

## 3.3.0 — 2026-08-14

Two tools join the framework, both serving one principle now written into the root protocol:
Claude Code should USE its own native features — hooks, skills, commands, subagents,
`/loop`, scheduled tasks — on the user's behalf; users don't ask for features they don't
know exist, so the orchestrator names the right one when a need matches.

- **ponytail** (plugin, `DietrichGebert/ponytail`, MIT) — the anti-over-engineering "lazy
  senior dev" ladder, installed via the plugin marketplace and ON at `full` everywhere. NEW
  `rules/ponytail.md` (levels and when; `ponytail:` ceiling markers as the sanctioned
  deliberate-debt convention; the `/ponytail-review` mode-reset gotcha; marketplace update
  flow). Subagent injection is scoped to the engineer via
  `PONYTAIL_SUBAGENT_MATCHER=engineer` in the settings `env` block. The reviewer gains an
  over-engineering REJECT criterion; `finish` runs `/ponytail-debt` in its open-item sweep;
  `adopt-project` offers `/ponytail-audit` on adopted code (findings → BACKLOG.md,
  report-only).
- **loop-engineering** (`cobusgreyling/loop-engineering`, MIT — npx CLI, nothing installs
  globally) — NEW leader-only `build-loop` skill: pattern pick (7 patterns) → cost estimate
  (`npx @cobusgreyling/loop cost`) → explicit user sign-off (hard gate) → scaffold in the
  workspace (`npx @cobusgreyling/loop init . --pattern <p> --tool claude`) → framework
  hardening (the scaffolded `loop-verifier.md` ships `model: inherit` and is ALWAYS
  rewritten to an explicit alias; the scaffold ships no `gate.yaml`, so one is created with
  the security floor as denylist; constraints/budget/COMMANDS/CHANGELOG wiring; the
  scaffolded AGENTS.md folds into the workspace CLAUDE.md) → native-first scheduling ladder
  (`/loop` attended · scheduled tasks are session-scoped cron, gone with the session ·
  OS scheduler + `claude -p --model sonnet` when it must survive restarts) → L1 report-only
  week one; graduation is user-owned, never score-owned.
- Automation-capture taxonomy completes to **command / skill / hook / loop** (root
  CLAUDE.md + project-orchestrator), plus the full-power principle paragraph in the root
  protocol. `/status` reports loop health where `LOOP.md` exists; the session pulse
  (both scripts) surfaces STATE.md `## High Priority` loop escalations, root and workspace.
- README: full-power + lean-code bullets, Node ≥18 recommended. Setup: node preflight (new
  Phase 0 step 4), ponytail marketplace + install in Phase 1, loop-CLI pre-warm in Phase 3
  step 4b, handoff line in Phase 5. Vault knowledge note updated.

**Upgrade steps** (from 3.2.0), on each installed machine:
1. NEW TOOL OFFERS (ask first, per the Update protocol): (a) the ponytail plugin —
   `claude plugin marketplace add DietrichGebert/ponytail` then
   `claude plugin install ponytail@ponytail` (its two lifecycle hooks need `node` on PATH;
   without node the skills still work and the hooks stay quiet); (b) Node.js ≥18 where
   missing (also powers the loop-engineering CLI). Declined or failed → record in HANDOFF
   and continue — everything degrades gracefully.
2. Root session applies to the projects root, copying from 3.3.0: NEW `rules/ponytail.md`
   and NEW `skills/build-loop/`; replace `agents/reviewer.md`,
   `agents/project-orchestrator.md`, `skills/finish/SKILL.md`,
   `skills/adopt-project/SKILL.md`, `skills/new-project/SKILL.md`, `commands/status.md`,
   `scripts/session-pulse.sh` + `session-pulse.ps1`; re-apply the CLAUDE.md block edits
   (automation-capture paragraph, the new full-power paragraph after it, the
   rules-directory line). Re-apply the machine's tier swaps (Sonnet tier:
   `agents/reviewer.md` `model: opus` → `model: sonnet`).
3. Merge into `~/.claude/settings.json`: `env.PONYTAIL_SUBAGENT_MATCHER = "engineer"`,
   `enabledPlugins["ponytail@ponytail"] = true`, and the `ponytail` entry in
   `extraKnownMarketplaces` (skip the plugin keys if the step-1 offer was declined).
4. DISPATCH the standard per-workspace bundle re-sync (agents/rules/skills including the
   new `build-loop`, plus both pulse scripts) — one haiku brief per workspace, parallel,
   each result reviewed. Loops are opt-in per project; no workspace is required to arm one.
5. Write `3.3.0` to `.claude/VERSION`; note the offers' outcomes in HANDOFF.

## 3.2.0 — 2026-08-14

Routing v2 and the session-economics doctrine — ported from the live orchestrator's latest
revision.

- **Routing table v2** (replaces the six-point quality gate), per beat in order:
  (1) transcription → haiku, regardless of file count; (2) hard opus triggers —
  security-critical surface as a TASK property in ANY system (authn/authz/session handling,
  crypto, secrets paths, PII/data integrity, money movement, destructive migrations,
  concurrency) · un-decomposable cross-module refactor · novel design with no in-repo
  precedent · codebase ambiguity → opus engineer + opus review; (3) caught-by-a-check gate —
  sonnet iff ALL FOUR: callers exercised by GATE_FULL · no trigger-2 surface · failing tests
  exist BEFORE the beat · precedent cited by path (advisor consults ≤2/beat; a wanted 3rd =
  promotion trigger); (4) neither → re-shape, don't route up: test-first prep-beat by a FRESH
  sonnet test-writer with no implementation context (top tier contributes only assertion
  lists for hard-trigger/cross-module invariants); escalating requirement-ambiguity to opus
  is a protocol violation.
- **Debugging is two-phase, always**: a read-only diagnosis beat (written cause +
  reproducing failing test) routes the fix beat through the table — never on a guess.
- **Session lifecycle + effort doctrine**: the leader session is a phase, not a residence —
  design sessions may grow at the highest effort; execution runs fresh, reading plan +
  ROSTER + pack; /clear is always safe (state lives on disk); leader carriage target <~250k
  average context/message. Employees carry `effort:` in their defs for ONE life
  (engineer/reviewer/researcher: high); an effort flip invalidates their prompt cache.
- **Escalation ladder v2**: advisor consults → fix rounds 1–3 (same engineer) → round 4
  promote the SAME employee → cap 5 adjudicate; failure diagnostic — wrong from not-knowing
  → bigger model, wrong from not-trying → the correction names the miss, same engineer;
  kill-switch — sonnet first-review rejection >1-in-3 over a week tightens the gate, never
  loosens the checks.
- **Conservation mode** at cap pressure: implementation 100% sonnet/haiku; remaining opus
  reserved for reviews + hard-trigger beats; a beat whose review cannot run on opus is
  PARKED, never down-reviewed.
- **Agents**: reviewer defaults to `opus` (sonnet only for reviewing haiku transcription) and
  judges test adequacy as criterion #1 on test-first beats; engineer BLOCKED now names its
  kind (REQUIREMENT vs CODEBASE ambiguity) and records advisor-consult counts;
  researcher/researching skill — the full claims table ALWAYS lives in a file, final message
  ≤40 lines. Acceptance criteria are authored by the leader/plan and copied VERBATIM into
  briefs. Model aliases only, never pinned versions; the session-close audit flags any agent
  that inherited the leader's model. Team skill additions: wave-scoped lead note, test-first
  prep-beat, ~50k employee-context handover trigger, ledger event vocabulary
  (consults/PARKED), leader carriage hygiene.

**Upgrade steps** (from 3.1.0), on each installed machine:
1. Framework tree (root session applies): copy from 3.2.0 — `agents/engineer.md`,
   `agents/reviewer.md`, `agents/researcher.md`, `agents/project-orchestrator.md`,
   `skills/team/SKILL.md`, `skills/researching/SKILL.md`, `templates/brief.md`. Re-apply the
   machine's tier swaps (Sonnet tier: `agents/reviewer.md` `model: opus` → `sonnet`; routing
   opus references collapse per the setup skill's tier mapping).
2. Projects-root CLAUDE.md: replace the routing block with 3.2.0's "Routing (per beat, in
   order)" + "Debugging is two-phase" + the updated "A higher model validates" paragraph; add
   the "Session lifecycle" and "Effort" paragraphs after the Do-inline block and the
   "Conservation mode" paragraph after No-silent-waits; extend the model-alias sentence.
   Keep filled machine values.
3. Per existing workspace (dispatched, one beat each): re-sync `.claude/agents/`,
   `skills/team/`, `skills/researching/`, and `templates`-derived brief format from the
   tier-swapped projects root; one-line CHANGELOG entry.
4. Write `3.2.0` to `.claude/VERSION`, commit; push the distribution repo if maintained here.

## 3.1.0 — 2026-08-13

Deterministic session pulse — checks become code, not model discipline; near-zero cost.

- **New `.claude/scripts/session-pulse.sh` + `.ps1`**, wired via hooks to SessionStart
  (matcher now includes `resume` — resumed sessions were previously unchecked) AND
  UserPromptSubmit (every prompt). The script is silent when healthy (no output = zero
  context tokens), local-only except one throttled `git fetch` per 6 hours, and injects
  `PULSE:` notices for: a newer published framework VERSION (root); root HANDOFF lagging the
  missions LEDGER; workspace HANDOFF/CHANGELOG lagging commits by >1h; any doc over 100 KB.
  Freshness/size notices are additionally throttled to once per 4-hour window
  (`.claude/last-pulse-nudge`, gitignored) so a known-stale doc never nags per prompt.
- **The update check no longer depends on the model remembering an instruction** — the hook
  runs it; CLAUDE.md's Framework-updates block now acts on the injected notice (apply before
  new mission work, never mid-task, deferrable). `/update` still forces a check. There is
  deliberately NO OS cron: when Claude is closed nothing can apply updates anyway, and the
  first session after any restart is checked by the hook.
- Workspace hooks ship in the workspace-settings template + `new-project` bundle; `/onboard`
  writes OS-correct hook commands into `.claude/settings.local.json` when a teammate's OS
  differs from the leader's. New fill-map token `__PULSE_COMMAND__` (per-OS).

**Upgrade steps** (from 3.0.2), on each installed machine:
1. Copy `.claude/scripts/session-pulse.ps1` + `.sh` from 3.1.0 into
   `<projects root>/.claude/scripts/`, filling `__DISTRIBUTION_REPO__` with this machine's
   clone path.
2. Replace the hooks in `<projects root>/.claude/settings.json` with the 3.1.0 shape
   (matcher `startup|resume|clear`; pulse command per this machine's OS; keep the filled
   vault path in the echo). Approve the hooks prompt at the next session start.
3. In the projects-root CLAUDE.md: replace the Framework-updates block with the 3.1.0
   version and add the "Pulse notices in general" paragraph (keep filled values).
4. Add `/.claude/last-pulse-nudge` to the projects-root `.gitignore`.
5. Per existing workspace (dispatched, one beat each): copy the two scripts into
   `WS/.claude/scripts/`; replace the `WS/.claude/settings.json` hooks with the 3.1.0
   workspace shape (this machine's OS command; teammates on another OS get theirs via
   `/onboard` → `.claude/settings.local.json`); append `.claude/last-pulse-nudge` to the
   workspace `.gitignore`; one-line CHANGELOG entry.
6. Write `3.1.0` to `.claude/VERSION`, commit; push the distribution repo if maintained here.

## 3.0.2 — 2026-08-13

- **Workspace migrations copy from the tier-swapped projects root, never the raw clone** —
  and the agents-bundle swap now names project-orchestrator.md and the rules re-sync
  explicitly. Prevents a non-Fable install's workspace orchestrators from being reset to
  `model: fable` during the 3.0.0 migration. (3.0.0 upgrade step 4 reworded.)

**Upgrade steps** (from 3.0.1): none — wording only. Machines that already applied 3.0.0's
workspace migration from the raw clone: verify each workspace's
`.claude/agents/project-orchestrator.md` frontmatter matches the install's tier; fix by
re-copying from the projects root.

## 3.0.1 — 2026-08-13

- **Update protocol: new tool dependencies are offered, never silent.** When a version's
  upgrade steps introduce a tool/plugin/CLI dependency, the updating session asks the user
  before installing (system-level installs always ask); declined or failed installs are
  recorded in HANDOFF and the framework degrades gracefully. The 3.0.0 graphify step is now
  worded as an explicit offer.

**Upgrade steps** (from 3.0.0): none — protocol wording only; the updated changelog copies
itself to `.claude/FRAMEWORK-CHANGELOG.md` as part of any update pass.

## 3.0.0 — 2026-08-13

Persistent-team orchestration and the token diet — the execution model changes (MAJOR).

- **Persistent employees replace spawn-per-task**: new `team` skill (+ HANDOVER/ROSTER
  templates) — engineer/verifier/reviewer are hired ONCE per project, onboard from
  CONTEXT_PACK + HANDOVER, and serve many beats via short messages; handover→rehire swaps the
  model without losing project knowledge; roster + ledger-before-dispatch make usage-limit
  kills recoverable. New agents: `engineer` (sonnet default, opus per gate, haiku for
  transcription) and `verifier` (haiku; owns `tmp/gates/`, serializes DB/Playwright runs).
  `implementer` is RETIRED. `reviewer`/`scout`/`researcher` rewritten (beat-oriented,
  gate-log evidence, claims-table contract).
- **Routing gate**: transcription-shaped beats → haiku regardless of size; a six-point
  quality-equivalence gate decides sonnet vs the top tier (ANY NO → stronger); a higher model
  always reviews the tier below; `exceeds-ability` is a rewarded status; every dispatch
  carries an explicit `model:` alias.
- **Evidence diet**: beats carry GATE_SCOPED (engineer inner loop) and GATE_FULL (verifier,
  once); ALL gate output piped to `tmp/gates/*.log`; context sees exit code + ≤40-line
  excerpt + ≤20-line tail; reviewers re-run gates only for money/security/migrations/
  concurrency or doubt. Engineering rule gains: log-file output discipline,
  process-supervision-is-code, the one-authoritative-number rule, and the defensive
  security-register section.
- **CONTEXT_PACK.md** becomes the seventh workspace doc (employees' 1-page onboarding pack;
  template shipped) with a query-first read protocol: `graphify query "<q>" --budget 1500`
  (optional CLI, `pip install graphifyy` — tree-sitter code pass, free; LLM semantic
  extraction approval-gated) → pack → targeted Grep → whole-file Read. Size hygiene: docs
  >100 KB archived by a haiku beat; graph refreshed via `graphify hook install`.
- **No silent waits**: >15-minute dispatches get bounded watchdogs; >30-minute stalls are
  stopped, inspected, resumed or re-scoped; interruptions surface immediately.
- **`finish` skill**: pre-merge go/no-go closeout (stale-number scan, live GATE_FULL re-run,
  register scan, open-item sweep, attribution + hygiene); missions end with its GO verdict.
- **Setup**: interview gains Q9 vault privacy (fills `__VAULT_CAPTURE__` — proactive vs
  ask-first) and Q10 optional graphify install; tier mapping updated to the new roster.

**Upgrade steps** (from 2.5.0), on each installed machine — per-workspace steps are
DISPATCHED per the Update protocol:
1. Framework tree (root session applies): copy from 3.0.0 — `agents/` (engineer, verifier,
   reviewer, scout, researcher, project-orchestrator; DELETE `implementer.md`),
   `skills/team/`, `skills/finish/`, `skills/new-project`, `skills/adopt-project`,
   `skills/onboard`, `rules/engineering.md`, `rules/project-docs.md`, `templates/brief.md`,
   `templates/docs/CONTEXT_PACK.md`, `templates/workspace-CLAUDE.md`,
   `templates/workspace.gitignore`, `templates/mission.md`. Re-apply the machine's model-tier
   swaps (project-orchestrator frontmatter, role-detection model name).
2. Projects-root CLAUDE.md: apply the 3.0.0 routing block (routing gate, review ladder,
   evidence diet, no-silent-waits, team-mode sentences, updated fast-path/don't-over-delegate
   wording, session-start pack reference) — copy the sections from 3.0.0's file, keeping
   filled machine values.
3. `rules/obsidian-vault.md`: the personal-capture bullet is now chosen at install; existing
   installs KEEP their current behavior (replace `__VAULT_CAPTURE__` with the proactive text
   from the setup skill unless the user asks for ask-first).
4. Per existing workspace (dispatched, one beat each): swap the `.claude/agents/` bundle —
   delete implementer.md, add engineer/verifier, replace the rest INCLUDING
   project-orchestrator.md — copying from the projects-root `.claude/` (already tier-swapped
   in step 1), never from the distribution clone directly; re-sync `.claude/rules/`; copy
   `skills/team/` + `skills/finish/` + the new `templates`-derived files; create
   `.claude/docs/CONTEXT_PACK.md` from the template, filled from the workspace's existing
   docs; create `tmp/gates/` + `tmp/team/`; append `graphify-out/` to the workspace
   `.gitignore`; one-line CHANGELOG entry.
5. Optional — OFFER to the user first: `pip install graphifyy`; if accepted, per workspace
   `graphify <code dirs>` (code pass only, vendor excluded) + `graphify hook install`;
   record the pack's graph-build line. Declined → everything still works (pack → Grep).
6. Write `3.0.0` to `.claude/VERSION`, commit; push the distribution repo if maintained here.

## 2.5.0 — 2026-08-04

- **Root commands** in `<projects root>/.claude/commands/`:
  - `orient` — re-ground a session on demand: role, HANDOFF, mission ledger,
    update status, drift check, recommended next action (session start already self-onboards
    via the hook; this repeats it anytime).
  - `status` — cross-project progress report: per project, state / in-flight / blockers /
    an estimate stated WITH its basis (backlog volume vs recent CHANGELOG cadence — "no
    basis to estimate" when there is none; never an invented date). More than ~3 active
    projects → one scout per project, root synthesizes.
  - `handoff` — rewrite the root HANDOFF fully current, sweep for uncaptured state, commit,
    and give a "safe to close" verdict or the exact list of what would be lost.
  - `update` — force the framework update check now, ignoring the 6-hour marker.
- SessionStart hook now mentions `/orient` and `/status` for discoverability.

**Upgrade steps** (from 2.4.0), on each installed machine:
1. Copy `.claude/commands/` (orient, status, handoff, update — 4 files) from 2.5.0 into
   `<projects root>/.claude/commands/`.
2. Replace the SessionStart hook echo in `<projects root>/.claude/settings.json` with the
   2.5.0 version (keeps the machine's filled vault path).
3. Write `2.5.0` to `.claude/VERSION`, commit; push the distribution repo if maintained here.

## 2.4.0 — 2026-08-04

- **Update migrations are dispatched, not inlined**: when a framework update's upgrade steps
  touch existing workspaces (bundle re-syncs, key renames, new commands/skills), the root
  session fans them out as per-workspace worker briefs — haiku for spelled-out surgery, opus
  for judgment-bearing steps, 3–5 in parallel across disjoint workspace trees — reviews each
  result before declaring the version applied, and writes a one-line CHANGELOG entry in each
  migrated workspace. Framework-tree steps remain root's own governance work. (Root
  CLAUDE.md's Framework-updates block and this file's Update protocol amended.)

**Upgrade steps** (from 2.3.0), on each installed machine:
1. Replace the "Framework updates" block in the projects-root CLAUDE.md with the 2.4.0
   version, keeping the machine's filled distribution-repo path.
2. Copy this FRAMEWORK-CHANGELOG.md over `<projects root>/.claude/FRAMEWORK-CHANGELOG.md`.
3. Write `2.4.0` to `.claude/VERSION`, commit; push the distribution repo if maintained here.

## 2.3.0 — 2026-08-04

- **Researching methodology shipped**: new `skills/researching` — questions not answerable
  from disk route **T0–T4** by the cheapest tier that settles them: disk first → one
  authoritative source (Context7 / clean-markdown fetch / `gh`) → community leads
  (`last30days` where installed; leads are verified before they enter work) → a structured
  `researcher` brief with a self-refutation pass → deep report only with the user's explicit
  approval and stated cost. Output contract: claims tables (claim · verbatim quote · URL ·
  date · source quality · confidence · what-would-refute-it); unverified = LEAD, never fact.
  Research never runs on an orchestrator model; sensitive data never enters a web query.
  Wired into root routing, the `researcher` agent, project-orchestrator routing, and the
  `new-project` workspace bundle.

**Upgrade steps** (from 2.2.0), on each installed machine:
1. Copy `skills/researching/` from 2.3.0 into `<projects root>/.claude/skills/` and into
   each existing workspace's `.claude/skills/`.
2. Re-copy `agents/researcher.md`, `agents/project-orchestrator.md`, and
   `skills/new-project` from 2.3.0; bundle-sync workspaces.
3. Add the researching routing bullet to the projects-root CLAUDE.md (after the scout-recon
   bullet — copy from 2.3.0).
4. Write `2.3.0` to `.claude/VERSION`, commit; push the distribution repo if maintained here.

## 2.2.0 — 2026-08-04

Workspace model aligned with live production practice (verified against two real workspaces),
plus automation capture.

- **Roles**: the `.env` key is `WORKSPACE_ROLE` = `team_leader` | `team_member` (was
  `CLAUDE_SESSION_ROLE` = leader/member). `.env` also carries the machine's git identity
  (`GIT_USER_NAME`, `GIT_USER_EMAIL`, `GITHUB_USERNAME`).
- **Repos**: created PRIVATE under a per-project GitHub owner (`github_org` in
  `workspace.yaml`, else the user's account). `workspace.yaml` gains `github_org`,
  `kind: code|vendor` (vendor = reference trees — cloned, read, never edited), and
  `submodules:`. Workspace docs: leader may direct-commit; members PR them too.
- **Session sync**: workspaces ship a `sync` command (`templates/commands/sync.md`) — fetch +
  `--ff-only` everything in the manifest (or the project's own `scripts/sync.sh`), run FIRST
  each session; `INFRASTRUCTURE.md` (workspace root) is the as-built handbook for ops-heavy
  projects, read before infra work.
- **Automation capture**: the second manual run of any flow (deploy-after-update, migration,
  seed, smoke test, release) is codified in the same mission as a workspace command / skill /
  hook and recorded in COMMANDS.md; workers flag candidates in DOC TRIGGERS; deploys are
  staging-first. `new-project` scaffolds `.claude/commands/` + `scripts/`; `adopt-project`
  preserves existing BOOTSTRAP.md/scripts/commands/vendor trees and runs the
  `claude-automation-recommender` agent (claude-code-setup plugin); workspace CLAUDE.md health
  via the claude-md-management plugin.
- **Global-rule benefits ported**: brief BINDING RULES now name the binding superpowers skills
  (`test-driven-development`, `systematic-debugging`); broad recon and plan-mode exploration
  route to `scout`, never root.

**Upgrade steps** (from 2.1.0), on each installed machine:
1. Copy from 2.2.0: `templates/example.env`, `templates/workspace.yaml`,
   `templates/commands/sync.md` (new), `templates/workspace-CLAUDE.md`,
   `templates/ONBOARDING.md`, `agents/project-orchestrator.md`, `rules/project-docs.md`,
   `skills/new-project`, `skills/onboard`, `skills/adopt-project` — then re-apply the
   machine's filled values (paths, model tier) where those files carry them.
2. In the projects-root CLAUDE.md: update role detection §2 to `WORKSPACE_ROLE`
   (`team_leader`/`team_member`); add the scout-recon routing bullet, the Automation-capture
   paragraph (after Caps), and the Git-section owner/direct-commit wording from 2.2.0.
3. Existing workspaces, per workspace: rename the `.env` key `CLAUDE_SESSION_ROLE` →
   `WORKSPACE_ROLE` (map leader→team_leader, member→team_member); add the git-identity keys;
   copy `.claude/commands/sync.md` from the template; bundle-sync agents/rules.
4. Write `2.2.0` to `.claude/VERSION`, commit; push the distribution repo if maintained here.

## 2.1.0 — 2026-08-04

- **Self-updating installs**: the root session now checks the distribution-repo clone for a
  newer published VERSION roughly every 6 hours — deterministically at session start (hook)
  and between tasks in long sessions, throttled via a gitignored
  `.claude/last-update-check` timestamp. A newer version is announced, pulled `--ff-only`,
  and applied per this file's Update protocol (each version's steps in order, never a blind
  overwrite; the security floor still gates destructive steps). Local-newer and offline cases
  are surfaced, never silent. `/setup` seeds the marker, verifies the clone's `origin`
  remote, and pins the clone path as `__DISTRIBUTION_REPO__`.

**Upgrade steps** (from 2.0.0), on each installed machine:
1. Copy the "Framework updates" block from 2.1.0's `all-projects/CLAUDE.md` into the
   projects-root CLAUDE.md (after the Session-rotation paragraph), replacing
   `__DISTRIBUTION_REPO__` with this machine's clone path.
2. Replace the SessionStart hook echo in `<projects root>/.claude/settings.json` with the
   2.1.0 version (adds the update-check step), keeping the machine's filled vault path.
3. Append `/.claude/last-update-check` to the projects-root `.gitignore`; write the current
   ISO timestamp to `.claude/last-update-check`.
4. Write `2.1.0` to `.claude/VERSION`, commit the projects root.

## 2.0.0 — 2026-08-04

Public distribution release: the framework is now a cloneable repo with no personal data.

- **Install is an interview**: `SETUP.md` replaced by `README.md` + the repo-local `setup`
  skill. A fresh clone installs itself via `/setup`, asking one question at a time: projects
  root, vault path, name, GitHub username, model tier, machine role, vault remote, optional
  About Me seeds. OS/shell/home are detected, not asked.
- **Placeholders**: every personal value (owner identity, GitHub account, absolute paths,
  machine environment) replaced by double-underscore placeholders filled at install; `{{…}}`
  tokens remain project-scaffold-time. The Environment section of the projects-root CLAUDE.md
  is now written per-OS at install.
- **Model-tier routing**: the install maps the user's plan (Fable / Opus / Sonnet-only) onto
  role detection, agent model frontmatter, and the settings model pin.
- **Security floor de-branded**: generic sensitive-data wording; domain context (banking,
  medical, …) is recorded in the vault's About Me instead.
- **Removed**: `.claude/reference/originals/` (source-methodology archive) and `SETUP.md`.
- **Repo governance**: distribution-repo CLAUDE.md with installer/maintainer modes, a PII
  gate, placeholder conventions, and this versioning protocol.

**Upgrade steps** (from 1.1.0): none on installed machines — installer-only release; installed
trees keep their filled values. Machines that redistribute the framework: replace any local
copy or `.zip` of the old package with a clone of this repo.

## 1.1.0 — 2026-08-03

- **Vault always on GitHub**: the Obsidian vault has a PRIVATE remote; every vault write is
  committed AND pushed in the same session (obsidian-vault rule updated).
- **Workspace `.env` = project credential store**: credentials the user shares for a project
  are saved to that workspace's gitignored `.env` in the same session for future sessions; key
  NAMES documented in `example.env` + ONBOARDING §3 (security floor + example.env template
  updated).

**Upgrade steps** (from 1.0.0):
1. In the vault: `git branch -m main` (if needed), create a private remote
   (`gh repo create <name> --private --source . --remote origin --push`) or
   `git remote add origin <url> && git push -u origin main`.
2. Replace `.claude/rules/obsidian-vault.md` "commit after writing" bullet with the
   commit-AND-push version (see 1.1.0 file), adjusting the remote URL to this machine's vault
   repo.
3. Add the credential-store bullet to the Security floor in `All Projects/CLAUDE.md` and the
   credential-store comment block to `templates/example.env` (copy from 1.1.0 files).
4. Bundle-sync workspaces, write `1.1.0` to `.claude/VERSION`, commit.

## 1.0.0 — 2026-08-03

Initial release. Everything below is established by SETUP.md's install phases (fresh installs
just follow SETUP.md; there are no prior versions to upgrade from).

- **Orchestration**: root session (Fable, All Projects root) as sole user interface; role
  detection (root / workspace orchestrator / worker); routing = inline · fast-path single-brief
  · full mission; two-phase mission execution (plan-mode session → root review + sign-off →
  resume same session with bypassPermissions); caps, mission/brief file protocol with IDs,
  ledgers, itemized review chain, revert-on-two-failures, NEEDS-DECISION escalation.
- **Agents**: project-orchestrator (fable), implementer (opus + Context7), scout (haiku,
  read-only), reviewer (sonnet + Playwright, opus override for risky diffs), researcher
  (sonnet + Context7). Workers never spawn.
- **Workspace model**: per-project workspace repo (Claude material + team memory, private on
  GitHub) wrapping Claude-free code repos; workspace.yaml manifest; example.env/.env with
  CLAUDE_SESSION_ROLE; leader/member PR protocol; gitignored tmp/ scratch tree.
- **Memory**: six docs + HANDOFF.md per workspace; root HANDOFF.md; Obsidian vault at
  ~/ObsidianVault (00–05 second-brain structure, main-sessions-write rule, proactive personal
  capture, VAULT TRIGGERS); everything git-versioned.
- **Discipline**: engineering + clean-architecture + hygiene rules; project-docs protocol;
  brainstorming-before-work; verification-before-done (gates verbatim; UI via Playwright with
  screenshots); session replaceability + rotation; SessionStart self-onboarding hooks.
- **Skills**: new-project, adopt-project, onboard. **Templates**: workspace CLAUDE.md,
  ONBOARDING.md, workspace.yaml, example.env, workspace .gitignore, workspace settings (hook),
  six docs, HANDOFF, mission, brief.
- **Settings** (user scope): Fable model pin, empty attribution, vault
  additionalDirectories/allow, gate allows, 13 plugins across 2 marketplaces.

**Upgrade steps**: none — initial release; install via SETUP.md.
