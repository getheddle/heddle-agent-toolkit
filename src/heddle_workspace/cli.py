"""`workspace` CLI entry point and subcommand dispatcher."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from heddle_workspace import (
    add as cmd_add,
)
from heddle_workspace import (
    doctor as cmd_doctor,
)
from heddle_workspace import (
    init as cmd_init,
)
from heddle_workspace import (
    link as cmd_link,
)
from heddle_workspace import (
    rm as cmd_rm,
)
from heddle_workspace import (
    status as cmd_status,
)
from heddle_workspace import (
    sync as cmd_sync,
)
from heddle_workspace import (
    overlay_cmd as cmd_overlay,
)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="workspace",
        description=(
            "Workspace lifecycle CLI for Heddle-based projects. "
            "See heddle-workspace/docs/WORKSPACE_SYNC_DESIGN.md for the full spec."
        ),
    )
    p.add_argument(
        "-C",
        "--cwd",
        type=Path,
        default=Path.cwd(),
        help="workspace root (default: current directory)",
    )
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("init", help="bootstrap an umbrella in the current directory")
    s.add_argument("--name", help="workspace name (default: directory basename)")
    s.add_argument(
        "--project-org",
        help="GitHub org/user that will host the umbrella (e.g. IranTransitionProject)",
    )
    s.add_argument(
        "--non-interactive",
        action="store_true",
        help="skip the wizard; require --name (and use defaults for everything else)",
    )
    s.add_argument(
        "--no-commit",
        action="store_true",
        help="write manifest and .gitignore but don't `git add` / `git commit`",
    )
    s.set_defaults(func=cmd_init.run)

    s = sub.add_parser(
        "link", help="link a divergent local workspace to an existing umbrella remote"
    )
    s.add_argument("remote", help="umbrella remote URL")
    s.add_argument(
        "--branch", default="main", help="upstream branch to merge from (default: main)"
    )
    s.set_defaults(func=cmd_link.run)

    s = sub.add_parser("sync", help="clone any missing manifest entry; fetch the rest")
    s.add_argument(
        "--fetch/--no-fetch",
        dest="fetch",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="fetch present entries after cloning missing ones",
    )
    s.set_defaults(func=cmd_sync.run)

    s = sub.add_parser("status", help="report manifest entries vs working tree")
    s.set_defaults(func=cmd_status.run)

    s = sub.add_parser("add", help="add an existing local repo to the manifest")
    s.add_argument("path", help="path to the repo relative to the workspace root")
    s.add_argument("--branch", help="default branch (auto-detected if omitted)")
    s.set_defaults(func=cmd_add.run)

    s = sub.add_parser("rm", help="remove a manifest entry (working tree untouched)")
    s.add_argument("path")
    s.set_defaults(func=cmd_rm.run)

    s = sub.add_parser(
        "doctor", help="verify manifest remotes are reachable and .gitignore is in sync"
    )
    s.set_defaults(func=cmd_doctor.run)

    s = sub.add_parser(
        "overlay",
        help="share an untracked file inside a child repo across machines",
    )
    osub = s.add_subparsers(dest="overlay_command", required=True)

    sa = osub.add_parser(
        "add",
        help="promote an untracked file into the umbrella's overlays/ tree",
    )
    sa.add_argument(
        "target",
        help="<repo>/<path>, e.g. heddle/notes-architecture.md",
    )
    sa.set_defaults(func=cmd_overlay.run)

    sr = osub.add_parser(
        "rm",
        help="demote an overlay back to a normal (untracked) file in the child repo",
    )
    sr.add_argument(
        "target",
        help="<repo>/<path>, e.g. heddle/notes-architecture.md",
    )
    sr.set_defaults(func=cmd_overlay.run)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args) or 0
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        return 130
    except Exception as exc:  # noqa: BLE001 — surfacing to CLI is fine
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
