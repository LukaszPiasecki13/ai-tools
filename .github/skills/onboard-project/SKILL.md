---
name: onboard-project
description: Set up a repository for this toolkit - detect the stack, write CLAUDE.md, install path-scoped rules and permission settings.
---

<!-- GENERATED FILE - DO NOT EDIT.
     Source: skills/onboard-project/SKILL.md
     Regenerate: python scripts/sync_copilot.py -->

# Onboard a Project

Bring a repository under this toolkit: detect what it is, install the matching rules, and
write a `CLAUDE.md` that says only what Claude cannot derive from the code itself.

Target: `$ARGUMENTS` (default: the current working directory).

## 1. Detect the stack — evidence only

Read, don't assume:

| Signal | File |
|--------|------|
| Python packaging and deps | `pyproject.toml`, `requirements*.txt`, `uv.lock`, `poetry.lock` |
| Python framework | imports of `fastapi`, `django`, `flask` in the source tree |
| Migrations | `alembic.ini`, `alembic/versions/`, `*/migrations/` |
| Node package manager | `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lockb` |
| Frontend framework | `package.json` dependencies: `@angular/core` vs `react` |
| Build/test scripts | `package.json` `scripts`, `pyproject.toml` `[tool.pytest.ini_options]`, `Makefile` |
| Firmware | `platformio.ini` |
| Existing quality gates | `.pre-commit-config.yaml`, `eslint.config.*`, `.ruff.toml`, CI workflows |

Record the **exact commands** the project already uses for install, run, test, lint and
typecheck. These go into `CLAUDE.md` verbatim — a wrong command there costs more than no
command at all.

## 2. Install the rules the stack actually needs

Rules ship with this toolkit in its `rules/` directory. Install only the matching ones:

| Stack detected | Rules |
|----------------|-------|
| Any Python | `python-coding-standards`, `error-handling-patterns`, `security-checklist` |
| Any TS/JS | `typescript-coding-standards`, `error-handling-patterns`, `security-checklist` |
| PowerShell | `powershell-coding-standards`, `security-checklist` |
| ESP32 / PlatformIO | `cpp-embedded-coding-standards` |
| Project keeps ADRs | `architecture-decisions` |

Run the toolkit's installer rather than copying by hand:

```bash
python <toolkit>/scripts/install.py --rules --target <project-path>
```

It writes into the project's `.claude/rules/`. Installing a rule for a stack the project does
not have wastes context on every session — that is the whole reason this step is selective.

## 3. Write `CLAUDE.md`

Start from `templates/project/CLAUDE.md.template` in the toolkit. Keep it **under 200 lines** —
past that, adherence drops and every session pays the tokens.

It should contain only:

- Build, test, lint, typecheck commands (exact, copy-pasteable)
- Project layout in two or three lines: where the entry points and the boundaries are
- Constraints Claude would otherwise get wrong: the virtualenv rule, the migration rule,
  the git-approval rule, anything with a "never" in it
- Domain vocabulary that does not appear in the code

It should **not** contain: generic coding standards (those are rules), dependency lists,
directory trees, or anything derivable by reading the repo.

## 4. Install permission settings

Copy `templates/project/settings.json` to the project's `.claude/settings.json`, then adjust
`permissions.deny` to the project's real secret paths. `.gitignore` prevents commits;
`permissions.deny` is what prevents reads.

Commit `.claude/settings.json`. Keep `.claude/settings.local.json` gitignored for anything
machine-specific.

## 5. Verify, then report

- Run each command written into `CLAUDE.md` and confirm it works. An unverified command is
  a bug with a long half-life.
- Start a session in the project and run `/context`; confirm `CLAUDE.md` appears under
  **Memory files**.

Report: stack detected (with the evidence file for each), rules installed, commands verified,
and anything you could not determine and need the user to answer.
