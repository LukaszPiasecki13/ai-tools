#!/usr/bin/env python3
"""Validate this toolkit against the Claude Code component schemas.

Catches the failure modes that are invisible until a component silently stops working:
frontmatter that does not parse, a skill whose name no longer matches its directory, a model
alias that does not exist, a rule whose glob can never match, a link to a file that moved,
a hook pointing at a script that is not there.

Usage:
    python scripts/validate_toolkit.py

Exits 1 when there is at least one error. Warnings are reported but do not fail the run.
"""

from __future__ import annotations

import json
import py_compile
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _frontmatter import FrontmatterError, as_list, load  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

MODEL_ALIASES = {"sonnet", "opus", "haiku", "fable", "inherit"}
AGENT_COLORS = {"red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"}
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DESCRIPTION_LIMIT = 1536  # description + when_to_use, per the skills schema

SKILL_KEYS = {
    "name", "description", "when_to_use", "disable-model-invocation", "user-invocable",
    "allowed-tools", "disallowed-tools", "model", "effort", "context", "agent", "background",
    "argument-hint", "arguments", "paths", "shell", "hooks", "metadata", "license",
    "compatibility",
}
AGENT_KEYS = {
    "name", "description", "tools", "disallowedTools", "model", "permissionMode", "maxTurns",
    "skills", "mcpServers", "hooks", "memory", "background", "effort", "isolation", "color",
    "initialPrompt", "experimental",
}

MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
STALE_PATHS = re.compile(r"\.claude/(rules|skills|agents)/")
SECRET_LIKE = re.compile(
    r"(?:ghp_[A-Za-z0-9]{20,}"
    r"|sk-[A-Za-z0-9]{20,}"
    r"|AKIA[0-9A-Z]{16}"
    r"|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)"
)


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: Path | str, message: str) -> None:
        self.errors.append(f"{self._rel(where)}: {message}")

    def warn(self, where: Path | str, message: str) -> None:
        self.warnings.append(f"{self._rel(where)}: {message}")

    @staticmethod
    def _rel(where: Path | str) -> str:
        if isinstance(where, Path):
            try:
                return str(where.relative_to(ROOT))
            except ValueError:
                return str(where)
        return where


def check_manifests(report: Report) -> None:
    plugin_path = ROOT / ".claude-plugin" / "plugin.json"
    market_path = ROOT / ".claude-plugin" / "marketplace.json"

    plugin: dict = {}
    for path in (plugin_path, market_path):
        if not path.exists():
            report.error(path, "missing - required for the repository to install as a plugin")

    if plugin_path.exists():
        try:
            plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            report.error(plugin_path, f"invalid JSON: {exc}")
            return
        name = plugin.get("name", "")
        if not name:
            report.error(plugin_path, "'name' is required")
        elif not KEBAB.match(name):
            report.error(plugin_path, f"'name' must be kebab-case, got {name!r}")
        version = plugin.get("version", "")
        if version and not re.match(r"^\d+\.\d+\.\d+", str(version)):
            report.warn(plugin_path, f"'version' should be semver, got {version!r}")
        # Component directories must sit at the plugin root, never inside .claude-plugin/.
        for component in ("skills", "agents", "hooks", "commands"):
            if (ROOT / ".claude-plugin" / component).exists():
                report.error(
                    plugin_path.parent / component,
                    "component directories belong at the plugin root, not inside .claude-plugin/",
                )

    if market_path.exists():
        try:
            market = json.loads(market_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            report.error(market_path, f"invalid JSON: {exc}")
            return
        if not market.get("owner", {}).get("name"):
            report.error(market_path, "'owner.name' is required")
        entries = market.get("plugins", [])
        if not entries:
            report.error(market_path, "'plugins' must list at least one plugin")
        for entry in entries:
            if not entry.get("source"):
                report.error(market_path, f"plugin {entry.get('name')!r} has no 'source'")
            if plugin and entry.get("name") == plugin.get("name"):
                break
        else:
            if plugin and entries:
                report.error(
                    market_path,
                    f"no entry matches the plugin name {plugin.get('name')!r} from plugin.json",
                )


def check_agents(report: Report) -> None:
    directory = ROOT / "agents"
    if not directory.is_dir():
        report.error(directory, "missing agents/ directory")
        return

    seen: dict[str, Path] = {}
    for path in sorted(directory.glob("*.md")):
        try:
            meta, body = load(path)
        except FrontmatterError as exc:
            report.error(path, str(exc))
            continue

        if not meta:
            report.error(path, "no YAML frontmatter")
            continue

        name = str(meta.get("name", ""))
        if not name:
            report.error(path, "'name' is required")
        else:
            if name != path.stem:
                report.error(path, f"'name' ({name}) must match the filename ({path.stem})")
            if not KEBAB.match(name):
                report.error(path, f"'name' must be lowercase with hyphens, got {name!r}")
            if name in seen:
                report.error(path, f"duplicate agent name, also defined in {seen[name].name}")
            seen[name] = path

        description = str(meta.get("description", "")).strip()
        if not description:
            report.error(path, "'description' is required - without it the agent is never delegated to")
        elif len(description) < 40:
            report.warn(path, "'description' is very short; it decides when this agent gets used")

        model = str(meta.get("model", "")).strip()
        if model and model not in MODEL_ALIASES and not model.startswith("claude-"):
            report.error(path, f"'model' must be an alias {sorted(MODEL_ALIASES)} or a claude-* id, got {model!r}")
        if not model:
            report.warn(path, "no 'model' set - the agent inherits the session model, which may be costlier than needed")

        color = str(meta.get("color", "")).strip()
        if color and color not in AGENT_COLORS:
            report.error(path, f"'color' must be one of {sorted(AGENT_COLORS)}, got {color!r}")

        for key in meta:
            if key not in AGENT_KEYS:
                report.warn(path, f"unrecognized frontmatter key {key!r}")

        if not body.strip():
            report.error(path, "empty system prompt")


def check_skills(report: Report) -> None:
    directory = ROOT / "skills"
    if not directory.is_dir():
        report.error(directory, "missing skills/ directory")
        return

    for skill_dir in sorted(p for p in directory.iterdir() if p.is_dir()):
        path = skill_dir / "SKILL.md"
        if not path.exists():
            report.error(skill_dir, "skill directory without a SKILL.md")
            continue

        try:
            meta, body = load(path)
        except FrontmatterError as exc:
            report.error(path, str(exc))
            continue

        if not meta:
            report.error(path, "no YAML frontmatter")
            continue

        name = str(meta.get("name", "")).strip()
        if name and name != skill_dir.name:
            report.error(path, f"'name' ({name}) must match the directory ({skill_dir.name})")
        if not KEBAB.match(skill_dir.name):
            report.error(path, f"directory name must be kebab-case, got {skill_dir.name!r}")

        description = str(meta.get("description", "")).strip()
        if not description:
            report.error(path, "'description' is required - it is how the skill gets selected")
        combined = len(description) + len(str(meta.get("when_to_use", "")))
        if combined > DESCRIPTION_LIMIT:
            report.error(path, f"description + when_to_use is {combined} chars, over the {DESCRIPTION_LIMIT} limit")

        for key in ("disable-model-invocation", "user-invocable", "background"):
            value = str(meta.get(key, "")).strip().lower()
            if value and value not in {"true", "false", "yes", "no", "on", "off", "1", "0"}:
                report.error(path, f"{key!r} must be a boolean, got {value!r}")

        if str(meta.get("context", "")).strip() not in {"", "fork"}:
            report.error(path, "'context' only accepts 'fork'")

        model = str(meta.get("model", "")).strip()
        if model and model not in MODEL_ALIASES and not model.startswith("claude-"):
            report.error(path, f"'model' must be an alias or a claude-* id, got {model!r}")

        for key in meta:
            if key not in SKILL_KEYS:
                report.warn(path, f"unrecognized frontmatter key {key!r}")

        if str(meta.get("disable-model-invocation", "")).lower() in {"true", "yes", "1"} and \
                str(meta.get("user-invocable", "true")).lower() in {"false", "no", "0"}:
            report.error(path, "skill is invocable by neither the model nor the user")

        if not body.strip():
            report.error(path, "empty skill body")


def check_rules(report: Report) -> None:
    directory = ROOT / "rules"
    if not directory.is_dir():
        report.error(directory, "missing rules/ directory")
        return

    for path in sorted(directory.glob("*.md")):
        try:
            meta, body = load(path)
        except FrontmatterError as exc:
            report.error(path, str(exc))
            continue

        if not meta:
            report.error(path, "no YAML frontmatter")
            continue

        if not str(meta.get("description", "")).strip():
            report.warn(path, "'description' is missing")

        patterns = as_list(meta.get("paths"))
        if not patterns:
            report.warn(
                path,
                "no 'paths' - this rule loads into every session and costs context even when irrelevant",
            )
        for pattern in patterns:
            if "[" in pattern and "]" not in pattern:
                report.error(path, f"glob {pattern!r} has an unterminated bracket expression and matches nothing")
            if pattern.startswith("/"):
                report.error(path, f"glob {pattern!r} is absolute; patterns are relative to the project root")

        if not body.strip():
            report.error(path, "empty rule body")


def check_hooks(report: Report) -> None:
    config = ROOT / "hooks" / "hooks.json"
    if not config.exists():
        return

    try:
        data = json.loads(config.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        report.error(config, f"invalid JSON: {exc}")
        return

    events = data.get("hooks", {})
    if not events:
        report.warn(config, "no hooks defined")

    referenced: set[Path] = set()
    for event, matchers in events.items():
        for matcher in matchers:
            for hook in matcher.get("hooks", []):
                command = str(hook.get("command", ""))
                for match in re.finditer(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\"'\s]+)", command):
                    referenced.add(ROOT / match.group(1))
                if hook.get("type") == "command" and not command:
                    report.error(config, f"{event}: command hook with no command")

    for script in sorted(referenced):
        if not script.exists():
            report.error(config, f"references {script.relative_to(ROOT)}, which does not exist")

    for script in sorted((ROOT / "hooks" / "scripts").glob("*.py")):
        try:
            py_compile.compile(str(script), doraise=True, cfile=str(Path("/tmp") / f"{script.stem}.pyc"))
        except py_compile.PyCompileError as exc:
            report.error(script, f"does not compile: {exc}")


def check_pre_commit_hooks_manifest(report: Report) -> None:
    """Validates .pre-commit-hooks.yaml - hooks THIS repo exposes to other projects via the
    `pre-commit` framework (the opposite direction from a project's own .pre-commit-config.yaml).

    Not a real YAML parser - the file is a flat list of hook definitions and a few regex lines
    catch the one failure mode that matters: `entry` pointing at a script that moved or never
    existed, which breaks every consumer's hook silently until their pre-commit run fails.
    """
    manifest = ROOT / ".pre-commit-hooks.yaml"
    if not manifest.exists():
        return

    text = manifest.read_text(encoding="utf-8")
    ids = re.findall(r"^-\s*id:\s*(\S+)", text, re.MULTILINE)
    if not ids:
        report.error(manifest, "no hook 'id' entries found")
    seen: set[str] = set()
    for hook_id in ids:
        if hook_id in seen:
            report.error(manifest, f"duplicate hook id: {hook_id}")
        seen.add(hook_id)
        if not KEBAB.match(hook_id):
            report.error(manifest, f"hook id must be kebab-case, got {hook_id!r}")

    interpreters = {"python3", "python", "sh", "bash"}
    for match in re.finditer(r"^\s*entry:\s*(.+)$", text, re.MULTILINE):
        parts = match.group(1).strip().split()
        script_token = parts[1] if parts and parts[0] in interpreters else (parts[0] if parts else "")
        if script_token and not script_token.startswith("-") and not (ROOT / script_token).exists():
            report.error(manifest, f"entry references {script_token}, which does not exist")


def strip_code_blocks(text: str) -> str:
    """Blank out fenced code blocks so illustrative snippets are not linted as prose."""
    out, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            out.append("")
            continue
        out.append("" if fenced else line)
    return "\n".join(out)


def check_links_and_secrets(report: Report) -> None:
    skip_dirs = {".git", "node_modules", "__pycache__", ".github"}
    for path in sorted(ROOT.rglob("*.md")):
        if any(part in skip_dirs for part in path.parts):
            continue
        raw = path.read_text(encoding="utf-8", errors="ignore")
        prose = strip_code_blocks(raw)

        for match in SECRET_LIKE.finditer(raw):
            report.error(path, f"looks like a committed credential: {match.group(0)[:12]}...")

        for match in MARKDOWN_LINK.finditer(prose):
            target = match.group(1)
            if target.startswith(("http://", "https://", "mailto:", "#", "<")):
                continue

            resolved = (path.parent / target.split("#")[0]).resolve()
            if resolved.exists():
                continue

            # A target whose own parent directory does not exist is an illustrative path
            # ("path/to/file.ts"), not a link into this repository. Only flag links that
            # point somewhere real enough to be a genuine mistake.
            if not resolved.parent.exists():
                continue

            report.error(path, f"broken link: {target}")
            if STALE_PATHS.search(target):
                report.warn(path, "links into the pre-2.0 .claude/ layout; sources now live at the repository root")


def main() -> int:
    report = Report()
    check_manifests(report)
    check_agents(report)
    check_skills(report)
    check_rules(report)
    check_hooks(report)
    check_pre_commit_hooks_manifest(report)
    check_links_and_secrets(report)

    for warning in report.warnings:
        print(f"WARN  {warning}")
    for error in report.errors:
        print(f"ERROR {error}")

    counts = f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)"
    if report.errors:
        print(f"\nFAILED: {counts}")
        return 1
    print(f"\nOK: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
