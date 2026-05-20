---
name: maintenance-planner
description: Reads a completed audit under `audits/<repo>-audits/` and writes a maintenance cycle subfolder under `session-starters/<repo>-<topic>-<date>/` — `0-roadmap-overview.md` plus lettered thematic sibling sessions. Flags items in the audit's `Decision points` section as needing human input before they can be planned. Stub — full body TBD; treat the responsibilities below as the contract.
status: stub
---

# maintenance-planner

**Status:** stub. The responsibilities below are the contract this
agent is expected to fulfill; the runtime body will be written after
the first end-to-end pass of the audit→plan→implement loop.

## Responsibility

Convert one audit artifact into one executable maintenance cycle.

## Inputs

- Path to an audit (`audits/<repo>-audits/<topic>-audit-<date>(.md|/)`).
- Optionally: a cap on cycle size (default: one session per finding
  cluster, max ~10 letters).

## Outputs

`session-starters/<repo>-<topic>-<date>/` containing:

- `0-roadmap-overview.md` — links back to source audit by relative
  path; lists the lettered sessions and their status.
- `A-<theme>.md` … `K-<theme>.md` — one session per finding cluster.
  Each session brief is self-contained per
  `session-starters/README.md`.

If the source audit has non-empty `Decision points`, write
`0-roadmap-overview.md` with a `## Blocked on decisions` section
listing them, and **do not** generate sessions for findings that
depend on those decisions. Return early with a clear "blocked"
status so the coordinator surfaces it.

## Out of scope

- Performing audits (that's `audit-runner`).
- Implementing the sessions (that's `maintenance-implementer`).
- Inventing findings the audit did not record.
