"""Tests for agent discovery adapter installation."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from heddle_workspace import agent_adapters


def test_install_links_claude_and_codex_adapters(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    codex_home = tmp_path / "codex"
    workspace.mkdir()
    (workspace / "AGENTS.md").write_text("# Agent instructions\n")

    results = agent_adapters.install(workspace, codex_home=codex_home)

    assert any(r.action == "linked" for r in results)
    assert (workspace / ".claude" / "skills" / "heddle-orient").is_symlink()
    assert (workspace / ".claude" / "agents" / "heddle-architect.md").is_symlink()
    assert (codex_home / "skills" / "heddle" / "heddle-orient").is_symlink()
    assert (workspace / ".agents" / "skills" / "heddle-orient").is_symlink()
    assert (workspace / ".cline" / "skills" / "heddle-orient").is_symlink()
    assert (workspace / ".cline" / "agents" / "heddle-architect.md").is_symlink()
    assert (workspace / ".devin" / "skills" / "heddle-orient").is_symlink()
    assert (workspace / ".qwen" / "skills" / "heddle-orient").is_symlink()
    assert (workspace / ".windsurf" / "skills" / "heddle-orient").is_symlink()
    assert (workspace / "GEMINI.md").is_symlink()
    assert (workspace / "QWEN.md").is_symlink()
    assert (workspace / ".rules").is_symlink()
    assert (workspace / ".github" / "copilot-instructions.md").is_symlink()
    assert (workspace / ".cursor" / "rules" / "heddle-workspace.mdc").is_file()
    assert (workspace / ".windsurf" / "rules" / "heddle-workspace.md").is_file()
    assert (workspace / ".cline" / "rules" / "heddle-workspace.md").is_file()
    assert (workspace / ".aider.conf.yml").is_file()

    toolkit = agent_adapters.toolkit_root()
    assert (
        workspace / ".claude" / "skills" / "heddle-orient"
    ).resolve() == (toolkit / "skills" / "heddle-orient").resolve()
    assert (
        codex_home / "skills" / "heddle" / "heddle-preflight"
    ).resolve() == (toolkit / "skills" / "heddle-preflight").resolve()
    assert (workspace / "GEMINI.md").resolve() == (workspace / "AGENTS.md").resolve()
    assert (
        "Use `AGENTS.md` as the canonical workspace instructions"
        in (workspace / ".cursor" / "rules" / "heddle-workspace.mdc").read_text()
    )
    assert "read:\n  - AGENTS.md\n" in (workspace / ".aider.conf.yml").read_text()


def test_install_is_idempotent(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    codex_home = tmp_path / "codex"
    workspace.mkdir()
    (workspace / "AGENTS.md").write_text("# Agent instructions\n")

    agent_adapters.install(workspace, codex_home=codex_home)
    second = agent_adapters.install(workspace, codex_home=codex_home)

    assert second
    assert {r.action for r in second} == {"ok"}


def test_install_skips_non_symlink_user_files(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    codex_home = tmp_path / "codex"
    local_skill = workspace / ".claude" / "skills" / "heddle-orient"
    local_skill.mkdir(parents=True)
    (workspace / "AGENTS.md").write_text("# Agent instructions\n")
    (local_skill / "SKILL.md").write_text("local copy\n")

    results = agent_adapters.install(workspace, codex_home=codex_home)

    skipped = [r for r in results if r.path == local_skill]
    assert skipped
    assert skipped[0].action == "skipped"
    assert not local_skill.is_symlink()
    assert (local_skill / "SKILL.md").read_text() == "local copy\n"


def test_index_docs_are_not_installed_as_claude_agents(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    codex_home = tmp_path / "codex"
    workspace.mkdir()
    (workspace / "AGENTS.md").write_text("# Agent instructions\n")

    agent_adapters.install(workspace, codex_home=codex_home)

    assert not (workspace / ".claude" / "agents" / "INDEX.md").exists()


def test_install_agent_adapters_shim_accepts_no_extra_args(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    codex_home = tmp_path / "codex"
    workspace.mkdir()
    (workspace / "AGENTS.md").write_text("# Agent instructions\n")

    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home)
    script = agent_adapters.toolkit_root() / "bin" / "install-agent-adapters"

    subprocess.run(
        [str(script), "--workspace", str(workspace)],
        capture_output=True,
        env=env,
        text=True,
        check=True,
    )

    assert (workspace / ".agents" / "skills" / "heddle-orient").is_symlink()
    assert (codex_home / "skills" / "heddle" / "heddle-orient").is_symlink()
