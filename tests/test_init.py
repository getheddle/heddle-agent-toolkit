"""Tests for `workspace init` helpers — focused on detection edge cases."""

from __future__ import annotations

import subprocess
from pathlib import Path

from heddle_workspace import init


def _make_child_repo(repo: Path, remote: str = "https://example.com/x.git") -> None:
    repo.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    subprocess.run(
        ["git", "remote", "add", "origin", remote], cwd=repo, check=True
    )


def test_detect_skips_symlinks_to_other_repos(tmp_path: Path) -> None:
    """A symlink that resolves to an already-detected repo should be skipped.

    Without this, a backward-compat alias (e.g. heddle-agent-toolkit pointing
    at heddle-workspace during a rename window) would produce a duplicate
    manifest entry with the same remote URL.
    """
    _make_child_repo(
        tmp_path / "heddle-workspace",
        remote="https://github.com/getheddle/heddle-workspace.git",
    )
    (tmp_path / "heddle-agent-toolkit").symlink_to("heddle-workspace")

    detected = init.detect_child_repos(tmp_path)
    names = [p.name for p, _, _ in detected]

    assert "heddle-workspace" in names
    assert "heddle-agent-toolkit" not in names
    assert len(detected) == 1


def test_detect_still_picks_up_real_repos(tmp_path: Path) -> None:
    """Sanity check: the symlink filter doesn't reject ordinary repos."""
    _make_child_repo(tmp_path / "alpha", remote="https://example.com/a.git")
    _make_child_repo(tmp_path / "beta", remote="https://example.com/b.git")

    detected = init.detect_child_repos(tmp_path)
    names = sorted(p.name for p, _, _ in detected)
    assert names == ["alpha", "beta"]


def test_detect_skips_local_only_and_hidden(tmp_path: Path) -> None:
    """Carve-out and hidden dirs continue to be skipped."""
    _make_child_repo(tmp_path / "(local-only)" / "secret")
    _make_child_repo(tmp_path / ".hidden-repo")
    _make_child_repo(tmp_path / "visible")

    names = [p.name for p, _, _ in init.detect_child_repos(tmp_path)]
    assert names == ["visible"]
