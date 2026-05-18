# mcp/ — Heddle-family MCP server templates

Claude Code can talk to [MCP servers](https://modelcontextprotocol.io/)
for external integrations (live documentation, GitHub PR/issue access,
etc.). This directory holds a **project-scoped `.mcp.json` template**
that can be dropped into a workspace root next to `heddle/`,
`heddle-sdk/`, and consuming-app siblings. Once present, every Claude
Code session opened in the workspace inherits the configured servers.

The toolkit does not auto-install MCP servers — they're opt-in,
because `.mcp.json` lives at the workspace root (not inside the
toolkit), the right set depends on which sibling repos are checked
out, and the GitHub server reads from the host's `gh` CLI auth.

## What's in the template

| Server | Transport | Why it's here |
|---|---|---|
| `context7` | stdio (`npx -y @upstash/context7-mcp`) | Live docs lookup for Pydantic v2, `nats-py`, FastAPI, FastMCP, DuckDB, LanceDB, structlog, etc. Avoids the "trained-on-old-API" failure mode for libraries where Claude's recall is stale. No auth. |
| `github` | stdio (`sh -c "...gh auth token... npx -y @modelcontextprotocol/server-github"`) | Cross-repo PR / issue / CI / release access for `getheddle/*` repos. Token is resolved at MCP startup from `gh auth token`, so rotation is automatic and no PAT is checked in. |

### Prerequisites

- **`npx`** (Node 18+) on `PATH` — both servers spawn via npm.
- **`gh` CLI authenticated** — `gh auth status` should show a logged-in
  account before the `github` server will work. The token is read
  every time the server starts; nothing sensitive lives in the
  config file.

## Installing

Two options.

### Option A — start fresh in a workspace without `.mcp.json`

```bash
./install.sh --workspace --mcp <workspace-path>
```

This copies `mcp/.mcp.template.json` to `<workspace>/.mcp.json`
**only if no `.mcp.json` exists yet**. It will not overwrite. Can be
combined with `--hooks` to drop both templates in one pass.

### Option B — merge into an existing `.mcp.json`

`install.sh` deliberately does not merge JSON (too fragile). Copy the
`mcpServers` entries from `.mcp.template.json` into your existing
`.mcp.json` by hand. Both entries are independent — you can take one
without the other.

## After install

1. Restart any running Claude Code sessions in the workspace so they
   rescan `.mcp.json`.
2. Verify with `claude mcp list` from the workspace root — both
   servers should show `✓ Connected`. If `github` shows a failure,
   confirm `gh auth status` reports a logged-in account.
3. `.mcp.json` is project-scoped: if you check the workspace root
   into git (it isn't a repo by default in the Heddle workspace
   convention), `.mcp.json` is safe to commit — no secrets are
   embedded.

## Why these two, specifically

The `agents/pyproject-deps-reviewer.md` and
`agents/mkdocs-doc-reviewer.md` agents shipped in the toolkit benefit
materially from `context7` — they reason about library APIs and doc
toolchains where library version skew is a real issue. The
`skills/cross-repo-pr/` skill assumes `gh` CLI plus, ideally, the
GitHub MCP for richer querying than `gh` alone gives.

Other MCP servers may be useful in specific consuming repos
(database MCPs in app repos that touch a DB; Slack/Linear MCPs in
team-shared workspaces); add those at the appropriate scope. This
toolkit template is intentionally just the two that pay off for
every Heddle-family workspace.
