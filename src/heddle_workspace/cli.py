"""`workspace` CLI entry point and subcommand dispatcher."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from heddle_workspace import (
    add as cmd_add,
)
from heddle_workspace import (
    agent_adapters as cmd_agent_adapters,
)
from heddle_workspace import (
    audit_repro as cmd_audit_repro,
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
    machine as cmd_machine,
)
from heddle_workspace import (
    overlay_cmd as cmd_overlay,
)
from heddle_workspace import (
    rm as cmd_rm,
)
from heddle_workspace import (
    scaffold as cmd_scaffold,
)
from heddle_workspace import (
    status as cmd_status,
)
from heddle_workspace import (
    sync as cmd_sync,
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
    s.add_argument(
        "--create-remote",
        action="store_true",
        help=(
            "after committing, run `gh repo create` for the umbrella. "
            "Default visibility is PRIVATE; pass --public to override."
        ),
    )
    s.add_argument(
        "--public",
        action="store_true",
        help=(
            "with --create-remote, create the umbrella as a PUBLIC repo. "
            "Must be requested explicitly; private is the default."
        ),
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

    s = sub.add_parser(
        "machine",
        help="manage the per-machine profile in (local-only)/machine.yaml",
    )
    msub = s.add_subparsers(dest="machine_command", required=True)
    mi = msub.add_parser(
        "init",
        help="create an annotated machine.yaml if missing (pre-filled from the local shell)",
    )
    mi.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing machine.yaml",
    )
    mi.set_defaults(func=cmd_machine.run)

    s = sub.add_parser(
        "scaffold",
        help=(
            "retro-fit the workflow conventions (AGENTS.md, roadmap/, "
            "session-starters/) into an existing workspace. Idempotent: "
            "existing files are left untouched. Does not stage or commit."
        ),
    )
    s.set_defaults(func=cmd_scaffold.run)

    s = sub.add_parser(
        "audit-repro",
        help="measure audit reproducibility (Phase 0 of audit-subsystem hardening)",
    )
    arsub = s.add_subparsers(dest="audit_repro_command", required=True)
    ars = arsub.add_parser(
        "score",
        help="score finding overlap across N>=2 audit runs (JSON or report files)",
    )
    ars.add_argument(
        "findings",
        nargs="+",
        help="paths to N>=2 finding files (.json array or .md with a ```findings block)",
    )
    ars.add_argument(
        "--line-window",
        type=int,
        default=cmd_audit_repro.DEFAULT_LINE_WINDOW,
        help=f"line tolerance when matching (default: {cmd_audit_repro.DEFAULT_LINE_WINDOW})",
    )
    ars.add_argument(
        "--concern-only",
        action="store_true",
        help="match on concern key alone (ignore file/line); closer to a human "
        "semantic match, looser than the default file+line+concern matcher",
    )
    ars.set_defaults(func=cmd_audit_repro.run)

    s = sub.add_parser(
        "agent-adapters",
        help="install coding-agent discovery adapters for toolkit skills",
    )
    aasub = s.add_subparsers(dest="agent_adapters_command", required=True)
    ai = aasub.add_parser(
        "install",
        help="symlink canonical skills/agents into agent-specific discovery paths",
    )
    ai.add_argument(
        "--agents-standard",
        dest="agents_standard",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="install shared .agents/skills adapters",
    )
    ai.add_argument(
        "--aider",
        dest="aider",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="install .aider.conf.yml read-only AGENTS.md adapter",
    )
    ai.add_argument(
        "--cline",
        dest="cline",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="install .cline rules, skills, and agents adapters",
    )
    ai.add_argument(
        "--claude",
        dest="claude",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="install .claude/skills and .claude/agents adapters",
    )
    ai.add_argument(
        "--codex",
        dest="codex",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="install Codex skills under $CODEX_HOME/skills/heddle",
    )
    ai.add_argument(
        "--copilot",
        dest="copilot",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="install .github/copilot-instructions.md adapter",
    )
    ai.add_argument(
        "--cursor",
        dest="cursor",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="install .cursor/rules adapter",
    )
    ai.add_argument(
        "--devin",
        dest="devin",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="install .devin/skills adapters",
    )
    ai.add_argument(
        "--gemini",
        dest="gemini",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="install GEMINI.md adapter",
    )
    ai.add_argument(
        "--qwen",
        dest="qwen",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="install QWEN.md and .qwen/skills adapters",
    )
    ai.add_argument(
        "--windsurf",
        dest="windsurf",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="install .windsurf rules and skills adapters",
    )
    ai.add_argument(
        "--zed",
        dest="zed",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="install .rules adapter for Zed",
    )
    ai.add_argument(
        "--codex-home",
        type=Path,
        help="override Codex home directory (default: $CODEX_HOME or ~/.codex)",
    )
    ai.set_defaults(func=cmd_agent_adapters.run)

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
