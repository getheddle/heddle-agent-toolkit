# Workspace Sync — Design

Status: **Draft** · Date: 2026-05-17 · Spec for the `bin/workspace`
CLI shipped by `heddle-workspace`.

> Examples below use `IranTransitionProject` as the concrete first
> consumer. The design is generic — substitute your project's GitHub
> org and workspace name wherever you see `IranTransitionProject`.
> The `heddle-workspace` repo itself is always the source of the
> CLI; your project's umbrella repo just contains the manifest and
> tracked loose files.

## Goal

Make it easy to move this workspace between machines and to keep two
or more instances (potentially used by different team members) in sync
without divergence. Anything that does not already have an online
upstream must be tracked somewhere shared; anything explicitly marked
local stays untracked.

## Non-goals

- Re-hosting or mirroring repos that already have a public/private
  upstream (`getheddle/*`, `IranTransitionProject/*`). They keep their
  own remotes; we only record *which* repos belong in the workspace
  and at what default branch.
- Cross-repo commits, monorepo conversion, or git subtree/submodule
  embedding. Each child repo's history stays where it lives.
- Backing up machine-local working state (uncommitted edits, IDE
  caches, `.DS_Store`, virtualenvs).

## Shape of the solution

A single **umbrella git repo** rooted at the workspace directory,
hosted as a *private* repo on the `IranTransitionProject` GitHub org
(the project account, not `getheddle`). It contains three kinds of
content:

1. **Loose shared files** committed directly — audit reports,
   `AGENTS.md`, `README.md`, `*.code-workspace`, agent config under
   `.claude/`, this design doc.
2. **A manifest** (`.heddle-workspace.yaml`) — the authoritative list of child
   git repos that belong in this workspace, with their remote URLs and
   default branch.
3. **A sync tool** (`bin/workspace`) — a small script (bash or uv-run
   Python) that reads the manifest and reconciles the local layout.

Every child path that is itself a git repo is **ignored** by the
umbrella (it cannot be added with `git add` anyway, and we want the
ignore to be explicit). The manifest is what binds them.

```
IranTransitionProject/                  ← umbrella repo (private)
├── .git/                                  ← umbrella's own history
├── .gitignore                             ← ignores child repos + carve-outs
├── .heddle-workspace.yaml                         ← manifest (source of truth)
├── bin/workspace                          ← sync tool
├── WORKSPACE_SYNC_DESIGN.md               ← this doc
├── AGENTS.md, README.md, *AUDIT*.md       ← tracked loose files
├── .claude/                               ← tracked agent config
├── (archive)/                             ← tracked (parens = category, not carve-out)
├── (local-only)/                          ← UNTRACKED carve-out (see below)
│
├── heddle/                                ← child repo (manifest entry)
├── heddle-sdk/                            ← child repo (manifest entry)
├── heddle-workspace/                  ← child repo (manifest entry)
├── warp-design/                           ← child repo (manifest entry)
├── baft/  baseline/  docman/              ← child repos (manifest entries)
├── getheddle.github.io/                   ← child repo (manifest entry)
├── getheddle-dotgithub/                   ← child repo (manifest entry)
└── IranTransitionProject.github.io/       ← child repo (manifest entry)
```

## The `(local-only)` carve-out

A top-level directory named exactly `(local-only)` is **never tracked**
by the umbrella and **never referenced** by the manifest. It is for:

- Personal scratch repos and experiments that should not leave the
  machine.
- Per-machine credentials, large fixtures, downloaded models, anything
  that fails the "would I want a teammate to fetch this?" test.
- Machine-pinned branches of a workspace repo someone is mid-rebase on
  (clone a second copy under `(local-only)/` rather than risk a force
  push from another machine).

Rules:

- Single canonical name: `(local-only)/` at the workspace root only.
  No deep matches, no glob (`*local-only*`), no per-repo equivalents.
  Keep the carve-out trivial to reason about.
- The umbrella's `.gitignore` lists `(local-only)/`.
- The sync tool refuses to touch anything under it (no clone, no
  status, no warning about "untracked repo here").

### Why the parenthesized prefix?

The workspace already uses `(archive)/` for retired-but-kept content.
We extend the same visual convention: a leading `(` sorts these
directories together at the top of every file listing and signals
"meta-category, not a project." `(archive)` is *tracked* (shared
history we still want around); `(local-only)` is *untracked*. The
convention is just naming — the actual tracking behavior is enforced
by the umbrella `.gitignore` and the manifest, not by the parens.

## Manifest format (`.heddle-workspace.yaml`)

```yaml
# Workspace manifest — source of truth for which child repos belong here.
# Edit by hand or via `bin/workspace add <path>`. Commit to umbrella.

workspace:
  name: IranTransitionProject
  umbrella_remote: git@github.com:IranTransitionProject/workspace.git

repos:
  - path: heddle
    remote: git@github.com:getheddle/heddle.git
    branch: main
  - path: heddle-sdk
    remote: git@github.com:getheddle/heddle-sdk.git
    branch: main
  - path: heddle-workspace
    remote: git@github.com:getheddle/heddle-workspace.git
    branch: main
  - path: warp-design
    remote: git@github.com:getheddle/warp-design.git
    branch: main
  - path: getheddle.github.io
    remote: git@github.com:getheddle/getheddle.github.io.git
    branch: main
  - path: getheddle-dotgithub
    remote: git@github.com:getheddle/.github.git
    branch: main
  - path: baft
    remote: git@github.com:IranTransitionProject/baft.git
    branch: main
  - path: baseline
    remote: git@github.com:IranTransitionProject/baseline.git
    branch: main
  - path: docman
    remote: git@github.com:IranTransitionProject/docman.git
    branch: main
  - path: IranTransitionProject.github.io
    remote: git@github.com:IranTransitionProject/IranTransitionProject.github.io.git
    branch: main
```

Fields are intentionally minimal. We do **not** pin to a SHA — each
child repo manages its own version through its own remote and PR flow.
The manifest answers "what should be here" not "at what commit."

### Optional fields (only when needed, not by default)

- `pin: <sha-or-tag>` — pin to a specific commit. Use sparingly; this
  is a `repo`-tool style frozen manifest and reintroduces the
  divergence problem the design is meant to avoid. Reserve for
  release branches.
- `private: true` — annotation only; informs the sync tool to surface
  auth-failure messages more helpfully.

## Sync tool (`bin/workspace`)

A small CLI. Commands:

| Command | Behavior |
|---|---|
| `workspace init` | **Bootstrap on the first machine.** Scan cwd, detect every immediate-child git repo with a remote, write `.heddle-workspace.yaml`, write `.gitignore` (carve-out + per-manifest-repo entries), stage and commit. Stops short of creating the GitHub repo — operator runs `gh repo create` and `git push -u` manually. Idempotent: re-running on an already-initialized umbrella just refreshes the manifest from the current layout. |
| `workspace link <umbrella-remote>` | **Bootstrap on a second machine that already has divergent content.** Adds the remote, `git fetch`, then `git merge --allow-unrelated-histories origin/<branch>`. Does **not** auto-resolve conflicts in loose files or the manifest — surfaces them and exits. After conflicts are resolved and committed, the operator runs `workspace sync` to clone any newly-introduced manifest entries. |
| `workspace status` | For each manifest entry: present? clean? on expected branch? ahead/behind upstream? Also lists workspace-root directories that are git repos but **not** in the manifest (decision required) and any tracked-but-missing path. Read-only. |
| `workspace sync` | Clone any missing manifest entry into its `path`. For present entries, fetch only (never auto-pull, never auto-checkout). Idempotent. |
| `workspace add <path>` | Detect remote from existing `.git/config`, append manifest entry, stage `.heddle-workspace.yaml`. Refuses if `path` is under `(local-only)/` or has no remote. |
| `workspace rm <path>` | Remove manifest entry. Does not delete the working tree (operator does that explicitly). |
| `workspace doctor` | Verify each manifest remote is reachable and the umbrella's `.gitignore` covers every manifest path. |

Design notes:

- **Never auto-merges or auto-pulls a child repo.** Sync only clones
  what's missing and fetches the rest. Updating a child repo is a
  per-repo decision, not a workspace-wide one.
- **Never touches `(local-only)/`** — not even `status`.
- **Idempotent.** Running `sync` twice is a no-op.
- Implementation: prefer a single bash script for portability; switch
  to `uv run` Python if YAML parsing or richer status output becomes
  painful.

## Umbrella `.gitignore` (sketch)

```gitignore
# Carve-out: anything local-only is untracked, full stop.
/(local-only)/

# Each manifest entry is its own git repo; the umbrella never tracks
# their content. Listed explicitly so a stray `git add -A` does the
# right thing even if the directory is empty.
/heddle/
/heddle-sdk/
/heddle-workspace/
/warp-design/
/getheddle.github.io/
/getheddle-dotgithub/
/baft/
/baseline/
/docman/
/IranTransitionProject.github.io/

# Machine noise
.DS_Store
```

`workspace doctor` keeps this list in sync with `.heddle-workspace.yaml`. If
that becomes annoying we can generate the per-repo block from the
manifest on every `workspace add/rm`.

## Bootstrap: linking two already-divergent workspaces

This is the **current situation**: workspaces exist on work and home,
neither is tracked by an umbrella remote yet, and the two have drifted
(different audit edits, different child repos present, possibly the
same child repo with different uncommitted work on each side). The
flow turns one machine into the source umbrella, then merges the other
machine's contents into it.

### Pick a primary

Pick whichever machine has the more current loose-file state (audit
reports, `AGENTS.md`, `.claude/` config). It doesn't matter which has
"more" child repos — those reconcile through the manifest. Call it
**Machine A**; the other is **Machine B**.

### Phase 1 — Machine A: become the umbrella

```bash
cd IranTransitionProject

# Move anything machine-local into the carve-out *before* init, so it
# never enters umbrella history.
mkdir -p '(local-only)'
mv heddle-sdk-ci-fix '(local-only)/'   # example

bin/workspace init               # writes .heddle-workspace.yaml + .gitignore, commits

# Create the private repo and push.
gh repo create IranTransitionProject/workspace --private --source=. --remote=origin
git push -u origin main
```

After this, Machine A is the source of truth for the umbrella content.
Each child repo's content is unchanged — `workspace init` only writes
two files (manifest, gitignore) and commits them.

### Phase 2 — Machine B: link and merge

```bash
cd IranTransitionProject

# 1. Commit B's existing loose-file state so the merge has something
#    to merge *against*. Don't squash; the divergence is the whole
#    point. If B's umbrella has no commits yet, make one now.
git add -A   # or stage selectively; whichever
git commit -m "machine-b state at link time"

# 2. Move B-specific stuff into the carve-out before linking.
mkdir -p '(local-only)'
mv <anything-machine-b-only-and-not-shareable> '(local-only)/'

# 3. Link to the umbrella remote A created.
bin/workspace link git@github.com:IranTransitionProject/workspace.git
# → runs: git remote add origin <url>
# → runs: git fetch origin
# → runs: git merge --allow-unrelated-histories origin/main
# → stops here if there are conflicts. There usually are.
```

### Phase 2.5 — Resolve conflicts

Three kinds of conflict, each handled differently:

**(a) Loose-file conflicts** (e.g. both sides edited
`AUDIT_TODO.md`). Resolve in your editor as usual, `git add`, commit.

**(b) Manifest conflicts.** If both machines have a child repo at the
same `path` pointing at the **same remote**, the merge is automatic.
If both have the same `path` pointing at **different remotes**, you
have two independent histories for one logical thing — the tool
cannot decide which is canonical. Options:

  - Pick one remote as canonical, drop the other's manifest entry,
    move the loser's working tree into `(local-only)/<path>-from-<machine>/`
    for archival, re-`workspace sync` to acquire the winner.
  - Or merge the two histories at the *child-repo* level first (set
    one as a second remote on the other, fetch, merge with
    `--allow-unrelated-histories`, push), then keep one manifest entry.

**(c) Child-repo present on both, divergent uncommitted work.** The
umbrella does not see inside child repos, so this can't surface as an
umbrella merge conflict — you'll only notice when you `cd` into the
child and run `git status`. The fix is per-repo and entirely standard:
commit/stash on each side, push to the child's own remote, pull on the
other side, resolve any conflicts there.

### Phase 3 — Finish the link

```bash
git push origin main             # publish the merged umbrella
bin/workspace sync               # clone any manifest entry not yet present
bin/workspace status             # confirm clean, all entries present, no orphans
```

After Phase 3, both machines are linked. Subsequent syncs follow the
steady-state "Day-to-day" flow below.

### Loose-file divergence — practical tip

Audit reports and `AGENTS.md` are the files most likely to have
silently diverged. Before running Phase 2, it's worth diffing them by
hand (`scp` one side to the other, or `git diff` after the link
fetch). Catching a substantive content drift before the merge lets
you resolve it as content rather than as a merge conflict, which is
usually less error-prone.

## Multi-machine / multi-person workflow

### New machine onboarding
1. `git clone git@github.com:IranTransitionProject/workspace.git IranTransitionProject`
2. `cd IranTransitionProject && bin/workspace sync`
3. Open `IranTransitionProject.code-workspace` in VS Code.

### Day-to-day
- Work in child repos normally. Each has its own remote and PR flow.
- Edit audit files, ADR-adjacent docs, or `.claude/` config? Commit
  to the umbrella.
- Added a new child repo? `bin/workspace add <path>`, commit the
  manifest, push the umbrella.

### Merging two workspaces
The umbrella is just a git repo, so divergence in **loose files** and
**the manifest** resolves with normal `git merge`/`git rebase`. The
contents of child repos are not in the merge — they each have their
own history on their own remote, so two machines can never diverge on
child-repo *content* through the umbrella. The worst case is a
manifest conflict (both machines added the same `path` pointing at
different remotes), which surfaces as a normal YAML conflict.

### "But I have a local-only repo I want to share now"
Promote it: create a private repo on `IranTransitionProject`, push the
local history to it, move the directory out of `(local-only)/`, then
`bin/workspace add <path>`. The carve-out is a parking lot, not a
prison.

## What this design deliberately does **not** do

- **No submodules.** Submodules pin SHAs, require extra commands for
  every operation, and create surprising detached-HEAD states. The
  manifest replaces them with something both humans and the sync tool
  can read.
- **No subtree/monorepo merge.** Child histories stay where they live.
- **No mirror-to-private of getheddle/\*.** Those have their own
  upstream; mirroring would just create a second source of truth.
- **No SHA-pinning by default.** Pinning re-creates the divergence
  problem (machine A advances heddle, machine B doesn't, the manifest
  must merge). The default contract is "this repo belongs here on
  this branch"; advancing is a child-repo concern.

## Open questions to resolve before implementation

1. **Umbrella repo name.** `IranTransitionProject/workspace`?
   `IranTransitionProject/IranTransitionProject`? Personal preference,
   but the clone command should produce a directory named
   `IranTransitionProject` either way.
2. **Sync tool language.** Bash (portable, no deps, weak YAML) or
   `uv run` Python (rich, but requires `uv`)? Recommendation: start
   bash, switch when it hurts.
3. **`heddle-sdk-ci-fix/` and `(archive)/`** — these are currently
   non-repo directories at root. Track in umbrella as-is, or move
   `heddle-sdk-ci-fix/` under `(local-only)/`? Recommendation:
   `(archive)/` stays tracked; `heddle-sdk-ci-fix/` moves to
   `(local-only)/` unless someone needs it shared.
4. **Audit reports** — keep at workspace root (current state) or move
   under `audits/`? Recommendation: leave them; `/audit-followup`
   already expects them at root.
5. **GitHub auth for `workspace sync`** — assume SSH keys are set up
   per developer; the tool just shells out to `git`. No token handling.
6. **Which machine is primary for the initial bootstrap?** Affects only
   the first push; either is recoverable. Recommend the machine whose
   loose-file state (audits, `AGENTS.md`, `.claude/`) is most current.
