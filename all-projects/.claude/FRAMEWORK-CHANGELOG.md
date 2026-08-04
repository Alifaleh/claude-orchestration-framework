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
   `.claude/HANDOFF.md` and per-machine settings must survive).
4. After the last step: write the new version to `.claude/VERSION`, re-sync every existing
   workspace's `.claude` bundle (agents/rules/onboard skill), commit the All Projects repo,
   and — if this machine maintains the distribution repo — commit and push the change there.

## Release protocol (when changing the framework locally)

Any framework change (CLAUDE.md, rules, agents, skills, templates, hooks) = bump
`.claude/VERSION`, add an entry here (changes + upgrade steps), sync workspace bundles, commit,
and push the distribution repo. No unversioned framework edits.

---

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
