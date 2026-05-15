# Invariants — cross-repo and pointers

## Framework-internal invariants (heddle Python)

The 21 framework-level invariants for `heddle` are documented canonically
in **[`heddle/docs/DESIGN_INVARIANTS.md`](https://github.com/getheddle/heddle/blob/main/docs/DESIGN_INVARIANTS.md)**.
Do not duplicate that content here. Read it directly when proposing
structural changes to `src/heddle/{core,worker,router,orchestrator,bus,scheduler}`.

The eight framework red lines (from the summary section there):

1. Never put LLM calls in the router.
2. Never carry state between worker tasks.
3. Never skip contract validation.
4. Never change condition-evaluation defaults from FALSE.
5. Never run multiple instances of a single-writer processor.
6. Never publish before subscribing in request-reply.
7. Never leak full transcripts to all council agents.
8. Never let a convergence detector mutate the transcript.

## Cross-repo invariants (added here)

These rules govern the seam between repositories. They are not in
`heddle/docs/DESIGN_INVARIANTS.md` because they don't apply to a single
codebase.

### C1. Schema source of truth lives in heddle

`heddle/schemas/v1/*.schema.json` is generated from
`heddle.core.messages` (Pydantic models) in the heddle repository. Every
other repository that uses these schemas — currently `heddle-sdk` —
*vendors* them through a sync tool. The vendored copies must match the
upstream commit recorded in `heddle-sdk/schemas/manifest.json`.

**How it fails:** Editing `heddle-sdk/schemas/v1/*.schema.json` directly
creates a second source of truth. Subsequent upstream changes silently
diverge. Foreign-language workers compiled against the local schema then
disagree with the Python runtime about field names, types, or required
fields — over the wire, silently.

**Enforcement:** `python tools/sync_schemas.py --check` (run from
`heddle-sdk/`) compares the vendored manifest hash against the upstream
commit. CI runs this on every PR. The `/heddle-contract-sync` skill in
this toolkit wraps the workflow.

### C2. Subject names are part of the contract

NATS subjects (`heddle.tasks.incoming`, `heddle.tasks.{worker_type}.{tier}`,
`heddle.results.{parent_task_id or "default"}`, `heddle.tasks.dead_letter`,
`heddle.goals.incoming`, `heddle.control.reload`) are defined in `heddle`
and must be reproduced **byte-identically** in every SDK's `Subjects`
helper. Same with queue group names (`processors-{worker_type}`).

**How it fails:** A typo or inconsistent capitalization in a downstream
SDK means workers from that language don't receive messages. The failure
is silent in the SDK (the subscription just never fires) and looks like a
slow worker in the producer.

### C3. Workers are stateless in every language

Invariant 1 from heddle's `DESIGN_INVARIANTS.md` applies to every SDK's
worker base. The base class must call a `reset()` hook (or equivalent)
after every task, unconditionally — including on exception paths.
Examples in any language must not encourage persistent per-task state.

### C4. Foreign workers are processor workers, not LLM workers

The SDK exists to host *processor* workers (deterministic transformations,
database writes, external-system calls). It does not reimplement
`LLMWorker`, knowledge silos, the Workshop UI, or orchestration. Foreign
LLM workers are out of scope until the upstream framework defines that
expansion.

**How it fails:** A "let's add LLM support to the .NET SDK" PR creates a
divergent runtime; suddenly there are two implementations of model-tier
selection, knowledge-silo discipline, and Workshop integration to keep in
sync. The maintenance cost is hidden until something diverges.

### C5. Transport stays abstract in core SDK packages

`Heddle.Sdk` (.NET) and `HeddleActor` (Swift) must not depend on a
concrete NATS client. NATS adapters live in sibling packages
(`Heddle.Sdk.Nats`, `swift-nats`). Core packages ship an in-memory
transport so examples and tests run without infrastructure.

**How it fails:** Pulling a concrete NATS dependency into the core
package means every consumer pulls the entire NATS client transitively,
the in-memory test path becomes harder to keep working, and a future
non-NATS transport (e.g., a SwiftNIO-based adapter for warp) becomes a
breaking change.

### C6. Language parity in the SDK

New behavior in the .NET SDK must have a Swift equivalent, and vice
versa, **unless explicitly documented as language-specific**. Otherwise
the two SDKs slowly diverge in capability and the wire protocol becomes
the lowest common denominator of "what both happen to expose."

### C7. Warp design must propose, not implement, framework changes

ADRs in `warp-design` may propose changes to `heddle` or `heddle-sdk`.
The implementation goes through the upstream repository's normal PR
flow — design docs do not get to silently change framework behavior by
being referenced.

## How to check before a commit

The `/heddle-preflight` skill (toolkit) wraps these checks:

- `heddle` repo: ruff, pyright, pytest (unit), schema export.
- `heddle-sdk` repo: schema sync check, dotnet build+test, swift build+test.
- `warp-design`: markdown lint, ADR format check.

When the change touches multiple repos, run preflight in each.
