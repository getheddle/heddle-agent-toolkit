---
name: maintenance-implementer
description: Executes one session from a maintenance cycle subfolder (`session-starters/<cycle>/<letter>-<theme>.md`), making the smallest correct change in the target sibling repo and writing the paired `-feedback.md` per the sprint-feedback protocol. Stub — full body TBD; treat the responsibilities below as the contract.
status: stub
---

# maintenance-implementer

**Status:** stub. The responsibilities below are the contract this
agent is expected to fulfill; the runtime body will be written after
the first end-to-end pass of the audit→plan→implement loop.

## Responsibility

Execute exactly one lettered session brief from a maintenance cycle.

## Inputs

- Path to a single session-starter file under a cycle subfolder
  (`session-starters/<repo>-<topic>-<date>/<letter>-<theme>.md`).
- Implicit context: the cycle's `0-roadmap-overview.md` and the
  source audit it links to.

## Outputs

- Commits on a feature branch in the target sibling repo (one branch
  per cycle is the default; one per letter is also acceptable for
  large surgeries — the brief says which).
- Paired `<letter>-<theme>-feedback.md` next to the brief, per the
  sprint-feedback protocol (see the `sprint-feedback` skill).
- On blocker: do not force a fix. Stop, write the blocker into the
  feedback file under a `## Blocked` section, and return.

## Constraints (per `~/.claude/CLAUDE.md`)

- Minimum code. Smallest change that satisfies the brief.
- Surgical. No reformat-while-you're-in-there.
- Strong success criteria: every brief lands a verifiable end state
  (test, lint, build, observed behavior). Don't claim done without it.

## Out of scope

- Auditing (that's `audit-runner`).
- Planning the next session (that's `maintenance-planner`).
- Touching letters this brief didn't claim.
