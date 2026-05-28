# session-starters/

This folder is the **disposable bridge** between roadmap thinking and
executable work. Two kinds of files live here:

1. **Standalone session prompts** — one-off Chat-or-Code session
   handoffs that don't fit a cycle. Loose files at the folder root.
2. **Maintenance cycles** — review-driven hardening, upgrade, audit,
   and optimization work organized as a cycle of sibling sessions.
   Each cycle lives in its own subfolder.

For the brief-authoring discipline that produces these sessions — the
R1 brief, the review rounds, then implementation — see *The cycle-brief
protocol* in `chat-first-project-development.md` v0.4.

## Maintenance-cycle pattern

A maintenance cycle starts when a **review artifact** lands. A review
artifact is any document that systematically inspects part of the
workspace and produces findings. Sources of review artifacts include:

- **Repository review** — a periodic full-codebase pass (Codex
  reviews, Claude reviews, internal reviews).
- **Security audit** — focused inspection for security posture.
- **Dependency / version audit** — check lib + language versions
  against current upstream, identify upgrade work.
- **Performance / optimization audit** — profile-driven review of
  hot paths.
- **Doc drift audit** — systematic check of doc accuracy against
  current code.
- **Cross-language schema audit** — verify foreign SDKs against the
  Python source-of-truth.
- **Operator / user feedback synthesis** — when accumulated reports
  warrant a hardening pass.

The cycle's findings get sliced into a small set of **thematic
sessions** (typically 6-12, lettered A-K or A-J), with a
`0-roadmap-overview.md` index. Each session is a self-contained
prompt with explicit fix shapes, evidence (file:line), test pins,
and done-when criteria. Sessions land; cycle archives; next review
begins.

## Cycle rules

### Cycle directory layout

```
session-starters/
  <cycle-name>/                       e.g. "repo-review-2026-05-10"
    0-roadmap-overview.md             cycle index — required
    A-<theme>.md                      thematic sessions, lettered
    B-<theme>.md
    ...
    K-deferred-decisions-...md        last letter is conventionally
                                       reserved for items needing
                                       user decisions
    (archived)/                       prior cycle subfolder — see
                                       below
```

### Cycle naming

`<kind>-<source>-<YYYY-MM-DD>` where:

- `kind` is one of: `repo-review`, `security-audit`, `dep-audit`,
  `perf-audit`, `doc-drift`, `schema-audit`, `feedback-synthesis`,
  or a domain-specific kind if the above don't fit.
- `source` is optional — used when multiple reviewers or sources
  produce parallel cycles (e.g. `repo-review-codex-2026-05-08`).
- Date is when the cycle's source review artifact was produced.

### Cycle index (`0-roadmap-overview.md`) — required contents

- One-line cycle description and source reference.
- Session list table: file, theme, severity mix, scope, user-input
  needed.
- Ordering notes — dependencies between sessions.
- Severity reference — count by tier from the source review.
- Predecessor index — link prior cycle's `(archived)/` items if any.
- Coverage checklist — every finding in the source review mapped to
  a session (omissions visible as table gaps).

### Per-session file shape

Every session file in a cycle has:

- **Top line** — what it does, in one sentence.
- **"Read first"** — source review section references, code paths
  that are exemplars, prior-session links.
- **Items** (numbered, e.g. A1, A2) — each with:
  - **Evidence** (file:line + grep / git output)
  - **Impact** (operator-visible effect, not just code smell)
  - **Fix** (concrete shape; pick one option if ambiguous)
  - **Test pin** (specific test name + shape)
  - **User input** flag if a design call is needed
- **Dependencies / order** — within and across sessions.
- **Done-when** — explicit acceptance criteria.
- **Cross-session pointers** — overlap with other sessions in the
  cycle.

### Cycle lifecycle

1. **Review artifact lands.** Stored in the relevant repo's
   `docs/reviews/` or as a workspace overlay (depending on scope).
2. **Cycle folder created** under `session-starters/<cycle-name>/`.
   Index + per-session files written from the review.
3. **Sessions execute.** Each session runs as one or more Code
   sessions; results land on `main` per the repo's normal commit
   discipline.
4. **Cycle archives.** When all items are either landed or
   explicitly deferred (typically via a `K-deferred-decisions-...md`),
   the cycle moves to `(archived)/` **within its own folder** — the
   `(archived)/` subdir holds the previous cycle's letters that the
   current cycle's items consumed/superseded.
5. **Deferred decisions promote.** Items in the `K-` file that
   represent long-lived design questions (not just "needs operator
   data") promote to `roadmap/` feature tracks. The `K-` file keeps
   the historical record.

### What goes here vs. `roadmap/`

| Stays in `session-starters/<cycle>/` | Promotes to `roadmap/` |
|---|---|
| Specific bug fixes | Long-lived design questions |
| Specific tests to add | New features |
| Doc drift fixes | New modules / contribs |
| Dep upgrades | Cross-repo coordination tracks |
| Security hardening | Anything that lives multiple months |

If an item in a cycle's K-file represents work that will outlive the
cycle, promote it to a `roadmap/` track with a back-reference to its
origin.

## Standalone session prompts (not in a cycle)

Loose files at this folder root are one-off prompts that don't fit a
cycle. Examples:

- A Chat session's handoff to Code for a specific feature increment.
- A prompt to Code summarizing a multi-session design conclusion.
- Feedback files (`FEEDBACK-<topic>.md`) from completed Code sessions.

Standalone prompts get cleaned up when their work lands — they're
disposable by design. Long-lived plans go in `roadmap/`, not here.

### Standalone naming

- Active session prompts: `<topic>.md` (lowercase, hyphen-separated).
- Code session feedback: `FEEDBACK-<topic>.md`.

## Current state

### Active cycles

*No active cycles yet.*

### Loose session prompts

*None yet.*

## For agents

- If you are about to do **review-driven hardening, doc drift, dep
  upgrade, security pass, or perf optimization** work, you are in
  the maintenance-cycle workflow. Read the cycle's
  `0-roadmap-overview.md` first, then the relevant session file.
  Don't pick up half a session; the index orders them for a reason.
- If you are about to do **feature work**, the right entry point is
  `roadmap/README.md`, not here. A loose file here might still be
  your handoff, but the persistent home is the roadmap.
- If you are about to **create a new cycle**, follow the rules
  above; copy the structure of any prior cycle subfolder if one
  exists.
