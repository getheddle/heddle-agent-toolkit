"""`workspace overlay add/rm` subcommands."""

from __future__ import annotations

import argparse
from pathlib import Path

from heddle_workspace import manifest, overlay


def run(args: argparse.Namespace) -> int:
    if args.overlay_command == "add":
        return _run_add(args)
    if args.overlay_command == "rm":
        return _run_rm(args)
    raise ValueError(f"unknown overlay subcommand: {args.overlay_command}")


def _run_add(args: argparse.Namespace) -> int:
    root: Path = args.cwd.resolve()
    m = manifest.load(root)
    repo, repo_relative = _split_target(root, args.target, m)
    overlay.ensure_overlays_dir(root)
    target_path = overlay.promote(root, repo, repo_relative)
    rel = target_path.relative_to(root)
    print(f"promoted: {repo}/{repo_relative}  →  {rel}")
    print("the original location is now a symlink into the overlay.")
    print(f"added '/{repo_relative}' to {repo}/.git/info/exclude (not committed).")
    print()
    print("Next: review, then commit the overlay file in the umbrella:")
    print(f"  git add {rel}")
    print("  git commit -m 'overlay: promote …'")
    return 0


def _run_rm(args: argparse.Namespace) -> int:
    root: Path = args.cwd.resolve()
    m = manifest.load(root)
    repo, repo_relative = _split_target(root, args.target, m)
    target_path = overlay.demote(root, repo, repo_relative)
    print(f"demoted: overlays/{repo}/{repo_relative}  →  {target_path.relative_to(root)}")
    print(f"removed '/{repo_relative}' from {repo}/.git/info/exclude.")
    print("the file is now a normal (untracked) file inside the child repo.")
    return 0


def _split_target(
    root: Path, target: str, m: manifest.Manifest
) -> tuple[str, str]:
    """Split '<repo>/<path>' into (repo, repo_relative), validating against manifest."""
    parts = target.split("/", 1)
    if len(parts) < 2 or not parts[1]:
        raise ValueError(
            f"target must be '<repo>/<path>', got: {target!r}"
        )
    repo, repo_relative = parts[0], parts[1]
    if not m.find(repo):
        raise ValueError(
            f"'{repo}' is not in the manifest. "
            f"Available repos: {', '.join(r.path for r in m.repos) or '(none)'}"
        )
    if not (root / repo).exists():
        raise FileNotFoundError(
            f"repo dir {repo}/ not present locally; run `workspace sync` first."
        )
    return repo, repo_relative
