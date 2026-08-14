---
name: build-loop
description: Design, scaffold, and arm a recurring agent loop (loop-engineering methodology on Claude Code's native /loop, scheduled tasks, or an OS scheduler). Use when the user asks for a recurring/scheduled automation ("build a loop", "every morning...", "keep PRs moving", "watch CI"), or when the orchestrator proposes automating a recurring flow. Leader-only; a loop is never armed without explicit user sign-off.
---

# Build a Loop

Wraps the loop-engineering methodology (github.com/cobusgreyling/loop-engineering, MIT — an
npx CLI, nothing installs globally) around Claude Code's native recurring-execution
features. Most users never touch those features; this skill is how the orchestrator wields
them on their behalf. Every proposal NAMES the native feature it will use and says in one
plain line what it does — the user learns the platform by watching it work.

**Prereq:** `node --version` ≥18 (the CLI runs via `npx @cobusgreyling/loop`). Missing →
offer the install; declined → record in HANDOFF and stop — no loop without the toolkit.

## 1. Pick the pattern (one primary loop per concern)

| Pain | Pattern |
|------|---------|
| Morning chaos / unclear priorities | `daily-triage` |
| PRs stalling on review/CI/rebase | `pr-babysitter` |
| CI red / flaky | `ci-sweeper` |
| CVE / dependency noise | `dependency-sweeper` |
| Post-merge TODOs piling up | `post-merge-cleanup` |
| Stale release notes | `changelog-drafter` |
| Noisy issue tracker | `issue-triage` |

Unsure → `daily-triage` at L1: it teaches state discipline with zero auto-fix risk.
Overlap rules: CI Sweeper owns failing checks (Babysitter never re-fixes the same branch in
the same hour); pause Dependency Sweeper while CI is red on main; Post-Merge runs off-peak.
Before a loop spawns work it reads `STATE.md` for another loop's `acting_on` — collision =
skip and note, never a second fix on the same item.

## 2. Cost, then sign-off (hard gate)

`npx @cobusgreyling/loop cost -p <pattern> -l L1 -c <cadence>` — show the user the daily
token estimate and suggested cap. Loops bill on cadence forever; nothing is scaffolded or
armed until the user approves pattern, cadence, budget, and mechanism.

## 3. Scaffold in the WORKSPACE root

Loop artifacts are Claude material — the workspace repo, never a code repo.

```
npx @cobusgreyling/loop init . --pattern <pattern> --tool claude
npx @cobusgreyling/loop doctor .
```

Scaffolds: `LOOP.md`, `STATE.md`, `loop-budget.md`, `loop-constraints.md`,
`loop-run-log.md`, `.claude/skills/loop-triage|loop-budget|loop-constraints/` (+ the
pattern's fix skills where applicable), `.claude/agents/loop-verifier.md`, and an
`AGENTS.md` template.

## 4. Framework hardening (always, same session)

1. `.claude/agents/loop-verifier.md` ships `model: inherit` → set an explicit alias
   (`model: sonnet`) — inherit on a leader session is a top-tier cost accident. It is the
   loop's maker/checker, distinct from the team's `verifier` employee.
2. The scaffold ships NO `gate.yaml` — create one (`version: 1`) with the security floor as
   denylist: `.env`, `.env.*`, `**/secrets/**`, `**/credentials/**`, `**/*_key*`,
   `**/*_secret*`, `**/migrations/**`, `auth/**`, `payments/**`, `billing/**`;
   `maxFiles: 10`; `autoMergeAllowlist: []` (stays empty until the user opts into L2+).
   Changes are checked with `npx @cobusgreyling/loop-gate check --action commit --paths
   <f1,f2>` (exit 2 = escalate). The gate is advisory — the constraints file makes it binding.
3. `loop-constraints.md` gains the framework bindings (3–5 lines): run `loop-gate check`
   before any commit; all gate/test output → `tmp/gates/loop-<pattern>-<seq>.log`;
   defensive security register in every report; no AI attribution anywhere; PR flow per
   `WORKSPACE_ROLE` — a loop never direct-commits a code repo.
4. Fold anything useful from the scaffolded `AGENTS.md` template into the workspace
   CLAUDE.md, then delete it — two instruction files drift.
5. `loop-budget.md`: write the daily caps the user approved (start from the cost output).
6. Docs, same session: run/status/doctor commands + the first-run command → COMMANDS.md;
   dated CHANGELOG.md entry ("armed <pattern> loop, L1, <cadence>"); a BACKLOG.md item for
   the L2 graduation decision.

## 5. Arm it — native-first ladder (name the feature to the user)

- **Attended, this session** — `/loop <interval> <prompt>`: Claude Code's native recurring
  loop with dynamic self-pacing. First run, verbatim from the scaffold output:
  `/loop 1d $loop-triage — update STATE.md. Report-only week one.`
  In a leader session keep ticks thin: a tick reads state and dispatches employees per the
  routing table; it never grinds inline.
- **Fixed schedule, this session** — a native scheduled task (cron-style): standard 5-field
  cron in local time, fires while the session is idle. Session-only — gone when the session
  ends, recurring jobs auto-expire after 7 days — right for a working week, wrong for
  infrastructure. Pick an off-minute (`3 9 * * 1-5`, not `0 9 * * *`).
- **Durable / unattended** — the only mechanism that survives restarts: an OS scheduler
  (Task Scheduler / cron) running headless Claude in the workspace, model pinned:
  `claude -p "LOOP RUN: run $loop-triage per LOOP.md. Report-only." --model sonnet`,
  with a lockfile check-then-arm and output to `tmp/loops/<pattern>-<date>.log` (the
  process-supervision rule: supervision is code, not conversation). Cadenced runs never
  ride the leader tier.

## 6. Operate and graduate

- Every run: read `loop-constraints.md` FIRST; check `loop-budget.md` (hard stop at cap —
  an extension is REQUESTED in STATE.md, never self-granted); do the work; update
  `STATE.md`; append one JSON line to `loop-run-log.md`; record a Post-Run Critique — one
  concrete change to improve the next cycle.
- Kill switch: a `loop-pause-all` flag in STATE.md stops every loop until the user clears it.
- **Graduation is user-owned, not score-owned** (`loop-audit` scores a fresh scaffold
  100/100 — it measures artifacts, not safety): L1 report-only for week one, always → L2
  (assisted fixes in worktrees, loop-verifier checking, still no auto-merge) only after a
  clean week AND user opt-in → L3 (unattended) only with budget + run-log evidence AND an
  explicit user opt-in. Never skip L1.
- Monthly-ish: `npx @cobusgreyling/loop metrics .` (token/ROI over the run log) → tune the
  cadence or retire the loop. Escalations land in STATE.md `## High Priority`; the session
  pulse surfaces them at session start.

## Proactive loops (the orchestrator's side)

The automation-capture rule's fourth form: a flow that recurs on TIME or EVENTS — morning
triage, PR shepherding, CI watching, changelog drafting before releases — is loop-shaped.
PROPOSE it (pattern + cost estimate + L1 plan, one plain line naming the native feature),
record the proposal in BACKLOG.md, and wait for sign-off. The same scaffold at the PROJECTS
root gives a cross-project morning triage feeding the root HANDOFF. Optional read-only MCP
server for pattern/state queries: `@cobusgreyling/loop-mcp-server`.
