#!/usr/bin/env python3
"""Generate the GitHub Copilot mirror and the component catalog from the Claude Code sources.

The toolkit keeps one set of sources - `rules/`, `agents/`, `skills/`, `CLAUDE.md` - and
projects them into two generated outputs:

1. The layout Copilot reads:
    rules/<name>.md        ->  .github/instructions/<name>.instructions.md   (paths -> applyTo)
    agents/<name>.md       ->  .github/agents/<name>.agent.md
    skills/<name>/*        ->  .github/skills/<name>/*
    CLAUDE.md              ->  .github/copilot-instructions.md

2. `docs/CATALOG.md` - the inventory of every component, so a hand-maintained list
   cannot go stale.

Everything listed above is generated output. Edit the source, re-run this script; never edit
a generated file directly, because the next run overwrites it.

Usage:
    python scripts/sync_copilot.py           # regenerate the mirror and the catalog
    python scripts/sync_copilot.py --check   # fail if either is out of date (CI)
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
MIRROR_DIRS = [
    ROOT / ".github" / "instructions",
    ROOT / ".github" / "agents",
    ROOT / ".github" / "skills",
]

TRUTHY = {"true", "yes", "on", "1"}


def truthy(value: object) -> bool:
    return str(value).strip().lower() in TRUTHY


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


def first_sentence(text: str, limit: int = 160) -> str:
    text = " ".join(str(text).split())
    for stop in (". ", " - ", " — "):
        if stop in text:
            text = text.split(stop)[0]
            break
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def catalog_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "_None._\n"
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |" for row in rows]
    return "\n".join(out) + "\n"


def build_catalog() -> str:
    """Render docs/CATALOG.md - the inventory of every component, derived from the sources."""
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
        banner("agents/, skills/, rules/, hooks/hooks.json").rstrip(),
        "",
        "# Component catalog",
        "",
        "Every component in the toolkit, derived from the component files themselves.",
        "",
        "## Agents",
        "",
        "Delegated automatically when a task matches the description, or invoked by name.",
        "",
        catalog_table(["Agent", "Model", "Purpose"], agents),
        "",
        "## Commands",
        "",
        "Typed deliberately. Hidden from automatic model invocation, so they never fire on their own.",
        "",
        catalog_table(["Command", "Arguments", "Context", "Purpose"], commands),
        "",
        "## Skills",
        "",
        "Loaded on demand when the description matches the task — free until used.",
        "",
        catalog_table(["Skill", "Invocation", "Purpose"], skills),
        "",
        "## Rules",
        "",
        "Path-scoped standards. Installed with `scripts/install.py`; they load when a matching file is read.",
        "",
        catalog_table(["Rule", "Applies to", "Purpose"], rules),
        "",
        "## Hooks",
        "",
        "Deterministic enforcement — these run regardless of what the model decides.",
        "",
        catalog_table(["Event", "Matcher", "Script", "Action"], hooks_rows),
    ]
    return "\n".join(parts).rstrip() + "\n"


def build() -> dict[Path, bytes]:
    """Compute the complete expected set of generated files as {path: content}."""
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

    expected[CATALOG] = build_catalog().encode("utf-8")

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
    if CATALOG.exists():
        found[CATALOG] = CATALOG.read_bytes()
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
            print(f"OK: Copilot mirror and catalog are in sync ({len(expected)} files)")
            return 0
        for path in changed:
            print(f"DRIFT  {path.relative_to(ROOT)}")
        for path in stale:
            print(f"STALE  {path.relative_to(ROOT)}")
        print("\nFAILED: out of date. Run: python scripts/sync_copilot.py")
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
