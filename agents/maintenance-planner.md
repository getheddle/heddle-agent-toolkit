---
name: maintenance-planner
description: Reads a completed audit under `audits/<repo>-audits/` and writes a maintenance cycle subfolder under `session-starters/<repo>-<topic>-<date>/` — `0-roadmap-overview.md` plus lettered thematic sibling sessions. Flags items in the audit's `Decision points` section as needing human input before they can be planned. Field-tested 2026-05-19; the responsibilities below are its contract.
status: validated
---

# maintenance-planner

**Status:** validated (field-tested 2026-05-19 against the
`contrib-events-audit-2026-05-19` design audit — correctly produced 8
decision-independent sessions and surfaced 3 decision points as blocked,
withholding the gated findings). The responsibilities below are its
contract.

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
