# Obsidian Vault — Second Brain

Vault: `__VAULT_PATH__` — `00 - Brain` (personal) | `01 - Projects` (one note per workspace) |
`02 - Work` | `03 - Knowledge` | `04 - Journal` (manual) | `05 - Templates`

## Who writes

- **Main sessions write; subagents never do.** Subagent reports carry VAULT TRIGGERS (usually
  empty — only decisions/lessons that would matter to another project or a future quarter); the
  main session above them writes those to the project's note. Root skips the write when the
  section is empty.
- The vault is a git repo with a PRIVATE remote (`__VAULT_REMOTE__`):
  **commit AND `git push` after every write, same session** — the remote copy is always
  current. If push fails (offline), say so and push at the next opportunity.

## Session start (read-only)

- Root session: read a project's note in `01 - Projects` on first mention of that project —
  including before answering anything about its status, state, or history.
- Real project with no note → create one from `05 - Templates/Project Note.md` (offer first if
  unsure it qualifies).

## Writing

- Project/technical content auto-documents into that project's note (`01 - Projects`) or
  `03 - Knowledge`: decisions and the WHY — features, architecture, dependencies,
  security-relevant changes, lessons. Durable summaries, not session play-by-play; update the
  existing note rather than spawning a new one. The workspace `.claude/docs/` files hold
  operational detail; the vault note holds the durable cross-project summary.
__VAULT_CAPTURE__
- NEVER delete or overwrite vault content without asking first. Unsure whether something
  belongs → ask.
- Conventions: `[[wikilinks]]`, YAML frontmatter on new notes, end every created/updated note
  with `*Last updated: YYYY-MM-DD*`.

## Before drafting emails or messages

Read `00 - Brain/About Me`, the recipient's note in `00 - Brain/Contacts/`, and the relevant
project note first.
