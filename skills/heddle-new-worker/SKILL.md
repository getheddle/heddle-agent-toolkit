---
name: heddle-new-worker
description: Scaffold a new Heddle worker (LLM or processor) with a YAML config that respects contracts, tiers, queue groups, and the shipped scaffolding command. Use when the user asks to add a worker, classifier, extractor, or any new step type. Walks through the heddle new worker CLI and the I/O contract rules that the scaffolder won't enforce on its own.
---

# /heddle-new-worker — scaffold a worker that respects the contract

Heddle ships a `heddle new worker` CLI that interactively scaffolds a
worker config. Use it. Don't hand-write YAML when the scaffolder exists.

## Steps

1. **Run the scaffolder** from the heddle repo root (or anywhere `heddle`
   resolves):

   ```bash
   uv run heddle new worker
   ```

   The wizard asks for: name, worker type (LLM vs. processor), model tier
   (`local` / `standard` / `frontier`), input/output schema source
   (inline YAML vs. Pydantic `schema_ref`), and concurrency.

2. **Pick a tier honestly.** The default should be `local` unless the
   step genuinely requires frontier reasoning. Cost and privacy live or
   die on this choice. See `anchors/PHILOSOPHY.md` §1.

3. **Pick `schema_ref` over inline schemas when you can.** Pointing to
   a Pydantic model in `heddle.core.messages` or a worker-specific
   model file gives you typed Python on the worker side for free. Inline
   schemas are appropriate only when the worker's I/O has no Python
   counterpart.

4. **Keep schemas shallow.** Required field types at the top level. No
   nested required structures, no `$ref`, no `oneOf`. Invariant 5 in
   `DESIGN_INVARIANTS.md` makes deep schemas silently pass through; deep
   validation is the LLM's job via system-prompt instructions, not the
   contract's job.

5. **Validate**:

   ```bash
   uv run heddle validate configs/workers/your-worker.yaml
   ```

6. **Test in Workshop**:

   ```bash
   uv run heddle workshop
   # → Workers → your-worker → Test → paste input → Run
   ```

## What the scaffolder doesn't catch

- **Stateless contract.** If you write a processor with `self.cache = ...`
  in `__init__`, the scaffolder won't stop you. The runtime calls
  `reset()` between tasks — make sure your reset path tears any state down.
- **Queue group naming.** Python workers register under
  `workers-{worker_type}`. Foreign processors (via heddle-sdk) register
  under `processors-{worker_type}`. Both share the same dispatch subject
  `heddle.tasks.{worker_type}.{tier}`. If you're adding a *foreign*
  worker, use heddle-sdk, not this skill.
- **Cross-repo seam.** If your new worker's input/output uses a
  message envelope that doesn't exist yet in `heddle.core.messages`,
  you're proposing a wire-protocol change — surface that to the user and
  consider an ADR.

## Output format

Once the worker is scaffolded and validated, report:

> Worker `<name>` created at `configs/workers/<name>.yaml`.
> Tier: `<tier>`. Schemas: `<inline | schema_ref:dotted.path>`.
> Validated. Workshop preview: `uv run heddle workshop`.

If you skipped scaffolding and wrote YAML by hand, explain why.
