# Claude Orchestration Framework

A complete operating model for Claude Code: you talk to ONE root session; it brainstorms
requirements with you, routes work to the right model tier, reviews evidence, and keeps
durable memory. Projects run as workspaces with clean code repos, a team git flow, and an
Obsidian second-brain vault.

## What you get after install

- **One interface** — a root orchestrator session at your projects root. It never writes
  project code itself: it decomposes, dispatches workers, and reviews their evidence. Root
  commands: `/orient` (re-ground the session), `/status` (cross-project progress report with
  evidence-based estimates), `/handoff` (bring the handoff current — "safe to close?"),
  `/update` (force the framework update check).
- **Layered execution** — a project-orchestrator per workspace running a persistent employee
  team (engineer / verifier / reviewer, plus scout and researcher) on the cheapest model that
  does the job well: a six-point routing gate decides the tier, a higher model always reviews
  the tier below, and employees onboard ONCE from a per-project context pack instead of
  re-reading the project every task. Full missions run two-phase: a plan-mode session writes
  the plan, you sign off on anything destructive, then the same session executes it.
- **Token diet** — gate output goes to log files (context sees exit codes + short excerpts,
  never full logs); the full suite runs once per beat by a haiku verifier; and with the
  optional graphify CLI (`pip install graphifyy`) code questions are answered from a free
  tree-sitter knowledge graph within a token budget before any file crawling.
- **Workspaces** — every project is a private workspace repo (Claude material + team memory)
  wrapping Claude-free code repos, vendor/reference trees, and submodule superprojects, under
  a per-project GitHub org or your account. Team roles (`team_leader` / `team_member`) drive
  the PR flow; a new teammate clones the workspace and runs `/onboard`.
- **Automation capture** — flows you repeat (deploy-after-update, migrations, smoke tests)
  get codified as workspace commands, skills, and hooks, recorded in COMMANDS.md — never left
  as chat knowledge.
- **Research discipline** — questions not answerable from disk route T0–T4 by the cheapest
  tier that settles them (source-on-disk → one authoritative lookup → community leads →
  multi-source verification → deep report, the last only with your approval); results are
  claims-with-sources tables, never vibes.
- **Memory** — seven docs (including the CONTEXT_PACK onboarding pack) + a HANDOFF file per
  workspace, a root HANDOFF, and the vault. Every session is replaceable — and so is every
  employee: knowledge handovers survive model swaps.
- **Verification discipline** — nothing is "done" without gate output shown; UI work is proven
  through the real screen (Playwright) with screenshots as evidence.

## Requirements

- Claude Code **v2.1.219 or newer** (subagent nesting), on a plan that includes at least
  Sonnet. Best with Fable or Opus — `/setup` adapts the routing to what you have.
- `git`. The GitHub CLI (`gh`) if you want private remotes created for you (recommended).
- [Obsidian](https://obsidian.md) (free) for the vault — opened once after install.

## Install

```bash
git clone https://github.com/Alifaleh/claude-orchestration-framework
cd claude-orchestration-framework
claude
```

Then, inside Claude:

```
/setup
```

`/setup` interviews you (one question at a time), installs everything OUTSIDE this clone,
merges the needed keys into your `~/.claude/settings.json`, installs the plugins the framework
relies on, and verifies the result. From then on you open Claude at your projects root and
talk to that session.

## What /setup asks you

1. Where should your All Projects directory live? (default `~/Desktop/All Projects`)
2. Where should your Obsidian vault live? (default `~/ObsidianVault`)
3. What should I call you? (seeds the vault's About Me note)
4. Your GitHub username — confirmed from `gh auth status`; used for remote URLs.
5. Which Claude models can this machine run — Fable, Opus, or Sonnet only? (sets the
   model-routing tier)
6. Is this machine's default role for shared projects **team_leader** (reviews and merges
   PRs, triggers deploys) or **team_member** (works via PRs only)?
7. Create a private GitHub repo for the vault so it's always backed up? (default name
   `obsidian-second-brain`; skippable — the vault then stays local-only)
8. Optional About Me seeds — role/title, employer, email, work context (e.g. regulated data
   such as banking or medical) — or skip and let Claude capture them over time.
9. Vault privacy — should Claude proactively save durable personal/work facts you mention,
   or only write personal notes when you explicitly ask?
10. Install the optional graphify CLI (`pip install graphifyy`) for the code knowledge graph
    and query-first reading? (skippable — reading degrades gracefully)

Everything else (OS, shell, home directory) is detected, not asked.

## Package layout

| Path | Contents | Installed to |
|---|---|---|
| `all-projects/` | Projects-root CLAUDE.md + `.claude/` (agents, rules, skills, templates, HANDOFF, SessionStart hook) | your projects root |
| `obsidian-vault/` | Vault seed (Home, `00–05` folders, About Me, note templates, framework knowledge note) | your vault path |
| `settings/settings-fragment.json` | Keys MERGED into `~/.claude/settings.json` | merged, never overwritten |
| `.claude/skills/setup/` | The installer interview — used by this repo only, never copied | — |

## Updating an existing install

Updates are automatic and effectively free: a deterministic session hook (SessionStart +
every prompt, throttled to one network check per 6 hours, silent when current — zero tokens)
fetches your clone of this repo and compares the published `VERSION` with the installed one.
When a newer version exists the root session announces it, pulls (`--ff-only`), and applies
each intermediate version's upgrade steps in order per `FRAMEWORK-CHANGELOG.md` — never a
blind overwrite, so your filled-in values and machine state survive. Keep the clone where
`/setup` found it.

You can also force a check anytime by telling the root session "update the framework".
