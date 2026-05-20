---
name: audit-cycle
description: Drive a workspace audit → maintenance-plan → implement loop. Use when the user asks to audit a repo, fix the findings from an audit, or run a periodic audit/maintenance pass. Picks the right subagent for the stage and surfaces blockers or decision points back to the user. Pairs with the four agents in `heddle-workspace/agents/`: `audit-runner`, `maintenance-planner`, `maintenance-implementer`, `audit-cycle-coordinator`.
---

# /audit-cycle — audit → plan → implement

This skill is the entry point for the workspace's audit-driven
maintenance loop. It does not perform the audit itself — it picks the
right subagent for the stage and wires their outputs to the
conventions under `audits/` and `session-starters/`.

## Before invoking

Confirm you're in a workspace (`/heddle-orient` if unsure). Audits
only run in workspace mode — they live under
`<workspace>/audits/<repo>-audits/`.

## The four stages

Map the user's request to a stage. Pick the smallest agent that does
the job; don't run the coordinator for a single audit.

| User says… | Stage | Agent |
|---|---|---|
| "Audit the `<repo>` for `<type>`." | Audit only | `audit-runner` |
| "Plan a maintenance cycle from this audit." | Plan only | `maintenance-planner` |
| "Implement letter `A` of this cycle." | Implement one | `maintenance-implementer` |
| "Run the full audit/fix loop on `<topic>`." | Full loop | `audit-cycle-coordinator` |
| Scheduled / unattended run | Full loop, no human | `audit-cycle-coordinator` via `loop` / `schedule` / `CronCreate` |

The supported `type:` keywords (`design`, `test-quality`,
`contract-extract`, `security`, `deps`, `schema`, `contrib`,
`docs-editorial`, `docs-technical`, `docs-persona`, `perf`,
`invariants`, `data`) and the audit document shape are in
[`heddle-workspace/docs/AUDITS.md`](../../docs/AUDITS.md). A `design`
audit (and `contrib`, now a `design` audit on a contrib namespace) is
checklist-driven and takes a `brief:`; see the "Design-audit discipline"
section there. The
audience-persona list (Operator, Worker Author, Framework
Contributor, Cluster Operator, Evaluator) lives in
[`heddle-workspace/docs/AUDIENCE_PERSONAS.md`](../../docs/AUDIENCE_PERSONAS.md);
a `docs-persona` audit requires a `persona:` argument from that list.

## Naming convention (mechanical link)

```
audit:  audits/<repo>-audits/<topic>-audit-<YYYY-MM-DD>(.md|/)
cycle:  session-starters/<repo>-<topic>-<YYYY-MM-DD>/
```

The maintenance cycle subfolder name matches the audit's stem minus
the `-audit-` infix. The cycle's `0-roadmap-overview.md` links back
to its source audit by relative path. Do not deviate — the planner
and implementer find each other through these names.

## When you must stop and surface

Three conditions return control to the user instead of pressing on:

1. **Audit's `Decision points` section is non-empty.** The planner
   refuses to plan items that depend on unresolved decisions. List
   them, ask the user, do not guess.
2. **A session brief hits a blocker.** The implementer writes the
   blocker into the paired `-feedback.md` and stops. Surface it.
3. **The audit reports `status: partial`** in its frontmatter. The
   runner was unable to complete its lens; re-run or expand scope
   before planning.

## Scheduling

The coordinator is stateless. To run the loop on a cadence (nightly
deps refresh, weekly invariants sweep), wrap it in:

- `/schedule` — durable cron-style scheduling.
- `/loop` — model-paced repeating.
- `CronCreate` — raw cron entry.

Do not bake the cadence into the agent body.

## What this skill is not

- Not a fixer for one-shot diffs — that's `heddle-invariant-guard` /
  `heddle-contract-reviewer`.
- Not a feature-design tool — that's `heddle-architect` + `roadmap/`.
- Not a substitute for reading the audit. Always read the audit
  before approving its planned cycle.
