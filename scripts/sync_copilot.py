#!/usr/bin/env python3
"""Generate the GitHub Copilot mirror from the Claude Code sources.

The toolkit keeps one set of sources - `rules/`, `agents/`, `skills/`, `CLAUDE.md` - and
projects them into the layout Copilot reads:

    rules/<name>.md        ->  .github/instructions/<name>.instructions.md   (paths -> applyTo)
    agents/<name>.md       ->  .github/agents/<name>.agent.md
    skills/<name>/*        ->  .github/skills/<name>/*
    CLAUDE.md              ->  .github/copilot-instructions.md

Everything under those `.github/` directories is generated output. Edit the source, re-run
this script; never edit the mirror, because the next run overwrites it.

Usage:
    python scripts/sync_copilot.py           # regenerate the mirror
    python scripts/sync_copilot.py --check   # fail if the mirror is out of date (CI)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _frontmatter import as_list, load  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MIRROR_DIRS = [
    ROOT / ".github" / "instructions",
    ROOT / ".github" / "agents",
    ROOT / ".github" / "skills",
]

def banner(source: str, note: str = "") -> str:
    lines = ["<!-- GENERATED FILE - DO NOT EDIT.", f"     Source: {source}"]
    if note:
        lines.append(f"     {note}")
    lines.append("     Regenerate: python scripts/sync_copilot.py -->")
    return "\n".join(lines) + "\n"

# Frontmatter keys that mean nothing to Copilot and would only add noise to the mirror.
CLAUDE_ONLY_AGENT_KEYS = {
    "color", "memory", "permissionMode", "isolation", "background", "effort", "maxTurns",
    "initialPrompt", "experimental", "disallowedTools", "mcpServers", "hooks", "skills",
}


def yaml_scalar(value: str) -> str:
    """Quote a scalar for YAML when it contains characters that would break parsing."""
    if any(ch in value for ch in ":#\n'\"") or value.strip() != value:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
        return f'"{escaped}"'
    return value


def render_instruction(path: Path) -> str:
    meta, body = load(path)
    patterns = as_list(meta.get("paths"))
    lines = ["---", f"name: {yaml_scalar(path.stem)}"]
    description = str(meta.get("description", "")).strip()
    if description:
        lines.append(f"description: {yaml_scalar(description)}")
    if patterns:
        # Copilot takes one comma-separated string, not a list.
        lines.append(f"applyTo: {yaml_scalar(','.join(patterns))}")
    lines.append("---")
    return "\n".join(lines) + "\n\n" + banner(f"rules/{path.name}") + "\n" + body.rstrip() + "\n"


def render_agent(path: Path) -> str:
    meta, body = load(path)
    lines = ["---"]
    for key in ("name", "description", "tools", "model"):
        value = meta.get(key)
        if value in (None, ""):
            continue
        rendered = ", ".join(value) if isinstance(value, list) else str(value)
        lines.append(f"{key}: {yaml_scalar(rendered)}")
    lines.append("---")
    dropped = sorted(k for k in meta if k in CLAUDE_ONLY_AGENT_KEYS)
    note = f"Claude-only keys not mirrored: {', '.join(dropped)}" if dropped else ""
    head = banner(f"agents/{path.name}", note)
    return "\n".join(lines) + "\n\n" + head + "\n" + body.rstrip() + "\n"


def render_skill(path: Path) -> str:
    meta, body = load(path)
    lines = ["---"]
    for key in ("name", "description"):
        value = meta.get(key)
        if value:
            lines.append(f"{key}: {yaml_scalar(str(value))}")
    lines.append("---")
    return "\n".join(lines) + "\n\n" + banner(f"skills/{path.parent.name}/SKILL.md") + "\n" + body.rstrip() + "\n"


def build() -> dict[Path, bytes]:
    """Compute the complete expected mirror as {path: content}."""
    expected: dict[Path, bytes] = {}

    for rule in sorted((ROOT / "rules").glob("*.md")):
        target = ROOT / ".github" / "instructions" / f"{rule.stem}.instructions.md"
        expected[target] = render_instruction(rule).encode("utf-8")

    for agent in sorted((ROOT / "agents").glob("*.md")):
        target = ROOT / ".github" / "agents" / f"{agent.stem}.agent.md"
        expected[target] = render_agent(agent).encode("utf-8")

    for skill_dir in sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir()):
        source = skill_dir / "SKILL.md"
        if not source.exists():
            continue
        expected[ROOT / ".github" / "skills" / skill_dir.name / "SKILL.md"] = render_skill(source).encode("utf-8")
        # Supporting files (scripts, reference docs) are copied verbatim.
        for extra in sorted(skill_dir.rglob("*")):
            if extra.is_dir() or extra.name == "SKILL.md":
                continue
            relative = extra.relative_to(skill_dir)
            expected[ROOT / ".github" / "skills" / skill_dir.name / relative] = extra.read_bytes()

    claude_md = ROOT / "CLAUDE.md"
    if claude_md.exists():
        content = banner("CLAUDE.md") + "\n" + claude_md.read_text(encoding="utf-8").rstrip() + "\n"
        expected[ROOT / ".github" / "copilot-instructions.md"] = content.encode("utf-8")

    return expected


def current() -> dict[Path, bytes]:
    found: dict[Path, bytes] = {}
    for directory in MIRROR_DIRS:
        if directory.is_dir():
            for path in sorted(directory.rglob("*")):
                if path.is_file():
                    found[path] = path.read_bytes()
    instructions = ROOT / ".github" / "copilot-instructions.md"
    if instructions.exists():
        found[instructions] = instructions.read_bytes()
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report drift instead of writing")
    args = parser.parse_args()

    expected, existing = build(), current()

    stale = sorted(set(existing) - set(expected))
    changed = sorted(p for p, content in expected.items() if existing.get(p) != content)

    if args.check:
        if not stale and not changed:
            print(f"OK: Copilot mirror is in sync ({len(expected)} files)")
            return 0
        for path in changed:
            print(f"DRIFT  {path.relative_to(ROOT)}")
        for path in stale:
            print(f"STALE  {path.relative_to(ROOT)}")
        print("\nFAILED: mirror is out of date. Run: python scripts/sync_copilot.py")
        return 1

    for path in stale:
        path.unlink()
    for path, content in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    for directory in MIRROR_DIRS:
        if directory.is_dir():
            for candidate in sorted(directory.rglob("*"), reverse=True):
                if candidate.is_dir() and not any(candidate.iterdir()):
                    candidate.rmdir()

    print(f"Wrote {len(changed)} file(s), removed {len(stale)} stale file(s); mirror has {len(expected)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
