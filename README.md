# heddle-workspace

Everything you need to assemble, run, and sync a Heddle-based project
workspace — agent tooling and workspace lifecycle in one place. The
sibling repos are [heddle](https://github.com/getheddle/heddle),
[heddle-sdk](https://github.com/getheddle/heddle-sdk),
[warp-design](https://github.com/getheddle/warp-design), and the
planned `warp`.

Two pillars:

### 1. Agent tooling

So that AI coding assistants working in any `getheddle/*` repo:

1. **Orient fast.** One canonical set of cross-repo anchors instead of
   re-reading each project's docs from scratch.
2. **Respect invariants.** Non-negotiable design rules and the framework's
   philosophy live in one place; sibling repos point here.
3. **Stay coherent across the seam.** Schema source-of-truth direction,
   subject conventions, and wire-protocol rules are documented once.

### 2. Workspace lifecycle

So that a Heddle-based project can be assembled, moved between
machines, and kept in sync across team members:

1. **Manifest-driven layout.** `workspace.yaml` declares which repos
   belong in the workspace and where their remotes live. The umbrella
   git repo (private, on the project's own org) tracks loose files,
   audit reports, agent config, and the manifest — never the contents
   of the child repos.
2. **Interactive bootstrap.** `bin/workspace init` walks you through
   creating a new workspace; `bin/workspace link` pulls an existing
   one into a fresh machine; `bin/workspace sync` reconciles missing
   children. An explicit `(local-only)/` carve-out keeps
   machine-specific content off the wire.
3. **Mergeable across machines.** Because the umbrella is a normal
   git repo, two divergent workspaces (work / home) reconcile through
   ordinary `git merge`. See `docs/WORKSPACE_SYNC_DESIGN.md` for the
   full spec.

## What's here

| Path | Contents |
|---|---|
| `AGENTS.md` | Canonical agent instructions. Read first. |
| `CLAUDE.md` | Claude-specific thin pointer to `AGENTS.md`. |
| `anchors/WORKSPACE.md` | Workspace layout, detection, cross-repo git + path conventions. |
| `anchors/ECOSYSTEM.md` | Map of `getheddle/*` repos and how they relate. |
| `anchors/PHILOSOPHY.md` | Design opinions: who Heddle is for, what trade-offs are intentional. |
| `anchors/INVARIANTS.md` | Pointer to `heddle/docs/DESIGN_INVARIANTS.md` + cross-repo invariants. |
| `anchors/CONTRACT_MAP.md` | Schema source-of-truth, sync direction, wire-protocol contract. |
| `skills/<name>/SKILL.md` | User-invokable workflows (`/heddle-orient`, etc.). |
| `agents/<name>.md` | Subagent definitions (architect, reviewers). |
| `hooks/settings.template.json` | Opt-in hooks template for Python lint + cross-repo edit warnings. See `hooks/README.md`. |
| `install.sh` | Symlink toolkit `skills/` and `agents/` into a target repo's `.claude/`; optional `--hooks` to drop the template. |

## Getting started

A Heddle-based project lives in a **workspace** — a parent directory
that holds the framework, this toolkit, and one or more consuming apps
as flat siblings. Sessions started at the workspace root get the
toolkit's skills and subagents for free; cross-repo tooling Just Works
because the siblings are reachable as `../heddle`, `../heddle-sdk`,
etc.

See `anchors/WORKSPACE.md` for the technical reference.

Three paths cover the common cases:

### Path A — Start a new Heddle-based project (greenfield)

```bash
mkdir my-project && cd my-project
git clone https://github.com/getheddle/heddle
git clone https://github.com/getheddle/heddle-workspace
./heddle-workspace/install.sh --workspace .
```

That's it. You now have:

- A `.claude/` populated with toolkit skills + subagents.
- A starter workspace-level `AGENTS.md` (edit it to describe your project).
- A starter `my-project.code-workspace` for VSCode multi-root.

Open VSCode with `code my-project.code-workspace`; create your app dir
as another sibling (`mkdir my-app && cd my-app && uv init`) and add it
to the `.code-workspace` `folders` list. Re-run
`./heddle-workspace/install.sh --workspace .` whenever you add
siblings — it's idempotent and updates the existing files only if you
delete them first.

### Path B — Adopt Heddle in an existing project

Run from one level **above** your existing app directory:

```bash
cd /path/to/parent-of-my-app
git clone https://github.com/getheddle/heddle
git clone https://github.com/getheddle/heddle-workspace
./heddle-workspace/install.sh --workspace .
```

Same three commands. The existing app becomes one of the workspace's
siblings. Update your app's `pyproject.toml` to consume heddle as an
editable sibling:

```toml
[tool.uv.sources]
heddle-ai = { path = "../heddle", editable = true }
```

Then `uv sync` from the app dir.

### Path C — Join an existing Heddle workspace

If the workspace is published as an umbrella git repo on your project's
GitHub org, joining it is one clone plus one sync:

```bash
git clone https://github.com/<your-org>/<workspace-name>
cd <workspace-name>
./bin/workspace sync          # clones every sibling listed in .heddle-workspace.yaml
```

See `docs/WORKSPACE_SYNC_DESIGN.md` for the umbrella-repo design and
the `bin/workspace` CLI reference. The same flow handles "I want to
work on this workspace from another machine" and "I'm joining a
team-mate's workspace" — the umbrella is just a git repo, so cloning
it on a second machine works the same way.

### Optional: enable hooks

The toolkit ships an opt-in hooks template (`hooks/settings.template.json`)
that adds two Claude Code hooks tuned to a Heddle workspace:

- **PostToolUse** — auto-`ruff --fix` on Python edits under `heddle/`.
- **PreToolUse** — reminder to run `/heddle-contract-sync` when editing
  schemas or vendored SDK models.

Enable when running the installer:

```bash
./heddle-workspace/install.sh --workspace --hooks .
```

The flag copies the template only if no `.claude/settings.json` exists
yet. If you already have one, see `hooks/README.md` for manual merge.

### Optional: further Claude Code tuning

After the workspace is bootstrapped, two add-ons further improve the
agent environment. Both are per-user (not per-workspace), so set them
up once.

**`claude-code-setup` plugin.** A meta-skill that analyzes the current
workspace and recommends additional automations (hooks, subagents,
skills, MCP servers) specific to what you've checked out — useful when
you add a new sibling app to the workspace.

```text
/plugin marketplace add claude-plugins-official
/plugin install claude-code-setup@claude-plugins-official
```

Invoke from a workspace-root session:

```text
/claude-code-setup:claude-automation-recommender
```

**MCP servers.** Two materially improve Heddle-family work:

| Server | Why |
|---|---|
| `github` | Cross-repo PR/issue/CI for `getheddle/*`. Pairs with `/cross-repo-pr`. |
| `context7` | Live docs for Pydantic, nats-py, structlog, DuckDB, LanceDB. |

```bash
claude mcp add github
claude mcp add context7
```

The generated workspace `AGENTS.md` (when you run with `--workspace`)
documents both of these for you and your collaborators.

### Optional: also install into individual repos

Each sibling repo can have the toolkit symlinked into its own
`.claude/` as well, so Claude sessions opened *inside* a repo (not at
the workspace root) get the same skills and subagents:

```bash
./install.sh ../heddle
./install.sh ../heddle-sdk        # if present
./install.sh ../my-app            # any consuming app
```

This is purely additive — workspace-level install handles workspace-
root sessions; per-repo install handles in-repo sessions. Most users
want both.

### VSCode notes

The generated `<workspace-name>.code-workspace` opens the workspace
root plus every sibling that's a git repo, in a multi-root view. Add or
remove `folders` entries as your workspace evolves. VSCode's
per-folder settings, recommended extensions, and shared launch configs
all work normally in this layout.

If you're using the Claude Code VSCode extension, open the
`.code-workspace` file rather than any individual sibling — that way
Claude's working directory is the workspace root, and `/heddle-orient`
detects workspace mode automatically.

## Status

Pre-release. Lives at `github.com/getheddle/heddle-workspace` (renamed
from `heddle-agent-toolkit` in May 2026 when workspace-lifecycle
tooling landed alongside the agent-tooling pillar).

The workspace convention is the **recommended pattern** for
Heddle-based projects. Agents and skills detect and operate in
workspace mode; the bootstrap experience is intentionally a small
number of plain commands rather than a single magic wrapper — fewer
abstractions to learn and to trust. The `bin/workspace` CLI, the
`.heddle-workspace.yaml` manifest schema, and the umbrella-repo
contract are documented in `anchors/WORKSPACE.md` and
`docs/WORKSPACE_SYNC_DESIGN.md`.

## License

MPL 2.0 (matches `heddle`).
