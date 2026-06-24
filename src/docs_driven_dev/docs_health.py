from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from .audit import decision_sections, discover_change_packets, roadmap_step_sections
from .paths import DOC_NAMES, docs_dir_for, generated_dir_for


THRESHOLDS = {
    "readme_lines": 180,
    "roadmap_lines": 800,
    "decisions_lines": 1200,
    "source_doc_lines": 2600,
    "change_packet_count": 12,
    "change_packet_lines": 3000,
}


def count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    return len(path.read_text(encoding="utf-8").splitlines())


def relative_path(project: Path, path: Path) -> str:
    try:
        return path.relative_to(project).as_posix()
    except ValueError:
        return str(path)


def step_status_counts(text: str) -> dict[str, int]:
    section_match = re.search(
        r"^#{2,3}\s+(?:Step Status|Step \u72b6\u6001\u603b\u89c8)[^\n]*\n(?P<body>.*?)(?=^---\s*$|^##\s+|\Z)",
        text,
        re.M | re.S,
    )
    section = section_match.group("body") if section_match else text
    counts: dict[str, int] = {}
    for line in section.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0].lower() in {"step", "---"}:
            continue
        if not line.strip().startswith("|"):
            continue
        status = cells[2]
        if not status or set(status) <= {"-"}:
            continue
        counts[status] = counts.get(status, 0) + 1
    return counts


def packet_line_count(packet: Path) -> int:
    return sum(count_lines(path) for path in packet.rglob("*.md"))


def collect_docs_health(project: Path, docs_dir: Path) -> dict[str, Any]:
    readme_path = project / "README.md"
    file_metrics: list[dict[str, Any]] = [
        {
            "name": "README.md",
            "path": relative_path(project, readme_path),
            "exists": readme_path.exists(),
            "lines": count_lines(readme_path),
            "role": "entrypoint",
        }
    ]

    source_doc_lines = 0
    for name in DOC_NAMES:
        path = docs_dir / name
        lines = count_lines(path)
        source_doc_lines += lines
        file_metrics.append(
            {
                "name": name,
                "path": relative_path(project, path),
                "exists": path.exists(),
                "lines": lines,
                "role": "source_doc",
            }
        )

    roadmap_path = docs_dir / "ROADMAP.md"
    roadmap_text = roadmap_path.read_text(encoding="utf-8") if roadmap_path.exists() else ""
    decisions_path = docs_dir / "DECISIONS.md"
    decisions_text = decisions_path.read_text(encoding="utf-8") if decisions_path.exists() else ""

    packets = discover_change_packets(docs_dir)
    packet_metrics = [
        {
            "path": relative_path(project, packet),
            "lines": packet_line_count(packet),
        }
        for packet in packets
    ]
    packet_metrics.sort(key=lambda item: int(item["lines"]), reverse=True)
    change_packet_lines = sum(int(item["lines"]) for item in packet_metrics)

    report: dict[str, Any] = {
        "schema_version": 1,
        "project": str(project),
        "docs_dir": str(docs_dir),
        "generated_dir": str(generated_dir_for(project, docs_dir)),
        "thresholds": THRESHOLDS,
        "files": file_metrics,
        "totals": {
            "readme_lines": count_lines(readme_path),
            "source_doc_lines": source_doc_lines,
            "change_packet_count": len(packet_metrics),
            "change_packet_lines": change_packet_lines,
        },
        "roadmap": {
            "step_sections": len(roadmap_step_sections(roadmap_text)),
            "step_status_counts": step_status_counts(roadmap_text),
        },
        "decisions": {
            "decision_count": len(decision_sections(decisions_text)),
        },
        "change_packets": {
            "count": len(packet_metrics),
            "total_lines": change_packet_lines,
            "largest": packet_metrics[:5],
        },
        "signals": [],
    }
    report["signals"] = docs_health_signals(report)
    return report


def docs_health_signals(report: dict[str, Any]) -> list[dict[str, str]]:
    signals: list[dict[str, str]] = []
    file_by_name = {item["name"]: item for item in report["files"]}

    readme = file_by_name.get("README.md", {})
    if int(readme.get("lines", 0)) > THRESHOLDS["readme_lines"]:
        signals.append(
            {
                "level": "review",
                "code": "readme-long",
                "path": str(readme.get("path", "README.md")),
                "message": "README is long; keep quick start and user workflow prominent, move maintainer runbook details elsewhere.",
            }
        )

    roadmap = file_by_name.get("ROADMAP.md", {})
    done_steps = int(report["roadmap"]["step_status_counts"].get("Done", 0))
    if int(roadmap.get("lines", 0)) > THRESHOLDS["roadmap_lines"]:
        signals.append(
            {
                "level": "review",
                "code": "roadmap-long",
                "path": str(roadmap.get("path", "docs/ROADMAP.md")),
                "message": f"ROADMAP is long and has {done_steps} done steps; consider keeping current state prominent and archiving older step details.",
            }
        )

    decisions = file_by_name.get("DECISIONS.md", {})
    if int(decisions.get("lines", 0)) > THRESHOLDS["decisions_lines"]:
        signals.append(
            {
                "level": "info",
                "code": "decisions-ledger-large",
                "path": str(decisions.get("path", "docs/DECISIONS.md")),
                "message": "DECISIONS is large; keep it append-only and prefer an index or summary over deleting old decisions.",
            }
        )

    totals = report["totals"]
    if int(totals["source_doc_lines"]) > THRESHOLDS["source_doc_lines"]:
        signals.append(
            {
                "level": "review",
                "code": "source-docs-large",
                "path": str(report["docs_dir"]),
                "message": "Source docs are large as a set; review whether current guidance and historical evidence are separated clearly.",
            }
        )

    if int(totals["change_packet_count"]) > THRESHOLDS["change_packet_count"]:
        signals.append(
            {
                "level": "info",
                "code": "many-change-packets",
                "path": str(Path(report["docs_dir"]) / "changes"),
                "message": "Many change packets exist; treat them as archive material unless the project defines a compaction policy.",
            }
        )

    if int(totals["change_packet_lines"]) > THRESHOLDS["change_packet_lines"]:
        signals.append(
            {
                "level": "info",
                "code": "change-packets-large",
                "path": str(Path(report["docs_dir"]) / "changes"),
                "message": "Change packet history is large; prefer generated indexes or explicit archives over deleting packet records.",
            }
        )

    return signals


def print_human_report(report: dict[str, Any]) -> None:
    print(f"Project: {report['project']}")
    print(f"Docs dir: {report['docs_dir']}")
    print("Document lines:")
    for item in report["files"]:
        status = "missing" if not item["exists"] else f"{item['lines']} lines"
        print(f"  {item['path']}: {status}")
    print(
        "Change packets: "
        f"{report['change_packets']['count']} packets, "
        f"{report['change_packets']['total_lines']} markdown lines"
    )
    if report["change_packets"]["largest"]:
        print("Largest change packets:")
        for item in report["change_packets"]["largest"]:
            print(f"  {item['path']}: {item['lines']} lines")
    if report["signals"]:
        print("Signals:")
        for item in report["signals"]:
            print(f"[{item['level']}] {item['code']}: {item['message']} ({item['path']})")
    else:
        print("No docs-health review signals.")


def cmd_docs_health(args: argparse.Namespace) -> int:
    project = Path(args.project).expanduser().resolve()
    docs_dir = docs_dir_for(project, args.docs_dir)
    report = collect_docs_health(project, docs_dir)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human_report(report)

    if args.write_report:
        out_dir = generated_dir_for(project, docs_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        report_path = out_dir / "docs-health.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if not args.json:
            print(f"Wrote {report_path}")

    return 0


__all__ = [
    "THRESHOLDS",
    "collect_docs_health",
    "cmd_docs_health",
    "count_lines",
    "docs_health_signals",
    "packet_line_count",
    "print_human_report",
    "step_status_counts",
]
