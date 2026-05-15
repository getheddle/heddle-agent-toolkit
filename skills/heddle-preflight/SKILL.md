---
name: heddle-preflight
description: Repo-aware pre-commit verification for any getheddle/* repo. Runs lint, type-check, unit tests, schema sync, and docs-build for the current working directory and reports a single pass/fail with details. Use before every commit on a structural change; required before cross-repo PRs.
---

# /heddle-preflight — verify before commit

Detect which `getheddle/*` repo you are in by the presence of marker
files and run the appropriate verification suite. Report a single
pass/fail at the end with per-step results.

## Detection

| Marker | Repo |
|---|---|
| `pyproject.toml` with `name = "heddle-ai"` | `heddle` |
| `Package.swift` + `dotnet/` | `heddle-sdk` |
| `EVOLUTION_LOG.md` + `decisions/` | `warp-design` |
| `Package.swift` + `Sources/Warp` (eventually) | `warp` (planned) |

If detection is ambiguous, ask the user.

## heddle (Python)

```bash
# Lint and format
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/

# Type-check (strict)
uv run pyright src/

# Unit tests (no infrastructure required)
uv run pytest tests/ -v -m "not integration and not deepeval"

# Worker config validation
uv run heddle validate configs/workers/*.yaml

# Docs build (strict — catches broken links)
uvx --from mkdocs --with mkdocs-material mkdocs build --strict
```

Optional but recommended on structural changes:

```bash
# Integration tests (needs NATS running)
uv run pytest tests/ -v -m integration
```

## heddle-sdk

```bash
# Schema sync still up to date with heddle
python tools/sync_schemas.py --check

# .NET
dotnet build dotnet/src/Heddle.Sdk/Heddle.Sdk.csproj
dotnet test dotnet/tests/Heddle.Sdk.Tests/Heddle.Sdk.Tests.csproj
dotnet build dotnet/src/Heddle.Sdk.Nats/Heddle.Sdk.Nats.csproj
dotnet build examples/dotnet/EchoWorker/EchoWorker.csproj

# Swift
swift package dump-package
swift build --package-path swift
swift test --package-path swift
swift build --package-path swift-nats
swift build --package-path examples/swift/echo-worker

# Docs build
uvx --from mkdocs --with mkdocs-material mkdocs build --strict
```

## warp-design

```bash
# Markdown lint (if rumdl or similar is configured)
[ -f .rumdl.toml ] && rumdl check . || echo "no markdown linter configured"

# ADR format check — files must match NNNN-kebab-case-title.md
ls decisions/ | grep -Ev '^[0-9]{4}-[a-z0-9-]+\.md$' && echo "ADR naming violation" || true

# Docs build (if mkdocs is added later)
[ -f mkdocs.yml ] && uvx --from mkdocs --with mkdocs-material mkdocs build --strict
```

## warp (planned, Swift)

When the repo exists:

```bash
swift build
swift test
# plus signing/notarization checks for release builds
```

## Cross-repo changes

If your change touches more than one repo:

1. Run preflight in **each** affected repo.
2. If heddle changed `core/messages.py` or `schemas/v1/*`, also run
   `/heddle-contract-sync` from `heddle-sdk/`.
3. Confirm docs were updated in the same change set (in each repo where
   docs reference the changed behavior).

## Output format

```
Preflight: <repo-name>
  ruff:         <pass|fail>
  pyright:      <pass|fail>
  pytest:       <pass|fail (N failed, M skipped)>
  schema sync:  <pass|fail|n/a>
  docs build:   <pass|fail>
Result: <PASS | FAIL>
```

If FAIL, do not commit. Report the failing step's first error to the
user and stop.
