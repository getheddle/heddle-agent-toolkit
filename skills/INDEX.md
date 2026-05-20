# Heddle Skills Index

Canonical skills live in this directory. Agent-specific discovery
surfaces should symlink here rather than copying these folders. Current
adapters include `.claude/skills`, `.agents/skills`, `.cline/skills`,
`.devin/skills`, `.qwen/skills`, `.windsurf/skills`, and Codex's
`$CODEX_HOME/skills/heddle`.

Each skill is a progressive-disclosure workflow with a
`SKILL.md` file. Coding agents that do not support skill discovery
should read only the relevant `SKILL.md` on demand.

| Skill | Use |
|---|---|
| [`heddle-orient`](heddle-orient/SKILL.md) | Start or resume work in a Heddle repo or workspace. |
| [`heddle-invariants`](heddle-invariants/SKILL.md) | Pull cross-repo invariants into context before risky changes. |
| [`heddle-contract-sync`](heddle-contract-sync/SKILL.md) | Check schema and wire-contract flow from `heddle` to `heddle-sdk`. |
| [`heddle-preflight`](heddle-preflight/SKILL.md) | Run repo-aware checks before handing off or committing. |
| [`heddle-new-worker`](heddle-new-worker/SKILL.md) | Scaffold or review a worker config that respects contracts. |
| [`cross-repo-pr`](cross-repo-pr/SKILL.md) | Coordinate paired pull requests across upstream and downstream repos. |
| [`warp-adr`](warp-adr/SKILL.md) | Create or format a `warp-design` ADR. |
| [`audit-cycle`](audit-cycle/SKILL.md) | Drive a workspace audit → maintenance-plan → implement loop. |

Install adapters from a workspace root:

```bash
./heddle-workspace/bin/install-agent-adapters --workspace .
```
