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

_Nothing yet._

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
