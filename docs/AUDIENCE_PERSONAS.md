# Audience personas

The workspace-default audience list for `docs-persona` audits. Each
persona is a viewpoint the `audit-runner` adopts when it reads a
repo's `docs/` looking for friction.

A repo may override or extend this list by adding its own
`docs/AUDIENCE_PERSONAS.md`. The audit-runner prefers the repo-local
list when present and falls back to this one.

## Why split docs by persona

A single "is this doc good?" question collapses three different
audiences who fail in different places. Splitting lets one audit
say "the operator-facing section is broken" without it being
diluted by "the contributor-facing section is fine."

## The default personas

Derived from `anchors/PHILOSOPHY.md` — solo/SMB-first, on-prem,
worker- and operator-oriented. Order is rough flow of engagement
(evaluate → operate → extend → contribute).

### `evaluator`
**Who:** Reads the docs trying to decide whether to adopt Heddle for
their use case. May skim only the README, index, and one or two
"vision" pages.

**Wins when:** in 5 minutes they can answer: what is this, what is
it for, what isn't it for, what does it cost me to try, what's the
smallest thing I can run.

**Fails when:** the docs assume they already know the project; the
"is this for me?" answer is buried; getting-started requires reading
three other pages first; the philosophy and the README disagree.

### `operator`
**Who:** Solo developer or small-business operator running Heddle on
their own machines. Installs the CLI, edits YAML, watches Workshop,
runs a workload, debugs when it breaks.

**Wins when:** install + first workflow is on one page; every error
message they actually see has a docs hit; the runbook for "it
stopped working" exists and is current.

**Fails when:** docs require a Kubernetes mindset; troubleshooting
points at "check the logs" with no log examples; the
configuration reference is incomplete or rotted.

### `worker-author`
**Who:** Writes a new heddle worker (LLM or processor) in Python,
.NET, or Swift. Knows the framework concepts but needs to know the
contract their worker must honor.

**Wins when:** they can scaffold a worker, run it locally against a
test workflow, and know exactly which I/O contract rules apply to
their tier.

**Fails when:** the worker contract is implied but not stated; the
tier semantics aren't documented; the SDK example uses a deprecated
pattern; the difference between LLM and processor workers is not
explicit.

### `framework-contributor`
**Who:** Modifies `heddle/`, `heddle-sdk/`, or the schemas
themselves. Cares about invariants, contract direction, cross-repo
seams.

**Wins when:** they know which anchors to read before changing X;
which subagents review their diff; how to run preflight; where the
schema source-of-truth lives and how to propagate a change.

**Fails when:** the invariants live in three places and disagree;
the cross-repo PR walkthrough is missing; the docs say "don't touch
this" without saying why.

### `cluster-operator`
**Who:** Runs Heddle across more than one machine — a small fleet,
a household, or modest cloud capacity. Solo/SMB scale, not platform
team.

**Wins when:** "how do I add a second machine?" is on the table of
contents; the NATS ACL and queue-group reality is documented;
failure modes between machines are spelled out.

**Fails when:** distributed concerns get hand-waved; the docs
silently assume one machine; cluster setup mixes "if you have an
ops team" caveats that don't apply.

## Adding a persona

Add a new persona only when an existing one is a poor fit for an
audience the docs are genuinely trying to serve. Each persona entry
should answer:

- **Who** — a one-sentence sketch.
- **Wins when** — the success state from this persona's viewpoint.
- **Fails when** — the failure patterns this audit lens watches for.

The `docs-persona` audit runner reads only the persona you ask for,
not all of them. If you want a multi-persona pass, run a folder-form
audit and ask for each persona as a facet.

## How `docs-persona` is invoked

```
type:    docs-persona
repo:    <repo>
topic:   <repo>-persona-<persona-slug>
persona: <one slug from above, e.g. operator>
```

The audit report's frontmatter must echo `persona:` so the planner
and the maintenance-cycle naming stay deterministic.
