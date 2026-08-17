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

# Armed loops (build-loop skill) escalate into STATE.md "## High Priority" — surface them.
state_hp() {
  [ -f STATE.md ] || return 0
  hp=$(awk '/^## High Priority/{f=1;next} /^## /{f=0} f && NF' STATE.md | grep -civ '^[-* ]*none')
  if [ "${hp:-0}" -gt 0 ] 2>/dev/null; then
    add "PULSE: STATE.md carries ${hp} high-priority loop item(s) — read them before new work."
  fi
}

if [ -f workspace.yaml ]; then
  # ---------- workspace checks (all local) ----------
  # Crew mode (3.8.0): surface non-default only (this also fires on UserPromptSubmit;
  # absent/solo = documented default, silent). Direct echo — bypasses the 4h cooldown.
  crew=$(grep -m1 '^CREW_MODE=' .env 2>/dev/null | cut -d= -f2- | tr 'A-Z' 'a-z' | tr -cd 'a-z')
  if [ -n "$crew" ] && [ "$crew" != "solo" ]; then
    echo "CREW_MODE: $crew"
  fi
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
  # Automation-audit staleness. Marker stores YYYY-MM-DD as CONTENT (mtime does not
  # survive clone); dates compare numerically once dashes are stripped.
  aud=$(cat .claude/automation-audit 2>/dev/null | tr -d '[:space:]')
  case "$aud" in
    [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) aud_n=$(printf '%s' "$aud" | tr -d '-') ;;
    *) aud_n="" ;;
  esac
  cutoff=$(date -d '30 days ago' +%Y%m%d 2>/dev/null || date -v-30d +%Y%m%d 2>/dev/null)
  if [ -n "$cutoff" ]; then
    if [ -z "$aud_n" ]; then
      add "PULSE: automation audit never run in this workspace — invoke the claude-code-map skill when the current task allows."
    elif [ "$aud_n" -lt "$cutoff" ] 2>/dev/null; then
      add "PULSE: automation audit last run $aud (>30 days) — invoke the claude-code-map skill when the current task allows."
    fi
  fi
  state_hp
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
  state_hp
fi

# Daily burn line (framework 4.0.0): cache at ~/.claude/usage-data/burn-<YYYYMMDD>.txt.
# Cache hit -> print it. Cache miss -> kick off a DETACHED refresh (redirected from
# stdin/stdout/stderr so it truly disowns from this hook's pipes) and print nothing
# this run — never block session start on a live token scan. Refresh writes to a
# .tmp file then renames on success, so a still-running refresh never looks like a
# present-but-empty cache to the next session. Direct echo — bypasses the 4h notices
# cooldown below, like CREW_MODE/FRAMEWORK UPDATE above; the daily cache filename is
# already its own once-a-day throttle.
{
  burn_dir="$HOME/.claude/usage-data"
  burn_cache="$burn_dir/burn-$(date +%Y%m%d).txt"
  if [ -f "$burn_cache" ]; then
    cat "$burn_cache" 2>/dev/null
  else
    mkdir -p "$burn_dir" 2>/dev/null
    burn_script_dir=$(dirname "$0")
    ( PYTHONIOENCODING=utf-8 python "$burn_script_dir/token-report.py" --yesterday-summary \
        >"$burn_cache.tmp" 2>/dev/null </dev/null \
        && mv "$burn_cache.tmp" "$burn_cache" & )
  fi
} 2>/dev/null

# Freshness/size notices: at most once per 4h window.
if [ -n "$notices" ]; then
  nmark=.claude/last-pulse-nudge
  if [ ! -f "$nmark" ] || [ $(( now - $(mt "$nmark") )) -ge 14400 ]; then
    printf '%s' "$notices"
    : > "$nmark"
  fi
fi
exit 0
