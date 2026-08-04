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
