# heddle-agent-toolkit

Shared AI-agent guidance, skills, and subagents for the `getheddle`
repository family ([heddle](https://github.com/getheddle/heddle),
[heddle-sdk](https://github.com/getheddle/heddle-sdk),
[warp-design](https://github.com/getheddle/warp-design), and the planned
`warp`).

This repository exists so that AI coding assistants working in any
`getheddle/*` repo:

1. **Orient fast.** One canonical set of cross-repo anchors instead of
   re-reading each project's docs from scratch.
2. **Respect invariants.** Non-negotiable design rules and the framework's
   philosophy live in one place; sibling repos point here.
3. **Stay coherent across the seam.** Schema source-of-truth direction,
   subject conventions, and wire-protocol rules are documented once.

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
| `install.sh` | Symlink toolkit `skills/` and `agents/` into a target repo's `.claude/`. |

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
git clone https://github.com/getheddle/heddle-agent-toolkit
./heddle-agent-toolkit/install.sh --workspace .
```

That's it. You now have:

- A `.claude/` populated with toolkit skills + subagents.
- A starter workspace-level `AGENTS.md` (edit it to describe your project).
- A starter `my-project.code-workspace` for VSCode multi-root.

Open VSCode with `code my-project.code-workspace`; create your app dir
as another sibling (`mkdir my-app && cd my-app && uv init`) and add it
to the `.code-workspace` `folders` list. Re-run
`./heddle-agent-toolkit/install.sh --workspace .` whenever you add
siblings — it's idempotent and updates the existing files only if you
delete them first.

### Path B — Adopt Heddle in an existing project

Run from one level **above** your existing app directory:

```bash
cd /path/to/parent-of-my-app
git clone https://github.com/getheddle/heddle
git clone https://github.com/getheddle/heddle-agent-toolkit
./heddle-agent-toolkit/install.sh --workspace .
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

If a collaborator's workspace declares its repos in a
`.heddle-workspace.yaml` manifest, you can mirror their setup by
cloning each sibling listed there. (A `heddle workspace clone`
subcommand to automate this is on the roadmap; until then it's
manual.) After cloning the siblings, run the same install:

```bash
./heddle-agent-toolkit/install.sh --workspace .
```

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

Pre-release. Tracked alongside the get-heddle org repos but not yet
published. Once stable, this lives at `github.com/getheddle/heddle-agent-toolkit`.

The workspace convention is the **recommended pattern** for Heddle-
based projects. Agents and skills in this toolkit detect and operate
in workspace mode; the bootstrap experience above is intentionally
three plain `git clone` + one `install.sh` commands rather than a
single `bootstrap.sh` wrapper — fewer abstractions to learn and to
trust. A `heddle workspace` CLI, the `.heddle-workspace.yaml`
manifest schema, and a `HEDDLE_WORKSPACE` env-var convention are
designed in `anchors/WORKSPACE.md` but not yet implemented; they will
land as the convention matures.

## License

MPL 2.0 (matches `heddle`).
