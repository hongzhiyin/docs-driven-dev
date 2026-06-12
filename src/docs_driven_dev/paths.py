from __future__ import annotations

import os
from pathlib import Path

from . import __version__


DOC_NAMES = ("SPEC.md", "ARCHITECTURE.md", "ROADMAP.md", "DECISIONS.md")
CHANGE_REQUIRED_DOC_NAMES = ("SPEC.md", "ROADMAP.md", "DECISIONS.md")
CHANGE_OPTIONAL_DOC_NAMES = ("ARCHITECTURE.md",)
DEFAULT_DOCS_DIR = "docs"
GENERATED_SUBDIR = "_generated/docdev"
CHANGES_SUBDIR = "changes"
SKILL_NAME = "docs-driven-dev"
VERSION = __version__


def project_root_from_module() -> Path:
    return Path(__file__).resolve().parents[2]


def path_from_env(name: str) -> Path | None:
    raw = os.environ.get(name)
    if not raw:
        return None
    return Path(os.path.expandvars(raw)).expanduser()


def find_source_root() -> Path:
    env = os.environ.get("DOCDEV_PROJECT_DIR")
    if env:
        return Path(os.path.expandvars(env)).expanduser().resolve()

    module_root = project_root_from_module()
    if (module_root / "skill" / "SKILL.md").exists():
        return module_root

    for candidate in (
        Path.home() / "Project" / SKILL_NAME,
        Path.home() / ".agents" / "skills" / SKILL_NAME,
        Path.home() / ".codex" / "skills" / SKILL_NAME,
        Path.home() / ".cursor" / "skills" / SKILL_NAME,
    ):
        if (candidate / "SKILL.md").exists():
            return candidate
        if (candidate / "skill" / "SKILL.md").exists():
            return candidate

    return module_root


def read_config(project: Path) -> dict[str, str]:
    config_path = project / ".docdev.toml"
    config: dict[str, str] = {}
    if not config_path.exists():
        return config

    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key == "docs_dir":
            config[key] = value
    return config


def docs_dir_for(project: Path, override: str | None = None) -> Path:
    config = read_config(project)
    raw = override or config.get("docs_dir") or DEFAULT_DOCS_DIR
    return (project / raw).resolve()


def generated_dir_for(project: Path, docs_dir: Path) -> Path:
    return docs_dir / GENERATED_SUBDIR


def changes_dir_for(docs_dir: Path) -> Path:
    return docs_dir / CHANGES_SUBDIR


def skill_source_dir() -> Path:
    root = find_source_root()
    if (root / "skill" / "SKILL.md").exists():
        return root / "skill"
    return root
