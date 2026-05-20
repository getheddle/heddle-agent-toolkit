# Audit reproducibility harness (Phase 0)

Measures how reproducible a design audit is, so the `audit-runner` body can be
hardened against a *number* instead of a hunch. Companion to
[`AUDITS.md`](AUDITS.md). Built for the audit-subsystem hardening session
(`session-starters/claude-code-instructions-audit-subsystem-hardening.md`).

## Why

The 2026-05-19 reproducibility experiment ran the same design audit of the same
unchanged `heddle.contrib.events` code twice, independently. The two runs agreed
on a stable core of ~15 findings but **each missed 4–5 major findings the other
caught — including each run's own headline finding** — and directly
contradicted each other on one correctness claim. A single open-ended audit pass
is not reproducible enough to build a pipeline on. This harness turns "not
reproducible enough" into a measured Jaccard overlap.

## Two pieces, deliberately separated

1. **Extraction** — audit prose → a normalized list of `Finding`s. This is the
   *subjective, model-driven* step, and it is the step whose reproducibility we
   are measuring. It is **not** done by this harness. Either:
   - the audit run emits a machine-readable findings block (see the prompt
     template below), or
   - a human/agent extracts findings into a `.json` array.
2. **Scoring** — `heddle_workspace.audit_repro`, exposed as
   `workspace audit-repro score`. Pure and deterministic: given normalized
   finding lists it computes pairwise Jaccard overlap (all + high-severity),
   the median + spread across all pairs, the symmetric-difference list, and a
   same-location/opposite-stance **contradiction** detector. Deterministic in →
   deterministic out, so it has a unit test and the surrounding harness can stay
   dumb.

> Location note (the brief left this to the executor): the scorer lives in the
> existing `heddle_workspace` Python package as a tested module + CLI
> subcommand, **not** a standalone `bin/audit-repro` script. Rationale: the
> workspace is already a `uv`-run Python package with a pytest suite; a tested
> module is the inspectable-but-not-a-framework option and gets CI for free. A
> bash+jq script would be more code and untested.

## Running the scorer

```bash
# strict matcher (default): file + line-window + concern key
workspace audit-repro score run-a.json run-b.json run-c.json run-d.json

# concern-only matcher: ignore file/line, match on concern key alone
workspace audit-repro score --concern-only run-a.json run-b.json
```

Each input is either a `.json` array of finding records or a Markdown report
containing a fenced ` ```findings ` JSON block.

### Finding record schema

```json
{
  "concern_key": "p3-restart-timer-loss",   // stable slug naming WHAT is wrong
  "file": "contrib/events/projectors/finalization_horizon.py",
  "line": 76,                                 // or null for module-wide findings
  "severity": "high",                         // low | medium | high
  "stance": "finding",                        // finding | ok  (ok = clean bill)
  "summary": "P3 in-memory timers lost on restart"
}
```

`concern_key` is load-bearing. Two runs that independently spotted the same
issue must be given the *same* `concern_key` for them to match — which is
exactly why extraction reproducibility, not scoring, is the open problem.
`stance: "ok"` lets a run record "I looked here and it's fine"; a matched pair
with opposite stances is a **contradiction**, counted in the union but never the
intersection.

## The matcher question (Gate 1)

The matcher strictness materially changes the number. On the run-0 baseline:

| Matcher | Stable core | Jaccard (all) | Jaccard (high) |
|---|---|---|---|
| `--concern-only` (≈ human semantic match) | 13 | **0.59** | **0.45** |
| strict `file + line + concern` (default) | 12 | **0.52** | **0.33** |

The 0.59 row reproduces the verified comparison doc's verdict exactly (13 core,
4 missed each way, 1 contradiction). The strict matcher scores *lower* because
both runs flagged "no DLQ" but cited it at different files (run-1 at
`jetstream/event_log.py`, run-2 at `dispatcher.py`) — a real artifact of
location-anchored matching, and the concrete reason Gate 1 must decide whether
`file:line` matching is good enough or a semantic matcher is needed. Either
matcher reaches the same conclusion: run-0 is far below any sane bar.

## Run-0 baseline

The before-number lives as fixtures: `tests/fixtures/audit_repro/run-1.findings.json`
and `run-2.findings.json`, faithfully extracted from the archived audits at
`(archive)/audit-subsystem-fieldtest-2026-05-19/` with the verified comparison
doc as authority. `tests/test_audit_repro.py` locks both numbers; if it ever
fails, the matcher changed, not the audits.

## Spawning blind runs (deferred to the session, not automated)

The harness scores runs; it does **not** spawn them. Producing N≥4 independent,
mutually-blind audit runs is driven **in-session by the top-level agent** via
parallel `Agent` tool calls — exactly as the run-0 experiment did — not by a
shell script shelling `claude -p`. Rationale: run-0 was produced this way, the
`audit-runner` is still a markdown file (not a registered `subagent_type`) so
Phase 0 spawns `heddle-architect` with the structured prompt below, and an
unattended CLI-spawn pattern has not been validated. Revisit `claude -p`
automation only if scheduling demands it.

Until Phase 2 ships a real `audit-runner` subagent, **state which agent produced
each run** in the harness report.

### Scratch-dir convention

Experiment runs are **not** audit artifacts. They go to a scratch dir, never to
`audits/`:

```
(local-only)/audit-repro/<topic>-<YYYY-MM-DD>/
  run-1.md   run-2.md   run-3.md   run-4.md     # each: full report + findings block
  score.txt                                      # workspace audit-repro score output
```

`(local-only)/` is untracked. The archived run-0 baseline is the only committed
reproducibility data; fresh runs stay local unless promoted deliberately.

### Blind-run prompt template

Each run must be blind to the others and to any prior audit artifact. Spawn the
auditor (`heddle-architect` for now) with:

> Perform a **design** audit of `<target>` against `<normative brief>` and
> `heddle/docs/DESIGN_INVARIANTS.md`. Do **not** open any existing audit under
> `audits/` or `(local-only)/audit-repro/`. Report findings as narrative, then
> emit a machine-readable block:
>
> ` ```findings `
> a JSON array of records `{concern_key, file, line, severity, stance, summary}`
> ` ``` `
>
> `concern_key` is a short stable slug for the issue. Use `stance:"ok"` to
> record a spot you examined and judged correct.

Phase 1 will inject the brief-contract checklist into this prompt and re-measure.
