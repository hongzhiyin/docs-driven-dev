from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

from .paths import SKILL_NAME, find_source_root, path_from_env, skill_source_dir


def target_path_for(target: str) -> Path:
    direct = path_from_env(f"DOCDEV_{target.upper()}_SKILL_DIR")
    if direct is not None:
        return direct

    if target == "codex":
        home = path_from_env("DOCDEV_CODEX_HOME") or path_from_env("CODEX_HOME") or Path.home() / ".codex"
        return home / "skills" / SKILL_NAME
    if target == "cursor":
        home = path_from_env("DOCDEV_CURSOR_HOME") or Path.home() / ".cursor"
        return home / "skills" / SKILL_NAME
    if target == "agents":
        home = path_from_env("DOCDEV_AGENTS_HOME") or Path.home() / ".agents"
        return home / "skills" / SKILL_NAME
    if target == "claude":
        home = path_from_env("DOCDEV_CLAUDE_HOME") or Path.home() / ".claude"
        return home / "skills" / SKILL_NAME
    raise ValueError(f"Unknown target {target}")


def copy_skill(source: Path, target: Path, force: bool) -> str:
    if target.exists() or target.is_symlink():
        marker = target / ".docdev-skill-source" if not target.is_symlink() else None
        if not force and not (marker and marker.exists()):
            return "exists; pass --force to replace"
        if target.is_symlink() or target.is_file():
            target.unlink()
        else:
            shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)
    (target / ".docdev-skill-source").write_text(str(source) + "\n", encoding="utf-8")
    return "copied"


def parse_targets(raw: str) -> list[str]:
    aliases = {
        "all": ["codex", "cursor", "agents", "claude"],
        "default": ["codex", "cursor", "agents", "claude"],
    }
    parts = [part.strip() for part in raw.split(",") if part.strip()]
    result: list[str] = []
    for part in parts:
        expanded = aliases.get(part, [part])
        for item in expanded:
            if item not in ("codex", "cursor", "agents", "claude"):
                raise SystemExit(f"Unknown target: {item}")
            if item not in result:
                result.append(item)
    return result


def cmd_sync_skill(args: argparse.Namespace) -> int:
    source = Path(args.source).expanduser().resolve() if args.source else skill_source_dir()
    if not (source / "SKILL.md").exists():
        raise SystemExit(f"Skill source missing SKILL.md: {source}")

    targets = parse_targets(args.targets)

    print("sync target paths:")
    for target in targets:
        print(f"  {target}: {target_path_for(target)}")

    if args.dry_run:
        return 0

    for target in targets:
        status = copy_skill(source, target_path_for(target), args.force)
        print(f"{target}: {status} -> {target_path_for(target)}")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    source_root = find_source_root()
    source = skill_source_dir()
    templates = source / "templates"
    print(f"docdev source root: {source_root}")
    print(f"skill source: {source}")
    print(f"templates: {templates} ({'ok' if templates.exists() else 'missing'})")
    print(f"python: {sys.version.split()[0]}")
    for target in ("codex", "cursor", "agents", "claude"):
        path = target_path_for(target)
        state = "installed" if path.exists() or path.is_symlink() else "missing"
        if path.is_symlink():
            state += f" -> {os.readlink(path)}"
        print(f"{target}: {state} ({path})")
    return 0 if templates.exists() else 1
