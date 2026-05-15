#!/usr/bin/env bash
# install.sh — link toolkit skills and agents into a target repo's .claude/
#
# Usage:
#   ./install.sh <target-repo-path>
#
# Creates symlinks inside <target>/.claude/skills/ and <target>/.claude/agents/
# pointing back into this toolkit. The target repo's existing
# .claude/settings.json and .claude/commands/ are left untouched.
#
# Idempotent: re-running replaces existing toolkit-owned symlinks but does
# not touch entries that are not toolkit symlinks (so repo-local agents
# and commands survive).

set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "usage: $0 <target-repo-path>" >&2
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

echo "Installing heddle-agent-toolkit into $target_abs"
echo "  toolkit root: $toolkit_root"
echo

link_dir skills
link_dir agents

echo
echo "Done. Next:"
echo "  - Restart the Claude Code session in the target repo so it rescans .claude/."
echo "  - Try /heddle-orient to verify discovery."
