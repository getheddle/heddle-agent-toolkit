# CLAUDE.md — heddle-workspace

Claude-specific notes. The canonical agent instructions live in
[`AGENTS.md`](AGENTS.md) — read that first.

## Claude-specific notes

- When session history is missing or compacted, re-orient from
  `anchors/ECOSYSTEM.md` and the active repo's `AGENTS.md`. Both should
  fit on one screen each.
- Prefer invoking `/heddle-orient` to silently re-reading anchor docs —
  it's tuned for cheap context entry.
- For non-trivial changes, spawn the `heddle-architect` subagent before
  writing code. It carries the design context in isolated context, so
  the top-level conversation stays uncluttered.

If this file ever conflicts with `AGENTS.md`, follow `AGENTS.md` and the
current user request.
