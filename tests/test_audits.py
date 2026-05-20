"""Tests for `heddle_workspace.audits` — per-repo audit subfolder scaffold."""

from __future__ import annotations

from pathlib import Path

from heddle_workspace import audits
from heddle_workspace.manifest import Manifest, RepoEntry


def _manifest(*paths: str) -> Manifest:
    return Manifest(
        name="ws",
        umbrella_remote=None,
        description=None,
        repos=[
            RepoEntry(path=p, remote=f"https://example.com/{p}.git", branch="main")
            for p in paths
        ],
    )


def test_audit_dirname_strips_leading_path() -> None:
    assert audits.audit_dirname_for("heddle") == "heddle-audits"
    assert audits.audit_dirname_for("apps/foo") == "foo-audits"


def test_ensure_creates_per_repo_subfolders(tmp_path: Path) -> None:
    m = _manifest("heddle", "heddle-sdk")
    created = audits.ensure_audit_dirs(tmp_path, m)

    assert (tmp_path / "audits" / "heddle-audits" / ".gitkeep").is_file()
    assert (tmp_path / "audits" / "heddle-sdk-audits" / ".gitkeep").is_file()
    assert tmp_path / "audits" in created
    assert tmp_path / "audits" / "heddle-audits" in created


def test_ensure_is_idempotent(tmp_path: Path) -> None:
    m = _manifest("heddle")
    audits.ensure_audit_dirs(tmp_path, m)
    second = audits.ensure_audit_dirs(tmp_path, m)
    assert second == []


def test_ensure_preserves_existing_audit_files(tmp_path: Path) -> None:
    """Removing a repo from the manifest must not delete its audits, but we
    also must not clobber existing files when ensuring an unrelated repo's
    folder."""
    m = _manifest("heddle")
    audits.ensure_audit_dirs(tmp_path, m)
    existing = tmp_path / "audits" / "heddle-audits" / "old-audit-2026-01-01.md"
    existing.write_text("historical content")

    m2 = _manifest("heddle", "heddle-sdk")
    audits.ensure_audit_dirs(tmp_path, m2)

    assert existing.read_text() == "historical content"
    assert (tmp_path / "audits" / "heddle-sdk-audits").is_dir()
