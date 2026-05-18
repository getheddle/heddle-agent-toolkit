"""`workspace sync` — clone missing manifest entries; fetch the rest.

After cloning/fetching, the umbrella's `overlays/` tree is reapplied:
any file under `overlays/<repo>/<path>` is symlinked into the
corresponding child repo's working tree (creating directories and
.git/info/exclude entries as needed). The symlink-recreation step is
idempotent — never auto-promotes new untracked files.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from heddle_workspace import git, manifest, overlay


def run(args: argparse.Namespace) -> int:
    root: Path = args.cwd.resolve()
    m = manifest.load(root)
    cloned = 0
    fetched = 0
    skipped = 0

    for repo in m.repos:
        target = root / repo.path
        if not target.exists():
            print(f"clone  {repo.path}  ←  {repo.remote}")
            git.run(
                "clone",
                "--branch",
                repo.branch,
                repo.remote,
                str(target),
                cwd=root,
            )
            cloned += 1
            continue

        if not git.is_repo(target):
            print(f"skip   {repo.path}  (exists but not a git repo)")
            skipped += 1
            continue

        if args.fetch:
            print(f"fetch  {repo.path}")
            git.run("fetch", "origin", cwd=target, check=False)
            fetched += 1
        else:
            skipped += 1

    applied, warnings = overlay.apply_all(root)
    if applied or warnings:
        print()
        print(f"overlays: {applied} symlink(s) applied/refreshed")
        for w in warnings:
            print(f"  warning: {w}")

    print()
    print(f"sync complete: {cloned} cloned, {fetched} fetched, {skipped} skipped")
    return 0
