---
name: setup
description: First-time interactive installation of the Claude Orchestration Framework from this cloned repo. Use when the user runs /setup, asks to install or set up the framework, or opens Claude in a fresh clone not yet installed on this machine. Interviews the user one question at a time, installs the trees outside the clone, fills all placeholders, merges settings, and verifies the install.
---

# Framework Setup

You are installing the Claude Orchestration Framework from this repo onto this machine. The
result: a projects root the user talks to through ONE root session, an Obsidian second-brain
vault, and orchestrator/worker agents — all filled with this user's answers.

Rules for the whole flow:

- ONE question at a time; wait for each answer before asking the next.
- Use your file tools (Read / Write / Edit / Glob) for copying and token-filling — never
  OS-specific one-liners like `sed`. This must work on Windows, macOS, and Linux.
- NEVER edit this repo's own files. All filling happens in the COPIES at the install targets;
  the clone stays pristine so `git pull` keeps working.
- Summarize each phase in a line or two as you complete it. If a step fails, stop and report
  it plainly — never fake a pass, never skip verification.
- **Already installed?** If a projects root with a `.claude/VERSION` file already exists on
  this machine (ask if unsure), STOP — this is an update, not an install: follow the Update
  protocol at the top of `FRAMEWORK-CHANGELOG.md`.

## Phase 0 — Preflight

1. `claude --version` → need **v2.1.219 or newer** (subagent nesting). Older → tell the user
   to update Claude Code first; stop.
2. `git --version` → required. Missing → help the user install it for their OS.
3. `gh --version` and `gh auth status` → wanted for private remotes. Missing → offer to
   install (Windows: `winget install GitHub.cli`; macOS: `brew install gh`; Linux: distro
   package), then `gh auth login --web`. The user may skip `gh` entirely — then every
   remote-creation step below is skipped and noted in the final report.
4. Detect the OS, shell, and absolute home directory yourself. Used for interview defaults,
   the Environment fill, and `__OS_SUMMARY__`.

## Phase 1 — Plugins

Register the marketplaces, then install each plugin. On failure: note it and continue — only
`superpowers` (brainstorming), `playwright` (UI verification), and `context7` (library docs)
are load-bearing for the framework's rules; flag those three loudly if missing.

```bash
claude plugin marketplace add anthropics/claude-plugins-official
claude plugin marketplace add kepano/obsidian-skills

claude plugin install mcp-server-dev@claude-plugins-official
claude plugin install playwright@claude-plugins-official
claude plugin install superpowers@claude-plugins-official
claude plugin install claude-md-management@claude-plugins-official
claude plugin install context7@claude-plugins-official
claude plugin install frontend-design@claude-plugins-official
claude plugin install skill-creator@claude-plugins-official
claude plugin install github@claude-plugins-official
claude plugin install security-guidance@claude-plugins-official
claude plugin install claude-code-setup@claude-plugins-official
claude plugin install postman@claude-plugins-official
claude plugin install data-engineering@claude-plugins-official
claude plugin install obsidian@obsidian-skills
```

## Phase 2 — Interview

Ask exactly these, one at a time, in this order. Offer the default; an empty or "default"
answer takes it.

1. **Projects root** — "Where should your All Projects directory live?"
   Default: `~/Desktop/All Projects` (Windows: `%USERPROFILE%\Desktop\All Projects`).
2. **Vault path** — "Where should your Obsidian vault (your second brain) live?"
   Default: `~/ObsidianVault`.
3. **Name** — "What should I call you? (goes into the vault's About Me note)"
4. **GitHub username** — read it from `gh auth status` and confirm: "GitHub remotes will be
   created under `<detected>` — correct?" (No `gh` → still ask for the username, used in URL
   templates; mark remote creation skipped.)
5. **Model tier** — "Which Claude models can this machine run — does your plan include Fable?
   Opus? Or Sonnet only?" → sets the MODEL TIER (mapping in Phase 3).
6. **Machine role** — "For shared projects, is this machine's default role **leader** (reviews
   and merges PRs) or **member** (works via PRs only)?" Default: leader for a personal machine.
7. **Vault remote** — "Create a PRIVATE GitHub repo for the vault so it's always backed up?
   What name?" Default: yes, `obsidian-second-brain`. Skipped → the vault stays local-only.
8. **About Me seeds (optional)** — "Anything you want in About Me right away — role/title,
   employer, email, work context (e.g. regulated data like banking or medical)? Or skip — I
   capture these over time."

## Phase 3 — Install the trees

With PROJECTS = answer 1 and VAULT = answer 2 (both absolute):

1. Create both directories. Copy `all-projects/` → PROJECTS and `obsidian-vault/` → VAULT,
   including dotfiles (`.claude/`, `.gitignore`).
2. **Fill every `__TOKEN__` in the copied trees** (Glob for `**/*` under both targets; check
   every text file). The fill map:

   | Token | Value |
   |---|---|
   | `__PROJECTS_ROOT__` | absolute projects root |
   | `__VAULT_PATH__` | absolute vault path |
   | `__GITHUB_USER__` | answer 4 |
   | `__VAULT_REMOTE__` | the vault repo URL under the user's GitHub account — if skipped, rewrite that bullet of `rules/obsidian-vault.md` to commit-only (no remote, no push) |
   | `__USER_NAME__` | answer 3 |
   | `__OS_SUMMARY__` | e.g. "Windows 11", "macOS 15", "Ubuntu 24.04" |
   | `__DATE__` | today, YYYY-MM-DD |
   | `__MACHINE_ROLE__` | answer 6 (`leader` or `member`) |
   | `__DISTRIBUTION_REPO__` | absolute path of THIS clone |
   | `__ENVIRONMENT_NOTES__` | the environment snippet (step 3) |
   | `__MODEL__` | settings fragment only — per the tier mapping (step 4) |

   When filling JSON files (e.g. `.claude/settings.json` hooks), JSON-escape the value —
   Windows backslashes must become `\\`.
   Afterwards VERIFY: a search for `__[A-Z_]+__` across PROJECTS and VAULT returns nothing.
   (`{{…}}` placeholders REMAIN — they are filled later at project-scaffold time.)
3. **Environment snippet** → becomes the `## Environment (this machine)` section of
   PROJECTS/CLAUDE.md. Write only what is TRUE for this machine, e.g.:
   - Windows: set `PYTHONIOENCODING=utf-8` before running Python that prints non-ASCII text
     (else cp1252 `UnicodeEncodeError`); suspect the 260-char path limit when file ops fail in
     deep trees; always quote paths containing spaces; PowerShell and Git Bash need different
     syntax — match the tool.
   - macOS / Linux: always quote paths containing spaces; if the system locale is non-English,
     note that `ls` / `git` dates render localized; anything else you detected in Phase 0.
   Then TEST the claim "inside subagents `cd` does not persist between Bash calls" on this
   harness (two Bash calls in one subagent, or two of your own calls if you cannot spawn):
   keep, drop, or invert that line accordingly in PROJECTS/CLAUDE.md and in
   PROJECTS/.claude/agents/*.md where it repeats.
4. **Model tier mapping** — edit the COPIES under PROJECTS:
   - **Fable tier**: defaults are already right (root + project-orchestrator `fable`,
     implementer `opus`, reviewer/researcher `sonnet`, scout `haiku`).
     `__MODEL__` → `"claude-fable-5[1m]"`.
   - **Opus tier** (no Fable): in PROJECTS/CLAUDE.md role detection §1, `Fable` → `Opus`;
     `agents/project-orchestrator.md` `model: fable` → `model: opus`; drop fable from the
     cost line. `__MODEL__` → `"opus"`.
   - **Sonnet tier**: root, project-orchestrator, implementer, and reviewer all become
     `sonnet`; scout stays `haiku`; rewrite the cost line to the models in play; DELETE the
     `"model"` key from the merged settings instead of filling `__MODEL__`; add one line to
     PROJECTS/CLAUDE.md routing: "Single-model install: review independence is reduced —
     risky diffs deserve the user's own eyes."
5. **About Me** — fill `VAULT/00 - Brain/About Me.md` from answers 3, 4, and 8 (plus OS and
   paths). Anything not given stays as its _(fill in)_ marker.
6. **Settings merge** — read `~/.claude/settings.json` (create `{}` if absent) and MERGE the
   keys from `settings/settings-fragment.json` after filling its tokens: never overwrite the
   file, append/union into existing arrays and objects. Validate the JSON afterwards
   (`python -m json.tool` or equivalent).
   **Conflict check**: if `~/.claude/CLAUDE.md` or `~/.claude/rules/` already carries an
   orchestration/routing protocol, show the user the overlap and ask whether to keep, move,
   or retire it — two orchestration protocols must not load at once.
7. **Git-init both trees**:
   - PROJECTS: `git init` + initial commit ("Bootstrap orchestration framework").
   - VAULT: `git init -b main` + initial commit ("Bootstrap vault"). If a vault remote was
     requested: `gh repo create <name> --private --source . --remote origin --push` from
     VAULT (name taken → ask for another, update `rules/obsidian-vault.md`'s remote URL in
     PROJECTS to match).
   Commits: imperative subject, sole-author, NO Claude/Anthropic attribution of any kind.
8. Set today's date in PROJECTS/.claude/HANDOFF.md's `*Last updated:*` footer.
9. **Seed the auto-updater**: write the current timestamp (ISO, e.g. `2026-08-04T12:00:00`) to
   `PROJECTS/.claude/last-update-check`. Verify `git -C <this clone> remote get-url origin`
   succeeds — that remote is what the 6-hourly update check fetches; if there is no remote,
   warn the user that auto-update stays off until the clone gets one. The clone must STAY at
   its current path (it is recorded as `__DISTRIBUTION_REPO__` in PROJECTS/CLAUDE.md).

## Phase 4 — Verify (before declaring done)

1. Tell the user to open a NEW Claude Code session at PROJECTS (accept the workspace-trust and
   SessionStart-hook prompts). That session must self-onboard: read `.claude/HANDOFF.md`
   before its first task, unprompted.
2. In that session (it can run these itself):
   - Dispatch `reviewer` with the probe "state the model your system prompt names, verbatim;
     use no tools" → the tier's reviewer model; with `model: opus` override → Opus (tiers
     that include it).
   - Ask a `general-purpose` subagent "which role does the projects-root CLAUDE.md assign
     you?" → answers WORKER and refuses to spawn agents.
3. `gh auth status` → the intended account; the vault remote exists and is private (if
   created).

## Phase 5 — Hand off

Report, facts only:

- Where everything landed (PROJECTS, VAULT, settings keys merged, plugins installed/failed).
- "From now on, open Claude at `<PROJECTS>` and talk to that ROOT session. First project:
  `/new-project <name> <components…>` — or `/adopt-project` for an existing codebase."
- Prerequisites still missing for real work (per project type: `uv` for Python, node via nvm
  for JS/TS, docker) — install on demand, asking before system-level installs.
- Have the user open the vault once in the Obsidian app (File → Open vault → VAULT) so
  `.obsidian/` gets generated.
- Updates are automatic: the root session checks this clone every ~6 hours (session start and
  between tasks) and applies newer versions per `FRAMEWORK-CHANGELOG.md`'s Update protocol —
  keep the clone in place. Saying "update the framework" to the root session forces a check
  anytime.
