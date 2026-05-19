# AGENTS.md — {{name}} (Heddle workspace)

This directory is a **Heddle workspace** — a parent directory holding
the [getheddle/*](https://github.com/getheddle) family repositories
and one or more consuming applications as flat siblings.

## Shared agent guidance

Cross-repo invariants, philosophy, schema source-of-truth direction,
and reusable skills/subagents live in
[`heddle-workspace/`](heddle-workspace/). The toolkit's
skills and subagents are symlinked into this workspace's `.claude/`,
so any Claude Code session started at the workspace root has access
to them.

If you are an AI agent, your first step is to invoke
`/heddle-orient`.

## Two kinds of work, two workflows

This workspace tracks two distinct kinds of work, each with its own
folder, discipline, and rhythm. **Before starting work, identify
which kind you are doing** and follow the rules for that kind.

| Kind | Examples | Folder | Rules |
|---|---|---|---|
| **Feature work** | New module, contrib, feature, cross-repo coordination, design exploration | [`roadmap/`](roadmap/) | [`roadmap/README.md`](roadmap/README.md) |
| **Maintenance work** | Repository review fixes, security audit, dep/lang upgrades, perf optimization, doc drift pass, schema audit | [`session-starters/<cycle>/`](session-starters/) | [`session-starters/README.md`](session-starters/README.md) |

**Feature work** is Chat-designed then Code-implemented. The
persistent home is a `roadmap/<track>.md` file. The bridge from
roadmap thinking to an executable session is a loose prompt file in
`session-starters/`.

**Maintenance work** is review-driven and Code-executed. The
persistent home is a **cycle subfolder** inside `session-starters/`,
with a `0-roadmap-overview.md` index plus thematic sibling sessions
lettered A through K. The source of items is always a review
artifact (repository review, security audit, dep audit, perf
profile, etc.) — never invented from imagination.

If you are not sure which kind your task is:

- "Build X" → feature work → `roadmap/`.
- "Fix the findings in review Y" → maintenance work →
  `session-starters/<cycle>/`.
- "Audit Z" → produces a review artifact that becomes the seed of a
  new maintenance cycle.
- "Upgrade lib W to vN" → maintenance work; create or extend a
  `dep-audit-<date>` cycle.

## Workspace-level vs. repo-level

| Workspace root (here) | Each sibling repo |
|---|---|
| `.claude/` with toolkit skills + subagents | `.claude/` with repo-local commands |
| Cross-cutting design docs and specs that span repos | Repo-internal docs |
| This `AGENTS.md` | Each repo's own `AGENTS.md` |
| `roadmap/` + `session-starters/` | Repo-internal CHANGELOG + issues |

For repo-specific verification commands and module layout, read the
relevant sibling's own `AGENTS.md`.

## VSCode

Open `{{name}}.code-workspace` for a multi-root view of the
siblings.

## Convention reference

`heddle-workspace/anchors/WORKSPACE.md` — the technical
reference for workspace detection, cross-repo git conventions, and
path conventions.
