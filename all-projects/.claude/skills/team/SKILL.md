---
name: team
description: Use when an orchestrator session has 2+ beats of work in a project — hires and runs the persistent employee team (engineer/verifier/reviewer) with beat briefs, health checks, knowledge handovers, promotions, and the roster; absorbs the ledger and fix-round discipline for formal plans. Leader-only; employees never invoke this.
---

# The team — persistent employees

Topology per project: leader (this session, the system architect) + wave-scoped `foreman` +
`eng-a` (+ `eng-b`/`eng-c` only in `duo`/`full` crew modes for file-disjoint beats — never in
`solo`) + `verifier` + `reviewer`. Employees
are **live background agents continued across beats** — hired once, never spawn-per-task; a
fresh Agent dispatch for an already-hired name is a protocol violation (it re-reads the whole
project and orphans the live context). Workers never re-delegate; the foreman is the sole
exception. DB-writing and Playwright beats serialize through the verifier. No STANDING lead
layer — the foreman exists per wave and dissolves with its report.

## Crew mode

`CREW_MODE=<solo|duo|full>` in the workspace `.env`; absent or unknown = `solo` (tell the
user on unknown; the session pulse surfaces non-default modes). Every wave dispatch carries
`crew: <mode>`. Fan-out: solo = 1 engineer lane serial · duo = ≤2 file-disjoint · full = 3–5
file-disjoint. Review batching: solo/duo = ONE combined top-tier review per wave over all
non-hard-trigger diffs (criteria still ticked per beat); full = per-beat standard + T-light
batching. Every mode: hard-trigger beats keep top-tier engineer + per-beat review;
verifier/scout/researcher unchanged; leader discipline (dormancy, plan-by-path, boundary
bookkeeping) is mode-independent. Switch ONLY on the user's ask:
`sed -i 's/^CREW_MODE=.*/CREW_MODE=<new>/' .env` (or `echo CREW_MODE=<new> >> .env` if
absent) — never shell-print `.env` — then apply immediately and note the switch in HANDOFF.

## Hire

Spawn via the Agent tool: agent type per role def (`engineer`/`verifier`/`reviewer`/`foreman`),
`run_in_background: true`, explicit `model:` alias per the routing table in the projects-root
CLAUDE.md (omission = the inherit footgun: the agent silently runs on the leader's model at
leader cost; the routing-floor hook denies it). Employee effort comes from the def's `effort:`
frontmatter and never changes during its life (an effort flip invalidates its prompt cache).
Hire prompt ≈6 lines: "You are <name>, persistent <role> on <project>. Read
`.claude/docs/CONTEXT_PACK.md` fully, then `tmp/team/<name>/HANDOVER.md` if it exists. Reply
with your onboarding receipt." Check the receipt against the pack — a wrong test command or
missed inherited WIP = defective onboarding → rehire; never patch onboarding by chat. Record
the spawn's agent ID in the roster: every later beat and fix round is a SendMessage
continuation of that live agent (idle background employees cost nothing; each wake rides the
prompt cache). Hire lazily — each employee at its first needed beat, never the whole bench
upfront.

## Beats

One beat = one brief file `tmp/briefs/<id>-brief.md` (format: `.claude/templates/brief.md` —
OBJECTIVE · WRITABLE · STANDING RULINGS (pre-authorized routine grants: use → log in report,
never halt) · SPEC · NEW CONTEXT · numbered ACCEPTANCE (copied VERBATIM from the
leader's plan — never authored downstream) · GATE_SCOPED · report path; GATE_FULL lives at
the wave level). Send via SendMessage to the employee's name: ~4 lines pointing at the brief
plus anything newer than its last beat — never repeat what the pack or handover already
carries. Reports land in files; replies stay ≤10 lines; a report flags any manual flow it
ran ≥2× with `AUTOMATION:` — the leader captures via the claude-code-map skill. Cycle per
beat: engineer works → reviewer verdict (a HIGHER tier than the writer) → criteria ticked →
next beat; the verifier launches GATE_FULL ONCE at wave end in the background — the wave
closes only on its green, but no beat or review ever waits on it mid-wave.

**Test-first prep-beat (hard-trigger/cross-module only):** a FRESH sonnet agent with no
implementation context writes the failing tests from the SPEC first ONLY when they encode
hard-trigger or cross-module invariants (the top tier contributes only the assertion list);
the reviewer's criterion #1 on such beats: test adequacy vs SPEC. Routine beats write their
tests FIRST in-beat — the order must be visible in the report/commits; contamination risk
applies to deriving tests from implementation, not to spec-driven test-first.

**Bugs:** two-phase always — written cause + reproducing failing test BEFORE any fix.
Reproducible single-module bugs: ONE dispatch does diagnose-then-fix, cause artifact first
in its report. Uncertain reproduction or cross-module: separate read-only diagnosis beat,
then the fix routed on that artifact.

## Waves — the foreman

A wave with ≥2 beats goes to ONE `foreman` (background; `model: sonnet`, or the top tier
when the wave carries a hard-trigger beat). Its dispatch carries: the plan file PATH + wave
heading (the foreman's FIRST action is reading that wave section from disk as verbatim law —
the leader never pastes it) · the roster with live agent IDs · gate commands ·
`crew: <mode>` · wave report path `tmp/briefs/wave-<n>-report.md`. The leader then goes
DORMANT until the report notification — any other notification during the wave (grandchild
hires/completions, intermediate stops) is not an event: end the turn immediately, no
bookkeeping, no status writes, no spot-reads. Single-beat waves skip the foreman and dispatch
the employee directly. Backstop (the one exception): a foreman notification arriving WITHOUT
its wave report is a stalled wave — SendMessage it to continue (its def forbids stopping with
live children; the leader's one relay message is the recovery, never a re-dispatch).

The foreman authors NO criteria, pipelines beats and reviews, runs fix rounds 1–3 against the
SAME live engineer, parks a blocked beat while the wave's other beats continue, and interrupts
the leader mid-wave ONLY when the whole wave is stopped — every other escalation (round-4
promotions, requirement ambiguity, observations) batches into the wave report. **Review
batching by crew mode:** in `full`, T-light beats (≤~50 changed
lines, single module, no hard-trigger surface, scoped gate green) get ONE reviewer pass over
their combined diffs; in `solo`/`duo`, ALL non-hard-trigger beats batch into ONE top-tier
review per wave over the combined diff. Per-beat criteria are still ticked individually in
every mode; hard-trigger beats keep per-beat top-tier review in every mode.

Wave report: header (wave id · duration · dispatch count) + per-beat verdict with the
reviewer's verdict VERBATIM (a paraphrased quality claim is invalid) · gate exit codes +
`tmp/gates/` paths · files touched · fix rounds · AUTOMATION flags · checkpoints ·
escalations verbatim. The leader ticks wave criteria from the report, spot-reads
hard-trigger reviewer reports, appends the wave line (duration + dispatches) to HANDOFF, and
only then plans the next wave.

## Health check — every beat, from the reply already in hand

Handover triggers: (a) ≥8 beats served; (b) drift — re-asking pack facts, wrong paths,
bloating replies; (c) the next beat needs a different tier (promotion/demotion); (d) 2 failed
fix rounds on one brief (re-scope first, usually promote); (e) the employee's working context
has grown past ~50k or ~150 messages (long-horizon degradation) — employees also
self-checkpoint at that bound, reporting `exceeds-ability` + checkpoint path.

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
**Session close:** every active employee writes its HANDOVER → TaskStop all → roster updated
→ if your tooling tracks token usage, record: session total · tokens-per-accepted-brief (the
framework's acceptance metric) · audit flags — any agent that inherited the leader's model
(inherit defect) · any sonnet-written beat whose review ran below the review tier.
**Session open:** read ROSTER + handovers; rehire lazily — each employee at its first needed
beat.

## Formal plans (absorbed subagent-driven-development discipline)

Per-plan ledger stays at `.superpowers/sdd/<plan-basename>/progress.md` — first line names
the plan; one line per event. Pre-flight: the plan has passed the plan diet
(project-orchestrator rule — DELIVERABLE named, beats costed + traced, fat cut to BACKLOG);
then scan the plan for same-file collisions before wave 1. Fix rounds: rounds 1–3 resume the SAME engineer with a 1–3-line correction; round 4 =
promote; cap 5, then adjudicate with the user (park with a written ruling, or stop). Minor
findings → the ledger's DEFERRED list, never silently dropped. Wave end: verifier runs the
full suite once + a top-tier review over the wave diff. Plan end: whole-branch review on the
top tier; docs-alive + PACK triggers settled by the leader; then run the `finish` skill's
closeout checklist — a plan is not "complete" until its GO verdict. Do NOT invoke
`superpowers:subagent-driven-development`'s dispatch loop — this skill supersedes it;
brainstorming, TDD, and systematic-debugging still bind employees via their briefs.
