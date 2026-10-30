#!/usr/bin/env python3
"""Drift snapshot for an sdlc task directory: write, check, extend.

Stdlib only. Replaces LLM drift checks with a hash comparison that costs no tokens.

Usage:
    python drift_check.py TASK_DIR snapshot  [--format text|json]
    python drift_check.py TASK_DIR check     [--format text|json]
    python drift_check.py TASK_DIR extend    [--format text|json]

Tracked files = union of the file map in 01-context.md (first column Path/Sciezka) and,
when it exists, the file map in 03-plan.md (first column Path). Relative paths resolve
against repo_root from _context.md.

snapshot  rewrites the "## Drift snapshot" section of _context.md (Gate C).
check     compares recorded file: lines with the current state; never writes.
extend    runs check, then appends file: lines for tracked paths not recorded yet;
          never changes recorded lines and writes nothing when drift exists (Gate P).
          The snapshot describes the repo before implementation; sdlc-implement uses it
          once (Phase 1) and then relies on its own baseline.

Snapshot lines (one per line, absolute paths):
    head: {repo} = {sha | unknown}                     informational
    status: {repo} = {clean | N-changed | unknown}     informational
    file: {path} = {blob sha | MISSING}                drift = any value differs

The file hash is the git blob SHA-1 of the raw bytes (same as
`git hash-object --no-filters`), so it is deterministic outside a repository too.

Exit codes: 0 no drift (or written), 1 drift found, 2 unusable input.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

SECTION = "## Drift snapshot"
MISSING = "MISSING"
UNKNOWN = "unknown"
PATH_HEADERS = {"path", "ścieżka", "sciezka"}

_REPO_ROOT = re.compile(r"^\s*(?:[-*]\s+)?`?repo_root`?\s*:\s*(?P<value>.+?)\s*$", re.MULTILINE)
_SNAPSHOT_LINE = re.compile(
    r"^\s*(?P<kind>head|status|file)\s*:\s*(?P<key>.+?)\s*=\s*(?P<value>\S+)\s*$"
)
_TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)*\|?\s*$")
_NEXT_SECTION = re.compile(r"^## ", re.MULTILINE)


class InputError(Exception):
    """The task directory cannot be processed."""


@dataclass
class Result:
    drift: list[dict[str, str]] = field(default_factory=list)
    info: list[str] = field(default_factory=list)
    unrecorded: list[str] = field(default_factory=list)
    written: list[str] = field(default_factory=list)


def blob_sha(path: Path) -> str:
    if not path.is_file():
        return MISSING
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data, usedforsecurity=False).hexdigest()


def _git(repo: Path, *args: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return completed.stdout if completed.returncode == 0 else None


def repo_state(repo: Path) -> tuple[str, str]:
    head = _git(repo, "rev-parse", "HEAD")
    status = _git(repo, "status", "--short")
    if status is None:
        status_text = UNKNOWN
    else:
        changed = sum(1 for line in status.splitlines() if line.strip())
        status_text = "clean" if changed == 0 else f"{changed}-changed"
    return (head.strip() if head else UNKNOWN), status_text


def _key(path: Path | str) -> str:
    return os.path.normcase(str(path))


def _cells(line: str) -> list[str]:
    body = line.strip().removeprefix("|").removesuffix("|")
    return [cell.strip().strip("`* ").strip() for cell in body.split("|")]


def _header_key(cell: str) -> str:
    return re.sub(r"\(.*?\)", "", cell).strip().lower()


def table_paths(text: str) -> list[str]:
    """First-column values of every table whose first header cell is Path/Sciezka."""
    lines = text.splitlines()
    paths: list[str] = []
    for index in range(len(lines) - 1):
        header, separator = lines[index], lines[index + 1]
        if not (header.lstrip().startswith("|") and _TABLE_SEPARATOR.match(separator)):
            continue
        if _header_key(_cells(header)[0]) not in PATH_HEADERS:
            continue
        for row in lines[index + 2 :]:
            if not row.lstrip().startswith("|"):
                break
            value = _cells(row)[0]
            if value and value not in {"-", "..."}:
                paths.append(value)
    return paths


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        raise InputError(f"cannot read {path}: {error}") from error


def repo_root_of(context_text: str) -> Path:
    match = _REPO_ROOT.search(context_text)
    if not match:
        raise InputError("_context.md has no repo_root line")
    return Path(match["value"].strip("`'\" "))


def tracked_files(task_dir: Path, root: Path) -> list[Path]:
    context_map, plan_map = task_dir / "01-context.md", task_dir / "03-plan.md"
    if not context_map.is_file():
        raise InputError(f"missing {context_map}")
    seen: dict[str, Path] = {}
    for source in (context_map, plan_map):
        if not source.is_file():
            continue
        for raw in table_paths(_read(source)):
            path = Path(raw)
            resolved = (path if path.is_absolute() else root / path).resolve()
            seen.setdefault(_key(resolved), resolved)
    return list(seen.values())


def _section_bounds(text: str) -> tuple[int, int] | None:
    start = text.find(SECTION)
    if start < 0:
        return None
    body_start = start + len(SECTION)
    following = _NEXT_SECTION.search(text, body_start)
    return start, (following.start() if following else len(text))


def _section_body(text: str) -> str:
    bounds = _section_bounds(text)
    return text[bounds[0] + len(SECTION) : bounds[1]] if bounds else ""


def _replace_section(text: str, body: str) -> str:
    block = f"{SECTION}\n{body.strip(chr(10))}\n"
    bounds = _section_bounds(text)
    if bounds is None:
        return text.rstrip("\n") + "\n\n" + block
    start, end = bounds
    tail = text[end:]
    return text[:start] + block + ("\n" + tail if tail else "")


def recorded(context_text: str) -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {"head": {}, "status": {}, "file": {}}
    for line in _section_body(context_text).splitlines():
        match = _SNAPSHOT_LINE.match(line)
        if match:
            entries[match["kind"]][match["key"]] = match["value"]
    return entries


def snapshot(task_dir: Path, result: Result) -> None:
    context_path = task_dir / "_context.md"
    text = _read(context_path)
    root = repo_root_of(text)
    head, status = repo_state(root)
    lines = [f"head: {root} = {head}", f"status: {root} = {status}"]
    lines += [f"file: {path} = {blob_sha(path)}" for path in tracked_files(task_dir, root)]
    context_path.write_text(_replace_section(text, "\n".join(lines)), encoding="utf-8")
    result.written = lines


def check(task_dir: Path, result: Result) -> None:
    text = _read(task_dir / "_context.md")
    root = repo_root_of(text)
    entries = recorded(text)
    if not entries["file"]:
        raise InputError("Drift snapshot has no file: lines; run 'snapshot' at Gate C first")
    for raw, expected in entries["file"].items():
        current = blob_sha(Path(raw))
        if current != expected:
            result.drift.append({"path": raw, "recorded": expected, "current": current})
    for repo, expected in entries["head"].items():
        head, _ = repo_state(Path(repo))
        if head != expected:
            result.info.append(f"head changed in {repo}: {expected} -> {head}")
    known = {_key(raw) for raw in entries["file"]}
    tracked = tracked_files(task_dir, root)
    result.unrecorded = [str(path) for path in tracked if _key(path) not in known]


def extend(task_dir: Path, result: Result) -> None:
    check(task_dir, result)
    if result.drift:
        return
    added = [f"file: {raw} = {blob_sha(Path(raw))}" for raw in result.unrecorded]
    if added:
        context_path = task_dir / "_context.md"
        text = _read(context_path)
        body = "\n".join([_section_body(text).strip("\n"), *added])
        context_path.write_text(_replace_section(text, body), encoding="utf-8")
    result.written = added
    result.unrecorded = []


def render(result: Result, as_json: bool) -> str:
    if as_json:
        return json.dumps(vars(result), ensure_ascii=False, indent=2)
    rows = [f"DRIFT {d['path']}: recorded {d['recorded']}, current {d['current']}" for d in result.drift]
    rows += [f"INFO {line}" for line in result.info]
    rows += [f"UNRECORDED {path}" for path in result.unrecorded]
    rows += [f"WRITTEN {line}" for line in result.written]
    rows.append(f"drift_check: {len(result.drift)} drifted file(s)")
    return "\n".join(rows)


MODES = {"snapshot": snapshot, "check": check, "extend": extend}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write or verify an sdlc drift snapshot.")
    parser.add_argument("task_dir", type=Path)
    parser.add_argument("mode", choices=sorted(MODES))
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    result = Result()
    try:
        MODES[args.mode](args.task_dir, result)
    except InputError as error:
        print(f"drift_check: {error}", file=sys.stderr)
        return 2
    print(render(result, args.format == "json"))
    return 1 if result.drift else 0


if __name__ == "__main__":
    sys.exit(main())
