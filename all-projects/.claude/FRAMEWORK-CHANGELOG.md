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
   result reviewed before the version is declared applied.
4. After the last step: write the new version to `.claude/VERSION`, re-sync every existing
   workspace's `.claude` bundle (agents/rules/onboard skill), commit the All Projects repo,
   and — if this machine maintains the distribution repo — commit and push the change there.

## Release protocol (when changing the framework locally)

Any framework change (CLAUDE.md, rules, agents, skills, templates, hooks) = bump
`.claude/VERSION`, add an entry here (changes + upgrade steps), sync workspace bundles, commit,
and push the distribution repo. No unversioned framework edits.

---

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
4. Per existing workspace (dispatched, one beat each): swap the `.claude/agents/` bundle
   (delete implementer.md, add engineer/verifier, replace the rest); copy
   `skills/team/` + `skills/finish/` + the new `templates`-derived files; create
   `.claude/docs/CONTEXT_PACK.md` from the template, filled from the workspace's existing
   docs; create `tmp/gates/` + `tmp/team/`; append `graphify-out/` to the workspace
   `.gitignore`; one-line CHANGELOG entry.
5. Optional: `pip install graphifyy`; per workspace `graphify <code dirs>` (code pass only,
   vendor excluded) + `graphify hook install`; record the pack's graph-build line.
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
