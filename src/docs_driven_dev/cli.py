from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DOC_NAMES = ("SPEC.md", "ARCHITECTURE.md", "ROADMAP.md", "DECISIONS.md")
CHANGE_REQUIRED_DOC_NAMES = ("SPEC.md", "ROADMAP.md", "DECISIONS.md")
CHANGE_OPTIONAL_DOC_NAMES = ("ARCHITECTURE.md",)
DEFAULT_DOCS_DIR = "docs"
GENERATED_SUBDIR = "_generated/docdev"
CHANGES_SUBDIR = "changes"
SKILL_NAME = "docs-driven-dev"
VERSION = "0.1.4"


@dataclass
class Finding:
    level: str
    message: str
    path: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        return {"level": self.level, "message": self.message, "path": self.path}


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


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
        Path.home() / "Project" / "docs-driven-dev",
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


def change_template_dir_for(lang: str, explicit: str | None = None) -> Path:
    base = template_dir_for(explicit)
    candidate = base / "change" / lang
    if candidate.exists():
        return candidate
    raise SystemExit(f"Could not find change templates for language {lang}: {candidate}")


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
    templates = change_template_dir_for(args.lang, args.template_dir)
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


def extract_decision_ids(text: str) -> list[int]:
    return [int(match.group(1)) for match in re.finditer(r"^##\s+D-(\d{3})\b", text, re.M)]


def roadmap_step_sections(text: str) -> list[tuple[str, str]]:
    headings = list(re.finditer(r"^(##+)\s+(Step\s+\d[^\n]+)", text, re.M))
    sections: list[tuple[str, str]] = []
    for idx, match in enumerate(headings):
        start = match.end()
        end = headings[idx + 1].start() if idx + 1 < len(headings) else len(text)
        sections.append((match.group(2), text[start:end]))
    return sections


def markdown_cells(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def markdown_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def docs_rel_for_markdown(project: Path, docs_dir: Path) -> str:
    return os.path.relpath(docs_dir.resolve(), project.resolve()).replace(os.sep, "/")


def audit_readme_documentation_map(project: Path, docs_dir: Path) -> list[Finding]:
    path = project / "README.md"
    if not path.exists():
        return []

    findings: list[Finding] = []
    text = path.read_text(encoding="utf-8")
    if not re.search(r"^##\s+Documentation\s+map\b", text, re.I | re.M):
        findings.append(Finding("warn", "README.md has no Documentation Map section", str(path)))

    docs_rel = docs_rel_for_markdown(project, docs_dir)
    for name in DOC_NAMES:
        expected = f"[{docs_rel}/{name}]({docs_rel}/{name})"
        if expected not in text:
            findings.append(Finding("warn", f"README Documentation Map missing {docs_rel}/{name} link", str(path)))
    return findings


def audit_spec_decision_table(spec_path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []
    match = re.search(r"^##\s+2\.\s+Decision Table\b(?P<body>.*?)(?=^##\s+|\Z)", text, re.M | re.S)
    if not match:
        return findings

    for line in match.group("body").splitlines():
        cells = markdown_cells(line)
        if len(cells) < 4 or markdown_separator_row(cells):
            continue
        if cells[0].lower() == "id":
            continue
        if not cells[2] or cells[2] in {"-", "—"}:
            row_id = cells[0] or "?"
            findings.append(Finding("warn", f"SPEC decision row {row_id} has empty Choice", str(spec_path)))
    return findings


def decision_sections(text: str) -> list[tuple[str, str]]:
    headings = list(re.finditer(r"^##\s+(D-\d{3})\b[^\n]*", text, re.M))
    sections: list[tuple[str, str]] = []
    for idx, match in enumerate(headings):
        start = match.end()
        end = headings[idx + 1].start() if idx + 1 < len(headings) else len(text)
        sections.append((match.group(1), text[start:end]))
    return sections


def labeled_block_body(section: str, labels: tuple[str, ...]) -> str | None:
    label_pattern = "|".join(re.escape(label) for label in labels)
    match = re.search(
        rf"^\*\*[^*\n]*(?:{label_pattern})[^*\n]*\*\*[：:][ \t]*(?P<inline>[^\n]*)$",
        section,
        re.I | re.M,
    )
    if not match:
        return None

    start = match.end()
    next_label = re.search(r"^\*\*[^*\n]+\*\*[：:]", section[start:], re.M)
    end = start + next_label.start() if next_label else len(section)
    return (match.group("inline") + "\n" + section[start:end]).strip()


def block_has_content(body: str | None) -> bool:
    if body is None:
        return False
    for line in body.splitlines():
        content = re.sub(r"^[-*]\s*", "", line.strip()).strip()
        if content and content not in {"-", "—"}:
            return True
    return False


def audit_decision_entry_completeness(decisions_path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []
    required_blocks: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("Options", ("Options", "选项")),
        ("Chosen", ("Chosen", "选择")),
        ("Risks", ("Risks", "风险")),
    )
    for decision_id, section in decision_sections(text):
        for label, aliases in required_blocks:
            if not block_has_content(labeled_block_body(section, aliases)):
                findings.append(Finding("warn", f"{decision_id} is missing {label} content", str(decisions_path)))
    return findings


def audit_roadmap_acceptance(roadmap_path: Path, text: str) -> tuple[list[Finding], list[str]]:
    findings: list[Finding] = []
    steps = roadmap_step_sections(text)
    for title, body in steps:
        if "验收" not in body and "Acceptance" not in body:
            findings.append(Finding("warn", f"{title} has no acceptance section", str(roadmap_path)))
    return findings, [title for title, _ in steps]


def architecture_omission_reason_exists(text: str) -> bool:
    for line in text.splitlines():
        upper = line.upper()
        lower = line.lower()
        if "ARCHITECTURE" not in upper:
            continue
        has_omission = "omission" in lower or "省略" in line
        has_reason = "reason" in lower or "原因" in line or "理由" in line
        if has_omission and has_reason:
            return True
    return False


def current_phase_from_roadmap(text: str) -> str:
    match = re.search(r"^\*\*[^*\n]*(?:Phase|阶段)[^*\n]*\*\*:\s*(.+)$", text, re.I | re.M)
    return match.group(1).strip() if match else ""


def markdown_section(text: str, labels: tuple[str, ...]) -> str | None:
    pattern = "|".join(re.escape(label) for label in labels)
    match = re.search(rf"^#+\s+[^\n]*(?:{pattern})[^\n]*$", text, re.I | re.M)
    if not match:
        return None
    start = match.end()
    next_heading = re.search(r"^#+\s+", text[start:], re.M)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end]


def checkbox_counts(section: str | None) -> tuple[int, int]:
    if section is None:
        return 0, 0
    checked = len(re.findall(r"^[ \t]*[-*]\s+\[[xX]\]\s+", section, re.M))
    unchecked = len(re.findall(r"^[ \t]*[-*]\s+\[\s\]\s+", section, re.M))
    return checked, unchecked


def section_has_real_table_row(section: str | None, pending_terms: tuple[str, ...] = ()) -> bool:
    if section is None:
        return False
    for line in section.splitlines():
        cells = markdown_cells(line)
        if len(cells) < 2 or markdown_separator_row(cells):
            continue
        lowered = " ".join(cells).lower()
        if any(term.lower() in lowered for term in pending_terms):
            continue
        if any("<" in cell and ">" in cell for cell in cells):
            continue
        if cells[0].lower() in {"id", "acceptance", "验收项"}:
            continue
        return True
    return False


def audit_change_packet(packet_dir: Path) -> tuple[list[Finding], dict[str, object]]:
    findings: list[Finding] = []
    summary: dict[str, object] = {"path": str(packet_dir), "architecture": "present"}

    for name in CHANGE_REQUIRED_DOC_NAMES:
        path = packet_dir / name
        if not path.exists():
            findings.append(Finding("error", f"change packet missing {name}", str(path)))

    decisions_path = packet_dir / "DECISIONS.md"
    if decisions_path.exists():
        decisions_text = decisions_path.read_text(encoding="utf-8")
        ids = extract_decision_ids(decisions_text)
        summary["decision_ids"] = ids
        if not ids:
            findings.append(Finding("warn", "change packet DECISIONS.md has no D-XXX entries", str(decisions_path)))
        elif len(ids) != len(set(ids)):
            findings.append(Finding("error", "change packet has duplicate D-XXX ids", str(decisions_path)))
        elif ids != sorted(ids):
            findings.append(Finding("error", "change packet D-XXX ids are not monotonic", str(decisions_path)))
        else:
            expected = list(range(1, max(ids) + 1))
            if ids != expected:
                findings.append(Finding("warn", "change packet D-XXX ids skip at least one number", str(decisions_path)))
        findings.extend(audit_decision_entry_completeness(decisions_path, decisions_text))

    roadmap_path = packet_dir / "ROADMAP.md"
    roadmap_text = roadmap_path.read_text(encoding="utf-8") if roadmap_path.exists() else ""
    if roadmap_text:
        roadmap_findings, steps = audit_roadmap_acceptance(roadmap_path, roadmap_text)
        findings.extend(roadmap_findings)
        summary["roadmap_steps"] = steps

    architecture_path = packet_dir / "ARCHITECTURE.md"
    if not architecture_path.exists():
        summary["architecture"] = "omitted"
        if not roadmap_text or not architecture_omission_reason_exists(roadmap_text):
            findings.append(
                Finding(
                    "warn",
                    "change packet omits ARCHITECTURE.md without a ROADMAP omission reason",
                    str(roadmap_path if roadmap_path.exists() else architecture_path),
                )
            )

    spec_path = packet_dir / "SPEC.md"
    if spec_path.exists():
        spec_text = spec_path.read_text(encoding="utf-8")
        invariant_ids = re.findall(r"\*\*#(\d+)\*\*", spec_text)
        summary["invariant_ids"] = [int(value) for value in invariant_ids]
        if not invariant_ids:
            findings.append(Finding("warn", "change packet SPEC.md has no numbered invariants like **#1**", str(spec_path)))

    phase = current_phase_from_roadmap(roadmap_text)
    phase_lower = phase.lower()
    implementing = "实现中" in phase or "implementation" in phase_lower or "implementing" in phase_lower
    completed = "已完成" in phase or "completed" in phase_lower or "done" in phase_lower

    if implementing or completed:
        pre_section = markdown_section(roadmap_text, ("Pre-Implementation Gate", "实现前门禁"))
        checked, unchecked = checkbox_counts(pre_section)
        if checked + unchecked == 0:
            findings.append(Finding("warn", "change packet has no pre-implementation gate checklist", str(roadmap_path)))
        elif unchecked:
            findings.append(Finding("warn", "change packet entered implementation before completing the pre-implementation gate", str(roadmap_path)))

        research = markdown_section(roadmap_text, ("Research Log", "调研记录"))
        if not section_has_real_table_row(research):
            findings.append(Finding("warn", "change packet entered implementation without a concrete research log", str(roadmap_path)))

    if completed:
        completion_section = markdown_section(roadmap_text, ("Completion Gate", "完成前门禁"))
        checked, unchecked = checkbox_counts(completion_section)
        if checked + unchecked == 0:
            findings.append(Finding("warn", "completed change packet has no completion gate checklist", str(roadmap_path)))
        elif unchecked:
            findings.append(Finding("warn", "completed change packet has unfinished completion gate items", str(roadmap_path)))

        verification = markdown_section(roadmap_text, ("Verification Records", "验证记录"))
        if not section_has_real_table_row(verification, ("pending", "待验证")):
            findings.append(Finding("warn", "completed change packet has no completed verification records", str(roadmap_path)))

    return findings, summary


def discover_change_packets(docs_dir: Path) -> list[Path]:
    changes_dir = changes_dir_for(docs_dir)
    if not changes_dir.exists():
        return []
    return sorted(path for path in changes_dir.iterdir() if path.is_dir())


def audit_project(project: Path, docs_dir: Path) -> tuple[list[Finding], dict[str, object]]:
    findings: list[Finding] = []
    summary: dict[str, object] = {
        "project": str(project),
        "docs_dir": str(docs_dir),
        "generated_dir": str(generated_dir_for(project, docs_dir)),
    }

    if not docs_dir.exists():
        findings.append(Finding("error", "docs directory is missing", str(docs_dir)))
        return findings, summary

    for name in DOC_NAMES:
        path = docs_dir / name
        if not path.exists():
            findings.append(Finding("error", f"missing {name}", str(path)))

    decisions_path = docs_dir / "DECISIONS.md"
    if decisions_path.exists():
        decisions_text = decisions_path.read_text(encoding="utf-8")
        ids = extract_decision_ids(decisions_text)
        summary["decision_ids"] = ids
        if not ids:
            findings.append(Finding("warn", "DECISIONS.md has no D-XXX entries", str(decisions_path)))
        elif len(ids) != len(set(ids)):
            findings.append(Finding("error", "DECISIONS.md has duplicate D-XXX ids", str(decisions_path)))
        elif ids != sorted(ids):
            findings.append(Finding("error", "D-XXX ids are not monotonic", str(decisions_path)))
        else:
            expected = list(range(1, max(ids) + 1))
            if ids != expected:
                findings.append(Finding("warn", "D-XXX ids skip at least one number", str(decisions_path)))
        findings.extend(audit_decision_entry_completeness(decisions_path, decisions_text))

    roadmap_path = docs_dir / "ROADMAP.md"
    if roadmap_path.exists():
        text = roadmap_path.read_text(encoding="utf-8")
        roadmap_findings, steps = audit_roadmap_acceptance(roadmap_path, text)
        findings.extend(roadmap_findings)
        summary["roadmap_steps"] = steps

    spec_path = docs_dir / "SPEC.md"
    if spec_path.exists():
        text = spec_path.read_text(encoding="utf-8")
        invariant_ids = re.findall(r"\*\*#(\d+)\*\*", text)
        summary["invariant_ids"] = [int(value) for value in invariant_ids]
        if not invariant_ids:
            findings.append(Finding("warn", "SPEC.md has no numbered invariants like **#1**", str(spec_path)))
        findings.extend(audit_spec_decision_table(spec_path, text))

    findings.extend(audit_readme_documentation_map(project, docs_dir))

    for pointer in ("AGENTS.md",):
        path = project / pointer
        if path.exists():
            text = path.read_text(encoding="utf-8")
            if docs_rel_for_markdown(project, docs_dir) not in text:
                findings.append(Finding("warn", f"{pointer} does not mention the active docs dir", str(path)))

    change_summaries: list[dict[str, object]] = []
    for packet_dir in discover_change_packets(docs_dir):
        packet_findings, packet_summary = audit_change_packet(packet_dir)
        findings.extend(packet_findings)
        change_summaries.append(packet_summary)
    summary["change_packets"] = change_summaries

    return findings, summary


def cmd_audit(args: argparse.Namespace) -> int:
    project = Path(args.project).expanduser().resolve()
    docs_dir = docs_dir_for(project, args.docs_dir)
    findings, summary = audit_project(project, docs_dir)
    payload = {
        "ok": not any(item.level == "error" for item in findings),
        "summary": summary,
        "findings": [item.as_dict() for item in findings],
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Project: {project}")
        print(f"Docs dir: {docs_dir}")
        if findings:
            for item in findings:
                suffix = f" ({item.path})" if item.path else ""
                print(f"[{item.level}] {item.message}{suffix}")
        else:
            print("No findings.")

    if args.write_report:
        out_dir = generated_dir_for(project, docs_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        report = out_dir / "audit.json"
        report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if not args.json:
            print(f"Wrote {report}")

    return 1 if any(item.level == "error" for item in findings) else 0


def parse_current_status(roadmap: Path) -> tuple[str | None, str | None]:
    if not roadmap.exists():
        return None, None
    text = roadmap.read_text(encoding="utf-8")
    phase_match = re.search(r"\*\*Phase\*\*:\s*(.+)", text)
    step_match = re.search(r"\*\*(?:Current\s+Step|当前\s*Step|Step)\*\*:\s*(.+)", text)
    return (
        phase_match.group(1).strip() if phase_match else None,
        step_match.group(1).strip() if step_match else None,
    )


def cmd_status(args: argparse.Namespace) -> int:
    project = Path(args.project).expanduser().resolve()
    docs_dir = docs_dir_for(project, args.docs_dir)
    decisions_path = docs_dir / "DECISIONS.md"
    ids = extract_decision_ids(decisions_path.read_text(encoding="utf-8")) if decisions_path.exists() else []
    next_id = max(ids, default=0) + 1
    phase, step = parse_current_status(docs_dir / "ROADMAP.md")

    print(f"Project: {project}")
    print(f"Docs dir: {docs_dir}")
    print(f"Phase: {phase or '?'}")
    print(f"Step: {step or '?'}")
    print(f"Next decision: D-{next_id:03d}")
    packets = discover_change_packets(docs_dir)
    print(f"Change packets: {len(packets)}")
    if packets:
        print(f"Latest change: {packets[-1].name}")
    return 0


def decision_skeleton(decision_id: int, title: str, today: str) -> str:
    return f"""
## D-{decision_id:03d} · {title}

**日期 / Date**: {today}

**上下文 / Context**:

**选项 / Options**:
- A.
- B.
- C.

**选择 / Chosen**:

**理由 / Rationale**:
-
-

**风险登记 / Risks**:
-

**对应代码 / 文档**：
- SPEC §
- ``
"""


def cmd_new_decision(args: argparse.Namespace) -> int:
    project = Path(args.project).expanduser().resolve()
    docs_dir = docs_dir_for(project, args.docs_dir)
    path = docs_dir / "DECISIONS.md"
    if not path.exists():
        raise SystemExit(f"Missing {path}")
    text = path.read_text(encoding="utf-8")
    ids = extract_decision_ids(text)
    next_id = max(ids, default=0) + 1
    today = args.date or _dt.date.today().isoformat()
    skeleton = decision_skeleton(next_id, args.title, today)
    path.write_text(text.rstrip() + "\n" + skeleton + "\n", encoding="utf-8")
    print(f"Appended D-{next_id:03d} to {path}")
    return 0


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


def link_claude_to_agents(force: bool, source: Path | None = None) -> str:
    target = target_path_for("claude")
    agents_target = Path("..") / ".." / ".agents" / "skills" / SKILL_NAME
    if target.exists() or target.is_symlink():
        if target.is_symlink() and os.readlink(target) == str(agents_target):
            return "already linked"
        if not force:
            return "exists; pass --force to replace"
        if target.is_symlink() or target.is_file():
            target.unlink()
        else:
            shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        target.symlink_to(agents_target)
        return "linked to ~/.agents"
    except OSError as exc:
        fallback_source = target_path_for("agents")
        if not (fallback_source / "SKILL.md").exists():
            fallback_source = source or fallback_source
        if not (fallback_source / "SKILL.md").exists():
            raise SystemExit(
                f"Claude symlink failed ({exc}) and no copy fallback source exists: {fallback_source}"
            )
        status = copy_skill(fallback_source, target, force=True)
        return f"symlink failed ({exc}); {status} fallback"


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
    if "claude" in targets and "agents" not in targets:
        print("claude target uses ~/.agents as source; syncing agents first")
        targets.insert(0, "agents")

    print("sync target paths:")
    for target in targets:
        print(f"  {target}: {target_path_for(target)}")

    if args.dry_run:
        return 0

    for target in targets:
        if target == "claude":
            status = link_claude_to_agents(args.force, source)
        else:
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


def cmd_update(args: argparse.Namespace) -> int:
    source_root = find_source_root()
    installer = source_root / "scripts" / "install_remote.sh"
    if not installer.exists():
        raise SystemExit(f"Native installer script missing: {installer}")

    command = [str(installer)]
    if args.version:
        command.extend(["--version", args.version])
    if args.release_base_url:
        command.extend(["--release-base-url", args.release_base_url])
    if args.install_root:
        command.extend(["--install-root", args.install_root])
    if args.bin_dir:
        command.extend(["--bin-dir", args.bin_dir])
    if args.sync_skill:
        command.append("--sync-skill")

    env = os.environ.copy()
    env.setdefault("DOCDEV_INSTALL_LOG_PREFIX", "[docdev update]")
    return subprocess.run(command, check=False, env=env).returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="docdev", description="Docs-driven development helper CLI.")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {VERSION}")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Create or refresh docs-driven project scaffolding.")
    init.add_argument("project", nargs="?", default=".")
    init.add_argument("--docs-dir", default=None)
    init.add_argument("--template-dir", default=None)
    init.add_argument("--force", action="store_true")
    init.add_argument("--write-config", action="store_true")
    init.add_argument("--no-readme", action="store_true")
    init.add_argument("--no-agents", action="store_true")
    init.set_defaults(func=cmd_init)

    change = sub.add_parser("new-change", help="Create a per-requirement change packet.")
    change.add_argument("slug")
    change.add_argument("project", nargs="?", default=".")
    change.add_argument("--docs-dir", default=None)
    change.add_argument("--template-dir", default=None)
    change.add_argument("--lang", choices=("zh", "en"), default="zh")
    change.add_argument("--date", default=None)
    change.add_argument("--with-architecture", action="store_true")
    change.add_argument("--force", action="store_true")
    change.set_defaults(func=cmd_new_change)

    audit = sub.add_parser("audit", help="Check docs-driven project invariants.")
    audit.add_argument("project", nargs="?", default=".")
    audit.add_argument("--docs-dir", default=None)
    audit.add_argument("--json", action="store_true")
    audit.add_argument("--write-report", action="store_true")
    audit.set_defaults(func=cmd_audit)

    status = sub.add_parser("status", help="Show active Phase, Step, and next D-XXX id.")
    status.add_argument("project", nargs="?", default=".")
    status.add_argument("--docs-dir", default=None)
    status.set_defaults(func=cmd_status)

    decision = sub.add_parser("new-decision", help="Append the next D-XXX decision skeleton.")
    decision.add_argument("title")
    decision.add_argument("project", nargs="?", default=".")
    decision.add_argument("--docs-dir", default=None)
    decision.add_argument("--date", default=None)
    decision.set_defaults(func=cmd_new_decision)

    sync = sub.add_parser("sync-skill", help="Sync the skill to Codex, Cursor, shared agents, and Claude.")
    sync.add_argument("--targets", default="all", help="Comma list: codex,cursor,agents,claude,all")
    sync.add_argument("--source", default=None)
    sync.add_argument("--force", action="store_true")
    sync.add_argument("--dry-run", action="store_true")
    sync.set_defaults(func=cmd_sync_skill)

    doctor = sub.add_parser("doctor", help="Show local install and sync state.")
    doctor.set_defaults(func=cmd_doctor)

    update = sub.add_parser("update", help="Update a native release install.")
    update.add_argument("--version", default=None, help="Version to install. Default: latest.")
    update.add_argument("--release-base-url", default=None, help="Manifest/artifact base URL.")
    update.add_argument("--install-root", default=None, help="Override DOCDEV_INSTALL_ROOT.")
    update.add_argument("--bin-dir", default=None, help="Override DOCDEV_BIN_DIR.")
    update.add_argument("--sync-skill", action="store_true", help="Refresh skill targets after update.")
    update.set_defaults(func=cmd_update)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
