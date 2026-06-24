from __future__ import annotations

import argparse
import datetime as _dt
import os
import re
import shutil
from pathlib import Path

from .paths import (
    CHANGE_OPTIONAL_DOC_NAMES,
    CHANGE_REQUIRED_DOC_NAMES,
    DOC_NAMES,
    GENERATED_SUBDIR,
    changes_dir_for,
    docs_dir_for,
    generated_dir_for,
    skill_source_dir,
)


def template_dir_for(explicit: str | None = None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()

    env = os.environ.get("DOCDEV_TEMPLATE_DIR")
    if env:
        return Path(env).expanduser().resolve()

    source = skill_source_dir()
    candidate = source / "templates"
    if candidate.exists():
        return candidate

    raise SystemExit(
        "Could not find templates. Set DOCDEV_PROJECT_DIR or pass --template-dir."
    )


def change_template_dir_for(explicit: str | None = None) -> Path:
    base = template_dir_for(explicit)
    candidate = base / "change"
    if candidate.exists():
        return candidate
    raise SystemExit(f"Could not find change templates: {candidate}")


def copy_template(name: str, docs_dir: Path, template_dir: Path, force: bool) -> bool:
    source = template_dir / name
    target = docs_dir / name
    if not source.exists():
        raise SystemExit(f"Missing template: {source}")
    if target.exists() and not force:
        return False
    shutil.copy2(source, target)
    return True


def normalize_slug(raw: str) -> str:
    slug = re.sub(r"[^\w.-]+", "-", raw.strip().lower(), flags=re.UNICODE)
    slug = re.sub(r"-{2,}", "-", slug).strip("-.")
    return slug or "change"


def ensure_readme_pointer(project: Path, docs_rel: str) -> None:
    path = project / "README.md"
    block = f"""## Documentation map

This project's source of truth lives in `{docs_rel}/`. Any code change must be
consistent with these documents; conflicts get resolved by editing the docs
first, then code.

| File | Contents |
|---|---|
| [{docs_rel}/SPEC.md]({docs_rel}/SPEC.md) | Rules, invariants, command list, default behaviour |
| [{docs_rel}/ARCHITECTURE.md]({docs_rel}/ARCHITECTURE.md) | Layers, module table, data flow, config |
| [{docs_rel}/ROADMAP.md]({docs_rel}/ROADMAP.md) | Step list, acceptance, current progress |
| [{docs_rel}/DECISIONS.md]({docs_rel}/DECISIONS.md) | D-XXX trade-off log |
"""
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if re.search(r"^##\s+Documentation\s+map\b", text, re.I | re.M):
            return
        path.write_text(text.rstrip() + "\n\n" + block, encoding="utf-8")
        return

    path.write_text(f"# {project.name}\n\n{block}", encoding="utf-8")


def ensure_agents_pointer(project: Path, docs_rel: str) -> None:
    path = project / "AGENTS.md"
    content = f"""# AGENTS.md

This project uses docs-driven development. Sources of truth live in `{docs_rel}/`.
Read `{docs_rel}/SPEC.md` first, then `{docs_rel}/ROADMAP.md` for current
progress. Update `{docs_rel}/DECISIONS.md` with a D-XXX entry whenever you make
a non-trivial trade-off, and never silently change behaviour declared in SPEC.

Generated reports belong under `{docs_rel}/{GENERATED_SUBDIR}/`, not in the
four source-of-truth documents.
"""
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if "docs-driven development" in text and GENERATED_SUBDIR in text:
            return
    path.write_text(content, encoding="utf-8")


def cmd_init(args: argparse.Namespace) -> int:
    project = Path(args.project).expanduser().resolve()
    docs_dir = docs_dir_for(project, args.docs_dir)
    docs_rel = os.path.relpath(docs_dir, project)
    templates = template_dir_for(args.template_dir)

    project.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    generated_dir_for(project, docs_dir).mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    skipped: list[str] = []
    for name in DOC_NAMES:
        if copy_template(name, docs_dir, templates, args.force):
            copied.append(name)
        else:
            skipped.append(name)

    if args.write_config:
        config_path = project / ".docdev.toml"
        if not config_path.exists() or args.force:
            config_path.write_text(f'docs_dir = "{docs_rel}"\n', encoding="utf-8")

    if not args.no_readme:
        ensure_readme_pointer(project, docs_rel)
    if not args.no_agents:
        ensure_agents_pointer(project, docs_rel)

    print(f"Initialized docs-driven project at {project}")
    if copied:
        print("Copied: " + ", ".join(copied))
    if skipped:
        print("Skipped existing: " + ", ".join(skipped))
    print(f"Generated reports dir: {docs_rel}/{GENERATED_SUBDIR}")
    return 0


def cmd_new_change(args: argparse.Namespace) -> int:
    project = Path(args.project).expanduser().resolve()
    docs_dir = docs_dir_for(project, args.docs_dir)
    templates = change_template_dir_for(args.template_dir)
    date = args.date or _dt.date.today().isoformat()
    slug = normalize_slug(args.slug)
    packet_dir = changes_dir_for(docs_dir) / f"{date}-{slug}"

    docs_dir.mkdir(parents=True, exist_ok=True)
    if packet_dir.exists() and not args.force:
        raise SystemExit(f"Change packet exists: {packet_dir}. Pass --force to refresh templates.")
    packet_dir.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    skipped: list[str] = []
    names = list(CHANGE_REQUIRED_DOC_NAMES)
    if args.with_architecture:
        names.extend(CHANGE_OPTIONAL_DOC_NAMES)

    for name in names:
        if copy_template(name, packet_dir, templates, args.force):
            copied.append(name)
        else:
            skipped.append(name)

    rel = os.path.relpath(packet_dir, project)
    print(f"Created change packet at {rel}")
    if copied:
        print("Copied: " + ", ".join(copied))
    if skipped:
        print("Skipped existing: " + ", ".join(skipped))
    if not args.with_architecture:
        print("ARCHITECTURE.md omitted; keep the ROADMAP omission reason current.")
    return 0
