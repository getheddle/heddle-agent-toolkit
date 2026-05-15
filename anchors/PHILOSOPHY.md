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

### 3. Zero-config UX is the headline

`heddle setup` should "just work" on a Mac with LM Studio or Ollama
installed. `heddle workshop` should open a browser tab that lets a
non-engineer try the shipped workers. Configuration files are for
*customization*, not for *first run*.

If a feature requires the user to write a config to use it at all, ask
whether the default could be intelligent enough to skip that step.

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
  first use."** Breaks zero-config.
- **"Let's match Kubernetes idioms."** Warp explicitly rejects k8s
  ergonomics. Heddle does too.
