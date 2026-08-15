"""Regression battery for routing-floor.py (lives beside the hook).

Deny cases assert exit 2 AND the 'routing-floor' marker on stderr; allow = exit 0.
"""
import json
import subprocess
import sys
from pathlib import Path

RF = str(Path(__file__).with_name("routing-floor.py"))
RUNNER = [sys.executable, RF]

# (expected_exit, tool_input dict)
CASES = [
    # unset model + unpinned type -> deny
    (2, {"subagent_type": "general-purpose", "prompt": "x", "description": "y"}),
    (2, {"prompt": "x", "description": "y"}),  # no type at all = general-purpose
    (2, {"subagent_type": "claude", "prompt": "x"}),
    (2, {"subagent_type": "code-simplifier:code-simplifier", "prompt": "x"}),
    (2, {"subagent_type": "general-purpose", "model": "", "prompt": "x"}),  # empty = unset
    # explicit model -> allow, any type
    (0, {"subagent_type": "general-purpose", "model": "sonnet", "prompt": "x"}),
    (0, {"subagent_type": "claude", "model": "haiku", "prompt": "x"}),
    (0, {"model": "opus", "prompt": "x"}),
    (0, {"subagent_type": "general-purpose", "model": "fable", "prompt": "x"}),  # audit-caught, not hook-blocked
    # pinned-def types -> allow without model
    (0, {"subagent_type": "scout", "prompt": "x"}),
    (0, {"subagent_type": "verifier", "prompt": "x"}),
    (0, {"subagent_type": "reviewer", "prompt": "x"}),
    (0, {"subagent_type": "researcher", "prompt": "x"}),
    (0, {"subagent_type": "engineer", "prompt": "x"}),
    (0, {"subagent_type": "foreman", "prompt": "x"}),
    (0, {"subagent_type": "Explore", "prompt": "x"}),
    (0, {"subagent_type": "explore", "prompt": "x"}),
    (0, {"subagent_type": "claude-code-guide", "prompt": "x"}),
    (0, {"subagent_type": "statusline-setup", "prompt": "x"}),
]

fails = 0
for expected, ti in CASES:
    r = subprocess.run(
        RUNNER, input=json.dumps({"tool_input": ti}), capture_output=True, text=True
    )
    ok = r.returncode == expected and (expected == 0 or "routing-floor" in r.stderr)
    if not ok:
        fails += 1
    print(f"{'PASS' if ok else 'FAIL'} exp={expected} got={r.returncode} :: {ti}")

EXTRAS = [
    ("malformed JSON fails open", "not json"),
    ("tool_input null fails open", json.dumps({"tool_input": None})),
    ("empty stdin fails open", ""),
]
for name, payload in EXTRAS:
    r = subprocess.run(RUNNER, input=payload, capture_output=True, text=True)
    ok = r.returncode == 0
    if not ok:
        fails += 1
    print(f"{'PASS' if ok else 'FAIL'} exp=0 got={r.returncode} :: <{name}>")

total = len(CASES) + len(EXTRAS)
print(f"\n{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
