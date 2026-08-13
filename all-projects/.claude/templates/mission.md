# MISSION {{ID}} — {{PROJECT_NAME}}

<!-- Written by the root session. ID = YYYYMMDD-HHMM-slug. Lives at
     All Projects/tmp/missions/<project>/<id>-mission.md -->

## Objective

_(What done looks like, in outcomes — not implementation steps.)_

## Workspace

`__PROJECTS_ROOT__/{{PROJECT_NAME}}`

## Constraints & decisions already made

_(Decisions the orchestrator must NOT reopen; risky areas; what's out of scope.)_

## Acceptance criteria

1. _(numbered, checkable, each verifiable by evidence)_
2. …

## Plan

Two-phase run: the PLAN-phase output is saved at `{{MISSION_DIR}}/{{ID}}-plan.md`; execution
follows only after root reviewed it (and the user signed off on any security-floor operation).
The plan decomposes into beats (WRITABLE · routing tier per the quality gate · GATE_SCOPED ·
GATE_FULL each); execution runs them through the `team` skill's persistent employees.

## Report

Write the report to: `{{MISSION_DIR}}/{{ID}}-report.md`
Format: `STATUS: DONE | NEEDS-DECISION | BLOCKED` · each criterion with its evidence (gate
output verbatim, reviewer verdict, PR links/commits) · doc updates made · `VAULT TRIGGERS:`
(usually empty — only what matters beyond this project).
