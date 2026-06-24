from __future__ import annotations

import argparse
from typing import Iterable

from .audit import cmd_audit, cmd_new_decision, cmd_status
from .docs_health import cmd_docs_health
from .paths import VERSION
from .release import cmd_uninstall, cmd_update
from .sync import cmd_doctor, cmd_sync_skill
from .templates import cmd_init, cmd_new_change


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

    health = sub.add_parser("docs-health", help="Report documentation size and maintenance signals.")
    health.add_argument("project", nargs="?", default=".")
    health.add_argument("--docs-dir", default=None)
    health.add_argument("--json", action="store_true")
    health.add_argument("--write-report", action="store_true")
    health.set_defaults(func=cmd_docs_health)

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
    update.add_argument("--sync-skill", dest="sync_skill", action="store_true", help="Refresh skill targets after update. Default.")
    update.add_argument("--no-sync-skill", dest="sync_skill", action="store_false", help="Update the release only; skip refreshing skill targets.")
    update.set_defaults(sync_skill=True)
    update.set_defaults(func=cmd_update)

    uninstall = sub.add_parser("uninstall", help="Remove a native release install and owned skill targets.")
    uninstall.add_argument("--install-root", default=None, help="Override DOCDEV_INSTALL_ROOT.")
    uninstall.add_argument("--bin-dir", default=None, help="Override DOCDEV_BIN_DIR.")
    uninstall.add_argument("--keep-skills", action="store_true", help="Remove only the native CLI install; keep agent skill targets.")
    uninstall.add_argument("--dry-run", action="store_true", help="Preview planned removals without deleting files.")
    uninstall.add_argument("--yes", action="store_true", help="Confirm destructive uninstall.")
    uninstall.set_defaults(func=cmd_uninstall)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    return args.func(args)
