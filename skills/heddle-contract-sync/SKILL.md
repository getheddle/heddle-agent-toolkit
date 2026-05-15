---
name: heddle-contract-sync
description: Verify or update the schema sync between heddle (upstream source of truth) and heddle-sdk (vendored copies). Use whenever a change touches heddle.core.messages, schemas/v1/*, .NET models, Swift models, or NATS subject conventions — or when you suspect downstream is behind upstream.
---

# /heddle-contract-sync — keep heddle and heddle-sdk in lockstep

The wire-protocol source of truth is `heddle.core.messages` (Pydantic
models) in the `heddle` repo. Schemas flow outward via
`heddle-sdk/tools/sync_schemas.py`. Everything else is downstream.

## When to invoke

- After editing `heddle/src/heddle/core/messages.py`.
- After regenerating `heddle/schemas/v1/*.schema.json`.
- After changing NATS subject names, queue group names, or contract
  envelope fields anywhere.
- Before merging a PR that touches any of the above.
- When a `heddle-sdk` test fails with a schema mismatch and you're not
  sure whether upstream is ahead or downstream forgot to sync.

## Workflow

### Step 1 — verify

From `heddle-sdk/`:

```bash
python tools/sync_schemas.py --check
```

Three outcomes:

- **OK** — vendored manifest matches upstream commit; no sync needed.
- **Behind upstream** — heddle has changed; downstream needs the update.
- **Manifest broken** — local edits to `heddle-sdk/schemas/v1/*` or the
  manifest itself. This is a violation of invariant C1. Investigate
  before syncing.

### Step 2 — sync (only if behind)

From `heddle-sdk/`, with a local heddle checkout adjacent:

```bash
python tools/sync_schemas.py --update --upstream ../heddle
```

This copies `schemas/v1/*.schema.json` from upstream, updates
`schemas/manifest.json` with the upstream commit hash + file hashes, and
reports what changed.

### Step 3 — propagate to language models

Vendored schemas update automatically. The language-specific models
(`.NET` and `Swift`) are not auto-generated today — they're manually
aligned and guarded by tests. After a sync:

```bash
# Run the contract tests in both languages to surface drift:
cd heddle-sdk
dotnet test dotnet/tests/Heddle.Sdk.Tests/Heddle.Sdk.Tests.csproj
swift test --package-path swift
```

If either fails, update the corresponding `Models/` directory by hand
to match the new schema, then re-run the tests. Aim for **language
parity** (invariant C6): if you added a field in .NET, add it in Swift
too unless explicitly documented as language-specific.

### Step 4 — propagate subject changes (if any)

Subject names and queue-group names are not in the JSON Schema files;
they live in code. If your upstream change touched subjects:

- Update `dotnet/src/Heddle.Sdk/Subjects.cs`.
- Update `swift/Sources/HeddleActor/Subjects.swift`.
- Update `heddle-agent-toolkit/anchors/CONTRACT_MAP.md` if it's a new
  subject.
- Update `heddle/docs/ARCHITECTURE.md` NATS-subjects table.

## What to verify before committing

```bash
# in heddle-sdk:
python tools/sync_schemas.py --check        # must say OK
dotnet build dotnet/src/Heddle.Sdk/Heddle.Sdk.csproj
dotnet test dotnet/tests/Heddle.Sdk.Tests/Heddle.Sdk.Tests.csproj
swift build --package-path swift
swift test --package-path swift
swift build --package-path swift-nats
```

If the change adds a *new* subject or field, also confirm:

- `heddle/docs/foreign-actors.md` documents it (heddle side).
- An example in `heddle-sdk/examples/` exercises it, or there's a test
  in `dotnet/tests/` and `swift/Tests/` that does.

## Output format

```
Sync check: <OK | behind | broken>
Upstream commit: <sha or "n/a">
Action taken: <none | --update run | manual edits applied>
Tests run: <list>
Result: <pass | fail with summary>
```

If anything fails, do not commit. Report to the user and ask for direction.
