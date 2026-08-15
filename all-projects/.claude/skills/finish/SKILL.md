---
name: finish
description: Use when a plan, phase, or release is about to be declared done or merged — or when the user runs /finish. Runs the pre-merge closeout checklist that turns "mostly achieved" into "fully achieved": stale-number scan, live gate re-verification, wording register scan, open-item sweep, docs-alive check, and a go/no-go verdict with evidence.
---

# Closeout checklist (go/no-go before "done")

Run every step; collect evidence; end with a verdict. In an orchestrator session, step 2 and
the greps are delegated (the verifier runs the gate; haiku runs the scans); the leader
assembles the verdict.

1. **Stale-number scan.** Grep `.claude/docs/`, the CONTEXT_PACK, README, and the branch's
   commit messages (`git log <base>..HEAD --format=%B`) for hardcoded test counts, gate
   totals, and baseline numbers. Each hit must either BE the project's single authoritative
   record or reference the command that produces the number — copied values elsewhere are
   findings.

2. **Live re-verification.** Run the project's GATE_FULL (from CONTEXT_PACK/COMMANDS.md,
   verbatim, piped to `tmp/gates/finish-<date>.log`). Diff the live counts against the
   authoritative recorded baseline: lower than recorded = regression, reject; higher = update
   the ONE authoritative record, same session.

3. **Register scan.** Grep the branch's commit messages, changed docs, and new test names for
   attacker-style security wording (per the engineering rule: name the mechanism and the
   property enforced, never the exploit story). Each hit gets a neutral defensive rewrite
   suggested — precision kept, register fixed.

4. **Open-item sweep.** List: the ledger's DEFERRED items · `TODO|FIXME|HACK` grep over the
   branch diff · unchecked ACCEPTANCE criteria in any brief for this plan · pending doc
   triggers (arch change without ARCHITECTURE.md edit, shipped work without a dated CHANGELOG
   entry, stale `*Last updated:*` footers on touched docs, PACK rows now wrong) · a
   `/ponytail-debt` harvest over the branch — a `ponytail:` marker with no named upgrade
   trigger is a finding; ledger deltas go to BACKLOG.md; run `/ponytail full` after to
   restore the ladder mode · automation sweep — manual flows run ≥2× this mission are
   captured per the automation-capture rule (`claude-code-map` table), permission-prompt
   friction → `/permissions` review, skill gaps → `skill-finder`; then write today's date
   (YYYY-MM-DD) into `.claude/automation-audit`.

5. **Attribution + hygiene.** `git log <base>..HEAD` must show the owner as sole author — no
   Co-Authored-By, no AI attribution; no stray files at repo root that belong in `tmp/`;
   `git status` clean or explained.

6. **Verdict.** Output:
   - `GO` — every step clean, with the gate log path and live counts; or
   - `NO-GO` — the numbered blocking findings (smallest fix first), each with file:line and
     the exact correction.

A `NO-GO` list becomes the next beats; re-run `finish` after they land. Never soften a NO-GO
into "minor notes" — deferred polish goes to the ledger's DEFERRED list explicitly.
