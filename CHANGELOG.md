# Changelog

All notable changes to the Heddle Agent Toolkit are documented here.
The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the
project adheres to [Semantic Versioning](https://semver.org/).

Changes to anchors, skills, or subagents in this repo are
**behavioural changes for agent consumers** of the toolkit and must
be recorded here. Documentation-only changes (typo fixes, README
clarifications) and CI/tooling adjustments are exempt. See `AGENTS.md`
"How this toolkit conflicts with a repo file" for guidance on
cross-repo coherence; see this `CHANGELOG.md` itself for the entry-
format model.

## [Unreleased]

### Changed

- **Repository renamed: `heddle-agent-toolkit` → `heddle-workspace`.**
  GitHub auto-redirects the old clone URLs. The rename reflects the
  repo's widened mission: in addition to the agent-tooling pillar
  (anchors, skills, subagents), it now also owns the workspace
  lifecycle pillar (umbrella-repo design, `.heddle-workspace.yaml`
  manifest, `bin/workspace` CLI). README, `AGENTS.md`, and
  `anchors/WORKSPACE.md` updated; historical CHANGELOG entries left
  verbatim. Consumer repos (`heddle/`, `heddle-sdk/`, `warp-design/`,
  `getheddle-dotgithub/`) updated separately so each repo's diff
  stays focused.

### Added

- `docs/WORKSPACE_SYNC_DESIGN.md` — full design rationale for the
  workspace-sync facility: the umbrella git repo on the project's own
  org, the `.heddle-workspace.yaml` manifest format with remote URLs,
  the `(local-only)/` carve-out, the `bin/workspace init / link /
  sync / status / add / rm / doctor` CLI, the bootstrap flow for two
  already-divergent workspaces, and explicit non-goals (no
  submodules, no SHA-pinning by default, no subtree embedding).
  Supersedes the unimplemented manifest sketch previously in
  `anchors/WORKSPACE.md`.
- `mcp/` — project-scoped `.mcp.json` template for Heddle-family
  workspaces, pre-configured with `context7` (live docs lookup, no
  auth) and `github` (cross-repo PR/issue/CI access; token resolved
  from `gh auth token` at MCP startup, so nothing sensitive is
  checked in). Mirrors the `hooks/` pattern: opt-in template, not
  auto-installed. `install.sh --mcp <target>` drops the template
  into `<target>/.mcp.json` when absent; see `mcp/README.md` for
  manual merge steps and prerequisites (`npx`, authenticated `gh`).
  Replaces the by-hand `claude mcp add github` / `claude mcp add
  context7` recommendation previously embedded in `install.sh`'s
  workspace `AGENTS.md` template.
- `agents/pyproject-deps-reviewer.md` — read-only reviewer for Python
  dependency changes (extras coverage, version drift, MPL-2.0 license
  compatibility, orphan deps, uv.lock hygiene). Spawn when a diff
  touches `pyproject.toml` or `uv.lock`.
- `agents/mkdocs-doc-reviewer.md` — read-only reviewer for MkDocs
  docs changes in `heddle/` and `heddle-sdk/` (nav coherence,
  cross-refs, code-block tags, cross-repo doc consistency).
- `skills/cross-repo-pr/` — coordinates paired PRs across `heddle`
  (upstream) and `heddle-sdk` (downstream). Wraps
  `/heddle-contract-sync`, sets matching branch names, drafts
  cross-linked PR bodies, and enforces upstream-first merge order.
- `hooks/settings.template.json` + `hooks/README.md` — opt-in Claude
  Code hooks template. PostToolUse auto-ruff on Python edits in
  `heddle/`; PreToolUse reminder when editing schemas or vendored SDK
  models.
- `install.sh --hooks` — copies the hooks template to
  `<target>/.claude/settings.json` only when no settings file exists
  (never merges; that's manual by design).
- README and workspace-extras `AGENTS.md` now document the optional
  `claude-code-setup` plugin and the recommended MCP servers
  (`github`, `context7`) for further Claude Code tuning.

### Removed

- `audits/` directory and its four files (`audit-heddle.md`,
  `audit-heddle-sdk.md`, `audit-warp-design.md`, `README.md`). These
  were point-in-time documentation audits from 2026-05-15 — every
  CRITICAL finding spot-checked has been addressed in the underlying
  repos (heddle's CLAUDE.md split landed, `pip install heddle-ai`
  is in README, NATS.md's Swift `package:` snippet uses
  `swift-nats`, all five warp-design research stubs exist). The
  files were marketed as "historical snapshots" in their own
  README, but agents reading them risk acting on stale findings as
  if still open. Removed to avoid that confusion. The files remain
  recoverable from git history if anyone needs to reference the
  audit decisions.

### Added

- `anchors/CONTRACT_MAP.md` "Control subjects" section — documents
  the `heddle.control.*` subject family as deliberately separate
  from the actor envelope family (`TaskMessage` / `TaskResult` /
  `OrchestratorGoal`). Reserved-subjects table lists today's only
  control subject (`heddle.control.reload` with raw-dict payload
  `{"action": "reload"}`), explains why no typed envelope today
  (one subject, one payload, typed envelope's cost exceeds its
  value), and lists the steps to promote to a typed
  `ControlMessage` if the control plane grows. Resolves
  Invariant-audit W2 — previously the raw-dict shape was implicit;
  now it's a documented convention with a clear promotion path.
- `anchors/CONTRACT_MAP.md` "Reserved middleware lane" section —
  formalizes the **underscore-prefix wire-key convention** that
  separates the typed application contract (Pydantic models +
  `schemas/v1/`) from the middleware lane (`_`-prefixed keys
  injected by tagged middleware modules like `heddle.tracing.otel`).
  Replaces the previous one-paragraph "Trace context" note. Defines:
  reserved keys table (today: `_trace_context`); rules for Pydantic
  models, JSON schemas, middleware modules, and SDKs; enforcement
  layers (lint, tests, doc). Resolves the audit-question of how to
  handle wire fields that live on the envelope today but aren't in
  the typed contract (Invariant audit M2 / Q1 in
  `INVARIANT_AUDIT_2026-05-15.md`) via approach (A) — convention +
  enforcement rather than hoisting individual fields into the
  schema. Pattern matches modern messaging stacks (HTTP body vs
  traceparent header; Kafka body vs headers; gRPC message vs
  metadata; CloudEvents typed vs extensions map). Companion lint
  script and tests live in
  [`heddle/tools/check_envelope_convention.py`](https://github.com/getheddle/heddle/blob/main/tools/check_envelope_convention.py)
  and
  [`heddle/tests/test_envelope_convention.py`](https://github.com/getheddle/heddle/blob/main/tests/test_envelope_convention.py)
  (heddle commit `52ade19`).

### Changed

- `agents/heddle-contract-reviewer.md` — sharpened after first
  field-use exposed three gaps:
  - **C1 split into C1a (vendoring drift) and C1b (wire ≡ source of
    truth).** A field that exists on the wire today (SDK models,
    middleware-injected, etc.) but is not declared in
    `core/messages.py` or `schemas/v1/*` is a **VIOLATION** under
    C1b. The previous rubric only caught hand-edited schema files
    and missed live-but-undeclared fields like `_trace_context`,
    which appears in both SDK models but in no upstream schema.
  - **Verification transparency required.** When schema sync is
    checked, the agent must run `python tools/sync_schemas.py
    --check` from `heddle-sdk/` and quote the output. "Schema
    manifest is in sync" without naming the verification method is
    no longer acceptable — a future reader needs to know whether the
    claim came from the canonical tool or from manual file
    comparison.
  - **Envelope-coverage check** added as a systematic step: for each
    envelope in upstream `core/messages.py`, confirm a corresponding
    model exists in both `.NET` and Swift directories. Missing a
    downstream model is a C6 violation even when no diff touched the
    envelope. This is the rule that catches "we added X upstream a
    month ago and forgot to mirror it" (the gap that surfaced
    Swift's missing `CheckpointState`).
- `agents/heddle-invariant-guard.md` — added a "When not to use this
  agent" section: this agent is a *diff reviewer*, not a codebase
  auditor. A bare "audit the codebase" prompt returns shallow grep
  output dressed as a review. The recommended substitute for
  snapshot audits is `Explore` → triage → optionally this agent
  per-file on surviving candidates. The section documents the
  workflow so future callers don't misuse the tool.

### Added

- `install.sh --workspace <path>` mode — same symlink install as
  single-repo mode, plus drops a starter workspace-level `AGENTS.md`
  and a starter `<workspace-name>.code-workspace` if neither exists.
  The `.code-workspace` `folders` list auto-discovers immediate-child
  git repositories. Files are only created when absent; re-running is
  safe. Single-repo mode (`./install.sh <repo>`) is unchanged.
- `README.md` — new "Getting started" section documenting the three
  user journeys (greenfield, adopt-existing, join-existing) for
  Heddle-based projects. Each path is three plain commands
  (`git clone heddle`, `git clone heddle-agent-toolkit`,
  `install.sh --workspace .`) rather than a bootstrap wrapper —
  fewer abstractions to learn or trust. Includes VSCode multi-root
  notes based on the existing user pattern and a status disclaimer
  framing the workspace convention as the *recommended* pattern that
  the toolkit is moving toward (CLI subcommands and manifest tooling
  intentionally deferred).
- `anchors/WORKSPACE.md` — new shared anchor defining the **Heddle
  workspace** convention: a parent directory holding `getheddle/*`
  repos and consuming apps as flat siblings, with optional
  `.heddle-workspace.yaml` manifest, workspace-level `.claude/`, and
  workspace-level `AGENTS.md`. Documents the detection heuristic
  (manifest → marker repos → single-repo fallback), the cross-repo
  git convention (walk siblings, union diffs), and the path
  convention (workspace-relative `<repo>/<path>` for cross-repo
  output, repo-relative otherwise). All other agents and skills point
  here rather than duplicating the convention.
- `skills/heddle-orient/SKILL.md` "rules to keep in mind" list grew
  from three to four items; progressive disclosure is now a top-level
  orientation rule alongside upstream-source-of-truth, statelessness,
  and solo/SMB orientation.
- `skills/heddle-new-worker/SKILL.md` adds an explicit step on
  scaffolding sensible, inspectable defaults in the worker YAML —
  every optional field should have a default the user can read,
  preferably with a one-line comment explaining *why* that default.

### Changed

- `anchors/PHILOSOPHY.md` §3 broadened from "Zero-config UX is the
  headline" to "Progressive disclosure with sensible, inspectable
  defaults" — the principle now spans UI, API, and architecture
  rather than just first-run UX, and explicitly names *inspectability*
  as the load-bearing second half (every default the system picks
  must be visible somewhere the user can read; no magic).
- `anchors/PHILOSOPHY.md` Anti-patterns list adds the
  inspectability-failure anti-pattern ("hide the decision in code and
  document it in the docstring") and re-frames the zero-config
  anti-pattern in the new vocabulary.
- `AGENTS.md` and `README.md` — `anchors/WORKSPACE.md` added to the
  "Read first" list as item 1; detection of workspace vs. single-repo
  is now a precondition for the rest of the toolkit's behavior.
- `agents/heddle-architect.md` — workspace-aware. Reads `WORKSPACE.md`
  in step 0 of context; the plan template gains an *App-level impact*
  section (framework changes that strand a consuming app's configs
  are half-landed); explicit workspace-relative path convention in
  output; spawn pattern handles workspace-root spawns with no specific
  starting repo named.
- `agents/heddle-invariant-guard.md` — workspace-aware. *Workspace
  context* preamble; review step 1 walks every git-controlled sibling
  in workspace mode and unions the diffs; new direction rule
  *Framework → app coherence* catches half-landed framework changes
  that don't update consuming-app configs in the same change set;
  output format gains per-repo grouping (`Repo: <name>` blocks) when
  reporting on cross-repo diffs.
- `agents/heddle-contract-reviewer.md` — workspace-aware. *Workspace
  context* preamble: looks in both `heddle/` and `heddle-sdk/`
  siblings without being asked when both are checked out; degrades
  gracefully to single-repo with a noted limitation when only one is
  available; explicit workspace-relative path convention; app-level
  siblings (e.g., `baft`) declared out of scope.
- `skills/heddle-orient/SKILL.md` — first step is now workspace
  detection; summary template has separate single-repo and workspace
  variants; `WORKSPACE.md` added to the "read deeper" table.
- `skills/heddle-preflight/SKILL.md` — workspace-aware. Workspace mode
  preflights only changed siblings by default (no wasted work on
  unchanged repos); app-level siblings handled per their own
  `AGENTS.md` (typically `<app> preflight` CLI subcommand) rather than
  guessed; output format gains per-repo blocks plus a workspace
  verdict.
- `skills/heddle-contract-sync/SKILL.md` — short preamble noting the
  skill assumes the workspace sibling layout, with the failure mode
  if `heddle-sdk/` is not checked out.

## [0.1.0] — 2026-05-15

Initial release.

### Added

- **Anchor docs** (`anchors/`):
  - `ECOSYSTEM.md` — repo map and ownership table for the `getheddle/*` family.
  - `PHILOSOPHY.md` — design opinions (solo/SMB orientation,
    privacy by default, local-first, typed contracts everywhere) and
    anti-patterns.
  - `INVARIANTS.md` — pointer to `heddle/docs/DESIGN_INVARIANTS.md` plus
    seven cross-repo invariants (C1–C7) governing the seam between
    repos: schema source of truth, byte-identical subject names,
    statelessness across languages, processor-not-LLM SDK scope,
    transport abstraction, language parity, and
    warp-design-proposes-only.
  - `CONTRACT_MAP.md` — wire-protocol schemas, NATS subjects, queue
    groups, and the workflow for evolving the contract across repos.
- **Skills** (`skills/<name>/SKILL.md`):
  - `/heddle-orient` — fast cross-repo orientation at session start.
  - `/heddle-invariants` — mid-session refresher on non-negotiable rules.
  - `/heddle-new-worker` — scaffold a worker that respects contracts.
  - `/heddle-contract-sync` — verify and update schema sync between
    `heddle` and `heddle-sdk`.
  - `/heddle-preflight` — repo-aware pre-commit verification.
  - `/warp-adr` — write or format an ADR for `warp-design`.
- **Subagents** (`agents/<name>.md`):
  - `heddle-architect` — read-only design consultant; returns
    implementation plans, not code.
  - `heddle-invariant-guard` — reviews diffs for violations of the
    eight framework red lines plus contrib→core import direction.
  - `heddle-contract-reviewer` — cross-repo wire-protocol coherence
    review (Python ↔ JSON Schema ↔ .NET ↔ Swift).
- **`install.sh`** — symlinks `skills/` and `agents/` into a target
  repo's `.claude/` using relative paths so both checkouts can move
  together. Idempotent; leaves repo-local skill/agent files alone.
- **`audits/`** — historical fresh-eyes documentation audits captured
  during the initial buildout (heddle, heddle-sdk, warp-design).

[Unreleased]: https://github.com/getheddle/heddle-workspace/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/getheddle/heddle-workspace/releases/tag/v0.1.0
