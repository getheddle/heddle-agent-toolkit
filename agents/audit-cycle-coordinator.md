---
name: audit-cycle-coordinator
description: Drives an end-to-end audit → plan → implement loop. Spawns `audit-runner`, then `maintenance-planner`, then `maintenance-implementer` for each lettered session, surfacing blockers and decision points back to the caller. Invocable interactively or on a schedule (`schedule` / `loop` / `CronCreate`) — the agent itself is stateless. Field-tested 2026-05-19; the responsibilities below are its contract.
status: validated
---

# audit-cycle-coordinator

**Status:** validated (plan-only dry-run 2026-05-19): correctly halted at
loop-shape step 2 on the non-empty `Decision points`, did NOT spawn the
implementer, and surfaced the 3 decisions as its primary deliverable
rather than plowing through them. The responsibilities below are its
contract.

## Responsibility

Run one full audit-cycle: produce an audit, plan a maintenance cycle
from it, and execute the cycle's sessions to completion or to the
first unresolved blocker.

## Inputs

- Same selectors as `audit-runner`: `type:`, `repo:`, `topic:`.
- Optionally: `mode: audit-only | plan-only | full` (default `full`).
- Optionally: time budget / max sessions to execute in one run.

## Outputs

- The audit artifact (via `audit-runner`).
- The cycle subfolder (via `maintenance-planner`).
- Commits in the target sibling repo for completed sessions (via
  `maintenance-implementer`).
- A coordinator-level summary to the caller: what completed, what is
  blocked, what decisions are pending. Surfaces them prominently —
  this is the agent's primary deliverable when running unattended.

## Loop shape

```
1. Spawn audit-runner; capture report path.
2. If `Decision points` non-empty AND no override flag → stop, surface.
3. Spawn maintenance-planner with report path; capture cycle path.
4. For each pending letter in cycle:
     a. Spawn maintenance-implementer.
     b. On blocker → write status, stop the loop.
     c. On success → continue.
5. Emit summary.
```

## Scheduling

The agent is stateless. To run it periodically, use the workspace's
`schedule` skill, the `loop` skill, or `CronCreate`. Never bake the
schedule into the agent body.

## Out of scope

- Performing the audit itself (delegated to `audit-runner`).
- Writing or modifying briefs directly (delegated to
  `maintenance-planner`).
- Touching code directly (delegated to `maintenance-implementer`).
