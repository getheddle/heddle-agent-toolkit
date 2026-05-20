"""`workspace add <path>` — register an existing local repo in the manifest."""

from __future__ import annotations

import argparse
from pathlib import Path

from heddle_workspace import audits, git, manifest
from heddle_workspace.manifest import LOCAL_ONLY_DIR, RepoEntry


def run(args: argparse.Namespace) -> int:
    root: Path = args.cwd.resolve()
    rel = Path(args.path)
    if rel.is_absolute():
        rel = rel.relative_to(root)
    target = root / rel
    path_str = str(rel)

    if path_str.startswith(LOCAL_ONLY_DIR):
        raise ValueError(
            f"refusing to add a repo under {LOCAL_ONLY_DIR}/ — that's the untracked carve-out."
        )
    if not target.is_dir():
        raise FileNotFoundError(f"{target} does not exist")
    if not git.is_repo(target):
        raise ValueError(f"{target} is not a git repo; cannot add to manifest")
    remote = git.origin_url(target)
    if not remote:
        raise ValueError(
            f"{target} has no `origin` remote. Set one first "
            "(`gh repo create` + `git push -u origin main`), then re-run."
        )
    branch = args.branch or git.current_branch(target) or "main"

    m = manifest.load(root)
    if m.find(path_str):
        raise ValueError(f"manifest already has an entry for {path_str}")
    m.repos.append(RepoEntry(path=path_str, remote=remote, branch=branch))
    m.repos.sort(key=lambda r: r.path)
    manifest.save(root, m)
    (root / ".gitignore").write_text(manifest.render_gitignore(m))
    print(f"added: {path_str}  ←  {remote}  ({branch})")
    for created in audits.ensure_audit_dirs(root, m):
        print(f"wrote {created.relative_to(root)}/")
    print("staged .heddle-workspace.yaml and .gitignore — review and commit.")
    return 0
