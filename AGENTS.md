# AGENTS.md — heddle-workspace

## Purpose

You are an AI coding agent working in one of the `getheddle/*` repositories.
This toolkit is your shared orientation surface across them. Before you
make structural changes, propose architecture, or write code that touches
the wire protocol, you must be oriented against the anchors below.

## Read first

In this order:

1. **[`anchors/WORKSPACE.md`](anchors/WORKSPACE.md)** — workspace
   detection, sibling layout, cross-repo git convention, path
   convention. Apply the detection check first; the rest of the
   anchors and your behavior depend on whether you are in workspace
   mode or single-repo mode.
2. **[`anchors/ECOSYSTEM.md`](anchors/ECOSYSTEM.md)** — how the repos
   relate, what each one owns, what is downstream.
3. **[`anchors/PHILOSOPHY.md`](anchors/PHILOSOPHY.md)** — who Heddle is for
   and which trade-offs are intentional. Drift starts here.
4. **[`anchors/INVARIANTS.md`](anchors/INVARIANTS.md)** — the
   non-negotiable rules. Points to `heddle/docs/DESIGN_INVARIANTS.md` for
   framework-internal invariants; adds the cross-repo ones.
5. **[`anchors/CONTRACT_MAP.md`](anchors/CONTRACT_MAP.md)** — where the
   schema source-of-truth lives and how changes flow across languages.

If you are in a session that crosses repository boundaries (e.g., changing
a Pydantic message in `heddle` that affects `heddle-sdk`), all five
anchors are required reading.

## How to use this toolkit

### Skills

User-invokable workflows. The full list is in
[`skills/INDEX.md`](skills/INDEX.md). Common ones:

- `/heddle-orient` — fast cross-repo summary at session start
- `/heddle-invariants` — pull invariants into context mid-session
- `/heddle-contract-sync` — verify schema sync between `heddle` and `heddle-sdk`
- `/heddle-preflight` — repo-aware pre-commit checks
- `/heddle-new-worker` — scaffold a worker config that respects contracts
- `/warp-adr` — create/format a warp-design ADR
- `/audit-cycle` — drive a workspace audit → maintenance-plan → implement
  loop. See [`docs/AUDITS.md`](docs/AUDITS.md) for the audit type
  catalog and document shape.

Skills are progressive-disclosure: invoking one loads its `SKILL.md` into
context. Don't read all skill files speculatively.

### Subagents

Spawn via the `Agent` tool when you want isolated context for a focused
job. Defined in [`agents/INDEX.md`](agents/INDEX.md):

- `heddle-architect` — read-only design consultant. Use **before** writing
  non-trivial code. Returns an implementation plan, not code.
- `heddle-invariant-guard` — reviews a diff for invariant violations
  (stateless workers, deterministic router, typed messages, contrib→core
  direction). Use before commit on structural changes.
- `heddle-contract-reviewer` — cross-repo wire-protocol coherence. Use
  when changes touch `heddle.core.messages`, `schemas/v1/*`, .NET models,
  Swift models, or subject conventions.
- `audit-runner` — performs a typed workspace audit (`security`,
  `deps`, `schema`, `contrib`, `docs-editorial`, `docs-technical`,
  `docs-persona`, `perf`, `invariants`, `data`) and writes the report
  under `audits/<repo>-audits/`. Type catalog in
  [`docs/AUDITS.md`](docs/AUDITS.md); persona catalog in
  [`docs/AUDIENCE_PERSONAS.md`](docs/AUDIENCE_PERSONAS.md).
- `maintenance-planner` — *(stub)* converts an audit into a
  `session-starters/<repo>-<topic>-<date>/` cycle.
- `maintenance-implementer` — *(stub)* executes one lettered session
  from a maintenance cycle.
- `audit-cycle-coordinator` — *(stub)* drives the audit → plan →
  implement loop end-to-end; invocable on a schedule.

### Agent adapters

The canonical source is always this repository:

- `skills/<name>/SKILL.md` for workflows. These files use
  Codex-compatible frontmatter (`name`, `description`) and can also be
  read manually by agents without native skill support.
- `agents/<name>.md` for subagent role definitions.

Agent-specific discovery surfaces are adapters. Claude Code discovers
these files through `.claude/` symlinks; Codex discovers the same skills
when they are symlinked under `$CODEX_HOME/skills/heddle/` (or
`~/.codex/skills/heddle/` if `CODEX_HOME` is unset); other agents use
their native project instruction or skill paths. The current mapping is
in `docs/AGENT_ADAPTERS.md`. Install adapters from a workspace root:

```bash
./heddle-workspace/bin/install-agent-adapters --workspace .
```

Do not copy skill or subagent text into adapter directories. If an agent
does not support discovery, start from this `AGENTS.md`, invoke
`/heddle-orient` by opening `skills/heddle-orient/SKILL.md`, then follow
the pointers in `skills/INDEX.md` and `agents/INDEX.md`.

## Non-negotiable rules across the family

These hold regardless of which repo you are working in:

- **Heddle (Python) is the source of truth.** Wire-protocol schemas,
  Pydantic message models, subject conventions, and queue-group names
  originate in `heddle/` and propagate outward. Do not invent a second
  protocol downstream.
- **Workers are stateless** in every language. SDK worker bases and
  foreign processor workers reset between tasks.
- **Schema changes flow heddle → heddle-sdk → consumers.** Never modify
  `heddle-sdk/schemas/v1/*` directly; run `tools/sync_schemas.py` from
  upstream.
- **Solo / small-business orientation is a constraint, not a tagline.**
  When a feature lands, it must be operable by one person on one or a
  few machines. If the proposed change implicitly assumes a platform team
  or a Kubernetes operator, push back.
- **Privacy by default.** The local tier exists so that private workloads
  never leave the user's machines. Don't add features that quietly route
  private data to remote providers.

## When this toolkit conflicts with a repo file

If a repo's `AGENTS.md` or `CLAUDE.md` appears to conflict with this
toolkit:

1. For **cross-repo invariants** (wire protocol, schema direction,
   philosophy): the toolkit wins. Fix the repo file.
2. For **repo-specific verification commands, layout, repo-local rules**:
   the repo file wins. Add a note here only if it is genuinely shared.

## What goes here vs. in a sibling repo

| Lives in toolkit | Lives in sibling repo |
|---|---|
| Cross-repo invariants and philosophy | Framework-internal invariants (heddle/docs/DESIGN_INVARIANTS.md) |
| Wire-protocol contract map | Repository layout and module map |
| Skills and subagents used across repos | Repo-local verification commands |
| Pointers to canonical docs | The canonical docs themselves |

Avoid duplication. When you would write the same paragraph in two repos,
move it into a toolkit anchor and replace the duplicates with pointers.

## CHANGELOG discipline (cross-cutting)

Each `getheddle/*` repo that produces released artifacts maintains a
`CHANGELOG.md` at its root in
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format:

| Repo | CHANGELOG | Notes |
|---|---|---|
| `heddle` | yes — root `CHANGELOG.md` | Backfilled from v0.9.2 release notes. |
| `heddle-sdk` | yes — root `CHANGELOG.md` | `[Unreleased]` only until first tag. |
| `heddle-workspace` | yes — root `CHANGELOG.md` | Skill/anchor changes are behaviour for agent consumers. |
| `warp-design` | **no** — uses `EVOLUTION_LOG.md` instead | Design-only repo; no behaviour to changelog. ADRs serve as the durable decision log. |
| `getheddle.github.io` | no | Single-page landing site. |

Adding, changing, deprecating, removing, or fixing user-facing
behaviour requires an entry under `[Unreleased]` in the relevant
repo's `CHANGELOG.md`. Documentation-only, refactor-without-behavioural-
delta, and CI-only commits are exempt. Each affected repo's
`AGENTS.md` review checklist includes this rule.

The toolkit's `/heddle-preflight` skill checks for an `Unreleased`
section with at least one categorized entry when commits touch
behaviour-bearing paths.
