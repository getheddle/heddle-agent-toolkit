# Philosophy — what Heddle is for and what trade-offs are intentional

These are design opinions, not invariants. They explain *why* the codebase
looks the way it does. If a proposed change pulls against one of these, the
change probably needs more thought, not a quick implementation.

## Who Heddle is for

**Solo operators, small teams, and small businesses** — not platform teams
with Kubernetes administrators. The headline user is someone who can
install a CLI, edit a YAML file, and run a workflow in a browser — and who
either has a small fleet of personal machines or rents modest cloud
capacity.

Heddle is *not* aimed at the hyperscaler-internal use case. The architecture
borrows hyperscaler *concepts* (queue groups, stateless workers,
deterministic routing) but rejects hyperscaler *ergonomics* (sprawling
control planes, ops teams, homogeneous fleets).

This shapes every decision below.

## The deliberate trade-offs

### 1. On-prem and local-first, with cloud as an option

Local model backends (LM Studio, Ollama) are first-class citizens, not
fallbacks. The first thing `heddle setup` does is auto-detect them. The
three-tier model selector (`local` / `standard` / `frontier`) exists so
that cost and privacy can be reasoned about per-step, not per-system.

If a new feature would *only* work with a paid frontier API, that's a
warning sign. Local should be a viable path.

### 2. Privacy as a default property, not a feature flag

The local tier exists so that private workloads never leave the user's
machines. Knowledge silos and blind audit patterns ensure that a model
reviewing work cannot see the work it produced. These are not opt-in
hardening — they are the default shape of the framework.

If your change quietly routes private data to a remote provider, it
violates this. Even logging into a hosted telemetry service for private
workloads is suspect.

### 3. Progressive disclosure with sensible, inspectable defaults

The system works out of the box for the common case, reveals
complexity only when the user reaches for it, and never hides what it
has decided on the user's behalf. This applies across UI, API, and
architecture — not just first-run UX.

- **UI.** `heddle setup` auto-detects backends and writes a working
  config without asking. `heddle workshop` opens a browser tab and
  runs the shipped workers with no prior configuration. The three
  usage paths — Workshop, guided CLI scaffolding, distributed
  deployment — disclose complexity in that order. A user can reach a
  result on path 1 without ever seeing paths 2 or 3.
- **API.** Worker base classes work with no arguments for the common
  case and accept progressively-typed configuration for advanced use.
  Typed Pydantic messages mean optional fields stay invisible until
  someone needs them; required fields surface with type errors at the
  point of use.
- **Architecture.** `InMemoryBus` runs in-process for tests and small
  deployments — same interface, same semantics, no external broker.
  `NATSBus` is the production substitute. Custom transports plug in
  without touching higher layers. Three model tiers (local / standard
  / frontier) let a workflow start fully local and grow into hybrid
  deployment one step at a time.
- **Inspectability — the half that's easy to forget.** Every default
  must be visible somewhere. `heddle config show` prints the active
  configuration with provenance. `heddle validate` surfaces what each
  worker's contract actually requires. The setup wizard writes its
  decisions to `~/.heddle/config.yaml` where the user can read and
  edit them. Worker YAMLs are the source of truth for I/O schemas —
  no hidden conventions. There is no "magic" that the user can't see
  after the fact.

The two halves are both load-bearing. A feature that requires the
user to choose something before first use violates the *sensible
defaults* half. A feature whose behaviour can't be inspected after
the fact violates the *inspectability* half — even if the defaults
are great. Both fail the test.

When proposing a new feature: if it requires a config file before
first use, ask whether a sensible default could remove the step. If
its behaviour depends on internal state the user can't query, surface
that state through a CLI command, a Workshop view, or a written
config artefact.

### 4. Workshop is the design surface, not the auxiliary

Workshop (the web UI) is where workers are tested, evaluated, and
iterated. CLI is for scripting; production workflows run via the NATS
bus. The order of UX priority is:

1. Workshop (interactive iteration)
2. CLI (automation)
3. Distributed deploy (scale)

Features that work in the CLI but can't be exercised in Workshop are
incomplete.

### 5. Stateless workers, deterministic router

This is also an invariant (see `INVARIANTS.md`), but it is *philosophy*
because it shapes everything: operational simplicity, horizontal scaling
without coordination, auditability, fast and predictable dispatch. The
cost is that workers can't optimize across tasks. The benefit is that
the whole system stays comprehensible to one operator.

We accept the cost intentionally. Don't add "smart" caching, batching,
or cross-task optimization that breaks the contract.

### 6. Typed contracts are the safety net

Pydantic messages and per-worker I/O schemas are the only thing standing
between two actors. There is no shared state to coordinate through, no
distributed tracing to reconstruct from. If contracts get sloppy —
untyped dicts, missing schemas, deep nested structures the LLM can't
satisfy — the system silently produces wrong results.

This is why the Python repo owns the schema source of truth and why
foreign SDKs vendor rather than redefine.

### 7. Apple Silicon is the right *personal* substrate

Apple Silicon optimizes for *best computer per user*: unified memory,
heterogeneous accelerators, tight HW/SW integration, privacy primitives
in the OS. Hyperscaler chips optimize for *cheapest compute per workload*.
They aren't competing axes — both exist because they solve different
problems.

This is why warp starts macOS-first (and why it will eventually grow a
Linux agent for Jetsons and traditional servers). It is not parochialism.
It is starting where the personal-compute story is sharpest.

### 8. Documentation quality is non-negotiable

The README, CONCEPTS, and getting-started docs are the first thing
operators see. They must be accurate, current, and free of broken links.
Sibling repos must feel like extensions of `heddle`, not separate
products with their own conventions.

If you change behavior, update the docs in the same PR. If you can't,
the change isn't ready.

**Behaviour changes also require a `CHANGELOG.md` entry.** Each
released-artifact-producing repo in the family (`heddle`,
`heddle-sdk`, `heddle-workspace`) maintains a
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) at its root.
Adding, changing, deprecating, removing, or fixing user-facing
behaviour requires an entry under `[Unreleased]` in the relevant
repo. Documentation-only changes, internal refactors with no
behavioural delta, and CI-only commits are exempt. `warp-design` uses
`EVOLUTION_LOG.md` and numbered ADRs in `decisions/` for the same
purpose, since it produces no released artifacts.

### 9. License: MPL 2.0, intentionally

Modified source files must remain open. Unmodified files can be combined
with proprietary code. This lets organizations adopt Heddle without
copyleft constraints contaminating their proprietary modules, while
ensuring improvements to Heddle itself stay open.

Don't propose re-licensing under MIT/Apache (loses the protection) or
under GPL (loses the practical adoptability). The choice is deliberate.

## Anti-patterns

Things that look reasonable on the surface but conflict with the
philosophy above:

- **"Let's add a managed-cloud control plane."** Defeats the
  on-prem-first stance and adds a third party to the privacy story.
- **"Let's smart-route via an LLM."** Breaks deterministic routing.
- **"Let's let workers cache across tasks for performance."** Breaks
  statelessness; corrupts horizontal scaling.
- **"Let's accept any dict as a payload and validate later."** Removes
  the only safety net.
- **"Let's optimize for the 1000-engineer use case."** Wrong audience.
  Heddle is solo/SMB-first; cross-organization scale is a non-goal of v1.
- **"Let's add a feature that requires writing a config file before
  first use."** Breaks the sensible-defaults half of progressive
  disclosure.
- **"Let's hide the decision in code and document it in the docstring."**
  Breaks the inspectability half of progressive disclosure. If a user
  has to read source to learn what the system chose, the system has
  failed them.
- **"Let's match Kubernetes idioms."** Warp explicitly rejects k8s
  ergonomics. Heddle does too.
