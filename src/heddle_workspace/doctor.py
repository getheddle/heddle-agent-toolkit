"""`workspace doctor` — verify remote reachability and .gitignore coverage."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from heddle_workspace import git, manifest
from heddle_workspace.manifest import LOCAL_ONLY_DIR

PUBLIC_ACK_FILENAME = ".umbrella-public-ok"


def run(args: argparse.Namespace) -> int:
    root: Path = args.cwd.resolve()
    m = manifest.load(root)
    problems: list[str] = []

    # Remote reachability — ls-remote with --exit-code is the cheap check.
    for repo in m.repos:
        r = git.run(
            "ls-remote", "--exit-code", "--heads", repo.remote, repo.branch,
            check=False, capture=True,
        )
        if r.returncode != 0:
            problems.append(
                f"  unreachable: {repo.path}  ←  {repo.remote} ({repo.branch})"
            )
        else:
            print(f"  ok   {repo.path}")

    # .gitignore coverage
    gitignore = root / ".gitignore"
    expected = manifest.render_gitignore(m)
    actual = gitignore.read_text() if gitignore.exists() else ""
    if actual.strip() != expected.strip():
        problems.append(
            "  .gitignore drift: contents differ from manifest-derived render."
        )

    # Umbrella visibility: the umbrella must be private unless explicitly
    # acknowledged. Drop a marker at (local-only)/.umbrella-public-ok to ack.
    vis_problem = _check_umbrella_visibility(root, m.umbrella_remote)
    if vis_problem:
        problems.append(vis_problem)

    print()
    if problems:
        print("doctor: PROBLEMS")
        for p in problems:
            print(p)
        return 1
    print("doctor: clean.")
    return 0


def _check_umbrella_visibility(root: Path, umbrella_remote: str | None) -> str | None:
    if not umbrella_remote:
        return None
    if not shutil.which("gh"):
        print("  visibility: skipped (gh not installed)")
        return None
    slug = _slug_from_remote(umbrella_remote)
    if not slug:
        return None
    try:
        out = subprocess.run(
            ["gh", "repo", "view", slug, "--json", "visibility"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        visibility = (json.loads(out).get("visibility") or "").upper()
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        print(f"  visibility: skipped ({slug} not reachable via gh)")
        return None

    ack = (root / LOCAL_ONLY_DIR / PUBLIC_ACK_FILENAME).exists()
    if visibility == "PRIVATE":
        print(f"  ok   umbrella visibility: PRIVATE ({slug})")
        return None
    if visibility == "PUBLIC" and ack:
        print(f"  ok   umbrella visibility: PUBLIC (acknowledged via {PUBLIC_ACK_FILENAME})")
        return None
    if visibility == "PUBLIC":
        return (
            f"  umbrella is PUBLIC ({slug}). Workspaces should be private by "
            "default. Either run "
            f"`gh repo edit {slug} --visibility private`, "
            f"or acknowledge by touching `{LOCAL_ONLY_DIR}/{PUBLIC_ACK_FILENAME}`."
        )
    # Internal, etc. — treat as non-private, same path.
    return (
        f"  umbrella visibility is {visibility} ({slug}), not PRIVATE. "
        f"Set it to private or acknowledge via `{LOCAL_ONLY_DIR}/{PUBLIC_ACK_FILENAME}`."
    )


def _slug_from_remote(remote: str) -> str | None:
    if remote.startswith("git@") and ":" in remote:
        tail = remote.split(":", 1)[1]
    elif remote.startswith("https://github.com/"):
        tail = remote.removeprefix("https://github.com/")
    else:
        return None
    return tail.removesuffix(".git") or None
