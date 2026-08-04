---
description: Fetch and fast-forward every repo in this workspace; flag anything needing action.
---

When the user types `sync` — and FIRST at every session start, and again before creating a
feature branch:

1. If the workspace has its own `scripts/sync.sh` (or `.ps1`), run THAT — it is the project's
   blessed sync — and relay its output. Otherwise:
2. For the workspace repo and EVERY repo in `workspace.yaml`: `git fetch`, then
   `git pull --ff-only` on the checked-out branch; where `submodules: true`, follow with
   `git submodule update --init --recursive`. Never force anything, never stash silently.
3. Report one line per repo; flag plainly:
   - local changes or a diverged branch → action needed by the user before anything else
   - a repo sitting on a feature branch → fetched only; rebase it on its base branch before
     pushing
4. team_member role: also run `gh pr status` — changes-requested PRs get fixed before new work.
