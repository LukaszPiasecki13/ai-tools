#!/usr/bin/env python3
"""Automated setup for new project: install templates + all rules + settings in one command.

Usage:
    python scripts/setup.py                    # current directory
    python scripts/setup.py /path/to/project   # specific project
    python scripts/setup.py --help
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates" / "project"
INSTALL_SCRIPT = ROOT / "scripts" / "install.py"


def setup_project(project_path: Path) -> None:
    """Complete setup: templates + all rules."""
    if not project_path.exists():
        print(f"❌ Project path does not exist: {project_path}")
        sys.exit(1)

    print(f"📦 Setting up ai-tools in: {project_path}")
    print()

    # Step 1: Copy templates
    print("📄 Installing templates...")
    templates = [
        ("CLAUDE.md.template", "CLAUDE.md"),
        ("settings.json", "settings.json"),
        ("mcp.json.example", "mcp.json"),
    ]
    for src_name, dst_name in templates:
        src = TEMPLATES_DIR / src_name
        dst = project_path / dst_name

        if src.exists():
            if dst.exists():
                print(f"  ℹ️  {dst_name} already exists, skipping")
            else:
                dst.write_text(src.read_text())
                print(f"  ✅ Created {dst_name}")
        else:
            print(f"  ⚠️  Template not found: {src_name}")

    print()

    # Step 2: Update .gitignore
    print("📋 Updating .gitignore...")
    gitignore_path = project_path / ".gitignore"
    gitignore_content = ""

    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text()

    # Add claude patterns if not present
    patterns = [
        ".claude/settings.local.json",  # machine-local settings
    ]

    for pattern in patterns:
        if pattern not in gitignore_content:
            gitignore_content += f"\n{pattern}\n"
            print(f"  ✅ Added pattern: {pattern}")

    gitignore_path.write_text(gitignore_content)
    print()

    # Step 3: Install all rules
    print("📚 Installing all coding standards rules...")
    rules = [
        "python-coding-standards",
        "typescript-coding-standards",
        "cpp-embedded-coding-standards",
        "error-handling-patterns",
        "security-checklist",
        "architecture-decisions",
    ]

    cmd = [
        sys.executable,
        str(INSTALL_SCRIPT),
        "--target",
        str(project_path),
        "--only",
        ",".join(rules),
        "--settings",
    ]

    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print(f"❌ Installation failed with exit code {result.returncode}")
        sys.exit(1)

    print()
    print("✨ Setup complete!")
    print()
    print("📌 Next steps:")
    print("  1. Review and adapt CLAUDE.md for your project")
    print("  2. Install ai-tools plugin (one-time global setup):")
    print("     Claude Code Settings → Plugins → Add → https://github.com/lukaszpiasecki13/ai-tools")
    print("  3. git add .claude CLAUDE.md .gitignore && git commit")
    print()
    print("🚀 Rules auto-load on file read. Agents/skills/hooks come from the plugin.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Quick setup: templates + rules + settings for new project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "project",
        nargs="?",
        default=".",
        help="Path to project (default: current directory)",
    )

    args = parser.parse_args()
    project_path = Path(args.project).resolve()

    setup_project(project_path)


if __name__ == "__main__":
    main()
