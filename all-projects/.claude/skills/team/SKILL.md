---
name: team
description: Use when an orchestrator session has 2+ beats of work in a project — hires and runs the persistent employee team (engineer/verifier/reviewer) with beat briefs, health checks, knowledge handovers, promotions, and the roster; absorbs the ledger and fix-round discipline for formal plans. Leader-only; employees never invoke this.
---

# The team — persistent employees

Topology per project: leader (this session, the system architect) + `eng-a` (+ `eng-b`/`eng-c`
only for file-disjoint beats) + `verifier` + `reviewer`. Employees are **named background
agents reused across beats** — never spawn-per-task. Workers never re-delegate. DB-writing and
Playwright beats serialize through the verifier. No standing lead layer; a wave-scoped
top-tier lead exists ONLY when decomposition requires reading code the leader hasn't read —
its criteria still come from the leader verbatim, its beats still go to the standing
reviewer.

## Hire

Spawn via the Agent tool: agent type per role def (`engineer`/`verifier`/`reviewer`),
`run_in_background: true`, explicit `model:` alias per the routing table in the projects-root
CLAUDE.md (omission = the inherit footgun: the agent silently runs on the leader's model at
leader cost). Employee effort comes from the def's `effort:` frontmatter and never changes
during its life (an effort flip invalidates its prompt cache). Hire prompt ≈6 lines: "You are
<name>, persistent <role> on <project>. Read `.claude/docs/CONTEXT_PACK.md` fully, then
`tmp/team/<name>/HANDOVER.md` if it exists. Reply with your onboarding receipt." Check the
receipt against the pack — a wrong test command or missed inherited WIP = defective
onboarding → rehire; never patch onboarding by chat.

## Beats

One beat = one brief file `tmp/briefs/<id>-brief.md` (format: `.claude/templates/brief.md` —
OBJECTIVE · WRITABLE · SPEC · NEW CONTEXT · numbered ACCEPTANCE (copied VERBATIM from the
leader's plan — never authored downstream) · GATE_SCOPED · GATE_FULL · report path). Send via
SendMessage to the employee's name: ~4 lines pointing at the brief plus anything newer than
its last beat — never repeat what the pack or handover already carries. Reports land in
files; replies stay ≤10 lines; a report flags any manual flow it ran ≥2× with
`AUTOMATION:` — the leader captures via the claude-code-map skill. Cycle per beat: engineer works → verifier runs GATE_FULL (one
SendMessage) → reviewer verdict (a HIGHER tier than the writer) → leader ticks the numbered
criteria → next beat.

**Test-first prep-beat (gray-zone flip):** when the routing gate fails on "no failing tests
exist", a FRESH sonnet agent with no implementation context writes the failing tests from the
SPEC first (single-file-against-explicit-spec scope); the top tier contributes only an
assertion list when tests span modules or encode hard-trigger invariants. The reviewer's
criterion #1 on such beats: test adequacy vs SPEC.

**Bugs:** two-phase always — a read-only diagnosis beat (written cause + reproducing failing
test) → the fix beat routed on that artifact.

## Health check — every beat, from the reply already in hand

Handover triggers: (a) ≥8 beats served; (b) drift — re-asking pack facts, wrong paths,
bloating replies; (c) the next beat needs a different tier (promotion/demotion); (d) 2 failed
fix rounds on one brief (re-scope first, usually promote); (e) the employee's working context
has grown past ~50k (long-horizon degradation).

## Handover → rehire (this IS the model switch — model and effort are fixed at spawn)

1. SendMessage: "Handover: write `tmp/team/<name>/HANDOVER.md` per the team skill's
   `templates/HANDOVER.md`, then stop."
2. TaskStop the agent.
3. Spawn fresh with the SAME NAME at the new tier — the name re-binds to the newest agent.
   The successor onboards from pack + handover; to the roster and the user it is the same
   employee with a new brain.

Max 2 promotions per brief, then re-scope (the 2-strike rule).

## Roster + session rituals

`tmp/team/ROSTER.md` (format: `templates/ROSTER.md`): one line per employee — name · role ·
model · beats served · open brief · handover path — plus a newest-first event log. Update on
hire/retire/promote.
**Ledger before dispatch:** the ledger's `dispatched(<model>)` line is written BEFORE the
SendMessage/spawn, never after — a usage-limit kill mid-wave must leave an accurate recovery
map. Ledger events: `<id>: dispatched(<model>) | consults(<n>) | accepted |
rejected(<reason>) | re-scoped → <id'> | promoted(<tier>) | PARKED(<why>)`. Under a heavy
usage week, prefer narrow waves (1–2 beats) so a cutoff strands less in-flight work.
**Conservation mode:** at the first top-tier-usage warning (or a requested-opus reply visibly
running on a lesser model): implementation → 100% sonnet/haiku; remaining opus reserved for
reviews + hard-trigger beats; a beat whose review cannot run on opus is PARKED, never
down-reviewed.
**Leader hygiene:** at each phase/wave boundary check carriage; past ~250k average context
per message → finish the wave's ledger entries, then start fresh re-reading plan + ROSTER +
pack (state-on-disk makes this free).
**Session close:** every active employee writes its HANDOVER → TaskStop all → roster updated
→ if your tooling tracks token usage, record: session total · tokens-per-accepted-brief (the
framework's acceptance metric) · audit flags — any agent that inherited the leader's model
(inherit defect) · any sonnet-written beat whose review ran below the review tier · leader
average carriage vs the ~250k budget.
**Session open:** read ROSTER + handovers; rehire lazily — each employee at its first needed
beat.

## Formal plans (absorbed subagent-driven-development discipline)

Per-plan ledger stays at `.superpowers/sdd/<plan-basename>/progress.md` — first line names
the plan; one line per event. Pre-flight: scan the plan for same-file collisions before wave
1. Fix rounds: rounds 1–3 resume the SAME engineer with a 1–3-line correction; round 4 =
promote; cap 5, then adjudicate with the user (park with a written ruling, or stop). Minor
findings → the ledger's DEFERRED list, never silently dropped. Wave end: verifier runs the
full suite once + a top-tier review over the wave diff. Plan end: whole-branch review on the
top tier; docs-alive + PACK triggers settled by the leader; then run the `finish` skill's
closeout checklist — a plan is not "complete" until its GO verdict. Do NOT invoke
`superpowers:subagent-driven-development`'s dispatch loop — this skill supersedes it;
brainstorming, TDD, and systematic-debugging still bind employees via their briefs.
