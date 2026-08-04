# BRIEF {{ID}} — {{SLUG}}

<!-- Written by the orchestrator (or root on fast path). ID = YYYYMMDD-HHMM-slug. Lives at
     <workspace>/tmp/briefs/<id>-brief.md -->

## Objective

_(One task, precisely.)_

## REPO

`{{ABS_PATH_TO_CODE_REPO}}` — branch: `{{FEATURE_BRANCH}}`

## WRITABLE

_(Exact files/dirs this brief may change — disjoint from every concurrent brief.)_

## READ FIRST

_(Paths the worker must read before editing anything.)_

## SPEC

_(The decisions, already made. The worker implements; it does not redesign.)_

## BINDING RULES

_(The 3–5 rules that bite on this task, quoted verbatim from the framework rules.)_

## ACCEPTANCE

1. _(numbered, checkable)_
2. …

## GATE

```bash
cd {{ABS_PATH_TO_CODE_REPO}} && {{GATE_COMMAND}}
```
Output is returned verbatim — including failures.

## REPORT

_(Implementer briefs only)_ Write to: `{{WORKSPACE}}/tmp/briefs/{{ID}}-report.md` — what changed,
gate output verbatim, then `DOC TRIGGERS:`.
