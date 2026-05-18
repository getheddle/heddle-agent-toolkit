# Heddle workspace — layout, detection, and conventions

A **Heddle workspace** is an *umbrella git repository* whose working
tree holds the Heddle family repositories plus one or more consuming
applications as flat siblings. Most non-trivial work in the family —
designing, reviewing, preflighting, syncing — touches more than one
repo, so the workspace is the natural unit, not any single repo.

The umbrella repo itself is small: it tracks loose files (audit
reports, agent config, the workspace manifest, the `.code-workspace`)
plus this anchor's conventions. It does **not** track the contents of
the child repos — each of those is its own git repo on its own remote,
referenced by the manifest.

This anchor defines what a workspace is, how to detect one, the shape
of the manifest, and the conventions that follow once you know you are
in one. For the umbrella repo's full design rationale and the
`bin/workspace` CLI reference, see
[`docs/WORKSPACE_SYNC_DESIGN.md`](../docs/WORKSPACE_SYNC_DESIGN.md).

## What's in a workspace

```text
<workspace-root>/                  # umbrella git repo (private, on project org)
├── .git/                          # umbrella's own history
├── .gitignore                     # ignores child repos + (local-only) carve-out
├── .heddle-workspace.yaml         # workspace manifest (authoritative)
├── .claude/                       # workspace-level toolkit install
├── AGENTS.md / CLAUDE.md          # workspace-level pointer
├── <project>.code-workspace       # VSCode multi-root
├── bin/workspace                  # sync CLI (symlinked from heddle-workspace/)
├── docs/, specs/                  # cross-cutting design docs (optional)
│
├── (archive)/                     # tracked: shared retired content
├── (local-only)/                  # UNTRACKED: machine-local carve-out
│
├── heddle/                        # child repo (manifest entry)
├── heddle-sdk/                    # child repo (manifest entry, optional)
├── heddle-workspace/              # this toolkit (manifest entry)
├── warp-design/                   # child repo (manifest entry, optional)
├── <app-1>/                       # consuming app (manifest entry)
├── <app-2>/                       # second consuming app, optional
└── <data-or-resource-repos>/      # app-specific peers
```

Required pieces: `heddle/` and `heddle-workspace/`. Everything else
is opt-in based on what the workspace is for.

## Detecting workspace mode

Apply these tests, in order, when an agent or skill is invoked:

1. **Manifest present.** If `.heddle-workspace.yaml` exists at `cwd`
   or any ancestor up to the filesystem root, you are in a workspace.
   Its location is the workspace root.
2. **Marker repos present.** If `cwd` (or an ancestor) contains both
   `heddle/` and `heddle-workspace/` as immediate children, treat
   it as the workspace root.
3. **Single-repo fallback.** If neither is true, you are working in a
   single repo or in a non-workspace context. Behave as before — no
   cross-repo behavior; no sibling traversal.

The manifest is authoritative when it disagrees with the marker-repos
heuristic.

## Manifest shape

```yaml
# .heddle-workspace.yaml — source of truth for which child repos belong here.
workspace:
  name: <human-readable workspace name>
  description: <one line, optional>
  umbrella_remote: git@github.com:<project-org>/<workspace-name>.git

repos:
  - path: heddle
    remote: git@github.com:getheddle/heddle.git
    branch: main
  - path: heddle-workspace
    remote: git@github.com:getheddle/heddle-workspace.git
    branch: main
  - path: heddle-sdk
    remote: git@github.com:getheddle/heddle-sdk.git
    branch: main
  - path: <app-1>
    remote: git@github.com:<project-org>/<app-1>.git
    branch: main
```

Fields are intentionally minimal. The manifest answers *what should be
here* and *where to clone it from*; it does **not** pin to a SHA —
each child repo manages its own version through its own remote and
PR flow. Pinning re-creates the divergence problem that the umbrella
is meant to avoid.

Optional per-entry fields (only when needed):

- `pin: <sha-or-tag>` — pin to a specific commit. Reserve for release
  branches; using it casually defeats the design.
- `role: framework | sdk | app | data | toolkit` — hint for tooling
  that wants to group repos by category.

## The `(local-only)/` carve-out

A top-level directory named exactly `(local-only)` is **never tracked**
by the umbrella and **never referenced** by the manifest. It is for
personal scratch repos, per-machine credentials, large fixtures, and
anything that fails the "would I want a teammate to fetch this?" test.

Rules:

- Single canonical name at the workspace root only. No deep matches,
  no glob, no per-repo equivalents.
- The umbrella's `.gitignore` includes `(local-only)/`.
- The `bin/workspace` CLI refuses to touch anything under it.

The parenthesized prefix mirrors the existing `(archive)/` convention:
both sort to the top of file listings and signal "meta-category, not
a project." `(archive)` is *tracked* (shared retired content);
`(local-only)` is *untracked*. The convention is just naming —
behavior is enforced by `.gitignore` and the manifest.

## Cross-repo git operations

The umbrella tracks workspace-level files only; each sibling is its
own git repo with its own history. When an agent needs the diff for a
workspace, the convention is:

```bash
# Walk every git-controlled sibling and report its diff.
for repo in <workspace>/*/; do
    [ -d "$repo/.git" ] || continue
    git -C "$repo" diff --staged   # or git diff for unstaged
done
# Plus the umbrella itself, for loose-file changes:
git -C <workspace> diff --staged
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

Workspace-level contents (tracked by the umbrella, not by any child):

- `.claude/` — toolkit skills + subagents installed for the workspace.
  Sessions started at the workspace root pick these up.
- `AGENTS.md` (and/or `CLAUDE.md`) — short pointer: "this is workspace
  `<name>`; the siblings are X, Y, Z; the shared agent guidance lives
  in `heddle-workspace/`."
- `.heddle-workspace.yaml` — the manifest above.
- `docs/`, `specs/` — cross-cutting design docs that span repos.
- Audit reports (`*_AUDIT_*.md`), `AUDIT_TODO.md` — periodic
  workspace-wide reviews. See the `/audit-followup` skill.
- `bin/workspace` — the sync CLI (symlinked from
  `heddle-workspace/bin/workspace`).

Each repo keeps its own `.claude/`, `AGENTS.md`, `docs/`, and
`CHANGELOG.md`. Workspace-level contents do not replace repo-level
contents; they add a coordination layer above them.

## `bin/workspace` CLI — quick reference

Full reference in `docs/WORKSPACE_SYNC_DESIGN.md`. Briefly:

| Command | Purpose |
|---|---|
| `workspace init` | Bootstrap on the first machine — write manifest + `.gitignore`, commit. |
| `workspace link <umbrella-remote>` | Bootstrap on a second machine that has divergent local content — fetch + merge unrelated histories, surface conflicts. |
| `workspace sync` | Clone any missing manifest entry; fetch (never auto-pull) the rest. |
| `workspace status` | Report state of every manifest entry, plus orphan child repos and tracked-but-missing paths. |
| `workspace add <path>` | Append a manifest entry from an existing local repo. |
| `workspace rm <path>` | Remove a manifest entry (working tree untouched). |
| `workspace doctor` | Verify each manifest remote is reachable and `.gitignore` covers every entry. |

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
