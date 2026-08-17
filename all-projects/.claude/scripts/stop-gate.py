#!/usr/bin/env python
"""Stop hook: blocks session end while the last test-gate.py slice is red.
Reads the same <project-root>/tmp/gates/hook-state-<session_id>.json that
test-gate.py writes. Self-disarms after 2 blocks and treats state older than
30 minutes as stale, so it never traps a session on an abandoned edit. Fails
open on every internal error.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

STATE_DIR_NAME = "tmp/gates"
STALE_AFTER_S = 30 * 60
# ponytail: stop-gate disarms for the session after 2 blocks; per-edit feedback still fires — revisit if red-ignoring shows up in wave reports
MAX_BLOCKS = 2


def safe_session_id(session_id: str) -> str:
    """Byte-identical to test-gate.py's helper — a divergence here silently
    breaks the state-file link between the two hooks."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", session_id or "unknown")
    return cleaned[:200] or "unknown"


def find_project_root(start: Path) -> Path | None:
    cur = start
    while True:
        if (cur / ".claude" / "gates.json").is_file():
            return cur
        if cur.parent == cur:
            return None
        cur = cur.parent


def write_state_atomic(state_path: Path, state: dict) -> None:
    tmp_path = state_path.with_suffix(state_path.suffix + f".tmp{os.getpid()}")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(state, f)
    os.replace(tmp_path, state_path)


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError, OSError):
        return 0
    if not isinstance(payload, dict):
        return 0

    if payload.get("stop_hook_active"):
        return 0  # official loop guard

    cwd = payload.get("cwd")
    session_id = payload.get("session_id") or "unknown"
    if not cwd:
        return 0

    root = find_project_root(Path(cwd).resolve())
    if root is None:
        return 0

    state_path = root / STATE_DIR_NAME / f"hook-state-{safe_session_id(session_id)}.json"
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
    except (OSError, ValueError):
        return 0
    if not isinstance(state, dict):
        return 0

    if state.get("status") != "red":
        return 0

    try:
        age_s = time.time() - float(state.get("ts"))
    except (TypeError, ValueError):
        return 0  # can't establish freshness — fail open
    if age_s >= STALE_AFTER_S:
        return 0

    blocks = state.get("blocks", 0)
    if not isinstance(blocks, int):
        blocks = 0
    if blocks >= MAX_BLOCKS:
        return 0  # self-disarm; leave state as is

    state["blocks"] = blocks + 1
    write_state_atomic(state_path, state)

    log_path = state.get("log", "<unknown>")
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    sys.stderr.write(f"test slice red since last edit — fix before finishing. Log: {log_path}\n")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)  # a broken hook must never trap a session
