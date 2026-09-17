---
name: setup-ai-tools
description: Automated setup for new repository - run this once in new repo to install templates and all coding rules at once.
---

<!-- GENERATED FILE - DO NOT EDIT.
     Source: skills/setup-ai-tools/SKILL.md
     Regenerate: python scripts/sync_copilot.py -->

# Quick Setup: AI Tools for New Repository

Automates full setup in one command: copies templates + installs all coding rules + updates .gitignore.

## Usage

```bash
# In your new repository
python path/to/ai-tools/scripts/setup.py
```

or

```bash
python path/to/ai-tools/scripts/setup.py /path/to/repo
```

Rules are plain file copies. Changes in ai-tools only reach a project when the installer is re-run there — re-run `python scripts/install.py --target /path/to/repo --only <rules>` whenever ai-tools changes and you want a project to pick them up.

## What this does

1. **Copies templates** — `CLAUDE.md`, `settings.json`, `mcp.json`
2. **Updates .gitignore** — adds `.claude/settings.local.json` (excludes machine-local settings)
3. **Installs all rules** — all 6 coding standards rules → `.claude/rules/ai-tools/`

## Result

After running, you have:

```
.claude/
├── settings.json                    # Comprehensive permissions (deny/ask/allow)
├── rules/ai-tools/
│   ├── python-coding-standards.md
│   ├── typescript-coding-standards.md
│   ├── cpp-embedded-coding-standards.md
│   ├── error-handling-patterns.md
│   ├── security-checklist.md
│   ├── architecture-decisions.md
│   └── .ai-tools-install.json
```

Plus:
- `CLAUDE.md` — project-specific constraints and commands (customize this)
- `.mcp.json` — MCP configuration template
- `.gitignore` — updated with Claude patterns

## Next steps

1. **Customize `CLAUDE.md`** — add project commands, constraints, vocabulary
2. **Install ai-tools plugin** (one-time global, in Claude Code):
   - Settings → Plugins → Add Plugin → `https://github.com/lukaszpiasecki13/ai-tools`
3. **Commit and push** — all changes are git-tracked

## How it all works

- **Rules** auto-load on file read in your project (path-scoped)
- **Plugin** (agents, skills, hooks, commands) loads globally in Claude Code
- **Settings** provides comprehensive permission patterns (deny destructive, ask git, etc.)

**No two separate steps needed.** Setup script does everything at once.
