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

    def test_init_and_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(cli.main(["init", tmp]), 0)
            for name in cli.DOC_NAMES:
                self.assertTrue((Path(tmp) / "docs" / name).exists())
            self.assertTrue((Path(tmp) / "docs" / "_generated" / "docdev").exists())
            self.assertEqual(cli.main(["audit", tmp]), 0)

    def test_new_decision_appends_next_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(cli.main(["init", tmp]), 0)
            self.assertEqual(cli.main(["new-decision", "Step 1 - follow-up", tmp]), 0)
            text = (Path(tmp) / "docs" / "DECISIONS.md").read_text(encoding="utf-8")
            self.assertIn("D-001", text)
            self.assertIn("D-002", text)

    def test_sync_dry_run(self) -> None:
        self.assertEqual(cli.main(["sync-skill", "--dry-run", "--targets", "codex,cursor"]), 0)


if __name__ == "__main__":
    unittest.main()
