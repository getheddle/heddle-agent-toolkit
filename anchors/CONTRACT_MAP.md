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
                          ├─► swift/Sources/HeddleActor/Models/ (manually-aligned Swift models)
                          └─► jvm/core/src/main/kotlin/heddle/sdk/Models.kt (manually-aligned JVM models)
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

## Control subjects

Control subjects carry **out-of-band signals to running actors** —
hot-reload broadcasts, future shutdown signals, future health pings.
They are deliberately separate from the actor envelope family
(`TaskMessage` / `TaskResult` / `OrchestratorGoal`):

| | Actor envelopes | Control subjects |
|---|---|---|
| Subject prefix | `heddle.tasks.*`, `heddle.results.*`, `heddle.goals.*` | `heddle.control.*` |
| Payload | Typed Pydantic models, schema-declared | Currently raw dicts; not in `schemas/v1/` |
| Validated by | `core.contracts` shallow validation | Publisher discipline — no validator runs |
| Direction | Actor-to-actor | Control plane → actors (fanout) |

### Reserved control subjects today

| Subject | Payload shape (today) | Owner | Notes |
|---|---|---|---|
| `heddle.control.reload` | `{"action": "reload"}` (raw dict, not validated) | `heddle.workshop.app_manager` (`notify_reload`) | Best-effort fanout; receivers (any `BaseActor`) call `on_reload()` (default no-op). |

### Why no schema today

The control plane is exactly one subject with one payload shape. A
typed `ControlMessage` envelope is the right move *if and when* the
control plane grows beyond one or two signals — at that point the
typo-cost and the cost of "publisher discipline" exceed the cost of
maintaining a typed envelope. Until then the raw-dict shape is
deliberately lightweight; receivers branch on `data.get("action")`
without claiming the wire contract is typed.

### When to promote to a typed envelope

If you add a second control signal that needs structured fields
(e.g. a `{"action": "shutdown", "grace_seconds": 10}` or a
`{"action": "health_ping", "request_id": "..."}`), promote the
control payload to a Pydantic envelope at that point. Steps:

1. Add `ControlMessage` to `heddle.core.messages` with `action: str`
   plus per-action fields as a discriminated union (or open
   metadata dict).
2. Export the schema via `tools/export_schemas.py`.
3. Update publishers (`workshop/app_manager.py:notify_reload` and
   peers) to construct + validate `ControlMessage` instances.
4. Update `BaseActor._run_control_listener` to parse via the
   envelope's `model_validate`.
5. Vendor downstream into `heddle-sdk` and update SDK `Subjects`
   helpers if foreign actors will subscribe to control too.

Today this is **deliberately deferred** — the control plane hasn't
demonstrated the growth that justifies the typed-envelope cost.

## Reserved middleware lane: underscore-prefixed wire keys

The wire envelope has two addressable surfaces:

1. **Application contract** — the Pydantic models in
   `heddle.core.messages` and the matching JSON Schemas in
   `schemas/v1/`. Application code reads and writes these fields.
   Strictly typed; changes follow the workflows in this document.
2. **Middleware lane** — top-level keys on the JSON envelope whose
   names **start with an underscore**. Owned by tagged middleware
   modules, not application code. **Not declared in the schemas.**
   Senders MAY include them; receivers MUST tolerate their presence
   without validation; application code SHOULD NOT read or write them
   directly.

Modern messaging stacks all separate these lanes (HTTP body vs
traceparent header; Kafka body vs headers; gRPC message vs metadata;
CloudEvents typed fields vs extensions map). Heddle's wire envelope
is a single JSON object, so the underscore-prefix convention is what
distinguishes the lanes within one object. The rule is
formalized as **Invariant #22** in the framework documentation (see
**[`heddle/docs/DESIGN_INVARIANTS.md`](../../heddle/docs/DESIGN_INVARIANTS.md#22-middleware-lane)**).

### Why this matters

The pattern lets new middleware concerns (tracing, correlation,
tenant tagging, etc.) ride on the existing envelope without expanding
the typed contract or breaking forward-compatibility. Application
schemas stay focused on what application code reads/writes;
middleware evolves on its own cadence.

### Reserved keys today

| Key | Owner | Spec |
|---|---|---|
| `_trace_context` | `heddle.tracing.otel` | W3C Trace Context (`traceparent` / `tracestate` headers, dict-shaped) |

Adding a new reserved key requires:

1. A tagged middleware module that owns the read/write of the key
   (e.g. `heddle.X.inject_X()` / `heddle.X.extract_X()`).
2. An update to this table.
3. An update to the allowlist in
   `heddle/tools/check_envelope_convention.py` (the mechanical
   enforcement of the convention).
4. Mention in `heddle/CHANGELOG.md` under `[Unreleased]` —
   middleware-lane additions are behavioural changes for downstream
   consumers.

### Rules

- **Application Pydantic models** (`heddle.core.messages`) MUST NOT
  declare fields whose names start with `_`. The middleware lane is
  reserved.
- **JSON Schemas** in `schemas/v1/` MUST NOT declare properties whose
  names start with `_`. Middleware-lane fields are intentionally
  unschema'd to preserve forward compatibility.
- **Schemas SHOULD NOT set top-level `additionalProperties: false`.**
  Heddle's Invariant 4 ("Shallow JSON Schema validation") and the
  middleware lane both depend on receivers tolerating unknown extras.
  If a future change makes strict validation necessary, the schema
  MUST also include `patternProperties: { "^_": {} }` to carve the
  middleware lane back out.
- **Middleware modules** (those listed in the allowlist above) MUST
  only read and write `_`-prefixed keys on the wire carrier. Reading
  or writing a non-`_` key on the carrier is a violation.
- **SDKs (any language) MUST propagate underscore-prefixed keys
  unchanged.** They don't parse or modify them. They MAY ignore them
  entirely. They MUST NOT reject envelopes that include them.

### Enforcement

Convention durability is enforced by three mechanisms, in order of
strength:

1. **Lint** — `heddle/tools/check_envelope_convention.py` runs in CI
   and rejects: Pydantic models declaring `_*` fields; middleware
   modules touching non-`_*` carrier keys; schemas declaring `_*`
   properties; schemas setting `additionalProperties: false` without
   the underscore carve-out.
2. **Tests** — `heddle/tests/test_envelope_convention.py` pins the
   runtime contract: middleware fields round-trip through Pydantic
   without rejection or contamination of the typed envelope.
3. **This document** — the human-readable rule, for new contributors
   and reviewers.

Drift on any of the three layers is recoverable but visible.

## When the contract changes

### Adding a new optional field

1. Add the field to the relevant Pydantic model in
   `heddle.core.messages` with a default value.
2. Regenerate `heddle/schemas/v1/*.schema.json` (heddle's schema
   exporter).
3. Run `python tools/sync_schemas.py --update --upstream ../heddle` from
   `heddle-sdk` to vendor the new schemas.
4. Add the field to the .NET, Swift, and JVM models. Both must compile with
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
   `heddle-workspace/anchors/CONTRACT_MAP.md` (this file).
3. Add it to each SDK's `Subjects` helper, byte-identical.
4. If the subject carries a new envelope shape, follow the "adding a new
   field" workflow first to get the envelope into the schemas.

## Verification

| Check | Command | Where |
|---|---|---|
| Schema sync up to date | `python tools/sync_schemas.py --check` | `heddle-sdk/` |
| .NET contract tests | `dotnet test dotnet/tests/Heddle.Sdk.Tests/Heddle.Sdk.Tests.csproj` | `heddle-sdk/` |
| Swift contract tests | `swift test --package-path swift` | `heddle-sdk/` |
| JVM contract tests | `./jvm/gradlew -p jvm test` | `heddle-sdk/` |
| Python message tests | `uv run pytest tests/ -k messages` | `heddle/` |
| Whole preflight | `/heddle-preflight` | anywhere |
