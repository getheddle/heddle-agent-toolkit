"""Tests for the overlay mechanism."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from heddle_workspace import overlay


def _make_child_repo(repo: Path) -> None:
    repo.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)


def test_promote_then_demote_round_trip(tmp_path: Path) -> None:
    repo = tmp_path / "heddle"
    _make_child_repo(repo)
    f = repo / "notes.md"
    f.write_text("hello\n")

    target = overlay.promote(tmp_path, "heddle", "notes.md")

    # File moved into the overlay
    assert target == tmp_path / "overlays" / "heddle" / "notes.md"
    assert target.read_text() == "hello\n"

    # Child-repo path is now a symlink to the overlay
    link = repo / "notes.md"
    assert link.is_symlink()
    assert link.resolve() == target.resolve()

    # The child repo's .git/info/exclude now hides the path
    exclude = (repo / ".git" / "info" / "exclude").read_text()
    assert "/notes.md" in exclude

    # `git status` inside the child reports clean (the symlink is excluded)
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo, capture_output=True, text=True, check=True,
    )
    assert r.stdout.strip() == ""

    # Demote reverses everything
    overlay.demote(tmp_path, "heddle", "notes.md")
    assert not target.exists()
    assert not link.is_symlink()
    assert link.is_file()
    assert link.read_text() == "hello\n"
    exclude_after = (repo / ".git" / "info" / "exclude").read_text()
    assert "/notes.md" not in exclude_after


def test_promote_refuses_missing_file(tmp_path: Path) -> None:
    _make_child_repo(tmp_path / "heddle")
    with pytest.raises(FileNotFoundError):
        overlay.promote(tmp_path, "heddle", "does-not-exist.md")


def test_promote_refuses_existing_symlink(tmp_path: Path) -> None:
    repo = tmp_path / "heddle"
    _make_child_repo(repo)
    (repo / "real.md").write_text("x")
    (repo / "link.md").symlink_to("real.md")
    with pytest.raises(ValueError, match="symlink"):
        overlay.promote(tmp_path, "heddle", "link.md")


def test_promote_refuses_overlay_collision(tmp_path: Path) -> None:
    repo = tmp_path / "heddle"
    _make_child_repo(repo)
    (repo / "notes.md").write_text("first")
    overlay.promote(tmp_path, "heddle", "notes.md")
    # Create a fresh notes.md in the child (the original was moved)
    (repo / "notes.md").unlink()  # remove the symlink
    (repo / "notes.md").write_text("second")
    with pytest.raises(FileExistsError):
        overlay.promote(tmp_path, "heddle", "notes.md")


def test_apply_all_is_idempotent(tmp_path: Path) -> None:
    repo = tmp_path / "heddle"
    _make_child_repo(repo)
    (repo / "notes.md").write_text("hello")
    overlay.promote(tmp_path, "heddle", "notes.md")

    applied1, warnings1 = overlay.apply_all(tmp_path)
    applied2, warnings2 = overlay.apply_all(tmp_path)
    assert warnings1 == [] and warnings2 == []
    # First call may apply 0 (already symlinked from promote()), second is also 0.
    assert applied2 == 0


def test_apply_all_warns_on_missing_child_repo(tmp_path: Path) -> None:
    # Create an overlay file for a repo that hasn't been cloned yet.
    overlays = tmp_path / "overlays" / "ghost"
    overlays.mkdir(parents=True)
    (overlays / "notes.md").write_text("orphan")

    _, warnings = overlay.apply_all(tmp_path)
    assert any("ghost" in w for w in warnings)


def test_apply_all_warns_on_real_file_collision(tmp_path: Path) -> None:
    repo = tmp_path / "heddle"
    _make_child_repo(repo)
    overlay_file = tmp_path / "overlays" / "heddle" / "notes.md"
    overlay_file.parent.mkdir(parents=True)
    overlay_file.write_text("overlay-content")

    # A real file at the child path blocks symlinking
    (repo / "notes.md").write_text("real-content")

    _, warnings = overlay.apply_all(tmp_path)
    assert any("notes.md" in w and "real file" in w for w in warnings)


def test_apply_all_replaces_stale_symlink(tmp_path: Path) -> None:
    repo = tmp_path / "heddle"
    _make_child_repo(repo)
    overlay_file = tmp_path / "overlays" / "heddle" / "notes.md"
    overlay_file.parent.mkdir(parents=True)
    overlay_file.write_text("overlay-content")

    # Pre-existing symlink pointing somewhere else
    (repo / "notes.md").symlink_to("/tmp/does-not-exist")

    applied, warnings = overlay.apply_all(tmp_path)
    assert warnings == []
    assert applied == 1
    assert (repo / "notes.md").resolve() == overlay_file.resolve()


def test_list_candidates_excludes_existing_symlinks(tmp_path: Path) -> None:
    repo = tmp_path / "heddle"
    _make_child_repo(repo)
    (repo / "promoted.md").write_text("x")
    (repo / "still-untracked.md").write_text("y")
    overlay.promote(tmp_path, "heddle", "promoted.md")

    cands = overlay.list_candidates(tmp_path, ["heddle"])
    paths = {c.path for c in cands}
    assert "still-untracked.md" in paths
    assert "promoted.md" not in paths
