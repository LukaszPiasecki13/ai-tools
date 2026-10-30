"""Regression tests for skills/sdlc-run/scripts/drift_check.py.

Run: pytest  (or: python -m unittest discover -s tests -v)

The script is the zero-token drift gate between sdlc-context, sdlc-plan and
sdlc-implement, so the cases that matter are a missed change (false negative) and a
rewrite that hides an earlier change (lost evidence).
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from conftest import ROOT

SCRIPT_DIR = ROOT / "skills" / "sdlc-run" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import drift_check  # noqa: E402

CONTEXT = """# Run: demo

repo_root: {root}
tier: standard
context_status: draft

## Drift snapshot
<!-- Gate C writes head:, status:, file: lines here -->

## Plan metrics
context_calls: unknown
"""

CONTEXT_MAP = """# Kontekst: demo
## Mapa plików
| Ścieżka (bezwzględna) | Rola w zadaniu | Etap |
|---|---|---|
| {root}/src/service.py | punkt wpięcia | impl |
"""

PLAN_MAP = """# Plan
### Mapa plików
| Path | Action | Anchor | DEC/AC |
|---|---|---|---|
| src/service.py | MODIFY | `Service.run` | DEC-01 |
| src/report.py | NEW | - | DEC-02 |

| File | Symbol | Signature | Status |
|---|---|---|---|
| src/other.py | x | `x()` | EXISTING |
"""


class DriftCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name) / "repo"
        self.task = Path(tmp.name) / "task"
        (self.repo / "src").mkdir(parents=True)
        self.task.mkdir()
        self.service = self.repo / "src" / "service.py"
        self.service.write_text("class Service:\n    pass\n", encoding="utf-8")
        (self.task / "_context.md").write_text(CONTEXT.format(root=self.repo), encoding="utf-8")
        (self.task / "01-context.md").write_text(CONTEXT_MAP.format(root=self.repo), encoding="utf-8")

    def run_mode(self, mode: str) -> drift_check.Result:
        result = drift_check.Result()
        drift_check.MODES[mode](self.task, result)
        return result

    def context(self) -> str:
        return (self.task / "_context.md").read_text(encoding="utf-8")


class TestSnapshot(DriftCase):
    def test_snapshot_writes_head_status_and_file_lines(self) -> None:
        self.run_mode("snapshot")
        text = self.context()
        self.assertIn(f"head: {self.repo} = ", text)
        self.assertIn(f"status: {self.repo} = ", text)
        self.assertIn(f"file: {self.service.resolve()} = {drift_check.blob_sha(self.service)}", text)
        self.assertNotIn("Gate C writes", text)
        self.assertIn("## Plan metrics\ncontext_calls: unknown", text)

    def test_blob_sha_matches_git_hash_object(self) -> None:
        self.assertEqual("e69de29bb2d1d6434b8b29ae775ad8c2e48c5391", drift_check.blob_sha(self._empty()))

    def test_missing_file_is_recorded_as_missing(self) -> None:
        self.assertEqual(drift_check.MISSING, drift_check.blob_sha(self.repo / "nope.py"))

    def _empty(self) -> Path:
        path = self.repo / "empty.txt"
        path.write_bytes(b"")
        return path


class TestCheck(DriftCase):
    def test_unchanged_files_have_no_drift(self) -> None:
        self.run_mode("snapshot")
        self.assertEqual([], self.run_mode("check").drift)

    def test_changed_content_is_drift(self) -> None:
        self.run_mode("snapshot")
        self.service.write_text("class Service:\n    changed = True\n", encoding="utf-8")
        drift = self.run_mode("check").drift
        self.assertEqual(1, len(drift))
        self.assertEqual(str(self.service.resolve()), drift[0]["path"])

    def test_deleted_file_is_drift(self) -> None:
        self.run_mode("snapshot")
        self.service.unlink()
        self.assertEqual(drift_check.MISSING, self.run_mode("check").drift[0]["current"])

    def test_check_never_writes(self) -> None:
        self.run_mode("snapshot")
        before = self.context()
        self.service.write_text("changed\n", encoding="utf-8")
        self.run_mode("check")
        self.assertEqual(before, self.context())

    def test_check_without_snapshot_is_unusable_input(self) -> None:
        with self.assertRaises(drift_check.InputError):
            self.run_mode("check")

    def test_plan_paths_are_reported_as_unrecorded(self) -> None:
        self.run_mode("snapshot")
        (self.task / "03-plan.md").write_text(PLAN_MAP, encoding="utf-8")
        unrecorded = self.run_mode("check").unrecorded
        self.assertEqual([str((self.repo / "src" / "report.py").resolve())], unrecorded)


class TestExtend(DriftCase):
    def test_extend_adds_plan_only_paths_and_keeps_recorded_lines(self) -> None:
        self.run_mode("snapshot")
        recorded_line = next(line for line in self.context().splitlines() if line.startswith("file:"))
        (self.task / "03-plan.md").write_text(PLAN_MAP, encoding="utf-8")
        result = self.run_mode("extend")
        text = self.context()
        self.assertIn(recorded_line, text)
        self.assertIn(f"file: {(self.repo / 'src' / 'report.py').resolve()} = MISSING", text)
        self.assertEqual(1, len(result.written))

    def test_new_file_appearing_after_extend_is_drift(self) -> None:
        self.run_mode("snapshot")
        (self.task / "03-plan.md").write_text(PLAN_MAP, encoding="utf-8")
        self.run_mode("extend")
        (self.repo / "src" / "report.py").write_text("x = 1\n", encoding="utf-8")
        self.assertEqual(drift_check.MISSING, self.run_mode("check").drift[0]["recorded"])

    def test_extend_refuses_to_write_when_drift_exists(self) -> None:
        self.run_mode("snapshot")
        (self.task / "03-plan.md").write_text(PLAN_MAP, encoding="utf-8")
        self.service.write_text("changed\n", encoding="utf-8")
        before = self.context()
        result = self.run_mode("extend")
        self.assertEqual(1, len(result.drift))
        self.assertEqual(before, self.context())

    def test_interface_table_paths_are_not_tracked(self) -> None:
        (self.task / "03-plan.md").write_text(PLAN_MAP, encoding="utf-8")
        tracked = drift_check.tracked_files(self.task, self.repo)
        self.assertNotIn((self.repo / "src" / "other.py").resolve(), tracked)


class TestCommandLine(DriftCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "drift_check.py"), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        )

    def test_exit_codes(self) -> None:
        self.assertEqual(2, self.run_cli(str(self.task), "check").returncode)
        self.assertEqual(0, self.run_cli(str(self.task), "snapshot").returncode)
        self.assertEqual(0, self.run_cli(str(self.task), "check").returncode)
        self.service.write_text("changed\n", encoding="utf-8")
        result = self.run_cli(str(self.task), "check", "--format", "json")
        self.assertEqual(1, result.returncode)
        self.assertIn('"recorded"', result.stdout)
        self.assertEqual(2, self.run_cli(str(self.task / "missing"), "check").returncode)


if __name__ == "__main__":
    unittest.main()
