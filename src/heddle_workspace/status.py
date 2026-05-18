"""`workspace status` — read-only report on the workspace state."""

from __future__ import annotations

import argparse
from pathlib import Path

from heddle_workspace import git, manifest, overlay
from heddle_workspace.manifest import LOCAL_ONLY_DIR


def run(args: argparse.Namespace) -> int:
    root: Path = args.cwd.resolve()
    m = manifest.load(root)

    print(f"workspace: {m.name}")
    if m.umbrella_remote:
        print(f"umbrella:  {m.umbrella_remote}")
    print()

    print("manifest entries:")
    if not m.repos:
        print("  (none)")
    manifest_paths: set[str] = set()
    for repo in m.repos:
        manifest_paths.add(repo.path)
        target = root / repo.path
        if not target.exists():
            print(f"  MISSING  {repo.path}  (not cloned yet — run `workspace sync`)")
            continue
        if not git.is_repo(target):
            print(f"  ORPHAN   {repo.path}  (exists but not a git repo)")
            continue
        branch = git.current_branch(target) or "?"
        clean = "clean" if git.is_clean(target) else "DIRTY"
        ab = git.ahead_behind(target, repo.branch)
        ab_str = f"  ↑{ab[0]} ↓{ab[1]}" if ab else "  (no upstream)"
        flag = "  " if branch == repo.branch else " *"
        print(f"{flag}{clean:6} {repo.path:30}  {branch}{ab_str}")

    # Orphan child repos: present, are git repos, but not in the manifest.
    print()
    print("orphans (git repos at workspace root not in the manifest):")
    orphans_found = False
    for entry in sorted(root.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        if entry.name == LOCAL_ONLY_DIR:
            continue
        if entry.name in manifest_paths:
            continue
        if git.is_repo(entry):
            remote = git.origin_url(entry) or "(no remote)"
            print(f"  {entry.name}  ← {remote}")
            orphans_found = True
    if not orphans_found:
        print("  (none)")

    # Overlay candidates: untracked files inside child repos that could be
    # promoted into the umbrella overlay tree.
    candidates = overlay.list_candidates(
        root, [r.path for r in m.repos]
    )
    if candidates:
        print()
        print("overlay candidates (untracked in child, not yet shared):")
        by_repo: dict[str, list[str]] = {}
        for c in candidates:
            by_repo.setdefault(c.repo, []).append(c.path)
        for repo, paths in by_repo.items():
            print(f"  {repo}: {len(paths)} untracked file(s)")
            for p in paths[:5]:
                print(f"    {p}")
            if len(paths) > 5:
                print(f"    … and {len(paths) - 5} more")
        print("  Run `workspace overlay add <repo>/<path>` to share.")

    return 0
