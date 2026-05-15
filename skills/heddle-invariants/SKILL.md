---
name: heddle-invariants
description: Mid-session refresher of Heddle's non-negotiable design invariants. Use when you're about to make a structural change to heddle/, when reviewing a diff that touches workers/router/orchestrator/bus, or when a long session has drifted and you want to recenter on the framework's red lines before continuing. Loads the cross-repo summary and points to canonical detail.
---

# /heddle-invariants — recenter on the rules that don't bend

Use this mid-session when you're about to make a structural change, or
when something feels off and you suspect the conversation has drifted
away from Heddle's design contracts.

## Eight framework red lines (heddle Python)

1. **No LLM in the router.** Deterministic routing by `worker_type` +
   `model_tier`. The decomposer chose the worker; the router delivers.
2. **No state between worker tasks.** `reset()` is unconditional. Replicas
   in a queue group are interchangeable.
3. **No skipping contract validation.** Shallow JSON Schema validation in
   `contracts.py` is the only safety net between actors.
4. **No flipping condition-eval defaults to TRUE.** Malformed / missing /
   unknown operator → FALSE (skip). Silent over-execution is worse than
   visible skip + warning.
5. **No multi-instance `serialize_writes=True` processors.** The lock is
   per-instance only. DuckDB and similar single-writer stores need
   exactly one processor.
6. **No publish before subscribe** for request-reply over NATS. Use
   `heddle.orchestrator.dispatch.dispatch_and_wait_for_result`.
7. **No leaking full transcripts to all council agents.**
   `sees_transcript_from` is a security boundary, not a hint.
8. **No transcript mutation by convergence detectors.** Detection is
   observation, not intervention.

Full detail with the *why* and *how it fails* for each, plus 13 more
framework invariants:
**[`heddle/docs/DESIGN_INVARIANTS.md`](https://github.com/getheddle/heddle/blob/main/docs/DESIGN_INVARIANTS.md)**

## Seven cross-repo invariants (the seam between repos)

1. **C1.** Schema source of truth lives in `heddle/`. Other repos vendor.
2. **C2.** Subject names and queue groups are byte-identical across
   languages.
3. **C3.** Workers are stateless in every language SDK too.
4. **C4.** Foreign workers are processor workers, not LLM workers.
5. **C5.** Core SDK packages stay transport-abstract.
6. **C6.** Language parity in heddle-sdk unless explicitly
   language-specific.
7. **C7.** warp-design ADRs propose; the implementation goes through
   upstream PRs.

Full detail:
[`anchors/INVARIANTS.md`](../../anchors/INVARIANTS.md).

## Two architectural direction rules

- **`core` and `worker` may not import from `contrib`.** The allowed
  direction is contrib → core. The other way is a violation.
- **Tests use `InMemoryBus` by default.** Tests that touch `NATSBus`
  must carry `@pytest.mark.integration`.

## Two philosophy guardrails that drift fast

These aren't mechanically enforced but they're the most common direction
of drift:

- **Solo / SMB / on-prem orientation.** If your design implicitly assumes
  a platform team or a Kubernetes operator, you've drifted.
- **Privacy by default via the local tier.** If you're routing private
  data to a remote provider for any reason, you've drifted.

## What to do now

State which invariants are relevant to the work in front of you and
proceed. If a proposed change pulls against one of them, surface that to
the user *before* implementing.
