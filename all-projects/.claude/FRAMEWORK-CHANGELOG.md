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
