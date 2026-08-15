"""PreToolUse deny hook (settings.json matcher: Bash|PowerShell).

Mechanical backstop for the sign-off rules in ~/.claude/CLAUDE.md "Security floor":
blocks only unambiguous destructive shapes; the written rules stay the primary gate.
Single python process (no shell wrapper) — Windows process-spawn overhead makes a
forking sh script ~5x slower. Fails open (exit 0) on any parse error: a broken
backstop must never take the shell down.

Pass after sign-off: when the user has explicitly signed off naming the exact
target, re-run the same command prefixed with CLAUDE_SIGNED_OFF=1 (bash) or
$env:CLAUDE_SIGNED_OFF=1; <command> (PowerShell) — the prefix records the sign-off
in the transcript. The .env gate is the exception: it has no escape; values never
enter the transcript.

ponytail: quoted-command interiors are not scanned — `bash -c "rm -rf src/"` and
`ssh host "rm -rf /x"` pass as single tokens; upgrade to quote-content scanning the
first time a wrapped destructive command shows up in a real transcript.
"""
import json
import re
import shlex
import sys
from typing import NoReturn

READERS = {
    "cat", "type", "more", "less", "head", "tail", "gc", "get-content",
    "select-string", "sls", "grep", "egrep", "rg", "ag", "findstr",
}
SEARCHERS = {"rg", "grep", "egrep", "ag", "findstr", "select-string", "sls"}
SQL_CLIENTS = r"(psql|mysql|mariadb|sqlite3|sqlplus)"


def deny(what: str) -> NoReturn:
    sys.stderr.write(
        f"security-floor gate: {what} requires explicit user sign-off naming the exact "
        'target (global CLAUDE.md, "Security floor"). Ask the user first; if they '
        "already signed off in this conversation, re-run the identical command prefixed "
        "with CLAUDE_SIGNED_OFF=1 (bash) or $env:CLAUDE_SIGNED_OFF=1; (PowerShell). "
        "Do not rephrase the command to route around the gate.\n"
    )
    sys.exit(2)


def deny_env() -> NoReturn:
    sys.stderr.write(
        "security-floor gate: printing .env values is blocked and has NO sign-off "
        "escape — secret values stay in .env and never enter the transcript (global "
        'CLAUDE.md, "Security floor"). Work with key NAMES instead: example.env '
        "documents them, and `cut -d= -f1 .env` lists names without values.\n"
    )
    sys.exit(2)


def _tokens(text: str) -> list[str]:
    try:
        return shlex.split(text, posix=False)  # posix=False keeps backslash paths
    except ValueError:
        return text.split()


def _cmd_word(tok: str) -> str:
    t = tok.strip("\"'").lower()
    return t.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]


def main() -> None:
    try:
        cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    except Exception:
        sys.exit(0)
    if not isinstance(cmd, str) or not cmd:
        sys.exit(0)

    flat = cmd.replace("\n", " ").replace("\t", " ")

    def m(pattern: str) -> "re.Match[str] | None":
        return re.search(pattern, flat, re.I)

    # 1. Printing .env values — checked FIRST: this gate has no sign-off escape.
    #    Token-wise per pipeline segment: a reader command must appear as its own
    #    token, and .env as a bare whitespace-free operand token — quoted prose
    #    that merely MENTIONS `cat .env` (commit messages, search patterns, docs)
    #    is not a read. Heredoc bodies and post-redirect write targets don't count;
    #    example/sample/template files are exempt.
    for seg in re.split(r"[|;&]", flat):
        toks = _tokens(seg)
        for i, t in enumerate(toks):
            if t.startswith("<<"):
                toks = toks[:i]  # heredoc body is document text, not a command
                break
        reader_at = next(
            (i for i, t in enumerate(toks) if _cmd_word(t) in READERS), None
        )
        if reader_at is None:
            continue
        for t in toks[reader_at + 1 :]:
            if t[0] == ">" or t.startswith(("1>", "2>")):
                break  # what follows a redirect is a write target, not a read source
            t2 = t.strip("\"'")
            if not t2 or " " in t2:
                continue  # quoted prose, not an operand
            if re.search(r"\.env\b", t2, re.I) and not re.search(
                r"example|sample|template", t2, re.I
            ):
                deny_env()

    if "CLAUDE_SIGNED_OFF=1" in flat:
        sys.exit(0)

    # 2. Force-push (incl. --force-with-lease, bundled flags like -uf, +refspec)
    if m(r"git [^|;&]*push[^|;&]*( --force| -[a-z]*f[a-z]*( |$)| \+[a-z0-9_])"):
        deny("a force-push")

    # 3. Destructive SQL. Piping SQL text INTO a client executes it — checked on the
    #    whole command; the rest is checked per segment, and a segment whose command
    #    is a search tool is skipped (grep/rg over migrations READS SQL, not runs it).
    if m(r"\btruncate\b[^|]*\|\s*" + SQL_CLIENTS + r"\b"):
        deny("TRUNCATE (destructive DB operation)")
    for seg in re.split(r"[|;&]", flat):
        first = next(
            (_cmd_word(t) for t in _tokens(seg) if t.strip("\"'")), None
        )
        if first in SEARCHERS:
            continue
        if re.search(r"\bdrop +(table|database|schema)\b", seg, re.I):
            deny("DROP (destructive DB operation)")
        if re.search(
            r"\btruncate +table\b|\b" + SQL_CLIENTS + r"\b[^|;&]*\btruncate\b",
            seg,
            re.I,
        ):
            deny("TRUNCATE (destructive DB operation)")
        if re.search(r"\bdelete +from\b(?![^|;&]*\bwhere\b)", seg, re.I):
            deny("bulk DELETE without WHERE")

    # 4. Repo deletion
    if m(r"\bgh +repo +delete\b"):
        deny("GitHub repo deletion")

    # 5. Recursive deletion outside sanctioned scratch areas. The trigger catches rm
    #    with any recursive flag form (-r, -rf, -fr, --recursive, PowerShell -Recurse
    #    via the rm alias) but not `git rm`/`pnpm rm`; then EVERY rm/Remove-Item
    #    operand list is scanned, ending at the next separator or redirect token.
    if m(r"(?<!git )(?<!pnpm )\brm +(-\S+ +)*(-[a-z]*r|--recursive)") or m(
        r"\bremove-item\b[^|;&]*-recurse"
    ):
        safe = re.compile(
            r"(^|[/\\])tmp([/\\]|$)|scratchpad|node_modules"
            r"|AppData[/\\]Local[/\\]Temp|^\$env:TE?MP",
            re.I,
        )
        toks = _tokens(flat)
        starts = [i for i, t in enumerate(toks) if t.lower() in ("rm", "remove-item")]
        for s in starts:
            skip_value = False
            for t in toks[s + 1 :]:
                low = t.lower()
                if low[0] in ">|;&" or low.startswith(("1>", "2>")):
                    break  # separator/redirect ends this command's operand list
                if skip_value:
                    skip_value = False
                    continue
                if low in ("-erroraction", "-ea"):
                    skip_value = True  # its value token is not a path
                    continue
                t2 = t.strip("\"'")
                if not t2 or t2.startswith("-"):
                    continue
                if not safe.search(t2):
                    deny("recursive force-delete outside tmp/ (bulk file deletion)")

    sys.exit(0)


if __name__ == "__main__":
    main()
