---
name: researching
description: Use when a task raises a question not answerable from what's on disk — library/API behavior, community sentiment, papers, contested claims, or a deep multi-source report — or when the user says "use our researching strategy". Routes T0-T4 by the cheapest tier that settles it, maps question types to tools, keeps research off orchestrator models, and returns claims-with-sources, never vibes.
---

# Researching strategy

Route by the CHEAPEST tier that settles the question; on doubt take the LOWER tier. Research
never runs on an orchestrator model: collection and reading go to workers (`scout`,
`researcher`); orchestrators read conclusions.

## Tiers

- **T0 — it's on disk.** The repo, `.claude/docs/`, `vendor/` reference trees, `tmp/repos/`,
  the vault. Framework/vendor internals: read the actual source BEFORE any web tier.
- **T1 — one question, one authoritative source, inline** (1–3 calls beat any dispatch):
  Context7 for any library/framework/API (`resolve-library-id` → `query-docs`); official
  docs/changelogs fetched as clean markdown (the obsidian plugin's `defuddle` skill — plain
  WebFetch summarizes lossily and 403s on academic domains); the `gh` CLI for repo facts.
- **T2 — community pulse:** recent community sentiment (Reddit/HN/X) — the `last30days` skill
  where installed, else WebSearch with the current year in the query. ONCE per topic; its
  output is LEADS — verify load-bearing leads at T1 before they enter work.
- **T3 — multi-source or contested:** ONE `researcher` brief, structured: question · preferred
  sources · claims-table output · self-refutation pass. Stronger-model adjudication (opus
  where the install has it) only when claims conflict on money/security/architecture stakes.
- **T4 — deep report:** a multi-agent deep-research run (a deep-research skill/workflow where
  installed; otherwise several parallel T3 briefs plus a synthesis pass). ONLY with the user's
  explicit approval per run, expected cost stated first. Full report → `tmp/research/`; only
  the distilled decision enters the docs.

## Tool map

- **Papers/PDFs:** WebFetch 403s on arxiv — download instead:
  `curl -L -o tmp/research/<name>.pdf https://arxiv.org/pdf/<id>` (no `.pdf` suffix on the
  id). DOI → `https://doi.org/<doi>` redirects to the publisher; paywalled →
  `https://api.unpaywall.org/v2/<DOI>?email=<user email>`. Then Read with `pages` (≤20 pages
  per request; chunk `1-20`, `21-40`, …). More than ~40 pages or multiple papers → delegate
  the reading to a `researcher` returning quoted extracts with page cites. Native Read handles
  PDFs — no converter tools needed. Heavy recurring paper work → propose an arxiv/paper-search
  MCP server (ask first; MCP schemas cost tokens every session).
- **JS-walled/interactive pages:** Playwright MCP (`browser_navigate` + `browser_snapshot`);
  screenshots → `tmp/screenshots/`.
- **Repo/code research:** `gh` CLI (search/view); clone into `tmp/repos/` and read the actual
  source.
- **Single facts:** WebSearch (current year in queries) → fetch the best hit as clean
  markdown.

## Output contract

Every T2+ result is a claims table: claim · verbatim quote · URL · pub date · source quality
(primary/secondary/blog/forum) · confidence · what-would-refute-it. Unverified = LEAD, never
fact. The full table always lives in a FILE; a researcher's final message is ≤40 lines —
distilled findings + the file path, never the table inline (leader-context hygiene).
Persistence: scratch → `tmp/research/<date>-<topic>.md`; durable → distill into
`.claude/docs/` (decision → CHANGELOG, design-shaping → ARCHITECTURE, gotcha → LESSONS) —
never a new root file.

## Sensitive-data line

Internal company systems are T0-only. Customer data, credentials, internal hostnames, and
proprietary code NEVER enter a web query.
