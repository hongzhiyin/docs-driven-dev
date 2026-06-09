from __future__ import annotations

import os
import subprocess
import sys
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

    def test_copy_skill_writes_installed_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "installed-skill"
            status = cli.copy_skill(ROOT / "skill", target, force=False)

            self.assertEqual(status, "copied")
            wrapper = target / "bin" / "docdev"
            ps_wrapper = target / "bin" / "docdev.ps1"
            cmd_wrapper = target / "bin" / "docdev.cmd"
            self.assertTrue(wrapper.exists())
            self.assertTrue(os.access(wrapper, os.X_OK))
            self.assertTrue(ps_wrapper.exists())
            self.assertTrue(cmd_wrapper.exists())
            text = wrapper.read_text(encoding="utf-8")
            self.assertIn(f'DOCDEV_PROJECT_DIR="{ROOT}"', text)
            self.assertIn(f'PYTHONPATH="{ROOT / "src"}"', text)
            ps_text = ps_wrapper.read_text(encoding="utf-8")
            self.assertIn(f"$env:DOCDEV_PROJECT_DIR = '{ROOT}'", ps_text)
            self.assertIn("python -m docs_driven_dev.cli @args", ps_text)
            cmd_text = cmd_wrapper.read_text(encoding="utf-8")
            self.assertIn(f'set "DOCDEV_PROJECT_DIR={ROOT}"', cmd_text)
            self.assertIn("python -m docs_driven_dev.cli %*", cmd_text)

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

    def test_claude_sync_copies_when_symlink_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agents_target = root / ".agents" / "skills" / "docs-driven-dev"
            claude_target = root / ".claude" / "skills" / "docs-driven-dev"

            def fake_target_path_for(target: str) -> Path:
                if target == "agents":
                    return agents_target
                if target == "claude":
                    return claude_target
                raise ValueError(target)

            with mock.patch("docs_driven_dev.cli.target_path_for", side_effect=fake_target_path_for):
                with mock.patch.object(Path, "symlink_to", side_effect=OSError("symlink denied")):
                    status = cli.link_claude_to_agents(force=True, source=ROOT / "skill")

            self.assertIn("symlink failed", status)
            self.assertIn("copied fallback", status)
            self.assertTrue((claude_target / "SKILL.md").exists())
            self.assertTrue((claude_target / "bin" / "docdev").exists())
            self.assertTrue((claude_target / "bin" / "docdev.ps1").exists())
            self.assertTrue((claude_target / "bin" / "docdev.cmd").exists())

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
        install_ps = (ROOT / "scripts" / "install.ps1").read_text(encoding="utf-8")
        update_ps = (ROOT / "scripts" / "update_cli.ps1").read_text(encoding="utf-8")

        self.assertIn("[docdev install]", install_sh)
        self.assertIn("[docdev update]", update_sh)
        self.assertIn('run_step 4 5 "sync skill targets"', update_sh)
        self.assertIn("failed with exit code", update_sh)
        self.assertIn("[docdev install]", install_ps)
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
