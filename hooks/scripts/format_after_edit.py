#!/usr/bin/env python3
"""PostToolUse(Edit|Write) formatter: apply the project's own formatter to the edited file.

Formatting an edited file by hand is the most repeated action in a coding session and the
easiest to automate away. The rule this follows: **only run a formatter the project already
uses.** Reformatting a repository that never opted in produces a diff full of noise that
nobody asked for, so each formatter runs only when both its config and its binary are present.

Silent on success. Fails open: a formatter that is missing, slow or broken never blocks work.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

TIMEOUT_SECONDS = 20

# extension -> (config files that mark the project as opted in, command builder)
FORMATTERS: dict[str, tuple[tuple[str, ...], str, list[str]]] = {
    ".py": (("pyproject.toml", "ruff.toml", ".ruff.toml"), "ruff", ["format"]),
    ".ts": ((".prettierrc", ".prettierrc.json", ".prettierrc.yaml", ".prettierrc.yml",
             ".prettierrc.js", "prettier.config.js", "prettier.config.mjs"), "npx",
            ["--no-install", "prettier", "--write"]),
    ".cpp": ((".clang-format",), "clang-format", ["-i"]),
}
# Extensions that share another extension's toolchain.
ALIASES = {
    ".tsx": ".ts", ".js": ".ts", ".jsx": ".ts", ".mjs": ".ts", ".cjs": ".ts",
    ".mts": ".ts", ".cts": ".ts", ".css": ".ts", ".scss": ".ts", ".json": ".ts",
    ".c": ".cpp", ".cc": ".cpp", ".h": ".cpp", ".hpp": ".cpp", ".ino": ".cpp",
    ".pyi": ".py",
}


def find_config(start: Path, names: tuple[str, ...], stop_at: Path) -> bool:
    """Walk up from the edited file looking for one of the config files, stopping at the
    project root so a stray config in a parent directory cannot opt the project in."""
    current = start if start.is_dir() else start.parent
    while True:
        for name in names:
            candidate = current / name
            if candidate.exists():
                # pyproject.toml only counts when it actually configures ruff.
                if name == "pyproject.toml":
                    try:
                        if "[tool.ruff" not in candidate.read_text(encoding="utf-8", errors="ignore"):
                            continue
                    except OSError:
                        continue
                return True
        if current == stop_at or current == current.parent:
            return False
        current = current.parent


def main() -> None:
    try:
        payload = json.load(sys.stdin)
        file_path = payload.get("tool_input", {}).get("file_path", "")
        cwd = payload.get("cwd", "")
    except Exception:
        sys.exit(0)

    if not isinstance(file_path, str) or not file_path:
        sys.exit(0)

    target = Path(file_path)
    if not target.is_file():
        sys.exit(0)

    suffix = ALIASES.get(target.suffix.lower(), target.suffix.lower())
    entry = FORMATTERS.get(suffix)
    if entry is None:
        sys.exit(0)

    config_names, binary, args = entry
    project_root = Path(cwd) if cwd else target.parent

    if not find_config(target, config_names, project_root):
        sys.exit(0)
    if shutil.which(binary) is None:
        sys.exit(0)

    try:
        before = target.read_bytes()
        subprocess.run(
            [binary, *args, str(target)],
            capture_output=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
        after = target.read_bytes()
    except (OSError, subprocess.SubprocessError):
        sys.exit(0)

    if before != after:
        # Tell Claude the file on disk no longer matches what it just wrote, so it re-reads
        # before editing again instead of working from a stale copy.
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": (
                        f"{target.name} was reformatted on disk by {binary}. "
                        "Re-read it before making further edits."
                    ),
                }
            },
            sys.stdout,
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
