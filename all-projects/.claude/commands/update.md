---
description: Check the framework distribution repo for a newer version right now and apply it per protocol.
---

When the user types `update` (or says "update the framework"):

Run the Framework-updates procedure from this directory's CLAUDE.md immediately, ignoring the
6-hour marker age: refresh `.claude/last-update-check`, fetch the distribution clone, compare
its `origin/main:VERSION` against `.claude/VERSION`, then act per the procedure — same
version → say so; remote newer → announce it and apply the Update protocol (framework-tree
steps yourself; per-workspace migrations dispatched to workers); local newer → surface the
unpushed framework changes instead of pulling. Report both versions and everything that
changed.
