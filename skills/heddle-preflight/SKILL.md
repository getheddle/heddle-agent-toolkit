---
name: heddle-preflight
description: Repo-aware pre-commit verification for any getheddle/* repo. Runs lint, type-check, unit tests, schema sync, and docs-build for the current working directory and reports a single pass/fail with details. Use before every commit on a structural change; required before cross-repo PRs.
---

# /heddle-preflight — verify before commit

Detect which `getheddle/*` repo you are in (or whether you are at a
workspace root) and run the appropriate verification suite. Report a
single pass/fail at the end with per-step results.

## Detection

First, apply the workspace check from
`heddle-workspace/anchors/WORKSPACE.md`. Then:

- **Workspace mode** (`cwd` is the workspace root): preflight runs
  per-sibling. By default, only run preflight in repos whose
  `git diff --staged` (or `git diff`) is non-empty — preflighting
  unchanged repos wastes time. Override with explicit user request
  ("preflight all repos in the workspace").
- **Single-repo mode** — detect which getheddle/* repo by marker file:

| Marker | Repo |
|---|---|
| `pyproject.toml` with `name = "heddle-ai"` | `heddle` |
| `Package.swift` + `dotnet/` | `heddle-sdk` |
| `EVOLUTION_LOG.md` + `decisions/` | `warp-design` |
| `Package.swift` + `Sources/Warp` (eventually) | `warp` (planned) |

If detection is ambiguous, ask the user.

App-level repos (e.g., `baft`) have their own preflight conventions
defined in their own `AGENTS.md` (typically `<app> preflight` as a CLI
subcommand). When workspace-mode preflight detects a changed app
sibling, run the app's documented preflight if the `AGENTS.md` defines
one; otherwise note that the sibling has changes but no defined
preflight and skip rather than guess.

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

## CHANGELOG check

For repos that maintain a `CHANGELOG.md` (heddle, heddle-sdk,
heddle-workspace), verify the `[Unreleased]` section has at least
one categorized entry when the staged diff touches behaviour-bearing
paths. Behaviour-bearing means:

- `src/`, `dotnet/src/`, `swift/Sources/`, `swift-nats/Sources/` —
  code that ships.
- `configs/workers/*.yaml`, `configs/orchestrators/*.yaml`, public
  schemas under `schemas/v1/` — user-facing contract.
- Skills, anchors, or subagents under `skills/`, `anchors/`, `agents/`
  in the toolkit.

Exempt: `docs/**.md`, `README.md`, `tests/`, `.github/`, internal
refactors with no user-visible delta. Don't fail-flag exempt diffs.

Mechanically (run from repo root):

```bash
# Has the diff touched behaviour-bearing paths?
git diff --staged --name-only | grep -E \
    '^(src/|dotnet/src/|swift/Sources/|swift-nats/Sources/|configs/workers/|configs/orchestrators/|schemas/v1/|skills/|anchors/|agents/)' \
    && BEHAVIOUR_CHANGE=1 || BEHAVIOUR_CHANGE=0

# If yes, does [Unreleased] have any categorized entries?
if [[ $BEHAVIOUR_CHANGE = 1 ]] && [[ -f CHANGELOG.md ]]; then
    awk '/^## \[Unreleased\]/{flag=1; next} /^## \[/{flag=0} flag' CHANGELOG.md \
        | grep -E '^### (Added|Changed|Deprecated|Removed|Fixed|Security)$' \
        > /dev/null || echo "warning: behaviour change but no Unreleased entry in CHANGELOG.md"
fi
```

A missing CHANGELOG entry is a warning, not a hard block — author can
judge whether the change is exempt (e.g., a refactor whose paths
touched `src/` but whose behaviour is unchanged). Prompt the user
before letting the commit proceed without an entry.

## Cross-repo changes

If your change touches more than one repo:

1. Run preflight in **each** affected repo.
2. If heddle changed `core/messages.py` or `schemas/v1/*`, also run
   `/heddle-contract-sync` from `heddle-sdk/`.
3. Confirm docs were updated in the same change set (in each repo where
   docs reference the changed behavior).
4. Each affected repo's `CHANGELOG.md` gets its own `[Unreleased]`
   entry — entries don't cross repo boundaries.

## Output format

Single-repo mode:

```
Preflight: <repo-name>
  ruff:         <pass|fail>
  pyright:      <pass|fail>
  pytest:       <pass|fail (N failed, M skipped)>
  schema sync:  <pass|fail|n/a>
  docs build:   <pass|fail>
  CHANGELOG:    <pass|warn (behaviour change, no Unreleased entry)|n/a>
Result: <PASS | FAIL>
```

Workspace mode (one block per changed sibling, then a workspace verdict):

```
Preflight: heddle
  ruff:         pass
  pyright:      pass
  pytest:       pass (0 failed, 12 skipped)
  ...
Result: PASS

Preflight: heddle-sdk
  schema sync:  fail (downstream behind upstream)
  ...
Result: FAIL

Workspace: FAIL (heddle-sdk schema sync)
```

If FAIL, do not commit. Report the failing step's first error to the
user and stop. If CHANGELOG is `warn`, prompt the user; don't auto-fail.
In workspace mode, the workspace verdict is FAIL if any sibling's
preflight is FAIL.
