# heddle-agent-toolkit

Shared AI-agent guidance, skills, and subagents for the `getheddle`
repository family ([heddle](https://github.com/getheddle/heddle),
[heddle-sdk](https://github.com/getheddle/heddle-sdk),
[warp-design](https://github.com/getheddle/warp-design), and the planned
`warp`).

This repository exists so that AI coding assistants working in any
`getheddle/*` repo:

1. **Orient fast.** One canonical set of cross-repo anchors instead of
   re-reading each project's docs from scratch.
2. **Respect invariants.** Non-negotiable design rules and the framework's
   philosophy live in one place; sibling repos point here.
3. **Stay coherent across the seam.** Schema source-of-truth direction,
   subject conventions, and wire-protocol rules are documented once.

## What's here

| Path | Contents |
|---|---|
| `AGENTS.md` | Canonical agent instructions. Read first. |
| `CLAUDE.md` | Claude-specific thin pointer to `AGENTS.md`. |
| `anchors/ECOSYSTEM.md` | Map of `getheddle/*` repos and how they relate. |
| `anchors/PHILOSOPHY.md` | Design opinions: who Heddle is for, what trade-offs are intentional. |
| `anchors/INVARIANTS.md` | Pointer to `heddle/docs/DESIGN_INVARIANTS.md` + cross-repo invariants. |
| `anchors/CONTRACT_MAP.md` | Schema source-of-truth, sync direction, wire-protocol contract. |
| `skills/<name>/SKILL.md` | User-invokable workflows (`/heddle-orient`, etc.). |
| `agents/<name>.md` | Subagent definitions (architect, reviewers). |
| `install.sh` | Symlink toolkit `skills/` and `agents/` into a target repo's `.claude/`. |

## Installing into a sibling repo

From the toolkit root:

```bash
./install.sh ../heddle
./install.sh ../heddle-sdk
./install.sh ../warp-design
```

This creates symlinks under `<target>/.claude/skills/` and
`<target>/.claude/agents/` pointing back into the toolkit. The target
repo's existing `.claude/settings.json` and any repo-specific
`.claude/commands/` are left alone.

## Status

Pre-release. Tracked alongside the get-heddle org repos but not yet
published. Once stable, this lives at `github.com/getheddle/heddle-agent-toolkit`.

## License

MPL 2.0 (matches `heddle`).
