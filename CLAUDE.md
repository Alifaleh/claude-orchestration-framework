# Claude Orchestration Framework — Distribution Repo

This repo is the framework's installer and source of truth. Nobody runs projects in here: the
framework you USE lives wherever `/setup` installs it (the projects root and vault the user
chooses). This clone stays pristine so `git pull` always works.

## Which mode applies (settle this before anything else)

1. **Framework not installed on this machine** — fresh clone, or the user asks to install /
   set up → **INSTALLER**: invoke the `setup` skill and follow it exactly. Ask its interview
   questions ONE at a time. Never edit this repo's files during an install; never start
   project work here.
2. **User asks to update an existing install** → follow the Update protocol at the top of
   `FRAMEWORK-CHANGELOG.md`. Never blind-overwrite an installed tree.
3. **User is changing the framework itself** → **MAINTAINER**: the rules below bind.

## Maintainer rules

**This repo is public. Everything committed here is published.**

### No personal data, ever

No real names, emails, GitHub accounts, employer names, machine usernames, absolute home paths
(`/home/<user>`, `/Users/<user>`, `C:\Users\<user>`), or machine-specific environment claims
(OS, locale, shell quirks). Machine- and person-specific content is written only by `/setup`
at install time, into the installed copies — never into this repo.

### Placeholder conventions — two kinds, never mixed

- `__DOUBLE_UNDERSCORE__` — filled once by `/setup` at install time (paths, identity, model,
  dates). The complete token list is the fill map in `.claude/skills/setup/SKILL.md`; a token
  used anywhere in the shipped trees MUST appear in that map, and every map entry must exist
  in the trees.
- `{{MUSTACHE}}` — survives install; filled later by `new-project` / `adopt-project` when a
  project is scaffolded (`{{PROJECT_NAME}}`, `{{DATE}}`, `{{ID}}`, …).

### PII gate — run before EVERY commit; all three must return nothing

```bash
grep -rniE '/home/[a-z]|/Users/[a-z]|C:\\Users' --include='*.md' --include='*.json' --include='*.yaml' .
grep -rniE '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}' --include='*.md' --include='*.json' --include='*.yaml' .
grep -rn 'github.com/' . | grep -vE '__GITHUB_USER__|anthropics/|kepano/'
```

Plus a judgment pass: any name, account, project name, or path you know belongs to a real
person or employer is a failure even if the patterns miss it.

### Versioning is law

Any change to the shipped trees bumps `VERSION` and adds a `FRAMEWORK-CHANGELOG.md` entry with
ordered Upgrade steps, in the same session — no unversioned framework edits. The root copies
and the `all-projects/.claude/` copies of VERSION and FRAMEWORK-CHANGELOG stay byte-identical
in this repo (installed copies diverge by design once filled).

### Repo boundary

- Shipped product: `all-projects/`, `obsidian-vault/`, `settings/settings-fragment.json`.
- Repo tooling: `README.md`, this file, `.claude/skills/setup/`.
- Nothing machine- or person-specific in the product; nothing product-behavioral in the
  tooling. The setup skill fills the product — it never becomes part of it.

### Working standards

- Surgical edits only; no unrequested files or refactors.
- After changing the setup skill, templates, or placeholders: re-verify the fill map ↔ tree
  token correspondence both directions, and re-read the interview end-to-end for coherence.
- Atomic commits, imperative subject line, sole-author — NEVER add `Co-Authored-By`,
  "Generated with Claude Code", or any Claude/Anthropic attribution to commits, PRs, or files.
