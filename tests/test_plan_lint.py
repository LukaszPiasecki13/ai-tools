"""Regression tests for skills/sdlc-plan/scripts/plan_lint.py.

Run: pytest  (or: python -m unittest discover -s tests -v)

The linter is the deterministic gate in front of the LLM plan review, so the cases that
matter are the ones where a wrong verdict wastes a reviewer call (false negative) or sends
a good plan back to a fixer for nothing (false positive).
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from conftest import ROOT

LINT_DIR = ROOT / "skills" / "sdlc-plan" / "scripts"
sys.path.insert(0, str(LINT_DIR))

import plan_lint  # noqa: E402

CONTEXT = """# Run manifest
- tier: {tier}
- ui: {ui}
- repo_root: {root}
- context_status: accepted
- plan_status: draft
- implementation_status: not-started

## Drift snapshot
head: {root} = 0123abcd
file: {root}/src/service.py = 4567cdef
"""

REQUIREMENTS = """# Requirements
- DEC-01: Limit is configurable
- DEC-02: Report is a separate module
### AC-01
User sees at most `limit` rows. Relates to DEC-01.
- AC-02: Report renders
"""

PLAN = """# Plan

## File map
| Path | Action | Anchor |
|---|---|---|
| src/service.py | MODIFY | `Service.run` |
| src/new_module.py | NEW | - |

## Interfaces
| File | Symbol | Signature | Status |
|---|---|---|---|
| src/service.py | Service.run | `def run(self, limit: int) -> str` | CHANGED |
| src/new_module.py | build_report | `def build_report() -> str` | NEW |

## Steps
| Step | Description | DEC | AC |
|---|---|---|---|
| S1 | Change run | DEC-01 | AC-01 |
| S2 | Add report | DEC-02 | AC-02 |

## Traceability
| DEC | Step |
|---|---|
| DEC-01 | S1 |
| DEC-02 | S2 |

| AC | Step | Test | E2E |
|---|---|---|---|
| AC-01 | S1 | test_run_limit | n.d. |
| AC-02 | S2 | n.d. | E2E-1 |
"""

SERVICE = "class Service:\n    def run(self):\n        return ''\n"


class LintCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name) / "repo"
        self.task = Path(tmp.name) / "task"
        (self.repo / "src").mkdir(parents=True)
        self.task.mkdir()
        (self.repo / "src" / "service.py").write_text(SERVICE, encoding="utf-8")

    def lint(
        self,
        plan: str = PLAN,
        requirements: str = REQUIREMENTS,
        tier: str = "standard",
        ui: str = "false",
        context: str | None = None,
    ) -> plan_lint.Report:
        text = context or CONTEXT.format(tier=tier, ui=ui, root=self.repo)
        (self.task / "_context.md").write_text(text, encoding="utf-8")
        (self.task / "02-requirements.md").write_text(requirements, encoding="utf-8")
        (self.task / "03-plan.md").write_text(plan, encoding="utf-8")
        return plan_lint.lint(self.task)

    def messages(self, report: plan_lint.Report, severity: str = "error") -> list[str]:
        return [f"{f.area}: {f.message}" for f in report.findings if f.severity == severity]

    def assertClean(self, report: plan_lint.Report) -> None:
        self.assertEqual([], self.messages(report), "unexpected errors")


class TestHappyPath(LintCase):
    def test_consistent_plan_has_no_errors(self) -> None:
        report = self.lint()
        self.assertClean(report)
        self.assertEqual(2, report.stats["files"])
        self.assertEqual(2, report.stats["steps"])

    def test_polish_headers_are_accepted(self) -> None:
        plan = (
            PLAN.replace("| Path | Action |", "| Ścieżka | Akcja |")
            .replace("| File | Symbol |", "| Plik | Symbol |")
            .replace("| Step | Description |", "| Krok | Opis |")
            .replace("| DEC | Step |", "| DEC | Krok |")
            .replace("| AC | Step |", "| AC | Krok |")
        )
        self.assertClean(self.lint(plan))

    def test_repo_root_is_read_from_manifest(self) -> None:
        report = self.lint()
        self.assertEqual(0, report.errors)


class TestFileMap(LintCase):
    def test_modify_of_missing_file_is_an_error(self) -> None:
        plan = PLAN.replace("src/service.py | MODIFY", "src/missing.py | MODIFY")
        errors = self.messages(self.lint(plan))
        self.assertTrue(any("MODIFY path not found: src/missing.py" in e for e in errors))

    def test_new_over_existing_file_is_an_error(self) -> None:
        (self.repo / "src" / "new_module.py").write_text("", encoding="utf-8")
        errors = self.messages(self.lint())
        self.assertTrue(any("marked NEW but already exists" in e for e in errors))

    def test_new_over_existing_file_only_warns_in_progress(self) -> None:
        (self.repo / "src" / "new_module.py").write_text("", encoding="utf-8")
        self.lint()
        report = plan_lint.lint(self.task, in_progress=True)
        self.assertClean(report)
        self.assertTrue(any("already exists" in w for w in self.messages(report, "warning")))

    def test_deleted_path_only_warns_in_progress(self) -> None:
        plan = PLAN.replace("| src/new_module.py | NEW | - |", "| src/new_module.py | NEW | - |\n| src/old.py | DELETE | - |")
        self.assertTrue(any("DELETE path not found" in e for e in self.messages(self.lint(plan))))
        report = plan_lint.lint(self.task, in_progress=True)
        self.assertClean(report)
        self.assertTrue(any("DELETE path not found" in w for w in self.messages(report, "warning")))

    def test_missing_modify_path_stays_an_error_in_progress(self) -> None:
        self.lint(PLAN.replace("src/service.py | MODIFY", "src/missing.py | MODIFY"))
        errors = self.messages(plan_lint.lint(self.task, in_progress=True))
        self.assertTrue(any("MODIFY path not found" in e for e in errors))

    def test_new_in_missing_directory_is_only_a_warning(self) -> None:
        plan = PLAN.replace("src/new_module.py | NEW", "src/pkg/new_module.py | NEW")
        plan = plan.replace("| src/new_module.py |", "| src/pkg/new_module.py |")
        report = self.lint(plan)
        self.assertClean(report)
        self.assertTrue(any("parent directory" in w for w in self.messages(report, "warning")))

    def test_unknown_action_is_an_error(self) -> None:
        plan = PLAN.replace("| MODIFY |", "| TOUCH |")
        self.assertTrue(any("invalid row" in e for e in self.messages(self.lint(plan))))

    def test_missing_table_is_an_error(self) -> None:
        errors = self.messages(self.lint("# Plan\nno tables here\n"))
        self.assertTrue(any("no file-map table" in e for e in errors))


class TestInterfaces(LintCase):
    def test_symbol_missing_from_existing_file_is_an_error(self) -> None:
        plan = PLAN.replace("Service.run | `def run", "Service.stop | `def stop")
        errors = self.messages(self.lint(plan))
        self.assertTrue(any("symbol 'Service.stop' not found" in e for e in errors))

    def test_changed_symbol_outside_the_file_map_is_an_error(self) -> None:
        (self.repo / "src" / "other.py").write_text("def run(): pass\n", encoding="utf-8")
        plan = PLAN.replace("| src/service.py | Service.run |", "| src/other.py | run |")
        errors = self.messages(self.lint(plan))
        self.assertTrue(any("file not in the file map" in e for e in errors))

    def test_existing_symbol_needs_no_file_map_row(self) -> None:
        plan = PLAN.replace("| CHANGED |", "| EXISTING |")
        self.assertClean(self.lint(plan))

    def test_invalid_status_is_an_error(self) -> None:
        plan = PLAN.replace("| CHANGED |", "| MAYBE |")
        self.assertTrue(any("status must be one of" in e for e in self.messages(self.lint(plan))))

    def test_missing_interface_table_is_only_a_warning(self) -> None:
        start, end = PLAN.index("## Interfaces"), PLAN.index("## Steps")
        report = self.lint(PLAN[:start] + PLAN[end:])
        self.assertClean(report)
        self.assertTrue(any("no interface table" in w for w in self.messages(report, "warning")))

    def test_symbol_name_extraction(self) -> None:
        cases = {
            "Service.run": "run",
            "async def fetch(self, x)": "fetch",
            "useThing()": "useThing",
            "": None,
        }
        for symbol, expected in cases.items():
            with self.subTest(symbol=symbol):
                self.assertEqual(expected, plan_lint.symbol_name(symbol))


class TestTraceability(LintCase):
    def test_dec_missing_from_matrix_is_an_error(self) -> None:
        plan = PLAN.replace("| DEC-02 | S2 |\n", "")
        self.assertTrue(any("DEC-02 is missing" in e for e in self.messages(self.lint(plan))))

    def test_ac_without_test_or_e2e_is_an_error(self) -> None:
        plan = PLAN.replace("| AC-01 | S1 | test_run_limit | n.d. |", "| AC-01 | S1 | n.d. | n.d. |")
        errors = self.messages(self.lint(plan))
        self.assertTrue(any("AC-01 has no test or E2E coverage" in e for e in errors))

    def test_unknown_step_is_an_error(self) -> None:
        plan = PLAN.replace("| DEC-01 | S1 |", "| DEC-01 | S9 |")
        self.assertTrue(any("unknown step S9" in e for e in self.messages(self.lint(plan))))

    def test_id_not_defined_in_requirements_is_an_error(self) -> None:
        plan = PLAN.replace("| DEC-02 | S2 |", "| DEC-02 | S2 |\n| DEC-07 | S2 |")
        self.assertTrue(any("DEC-07 is not defined" in e for e in self.messages(self.lint(plan))))

    def test_orphan_step_is_only_a_warning(self) -> None:
        plan = PLAN.replace("| S2 | Add report | DEC-02 | AC-02 |", "| S2 | Add report | DEC-02 | AC-02 |\n| S3 | Cleanup | - | - |")
        report = self.lint(plan)
        self.assertClean(report)
        self.assertTrue(any("step S3" in w for w in self.messages(report, "warning")))

    def test_ui_without_any_e2e_warns(self) -> None:
        plan = PLAN.replace("| AC-02 | S2 | n.d. | E2E-1 |", "| AC-02 | S2 | test_report | n.d. |")
        report = self.lint(plan, ui="true")
        self.assertTrue(any("no AC row has an E2E" in w for w in self.messages(report, "warning")))

    def test_requirements_are_read_from_line_starts_only(self) -> None:
        decs, acs = plan_lint.read_requirements(REQUIREMENTS)
        self.assertEqual({"DEC-01", "DEC-02"}, decs)
        self.assertEqual({"AC-01", "AC-02"}, acs)


class TestLineReferences(LintCase):
    def test_file_line_reference_is_an_error(self) -> None:
        errors = self.messages(self.lint(PLAN + "\nSee service.py:42 for details.\n"))
        self.assertTrue(any("line-ref" in e for e in errors))

    def test_prose_line_reference_is_an_error(self) -> None:
        errors = self.messages(self.lint(PLAN + "\nChange line 17 of the handler.\n"))
        self.assertTrue(any("line-ref" in e for e in errors))

    def test_code_fence_and_urls_are_ignored(self) -> None:
        plan = PLAN + "\n```\nservice.py:42\n```\nHost example.com:443 is reachable.\n"
        self.assertClean(self.lint(plan))


class TestTierAndStatus(LintCase):
    def _many_files(self, count: int) -> str:
        rows = "\n".join(f"| src/extra_{i}.py | NEW | - |" for i in range(count))
        return PLAN.replace("| src/new_module.py | NEW | - |", "| src/new_module.py | NEW | - |\n" + rows)

    def test_standard_over_eight_files_is_an_error(self) -> None:
        errors = self.messages(self.lint(self._many_files(7)))
        self.assertTrue(any("exceed the standard limit" in e for e in errors))

    def test_full_tier_accepts_more_files(self) -> None:
        errors = self.messages(self.lint(self._many_files(7), tier="full"))
        self.assertFalse(any("standard limit" in e for e in errors))

    def test_trivial_tier_has_no_plan(self) -> None:
        errors = self.messages(self.lint(tier="trivial"))
        self.assertTrue(any("tier must be one of" in e for e in errors))

    def test_invalid_status_fields_are_errors(self) -> None:
        context = CONTEXT.format(tier="standard", ui="false", root=self.repo).replace(
            "plan_status: draft", "plan_status: maybe"
        )
        errors = self.messages(self.lint(context=context))
        self.assertTrue(any("plan_status must be one of" in e for e in errors))

    def test_unknown_ui_flag_is_an_error(self) -> None:
        errors = self.messages(self.lint(ui="unknown"))
        self.assertTrue(any("ui must be one of" in e for e in errors))

    def test_draft_context_is_an_error(self) -> None:
        context = CONTEXT.format(tier="standard", ui="false", root=self.repo).replace(
            "context_status: accepted", "context_status: draft"
        )
        errors = self.messages(self.lint(context=context))
        self.assertTrue(any("finish Gate C" in e for e in errors))

    def test_missing_drift_snapshot_is_an_error(self) -> None:
        context = CONTEXT.format(tier="standard", ui="false", root=self.repo)
        context = context[: context.index("## Drift snapshot")]
        errors = self.messages(self.lint(context=context))
        self.assertTrue(any("no 'head:' line" in e for e in errors))
        self.assertTrue(any("no 'file:' line" in e for e in errors))


TESTS_TABLE = """
## Tests
| Test | AC | Input | Expected |
|---|---|---|---|
| test_run_limit | AC-01 | 100 rows | 10 rows |
"""


class TestTestNamesAndConsistency(LintCase):
    def test_known_test_name_is_clean(self) -> None:
        report = self.lint(PLAN + TESTS_TABLE)
        self.assertClean(report)
        self.assertFalse(any("Tests table" in w for w in self.messages(report, "warning")))

    def test_unknown_test_name_is_an_error(self) -> None:
        plan = (PLAN + TESTS_TABLE).replace("| AC-01 | S1 | test_run_limit |", "| AC-01 | S1 | test_typo |")
        errors = self.messages(self.lint(plan))
        self.assertTrue(any("'test_typo' is not defined in the Tests table" in e for e in errors))

    def test_backticked_test_names_in_one_cell_are_accepted(self) -> None:
        tests = TESTS_TABLE + "| `test_other` | AC-01 | x | y |\n"
        plan = (PLAN + tests).replace(
            "| AC-01 | S1 | test_run_limit |", "| AC-01 | S1 | `test_run_limit`, `test_other` |"
        )
        self.assertClean(self.lint(plan))

    def test_missing_tests_table_only_warns(self) -> None:
        report = self.lint()
        self.assertClean(report)
        self.assertTrue(any("no Tests table" in w for w in self.messages(report, "warning")))

    def test_duplicate_matrix_row_is_an_error(self) -> None:
        plan = PLAN.replace("| DEC-02 | S2 |", "| DEC-02 | S2 |\n| DEC-02 | S2 |")
        errors = self.messages(self.lint(plan))
        self.assertTrue(any("duplicate DEC-02 row" in e for e in errors))

    def test_step_lists_id_missing_from_matrix_is_an_error(self) -> None:
        plan = PLAN.replace("| S2 | Add report | DEC-02 |", "| S2 | Add report | DEC-01, DEC-02 |")
        errors = self.messages(self.lint(plan))
        self.assertTrue(any("S2 lists DEC-01 but the DEC matrix" in e for e in errors))

    def test_matrix_maps_id_the_step_does_not_list_is_an_error(self) -> None:
        plan = PLAN.replace("| AC-01 | S1 | test_run_limit |", "| AC-01 | S1, S2 | test_run_limit |")
        errors = self.messages(self.lint(plan))
        self.assertTrue(any("maps AC-01 to S2 but S2 does not list it" in e for e in errors))


class TestBundledTemplate(LintCase):
    def test_template_tables_are_machine_readable(self) -> None:
        template = (LINT_DIR.parent / "plan-template.md").read_text(encoding="utf-8")
        service = self.repo / "src" / "foo" / "service.py"
        service.parent.mkdir()
        service.write_text("class FooService:\n    def run(self):\n        return None\n", encoding="utf-8")
        report = self.lint(template)
        self.assertClean(report)
        self.assertEqual(2, report.stats["files"])
        self.assertEqual(2, report.stats["steps"])


class TestCommandLine(LintCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(LINT_DIR / "plan_lint.py"), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )

    def test_exit_codes(self) -> None:
        self.lint()
        self.assertEqual(0, self.run_cli(str(self.task)).returncode)
        (self.task / "03-plan.md").write_text(PLAN.replace("S1 |", "S9 |", 1), encoding="utf-8")
        self.assertEqual(1, self.run_cli(str(self.task)).returncode)
        self.assertEqual(2, self.run_cli(str(self.task / "missing")).returncode)

    def test_json_output_reports_counts(self) -> None:
        self.lint()
        result = self.run_cli(str(self.task), "--format", "json")
        self.assertEqual(0, result.returncode)
        self.assertIn('"errors": 0', result.stdout)


if __name__ == "__main__":
    unittest.main()
