"""Overlay mechanism: share untracked files across machines.

The umbrella tracks files that conceptually live inside child repos but
that the child repos themselves don't want to track (drafts, notes,
session starters, per-machine scratch). Each overlay file lives under
``overlays/<repo>/<path>`` in the umbrella; the child repo's working
tree gets a symlink pointing back into the overlay. The child repo's
``.git/info/exclude`` keeps the symlink invisible to its ``git status``.

Promotion (untracked → overlay) and demotion (overlay → untracked) are
always explicit operator actions, never automatic. ``workspace sync``
recreates the symlinks but never sweeps up new untracked files.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from heddle_workspace import git

OVERLAYS_DIRNAME = "overlays"
GIT_EXCLUDE_RELPATH = Path(".git/info/exclude")


@dataclass
class OverlayCandidate:
    """An untracked file in a child repo that could be promoted."""

    repo: str  # manifest-relative repo path, e.g. "heddle"
    path: str  # repo-relative file path, e.g. "notes/foo.md"


def overlays_root(workspace_root: Path) -> Path:
    return workspace_root / OVERLAYS_DIRNAME


def overlay_target(workspace_root: Path, repo: str, repo_relative: str) -> Path:
    """Where the overlay file lives inside the umbrella."""
    return overlays_root(workspace_root) / repo / repo_relative


def ensure_overlays_dir(workspace_root: Path) -> Path:
    p = overlays_root(workspace_root)
    p.mkdir(parents=True, exist_ok=True)
    keep = p / ".gitkeep"
    if not keep.exists() and not any(p.iterdir()):
        keep.write_text("")
    return p


def promote(workspace_root: Path, repo: str, repo_relative: str) -> Path:
    """Move a real file/dir from <repo>/<path> into the overlay; replace with symlink.

    Returns the path to the overlay file in the umbrella.
    """
    repo_dir = workspace_root / repo
    source = repo_dir / repo_relative
    if not source.exists() and not source.is_symlink():
        raise FileNotFoundError(f"no such file in {repo}: {repo_relative}")
    if source.is_symlink():
        raise ValueError(f"{repo}/{repo_relative} is already a symlink; nothing to promote")

    target = overlay_target(workspace_root, repo, repo_relative)
    if target.exists():
        raise FileExistsError(
            f"overlay already exists at overlays/{repo}/{repo_relative}; "
            "remove it first or pick a different path"
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    # Move preserves contents and (for dirs) recursively moves the tree.
    source.rename(target)
    _create_symlink(source, target)
    _add_to_git_exclude(repo_dir, repo_relative)
    return target


def demote(workspace_root: Path, repo: str, repo_relative: str) -> Path:
    """Reverse: move overlay file back into <repo> as a real file; drop symlink + exclude."""
    repo_dir = workspace_root / repo
    link = repo_dir / repo_relative
    target = overlay_target(workspace_root, repo, repo_relative)

    if not target.exists():
        raise FileNotFoundError(f"no overlay at overlays/{repo}/{repo_relative}")
    if link.exists() and not link.is_symlink():
        raise ValueError(
            f"{repo}/{repo_relative} exists as a real file alongside the overlay; "
            "this is unexpected — resolve manually before demoting"
        )
    if link.is_symlink():
        link.unlink()
    target.rename(link)
    _remove_from_git_exclude(repo_dir, repo_relative)
    return link


def apply_all(workspace_root: Path) -> tuple[int, list[str]]:
    """Walk overlays/ and ensure every entry is symlinked into its child repo.

    Returns (count_applied, warnings).
    Idempotent — re-running on a fully-synced workspace does nothing.
    """
    root_dir = overlays_root(workspace_root)
    if not root_dir.exists():
        return 0, []

    applied = 0
    warnings: list[str] = []
    for repo_dir in sorted(p for p in root_dir.iterdir() if p.is_dir()):
        repo = repo_dir.name
        child_repo = workspace_root / repo
        if not child_repo.is_dir():
            warnings.append(
                f"overlay for '{repo}' but no checked-out repo at {child_repo} "
                "— run `workspace sync` first"
            )
            continue
        for src in _walk_overlay_entries(repo_dir):
            repo_relative = src.relative_to(repo_dir).as_posix()
            link = child_repo / repo_relative
            if link.is_symlink():
                if link.resolve() == src.resolve():
                    continue  # already correct
                link.unlink()
            elif link.exists():
                warnings.append(
                    f"{repo}/{repo_relative} exists as a real file; overlay not applied "
                    "(move or remove it, then re-run sync)"
                )
                continue
            link.parent.mkdir(parents=True, exist_ok=True)
            _create_symlink(link, src)
            _add_to_git_exclude(child_repo, repo_relative)
            applied += 1
    return applied, warnings


def list_candidates(
    workspace_root: Path, repos: list[str]
) -> list[OverlayCandidate]:
    """Per child repo, find untracked files that aren't already overlay symlinks."""
    candidates: list[OverlayCandidate] = []
    for repo in repos:
        repo_dir = workspace_root / repo
        if not git.is_repo(repo_dir):
            continue
        r = git.run(
            "status", "--porcelain", "--untracked-files=normal",
            cwd=repo_dir, capture=True, check=False,
        )
        if r.returncode != 0:
            continue
        for line in r.stdout.splitlines():
            if not line.startswith("?? "):
                continue
            rel = line[3:].rstrip("/")
            link = repo_dir / rel
            if link.is_symlink():
                continue  # already an overlay
            candidates.append(OverlayCandidate(repo=repo, path=rel))
    return candidates


# --- internals ---


def _walk_overlay_entries(root: Path):
    """Yield each file in the overlay tree (recurses into directories)."""
    for p in sorted(root.rglob("*")):
        if p.name == ".gitkeep":
            continue
        if p.is_file() or p.is_symlink():
            yield p


def _create_symlink(link: Path, target: Path) -> None:
    """Create `link` pointing at `target`, using a relative path for portability."""
    link.parent.mkdir(parents=True, exist_ok=True)
    rel_target = os.path.relpath(target.resolve(), start=link.parent.resolve())
    link.symlink_to(rel_target)


def _add_to_git_exclude(repo_dir: Path, repo_relative: str) -> None:
    """Append a line to the repo's .git/info/exclude so its `git status` ignores the symlink."""
    exclude_path = repo_dir / GIT_EXCLUDE_RELPATH
    exclude_path.parent.mkdir(parents=True, exist_ok=True)
    line = f"/{repo_relative}"
    existing = exclude_path.read_text() if exclude_path.exists() else ""
    if any(stripped == line for stripped in (l.rstrip() for l in existing.splitlines())):
        return  # already excluded
    needs_newline = bool(existing) and not existing.endswith("\n")
    with exclude_path.open("a") as fh:
        if needs_newline:
            fh.write("\n")
        if not existing:
            fh.write("# heddle-workspace overlays\n")
        fh.write(line + "\n")


def _remove_from_git_exclude(repo_dir: Path, repo_relative: str) -> None:
    exclude_path = repo_dir / GIT_EXCLUDE_RELPATH
    if not exclude_path.exists():
        return
    line = f"/{repo_relative}"
    kept = [l for l in exclude_path.read_text().splitlines() if l.rstrip() != line]
    exclude_path.write_text("\n".join(kept) + ("\n" if kept else ""))
