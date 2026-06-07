from __future__ import annotations

import os
import sys
import tempfile
import unittest
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

    def test_sync_dry_run(self) -> None:
        self.assertEqual(cli.main(["sync-skill", "--dry-run", "--targets", "codex,cursor"]), 0)

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
