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
| `design` | Architecture & implementation vs a normative brief's stated intent: structural drift, MUST/MUST-NOT/DEFERS compliance, layering. Checklist-driven (see "Design-audit discipline"). | One module/package + its brief |
| `test-quality` | A test suite's effectiveness: functional vs adversarial balance, tests that pin wrong behavior, assertions on private state, missing failure-mode coverage | One module's tests |
| `contract-extract` | Turns a normative brief into a reusable contract checklist: every MUST/MUST-NOT/DEFERS as a `(key, statement, §ref, predicate, severity)` row. Output feeds `design` audits. | One brief |
| `security` | Credential handling, ACLs, secrets in tree, dep CVEs, network exposure | One repo, all files |
| `deps` | `pyproject.toml`/`uv.lock`/`.csproj`/`Package.swift` — outdated, unused, license, version skew across siblings | One repo (cross-repo for skew) |
| `schema` | `heddle/schemas/v1/*.schema.json` ↔ `heddle.core.messages` ↔ heddle-sdk vendored copies | Cross-repo by definition |
| `contrib` | A `design` audit scoped to one `heddle.contrib.*` namespace (was a standalone type; now a `design` audit with a contrib target) | One contrib module |
| `docs-editorial` | Style/voice consistency, terminology glossary drift, formatting, grammar, external-link validity, attributions, license/credit hygiene | One repo's `docs/` |
| `docs-technical` | Accuracy against current code, completeness (orphan features, undocumented surfaces), clarity, freshness of examples and runbooks | One repo's `docs/` |
| `docs-persona` | Reads the docs from one persona's viewpoint (Operator, Worker Author, Framework Contributor, Cluster Operator, Evaluator). Requires a `persona:` argument. | One repo's `docs/`, one persona |
| `perf` | Hot paths, query patterns, allocations; produces a profile, not just notes | Typically one process |
| `invariants` | Framework-wide check against `heddle-workspace/anchors/INVARIANTS.md` | One repo or cross-repo |
| `data` | A consuming app's data/persistence layer: row-shape, stale/orphan rows, schema drift between code and the database | one app's data layer / external data source |
| `friction` | The workspace's own artifact set — anchors, roadmap tracks, glossary entries, operational templates, adopted tool bindings — asking of each: *what friction does this still solve?* Items that no longer pay their way get deprecated; shifted ones get re-scoped. The retrospective form of the *Anti-bureaucracy guardrail* (see `chat-first-project-development.md` v0.4, *Anti-bureaucracy guardrail → the retrospective form*). | The workspace artifact set, **not a code repo** (unlike every other type). `runtime: audit-mcp (pending)` — cataloged but not yet runnable through the four-agent pipeline; the runnable form is queued for the audit-mcp track. |

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

## Design-audit discipline (reproducibility)

`design` audits are the least reproducible kind: an open-ended "audit
this against the brief" pass converges with itself only ~30-50% of the
time (measured 2026-05-19 — see
`<workspace>/audits/heddle-audits/_contracts/` and the audit-repro
harness). Two levers move that number, and `design` audits MUST use both:

1. **Checklist-driven.** Extract the brief's normative contract once (a
   `contract-extract` audit, output under
   `audits/<repo>-audits/_contracts/<topic>-<brief>-contract.md`), then
   make every `design` audit report **pass / fail / uncertain** for each
   contract `key`. This raises contract-verification agreement to ~97%
   and is the only thing that reliably catches MUST-violations (a single
   open-ended pass missed them ~50% of the time). Findings MUST be tagged
   with the contract `key` — that shared vocabulary is what makes audits
   comparable.
2. **Open sweep, treated as enrichment.** Keep one open-ended "anything
   else not in the checklist?" pass — it catches novel correctness bugs a
   contract can't enumerate. But it is **not reproducible** (~0 agreement
   on slugs across runs), so treat it as best-effort: run it multi-pass
   and merge, and **promote any open finding that recurs across runs into
   the contract checklist**, where it becomes reproducible.

`contract-extract` is a prerequisite of a rigorous `design` audit, not a
nicety. The checklist is a living artifact: it grows as recurring open
findings graduate into it.

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

## Contract checklist  (design audits only)
One row per contract `key` from the `_contracts/` checklist:
`key` — pass | fail | uncertain — `file:line` — note. A `fail` becomes a
tagged finding below; an `uncertain` is honest non-determination, not a
guess.

## Coverage ledger
A `file × concern` matrix recording what was examined. Every source file
in scope is a row; the concerns examined are columns; cells are
✓ (examined) / – (n/a) / ∅ (NOT examined — a gap). Empty/∅ cells are
flagged so omissions are visible rather than silent. This is what stops
an audit from quietly skipping a file.

## Findings
Each finding is a numbered entry with a severity, a path, and (for design
audits) the contract `key` it maps to (or `open` if from the open sweep):
1. **[high]** `path/to/file.py:42` — what's wrong, why it matters. `(key)`
...

## Decision points
Open questions the planner cannot resolve without a human:
- ...

## Out of scope
What this audit deliberately did not look at.
```

For machine scoring, a design audit also emits the findings as a fenced
`findings` JSON block (see `AUDIT_REPRO.md`): records of
`{concern_key, file, line, severity, stance, summary}`, `concern_key`
being the contract `key` (or an open-sweep slug).

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
