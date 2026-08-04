---
name: onboard
description: Set up this workspace from a fresh clone - read the project docs, clone the code repos from workspace.yaml, install prerequisites, create .env (asking your role - leader or member), run setup, launch the project, and verify health. Use when the user runs /onboard, asks to set up / bootstrap this project, or the environment is missing/broken.
---

# Onboard

Run from a workspace root (the directory containing `workspace.yaml`). Goal: from bare clone to
a verified running project, following the workspace's own ONBOARDING.md as the source of truth.

## Steps

1. **Understand the project.** Read `ONBOARDING.md`, `CLAUDE.md`, `.claude/docs/PROJECT.md`,
   and `workspace.yaml`. Summarize for the user in a few lines what this project is and what
   you're about to set up.
2. **Code repos.** For each entry in `workspace.yaml` missing from disk:
   `git clone <url> <path>` (branch per manifest). Never clone into a non-empty directory —
   report instead.
3. **Prerequisites.** Check each tool in ONBOARDING.md §1 (`command -v …`, version checks).
   Missing tools: install per ONBOARDING.md — ask before any system-level install (admin
   rights / system package manager).
4. **Env files.** `cp example.env .env` if absent; ask the user ONE question: leader or member
   on this machine? Write `CLAUDE_SESSION_ROLE`. For remaining keys and per-repo env files
   (ONBOARDING.md §3): create from the examples, ask the user for values of secret keys by NAME
   — never invent, never print values back.
5. **Setup + launch.** Run ONBOARDING.md §4 then §5 exactly as written (`cd <repo> && …` form).
   A written-down command is never "improved"; if one fails, fix the cause, then update
   ONBOARDING.md §7 (Common issues) in the same session.
6. **Verify.** Run every health check in ONBOARDING.md §6 and show the output.
7. **Report**: what's running, on which ports/URLs, how to stop it, your configured role, and
   anything skipped or still needed.
