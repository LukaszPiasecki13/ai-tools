"""Shared paths for the toolkit test suite.

Tests are plain stdlib `unittest.TestCase` classes, so `python -m unittest discover -s tests`
keeps working with zero dependencies - that is what CI runs, per the toolkit's stdlib-only
policy. pytest auto-discovers the same classes, so `pytest` also works and is the preferred
way to run them locally (better output, `-k` filtering, `--lf`).
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOKS = ROOT / "hooks" / "scripts"
SCRIPTS = ROOT / "scripts"
