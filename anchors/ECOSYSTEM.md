# Ecosystem map — getheddle/*

The `getheddle` organization is a small, intentional family of repositories.
Knowing which one owns what keeps changes coherent across the seam.

## The repositories

```text
                ┌─────────────────────────────────────────────┐
                │ heddle (Python)                             │
                │   Actor-mesh framework over NATS.           │
                │   Wire-protocol + schema source of truth.   │
                │   Workshop web UI. CLI. Six shipped workers.│
                │   ── owns the runtime ──                    │
                └──────────────┬──────────────────────────────┘
                               │ schemas vendored, wire conventions copied
                               ▼
                ┌─────────────────────────────────────────────┐
                │ heddle-sdk (.NET + Swift)                   │
                │   Foreign-language worker SDKs.             │
                │   Vendors schemas/v1/*.schema.json.         │
                │   Transport-agnostic core + NATS adapters.  │
                │   ── owns language-side integration ──      │
                └──────────────┬──────────────────────────────┘
                               │ Swift package consumed by
                               ▼
                ┌─────────────────────────────────────────────┐
                │ warp-design (markdown only)                 │
                │   Vision, ADRs, evolution log, research.    │
                │   Pre-implementation. macOS cluster agent.  │
                │   ── owns design exploration ──             │
                └──────────────┬──────────────────────────────┘
                               │ informs
                               ▼
                ┌─────────────────────────────────────────────┐
                │ warp (planned — Swift)                      │
                │   Production code for the macOS agent.      │
                │   Supervises heddle Python service via      │
                │   SMAppService; mDNS peer discovery.        │
                │   ── will own the agent runtime ──          │
                └─────────────────────────────────────────────┘
```

Plus the org overview site at **`getheddle.github.io`** (lands at
`getheddle.dev`), which introduces the family to the wider world.

And this repo: **`heddle-workspace`** — the AI-agent guidance layer
that pulls invariants and skills out of any single repo so they can be
shared.

## Who owns what

| Concern | Owner |
|---|---|
| Wire protocol (TaskMessage, TaskResult, OrchestratorGoal) | `heddle` |
| Pydantic message models (`heddle.core.messages`) | `heddle` |
| JSON Schema files (`schemas/v1/*.schema.json`) | `heddle` — exported, vendored downstream |
| NATS subject conventions | `heddle` |
| Queue-group naming (`processors-{worker_type}`) | `heddle` |
| Router rules, model tiers | `heddle` |
| .NET / Swift contract models | `heddle-sdk` (derived from heddle schemas) |
| Transport adapters per language | `heddle-sdk` |
| Vision, ADRs for the macOS cluster agent | `warp-design` |
| The actual macOS daemon | `warp` (planned) |
| Cross-repo agent guidance, skills, subagents | this repo |
| Org-level public face | `getheddle.github.io` |

## Direction of dependency

Always flows **outward from `heddle/`**:

- A change to `heddle.core.messages` may require a follow-up sync into
  `heddle-sdk` via `tools/sync_schemas.py`.
- A change to subject conventions is an upstream change in `heddle` plus
  downstream updates in every SDK's `Subjects` helper.
- A change in `heddle-sdk` that has no upstream counterpart in `heddle` is
  almost always wrong — flag it.

## When changes cross repos

The repo where you start the change determines the workflow:

- **Start in `heddle`** (the common case): make the change, run heddle's
  own tests, then run the SDK schema-sync check from `heddle-sdk` to see
  if downstream needs updating.
- **Start in `heddle-sdk`**: only language-side concerns belong here
  (codegen, transport adapters, language ergonomics). If your edit
  *implies* a wire-protocol change, stop and start over in `heddle`.
- **Start in `warp-design`**: writing an ADR or evolution-log entry that
  may *propose* a change to `heddle` or `heddle-sdk`. The proposal is
  fine; the implementation goes through the upstream repo's normal PR flow.
