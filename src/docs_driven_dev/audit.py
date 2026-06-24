from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
from pathlib import Path

from .models import Finding
from .paths import (
    CHANGE_REQUIRED_DOC_NAMES,
    DOC_NAMES,
    changes_dir_for,
    docs_dir_for,
    generated_dir_for,
)


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
        ("Options", ("Options", "\u9009\u9879")),
        ("Chosen", ("Chosen", "\u9009\u62e9")),
        ("Risks", ("Risks", "\u98ce\u9669")),
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
        if "\u9a8c\u6536" not in body and "Acceptance" not in body:
            findings.append(Finding("warn", f"{title} has no acceptance section", str(roadmap_path)))
    return findings, [title for title, _ in steps]


def architecture_omission_reason_exists(text: str) -> bool:
    for line in text.splitlines():
        upper = line.upper()
        lower = line.lower()
        if "ARCHITECTURE" not in upper:
            continue
        has_omission = "omission" in lower or "\u7701\u7565" in line
        has_reason = "reason" in lower or "\u539f\u56e0" in line or "\u7406\u7531" in line
        if has_omission and has_reason:
            return True
    return False


def current_phase_from_roadmap(text: str) -> str:
    match = re.search(r"^\*\*[^*\n]*(?:Phase|\u9636\u6bb5)[^*\n]*\*\*:\s*(.+)$", text, re.I | re.M)
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
        if cells[0].lower() in {"id", "acceptance", "\u9a8c\u6536\u9879"}:
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
    implementing = "\u5b9e\u73b0\u4e2d" in phase or "implementation" in phase_lower or "implementing" in phase_lower
    completed = "\u5df2\u5b8c\u6210" in phase or "completed" in phase_lower or "done" in phase_lower

    if implementing or completed:
        pre_section = markdown_section(roadmap_text, ("Pre-Implementation Gate", "\u5b9e\u73b0\u524d\u95e8\u7981"))
        checked, unchecked = checkbox_counts(pre_section)
        if checked + unchecked == 0:
            findings.append(Finding("warn", "change packet has no pre-implementation gate checklist", str(roadmap_path)))
        elif unchecked:
            findings.append(Finding("warn", "change packet entered implementation before completing the pre-implementation gate", str(roadmap_path)))

        research = markdown_section(roadmap_text, ("Research Log", "\u8c03\u7814\u8bb0\u5f55"))
        if not section_has_real_table_row(research):
            findings.append(Finding("warn", "change packet entered implementation without a concrete research log", str(roadmap_path)))

    if completed:
        completion_section = markdown_section(roadmap_text, ("Completion Gate", "\u5b8c\u6210\u524d\u95e8\u7981"))
        checked, unchecked = checkbox_counts(completion_section)
        if checked + unchecked == 0:
            findings.append(Finding("warn", "completed change packet has no completion gate checklist", str(roadmap_path)))
        elif unchecked:
            findings.append(Finding("warn", "completed change packet has unfinished completion gate items", str(roadmap_path)))

        verification = markdown_section(roadmap_text, ("Verification Records", "\u9a8c\u8bc1\u8bb0\u5f55"))
        if not section_has_real_table_row(verification, ("pending", "\u5f85\u9a8c\u8bc1")):
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
    step_match = re.search(r"\*\*(?:Current\s+Step|\u5f53\u524d\s*Step|Step)\*\*:\s*(.+)", text)
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
## D-{decision_id:03d} - {title}

**Date**: {today}

**Context**:

**Options**:
- A.
- B.
- C.

**Chosen**:

**Rationale**:
-
-

**Risks**:
-

**Related code / docs**:
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
