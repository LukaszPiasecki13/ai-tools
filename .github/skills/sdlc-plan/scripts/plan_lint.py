#!/usr/bin/env python3
"""Deterministic checks for an sdlc-plan artifact set, run before any LLM review.

Stdlib only, so it runs on a fresh clone and in CI without installing anything.
A green run does not prove the plan is right; it proves the mechanical claims
(paths, symbols, traceability, status fields) hold, so a reviewer spends tokens
on judgement instead of on typos.

Usage:
    python plan_lint.py TASK_DIR [--repo-root PATH] [--tier standard|full]
                        [--format text|json]

TASK_DIR holds _context.md, 02-requirements.md and 03-plan.md. Exit codes:
0 no errors (warnings allowed), 1 errors found, 2 unusable input.

Plan contract - tables are recognised by their header cells, not by headings
(Polish aliases such as Sciezka/Akcja/Plik/Krok are accepted):

    File map    | Path | Action | ...        Action: NEW | MODIFY | DELETE
    Interfaces  | File | Symbol | Status |   Status: NEW | EXISTING | CHANGED
    Steps       | Step | ... | DEC | AC |   Step ids: S1, S2, ...; DEC/AC columns optional
    Tests       | Test | AC | ...           test names referenced by the AC matrix
    DEC matrix  | DEC | Step |
    AC matrix   | AC | Step | Test | E2E |   Test/E2E may be n.d. but not both

Requirements are read from lines that start with an id (- DEC-01: ..., - AC-01: ...).
The manifest must have context_status: accepted, ui: true|false and a Drift snapshot
with at least one head: and one file: line.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

PLAN_TIERS = {"standard", "full"}
PLAN_STATUSES = {"not-started", "draft", "accepted"}
IMPLEMENTATION_STATUSES = {"not-started", "deferred", "in-progress", "blocked", "completed"}
CONTEXT_STATUSES = {"draft", "accepted"}
UI_VALUES = {"true", "false"}
FILE_ACTIONS = {"NEW", "MODIFY", "DELETE"}
SYMBOL_STATUSES = {"NEW", "EXISTING", "CHANGED"}
STANDARD_MAX_FILES = 8
EMPTY_CELLS = {"", "-", "n.d.", "n/a", "nd"}

HEADER_ALIASES = {
    "ścieżka": "path",
    "sciezka": "path",
    "akcja": "action",
    "plik": "file",
    "krok": "step",
    "testy": "test",
}

_MANIFEST_LINE = re.compile(
    r"^\s*(?:[-*]\s+)?`?(?P<key>tier|ui|repo_root|plan_status|"
    r"implementation_status|context_status)`?\s*:\s*(?P<value>.+?)\s*$",
    re.MULTILINE,
)
_REQUIREMENT_DEF = re.compile(
    r"^\s*(?:[-*+]\s+|#{1,6}\s+|\|\s*)?(?:\*\*|`)?\s*((?:DEC|AC)-\d+)\b",
    re.MULTILINE,
)
_TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)*\|?\s*$")
_SNAPSHOT_LINE = re.compile(r"^\s*(?P<kind>head|file)\s*:\s*\S.*=\s*\S+\s*$", re.MULTILINE)
_STEP_ID = re.compile(r"S\d+")
_STEP_TOKEN = re.compile(r"\bS\d+\b")
_REQUIREMENT_TOKEN = re.compile(r"\b(?:DEC|AC)-\d+\b")
_TEST_SPLIT = re.compile(r"[,;]")
_LINE_REF = re.compile(
    r"(?i)\b(?:lines?|linii?|linie|linia|wiersz\w*)\s+\d+"
    r"|\.(?:py|ts|tsx|js|jsx|cs|java|go|rs|cpp|h|hpp|ps1|md|json|ya?ml|sql|html|scss"
    r"|css):\d+"
)


class InputError(Exception):
    """The task directory cannot be linted (missing or unreadable artifact)."""


@dataclass(frozen=True)
class Finding:
    severity: str
    area: str
    message: str
    line: int | None = None


@dataclass(frozen=True)
class Table:
    header: list[str]
    rows: list[tuple[int, list[str]]]

    def cell(self, row: list[str], column: str) -> str:
        if column not in self.header:
            return ""
        index = self.header.index(column)
        return row[index] if index < len(row) else ""


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    stats: dict[str, int] = field(default_factory=dict)

    def add(self, severity: str, area: str, message: str, line: int | None = None) -> None:
        self.findings.append(Finding(severity, area, message, line))

    @property
    def errors(self) -> int:
        return sum(1 for item in self.findings if item.severity == "error")

    @property
    def warnings(self) -> int:
        return sum(1 for item in self.findings if item.severity == "warning")


def _clean(cell: str) -> str:
    return cell.strip().replace("\\|", "|").strip("`* ").strip()


def _split_row(line: str) -> list[str]:
    body = line.strip().removeprefix("|")
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [_clean(cell) for cell in re.split(r"(?<!\\)\|", body)]


def _normalize_header(cell: str) -> str:
    base = re.sub(r"\(.*?\)", "", cell).strip().lower()
    return HEADER_ALIASES.get(base, base)


def visible_lines(text: str) -> list[tuple[int, str]]:
    """Numbered lines outside fenced code blocks."""
    lines: list[tuple[int, str]] = []
    fence: str | None = None
    for number, line in enumerate(text.splitlines(), start=1):
        marker = line.lstrip()[:3]
        if marker in {"```", "~~~"}:
            fence = marker if fence is None else (None if fence == marker else fence)
            continue
        if fence is None:
            lines.append((number, line))
    return lines


def parse_tables(lines: list[tuple[int, str]]) -> list[Table]:
    tables: list[Table] = []
    index = 0
    while index < len(lines) - 1:
        if lines[index][1].lstrip().startswith("|") and _TABLE_SEPARATOR.match(
            lines[index + 1][1]
        ):
            header = [_normalize_header(cell) for cell in _split_row(lines[index][1])]
            rows: list[tuple[int, list[str]]] = []
            index += 2
            while index < len(lines) and lines[index][1].lstrip().startswith("|"):
                rows.append((lines[index][0], _split_row(lines[index][1])))
                index += 1
            tables.append(Table(header, rows))
        else:
            index += 1
    return tables


def read_manifest(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for match in _MANIFEST_LINE.finditer(text):
        values.setdefault(match["key"], match["value"].strip("`'\" "))
    return values


def read_requirements(text: str) -> tuple[set[str], set[str]]:
    ids = {match[1] for match in _REQUIREMENT_DEF.finditer(text)}
    return {i for i in ids if i.startswith("DEC")}, {i for i in ids if i.startswith("AC")}


def symbol_name(symbol: str) -> str | None:
    """Last identifier before any parameter list: `A.run(self)` -> `run`."""
    names = re.findall(r"[A-Za-z_$][\w$]*", symbol.split("(", 1)[0])
    return names[-1] if names else None


def _token(value: str) -> str:
    parts = value.split()
    return parts[0].lower() if parts else ""


def _resolve(raw: str, repo_root: Path) -> Path:
    path = Path(raw)
    return (path if path.is_absolute() else repo_root / path).resolve()


def _find(tables: list[Table], columns: set[str]) -> Table | None:
    return next((table for table in tables if columns <= set(table.header)), None)


def check_manifest(report: Report, manifest: dict[str, str], override: str | None) -> str:
    tier = override or _token(manifest.get("tier", ""))
    if tier not in PLAN_TIERS:
        report.add("error", "status", f"tier must be one of {sorted(PLAN_TIERS)}, got {tier!r}")
    fields = (
        ("plan_status", PLAN_STATUSES),
        ("implementation_status", IMPLEMENTATION_STATUSES),
        ("context_status", CONTEXT_STATUSES),
    )
    for key, allowed in fields:
        value = _token(manifest.get(key, ""))
        if value not in allowed:
            report.add("error", "status", f"{key} must be one of {sorted(allowed)}, got {value!r}")
    if _token(manifest.get("context_status", "")) == "draft":
        report.add("error", "status", "context_status is draft; finish Gate C in sdlc-context first")
    ui = _token(manifest.get("ui", ""))
    if ui not in UI_VALUES:
        report.add("error", "status", f"ui must be one of {sorted(UI_VALUES)}, got {ui!r}")
    return tier


def check_snapshot(report: Report, context_text: str) -> None:
    kinds = {match["kind"] for match in _SNAPSHOT_LINE.finditer(context_text)}
    for kind in ("head", "file"):
        if kind not in kinds:
            report.add(
                "error",
                "snapshot",
                f"Drift snapshot has no '{kind}:' line; Gate C must write it before accepting",
            )


def _check_path_state(
    report: Report, raw: str, path: Path, action: str, line: int, in_progress: bool = False
) -> None:
    if action == "NEW":
        if path.exists():
            severity = "warning" if in_progress else "error"
            report.add(severity, "file-map", f"marked NEW but already exists: {raw}", line)
        elif not path.parent.is_dir():
            report.add("warning", "file-map", f"parent directory does not exist: {raw}", line)
    elif not path.exists():
        severity = "warning" if in_progress and action == "DELETE" else "error"
        report.add(severity, "file-map", f"{action} path not found: {raw}", line)


def check_file_map(
    report: Report, tables: list[Table], repo_root: Path, in_progress: bool = False
) -> dict[Path, str]:
    table = _find(tables, {"path", "action"})
    if table is None:
        report.add("error", "file-map", "no file-map table (columns: Path | Action)")
        return {}
    files: dict[Path, str] = {}
    for line, row in table.rows:
        raw, action = table.cell(row, "path"), table.cell(row, "action").upper()
        if not raw or action not in FILE_ACTIONS:
            report.add(
                "error",
                "file-map",
                f"invalid row (path={raw!r}, action={action!r}); "
                f"action must be one of {sorted(FILE_ACTIONS)}",
                line,
            )
            continue
        path = _resolve(raw, repo_root)
        if path in files:
            report.add("warning", "file-map", f"duplicate path: {raw}", line)
        files[path] = action
        _check_path_state(report, raw, path, action, line, in_progress)
    report.stats["files"] = len(files)
    return files


def _check_interface_row(
    report: Report, raw: str, symbol: str, status: str, files: dict[Path, str], root: Path, line: int
) -> None:
    path = _resolve(raw, root)
    if status in {"NEW", "CHANGED"} and path not in files:
        report.add("error", "interface", f"{status} {symbol!r}: file not in the file map: {raw}", line)
    if status == "NEW":
        return
    if not path.is_file():
        report.add("error", "interface", f"file not found for {symbol!r}: {raw}", line)
        return
    name = symbol_name(symbol)
    content = path.read_text(encoding="utf-8", errors="replace")
    if name is None or not re.search(rf"\b{re.escape(name)}\b", content):
        report.add("error", "interface", f"symbol {symbol!r} not found in {raw}", line)


def check_interfaces(report: Report, tables: list[Table], files: dict[Path, str], root: Path) -> None:
    table = _find(tables, {"file", "symbol", "status"})
    if table is None:
        report.add(
            "warning",
            "interface",
            "no interface table (File | Symbol | Status); fine only when no code symbols change",
        )
        return
    for line, row in table.rows:
        status = table.cell(row, "status").upper()
        if status not in SYMBOL_STATUSES:
            report.add("error", "interface", f"status must be one of {sorted(SYMBOL_STATUSES)}", line)
            continue
        _check_interface_row(
            report, table.cell(row, "file"), table.cell(row, "symbol"), status, files, root, line
        )


def check_steps(report: Report, tables: list[Table]) -> set[str]:
    table = next((item for item in tables if item.header[:1] == ["step"]), None)
    if table is None:
        report.add("error", "steps", "no steps table (first column: Step)")
        return set()
    ids: set[str] = set()
    for line, row in table.rows:
        step = row[0] if row else ""
        if not _STEP_ID.fullmatch(step):
            report.add("error", "steps", f"step id must look like S1, got {step!r}", line)
        elif step in ids:
            report.add("error", "steps", f"duplicate step id {step}", line)
        else:
            ids.add(step)
    report.stats["steps"] = len(ids)
    return ids


def _check_matrix_rows(
    report: Report, table: Table, label: str, required: set[str], steps: set[str], evidence: tuple[str, ...]
) -> set[str]:
    used: set[str] = set()
    seen: set[str] = set()
    for line, row in table.rows:
        key = table.cell(row, label.lower())
        if key in seen:
            report.add("error", "matrix", f"duplicate {key} row in the {label} matrix", line)
            continue
        seen.add(key)
        if key not in required:
            report.add("error", "matrix", f"{key or '(empty)'} is not defined in 02-requirements.md", line)
            continue
        tokens = set(_STEP_TOKEN.findall(table.cell(row, "step")))
        if not tokens:
            report.add("error", "matrix", f"{key} maps to no step", line)
        for token in sorted(tokens - steps):
            report.add("error", "matrix", f"{key} references unknown step {token}", line)
        used |= tokens & steps
        covered = any(table.cell(row, column).lower() not in EMPTY_CELLS for column in evidence)
        if evidence and not covered:
            report.add("error", "matrix", f"{key} has no test or E2E coverage", line)
    for missing in sorted(required - seen):
        report.add("error", "matrix", f"{missing} is missing from the {label} matrix")
    return used


def check_matrices(
    report: Report, tables: list[Table], decs: set[str], acs: set[str], steps: set[str], ui: bool
) -> None:
    dec_table = _matrix_tables(tables, "dec")
    ac_table = _matrix_tables(tables, "ac")
    used: set[str] = set()
    for table, label, required, evidence in (
        (dec_table, "DEC", decs, ()),
        (ac_table, "AC", acs, ("test", "e2e")),
    ):
        if table is None:
            if required:
                report.add("error", "matrix", f"no {label} matrix (columns: {label} | Step ...)")
            continue
        used |= _check_matrix_rows(report, table, label, required, steps, evidence)
    for step in sorted(steps - used):
        report.add("warning", "matrix", f"step {step} appears in no DEC/AC matrix row")
    if ui and ac_table is not None:
        has_e2e = any(ac_table.cell(row, "e2e").lower() not in EMPTY_CELLS for _, row in ac_table.rows)
        if not has_e2e:
            report.add("warning", "matrix", "ui is true but no AC row has an E2E entry")
    if ac_table is not None:
        check_test_names(report, tables, ac_table)
    check_step_columns(report, tables, dec_table, ac_table)


def _matrix_tables(tables: list[Table], label: str) -> Table | None:
    return next((t for t in tables if t.header[:1] == [label] and "step" in t.header), None)


def check_test_names(report: Report, tables: list[Table], ac_table: Table) -> None:
    """Every test named in the AC matrix must be a row of the Tests table."""
    tests_table = next((t for t in tables if t.header[:1] == ["test"]), None)
    referenced = [
        (line, _clean(name))
        for line, row in ac_table.rows
        for name in _TEST_SPLIT.split(ac_table.cell(row, "test"))
        if _clean(name).lower() not in EMPTY_CELLS
    ]
    if not referenced:
        return
    if tests_table is None:
        report.add("warning", "tests", "no Tests table (first column: Test); test names not verified")
        return
    known = {_clean(row[0]) for _, row in tests_table.rows if row}
    for line, name in referenced:
        if name not in known:
            report.add("error", "tests", f"test {name!r} is not defined in the Tests table", line)


def _pairs(table: Table, key_column: str, value_pattern: re.Pattern[str], value_column: str) -> set[tuple[str, str]]:
    return {
        (table.cell(row, key_column), token)
        for _, row in table.rows
        for token in value_pattern.findall(table.cell(row, value_column))
    }


def check_step_columns(
    report: Report, tables: list[Table], dec_table: Table | None, ac_table: Table | None
) -> None:
    """DEC/AC columns of the Steps table must agree with the matrices in both directions."""
    steps_table = next((t for t in tables if t.header[:1] == ["step"]), None)
    if steps_table is None:
        return
    for label, matrix in (("dec", dec_table), ("ac", ac_table)):
        if matrix is None or label not in steps_table.header:
            continue
        from_steps = {
            (step, ident)
            for step, ident in _pairs(steps_table, "step", _REQUIREMENT_TOKEN, label)
            if ident.lower().startswith(label)
        }
        from_matrix = {(step, ident) for ident, step in _pairs(matrix, label, _STEP_TOKEN, "step")}
        for step, ident in sorted(from_steps - from_matrix):
            report.add("error", "matrix", f"{step} lists {ident} but the {label.upper()} matrix does not map it to {step}")
        for step, ident in sorted(from_matrix - from_steps):
            report.add("error", "matrix", f"the {label.upper()} matrix maps {ident} to {step} but {step} does not list it")


def check_line_references(report: Report, lines: list[tuple[int, str]]) -> None:
    for number, text in lines:
        match = _LINE_REF.search(text)
        if match:
            report.add(
                "error",
                "line-ref",
                f"line-number reference {match.group(0)!r}; cite the class or function",
                number,
            )


def check_tier(report: Report, tier: str, file_count: int) -> None:
    if tier == "standard" and file_count > STANDARD_MAX_FILES:
        report.add(
            "error",
            "tier",
            f"{file_count} files exceed the standard limit of {STANDARD_MAX_FILES}; "
            "confirm the full tier with the user",
        )


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        raise InputError(f"cannot read {path}: {error}") from error


def lint(
    task_dir: Path, repo_root: Path | None = None, tier: str | None = None, in_progress: bool = False
) -> Report:
    context_text = _read(task_dir / "_context.md")
    manifest = read_manifest(context_text)
    decs, acs = read_requirements(_read(task_dir / "02-requirements.md"))
    plan = _read(task_dir / "03-plan.md")
    root = repo_root or Path(manifest.get("repo_root") or Path.cwd())

    report = Report()
    lines = visible_lines(plan)
    tables = parse_tables(lines)
    tier = check_manifest(report, manifest, tier)
    check_snapshot(report, context_text)
    files = check_file_map(report, tables, root, in_progress)
    check_interfaces(report, tables, files, root)
    steps = check_steps(report, tables)
    check_matrices(report, tables, decs, acs, steps, _token(manifest.get("ui", "")) == "true")
    check_line_references(report, lines)
    check_tier(report, tier, len(files))
    report.stats.update({"dec": len(decs), "ac": len(acs)})
    return report


def render_text(report: Report) -> str:
    rows = [
        f"{item.severity.upper():7} [{item.area}]"
        + (f" plan line {item.line}:" if item.line else ":")
        + f" {item.message}"
        for item in report.findings
    ]
    summary = ", ".join(f"{key}={value}" for key, value in sorted(report.stats.items()))
    rows.append(f"plan_lint: {report.errors} error(s), {report.warnings} warning(s); {summary}")
    return "\n".join(rows)


def render_json(report: Report) -> str:
    payload = {
        "errors": report.errors,
        "warnings": report.warnings,
        "stats": report.stats,
        "findings": [vars(item) for item in report.findings],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint an sdlc-plan artifact set.")
    parser.add_argument("task_dir", type=Path)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--tier", choices=sorted(PLAN_TIERS))
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--in-progress",
        action="store_true",
        help="implementation already started: an existing NEW path is a warning, not an error",
    )
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        report = lint(args.task_dir, args.repo_root, args.tier, args.in_progress)
    except InputError as error:
        print(f"plan_lint: {error}", file=sys.stderr)
        return 2
    print(render_json(report) if args.format == "json" else render_text(report))
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
