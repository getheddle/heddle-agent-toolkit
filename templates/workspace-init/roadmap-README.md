# {{name}} — Roadmap

This folder is the persistent home for **feature thinking** in this
workspace. One file per track, with status, problem, scope,
dependencies, and current next concrete step. The folder complements
`../session-starters/` — that folder holds the disposable bridge
prompts from a roadmap track to the next executable Chat or Code
session, plus **maintenance cycles** (see below).

## Two kinds of work, two homes

| Kind | Lives in | Index | Rhythm |
|---|---|---|---|
| **Feature tracks** — new modules, features, contribs, cross-repo coordination | `roadmap/` (here) | this `README.md` | Long-lived (months) |
| **Maintenance cycles** — repo review, security audit, dep upgrades, perf optimization, doc drift | `../session-starters/<cycle>/` | each cycle's `0-roadmap-overview.md` | Cycle-bounded (typically 1-2 weeks of work) |

The two work kinds have **different shapes, different discipline,
and different decision patterns**. Feature work is Chat-designed
then Code-implemented; maintenance is review-driven and Code-only
unless an item needs a user design call. See
[`../session-starters/README.md`](../session-starters/README.md)
for the maintenance-cycle rules and current cycles.

When a maintenance cycle's `K-` file (deferred decisions) contains a
**long-lived design question** that will outlive the cycle, that
item promotes to a feature track here.

## How tracks work

- **idea** — Floated, no scope yet. Lives in the roadmap to keep it
  visible until promoted or retired.
- **proposed** — Scoped, not yet ready to execute. Awaiting
  dependency, decision, or evidence.
- **ready** — Spec'd and executable. A session-starter exists or
  can be derived directly from the track doc.
- **in flight** — Active work happening, either in a Chat session,
  a Code session, or an external real-project track. Track doc
  links to the active artifacts.
- **shipped** — Lands in a release. Track doc retained as
  historical record with link to release notes; status updated.
- **parked** — Explicitly deferred. Track doc keeps the reason and
  the gate that would re-open it.
- **retired** — No longer relevant. Track doc kept for traceability.

## Tracks by status

*No tracks yet. Add the first one and a status table below.*

<!-- Example structure for when tracks exist:

### In flight (work happening now)

| Track | Note |
|---|---|

### Ready to execute

| Track | Next step |
|---|---|

### Proposed (scoped, coordination needed)

| Track | Next step |
|---|---|

### Parked (evidence-gated)

| Track | Gate |
|---|---|

-->

## How to add a track

1. Decide the slug — lowercase, hyphen-separated, distinctive.
2. Copy an existing track's structure.
3. Fill in: status, problem, scope, non-scope, dependencies, next
   concrete step, links (session-starter if any, code if any,
   conversation references if any).
4. Add a row to the appropriate status table above.
5. Commit (or hand the file off to Code if you don't want to commit
   from Chat).

## How a track moves

- **idea → proposed** — when scope and non-scope are concrete enough
  that a session-starter could be written from the track doc.
- **proposed → ready** — when dependencies are met and someone can
  start work today.
- **ready → in flight** — when a session-starter exists in
  `../session-starters/` or a Code session is actively running.
- **in flight → shipped** — when the work lands in a release. Move
  the track doc's status, link the release notes, leave the doc.
- **anything → parked** — when work is explicitly deferred. Record
  the gate.
- **anything → retired** — when the track is no longer relevant.
  Record why.
