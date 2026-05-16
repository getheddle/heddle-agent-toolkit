---
name: heddle-orient
description: Use at session start (or after compaction) when working in a getheddle/* repository (heddle, heddle-sdk, warp-design, warp). Loads a one-screen cross-repo orientation — repo map, owner of each concern, schema source-of-truth direction, where to read further — without re-reading the full architecture docs. Especially useful when a session touches more than one of these repos.
---

# /heddle-orient — fast cross-repo orientation

Use this skill when you start (or resume) a session that touches any
`getheddle/*` repo. It is meant to replace re-reading the full anchor
docs every time. If something here is unclear, *then* read the linked
anchor.

## First: detect workspace vs. single-repo

Apply the detection check from
`heddle-agent-toolkit/anchors/WORKSPACE.md`:

- `.heddle-workspace.yaml` at `cwd` or any ancestor → **workspace mode**;
  that file's directory is the workspace root.
- Otherwise: `cwd` (or an ancestor) contains both `heddle/` and
  `heddle-agent-toolkit/` as immediate children → **workspace mode**;
  that directory is the workspace root.
- Otherwise: **single-repo mode** — you're inside one getheddle/* repo
  cloned alone, or in a non-workspace context.

In workspace mode, list the siblings present (which getheddle/* repos
are checked out, which apps, which data peers). In single-repo mode,
state which repo you're in.

## The ecosystem (one screen)

```text
heddle (Python)               source of truth: wire protocol, schemas, subjects
  │  exports schemas/v1/*.schema.json
  ▼
heddle-sdk (.NET + Swift)     vendored schemas → language SDKs for processor workers
  │  Swift package consumed by
  ▼
warp-design (markdown only)   pre-implementation vision + ADRs
  │  informs
  ▼
warp (planned, Swift)         macOS cluster agent; not implemented yet

heddle-agent-toolkit          this toolkit: shared agent guidance, skills, subagents
getheddle.github.io           org-level overview site (planned → getheddle.dev)
```

## Who owns what

- **heddle**: TaskMessage / TaskResult / OrchestratorGoal, JSON Schemas,
  subject names, queue groups, router rules, Workshop UI, CLI, six
  shipped workers.
- **heddle-sdk**: .NET and Swift contract models (derived from heddle
  schemas), transport-agnostic worker bases, NATS adapters per language.
  Does **not** reimplement LLM workers, knowledge silos, Workshop, or
  orchestration.
- **warp-design**: ADRs, evolution log, vision docs. No code.
- **warp** (planned): Swift daemon for macOS-first ad-hoc clustering.

## The four rules to keep in mind

1. **heddle is upstream.** Schemas, subjects, queue groups originate
   there. Downstream repos vendor or mirror; they never invent.
2. **Workers are stateless** in every language. Reset between tasks.
   Mandatory.
3. **Progressive disclosure with sensible, inspectable defaults.**
   The common case works with no configuration. Complexity reveals
   itself only when the user reaches for it. Every default the system
   picks is visible somewhere the user can read. No magic.
4. **Solo / SMB / on-prem orientation.** If a change implicitly assumes
   a platform team or k8s ops, push back.

## When to read deeper

| If you're about to... | Read |
|---|---|
| Make structural changes to heddle | `heddle/docs/DESIGN_INVARIANTS.md` |
| Touch wire-protocol or schema files | `anchors/CONTRACT_MAP.md`, `anchors/INVARIANTS.md` |
| Design a new feature | `anchors/PHILOSOPHY.md` |
| Work in heddle-sdk | `heddle-sdk/AGENTS.md` |
| Work across siblings from the workspace root | `anchors/WORKSPACE.md` |
| Write a warp ADR | `warp-design/decisions/` (existing ADRs as format reference) |

## Which subagent for what

- Non-trivial change you haven't designed yet → spawn `heddle-architect`.
- Diff that touches workers, router, orchestrator, bus → spawn
  `heddle-invariant-guard`.
- Diff that touches `core/messages.py`, `schemas/v1/*`, .NET models, or
  Swift models → spawn `heddle-contract-reviewer`.

## What to actually do now

1. State whether you're in workspace mode or single-repo mode, and what
   you're about to touch. In workspace mode, list the siblings present.
2. If the change is multi-repo (e.g., a schema change), invoke
   `/heddle-contract-sync` before committing in either repo.
3. If you are unsure which invariants apply, invoke `/heddle-invariants`.

Output a short summary back to the user once oriented:

> Single-repo: "Oriented. Working in `<repo>`. The relevant anchors are
> `<list>`. Next step: `<what you propose>`."

> Workspace: "Oriented. Workspace `<name>` with siblings `<list>`. About
> to touch `<repos>`. The relevant anchors are `<list>`. Next step:
> `<what you propose>`."
