# AGENTS.md — {{name}} (Heddle workspace)

This directory is a **Heddle workspace** — a parent directory holding
the [getheddle/*](https://github.com/getheddle) family repositories
and one or more consuming applications as flat siblings.

## Shared agent guidance

Cross-repo invariants, philosophy, schema source-of-truth direction,
and reusable skills/subagents live in
[`heddle-workspace/`](heddle-workspace/). The canonical skills live in
`heddle-workspace/skills/`; subagents live in
`heddle-workspace/agents/`. Agent-specific discovery paths (`.claude/`,
`.agents/`, `.cursor/`, `.windsurf/`, `.cline/`, `GEMINI.md`,
`QWEN.md`, and others) are adapters back to those canonical files.
See `heddle-workspace/docs/AGENT_ADAPTERS.md` for the full adapter map.

If you are an AI agent, your first step is to invoke
`/heddle-orient`.

Install or refresh local agent adapters with:

```bash
./heddle-workspace/bin/install-agent-adapters --workspace .
```

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
artifact (audit report) under [`audits/`](audits/) — never invented
from imagination.

The audit ↔ cycle link is **mechanical, by name** (see
[`audits/README.md`](audits/README.md)):

```
audit:  audits/<repo>-audits/<topic>-audit-<YYYY-MM-DD>(.md|/)
cycle:  session-starters/<repo>-<topic>-<YYYY-MM-DD>/
```

Per-repo audit subfolders are created lazily by `workspace init` /
`workspace add` and preserved when a repo is removed. The audit-type
catalog and audit document shape live in
[`heddle-workspace/docs/AUDITS.md`](heddle-workspace/docs/AUDITS.md).

If you are not sure which kind your task is:

- "Build X" → feature work → `roadmap/`.
- "Fix the findings in audit Y" → maintenance work →
  `session-starters/<repo>-<topic>-<date>/`.
- "Audit Z" → run the `audit-runner` subagent; the report lands in
  `audits/<repo>-audits/` and seeds a new maintenance cycle.
- "Upgrade lib W to vN" → maintenance work, seeded by a `deps` audit.

## Workspace-level vs. repo-level

| Workspace root (here) | Each sibling repo |
|---|---|
| Agent adapters pointing to toolkit skills + subagents | Repo-local agent commands and instructions |
| Cross-cutting design docs and specs that span repos | Repo-internal docs |
| This `AGENTS.md` | Each repo's own `AGENTS.md` |
| `roadmap/` + `session-starters/` + `audits/` | Repo-internal CHANGELOG + issues |

For repo-specific verification commands and module layout, read the
relevant sibling's own `AGENTS.md`.

## VSCode

Open `{{name}}.code-workspace` for a multi-root view of the
siblings.

## Convention reference

`heddle-workspace/anchors/WORKSPACE.md` — the technical
reference for workspace detection, cross-repo git conventions, and
path conventions.
