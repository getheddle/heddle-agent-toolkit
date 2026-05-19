"""`workspace scaffold` — retro-fit the workflow conventions into an existing
workspace.

Writes any of `AGENTS.md`, `roadmap/README.md`, `session-starters/README.md`
that are missing, using the same templates as `workspace init`. Idempotent:
files that already exist are never overwritten. Does **not** stage or commit
— the user reviews the new files and commits them on their own terms.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from heddle_workspace import init, manifest


def run(args: argparse.Namespace) -> int:
    root: Path = args.cwd.resolve()
    if not manifest.manifest_path(root).exists():
        raise FileNotFoundError(
            f"no workspace manifest at {root}. "
            "Run `workspace init` first, or `workspace link <remote>`."
        )
    m = manifest.load(root)
    before = {rel: (root / rel).exists() for rel in init._SCAFFOLD_FILES}
    init._scaffold_workflow_conventions(root, m.name)
    after = {rel: (root / rel).exists() for rel in init._SCAFFOLD_FILES}

    created = [rel for rel in init._SCAFFOLD_FILES if not before[rel] and after[rel]]
    skipped = [rel for rel in init._SCAFFOLD_FILES if before[rel]]

    print()
    if created:
        print("Created:")
        for rel in created:
            print(f"  {rel}")
    if skipped:
        print("Already present (left untouched):")
        for rel in skipped:
            print(f"  {rel}")
    if created:
        print("\nReview the new files and stage them when you're satisfied.")
    return 0
