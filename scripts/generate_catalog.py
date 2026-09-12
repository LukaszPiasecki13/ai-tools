#!/usr/bin/env python3
"""Generate docs/CATALOG.md - the inventory of every component in the toolkit.

A hand-maintained inventory is wrong within a week. This one is derived from the component
files themselves, so it cannot drift from what is actually installed.

Usage:
    python scripts/generate_catalog.py           # write docs/CATALOG.md
    python scripts/generate_catalog.py --check   # fail if out of date (CI)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _frontmatter import as_list, load  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "docs" / "CATALOG.md"

TRUTHY = {"true", "yes", "on", "1"}


def truthy(value: object) -> bool:
    return str(value).strip().lower() in TRUTHY


def first_sentence(text: str, limit: int = 160) -> str:
    text = " ".join(str(text).split())
    for stop in (". ", " - ", " — "):
        if stop in text:
            text = text.split(stop)[0]
            break
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "_None._\n"
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |" for row in rows]
    return "\n".join(out) + "\n"


def build() -> str:
    agents, commands, skills, rules = [], [], [], []

    for path in sorted((ROOT / "agents").glob("*.md")):
        meta, _ = load(path)
        agents.append([
            f"`{meta.get('name', path.stem)}`",
            str(meta.get("model", "inherit")),
            first_sentence(meta.get("description", "")),
        ])

    for skill_dir in sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir()):
        source = skill_dir / "SKILL.md"
        if not source.exists():
            continue
        meta, _ = load(source)
        name = skill_dir.name
        description = first_sentence(meta.get("description", ""))

        if truthy(meta.get("disable-model-invocation")):
            hint = str(meta.get("argument-hint", "")).strip()
            isolated = "fork" if str(meta.get("context", "")).strip() == "fork" else ""
            commands.append([f"`/ai-tools:{name}`", f"`{hint}`" if hint else "—", isolated or "—", description])
        else:
            auto = "model-invoked" if not truthy(meta.get("user-invocable", "true")) else "model or user"
            skills.append([f"`{name}`", auto, description])

    for path in sorted((ROOT / "rules").glob("*.md")):
        meta, _ = load(path)
        patterns = as_list(meta.get("paths"))
        rules.append([
            f"`{path.stem}`",
            ", ".join(f"`{p}`" for p in patterns) if patterns else "**always loaded**",
            first_sentence(meta.get("description", "")),
        ])

    hooks_rows = []
    hooks_file = ROOT / "hooks" / "hooks.json"
    if hooks_file.exists():
        config = json.loads(hooks_file.read_text(encoding="utf-8"))
        for event, matchers in config.get("hooks", {}).items():
            for matcher in matchers:
                for hook in matcher.get("hooks", []):
                    command = str(hook.get("command", ""))
                    script = command.split("/")[-1].strip("\"'") if "/" in command else command
                    hooks_rows.append([
                        f"`{event}`",
                        f"`{matcher.get('matcher', '*')}`",
                        f"`{script}`",
                        str(hook.get("statusMessage", "")).rstrip("."),
                    ])

    parts = [
        "<!-- GENERATED FILE - DO NOT EDIT.",
        "     Regenerate: python scripts/generate_catalog.py -->",
        "",
        "# Component catalog",
        "",
        "Every component in the toolkit, derived from the component files themselves.",
        "",
        "## Agents",
        "",
        "Delegated automatically when a task matches the description, or invoked by name.",
        "",
        table(["Agent", "Model", "Purpose"], agents),
        "",
        "## Commands",
        "",
        "Typed deliberately. Hidden from automatic model invocation, so they never fire on their own.",
        "",
        table(["Command", "Arguments", "Context", "Purpose"], commands),
        "",
        "## Skills",
        "",
        "Loaded on demand when the description matches the task — free until used.",
        "",
        table(["Skill", "Invocation", "Purpose"], skills),
        "",
        "## Rules",
        "",
        "Path-scoped standards. Installed with `scripts/install.py`; they load when a matching file is read.",
        "",
        table(["Rule", "Applies to", "Purpose"], rules),
        "",
        "## Hooks",
        "",
        "Deterministic enforcement — these run regardless of what the model decides.",
        "",
        table(["Event", "Matcher", "Script", "Action"], hooks_rows),
    ]
    return "\n".join(parts).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the catalog is out of date")
    args = parser.parse_args()

    content = build()
    existing = CATALOG.read_text(encoding="utf-8") if CATALOG.exists() else ""

    if args.check:
        if content == existing:
            print("OK: catalog is up to date")
            return 0
        print("FAILED: docs/CATALOG.md is out of date. Run: python scripts/generate_catalog.py")
        return 1

    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    CATALOG.write_text(content, encoding="utf-8")
    print(f"Wrote {CATALOG.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
