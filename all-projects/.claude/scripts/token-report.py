#!/usr/bin/env python3
"""token-report.py - read-only token accounting over Claude Code transcript JSONLs.

Scans ``~/.claude/projects/<slug>/**/*.jsonl`` for transcript files modified
within the last N days (recursing into each session's ``subagents/`` folder,
since those are separate JSONL files that carry real token spend of their
own), streams every matched file line by line, and sums per-message token
usage grouped by (project slug, session file, model).

This script is READ-ONLY: it never writes, moves, or deletes anything under
~/.claude/projects.

Usage:
    python token-report.py [--days N] [--project SLUG_SUBSTRING] [--subagents-only]

    --days N               Only include files modified in the last N days
                            (default 7).
    --project SUBSTRING    Only include project slugs containing this
                            substring (case-insensitive).
    --subagents-only       Only include subagent transcripts (basename
                            starting with "agent-"). AVG_CTX column =
                            cache_read // msgs per row.

Output:
    An ASCII-aligned table of (project, session file, model) -> token
    totals, sorted by total tokens descending, followed by grand totals per
    model and one approx-weighted grand total line, where
    weight = input + output + 0.1*cache_read + 1.25*cache_write.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_DAYS = 7
SECONDS_PER_DAY = 86400

# approx-weighted formula: mirrors Anthropic's rough cache-token cost
# multipliers (a cache read costs about a tenth of a fresh input token,
# a cache write costs about 1.25x a fresh input token). This is a coarse
# cost proxy, not a billing figure.
CACHE_READ_WEIGHT = 0.1
CACHE_WRITE_WEIGHT = 1.25

GroupKey = tuple[str, str, str]  # (project slug, session file, model)


@dataclass
class UsageTotals:
    """Accumulated token usage for one (project, session file, model) group,
    or for a grand-total roll-up of several such groups."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    message_count: int = 0

    def add(self, input_tokens: int, output_tokens: int, cache_read: int, cache_write: int) -> None:
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.cache_read_tokens += cache_read
        self.cache_write_tokens += cache_write
        self.message_count += 1

    def merge(self, other: UsageTotals) -> None:
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens
        self.cache_read_tokens += other.cache_read_tokens
        self.cache_write_tokens += other.cache_write_tokens
        self.message_count += other.message_count

    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens + self.cache_read_tokens + self.cache_write_tokens

    @property
    def weighted(self) -> float:
        return (
            self.input_tokens
            + self.output_tokens
            + CACHE_READ_WEIGHT * self.cache_read_tokens
            + CACHE_WRITE_WEIGHT * self.cache_write_tokens
        )

    @property
    def avg_ctx(self) -> int:
        return self.cache_read_tokens // self.message_count if self.message_count > 0 else 0


@dataclass
class SkipStats:
    """Counts of everything that was deliberately NOT included in the totals,
    so the report never silently under-counts without saying so."""

    json_errors: int = 0
    unrecognized_usage: int = 0
    unreadable_files: int = 0

    @property
    def total_lines(self) -> int:
        return self.json_errors + self.unrecognized_usage


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only token accounting over Claude Code transcript JSONLs.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_DAYS,
        help=f"Only include files modified in the last N days (default {DEFAULT_DAYS}).",
    )
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        metavar="SLUG_SUBSTRING",
        help="Only include project slugs containing this substring (case-insensitive).",
    )
    parser.add_argument(
        "--subagents-only",
        action="store_true",
        help="Only include transcript files whose basename starts with 'agent-'.",
    )
    parser.add_argument(
        "--yesterday-summary",
        action="store_true",
        help=(
            "Print exactly one summary line for the previous local calendar "
            "day's token burn, then exit. Ignores --days/--project/"
            "--subagents-only; unlike them, this always scans every project."
        ),
    )
    args = parser.parse_args(argv)
    if args.days <= 0:
        parser.error("--days must be a positive integer")
    return args


def discover_jsonl_files(
    projects_dir: Path, days: int, project_filter: str | None, subagents_only: bool = False
) -> Iterator[tuple[str, str, Path]]:
    """Yield (project_slug, session_file, absolute_path) for every transcript
    JSONL modified within the last `days` days, under project slugs whose
    directory name matches `project_filter` (case-insensitive substring, or
    all projects when `project_filter` is None).

    Recurses under each project slug directory so that subagent transcripts
    (``<session-uuid>/subagents/agent-*.jsonl``) are included as their own
    session files, alongside top-level ``<session-uuid>.jsonl`` files.

    When `subagents_only` is True, only includes files whose basename starts
    with 'agent-'.
    """
    if not projects_dir.is_dir():
        return

    cutoff = time.time() - days * SECONDS_PER_DAY
    needle = project_filter.lower() if project_filter else None

    for project_dir in sorted(projects_dir.iterdir()):
        if not project_dir.is_dir():
            continue
        slug = project_dir.name
        if needle is not None and needle not in slug.lower():
            continue

        for jsonl_path in project_dir.rglob("*.jsonl"):
            try:
                mtime = jsonl_path.stat().st_mtime
            except OSError:
                continue
            if mtime < cutoff:
                continue
            if subagents_only and not jsonl_path.name.startswith("agent-"):
                continue
            session_file = jsonl_path.relative_to(project_dir).as_posix()
            yield slug, session_file, jsonl_path


def extract_usage_and_model(obj: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    """Defensively locate a usage payload on one parsed transcript line.

    The layout observed in this install nests usage under message.usage,
    with message.model alongside it (assistant-type lines). Some other event
    types could in principle carry usage/model as top-level siblings instead
    (top-level layout), so that is checked as a fallback. Returns
    (usage_dict, model_str_or_None), or (None, None) when the line carries no
    usage payload at all (true for most lines: queue-operations, attachment
    hook events, user/system lines, etc. - not a malformed line, just an
    irrelevant one).
    """
    message = obj.get("message")
    if isinstance(message, dict):
        usage = message.get("usage")
        if isinstance(usage, dict):
            model = message.get("model") or obj.get("model")
            return usage, model

    usage = obj.get("usage")
    if isinstance(usage, dict):
        return usage, obj.get("model")

    return None, None


def iter_usage_records(path: Path, skips: SkipStats) -> Iterator[tuple[str, int, int, int, int]]:
    """Stream one transcript file line by line, yielding
    (model, input_tokens, output_tokens, cache_read_tokens, cache_write_tokens)
    for every usage-bearing line. Never loads the whole file into memory:
    the file is iterated one line at a time.

    Malformed JSON and usage payloads with an unrecognized shape are counted
    in `skips` and skipped individually - never swallowed by a broad except.
    """
    try:
        fh = path.open("r", encoding="utf-8", errors="replace")
    except OSError:
        skips.unreadable_files += 1
        return

    with fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                skips.json_errors += 1
                continue

            if not isinstance(obj, dict):
                skips.json_errors += 1
                continue

            usage, model = extract_usage_and_model(obj)
            if usage is None:
                continue

            try:
                input_tokens = int(usage.get("input_tokens") or 0)
                output_tokens = int(usage.get("output_tokens") or 0)
                cache_read = int(usage.get("cache_read_input_tokens") or 0)
                cache_write = int(usage.get("cache_creation_input_tokens") or 0)
            except (TypeError, ValueError):
                skips.unrecognized_usage += 1
                continue

            yield (str(model) if model else "unknown", input_tokens, output_tokens, cache_read, cache_write)


def to_ascii(text: str) -> str:
    """Force a display string to plain ASCII so console output stays safe
    regardless of the active codepage / PYTHONIOENCODING setting."""
    return text.encode("ascii", errors="replace").decode("ascii")


def elide(text: str, width: int) -> str:
    """Shorten `text` to at most `width` characters for table display,
    keeping the tail (the most distinguishing part of a project slug or a
    nested subagent session path) and prefixing '...' when truncated."""
    if len(text) <= width:
        return text
    if width <= 3:
        return text[:width]
    return "..." + text[-(width - 3):]


def format_int(n: int) -> str:
    return f"{n:,}"


# Text column widths (ASCII-only, fixed-width, space-separated). Text is
# elided with a leading '...' when it overflows - a display nicety that
# never changes the underlying counts.
COL_PROJECT = 30
COL_SESSION = 36
COL_MODEL = 26

NUM_LABELS = ("INPUT", "OUTPUT", "CACHE_READ", "CACHE_WRITE", "TOTAL")
MSGS_LABEL = "MSGS"


def compute_num_width(all_totals: list[UsageTotals]) -> int:
    """Widest formatted (comma-grouped) numeric value across every totals
    object about to be printed, so a numeric column is NEVER truncated or
    misaligned - unlike text columns, truncating a count would misrepresent
    the data, so numeric columns size to fit instead of eliding."""
    widest = max(len(label) for label in NUM_LABELS)
    for t in all_totals:
        for value in (t.input_tokens, t.output_tokens, t.cache_read_tokens, t.cache_write_tokens, t.total):
            widest = max(widest, len(format_int(value)))
    return widest


def compute_msgs_width(all_totals: list[UsageTotals]) -> int:
    widest = len(MSGS_LABEL)
    for t in all_totals:
        widest = max(widest, len(format_int(t.message_count)))
    return widest


def compute_avg_ctx_width(all_totals: list[UsageTotals]) -> int:
    widest = len("AVG_CTX")
    for t in all_totals:
        widest = max(widest, len(format_int(t.avg_ctx)))
    return widest


def build_header_row(num_width: int, msgs_width: int, avg_ctx_width: int) -> str:
    return (
        f"{'PROJECT':<{COL_PROJECT}} {'SESSION FILE':<{COL_SESSION}} {'MODEL':<{COL_MODEL}} "
        f"{'INPUT':>{num_width}} {'OUTPUT':>{num_width}} {'CACHE_READ':>{num_width}} {'CACHE_WRITE':>{num_width}} "
        f"{'MSGS':>{msgs_width}} {'AVG_CTX':>{avg_ctx_width}} {'TOTAL':>{num_width}}"
    )


def build_model_header_row(num_width: int, msgs_width: int, avg_ctx_width: int) -> str:
    return (
        f"{'MODEL':<{COL_MODEL}} {'INPUT':>{num_width}} {'OUTPUT':>{num_width}} {'CACHE_READ':>{num_width}} "
        f"{'CACHE_WRITE':>{num_width}} {'MSGS':>{msgs_width}} {'AVG_CTX':>{avg_ctx_width}} {'TOTAL':>{num_width}}"
    )


def format_row(
    project: str, session_file: str, model: str, totals: UsageTotals, num_width: int, msgs_width: int, avg_ctx_width: int
) -> str:
    return (
        f"{to_ascii(elide(project, COL_PROJECT)):<{COL_PROJECT}} "
        f"{to_ascii(elide(session_file, COL_SESSION)):<{COL_SESSION}} "
        f"{to_ascii(elide(model, COL_MODEL)):<{COL_MODEL}} "
        f"{format_int(totals.input_tokens):>{num_width}} "
        f"{format_int(totals.output_tokens):>{num_width}} "
        f"{format_int(totals.cache_read_tokens):>{num_width}} "
        f"{format_int(totals.cache_write_tokens):>{num_width}} "
        f"{format_int(totals.message_count):>{msgs_width}} "
        f"{format_int(totals.avg_ctx):>{avg_ctx_width}} "
        f"{format_int(totals.total):>{num_width}}"
    )


def format_model_row(model: str, totals: UsageTotals, num_width: int, msgs_width: int, avg_ctx_width: int) -> str:
    return (
        f"{to_ascii(elide(model, COL_MODEL)):<{COL_MODEL}} "
        f"{format_int(totals.input_tokens):>{num_width}} "
        f"{format_int(totals.output_tokens):>{num_width}} "
        f"{format_int(totals.cache_read_tokens):>{num_width}} "
        f"{format_int(totals.cache_write_tokens):>{num_width}} "
        f"{format_int(totals.message_count):>{msgs_width}} "
        f"{format_int(totals.avg_ctx):>{avg_ctx_width}} "
        f"{format_int(totals.total):>{num_width}}"
    )


def compute_yesterday_window(now: float | None = None) -> tuple[float, float, str]:
    """Return (start_epoch, end_epoch, date_label) bounding the previous
    LOCAL calendar day as a half-open [start, end) window, plus that day's
    label as YYYY-MM-DD."""
    now = time.time() if now is None else now
    t = time.localtime(now)
    today_start = time.mktime((t.tm_year, t.tm_mon, t.tm_mday, 0, 0, 0, 0, 0, -1))
    yesterday_start = today_start - SECONDS_PER_DAY
    yesterday_label = time.strftime("%Y-%m-%d", time.localtime(yesterday_start))
    return yesterday_start, today_start, yesterday_label


def yesterday_summary() -> int:
    """--yesterday-summary: print exactly ONE line summarizing yesterday's
    (local calendar day) token burn, computed from the same per-project
    totals the windowed report sums from - just grouped by project slug
    alone. Fetches the superset via discover_jsonl_files(days=2), which
    always fully covers yesterday regardless of what time "now" is, then
    narrows to the exact calendar-day mtime window in memory. Runtime is
    therefore bounded by a --days 2 run, never worse.
    """
    projects_dir = Path.home() / ".claude" / "projects"
    start_epoch, end_epoch, date_label = compute_yesterday_window()

    per_project: dict[str, UsageTotals] = defaultdict(UsageTotals)
    if projects_dir.is_dir():
        skips = SkipStats()  # discarded - this mode reports one line, no skip detail
        for slug, _session_file, path in discover_jsonl_files(projects_dir, 2, None):
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            if not (start_epoch <= mtime < end_epoch):
                continue
            for model, inp, out, cread, cwrite in iter_usage_records(path, skips):
                per_project[slug].add(inp, out, cread, cwrite)

    grand = UsageTotals()
    for totals in per_project.values():
        grand.merge(totals)

    if grand.total == 0:
        print(f"burn {date_label}: 0 tokens (top: none 0%)")
        return 0

    top_slug, top_totals = max(per_project.items(), key=lambda kv: kv[1].total)
    top_pct = round(100 * top_totals.total / grand.total)
    print(f"burn {date_label}: {format_int(grand.total)} tokens (top: {top_slug} {top_pct}%)")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.yesterday_summary:
        return yesterday_summary()

    projects_dir = Path.home() / ".claude" / "projects"

    filter_desc = args.project if args.project else "(none)"
    scope_desc = "subagent files only" if args.subagents_only else "all files"
    print(f"Token report - source: {projects_dir}")
    print(
        f"Window: last {args.days} day(s)   Project filter: {filter_desc}"
        f"   Scope: {scope_desc}"
    )

    if not projects_dir.is_dir():
        print("Projects directory not found - nothing to report.")
        return 0

    skips = SkipStats()
    groups: dict[GroupKey, UsageTotals] = defaultdict(UsageTotals)
    files_processed = 0

    for slug, session_file, path in discover_jsonl_files(projects_dir, args.days, args.project, args.subagents_only):
        files_processed += 1
        for model, inp, out, cread, cwrite in iter_usage_records(path, skips):
            groups[(slug, session_file, model)].add(inp, out, cread, cwrite)

    print(f"Files scanned in window: {files_processed}")
    print("")

    if not groups:
        print("No usage-bearing transcript lines found for this window/filter.")
        print(
            f"Skipped lines: {skips.total_lines} "
            f"(json_errors={skips.json_errors}, unrecognized_usage={skips.unrecognized_usage})"
        )
        if skips.unreadable_files:
            print(f"Unreadable files (open/permission errors): {skips.unreadable_files}")
        return 0

    # Main table: one row per (project, session file, model), sorted by total desc.
    rows: list[tuple[GroupKey, UsageTotals]] = sorted(
        groups.items(), key=lambda kv: (-kv[1].total, kv[0][0], kv[0][1], kv[0][2])
    )

    # Grand totals per model.
    per_model: dict[str, UsageTotals] = defaultdict(UsageTotals)
    for (_slug, _session_file, model), totals in groups.items():
        per_model[model].merge(totals)

    model_rows: list[tuple[str, UsageTotals]] = sorted(
        per_model.items(), key=lambda kv: (-kv[1].total, kv[0])
    )

    grand = UsageTotals()
    for _model, totals in model_rows:
        grand.merge(totals)

    # Numeric columns are sized from the real data (main rows + per-model
    # grand totals + the overall grand total) so cumulative totals in the
    # billions still line up instead of overflowing a hardcoded width.
    all_totals_for_width = [t for _key, t in rows] + [t for _model, t in model_rows] + [grand]
    num_width = compute_num_width(all_totals_for_width)
    msgs_width = compute_msgs_width(all_totals_for_width)
    avg_ctx_width = compute_avg_ctx_width(all_totals_for_width)

    header_row = build_header_row(num_width, msgs_width, avg_ctx_width)
    separator = "-" * len(header_row)

    print(header_row)
    print(separator)
    for (slug, session_file, model), totals in rows:
        print(format_row(slug, session_file, model, totals, num_width, msgs_width, avg_ctx_width))

    model_header_row = build_model_header_row(num_width, msgs_width, avg_ctx_width)
    model_separator = "-" * len(model_header_row)

    print("")
    print("GRAND TOTALS BY MODEL")
    print(model_header_row)
    print(model_separator)
    for model, totals in model_rows:
        print(format_model_row(model, totals, num_width, msgs_width, avg_ctx_width))

    print(model_separator)
    print(format_model_row("ALL MODELS", grand, num_width, msgs_width, avg_ctx_width))

    print("")
    print(f"approx-weighted grand total (all models): {format_int(round(grand.weighted))}")
    print("  (approx-weighted = input + output + 0.1*cache_read + 1.25*cache_write)")

    print("")
    print(
        f"Skipped lines: {skips.total_lines} "
        f"(json_errors={skips.json_errors}, unrecognized_usage={skips.unrecognized_usage}) "
        f"-- {files_processed} file(s) scanned in window"
    )
    if skips.unreadable_files:
        print(f"Unreadable files (open/permission errors): {skips.unreadable_files}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
