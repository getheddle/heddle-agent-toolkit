#!/usr/bin/env bash
# install.sh — link toolkit skills and agents into a target's .claude/
#
# This is the legacy Claude Code bootstrap. To install all supported
# discovery adapters for Claude, Codex, Cursor, Windsurf, Cline, and
# other coding agents, prefer:
#   ./bin/install-agent-adapters --workspace <workspace-path>
#
# Usage:
#   ./install.sh <target-repo-path>            # single-repo install
#   ./install.sh --workspace <workspace-path>  # workspace install
#   ./install.sh --hooks <target>              # also drop hooks template
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
# Hooks (--hooks): copies hooks/settings.template.json to
# <target>/.claude/settings.json ONLY if no settings.json exists. We
# never merge JSON automatically — if a settings file already exists,
# see hooks/README.md for the manual merge steps. Can be combined with
# --workspace.
#
# MCP (--mcp): copies mcp/.mcp.template.json to <target>/.mcp.json ONLY
# if no .mcp.json exists. See mcp/README.md for the manual merge steps
# when a file already exists, and for prerequisites (npx, gh CLI).
# Typically combined with --workspace since .mcp.json is most useful
# at the workspace root.
#
# Idempotent: re-running replaces existing toolkit-owned symlinks but
# does not touch entries that are not toolkit symlinks. Workspace
# extras (AGENTS.md, .code-workspace, settings.json, .mcp.json) are
# only created when absent; an existing file is never overwritten.

set -euo pipefail

mode="repo"
install_hooks=0
install_mcp=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --workspace) mode="workspace"; shift ;;
        --hooks)     install_hooks=1;   shift ;;
        --mcp)       install_mcp=1;     shift ;;
        --)          shift; break ;;
        -*)
            echo "error: unknown flag '$1'" >&2
            exit 2 ;;
        *) break ;;
    esac
done

if [[ $# -ne 1 ]]; then
    echo "usage:" >&2
    echo "  $0 <target-repo-path>            # single-repo install" >&2
    echo "  $0 --workspace <workspace-path>  # workspace install" >&2
    echo "  $0 --hooks <target>              # also drop hooks template" >&2
    echo "  $0 --mcp <target>                # also drop .mcp.json template" >&2
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

    # Workspace-level AGENTS.md (created only if absent), generated from
    # the canonical template with the workspace name substituted in. The
    # template is the single source of truth — keep content there, not here.
    local agents_template="$toolkit_root/templates/workspace-init/AGENTS.md"
    if [[ -e "$agents_md" ]]; then
        echo "skip:    AGENTS.md (exists)"
    elif [[ ! -e "$agents_template" ]]; then
        echo "skip:    AGENTS.md (template not found at $agents_template)"
    else
        sed "s|{{name}}|$ws_name|g" "$agents_template" > "$agents_md"
        echo "wrote:   AGENTS.md"
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

echo "Installing heddle-workspace into $target_abs ($mode mode)"
echo "  toolkit root: $toolkit_root"
echo

link_dir skills
link_dir agents

if [[ "$mode" == "workspace" ]]; then
    install_workspace_extras "$target_abs"
fi

if [[ "$install_hooks" == "1" ]]; then
    settings="$target_abs/.claude/settings.json"
    template="$toolkit_root/hooks/settings.template.json"
    if [[ ! -e "$template" ]]; then
        echo "skip:    hooks (template not found at $template)"
    elif [[ -e "$settings" ]]; then
        echo "skip:    settings.json (exists — see hooks/README.md to merge by hand)"
    else
        cp "$template" "$settings"
        echo "wrote:   .claude/settings.json (from hooks template)"
    fi
fi

if [[ "$install_mcp" == "1" ]]; then
    mcp_dst="$target_abs/.mcp.json"
    mcp_template="$toolkit_root/mcp/.mcp.template.json"
    if [[ ! -e "$mcp_template" ]]; then
        echo "skip:    mcp (template not found at $mcp_template)"
    elif [[ -e "$mcp_dst" ]]; then
        echo "skip:    .mcp.json (exists — see mcp/README.md to merge by hand)"
    else
        cp "$mcp_template" "$mcp_dst"
        echo "wrote:   .mcp.json (from mcp template)"
    fi
fi

echo
echo "Done. Next:"
echo "  - Restart the Claude Code session in the target so it rescans .claude/."
echo "  - Try /heddle-orient to verify discovery."
echo "  - For all coding-agent adapters, run:"
echo "    $toolkit_root/bin/install-agent-adapters --workspace $target_abs"
