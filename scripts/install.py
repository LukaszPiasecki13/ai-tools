#!/usr/bin/env python3
"""Install the toolkit's path-scoped rules into a project or into your user scope.

Why this exists: a Claude Code plugin can carry skills, agents, commands and hooks, but the
plugin manifest has no `rules` field. Path-scoped rules are read from `.claude/rules/` in a
project or `~/.claude/rules/` for your account, so they need their own install step. Everything
else in this toolkit travels with the plugin and does not need copying.

Typical use:

    python scripts/install.py --user                      # rules for every project on this machine
    python scripts/install.py --target ../my-project      # rules for one project
    python scripts/install.py --target ../my-project --settings
    python scripts/install.py --list

Re-running is safe: files this installer wrote are refreshed, and anything it did not write is
left alone.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _frontmatter import as_list, load  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / "rules"
SUBDIR = "ai-tools"  # rules land in a namespaced subdirectory, never loose in rules/
MANIFEST = ".ai-tools-install.json"

# The knowledge-base validator has to live inside the target repo, not travel with the plugin:
# pre-commit and CI run it with no Claude Code involved at all. Tracked by its own manifest so
# re-running refreshes what this installer wrote, and a marker string lets it recognise (and
# safely adopt) a copy that was placed by hand before this installer path existed.
KB_VALIDATOR_DIR = ROOT / "skills" / "knowledge-base" / "scripts"
KB_VALIDATOR_MARKERS = {
    "kb_validate.py": "Walidator bazy wiedzy dla agentów AI",
    "test_kb_validate.py": "Testy walidatora bazy wiedzy",
}
KB_VALIDATOR_MANIFEST = ".ai-tools-kb-validate.json"

# Which rules a stack needs. Installing more than this spends context on every session.
PROFILES: dict[str, tuple[str, ...]] = {
    "python": ("python-coding-standards", "error-handling-patterns", "security-checklist"),
    "typescript": ("typescript-coding-standards", "error-handling-patterns", "security-checklist"),
    "powershell": ("powershell-coding-standards", "security-checklist"),
    "embedded": ("cpp-embedded-coding-standards",),
    "adr": ("architecture-decisions",),
}


def available() -> dict[str, Path]:
    return {path.stem: path for path in sorted(RULES_DIR.glob("*.md"))}


def detect(target: Path) -> set[str]:
    """Infer which profiles a project needs from files that are actually present."""
    profiles: set[str] = set()

    if any(target.glob("**/pyproject.toml")) or any(target.glob("**/requirements*.txt")):
        profiles.add("python")

    for package_json in target.glob("**/package.json"):
        if "node_modules" in package_json.parts:
            continue
        profiles.add("typescript")
        break

    if any(target.glob("**/*.ps1")) or any(target.glob("**/*.psm1")):
        profiles.add("powershell")
    if any(target.glob("**/platformio.ini")):
        profiles.add("embedded")
    if (target / "docs" / "adr").is_dir() or (target / "docs" / "decisions").is_dir():
        profiles.add("adr")

    return profiles


def resolve(profiles: set[str], explicit: list[str]) -> list[str]:
    if explicit:
        return sorted(set(explicit))
    selected: set[str] = set()
    for profile in profiles:
        selected.update(PROFILES.get(profile, ()))
    return sorted(selected)


def install_rules(destination: Path, names: list[str], link: bool, dry_run: bool) -> list[str]:
    rules = available()
    unknown = [name for name in names if name not in rules]
    if unknown:
        raise SystemExit(f"Unknown rule(s): {', '.join(unknown)}. Run --list to see what exists.")

    rules_root = destination / ".claude" / "rules" / SUBDIR
    manifest_path = destination / ".claude" / "rules" / SUBDIR / MANIFEST

    previously: list[str] = []
    if manifest_path.exists():
        try:
            previously = json.loads(manifest_path.read_text(encoding="utf-8")).get("rules", [])
        except (json.JSONDecodeError, OSError):
            previously = []

    if dry_run:
        for name in names:
            print(f"  would install {name}.md -> {rules_root / (name + '.md')}")
        for stale in sorted(set(previously) - set(names)):
            print(f"  would remove   {stale}.md (no longer selected)")
        return names

    rules_root.mkdir(parents=True, exist_ok=True)

    for stale in sorted(set(previously) - set(names)):
        stale_path = rules_root / f"{stale}.md"
        if stale_path.exists() or stale_path.is_symlink():
            stale_path.unlink()
            print(f"  removed   {stale}.md")

    for name in names:
        source, target = rules[name], rules_root / f"{name}.md"
        if target.exists() or target.is_symlink():
            target.unlink()
        if link:
            target.symlink_to(source)
        else:
            shutil.copy2(source, target)
        print(f"  installed {name}.md")

    manifest_path.write_text(
        json.dumps(
            {
                "source": "https://github.com/lukaszpiasecki13/ai-tools",
                "installed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "mode": "symlink" if link else "copy",
                "rules": names,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return names


def install_settings(destination: Path, dry_run: bool) -> None:
    template = ROOT / "templates" / "project" / "settings.json"
    target = destination / ".claude" / "settings.json"

    if not template.exists():
        print(f"  skipped settings: {template} is missing")
        return
    if target.exists():
        print(f"  skipped settings: {target} already exists - merge permissions.deny by hand")
        return
    if dry_run:
        print(f"  would install settings.json -> {target}")
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(template, target)
    print(f"  installed settings.json -> {target}")


def _looks_like_kb_validator(path: Path, name: str) -> bool:
    marker = KB_VALIDATOR_MARKERS.get(name)
    if marker is None:
        return False
    try:
        return marker in path.read_text(encoding="utf-8", errors="ignore")[:400]
    except OSError:
        return False


def install_kb_validator(destination: Path, dry_run: bool) -> bool:
    """Copy the knowledge-base validator (and its tests) into <destination>/scripts/.

    Safe to re-run: files this installer wrote (tracked by KB_VALIDATOR_MANIFEST) are
    refreshed. A file that already exists and is NOT tracked is left alone unless its content
    matches the known validator marker - which lets a copy placed by hand before this command
    existed be adopted instead of silently overwritten or permanently skipped.
    """
    scripts_root = destination / "scripts"
    manifest_path = scripts_root / KB_VALIDATOR_MANIFEST
    managed = manifest_path.exists()
    installed_any = False

    for name in KB_VALIDATOR_MARKERS:
        source = KB_VALIDATOR_DIR / name
        target = scripts_root / name
        if target.exists() and not managed and not _looks_like_kb_validator(target, name):
            print(f"  skipped {name}: {target} already exists and is not managed by this installer")
            continue
        if dry_run:
            print(f"  would install {name} -> {target}")
            installed_any = True
            continue
        scripts_root.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        print(f"  installed {name}")
        installed_any = True

    if dry_run or not installed_any:
        return installed_any

    manifest_path.write_text(
        json.dumps(
            {
                "source": "https://github.com/lukaszpiasecki13/ai-tools",
                "installed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "files": list(KB_VALIDATOR_MARKERS),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return installed_any


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--target", type=Path, help="project directory to install into")
    scope.add_argument("--user", action="store_true", help="install into ~/.claude/rules (every project)")
    parser.add_argument("--only", default="", help="comma-separated rule names, overriding stack detection")
    parser.add_argument("--settings", action="store_true", help="also install the project settings template")
    parser.add_argument(
        "--validator", action="store_true",
        help="also install the knowledge-base validator into scripts/ (requires --target)",
    )
    parser.add_argument("--link", action="store_true", help="symlink instead of copy (updates follow the repo)")
    parser.add_argument("--dry-run", action="store_true", help="print what would happen, change nothing")
    parser.add_argument("--list", action="store_true", help="list available rules and profiles")
    args = parser.parse_args(argv)

    if args.list:
        print("Rules:")
        for name, path in available().items():
            meta, _ = load(path)
            patterns = ", ".join(as_list(meta.get("paths"))) or "(always loaded)"
            print(f"  {name:<32} {patterns}")
        print("\nProfiles:")
        for profile, names in PROFILES.items():
            print(f"  {profile:<12} {', '.join(names)}")
        return 0

    if args.validator and args.user:
        parser.error("--validator installs into a project's scripts/ - use --target, not --user")

    if args.user:
        destination = Path.home()
        print(f"Installing rules for every project on this machine ({destination / '.claude' / 'rules' / SUBDIR})")
        profiles = set(PROFILES)  # user scope: path globs keep them dormant until they match
    else:
        destination = (args.target or Path.cwd()).resolve()
        if not destination.is_dir():
            raise SystemExit(f"Target {destination} is not a directory")
        profiles = detect(destination)
        print(f"Target: {destination}")
        print(f"Detected: {', '.join(sorted(profiles)) or 'nothing recognizable'}")

    names = resolve(profiles, [n.strip() for n in args.only.split(",") if n.strip()])
    did_something = bool(names)
    if names:
        install_rules(destination, names, args.link, args.dry_run)
    else:
        print("No rules selected. Use --only to choose explicitly, or --list to see what exists.")

    if args.settings and not args.user:
        install_settings(destination, args.dry_run)
        did_something = True

    if args.validator and not args.user:
        did_something = install_kb_validator(destination, args.dry_run) or did_something

    if not did_something:
        return 1

    print(
        "\nInstalled. The rest of the toolkit - skills, agents, commands, hooks - "
        "travels with the plugin:\n"
        "  /plugin marketplace add lukaszpiasecki13/ai-tools\n"
        "  /plugin install ai-tools@ai-tools"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:  # piping into head/less closes stdout early
        sys.stdout = None
        raise SystemExit(0)
