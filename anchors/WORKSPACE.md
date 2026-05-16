# Heddle workspace — layout, detection, and conventions

A **Heddle workspace** is a parent directory that holds the Heddle
family repositories plus one or more consuming applications as flat
siblings. Most non-trivial work in the family — designing, reviewing,
preflighting, syncing — touches more than one repo, so the workspace
is the natural unit, not any single repo.

This anchor defines what a workspace is, how to detect one from inside
an agent or skill, and the conventions that follow once you know you
are in one.

## What's in a workspace

A typical workspace looks like:

```text
<workspace-root>/
├── .claude/                       # workspace-level toolkit install (optional)
├── .heddle-workspace.yaml         # workspace manifest (optional, see below)
├── AGENTS.md / CLAUDE.md          # workspace-level pointer (optional)
├── heddle/                        # framework, source of truth
├── heddle-sdk/                    # .NET + Swift SDKs (optional)
├── heddle-agent-toolkit/          # this toolkit
├── warp-design/                   # ADRs, vision (optional)
├── <app-1>/                       # consuming app, e.g. baft
├── <app-2>/                       # second consuming app, optional
└── <data-or-resource-repos>/      # app-specific peers, e.g. baseline
```

Not every workspace has every entry. The required pieces are
`heddle/` and `heddle-agent-toolkit/`; everything else is opt-in based
on what the workspace is for.

## Detecting workspace mode

Apply these tests, in order, when an agent or skill is invoked:

1. **Manifest present.** If `.heddle-workspace.yaml` exists at `cwd`
   or any ancestor up to the filesystem root, you are in a workspace.
   Its location is the workspace root.
2. **Marker repos present.** If `cwd` (or an ancestor) contains both
   `heddle/` and `heddle-agent-toolkit/` as immediate children, treat
   it as the workspace root.
3. **Single-repo fallback.** If neither is true, you are working in a
   single repo or in a non-workspace context. Behave as before — no
   cross-repo behavior; no sibling traversal.

The manifest is authoritative when it disagrees with the marker-repos
heuristic.

### Manifest shape (when present)

```yaml
# .heddle-workspace.yaml
name: <human-readable workspace name>
description: <one line>
heddle_repos:                    # required getheddle/* repos in this workspace
  - heddle
  - heddle-agent-toolkit
  - heddle-sdk                   # optional
apps:                            # consuming applications
  - path: <app-dir>
    requires_heddle: editable    # or "pinned"
data:                            # data/resource peers
  - <data-dir>
```

Read the manifest when it's present; fall back to scanning the workspace
root when it isn't. Never invent fields the manifest doesn't declare.

## Cross-repo git operations

The workspace root is **not** a git repository. Each sibling is its own
repo with its own history. When an agent needs the diff for a workspace,
the convention is:

```bash
# Walk every git-controlled sibling and report its diff.
for repo in <workspace>/*/; do
    [ -d "$repo/.git" ] || continue
    git -C "$repo" diff --staged   # or git diff for unstaged
done
```

The union of those diffs is the workspace changeset. Treat each repo's
diff independently for review purposes — invariants and contracts are
checked per repo, but coherence (e.g., framework change requires app
config update) is checked across them.

## Path conventions in agent output

| Mode | Convention |
|---|---|
| Single-repo (no workspace detected, or change confined to one repo) | Repo-relative paths: `src/heddle/core/messages.py` |
| Workspace (change spans siblings) | Workspace-relative paths: `heddle/src/heddle/core/messages.py`, `baft/configs/workers/foo.yaml` |

The workspace-relative form makes it unambiguous which sibling the
file belongs to and lets the user navigate from the workspace root.

## What lives at the workspace level

Workspace-level contents (as opposed to repo-level):

- `<workspace>/.claude/` — toolkit skills + subagents installed for the
  workspace, plus workspace-only commands. Sessions started at the
  workspace root pick these up.
- `<workspace>/AGENTS.md` (and/or `CLAUDE.md`) — short pointer:
  "this is workspace `<name>`; the siblings are X, Y, Z; the shared
  agent guidance lives in `heddle-agent-toolkit/`."
- `<workspace>/specs/` (or similar) — cross-cutting design docs that
  span repos. The architecture doc for a feature that touches three
  repos belongs here, not arbitrarily inside one of them.
- `<workspace>/.heddle-workspace.yaml` — the manifest above.

Each repo keeps its own `.claude/`, `AGENTS.md`, `docs/`, and
`CHANGELOG.md`. Workspace-level contents do not replace repo-level
contents; they add a coordination layer above them.

## Pointers to repo-level docs

Once you know which repo(s) the work touches, drop into the repo's own
`AGENTS.md` for repo-specific verification commands and module layout.
The workspace anchor does not duplicate repo-level content — it tells
you which repo to look in.

## When the workspace concept does not apply

- A user invoking the toolkit in a single getheddle/* repo cloned
  alone (no siblings). Detection falls back to single-repo mode.
- A consumer who installs `heddle-ai` from PyPI without checking out
  the family. They have no workspace; they have a Python dependency.
- An agent operating on remote git refs (no checkout). No workspace
  applies.

In all three cases, behave as a single-repo (or no-repo) agent. The
workspace conventions are additive — they kick in when the layout
exists, not when it doesn't.
