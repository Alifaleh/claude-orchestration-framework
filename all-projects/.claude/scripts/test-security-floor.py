"""Regression battery for security-floor.py (lives beside the hook — the gate is
live infrastructure, its tests are not session scratch).

Each deny case asserts BOTH exit 2 and the deny CATEGORY substring on stderr, so a
case cannot pass on the wrong pattern. Expected 0 = allowed.
"""
import json
import subprocess
import sys
from pathlib import Path

SF = str(Path(__file__).with_name("security-floor.py"))
RUNNER = [sys.executable, SF]

# (expected, command): expected is 0 (allow) or the stderr category substring (deny)
CASES = [
    # force-push
    ("force-push", "git push --force"),
    ("force-push", "git push -f origin main"),
    ("force-push", "git push -uf origin main"),
    ("force-push", "git push origin +main"),
    ("force-push", "git push origin main --force-with-lease"),
    (0, "git push origin feature-x"),
    (0, 'git commit -m "add +feature" && git push origin main'),
    # destructive SQL
    ("DROP", 'mysql -e "DROP TABLE users"'),
    ("TRUNCATE", 'psql -c "TRUNCATE users;"'),
    ("TRUNCATE", 'echo "TRUNCATE TABLE t" | sqlite3 db.sqlite'),
    ("TRUNCATE", 'echo "TRUNCATE users;" | psql -d app'),
    (0, "truncate -s 0 tmp/app.log"),
    ("DELETE", 'psql -c "DELETE FROM users;"'),
    ("DELETE", 'psql -c "DELETE FROM logs; DELETE FROM users WHERE id=1"'),
    (0, 'psql -c "DELETE FROM users WHERE id=5;"'),
    # searching SQL text is reading, not running (incl. piped search — N2)
    (0, 'grep -rn "DELETE FROM" migrations/'),
    (0, 'rg "DROP TABLE" migrations/'),
    (0, 'grep -rn "DELETE FROM" migrations/ | head -20'),
    (0, "grep TRUNCATE migrations/schema.sql | head"),
    ("DROP", 'cd x && psql -c "DROP TABLE t"'),
    # repo deletion
    ("repo deletion", "gh repo delete Alifaleh/scratch --yes"),
    # recursive deletion
    ("recursive force-delete", "rm -rf src/"),
    ("recursive force-delete", "rm -rf src/ && rm -rf tmp/x"),
    ("recursive force-delete", "rm -r src/"),
    ("recursive force-delete", "rm --recursive --force src/"),
    ("recursive force-delete", r"rm -Recurse -Force C:\build"),
    ("recursive force-delete", r'find . -name "*.pyc" -exec rm -rf {} \;'),
    ("recursive force-delete", r"Remove-Item -Recurse -Force C:\build"),
    ("recursive force-delete", 'rm -rf "src'),  # unbalanced quote -> fallback tokenizer
    (0, "rm -rf tmp/gates"),
    (0, "rm -rf tmp/gates && python run.py"),
    (0, "rm -rf tmp/gates 2>/dev/null"),
    (0, "rm -rf /tmp/build"),
    (0, "rm -rf backend/tmp/build"),
    (0, "rm -rf ./project/tmp"),
    (0, "rm -rf ~/tmp/scratch"),
    (0, "rm -rf node_modules"),
    (0, "rm -rf node_modules && npm install"),
    (0, 'rm -rf "C:/Users/alifa/AppData/Local/Temp/claude/x y"'),
    (0, r"Remove-Item -Recurse -Force $env:TEMP\claude-x"),
    (0, r"Remove-Item -Path tmp\gates -Recurse -Force -ErrorAction SilentlyContinue"),
    (0, "git rm -rf --cached ."),
    (0, "pnpm rm -r left-pad"),
    # .env values (no sign-off escape)
    (".env values", "cat .env"),
    (".env values", "head -3 .env"),
    (".env values", "type .env"),
    (".env values", "Get-Content .env"),
    (".env values", "gc jawab/.env"),
    (".env values", "grep API_KEY .env"),
    (".env values", "rg SECRET backend/.env"),
    (".env values", "cat .env.example && cat .env"),
    (".env values", 'cat ".env"'),
    (".env values", "sudo cat .env"),
    (".env values", "cat .env > /tmp/leak.txt"),
    (0, "cat .env.example"),
    (0, "cat example.env"),
    (0, "cat backend/.env.sample"),
    (0, "cat config.py"),
    # mentions of .env in text are not reads (N1)
    (0, 'git commit -m "gate blocks cat .env reads"'),
    (0, 'echo "use cat .env never" >> notes.md'),
    (0, 'rg "cat .env" scripts/'),
    (0, "cat <<EOF > .env\nAPI_KEY=placeholder\nEOF"),
    (0, "cat data.txt > .env"),
    # sign-off escape (both shells) — never unlocks .env
    (0, "CLAUDE_SIGNED_OFF=1 rm -rf src/"),
    (0, r"$env:CLAUDE_SIGNED_OFF=1; Remove-Item -Recurse -Force C:\build"),
    (".env values", "CLAUDE_SIGNED_OFF=1 cat .env"),
    # benign
    (0, "echo hello"),
    (0, ""),
]


def run(payload: str) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(RUNNER, input=payload, capture_output=True, text=True)


fails = 0
for expected, cmd in CASES:
    r = run(json.dumps({"tool_input": {"command": cmd}}))
    if expected == 0:
        ok = r.returncode == 0
    else:
        ok = r.returncode == 2 and expected in r.stderr
    if not ok:
        fails += 1
    print(f"{'PASS' if ok else 'FAIL'} exp={expected!r} got={r.returncode} :: {cmd!r}")
    if not ok and r.stderr.strip():
        print(f"     stderr: {r.stderr.strip()[:160]}")

EXTRAS = [
    ("malformed JSON fails open", "not json"),
    ("tool_input null fails open", json.dumps({"tool_input": None})),
    ("empty stdin fails open", ""),
]
for name, payload in EXTRAS:
    r = run(payload)
    ok = r.returncode == 0
    if not ok:
        fails += 1
    print(f"{'PASS' if ok else 'FAIL'} exp=0 got={r.returncode} :: <{name}>")

total = len(CASES) + len(EXTRAS)
print(f"\n{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
