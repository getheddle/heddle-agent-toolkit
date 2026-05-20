# Heddle Subagents Index

For the *when, why, and how* of each subagent — and how it pairs with
skills and the audit-cycle pipeline — see the workspace landing at
[`../README.md`](../README.md#tool-catalog--when-why-how).

Canonical subagent definitions live in this directory. Agent adapters
symlink these files into native discovery paths where supported (for
example `.claude/agents` and `.cline/agents`). Agents without native
subagent discovery should read the relevant file on demand when they
support delegated review or planning roles.

| Subagent | Use |
|---|---|
| [`heddle-architect`](heddle-architect.md) | Read-only design consultant before non-trivial implementation. |
| [`heddle-invariant-guard`](heddle-invariant-guard.md) | Diff reviewer for structural invariant violations. |
| [`heddle-contract-reviewer`](heddle-contract-reviewer.md) | Cross-repo wire-protocol and schema coherence reviewer. |
| [`mkdocs-doc-reviewer`](mkdocs-doc-reviewer.md) | Read-only reviewer for MkDocs documentation changes. |
| [`pyproject-deps-reviewer`](pyproject-deps-reviewer.md) | Read-only reviewer for Python dependency and lockfile changes. |
| [`audit-runner`](audit-runner.md) | Performs a typed audit (design/test-quality/contract-extract/security/deps/schema/contrib/docs/perf/invariants/data) and writes the report into `audits/<repo>-audits/`. `design` audits are checklist-driven. |
| [`maintenance-planner`](maintenance-planner.md) | **Validated.** Converts a completed audit into a `session-starters/<repo>-<topic>-<date>/` cycle subfolder; flags decision points. |
| [`maintenance-implementer`](maintenance-implementer.md) | **Validated.** Executes one lettered session from a maintenance cycle in the target sibling repo. |
| [`audit-cycle-coordinator`](audit-cycle-coordinator.md) | **Validated.** Drives the audit → plan → implement loop end-to-end; invocable interactively or on a schedule. |

Install adapters from a workspace root:

```bash
./heddle-workspace/bin/install-agent-adapters --workspace .
```
