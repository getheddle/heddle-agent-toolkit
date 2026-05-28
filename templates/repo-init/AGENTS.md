# AGENTS.md — {{name}} (Heddle repo)

This is the **repo-level** agent guidance for `{{name}}`, one sibling in
a [Heddle workspace](https://github.com/getheddle). It **extends** the
workspace-root `AGENTS.md` — it does not restate it. Read the root file
first for cross-repo conventions, then this file for what is specific to
`{{name}}`.

## Precedence

Context files layer from broad to narrow:

> user-level < workspace-level < repo-level < per-folder

Closer files win for the rules they state, and inherit everything they
don't state from the next level out. So this file overrides the
workspace root only where the two speak to the same rule; everywhere
else, the root still applies. (See *Context-file precedence → Nested
AGENTS.md as the natural application* in
`chat-first-project-development.md` v0.4.)

## What this repo is

One line on the repo's role in the workspace and its primary
language/runtime. *(Replace with the real description.)*

## Stack & commands

- **Language / runtime:** …
- **Package manager:** …
- **Install:** `…`
- **Test:** `…`
- **Lint / type-check:** `…`
- **Build:** `…`

## Non-obvious patterns

Repo-specific conventions an agent would otherwise get wrong — module
layout that doesn't match the obvious guess, generated files that must
not be hand-edited, a step that must run before a particular change.
Keep this short and high-signal; it is the main reason this file exists.

## Pointers

- Workspace-root `AGENTS.md` — cross-repo conventions, where artifacts
  live, the feature/maintenance split.
- `heddle-workspace/anchors/` — durable cross-repo reference
  (`PHILOSOPHY.md`, `INVARIANTS.md`, `WORKSPACE.md`, `CONTRACT_MAP.md`).
- If you are an AI agent, invoke `/heddle-orient` first.
