#!/usr/bin/env python
"""PostToolUse hook: runs a per-project test slice after every Edit/Write/
NotebookEdit. Reads <project-root>/.claude/gates.json; on a matching rule,
runs the configured slice command and reports red/green via exit code plus
a per-session state file that stop-gate.py reads. Schema + examples live at
skills/team/templates/gates.json. Fails open on every internal error — a
broken hook must never trap a session.
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

STATE_DIR_NAME = "tmp/gates"  # relative to project root
DEFAULT_TIMEOUT_S = 60
MAX_LOG_TAIL_LINES = 25


def safe_session_id(session_id: str) -> str:
    """Sanitize an untrusted session_id for use in a filename. Kept
    byte-identical in stop-gate.py — a divergence here silently breaks the
    state-file link between the two hooks."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", session_id or "unknown")
    return cleaned[:200] or "unknown"


def find_project_root(start: Path) -> Path | None:
    """Walk up from `start` (a directory) for the nearest ancestor whose
    .claude/gates.json exists. Returns that ancestor (the project root), or
    None if no ancestor has one."""
    cur = start
    while True:
        if (cur / ".claude" / "gates.json").is_file():
            return cur
        if cur.parent == cur:
            return None
        cur = cur.parent


def log_config_error(root: Path, message: str) -> None:
    try:
        gates_dir = root / STATE_DIR_NAME
        gates_dir.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(gates_dir / "hook-errors.log", "a", encoding="utf-8") as f:
            f.write(f"{stamp} test-gate: {message}\n")
    except OSError:
        pass  # a broken log write must never crash the hook


def read_state(state_path: Path) -> dict:
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        return loaded if isinstance(loaded, dict) else {}
    except (OSError, ValueError):
        return {}


def write_state_atomic(state_path: Path, state: dict) -> None:
    tmp_path = state_path.with_suffix(state_path.suffix + f".tmp{os.getpid()}")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(state, f)
    os.replace(tmp_path, state_path)


def tail_lines(path: Path, n: int) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        return "".join(lines[-n:])
    except OSError:
        return ""


def kill_process_tree(pid: int) -> None:
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                capture_output=True,
            )
        else:
            os.killpg(os.getpgid(pid), signal.SIGKILL)
    except (OSError, subprocess.SubprocessError):
        pass


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError, OSError):
        return 0
    if not isinstance(payload, dict):
        return 0

    tool_name = payload.get("tool_name") or ""
    tool_input = payload.get("tool_input") or {}
    session_id = payload.get("session_id") or "unknown"
    cwd_hint = payload.get("cwd")

    if tool_name == "NotebookEdit":
        raw_file_path = tool_input.get("notebook_path")
    else:
        raw_file_path = tool_input.get("file_path")
    if not raw_file_path:
        return 0

    file_path = Path(raw_file_path)
    if not file_path.is_absolute() and cwd_hint:
        file_path = Path(cwd_hint) / file_path
    file_path = file_path.resolve()

    root = find_project_root(file_path.parent)
    if root is None:
        return 0

    gates_json_path = root / ".claude" / "gates.json"
    try:
        with open(gates_json_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (OSError, ValueError):
        log_config_error(root, f"unparseable gates.json at {gates_json_path}")
        return 0

    if not isinstance(config, dict) or not isinstance(config.get("rules"), list):
        log_config_error(root, "gates.json missing a top-level 'rules' list")
        return 0

    rel_path = file_path.relative_to(root).as_posix()

    matched_rule = None
    for rule in config["rules"]:
        if not isinstance(rule, dict) or "match" not in rule or "slice" not in rule:
            log_config_error(root, f"bad rule (missing match/slice): {rule!r}")
            return 0
        match_pat, slice_cmd = rule["match"], rule["slice"]
        if not isinstance(match_pat, str) or not (slice_cmd is None or isinstance(slice_cmd, str)):
            log_config_error(root, f"bad rule (wrong value types): {rule!r}")
            return 0
        if fnmatch.fnmatch(rel_path, match_pat):
            matched_rule = rule
            break

    if matched_rule is None:
        return 0  # no matching rule — silent, this is not an error

    slice_cmd = matched_rule["slice"]
    if slice_cmd is None:
        return 0  # explicit opt-out

    timeout_s = matched_rule.get("timeout_s", DEFAULT_TIMEOUT_S)
    if not isinstance(timeout_s, (int, float)) or timeout_s <= 0:
        timeout_s = DEFAULT_TIMEOUT_S

    gates_dir = root / STATE_DIR_NAME
    gates_dir.mkdir(parents=True, exist_ok=True)
    ts_label = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    log_path = gates_dir / f"hook-{ts_label}-{os.getpid()}.log"
    state_path = gates_dir / f"hook-state-{safe_session_id(session_id)}.json"

    command = slice_cmd.replace("{file}", f'"{file_path}"')

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    prior_state = read_state(state_path)
    prior_blocks = prior_state.get("blocks", 0)
    if not isinstance(prior_blocks, int):
        prior_blocks = 0

    log_f = open(log_path, "w", encoding="utf-8")
    timed_out = False
    exit_code = None
    try:
        popen_kwargs = dict(
            shell=True,
            cwd=str(root),
            env=env,
            stdout=log_f,
            stderr=subprocess.STDOUT,
        )
        if os.name != "nt":
            popen_kwargs["start_new_session"] = True
        proc = subprocess.Popen(command, **popen_kwargs)
        try:
            exit_code = proc.wait(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            timed_out = True
            kill_process_tree(proc.pid)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
    finally:
        log_f.close()

    if timed_out:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("WARN timeout\n")
        return 0  # slowness never blocks; prior state is left untouched

    now = time.time()
    if exit_code == 0:
        write_state_atomic(state_path, {
            "status": "green", "log": str(log_path), "ts": now, "blocks": 0,
        })
        return 0

    write_state_atomic(state_path, {
        "status": "red", "log": str(log_path), "ts": now, "blocks": prior_blocks,
    })
    tail = tail_lines(log_path, MAX_LOG_TAIL_LINES)
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    sys.stderr.write(f"test slice red — log: {log_path}\n{tail}")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)  # a broken hook must never trap a session
