# Heddle Subagents Index

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
| [`audit-runner`](audit-runner.md) | Performs a typed audit (security/deps/schema/contrib/docs/perf/invariants/data) and writes the report into `audits/<repo>-audits/`. |
| [`maintenance-planner`](maintenance-planner.md) | **Stub.** Converts a completed audit into a `session-starters/<repo>-<topic>-<date>/` cycle subfolder; flags decision points. |
| [`maintenance-implementer`](maintenance-implementer.md) | **Stub.** Executes one lettered session from a maintenance cycle in the target sibling repo. |
| [`audit-cycle-coordinator`](audit-cycle-coordinator.md) | **Stub.** Drives the audit → plan → implement loop end-to-end; invocable interactively or on a schedule. |

Install adapters from a workspace root:

```bash
./heddle-workspace/bin/install-agent-adapters --workspace .
```
