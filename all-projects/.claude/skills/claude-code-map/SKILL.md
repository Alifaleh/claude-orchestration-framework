---
name: claude-code-map
description: Map a recurring need or observed friction to the right Claude Code feature (command, skill, hook, agent, MCP, loop) and create it per policy.
---

# Claude Code Map

Turn observed repetition and friction into native Claude Code machinery instead of re-thinking flows every session.

## When to invoke

- **Audit moments:** project adoption (adopt-project step 6); finish-skill closeout; the session pulse reports the automation audit missing or stale; a beat report or one-off dispatch report carries an `AUTOMATION:` flag.
- **Friction moments mid-mission:** the same manual flow ran twice; repeated permission prompts; repeated lookups of the same external fact.

## Decision table

| Observed need | Feature | How |
|---|---|---|
| Same typed flow ran 2× (deploy, migrate, seed, smoke, release) | Command | `.claude/commands/<verb>.md`, wrapping a `scripts/` script where one fits |
| Recurring flow that needs judgment, not just typing | Workspace skill | `.claude/skills/<name>/` — via the skill-creator plugin if enabled, else by hand from the official skills docs |
| Missing domain expertise | Skill install | The skill-finder skill (vetted, transcribed, workspace-local) |
| A step that must fire deterministically, every time | Hook | Workspace `.claude/settings.json` hook; hooks running NEW code need user sign-off |
| Recurring role or perspective (domain reviewer, critic) | Agent | Workspace agent `.md` with an explicit `model:` alias — never omit it |
| External system integration | MCP server | User sign-off first; note its schema rides every session's context |
| Time- or event-driven recurrence | Loop | build-loop skill: PROPOSAL into BACKLOG.md with pattern + cost estimate; never armed without user sign-off |
| Permission-prompt friction | Permission tuning | Review `/permissions` (recent auto-mode denials); suggest the user run `/fewer-permission-prompts` |
| Environment visibility (branch, model, cost in prompt) | Statusline | Suggest the user run `/statusline` |
| Settings/config change | Settings edit | The update-config skill (claude-code-setup plugin) if enabled, else direct edit with a JSON parse check |

## Creation policy (framework default — the owner can tighten it in the workspace CLAUDE.md)

- **Create, then report:** workspace-scoped commands, skills, and agents — create immediately, list them in the report and the workspace CHANGELOG.
- **Sign-off first, every time:** hooks that run new code, anything global under `~/.claude/`, MCP servers, armed loops.

## Audit procedure

1. If the claude-code-setup plugin is enabled, dispatch the claude-automation-recommender agent (read-only; it does web checks — run it at audits only, never per-session).
2. Frequency scan: `git log --oneline --since="30 days ago"` plus COMMANDS.md vs. flows actually run by hand this month; anything seen ≥2× and uncaptured → decision table.
3. Friction review: permission prompts hit, repeated manual sequences, missing docs or gates.
4. Create or propose per the policy above; write the marker — file `.claude/automation-audit` containing today's date as `YYYY-MM-DD` (content, not mtime); add one CHANGELOG line listing what was created/proposed.

## Currency

No local feature inventory is kept — it would be stale by construction. For "does Claude Code have X now?": dispatch the claude-code-guide agent if available, else fetch the official docs on demand (code.claude.com/docs — the `llms.txt` index lists every page).

## Accepted gap

Missions that never run the finish skill are covered only by the session pulse and the 30-day marker. This is deliberate: repetition is semantic, hooks must never call an LLM, so no hook can detect it deterministically.
