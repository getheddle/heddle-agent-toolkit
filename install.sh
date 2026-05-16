#!/usr/bin/env bash
# install.sh — link toolkit skills and agents into a target's .claude/
#
# Usage:
#   ./install.sh <target-repo-path>            # single-repo install
#   ./install.sh --workspace <workspace-path>  # workspace install
#
# Single-repo mode (default): creates symlinks inside
# <target>/.claude/skills/ and <target>/.claude/agents/ pointing back
# into this toolkit. The target's existing .claude/settings.json and
# .claude/commands/ are left untouched.
#
# Workspace mode (--workspace): same symlink install, plus drops a
# starter workspace-level AGENTS.md and a starter <workspace-name>.code-
# workspace file if neither exists yet. Use this when the target is a
# parent directory holding the Heddle family repos and consuming apps
# as flat siblings. See anchors/WORKSPACE.md for the convention.
#
# Idempotent: re-running replaces existing toolkit-owned symlinks but
# does not touch entries that are not toolkit symlinks. Workspace
# extras (AGENTS.md, .code-workspace) are only created when absent; an
# existing file is never overwritten.

set -euo pipefail

mode="repo"
if [[ "${1:-}" == "--workspace" ]]; then
    mode="workspace"
    shift
fi

if [[ $# -ne 1 ]]; then
    echo "usage:" >&2
    echo "  $0 <target-repo-path>            # single-repo install" >&2
    echo "  $0 --workspace <workspace-path>  # workspace install" >&2
    exit 2
fi

target="$1"
if [[ ! -d "$target" ]]; then
    echo "error: target '$target' is not a directory" >&2
    exit 1
fi

# Resolve toolkit root (directory of this script) and target to absolute paths.
toolkit_root="$(cd "$(dirname "$0")" && pwd -P)"
target_abs="$(cd "$target" && pwd -P)"

if [[ "$toolkit_root" == "$target_abs" ]]; then
    echo "error: refusing to install into self" >&2
    exit 1
fi

mkdir -p "$target_abs/.claude/skills" "$target_abs/.claude/agents"

# Compute a relative path from $1 (start dir) to $2 (target). Uses python3,
# which ships with macOS. Relative symlinks survive both checkouts moving in
# tandem (e.g., when the family is rehomed under a different parent dir).
relpath() {
    python3 -c "import os.path, sys; print(os.path.relpath(sys.argv[2], sys.argv[1]))" "$1" "$2"
}

link_dir() {
    local kind="$1"  # skills or agents
    local src_dir="$toolkit_root/$kind"
    local dst_dir="$target_abs/.claude/$kind"

    if [[ ! -d "$src_dir" ]]; then
        return 0
    fi

    for entry in "$src_dir"/*; do
        [[ -e "$entry" ]] || continue
        local name
        name="$(basename "$entry")"
        local dst="$dst_dir/$name"
        local link_target
        link_target="$(relpath "$dst_dir" "$entry")"

        if [[ -L "$dst" ]]; then
            # Existing symlink: replace if it points elsewhere, leave if same.
            local current
            current="$(readlink "$dst")"
            if [[ "$current" != "$link_target" ]]; then
                rm "$dst"
                ln -s "$link_target" "$dst"
                echo "updated: $kind/$name"
            else
                echo "ok:      $kind/$name"
            fi
        elif [[ -e "$dst" ]]; then
            echo "skip:    $kind/$name (exists, not a symlink — leaving repo-local copy)"
        else
            ln -s "$link_target" "$dst"
            echo "linked:  $kind/$name"
        fi
    done
}

install_workspace_extras() {
    local ws="$1"
    local ws_name
    ws_name="$(basename "$ws")"
    local agents_md="$ws/AGENTS.md"
    local code_ws="$ws/${ws_name}.code-workspace"

    # Workspace-level AGENTS.md (created only if absent).
    if [[ ! -e "$agents_md" ]]; then
        cat > "$agents_md" <<EOF
# AGENTS.md — $ws_name (Heddle workspace)

This directory is a **Heddle workspace** — a parent directory holding
the [getheddle/*](https://github.com/getheddle) family repositories
and one or more consuming applications as flat siblings.

## Shared agent guidance

Cross-repo invariants, philosophy, schema source-of-truth direction,
and reusable skills/subagents live in
[\`heddle-agent-toolkit/\`](heddle-agent-toolkit/). The toolkit's
skills and subagents are symlinked into this workspace's \`.claude/\`,
so any Claude Code session started at the workspace root has access
to them.

If you are an AI agent, your first step is to invoke
\`/heddle-orient\`.

## Workspace-level vs. repo-level

| Workspace root (here) | Each sibling repo |
|---|---|
| \`.claude/\` with toolkit skills + subagents | \`.claude/\` with repo-local commands |
| Cross-cutting design docs and specs that span repos | Repo-internal docs |
| This \`AGENTS.md\` | Each repo's own \`AGENTS.md\` |

For repo-specific verification commands and module layout, read the
relevant sibling's own \`AGENTS.md\`.

## VSCode

Open \`${ws_name}.code-workspace\` for a multi-root view of the
siblings.

## Convention reference

\`heddle-agent-toolkit/anchors/WORKSPACE.md\` — the technical
reference for workspace detection, cross-repo git conventions, and
path conventions.
EOF
        echo "wrote:   AGENTS.md"
    else
        echo "skip:    AGENTS.md (exists)"
    fi

    # <workspace-name>.code-workspace (created only if absent). Folders
    # list = "." first, then every immediate-child directory that is a
    # git repo. Hidden dirs and non-git dirs are skipped.
    if [[ ! -e "$code_ws" ]]; then
        local folders
        folders='    {"path": "."}'
        local entry
        for entry in "$ws"/*/; do
            [[ -d "$entry/.git" ]] || continue
            local name
            name="$(basename "$entry")"
            folders="$folders,
    {\"path\": \"$name\"}"
        done
        cat > "$code_ws" <<EOF
{
  "folders": [
$folders
  ],
  "settings": {}
}
EOF
        echo "wrote:   ${ws_name}.code-workspace"
    else
        echo "skip:    ${ws_name}.code-workspace (exists)"
    fi
}

echo "Installing heddle-agent-toolkit into $target_abs ($mode mode)"
echo "  toolkit root: $toolkit_root"
echo

link_dir skills
link_dir agents

if [[ "$mode" == "workspace" ]]; then
    install_workspace_extras "$target_abs"
fi

echo
echo "Done. Next:"
echo "  - Restart the Claude Code session in the target so it rescans .claude/."
echo "  - Try /heddle-orient to verify discovery."
