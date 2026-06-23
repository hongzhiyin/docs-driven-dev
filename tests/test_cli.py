from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from docs_driven_dev import cli


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.old_project_dir = os.environ.get("DOCDEV_PROJECT_DIR")
        os.environ["DOCDEV_PROJECT_DIR"] = str(ROOT)

    def tearDown(self) -> None:
        if self.old_project_dir is None:
            os.environ.pop("DOCDEV_PROJECT_DIR", None)
        else:
            os.environ["DOCDEV_PROJECT_DIR"] = self.old_project_dir

    def finding_messages(self, project: Path) -> list[str]:
        findings, _summary = cli.audit_project(project, cli.docs_dir_for(project))
        return [item.message for item in findings]

    def test_version_flag(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as caught:
                cli.main(["--version"])

        self.assertEqual(caught.exception.code, 0)
        self.assertEqual(stdout.getvalue().strip(), f"docdev {cli.VERSION}")

    def test_update_dispatches_to_native_installer(self) -> None:
        completed = subprocess.CompletedProcess(args=["install_remote"], returncode=7)
        with mock.patch("docs_driven_dev.release.os.name", "posix"):
            with mock.patch("docs_driven_dev.release.find_source_root", return_value=ROOT):
                with mock.patch("docs_driven_dev.release.subprocess.run", return_value=completed) as run:
                    code = cli.main(
                        [
                            "update",
                            "--version",
                            "0.1.0",
                            "--release-base-url",
                            "file:///tmp/assets",
                            "--install-root",
                            "/tmp/install-root",
                            "--bin-dir",
                            "/tmp/bin",
                        ]
                    )

        self.assertEqual(code, 7)
        command = run.call_args.args[0]
        env = run.call_args.kwargs["env"]
        self.assertEqual(command[0], str(ROOT / "scripts" / "install_remote.sh"))
        self.assertIn("--version", command)
        self.assertIn("0.1.0", command)
        self.assertIn("--sync-skill", command)
        self.assertNotIn("--no-sync-skill", command)
        self.assertEqual(env["DOCDEV_INSTALL_LOG_PREFIX"], "[docdev update]")

    def test_update_dispatches_to_windows_native_installer(self) -> None:
        completed = subprocess.CompletedProcess(args=["install_remote"], returncode=0)
        with mock.patch("docs_driven_dev.release.os.name", "nt"):
            with mock.patch("docs_driven_dev.release.find_source_root", return_value=ROOT):
                with mock.patch("docs_driven_dev.release.subprocess.run", return_value=completed) as run:
                    code = cli.main(
                        [
                            "update",
                            "--version",
                            "0.1.0",
                            "--release-base-url",
                            "file:///tmp/assets",
                            "--install-root",
                            "C:\\docdev",
                            "--bin-dir",
                            "C:\\docdev\\bin",
                            "--no-sync-skill",
                        ]
                    )

        self.assertEqual(code, 0)
        command = run.call_args.args[0]
        env = run.call_args.kwargs["env"]
        self.assertEqual(
            command[:6],
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "scripts" / "install_remote.ps1"),
            ],
        )
        self.assertIn("-Version", command)
        self.assertIn("0.1.0", command)
        self.assertIn("-ReleaseBaseUrl", command)
        self.assertIn("file:///tmp/assets", command)
        self.assertIn("-InstallRoot", command)
        self.assertIn("C:\\docdev", command)
        self.assertIn("-BinDir", command)
        self.assertIn("C:\\docdev\\bin", command)
        self.assertIn("-NoSyncSkill", command)
        self.assertNotIn("-SyncSkill", command)
        self.assertEqual(env["DOCDEV_INSTALL_LOG_PREFIX"], "[docdev update]")

    def test_update_can_skip_skill_sync(self) -> None:
        completed = subprocess.CompletedProcess(args=["install_remote"], returncode=0)
        with mock.patch("docs_driven_dev.release.os.name", "posix"):
            with mock.patch("docs_driven_dev.release.find_source_root", return_value=ROOT):
                with mock.patch("docs_driven_dev.release.subprocess.run", return_value=completed) as run:
                    code = cli.main(["update", "--no-sync-skill"])

        self.assertEqual(code, 0)
        command = run.call_args.args[0]
        self.assertIn("--no-sync-skill", command)
        self.assertNotIn("--sync-skill", command)

    def write_generated_launcher(self, bin_dir: Path) -> Path:
        bin_dir.mkdir(parents=True, exist_ok=True)
        launcher = bin_dir / "docdev"
        launcher.write_text(
            '#!/bin/sh\nDOCDEV_PROJECT_DIR="/tmp/docdev" PYTHONPATH="/tmp/docdev/src" exec python3 -m docs_driven_dev.cli "$@"\n',
            encoding="utf-8",
        )
        return launcher

    def uninstall_env(self, root: Path) -> dict[str, str]:
        return {
            "DOCDEV_CODEX_HOME": str(root / "homes" / ".codex"),
            "DOCDEV_CURSOR_HOME": str(root / "homes" / ".cursor"),
            "DOCDEV_AGENTS_HOME": str(root / "homes" / ".agents"),
            "DOCDEV_CLAUDE_HOME": str(root / "homes" / ".claude"),
        }

    def test_uninstall_requires_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            install_root = root / "share" / "docdev"
            bin_dir = root / "bin"
            install_root.mkdir(parents=True)
            launcher = self.write_generated_launcher(bin_dir)

            with mock.patch.dict(os.environ, self.uninstall_env(root), clear=False):
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    code = cli.main(["uninstall", "--install-root", str(install_root), "--bin-dir", str(bin_dir)])

            self.assertEqual(code, 2)
            self.assertIn("Refusing to uninstall without --yes", stderr.getvalue())
            self.assertTrue(install_root.exists())
            self.assertTrue(launcher.exists())

    def test_uninstall_dry_run_does_not_delete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            install_root = root / "share" / "docdev"
            bin_dir = root / "bin"
            install_root.mkdir(parents=True)
            launcher = self.write_generated_launcher(bin_dir)
            codex_target = root / "homes" / ".codex" / "skills" / "docs-driven-dev"
            codex_target.mkdir(parents=True)
            (codex_target / ".docdev-skill-source").write_text("test\n", encoding="utf-8")

            stdout = io.StringIO()
            with mock.patch.dict(os.environ, self.uninstall_env(root), clear=False):
                with contextlib.redirect_stdout(stdout):
                    code = cli.main(
                        [
                            "uninstall",
                            "--dry-run",
                            "--install-root",
                            str(install_root),
                            "--bin-dir",
                            str(bin_dir),
                        ]
                    )

            self.assertEqual(code, 0)
            self.assertIn("remove: install root", stdout.getvalue())
            self.assertTrue(install_root.exists())
            self.assertTrue(launcher.exists())
            self.assertTrue(codex_target.exists())

    def test_uninstall_removes_owned_paths_and_skips_unmarked_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            install_root = root / "share" / "docdev"
            bin_dir = root / "bin"
            install_root.mkdir(parents=True)
            launcher = self.write_generated_launcher(bin_dir)
            env = self.uninstall_env(root)
            codex_target = Path(env["DOCDEV_CODEX_HOME"]) / "skills" / "docs-driven-dev"
            cursor_target = Path(env["DOCDEV_CURSOR_HOME"]) / "skills" / "docs-driven-dev"
            agents_target = Path(env["DOCDEV_AGENTS_HOME"]) / "skills" / "docs-driven-dev"
            claude_target = Path(env["DOCDEV_CLAUDE_HOME"]) / "skills" / "docs-driven-dev"
            for target in (codex_target, cursor_target, agents_target):
                target.mkdir(parents=True)
            (codex_target / ".docdev-skill-source").write_text("test\n", encoding="utf-8")
            (agents_target / ".docdev-skill-source").write_text("test\n", encoding="utf-8")
            claude_symlink_created = False
            if os.name != "nt":
                claude_target.parent.mkdir(parents=True)
                claude_target.symlink_to(Path("..") / ".." / ".agents" / "skills" / "docs-driven-dev")
                claude_symlink_created = True

            with mock.patch.dict(os.environ, env, clear=False):
                code = cli.main(["uninstall", "--yes", "--install-root", str(install_root), "--bin-dir", str(bin_dir)])

            self.assertEqual(code, 0)
            self.assertFalse(install_root.exists())
            self.assertFalse(launcher.exists())
            self.assertFalse(codex_target.exists())
            self.assertTrue(cursor_target.exists())
            self.assertFalse(agents_target.exists())
            if claude_symlink_created:
                self.assertFalse(claude_target.is_symlink())

    def test_uninstall_keep_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            install_root = root / "share" / "docdev"
            bin_dir = root / "bin"
            install_root.mkdir(parents=True)
            launcher = self.write_generated_launcher(bin_dir)
            codex_target = root / "homes" / ".codex" / "skills" / "docs-driven-dev"
            codex_target.mkdir(parents=True)
            (codex_target / ".docdev-skill-source").write_text("test\n", encoding="utf-8")

            with mock.patch.dict(os.environ, self.uninstall_env(root), clear=False):
                code = cli.main(
                    [
                        "uninstall",
                        "--yes",
                        "--keep-skills",
                        "--install-root",
                        str(install_root),
                        "--bin-dir",
                        str(bin_dir),
                    ]
                )

            self.assertEqual(code, 0)
            self.assertFalse(install_root.exists())
            self.assertFalse(launcher.exists())
            self.assertTrue(codex_target.exists())

    def test_init_and_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(cli.main(["init", tmp]), 0)
            for name in cli.DOC_NAMES:
                self.assertTrue((Path(tmp) / "docs" / name).exists())
            self.assertTrue((Path(tmp) / "docs" / "_generated" / "docdev").exists())
            self.assertEqual(cli.main(["audit", tmp]), 0)
            self.assertEqual(self.finding_messages(Path(tmp)), [])

    def test_new_decision_appends_next_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(cli.main(["init", tmp]), 0)
            self.assertEqual(cli.main(["new-decision", "Step 1 - follow-up", tmp]), 0)
            text = (Path(tmp) / "docs" / "DECISIONS.md").read_text(encoding="utf-8")
            self.assertIn("D-001", text)
            self.assertIn("D-002", text)

    def test_new_change_creates_default_packet_without_architecture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            self.assertEqual(cli.main(["init", tmp]), 0)
            self.assertEqual(cli.main(["new-change", "sample-feature", tmp, "--date", "2026-06-09"]), 0)

            packet = project / "docs" / "changes" / "2026-06-09-sample-feature"
            self.assertTrue((packet / "SPEC.md").exists())
            self.assertTrue((packet / "ROADMAP.md").exists())
            self.assertTrue((packet / "DECISIONS.md").exists())
            self.assertFalse((packet / "ARCHITECTURE.md").exists())
            self.assertEqual(self.finding_messages(project), [])

    def test_new_change_can_include_architecture_and_english_templates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            self.assertEqual(cli.main(["init", tmp]), 0)
            self.assertEqual(
                cli.main(
                    [
                        "new-change",
                        "api-contract",
                        tmp,
                        "--date",
                        "2026-06-09",
                        "--lang",
                        "en",
                        "--with-architecture",
                    ]
                ),
                0,
            )

            packet = project / "docs" / "changes" / "2026-06-09-api-contract"
            self.assertTrue((packet / "ARCHITECTURE.md").exists())
            spec = (packet / "SPEC.md").read_text(encoding="utf-8")
            self.assertIn("One-Sentence Goal", spec)
            self.assertEqual(self.finding_messages(project), [])

    def test_audit_warns_when_change_omits_architecture_without_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            self.assertEqual(cli.main(["init", tmp]), 0)
            self.assertEqual(cli.main(["new-change", "small-copy", tmp, "--date", "2026-06-09"]), 0)

            roadmap = project / "docs" / "changes" / "2026-06-09-small-copy" / "ROADMAP.md"
            text = roadmap.read_text(encoding="utf-8")
            roadmap.write_text(
                text.replace(
                    "**ARCHITECTURE 省略理由 / Architecture Omission Reason**: 当前需求尚未确认结构、数据流、接口、配置或迁移变化；如调研发现需要结构说明，先补 `ARCHITECTURE.md` 再实现。\n",
                    "",
                ),
                encoding="utf-8",
            )

            messages = self.finding_messages(project)
            self.assertIn("change packet omits ARCHITECTURE.md without a ROADMAP omission reason", messages)

    def test_audit_warns_when_change_enters_implementation_without_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            self.assertEqual(cli.main(["init", tmp]), 0)
            self.assertEqual(cli.main(["new-change", "approval-gate", tmp, "--date", "2026-06-09"]), 0)

            roadmap = project / "docs" / "changes" / "2026-06-09-approval-gate" / "ROADMAP.md"
            text = roadmap.read_text(encoding="utf-8")
            roadmap.write_text(text.replace("**阶段 / Phase**: 需求接入", "**阶段 / Phase**: 实现中"), encoding="utf-8")

            messages = self.finding_messages(project)
            self.assertIn(
                "change packet entered implementation before completing the pre-implementation gate",
                messages,
            )
            self.assertIn("change packet entered implementation without a concrete research log", messages)

    def test_sync_dry_run(self) -> None:
        self.assertEqual(cli.main(["sync-skill", "--dry-run", "--targets", "codex,cursor"]), 0)

    def test_copy_skill_does_not_write_installed_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "installed-skill"
            status = cli.copy_skill(ROOT / "skill", target, force=False)

            self.assertEqual(status, "copied")
            self.assertTrue((target / "SKILL.md").exists())
            self.assertTrue((target / ".docdev-skill-source").exists())
            self.assertFalse((target / "bin" / "docdev").exists())
            self.assertFalse((target / "bin" / "docdev.ps1").exists())
            self.assertFalse((target / "bin" / "docdev.cmd").exists())

    def test_copy_skill_replaces_marked_target_without_stale_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "installed-skill"
            self.assertEqual(cli.copy_skill(ROOT / "skill", target, force=False), "copied")
            stale = target / "old-installed-only-file.txt"
            stale.write_text("stale", encoding="utf-8")

            self.assertEqual(cli.copy_skill(ROOT / "skill", target, force=False), "copied")

            self.assertFalse(stale.exists())
            self.assertTrue((target / "SKILL.md").exists())
            self.assertFalse((target / "bin" / "docdev").exists())

    def test_copy_skill_replacement_removes_old_installed_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "installed-skill"
            self.assertEqual(cli.copy_skill(ROOT / "skill", target, force=False), "copied")
            old_bin = target / "bin"
            old_bin.mkdir()
            old_wrapper = old_bin / "docdev"
            old_wrapper.write_text("old wrapper", encoding="utf-8")

            self.assertEqual(cli.copy_skill(ROOT / "skill", target, force=False), "copied")

            self.assertFalse(old_wrapper.exists())
            self.assertFalse(old_bin.exists())

    def test_target_path_env_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {
                "DOCDEV_CURSOR_SKILL_DIR": str(root / "cursor-direct"),
                "DOCDEV_AGENTS_SKILL_DIR": str(root / "agents-direct"),
                "DOCDEV_AGENTS_HOME": str(root / "agents-home"),
                "DOCDEV_CLAUDE_HOME": str(root / "claude-home"),
                "DOCDEV_CODEX_HOME": str(root / "codex-home"),
            }
            with mock.patch.dict(os.environ, env, clear=False):
                self.assertEqual(cli.target_path_for("cursor"), root / "cursor-direct")
                self.assertEqual(cli.target_path_for("agents"), root / "agents-direct")
                self.assertEqual(cli.target_path_for("claude"), root / "claude-home" / "skills" / "docs-driven-dev")
                self.assertEqual(cli.target_path_for("codex"), root / "codex-home" / "skills" / "docs-driven-dev")

    def test_claude_sync_copies_without_agents_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents_home = root / ".agents"
            claude_target = root / ".claude" / "skills" / "docs-driven-dev"
            env = {
                "DOCDEV_AGENTS_HOME": str(agents_home),
                "DOCDEV_CLAUDE_HOME": str(root / ".claude"),
            }
            stdout = io.StringIO()

            with mock.patch.dict(os.environ, env, clear=False):
                with contextlib.redirect_stdout(stdout):
                    code = cli.main(["sync-skill", "--targets", "claude", "--source", str(ROOT / "skill"), "--force"])

            self.assertEqual(code, 0)
            self.assertNotIn("syncing agents first", stdout.getvalue())
            self.assertFalse(agents_home.exists())
            self.assertTrue((claude_target / "SKILL.md").exists())
            self.assertTrue((claude_target / ".docdev-skill-source").exists())
            self.assertFalse((claude_target / "bin" / "docdev").exists())
            self.assertFalse((claude_target / "bin" / "docdev.ps1").exists())
            self.assertFalse((claude_target / "bin" / "docdev.cmd").exists())

    @unittest.skipIf(os.name == "nt", "creating symlinks is not portable on Windows test hosts")
    def test_copy_skill_replaces_legacy_claude_symlink_when_forced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claude_target = root / ".claude" / "skills" / "docs-driven-dev"
            claude_target.parent.mkdir(parents=True)
            claude_target.symlink_to(Path("..") / ".." / ".agents" / "skills" / "docs-driven-dev")

            self.assertEqual(cli.copy_skill(ROOT / "skill", claude_target, force=True), "copied")

            self.assertFalse(claude_target.is_symlink())
            self.assertTrue((claude_target / "SKILL.md").exists())
            self.assertTrue((claude_target / ".docdev-skill-source").exists())

    @unittest.skipIf(os.name == "nt", "setup_project.sh is a Unix shell script")
    def test_setup_project_script_creates_audit_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"

            result = subprocess.run(
                [str(ROOT / "scripts" / "setup_project.sh"), str(project)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((project / "docs" / "SPEC.md").exists())
            self.assertTrue((project / "docs" / "_generated" / "docdev" / "audit.json").exists())

    @unittest.skipIf(os.name == "nt", "setup_project.sh is a Unix shell script")
    def test_setup_project_script_audits_custom_docs_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "target"

            result = subprocess.run(
                [
                    str(ROOT / "scripts" / "setup_project.sh"),
                    str(project),
                    "--docs-dir",
                    "project-docs",
                    "--write-config",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((project / "project-docs" / "SPEC.md").exists())
            self.assertTrue((project / "project-docs" / "_generated" / "docdev" / "audit.json").exists())
            self.assertFalse((project / "docs" / "_generated" / "docdev" / "audit.json").exists())

    def test_install_script_default_targets_and_force(self) -> None:
        text = (ROOT / "scripts" / "install.sh").read_text(encoding="utf-8")
        self.assertIn("TARGETS=${DOCDEV_INSTALL_TARGETS:-codex,cursor,agents,claude}", text)
        self.assertIn('"$PROJECT_DIR/scripts/update_cli.sh" --targets "$TARGETS" --force', text)

    def test_install_script_supports_no_force(self) -> None:
        text = (ROOT / "scripts" / "install.sh").read_text(encoding="utf-8")
        self.assertIn("--no-force", text)
        self.assertIn('"$PROJECT_DIR/scripts/update_cli.sh" --targets "$TARGETS"', text)

    def test_install_and_update_scripts_emit_step_logs(self) -> None:
        install_sh = (ROOT / "scripts" / "install.sh").read_text(encoding="utf-8")
        update_sh = (ROOT / "scripts" / "update_cli.sh").read_text(encoding="utf-8")
        install_remote_sh = (ROOT / "scripts" / "install_remote.sh").read_text(encoding="utf-8")
        install_ps = (ROOT / "scripts" / "install.ps1").read_text(encoding="utf-8")
        update_ps = (ROOT / "scripts" / "update_cli.ps1").read_text(encoding="utf-8")
        install_remote_ps = (ROOT / "scripts" / "install_remote.ps1").read_text(encoding="utf-8")

        self.assertIn("[docdev install]", install_sh)
        self.assertIn("DOCDEV_INSTALL_LOG_PREFIX", install_remote_sh)
        self.assertIn("[docdev update]", update_sh)
        self.assertIn('run_step 4 5 "sync skill targets"', update_sh)
        self.assertIn("failed with exit code", update_sh)
        self.assertIn("[docdev install]", install_ps)
        self.assertIn("DOCDEV_INSTALL_LOG_PREFIX", install_remote_ps)
        self.assertIn("[docdev update]", update_ps)
        self.assertIn('Invoke-DocdevNativeStep 4 7 "sync skill targets"', update_ps)
        self.assertIn('Invoke-DocdevNativeStep 7 7 "status source checkout"', update_ps)
        self.assertIn("failed with exit code", update_ps)

    def test_windows_install_scripts_exist_and_delegate(self) -> None:
        install = (ROOT / "scripts" / "install.ps1").read_text(encoding="utf-8")
        update = (ROOT / "scripts" / "update_cli.ps1").read_text(encoding="utf-8")
        install_cli = (ROOT / "scripts" / "install_cli.ps1").read_text(encoding="utf-8")

        self.assertIn("update_cli.ps1", install)
        self.assertIn("codex,cursor,agents,claude", install)
        self.assertIn("& $UpdateScript -Targets $Targets -Force", install)
        self.assertNotIn("@Args", install)
        self.assertIn("python -m unittest discover", update)
        self.assertIn("python -m docs_driven_dev.cli @SyncArgs", update)
        self.assertIn("docdev.ps1", install_cli)
        self.assertIn("docdev.cmd", install_cli)
        self.assertIn('Join-Path $ProjectDir "src"', install_cli)

    def test_windows_scripts_configure_utf8_output(self) -> None:
        powershell_scripts = [
            ROOT / "scripts" / "install.ps1",
            ROOT / "scripts" / "update_cli.ps1",
            ROOT / "scripts" / "install_cli.ps1",
            ROOT / "scripts" / "install_remote.ps1",
        ]
        for script in powershell_scripts:
            text = script.read_text(encoding="utf-8")
            with self.subTest(script=script.name):
                self.assertIn("function Set-DocdevUtf8Console", text)
                self.assertIn("Set-DocdevUtf8Console", text)
                self.assertIn("System.Text.UTF8Encoding", text)
                self.assertIn("[Console]::OutputEncoding", text)
                self.assertIn("$script:OutputEncoding", text)
                self.assertIn('$env:PYTHONUTF8 = "1"', text)
                self.assertIn('$env:PYTHONIOENCODING = "utf-8"', text)

        for script in (ROOT / "scripts" / "install_cli.ps1", ROOT / "scripts" / "install_remote.ps1"):
            text = script.read_text(encoding="utf-8")
            with self.subTest(generated_launcher_template=script.name):
                self.assertIn("$PowerShellUtf8Prelude", text)
                self.assertIn("$OutputEncoding = $Utf8NoBom", text)
                self.assertIn("$env:PYTHONUTF8 = '1'", text)
                self.assertIn("$env:PYTHONIOENCODING = 'utf-8'", text)
                self.assertLess(text.index("$PowerShellUtf8Prelude"), text.index("`$env:DOCDEV_PROJECT_DIR"))
                self.assertIn("chcp 65001 >nul", text)
                self.assertLess(text.index("chcp 65001 >nul"), text.index('set "DOCDEV_PROJECT_DIR='))

    def test_remote_install_scripts_exist(self) -> None:
        install_sh = (ROOT / "scripts" / "install_remote.sh").read_text(encoding="utf-8")
        install_ps = (ROOT / "scripts" / "install_remote.ps1").read_text(encoding="utf-8")

        self.assertIn("DOCDEV_RELEASE_BASE_URL", install_sh)
        self.assertIn("GITHUB_TOKEN", install_sh)
        self.assertIn("--retry 3", install_sh)
        self.assertIn("--retry-all-errors", install_sh)
        self.assertIn("checksum mismatch", install_sh)
        self.assertIn("~/.local/share/docdev", install_sh)
        self.assertIn("SYNC_SKILL=1", install_sh)
        self.assertIn("--no-sync-skill", install_sh)
        self.assertIn("Get-FileHash -Algorithm SHA256", install_ps)
        self.assertIn("New-Item -ItemType Junction", install_ps)
        self.assertIn("[switch]$NoSyncSkill", install_ps)
        self.assertIn("[switch]$NoModifyPath", install_ps)
        self.assertIn('Join-Path $BinDir "docdev.cmd"', install_ps)
        self.assertIn("Set-Content -Encoding ASCII -Path $CmdLauncher", install_ps)
        self.assertIn('[Environment]::SetEnvironmentVariable("Path"', install_ps)
        self.assertIn("attempted to add to user PATH but could not verify persistence", install_ps)
        self.assertIn("attempted to add to current process PATH but could not verify it", install_ps)
        self.assertIn("Enable-DocdevCommandOnPath -Directory $BinDir", install_ps)
        self.assertIn("skipped PATH update because -NoModifyPath was set", install_ps)
        self.assertIn('--targets "codex,cursor,agents,claude"', install_ps)
        self.assertNotIn("--targets codex,cursor,agents,claude", install_ps)

    @unittest.skipIf(os.name == "nt", "package_release.sh is exercised by Unix shell test environments")
    def test_package_release_script_emits_manifest_and_excludes_local_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [str(ROOT / "scripts" / "package_release.sh"), "--out", tmp],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            manifest_path = Path(tmp) / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            artifact = Path(tmp) / manifest["artifact"]
            checksum = Path(tmp) / f"{manifest['artifact']}.sha256"
            install_sh = Path(tmp) / "install_remote.sh"
            install_ps1 = Path(tmp) / "install_remote.ps1"

            self.assertEqual(manifest["version"], cli.VERSION)
            self.assertTrue(artifact.exists())
            self.assertTrue(checksum.exists())
            self.assertTrue(install_sh.exists())
            self.assertTrue(os.access(install_sh, os.X_OK))
            self.assertTrue(install_ps1.exists())
            self.assertEqual(len(manifest["sha256"]), 64)
            self.assertEqual(
                manifest["installers"],
                [
                    {"platform": "unix", "artifact": "install_remote.sh"},
                    {"platform": "windows", "artifact": "install_remote.ps1"},
                ],
            )

            with tarfile.open(artifact, "r:gz") as archive:
                names = archive.getnames()

            self.assertIn(f"docdev-{cli.VERSION}/src/docs_driven_dev/cli.py", names)
            self.assertIn(f"docdev-{cli.VERSION}/src/docs_driven_dev/audit.py", names)
            self.assertIn(f"docdev-{cli.VERSION}/src/docs_driven_dev/commands.py", names)
            self.assertIn(f"docdev-{cli.VERSION}/src/docs_driven_dev/release.py", names)
            self.assertIn(f"docdev-{cli.VERSION}/src/docs_driven_dev/sync.py", names)
            self.assertIn(f"docdev-{cli.VERSION}/src/docs_driven_dev/templates.py", names)
            self.assertIn(f"docdev-{cli.VERSION}/skill/SKILL.md", names)
            self.assertFalse(any("__pycache__" in name for name in names))
            self.assertFalse(any(name.endswith(".pyc") for name in names))
            self.assertFalse(any("/.git/" in name or "/.venv/" in name for name in names))
            self.assertFalse(any("docs/_generated/docdev/" in name and not name.endswith("docs/_generated/docdev/") for name in names))

    @unittest.skipIf(os.name == "nt", "install_remote.sh is a Unix shell script")
    def test_install_remote_script_supports_local_release_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            install_root = root / "share" / "docdev"
            bin_dir = root / "bin"
            project = root / "target"

            package = subprocess.run(
                [str(ROOT / "scripts" / "package_release.sh"), "--out", str(assets)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(package.returncode, 0, package.stdout + package.stderr)

            install = subprocess.run(
                [
                    str(ROOT / "scripts" / "install_remote.sh"),
                    "--release-base-url",
                    assets.as_uri(),
                    "--install-root",
                    str(install_root),
                    "--bin-dir",
                    str(bin_dir),
                    "--no-sync-skill",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)

            launcher = bin_dir / "docdev"
            self.assertTrue(launcher.exists())
            self.assertTrue((install_root / "current").exists())
            self.assertEqual(
                subprocess.run([str(launcher), "init", str(project)], text=True, capture_output=True, check=False).returncode,
                0,
            )
            audit = subprocess.run([str(launcher), "audit", str(project)], text=True, capture_output=True, check=False)
            self.assertEqual(audit.returncode, 0, audit.stdout + audit.stderr)
            self.assertIn("No findings.", audit.stdout)

    @unittest.skipIf(os.name == "nt", "install_remote.sh is a Unix shell script")
    def test_install_remote_rejects_checksum_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "assets"
            bad_assets = root / "bad-assets"
            install_root = root / "share" / "docdev"
            bin_dir = root / "bin"

            package = subprocess.run(
                [str(ROOT / "scripts" / "package_release.sh"), "--out", str(assets)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(package.returncode, 0, package.stdout + package.stderr)
            shutil.copytree(assets, bad_assets)
            manifest_path = bad_assets / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["sha256"] = "0" * 64
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

            install = subprocess.run(
                [
                    str(ROOT / "scripts" / "install_remote.sh"),
                    "--release-base-url",
                    bad_assets.as_uri(),
                    "--install-root",
                    str(install_root),
                    "--bin-dir",
                    str(bin_dir),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(install.returncode, 0)
            self.assertIn("checksum mismatch", install.stderr)
            self.assertFalse((install_root / "current").exists())

    def test_skill_documents_existing_code_adoption(self) -> None:
        text = (ROOT / "skill" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("已有代码库没有项目级四件套时，这是 adoption case", text)
        self.assertIn("不是 blocked case", text)
        self.assertIn("`docdev init <project>`", text)
        self.assertIn('docdev new-change "<slug>" <project>', text)
        self.assertIn("不要让一个单独的", text)
        self.assertIn("成为项目唯一的 docs-driven artifact", text)

    def test_skill_requires_workflow_when_explicitly_named(self) -> None:
        text = (ROOT / "skill" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("description: >-", text)
        self.assertIn("用 docs-driven development 维护项目", text)
        self.assertIn("四件套文档", text)
        self.assertIn("## Invocation Contract（调用合同）", text)
        self.assertIn("只读一遍 `SKILL.md` 然后直接写代码是不够的", text)
        self.assertIn("不要把明确的 `docs-driven-dev` 调用静默降级", text)
        self.assertIn("在改代码前创建或更新必要的 docs artifacts", text)
        self.assertIn("即使只是小修复", text)
        self.assertIn("Workflow B0 - Small Existing-Project Fix（小修复）", text)
        self.assertLess(
            text.index("Workflow B0 - Small Existing-Project Fix（小修复）"),
            text.index("Workflow B - Existing Project Requirement（已有项目需求）"),
        )
        self.assertIn('docdev new-change "<slug>" <project>', text)
        self.assertIn('Treat an explicit user request like "fix it", "补上吧", or "implement it"', text)

    def test_skill_documents_delegation_guidance(self) -> None:
        text = (ROOT / "skill" / "SKILL.md").read_text(encoding="utf-8")
        spec = (ROOT / "docs" / "SPEC.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("## Delegation Guidance（委派指导）", text)
        self.assertNotIn("### Delegation Guidance（委派指导）", text)
        self.assertLess(
            text.index("## Delegation Guidance（委派指导）"),
            text.index("## Workflow A - Bootstrap（项目初始化）"),
        )
        self.assertIn("优先考虑委派", text)
        self.assertIn("Delegation 是", text)
        self.assertIn("ownership 仍由主 agent 收束", text)
        self.assertIn("主 agent owns", text)
        self.assertIn("用户意图、SPEC invariants、scope、implementation gate", text)
        self.assertIn("已批准的窄范围 implementation slice", text)
        self.assertIn("文档一致性检查", text)
        self.assertIn("测试失败定位", text)
        self.assertIn("objective", text)
        self.assertIn("file scope", text)
        self.assertIn("write permission", text)
        self.assertIn("changed files / findings", text)
        self.assertIn("uncertainty", text)
        self.assertIn("Agent delegation", spec)
        self.assertIn("Main agent owns docs-driven scope", spec)
        self.assertIn("skill-level workflow guidance", spec)
        self.assertIn("before executing any workflow", spec)
        self.assertIn("Present delegation guidance as a top-level workflow rule", spec)
        self.assertIn("优先考虑 delegation", readme)

    def test_readme_documents_explicit_invocation_fast_path(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("不应把它当成泛泛的参考方法", text)
        self.assertIn("small-fix path", text)
        self.assertIn("窄范围 bug fix", text)
        self.assertIn("明确禁止改文档", text)

    def test_docs_explain_path_and_replacement_contract(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        skill = (ROOT / "skill" / "SKILL.md").read_text(encoding="utf-8")
        skill_bundle = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((ROOT / "skill").rglob("*.md"))
        )
        spec = (ROOT / "docs" / "SPEC.md").read_text(encoding="utf-8")

        self.assertLessEqual(len(skill.splitlines()), 230)
        self.assertIn("源码 checkout", readme)
        self.assertIn("不会把 `docdev` 加入全局 shell `PATH`", readme)
        self.assertIn("Windows installer 默认把 `$HOME\\.local\\bin` 加入当前用户 PATH", readme)
        self.assertIn("默认把 `$HOME\\.local\\bin` 加入当前用户 PATH", readme)
        self.assertIn("-NoModifyPath", readme)
        self.assertIn("直接在终端运行 CLI", readme)
        self.assertIn("让当前 skill 目标反映这个源码 checkout 的 `skill/` 内容", readme)
        self.assertIn("手动覆盖可能留下 stale untracked files", readme)
        self.assertIn("~/.local/bin/docdev", readme)
        self.assertIn("docdev uninstall --dry-run", readme)
        self.assertIn("docdev uninstall --yes", readme)
        self.assertIn("docdev uninstall --yes --keep-skills", readme)
        self.assertIn("Install And Update Boundary（安装与更新边界）", skill)
        self.assertIn("不属于 active", skill)
        self.assertIn("README / SPEC / DECISIONS", skill)
        self.assertIn("先运行 native", readme)
        self.assertIn("按这个顺序解析 CLI", skill)
        self.assertIn("`docdev <command>` if available on `PATH`", skill)
        self.assertIn("agent 执行 CLI 时使用 `docdev` 或 native", readme)
        active_surface_forbidden = [
            "wrapper",
            "skill-local",
            "<skill-dir>",
            "docdev.cmd",
            ".docdev-skill-source",
            "legacy",
            "旧路径",
            "旧入口",
            "不会被自动清理",
            "skill 目录下",
        ]
        for forbidden in active_surface_forbidden:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, skill)
                self.assertNotIn(forbidden, readme)
                self.assertNotIn(forbidden, skill_bundle)
        active_skill_source_forbidden = [
            "Source Checkout",
            "源码",
            "source checkout",
            "install.sh",
            "install.ps1",
            ".venv",
            "DOCDEV_PROJECT_DIR",
            "PYTHONPATH",
            "DOCDEV_<TARGET>_SKILL_DIR",
            "DOCDEV_<TARGET>_HOME",
            "install_remote",
            "DOCDEV_RELEASE_BASE_URL",
            "Native Release Install",
            "default native layout",
            "Private GitHub",
            "docdev uninstall",
            "~/.local/bin/docdev",
            "$HOME\\.local\\bin",
            "docdev.ps1",
            "bin/docdev",
        ]
        for forbidden in active_skill_source_forbidden:
            with self.subTest(skill_source_forbidden=forbidden):
                self.assertNotIn(forbidden, skill)
                self.assertNotIn(forbidden, skill_bundle)
        self.assertIn("docdev.cmd", spec)

    def test_audit_warns_on_readme_documentation_map_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(cli.main(["init", tmp]), 0)
            readme = Path(tmp) / "README.md"
            text = readme.read_text(encoding="utf-8")
            readme.write_text(text.replace("[docs/SPEC.md](docs/SPEC.md)", "[docs/OLD.md](docs/OLD.md)"), encoding="utf-8")

            messages = self.finding_messages(Path(tmp))
            self.assertIn("README Documentation Map missing docs/SPEC.md link", messages)

    def test_audit_warns_on_spec_decision_table_empty_choice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(cli.main(["init", tmp]), 0)
            spec = Path(tmp) / "docs" / "SPEC.md"
            text = spec.read_text(encoding="utf-8")
            spec.write_text(text.replace("| B | Main framework / SDK | <example: no runtime dependencies> | See D-001 |", "| B | Main framework / SDK | | See D-001 |"), encoding="utf-8")

            messages = self.finding_messages(Path(tmp))
            self.assertIn("SPEC decision row B has empty Choice", messages)

    def test_audit_warns_on_incomplete_decision_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(cli.main(["init", tmp]), 0)
            decisions = Path(tmp) / "docs" / "DECISIONS.md"
            text = decisions.read_text(encoding="utf-8")
            decisions.write_text(
                text.rstrip()
                + """

---

## D-002 - Incomplete decision

**Date**: 2026-06-08

**Context**:
This fixture intentionally leaves required decision blocks empty.

**Options**:
-

**Chosen**:

**Risks**:
-
""",
                encoding="utf-8",
            )

            messages = self.finding_messages(Path(tmp))
            self.assertIn("D-002 is missing Options content", messages)
            self.assertIn("D-002 is missing Chosen content", messages)
            self.assertIn("D-002 is missing Risks content", messages)


if __name__ == "__main__":
    unittest.main()
