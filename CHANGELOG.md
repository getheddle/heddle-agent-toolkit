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

[Unreleased]: https://github.com/getheddle/heddle-agent-toolkit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/getheddle/heddle-agent-toolkit/releases/tag/v0.1.0
