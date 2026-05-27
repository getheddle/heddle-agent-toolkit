# Heddle workspace — layout, detection, and conventions

A **Heddle workspace** is an *umbrella git repository* whose working
tree holds the Heddle family repositories plus one or more consuming
applications as flat siblings. Most non-trivial work in the family —
designing, reviewing, preflighting, syncing — touches more than one
repo, so the workspace is the natural unit, not any single repo.

The umbrella repo itself is small: it tracks loose files (audit
reports, agent adapter config, the workspace manifest, the
`.code-workspace`) plus this anchor's conventions. It does **not**
track the contents of the child repos — each of those is its own git
repo on its own remote, referenced by the manifest.

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
├── AGENTS.md / CLAUDE.md          # workspace-level agent instructions
├── .claude/, .agents/, ...        # optional agent adapter dirs
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

One well-known file inside `(local-only)/` has a defined schema:
`machine.yaml`, the per-machine profile read by skills and agents that
need to know which optional tools, mounts, or capabilities exist on
this machine. See [`docs/MACHINE_PROFILE.md`](../docs/MACHINE_PROFILE.md)
for the schema and consumption rules. Everything else in
`(local-only)/` is freeform.

## The `overlays/` store

There is a third class of file beyond *tracked-by-the-umbrella* and
*untracked `(local-only)/`*: files that conceptually belong **inside a
child repo** but that the child repo doesn't want to track — drafts,
session-starter queues, in-flight notes. The umbrella's `.gitignore`
hides the child dir, and the child's own `.gitignore` ignores them, so
without help they stay machine-local and never sync.

The **overlay store** closes that gap. The umbrella reserves a
top-level `overlays/` directory that mirrors the child-repo layout:

```text
<workspace-root>/
├── overlays/
│   └── heddle/
│       ├── session-starters/                  ← whole directory
│       │   └── A-design-chat.md
│       └── notes-architecture.md
└── heddle/                                     ← gitignored from umbrella
    ├── session-starters → ../overlays/heddle/session-starters/   (symlink)
    └── notes-architecture.md → ../overlays/heddle/notes-architecture.md
```

**The overlay file is the source of truth.** The child repo's working
tree gets a symlink pointing back into `overlays/<repo>/<path>`, so the
file is tracked by the *umbrella* while still appearing at its logical
location inside the child. Editing through the child path transparently
edits the umbrella-tracked file. The child repo's
`.git/info/exclude` (a local, uncommitted ignore) hides the symlink so
the child's own `git status` stays clean. The rule is simply: *anything
under `overlays/<repo>/...` overlays onto `<repo>/...`* — the manifest
does not enumerate overlay paths; the tree is self-describing.

**Two use cases it serves:**

- **Migrating a legacy project into the workspace** while preserving its
  untracked, in-flight artifacts portably across machines. (Example:
  the `IranTransitionProject` workspace overlays `baseline/staging`
  onto `overlays/baseline/staging/`.)
- **Development-transient files** whose natural home is inside a repo
  but where repo-tracking would be wrong.

**Adding one is always explicit** — `sync` never auto-promotes:

- `workspace status` surfaces *overlay candidates*: per child repo, the
  untracked files that aren't already overlay symlinks, so you can see
  what's promotable without searching.
- `workspace overlay add <repo>/<path>` moves the file into
  `overlays/<repo>/`, replaces the original with the symlink, updates
  the child's `.git/info/exclude`, and prints the `git add` command to
  commit the overlay file in the umbrella.
- `workspace overlay rm <repo>/<path>` reverses it — moves the file
  back to a real (untracked) file in the child repo.
- On a second machine the round-trip is `git pull` (in the umbrella) →
  `workspace sync`, which walks `overlays/` and recreates every symlink
  from the now-present overlay files.

Symlinks are the only mode implemented today; they assume a
POSIX-friendly host (Windows native symlinks need Developer Mode or
elevation). Full design, edge cases, and the eventual `--copy` mode are
in [`docs/WORKSPACE_SYNC_DESIGN.md`](../docs/WORKSPACE_SYNC_DESIGN.md)
"The overlay mechanism".

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

- `AGENTS.md` (and/or `CLAUDE.md`) — short pointer: "this is workspace
  `<name>`; the siblings are X, Y, Z; the shared agent guidance lives
  in `heddle-workspace/`."
- Agent adapter files — optional discovery surfaces generated by
  `workspace agent-adapters install`, such as `.claude/`, `.agents/`,
  `.cursor/`, `.windsurf/`, `.cline/`, `.github/copilot-instructions.md`,
  `GEMINI.md`, `QWEN.md`, and `.rules`. These point back to the canonical
  toolkit material instead of copying it. See
  `heddle-workspace/docs/AGENT_ADAPTERS.md`.
- `.heddle-workspace.yaml` — the manifest above.
- `docs/`, `specs/` — cross-cutting design docs that span repos.
- Audit reports (`*_AUDIT_*.md`), `AUDIT_TODO.md` — periodic
  workspace-wide reviews. See the `/audit-followup` skill.
- `bin/workspace` — the sync CLI (symlinked from
  `heddle-workspace/bin/workspace`).
- `roadmap/` — persistent home for **feature thinking** across the
  workspace; one file per track. Scaffolded by `workspace init` with a
  `README.md` describing the track lifecycle.
- `session-starters/` — disposable bridge prompts plus
  **maintenance-cycle** subfolders (review-driven hardening, dep
  audits, security passes). Scaffolded by `workspace init` with a
  `README.md` describing the cycle pattern.

The `roadmap/` + `session-starters/` split is the formal expression of
the "feature work vs. maintenance work" distinction; the templates
shipped with `workspace init` define the discipline for each. Existing
files are never overwritten, so running init against an established
workspace is safe.

Each repo keeps its own `AGENTS.md`, optional agent adapter directories,
`docs/`, and `CHANGELOG.md`. Workspace-level contents do not replace
repo-level contents; they add a coordination layer above them.

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
| `workspace agent-adapters install` | Install thin adapters from canonical Heddle skills/instructions into coding-agent discovery paths. |
| `workspace overlay add <repo>/<path>` | Promote an untracked child-repo file/dir into the umbrella's `overlays/` store; replaces the original with a symlink. See "The `overlays/` store". |
| `workspace overlay rm <repo>/<path>` | Demote an overlay back to a real (untracked) file in the child repo. |

## Sibling conventions to know

A few repo-level conventions are easy to miss when crossing siblings;
they're recorded here so agents and skills don't re-discover them
each session.

### `heddle/` — test layout

- Tests for any `heddle.contrib.<pkg>.*` module MUST live in
  `tests/contrib/<pkg>/`. No top-level `test_contrib_*.py` files; no
  top-level `test_<contrib-module>_*.py` files. No exceptions.
- Tests for non-contrib modules currently live flat at
  `tests/test_*.py`. This is legacy. New non-contrib tests SHOULD
  prefer a sub-tree mirror (e.g., `tests/orchestrator/test_*.py`)
  when introducing one is straightforward. Existing top-level tests
  migrate opportunistically when touched, not as a batch.
- Canonical example of the contrib pattern: `tests/contrib/events/`,
  introduced in Sprint 1 of the M2 plan
  (`heddle-contrib-events-m2-architecture-v7.md`).
- File naming inside a `tests/contrib/<pkg>/` sub-tree drops the
  redundant prefix — the directory tells you the package. E.g.
  `tests/contrib/duckdb/test_query.py`, not
  `tests/contrib/duckdb/test_contrib_duckdb_query.py`.
- Shared test fixtures live in `heddle/tests/fixtures.py` (pytest
  fixture module, imported via conftest if needed). Public test
  utilities meant for downstream-app reuse live in
  `heddle/src/heddle/contrib/<pkg>/testing.py` and ARE part of the
  package's public surface.

### `heddle-sdk/` — Swift test framework

- The active Swift test runner is **Swift Testing** (`@Test`,
  `#expect`, `#require`). Requires Swift 6.2+ with Testing 6.3.1+.
- Do NOT use `XCTestCase`. On this toolchain `canImport(XCTest)` is
  false; XCTest-wrapped tests compile to empty translation units
  and never register, producing silent green CI with no tests
  executed.
- Tests that must run under both runtimes (rare) use the
  `#if canImport(XCTest) … #elseif canImport(Testing) … #endif`
  split shown in `swift/Tests/HeddleActorTests/SubjectTests.swift`.
- This applies to every Swift test addition across the workspace.

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
