"""`workspace init` — bootstrap an umbrella in the current directory."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from heddle_workspace import git, manifest, overlay, wizard
from heddle_workspace.manifest import LOCAL_ONLY_DIR, Manifest, RepoEntry


def detect_child_repos(root: Path) -> list[tuple[Path, str, str]]:
    """Return (path, remote, branch) for each immediate-child git repo with a remote.

    Hidden dirs and the `(local-only)` carve-out are skipped.
    """
    found = []
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue
        if entry.name == LOCAL_ONLY_DIR:
            continue
        if not git.is_repo(entry):
            continue
        remote = git.origin_url(entry)
        if not remote:
            continue
        branch = git.current_branch(entry) or "main"
        found.append((entry, remote, branch))
    return found


def run(args: argparse.Namespace) -> int:
    root: Path = args.cwd.resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"workspace root not found: {root}")

    existing = manifest.manifest_path(root)
    if existing.exists():
        print(f"manifest already exists at {existing}.")
        print("Use `workspace add` / `workspace rm` to edit it; init is one-shot.")
        return 1

    detected = detect_child_repos(root)

    if args.non_interactive:
        if not args.name:
            raise ValueError("--non-interactive requires --name")
        name = args.name
        umbrella_remote = (
            f"git@github.com:{args.project_org}/{name}.git" if args.project_org else None
        )
        repos = [
            RepoEntry(path=p.name, remote=r, branch=b) for (p, r, b) in detected
        ]
        description = None
    else:
        name, description, umbrella_remote, repos = wizard.run_init_wizard(
            root=root,
            detected=detected,
            default_name=args.name or root.name,
            default_project_org=args.project_org,
        )

    m = Manifest(
        name=name,
        umbrella_remote=umbrella_remote,
        description=description,
        repos=repos,
    )
    manifest_file = manifest.save(root, m)
    gitignore = root / ".gitignore"
    gitignore.write_text(manifest.render_gitignore(m))
    print(f"wrote {manifest_file.relative_to(root)}")
    print(f"wrote {gitignore.relative_to(root)}")

    _ensure_local_only(root)
    overlay.ensure_overlays_dir(root)

    if args.no_commit:
        print("--no-commit: skipped staging and committing.")
        return 0

    if not git.is_repo(root):
        git.run("init", "-b", "main", cwd=root)
        print("initialized umbrella git repo")

    _stage_and_commit(root, m)
    _print_next_steps(name, umbrella_remote)
    return 0


def _ensure_local_only(root: Path) -> None:
    target = root / LOCAL_ONLY_DIR
    if not target.exists():
        target.mkdir()
        (target / ".gitkeep").write_text("")
    # Even though the dir is gitignored, we want it present so users see it.


def _stage_and_commit(root: Path, m: Manifest) -> None:
    # Stage only the files we wrote, plus any loose root files the user wants
    # to capture. The umbrella's own commit message references the manifest.
    git.run("add", ".gitignore", manifest.MANIFEST_FILENAME, cwd=root)
    if (root / overlay.OVERLAYS_DIRNAME / ".gitkeep").exists():
        git.run("add", f"{overlay.OVERLAYS_DIRNAME}/.gitkeep", cwd=root)
    # If the user already had loose files (README, AGENTS.md, audit reports),
    # stage them too — they belong in the umbrella history.
    for fname in (
        "README.md",
        "AGENTS.md",
        "CLAUDE.md",
    ):
        p = root / fname
        if p.exists():
            git.run("add", fname, cwd=root)
    # Any *.code-workspace at root
    for ws in root.glob("*.code-workspace"):
        git.run("add", ws.name, cwd=root)
    # Audit reports
    for audit in root.glob("*AUDIT*.md"):
        git.run("add", audit.name, cwd=root)
    if (root / "AUDIT_TODO.md").exists():
        git.run("add", "AUDIT_TODO.md", cwd=root)

    msg = f"workspace init: {m.name} ({len(m.repos)} repos)"
    git.run("commit", "-m", msg, cwd=root)
    print(f"committed: {msg}")


def _print_next_steps(name: str, umbrella_remote: str | None) -> None:
    print()
    print("Next steps:")
    if umbrella_remote:
        print(f"  1. Create the private GitHub repo for {name}:")
        org = _org_from_remote(umbrella_remote)
        if org:
            print(f"     gh repo create {org}/{name} --private --source=. --remote=origin")
        else:
            print(f"     gh repo create <org>/{name} --private --source=. --remote=origin")
        print("  2. Push:")
        print("     git push -u origin main")
    else:
        print("  Create the umbrella's GitHub repo (gh repo create ... --private) and push.")
    print("  Then on another machine: `workspace link <umbrella-remote>`.")


def _org_from_remote(remote: str) -> str | None:
    # ssh-style: git@github.com:<org>/<repo>.git
    if remote.startswith("git@") and ":" in remote:
        return remote.split(":", 1)[1].split("/", 1)[0]
    # https-style: https://github.com/<org>/<repo>.git
    if remote.startswith("https://github.com/"):
        return remote.removeprefix("https://github.com/").split("/", 1)[0]
    return None


def has_uv() -> bool:
    return shutil.which("uv") is not None
