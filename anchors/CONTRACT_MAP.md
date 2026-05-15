# Contract map — schema source of truth and how it propagates

This document is the operational reference for "where do the wire schemas
live, and what do I do when they change?"

## The contract

The Heddle wire protocol is intentionally small:

| Envelope | Defined in | Purpose |
|---|---|---|
| `TaskMessage` | `heddle.core.messages` (Pydantic) | A unit of work dispatched to a worker |
| `TaskResult` | `heddle.core.messages` (Pydantic) | A worker's response |
| `OrchestratorGoal` | `heddle.core.messages` (Pydantic) | A higher-level goal handed to an orchestrator |

Plus per-worker I/O schemas — defined per-worker in YAML, or by Pydantic
model reference (`input_schema_ref` / `output_schema_ref`).

## Source of truth

```text
              heddle.core.messages (Pydantic)            ← source of truth
                          │
                          │ exported via schema generator
                          ▼
              heddle/schemas/v1/*.schema.json            ← JSON Schema, in heddle repo
                          │
                          │ vendored via tools/sync_schemas.py
                          ▼
              heddle-sdk/schemas/v1/*.schema.json        ← vendored copy
              heddle-sdk/schemas/manifest.json           ← records upstream commit + hashes
                          │
                          ├─► dotnet/src/Heddle.Sdk/Models/    (manually-aligned .NET models)
                          └─► swift/Sources/HeddleActor/Models/ (manually-aligned Swift models)
```

The Python Pydantic models are authoritative. The JSON Schema files are
the *interchange* format. The language-specific models are derived (today
by hand, with regression tests guarding the contract).

## NATS subject conventions

These names are part of the contract — exact bytes, same in every SDK.

| Subject | Purpose | Direction |
|---|---|---|
| `heddle.goals.incoming` | Top-level goals for orchestrators | client → orchestrator |
| `heddle.tasks.incoming` | Tasks awaiting routing | producer → router |
| `heddle.tasks.{worker_type}.{tier}` | Task delivery to workers | router → worker queue group |
| `heddle.tasks.dead_letter` | Unroutable or rate-limited tasks | router → dead-letter consumer |
| `heddle.results.{parent_task_id}` | Results from a worker, addressed to the task's parent | worker → orchestrator or standalone caller |
| `heddle.results.default` | Results for standalone tasks (where `parent_task_id` is null) | worker → caller |

The worker always publishes to `heddle.results.{parent_task_id or "default"}` — that is the wire-level form. For orchestrator-dispatched tasks the orchestrator sets `parent_task_id == goal_id`, so orchestrator code subscribes to `heddle.results.{goal_id}` in practice; the underlying subject is still parameterized by `parent_task_id` on the worker side. The canonical form for SDK and foreign-actor docs is `parent_task_id`.
| `heddle.control.reload` | Config hot-reload broadcast | control-plane → workers |

## Queue groups

| Worker class | Queue group |
|---|---|
| Python `LLMWorker` / `ProcessorWorker` | `workers-{worker_type}` |
| Foreign processor workers (SDK) | `processors-{worker_type}` |

Both subscribe to the same `heddle.tasks.{worker_type}.{tier}` subject; the
distinct queue-group names mean Python and foreign processors form
separate consumer pools and the router can be informed by deployment
which kind is available.

## Trace context

When present, `_trace_context` rides as a top-level key on the JSON
envelope. SDKs propagate it unchanged — they don't parse or modify it.

## When the contract changes

### Adding a new optional field

1. Add the field to the relevant Pydantic model in
   `heddle.core.messages` with a default value.
2. Regenerate `heddle/schemas/v1/*.schema.json` (heddle's schema
   exporter).
3. Run `python tools/sync_schemas.py --update --upstream ../heddle` from
   `heddle-sdk` to vendor the new schemas.
4. Add the field to the .NET and Swift models. Both must compile with
   the field omitted from incoming JSON.
5. Update `docs/foreign-actors.md` in heddle if the field is observable
   to processor workers.
6. Run `/heddle-contract-sync` and `/heddle-preflight` in both repos.

### Adding a required field — don't

This is a wire-breaking change. Old workers will reject messages from new
producers, and new workers will reject messages from old producers.
Prefer: ship an optional field, migrate consumers, then plan a separate
version bump.

### Renaming or removing a field

Wire-breaking. Treat as a v2 conversation. Open an ADR in `warp-design`
or a discussion before implementing.

### Adding a new subject

1. Decide the name following existing patterns. The convention is
   `heddle.<topic>.<sub>`.
2. Add it to `heddle/docs/ARCHITECTURE.md` (NATS subjects table) and to
   `heddle-agent-toolkit/anchors/CONTRACT_MAP.md` (this file).
3. Add it to each SDK's `Subjects` helper, byte-identical.
4. If the subject carries a new envelope shape, follow the "adding a new
   field" workflow first to get the envelope into the schemas.

## Verification

| Check | Command | Where |
|---|---|---|
| Schema sync up to date | `python tools/sync_schemas.py --check` | `heddle-sdk/` |
| .NET contract tests | `dotnet test dotnet/tests/Heddle.Sdk.Tests/Heddle.Sdk.Tests.csproj` | `heddle-sdk/` |
| Swift contract tests | `swift test --package-path swift` | `heddle-sdk/` |
| Python message tests | `uv run pytest tests/ -k messages` | `heddle/` |
| Whole preflight | `/heddle-preflight` | anywhere |
