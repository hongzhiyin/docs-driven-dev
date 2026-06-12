from __future__ import annotations

import argparse
import os
import subprocess

from .paths import find_source_root


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
