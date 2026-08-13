# ROOT HANDOFF

Snapshot for the next root session. Rewritten in place; the append-only event log is
`tmp/missions/LEDGER.md`. Bring yourself current here, then work.

## In flight

- Nothing running. Fresh install of the orchestration framework.

## Projects

- None yet. Create with `/new-project`; adopt existing ones with `/adopt-project`.

## Open decisions (waiting on the user)

- None.

## Agreements & context

- The user talks ONLY to root; root never implements (fast path for single-beat tasks; full
  missions run the persistent employee team via the `team` skill). Requirements are
  brainstormed with the user BEFORE dispatch (`superpowers:brainstorming`); UI verification
  always via Playwright + screenshots, driven by the verifier.
- Full missions run TWO-PHASE by default: plan-mode session in the workspace → root reviews the
  plan (user sign-off for security-floor ops) → resume the same session_id with
  bypassPermissions to execute.
- Vault at `__VAULT_PATH__` (git repo) — personal/work capture policy per the obsidian-vault
  rule (chosen at install).
- Session self-onboarding is hook-enforced (SessionStart hooks); handoff files are the
  replaceability mechanism — keep them current.

*Last updated: (set on install)*
