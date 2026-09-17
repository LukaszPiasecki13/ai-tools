"""Tests for scripts/install.py's knowledge-base validator installer.

Covers the failure mode this mechanism exists to prevent: a hand-copied kb_validate.py in a
project drifting silently from the toolkit's source of truth. Each case runs against a real
temporary directory rather than mocking the filesystem, so a change to install_kb_validator's
actual file-writing behaviour is what these tests exercise.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from conftest import ROOT, SCRIPTS

sys.path.insert(0, str(SCRIPTS))
import install  # noqa: E402


class TestInstallKbValidator(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.destination = Path(self._tmp.name)

    def test_fresh_install_writes_both_files_and_a_manifest(self) -> None:
        installed = install.install_kb_validator(self.destination, dry_run=False)

        self.assertTrue(installed)
        for name in install.KB_VALIDATOR_MARKERS:
            target = self.destination / "scripts" / name
            source = install.KB_VALIDATOR_DIR / name
            self.assertEqual(target.read_text(encoding="utf-8"), source.read_text(encoding="utf-8"))

        manifest = json.loads((self.destination / "scripts" / install.KB_VALIDATOR_MANIFEST).read_text())
        self.assertEqual(set(manifest["files"]), set(install.KB_VALIDATOR_MARKERS))

    def test_dry_run_changes_nothing_on_disk(self) -> None:
        installed = install.install_kb_validator(self.destination, dry_run=True)

        self.assertTrue(installed)
        self.assertFalse((self.destination / "scripts").exists())

    def test_rerun_refreshes_a_file_this_installer_previously_wrote(self) -> None:
        install.install_kb_validator(self.destination, dry_run=False)
        target = self.destination / "scripts" / "kb_validate.py"
        target.write_text("# locally edited, should be overwritten on refresh\n", encoding="utf-8")

        install.install_kb_validator(self.destination, dry_run=False)

        self.assertNotIn("locally edited", target.read_text(encoding="utf-8"))

    def test_adopts_a_copy_placed_by_hand_before_the_manifest_existed(self) -> None:
        """Reproduces the waterworks-monitoring-platform case: kb_validate.py was `cp`-ed in
        manually, with no manifest, before this installer path existed."""
        scripts_root = self.destination / "scripts"
        scripts_root.mkdir()
        (scripts_root / "kb_validate.py").write_text(
            (install.KB_VALIDATOR_DIR / "kb_validate.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        self.assertFalse((scripts_root / install.KB_VALIDATOR_MANIFEST).exists())

        installed = install.install_kb_validator(self.destination, dry_run=False)

        self.assertTrue(installed)
        self.assertTrue((scripts_root / install.KB_VALIDATOR_MANIFEST).exists())
        self.assertTrue((scripts_root / "test_kb_validate.py").exists())

    def test_refuses_to_clobber_an_unrelated_file_with_the_same_name(self) -> None:
        scripts_root = self.destination / "scripts"
        scripts_root.mkdir()
        (scripts_root / "kb_validate.py").write_text("# this project's own script\n", encoding="utf-8")

        install.install_kb_validator(self.destination, dry_run=False)

        self.assertEqual(
            (scripts_root / "kb_validate.py").read_text(encoding="utf-8"),
            "# this project's own script\n",
        )
        # The other file has no name collision, so it still gets installed independently.
        self.assertTrue((scripts_root / "test_kb_validate.py").exists())

    def test_validator_flag_alone_installs_without_any_rule_selected(self) -> None:
        """Regression: --validator (or --settings) on a directory that matches zero rule
        profiles used to hit the early `if not names: return 1` and never run at all. An
        empty temp dir matches no profile in `detect()`, which is exactly the case this
        covers."""
        exit_code = install.main(["--target", str(self.destination), "--validator"])

        self.assertEqual(exit_code, 0)
        self.assertTrue((self.destination / "scripts" / "kb_validate.py").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
