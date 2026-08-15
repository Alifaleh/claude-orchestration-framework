# BRIEF {{ID}} — {{SLUG}} (beat {{N}} for {{EMPLOYEE}})

<!-- Written by the orchestrator (or root on fast path). ID = YYYYMMDD-HHMM-slug. Lives at
     <workspace>/tmp/briefs/<id>-brief.md -->

## OBJECTIVE

_(One sentence.)_

_(Security-verification work — anything that writes or runs code exercising authentication,
rate limiting, isolation, or access control — OPENS with one line naming whose system this is and
that the goal is defence. Then describe mechanisms in mechanical terms: "a load generator", "the
legitimate holder", "sustained failed-login load". See `.claude/rules/engineering.md`, "Writing
about security work".)_

## REPO

`{{ABS_PATH_TO_CODE_REPO}}` — branch: `{{FEATURE_BRANCH}}`

## WRITABLE

_(Exact files/trees this beat may change — disjoint vs any concurrent beat; everything else
read-only.)_

## SPEC

_(The decisions, already made — exact names/values verbatim. The worker implements; it does
not redesign.)_

## NEW CONTEXT

_(Only what the pack/handover don't carry — new sections, interfaces from other beats. NEVER
repeat what CONTEXT_PACK.md already says.)_

## BINDING RULES

_(The 3–5 rules that bite on this task, quoted verbatim from the framework rules — plus the
superpowers skills that bind: TDD for behavior changes, systematic-debugging for bug hunts.)_

## ACCEPTANCE

_(Copied VERBATIM from the leader's mission/plan — never authored by whoever implements or
manages the wave.)_

1. _(numbered, independently checkable)_
2. …

## GATE_SCOPED

```bash
cd {{ABS_PATH_TO_CODE_REPO}} && {{SCOPED_GATE_COMMAND}} > tmp/gates/{{ID}}-<seq>.log 2>&1
```
The engineer's inner loop — run as often as needed, always piped to the log.

## GATE_FULL

```bash
cd {{ABS_PATH_TO_CODE_REPO}} && {{FULL_GATE_COMMAND}} > tmp/gates/{{ID}}-full.log 2>&1
```
The VERIFIER runs this ONCE at beat end — never the engineer.

## REPORT

Write to: `{{WORKSPACE}}/tmp/briefs/{{ID}}-report.md` — STATUS
done|partial|blocked|exceeds-ability · what changed · evidence (per gate: command · exit
code · log path · on failure ≤40-line excerpt + ≤20-line tail) · deviations · risks ·
`DOC TRIGGERS:` / PACK flags.
