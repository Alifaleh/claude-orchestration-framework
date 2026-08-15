# Session pulse - deterministic checks whose output is injected into Claude's context.
# Wired via SessionStart + UserPromptSubmit hooks. Designed to be effectively free:
#   - QUIET when healthy: no output means no context tokens, ever.
#   - Local stat/git-log calls only (milliseconds); network at most once per 6 hours.
#   - Freshness/size notices print at most once per 4-hour window (.claude/last-pulse-nudge)
#     so a known-stale doc never nags on every prompt.
# Branches on location: a directory with workspace.yaml = workspace; otherwise = projects root.
# PowerShell 5.1-safe: no &&, no ternary.

$ErrorActionPreference = 'SilentlyContinue'

function MTimeUtc($p) {
  if (Test-Path $p) { return (Get-Item $p).LastWriteTimeUtc }
  return $null
}

$nowUtc = (Get-Date).ToUniversalTime()
$notices = @()

# Armed loops (build-loop skill) escalate into STATE.md "## High Priority" - surface them.
function Add-StateNotice {
  if (-not (Test-Path 'STATE.md')) { return }
  $inHp = $false; $hp = 0
  foreach ($line in (Get-Content 'STATE.md')) {
    if ($line -match '^## High Priority') { $inHp = $true; continue }
    if ($line -match '^## ') { $inHp = $false; continue }
    if ($inHp) {
      $t = $line.Trim()
      if ($t -and ($t -notmatch '^[-*\s]*none')) { $hp++ }
    }
  }
  if ($hp -gt 0) {
    $script:notices += ('PULSE: STATE.md carries ' + $hp + ' high-priority loop item(s) - read them before new work.')
  }
}

if (Test-Path 'workspace.yaml') {
  # ---------- workspace checks (all local) ----------
  $head = $null
  $t = git log -1 --format=%ct
  if ($t) { $head = [DateTimeOffset]::FromUnixTimeSeconds([long]$t).UtcDateTime }
  $h = MTimeUtc '.claude/HANDOFF.md'
  if ($head -and $h -and ($head -gt $h.AddHours(1))) {
    $notices += 'PULSE: commits are newer than .claude/HANDOFF.md by >1h - bring the handoff current (handoff rule).'
  }
  $c = MTimeUtc '.claude/docs/CHANGELOG.md'
  if ($head -and $c -and ($head -gt $c.AddHours(1))) {
    $notices += 'PULSE: commits with no CHANGELOG trail - reconcile per the project-docs rule.'
  }
  Get-ChildItem '.claude/docs/*.md' | Where-Object { $_.Length -gt 102400 } | ForEach-Object {
    $notices += ('PULSE: .claude/docs/' + $_.Name + ' exceeds 100 KB - run the size-hygiene archival beat (project-docs rule).')
  }
  # Automation-audit staleness. Marker stores yyyy-MM-dd as CONTENT (mtime does not survive clone).
  $aud = $null
  if (Test-Path '.claude/automation-audit') { $aud = (Get-Content '.claude/automation-audit' | Out-String).Trim() }
  $audStale = $true
  if ($aud -match '^\d{4}-\d{2}-\d{2}$') {
    $d = [DateTime]::ParseExact($aud, 'yyyy-MM-dd', $null)
    if ($d -gt $nowUtc.AddDays(-30)) { $audStale = $false }
  } else {
    $aud = $null
  }
  if ($audStale) {
    if ($aud) {
      $notices += ('PULSE: automation audit last run ' + $aud + ' (>30 days) - invoke the claude-code-map skill when the current task allows.')
    } else {
      $notices += 'PULSE: automation audit never run in this workspace - invoke the claude-code-map skill when the current task allows.'
    }
  }
  Add-StateNotice
} else {
  # ---------- projects-root checks ----------
  $marker = '.claude/last-update-check'
  $due = $true
  $m = MTimeUtc $marker
  if ($m) {
    if (($nowUtc - $m).TotalHours -lt 6) { $due = $false }
  }
  if ($due) {
    Get-Date -Format o | Out-File -FilePath $marker -Encoding utf8
    $repo = '__DISTRIBUTION_REPO__'
    if (Test-Path $repo) {
      git -C $repo fetch --quiet
      if ($LASTEXITCODE -eq 0) {
        $remote = (git -C $repo show origin/main:VERSION | Out-String).Trim()
        $localv = (Get-Content '.claude/VERSION' | Out-String).Trim()
        if ($remote -and $localv -and ($remote -ne $localv)) {
          # Update notices bypass the nudge cooldown (they already fire at most once per 6h).
          Write-Output ("PULSE: FRAMEWORK UPDATE - installed " + $localv + ", published " + $remote + ". Apply per CLAUDE.md 'Framework updates' (local ahead = unpushed changes: surface, don't pull). /update forces a re-check.")
        }
      }
    }
  }
  $l = MTimeUtc 'tmp/missions/LEDGER.md'
  $h = MTimeUtc '.claude/HANDOFF.md'
  if ($l -and $h -and ($l -gt $h)) {
    $notices += 'PULSE: the missions LEDGER is newer than the root HANDOFF - bring the handoff current.'
  }
  Add-StateNotice
}

# Freshness/size notices: at most once per 4h window.
if ($notices.Count -gt 0) {
  $nmark = '.claude/last-pulse-nudge'
  $nm = MTimeUtc $nmark
  $cool = $true
  if ($nm) {
    if (($nowUtc - $nm).TotalHours -lt 4) { $cool = $false }
  }
  if ($cool) {
    $notices | ForEach-Object { Write-Output $_ }
    New-Item -ItemType File -Path $nmark -Force | Out-Null
  }
}
exit 0
