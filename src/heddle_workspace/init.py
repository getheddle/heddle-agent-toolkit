"""`workspace init` — bootstrap an umbrella in the current directory."""

from __future__ import annotations

import argparse
import shutil
import subprocess
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
    _scaffold_workflow_conventions(root, name)

    if args.no_commit:
        print("--no-commit: skipped staging and committing.")
        return 0

    if not git.is_repo(root):
        git.run("init", "-b", "main", cwd=root)
        print("initialized umbrella git repo")

    _stage_and_commit(root, m)

    if args.create_remote:
        if not umbrella_remote:
            print(
                "\n--create-remote: no umbrella_remote in manifest; "
                "re-run with --project-org or add a remote and try again."
            )
            return 1
        return _create_remote(root, name, umbrella_remote, public=args.public)

    _print_next_steps(name, umbrella_remote, public=args.public)
    return 0


def _create_remote(root: Path, name: str, umbrella_remote: str, *, public: bool) -> int:
    if not shutil.which("gh"):
        print(
            "\n--create-remote requires the GitHub CLI (`gh`). "
            "Install it from https://cli.github.com/ and re-run, "
            "or create the repo manually:"
        )
        _print_next_steps(name, umbrella_remote, public=public)
        return 1
    org = _org_from_remote(umbrella_remote)
    if not org:
        print(
            f"\n--create-remote: could not parse org from {umbrella_remote}; "
            "create the repo manually."
        )
        return 1
    visibility = "--public" if public else "--private"
    label = "PUBLIC" if public else "private"
    print()
    print(f"Creating {label} GitHub repo: {org}/{name}")
    try:
        subprocess.run(
            [
                "gh", "repo", "create", f"{org}/{name}",
                visibility, "--source=.", "--remote=origin", "--push",
            ],
            cwd=root,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        print(f"\ngh repo create failed (exit {exc.returncode}).")
        return exc.returncode
    if public:
        print()
        print(
            "Note: this umbrella was created PUBLIC by explicit request. "
            "If that was unintended, run "
            f"`gh repo edit {org}/{name} --visibility private` now."
        )
    return 0


def _ensure_local_only(root: Path) -> None:
    target = root / LOCAL_ONLY_DIR
    if not target.exists():
        target.mkdir()
        (target / ".gitkeep").write_text("")
    # Even though the dir is gitignored, we want it present so users see it.


_SCAFFOLD_FILES = {
    "AGENTS.md": "AGENTS.md",
    "roadmap/README.md": "roadmap-README.md",
    "session-starters/README.md": "session-starters-README.md",
}


def _templates_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "templates" / "workspace-init"


def _scaffold_workflow_conventions(root: Path, name: str) -> None:
    """Create roadmap/ and session-starters/ with the standard READMEs, plus
    AGENTS.md, if missing. Existing files are left untouched so re-running
    init on an established workspace is safe."""
    tdir = _templates_dir()
    for rel, template_name in _SCAFFOLD_FILES.items():
        dest = root / rel
        if dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        rendered = (tdir / template_name).read_text().replace("{{name}}", name)
        dest.write_text(rendered)
        print(f"wrote {rel}")


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
        "roadmap/README.md",
        "session-starters/README.md",
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


def _print_next_steps(
    name: str, umbrella_remote: str | None, *, public: bool = False
) -> None:
    visibility = "--public" if public else "--private"
    print()
    print("Next steps:")
    print(
        "  The umbrella holds your workspace's coordination state and "
        "(optionally) loose docs. Default visibility is PRIVATE — only "
        "pass --public if you have a specific reason and confirm it twice."
    )
    if umbrella_remote:
        org = _org_from_remote(umbrella_remote) or "<org>"
        print(f"  1. Create the GitHub repo for {name}:")
        print(
            f"     gh repo create {org}/{name} {visibility} "
            "--source=. --remote=origin"
        )
        print("  2. Push:")
        print("     git push -u origin main")
        print()
        print(
            "  Or let `workspace init --create-remote` do both for you "
            "(private by default; add --public to override)."
        )
    else:
        print(
            f"  Create the umbrella's GitHub repo (gh repo create ... {visibility}) "
            "and push."
        )
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
