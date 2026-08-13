#!/bin/sh
# Session pulse — deterministic checks whose output is injected into Claude's context.
# Wired via SessionStart + UserPromptSubmit hooks. Designed to be effectively free:
#   - QUIET when healthy: no output → no context tokens, ever.
#   - Local stat/git-log calls only (milliseconds); network at most once per 6 hours.
#   - Freshness/size notices print at most once per 4-hour window (.claude/last-pulse-nudge)
#     so a known-stale doc never nags on every prompt.
# Branches on location: a directory with workspace.yaml = workspace; otherwise = projects root.

mt() { stat -c %Y "$1" 2>/dev/null || stat -f %m "$1" 2>/dev/null || echo 0; }

now=$(date +%s)
notices=""
add() { notices="${notices}${1}
"; }

if [ -f workspace.yaml ]; then
  # ---------- workspace checks (all local) ----------
  head_t=$(git log -1 --format=%ct 2>/dev/null)
  [ -n "$head_t" ] || head_t=0
  if [ -f .claude/HANDOFF.md ] && [ "$head_t" -gt $(( $(mt .claude/HANDOFF.md) + 3600 )) ]; then
    add "PULSE: commits are newer than .claude/HANDOFF.md by >1h — bring the handoff current (handoff rule)."
  fi
  if [ -f .claude/docs/CHANGELOG.md ] && [ "$head_t" -gt $(( $(mt .claude/docs/CHANGELOG.md) + 3600 )) ]; then
    add "PULSE: commits with no CHANGELOG trail — reconcile per the project-docs rule."
  fi
  for f in .claude/docs/*.md; do
    [ -f "$f" ] || continue
    if [ "$(wc -c < "$f")" -gt 102400 ]; then
      add "PULSE: $f exceeds 100 KB — run the size-hygiene archival beat (project-docs rule)."
    fi
  done
else
  # ---------- projects-root checks ----------
  marker=.claude/last-update-check
  if [ ! -f "$marker" ] || [ $(( now - $(mt "$marker") )) -ge 21600 ]; then
    date -Iseconds > "$marker" 2>/dev/null || : > "$marker"
    repo="__DISTRIBUTION_REPO__"
    if [ -d "$repo" ] && git -C "$repo" fetch --quiet; then
      remote=$(git -C "$repo" show origin/main:VERSION 2>/dev/null | tr -d '[:space:] ')
      localv=$(tr -d '[:space:] ' < .claude/VERSION 2>/dev/null)
      if [ -n "$remote" ] && [ -n "$localv" ] && [ "$remote" != "$localv" ]; then
        # Update notices bypass the nudge cooldown (they already fire ≤ once per 6h).
        echo "PULSE: FRAMEWORK UPDATE — installed $localv, published $remote. Apply per CLAUDE.md 'Framework updates' (local ahead = unpushed changes: surface, don't pull). /update forces a re-check."
      fi
    fi
  fi
  if [ -f tmp/missions/LEDGER.md ] && [ -f .claude/HANDOFF.md ] && [ tmp/missions/LEDGER.md -nt .claude/HANDOFF.md ]; then
    add "PULSE: the missions LEDGER is newer than the root HANDOFF — bring the handoff current."
  fi
fi

# Freshness/size notices: at most once per 4h window.
if [ -n "$notices" ]; then
  nmark=.claude/last-pulse-nudge
  if [ ! -f "$nmark" ] || [ $(( now - $(mt "$nmark") )) -ge 14400 ]; then
    printf '%s' "$notices"
    : > "$nmark"
  fi
fi
exit 0
