# Audits — convention and type catalog

Workspace-level reference for how audits are performed and recorded.
The companion at `<workspace>/audits/README.md` documents the *layout*
of the `audits/` tree; this doc documents the *kinds* of audits and
how each one is run.

## Lifecycle

```
   ┌────────────┐    ┌──────────────────┐    ┌──────────────────────┐
   │ audit-     │───►│ audits/<repo>-   │───►│ maintenance-planner   │
   │ runner     │    │ audits/<topic>-  │    │ writes cycle subfolder│
   └────────────┘    │ audit-<date>.md  │    │ in session-starters/  │
                     └──────────────────┘    └──────────┬────────────┘
                                                        │
                                                        ▼
                                          ┌─────────────────────────┐
                                          │ maintenance-implementer │
                                          │ executes A, B, C, … one │
                                          │ session at a time       │
                                          └─────────────────────────┘
```

`audit-cycle-coordinator` is an optional orchestrator that drives the
whole loop — useful when scheduled (`schedule` / `loop` skill, or
`CronCreate`).

## Audit type catalog

Every audit declares a `type:` in its frontmatter. The runner uses the
type to pick a lens; the planner uses it to weight the resulting
session cycle. Add a new type only when an existing one is a poor fit.

| Type | What it inspects | Default scope |
|---|---|---|
| `security` | Credential handling, ACLs, secrets in tree, dep CVEs, network exposure | One repo, all files |
| `deps` | `pyproject.toml`/`uv.lock`/`.csproj`/`Package.swift` — outdated, unused, license, version skew across siblings | One repo (cross-repo for skew) |
| `schema` | `heddle/schemas/v1/*.schema.json` ↔ `heddle.core.messages` ↔ heddle-sdk vendored copies | Cross-repo by definition |
| `contrib` | A specific `heddle.contrib.*` namespace for invariant compliance (stateless workers, typed messages, council discipline) | One contrib module |
| `docs-editorial` | Style/voice consistency, terminology glossary drift, formatting, grammar, external-link validity, attributions, license/credit hygiene | One repo's `docs/` |
| `docs-technical` | Accuracy against current code, completeness (orphan features, undocumented surfaces), clarity, freshness of examples and runbooks | One repo's `docs/` |
| `docs-persona` | Reads the docs from one persona's viewpoint (Operator, Worker Author, Framework Contributor, Cluster Operator, Evaluator). Requires a `persona:` argument. | One repo's `docs/`, one persona |
| `perf` | Hot paths, query patterns, allocations; produces a profile, not just notes | Typically one process |
| `invariants` | Framework-wide check against `heddle-workspace/anchors/INVARIANTS.md` | One repo or cross-repo |
| `data` | ProfitFab/TopSpeed data shape, stale rows, schema drift on the SQL side | shoppulse / data peers |

A multi-dimensional audit (folder form) typically combines lenses —
e.g. a `contrib-events` audit folder might contain `invariants.md`,
`schema.md`, `docs-technical.md` as siblings.

### The docs audit family

`docs-*` types are deliberately split because they answer different
questions and want different reviewers. Don't collapse them.

- **`docs-editorial`** — does the writing meet our standards? Lenses:
  style guide, terminology glossary (cross-document consistency),
  inclusive language, formatting (headings, code-block languages,
  admonitions), grammar/spelling, dead external links, attribution
  and credit hygiene, license notices on third-party material.
- **`docs-technical`** — does the writing reflect reality? Lenses:
  every documented API/CLI/flag/config option still exists; every
  shipped surface is documented somewhere; examples run as written;
  diagrams match the code; runbooks and migration notes are
  current; nothing is in the past tense about future plans (or vice
  versa).
- **`docs-persona`** — *for one persona at a time*, can this audience
  find what they need, in the order they need it, without unstated
  prerequisites? Personas live in
  [`AUDIENCE_PERSONAS.md`](AUDIENCE_PERSONAS.md). The runner needs a
  `persona:` argument; the topic is typically `<repo>-persona-<persona-slug>`.

To audit docs holistically, run all three (often as a folder-form
audit `docs-audit-<date>/` with one facet per lens, plus one
`persona-<slug>.md` per audience).

## Audit document shape

Frontmatter, then narrative. The audit-runner emits this; the planner
parses it.

```markdown
---
type: <one of the catalog>
repo: <repo-name>           # e.g. heddle, heddle-sdk
topic: <kebab-case>
date: YYYY-MM-DD
auditor: <agent name or human>
status: complete | partial
---

# <Repo> — <topic> audit — YYYY-MM-DD

## Summary
1–3 sentences. The headline.

## Findings
Each finding is a numbered entry with a severity and a path:
1. **[high]** `path/to/file.py:42` — what's wrong, why it matters.
...

## Decision points
Open questions the planner cannot resolve without a human:
- ...

## Out of scope
What this audit deliberately did not look at.
```

`Decision points` is load-bearing: it's how the planner knows when to
stop and flag rather than auto-plan a fix.

## Source-of-truth direction

Cross-repo audits respect the upstream→downstream rule from
`anchors/CONTRACT_MAP.md`: an audit that finds drift between
`heddle/schemas/v1/*` and `heddle-sdk` records the upstream as
correct unless explicitly stated. The planner generates downstream
session-starters accordingly.

## Cron / loop integration

The `audit-cycle-coordinator` subagent is invocable both
interactively (`Agent({ subagent_type: "audit-cycle-coordinator" })`)
and on a schedule. It is itself stateless — the schedule lives in
`schedule` / `loop` / `CronCreate`, never in the agent.
