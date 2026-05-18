---
name: cross-repo-pr
description: Coordinate paired pull requests across `heddle` (upstream source of truth for schemas, subjects, wire protocol) and `heddle-sdk` (vendored copies in .NET + Swift). Use when a change touches `heddle/schemas/v1/*`, `heddle.core.messages`, or NATS subject names AND the downstream SDK needs a corresponding update. Walks through: contract sync, paired branches, paired PR bodies that cross-link, and the merge order that respects upstream → downstream direction.
---

# /cross-repo-pr — coordinate paired heddle ↔ heddle-sdk PRs

The Heddle family has one hard rule about cross-repo changes:

> **`heddle/` is the upstream source of truth. `heddle-sdk/` vendors
> copies of schemas, subjects, and wire-protocol facts. Downstream
> never invents; downstream syncs.**

Anchor: `heddle-workspace/anchors/CONTRACT_MAP.md`.

This skill exists because a paired PR has four ceremony steps that are
easy to forget:

1. Schema sync verification.
2. Paired branches with matching names.
3. Cross-linked PR bodies.
4. Merge order: upstream first, downstream second.

## Preconditions

- You are in a workspace (both `heddle/` and `heddle-sdk/` are
  siblings). If you're not, stop and tell the user — this skill
  doesn't operate on a lone repo. (See workspace detection in
  `heddle-workspace/anchors/WORKSPACE.md`.)
- The change touches at least one of:
  - `heddle/schemas/v1/*.schema.json`
  - `heddle/src/heddle/core/messages.py` (or the subjects helper)
  - `heddle-sdk/dotnet/src/Heddle.Sdk/Models/`
  - `heddle-sdk/swift/Sources/HeddleActor/Models/`
  - Any `Subjects` helper in either repo.

If only one side is touched and the change is wire-protocol relevant,
the **other side is the work that's missing** — call that out before
opening any PR.

## Step 1 — Run `/heddle-contract-sync`

Always invoke `/heddle-contract-sync` first. That skill verifies the
schemas, subject constants, and model fields are byte-equivalent
across the seam. If it reports drift you didn't intend, stop and
reconcile before opening PRs.

If `/heddle-contract-sync` updates files, those updates **must be in
the diff** — never open a paired PR with an unsynced downstream.

## Step 2 — Paired branches

Use **matching branch names** on both sides:

```
heddle:     feat/<topic>
heddle-sdk: feat/<topic>
```

Same `<topic>`. Reviewers can `git checkout` the same name in both
repos. If the topic name is taken on one side and not the other,
choose a new shared name rather than diverging.

## Step 3 — PR bodies that cross-link

Before either PR exists, draft both bodies. They must:

- Cross-link by URL. Each PR body's first paragraph says **"Paired
  with getheddle/<other-repo>#NNN"**. (After both are opened, edit
  each body to fill in the other's PR number.)
- State the **direction of authority** explicitly: "Schema change
  originates in `heddle/`; `heddle-sdk/` vendors the result." Even if
  obvious, this anchors reviewers.
- List the contract artifacts touched (schemas, subjects, models)
  with file paths, so a reviewer of one side can sanity-check the
  other without context-switching repos.

Use this template per side:

```markdown
## Summary

Paired with getheddle/<other-repo>#<NNN>.

**Direction:** schema/subject change originates in `heddle/`;
`heddle-sdk/` vendors the result.

### Contract artifacts touched
- `heddle/schemas/v1/<file>.schema.json`
- `heddle/src/heddle/core/messages.py` (XxxMessage)
- `heddle-sdk/dotnet/src/Heddle.Sdk/Models/Xxx.cs`
- `heddle-sdk/swift/Sources/HeddleActor/Models/Xxx.swift`

### Why
<1–3 sentences on the change motivation, not the mechanics.>

## Test plan
- [ ] /heddle-preflight in heddle/
- [ ] /heddle-preflight in heddle-sdk/
- [ ] /heddle-contract-sync reports clean
- [ ] Upstream merged before downstream
```

## Step 4 — Open both PRs, then cross-link

Open `heddle` first (upstream), then `heddle-sdk` (downstream).
Immediately after the second is created, edit the **first PR's body**
to fill in the downstream PR number. The downstream body already has
the upstream number from when you drafted it (you opened upstream
first).

Use the GitHub MCP if available (`mcp__github__*`) or `gh pr create`.
Pass the body via heredoc to preserve formatting.

## Step 5 — Merge order

**Upstream merges first.** Then re-run CI on the downstream PR
against the now-merged upstream `main`, and merge downstream second.

Never squash both simultaneously — if upstream fails after merge for
any reason and downstream is already merged, you've shipped a
downstream that references an upstream that no longer exists.

## What this skill does NOT do

- It does not invent a change for the missing side. If downstream is
  missing, surface it for human decision; don't auto-generate model
  files.
- It does not bypass `/heddle-contract-sync`. That is the only
  authoritative drift check.
- It does not push to forks or non-`getheddle` remotes. If `git
  remote -v` shows an unexpected origin, stop and ask.

## See also

- `heddle-workspace/anchors/CONTRACT_MAP.md` — wire-protocol facts
  and sync direction.
- `/heddle-contract-sync` — the drift-check skill this one wraps.
- `/heddle-preflight` — per-repo verification you run on each side
  before opening the PRs.
