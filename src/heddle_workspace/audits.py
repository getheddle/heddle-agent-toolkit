"""Per-repo audit subfolder maintenance.

Each repo in the manifest gets an `audits/<repo>-audits/` subfolder with
a `.gitkeep`. Created lazily by `workspace init` / `workspace add`;
never removed by `workspace rm` because audits are historical artifacts.

See `<workspace>/audits/README.md` and
`heddle-workspace/docs/AUDITS.md` for the convention.
"""

from __future__ import annotations

from pathlib import Path

from heddle_workspace.manifest import Manifest

AUDITS_DIRNAME = "audits"


def audit_dirname_for(repo_path: str) -> str:
    """`heddle` → `heddle-audits`. `apps/foo` → `foo-audits`."""
    leaf = Path(repo_path).name
    return f"{leaf}-audits"


def ensure_audit_dirs(root: Path, manifest: Manifest) -> list[Path]:
    """Create `audits/<repo>-audits/` for each repo in the manifest.

    Idempotent — existing dirs and files are left untouched. Returns the
    paths that were newly created (for the caller to print or stage).
    """
    audits_root = root / AUDITS_DIRNAME
    created: list[Path] = []
    if not audits_root.exists():
        audits_root.mkdir()
        created.append(audits_root)
    for entry in manifest.repos:
        sub = audits_root / audit_dirname_for(entry.path)
        if sub.exists():
            continue
        sub.mkdir(parents=True)
        (sub / ".gitkeep").write_text("")
        created.append(sub)
    return created
