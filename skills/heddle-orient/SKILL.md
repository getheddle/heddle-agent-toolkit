---
name: heddle-orient
description: Use at session start (or after compaction) when working in a getheddle/* repository (heddle, heddle-sdk, warp-design, warp). Loads a one-screen cross-repo orientation — repo map, owner of each concern, schema source-of-truth direction, where to read further — without re-reading the full architecture docs. Especially useful when a session touches more than one of these repos.
---

# /heddle-orient — fast cross-repo orientation

Use this skill when you start (or resume) a session that touches any
`getheddle/*` repo. It is meant to replace re-reading the full anchor
docs every time. If something here is unclear, *then* read the linked
anchor.

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

## The three rules to keep in mind

1. **heddle is upstream.** Schemas, subjects, queue groups originate
   there. Downstream repos vendor or mirror; they never invent.
2. **Workers are stateless** in every language. Reset between tasks.
   Mandatory.
3. **Solo / SMB / on-prem orientation.** If a change implicitly assumes
   a platform team or k8s ops, push back.

## When to read deeper

| If you're about to... | Read |
|---|---|
| Make structural changes to heddle | `heddle/docs/DESIGN_INVARIANTS.md` |
| Touch wire-protocol or schema files | `anchors/CONTRACT_MAP.md`, `anchors/INVARIANTS.md` |
| Design a new feature | `anchors/PHILOSOPHY.md` |
| Work in heddle-sdk | `heddle-sdk/AGENTS.md` |
| Write a warp ADR | `warp-design/decisions/` (existing ADRs as format reference) |

## Which subagent for what

- Non-trivial change you haven't designed yet → spawn `heddle-architect`.
- Diff that touches workers, router, orchestrator, bus → spawn
  `heddle-invariant-guard`.
- Diff that touches `core/messages.py`, `schemas/v1/*`, .NET models, or
  Swift models → spawn `heddle-contract-reviewer`.

## What to actually do now

1. State which repo you are in and what you're about to touch.
2. If the change is multi-repo (e.g., a schema change), invoke
   `/heddle-contract-sync` before committing in either repo.
3. If you are unsure which invariants apply, invoke `/heddle-invariants`.

Output a short summary back to the user once oriented:

> "Oriented. Working in `<repo>`. The relevant anchors are
> `<list>`. Next step: `<what you propose>`."
