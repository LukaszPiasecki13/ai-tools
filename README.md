# AI Toolkit

> This repository is public for reference only. No license is granted to use, copy, or
> install it — see [LICENSE](LICENSE).

A personal engineering toolkit for [Claude Code](https://code.claude.com/docs), packaged as a
plugin: subagents, skills, slash commands, path-scoped coding standards, and hooks that
enforce the rules rather than just describing them.

Covers Python/FastAPI, TypeScript (React and Angular), PowerShell, and ESP32/PlatformIO
firmware.

## Install

**1. The plugin** — agents, skills, commands and hooks, in every project:

```
/plugin marketplace add lukaszpiasecki13/ai-tools
/plugin install ai-tools@ai-tools
```

**2. The rules** — coding standards that load when a matching file is touched. Plugins cannot
carry path-scoped rules, so they install separately:

```bash
git clone https://github.com/lukaszpiasecki13/ai-tools
cd ai-tools

python scripts/install.py --user                    # every project on this machine
python scripts/install.py --target ../my-project    # one project, rules matched to its stack
python scripts/install.py --list                    # what is available
```

The installer detects the stack from `pyproject.toml`, `package.json`, `platformio.ini` and
friends, and installs only the matching rules — an irrelevant rule costs context in every
session.

**3. A new project** — run `/ai-tools:onboard-project` in it. It detects the stack, installs
the right rules, writes a `CLAUDE.md` from the template, and sets up `permissions.deny` so
credential files cannot be read.

### Developing the toolkit itself

```bash
claude --plugin-dir /path/to/ai-tools
```

Loads the working copy directly, so edits take effect on `/reload-plugins` with no install
step. This is also the answer to "I want the toolkit available while working in another
repository": load it as a plugin rather than opening both repositories side by side —
`--add-dir` does **not** load `CLAUDE.md`, rules or agents from the added directory unless
`CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` is set.

## What is inside

| | Count | |
|---|---|---|
| **Agents** | 6 | `explorer`, `debugger`, `code-reviewer`, `test-writer`, `documentation-writer`, `esp32-firmware-engineer` |
| **Commands** | 9 | `/ai-tools:commit`, `pr-description`, `adr`, `security-scan`, `test-focus`, `onboard-project`, `fastapi-endpoint`, `react-feature`, `toolkit-validate` |
| **Skills** | 16 | API and database design, React and Angular patterns, testing, git workflows, debugging, domain modelling, UI verification, the `prepare-work` pipeline, Jira extraction, ESP32 serial monitoring |
| **Rules** | 7 | Python, TypeScript, PowerShell, embedded C++, security, error handling, ADRs |
| **Hooks** | 3 | destructive-command guard, credential-read guard, format-on-edit |

Full inventory with descriptions and trigger conditions: [docs/CATALOG.md](docs/CATALOG.md).

## The hooks

These are the part that does not depend on the model cooperating:

- **`guard_bash`** blocks force pushes, `reset --hard`, `clean -f`, wholesale `checkout .`,
  recursive deletes of root/home/wildcard paths, piping a downloaded script into a shell,
  `DROP TABLE`, reading `.env` through `cat`, and `pip install` outside a virtual environment.
- **`guard_secrets`** blocks reads of `.env`, private keys, service-account files and
  credential stores — `.gitignore` stops a commit, nothing else stops a read.
- **`format_after_edit`** runs the project's own formatter after each edit, and **only** if
  that project already has the formatter configured.

Every pattern has a deny case and an allow case in [tests/test_hooks.py](tests/test_hooks.py);
a guard with false positives gets switched off, and then it protects nothing.

## Layout

```
agents/           subagent definitions            -> plugin
skills/           skills and slash commands       -> plugin
hooks/            hooks.json + Python scripts     -> plugin
rules/            path-scoped standards           -> scripts/install.py
templates/        project CLAUDE.md, settings, MCP config
scripts/          validator, Copilot sync, installer
tests/            hook regression tests
docs/             architecture, catalog, cost model, ADRs
.github/          GENERATED Copilot mirror + CI
```

`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` make the repository
installable as a single-plugin marketplace.

## GitHub Copilot

The same sources are mirrored into the layout Copilot reads —
`.github/instructions/*.instructions.md` (with `paths` translated to `applyTo`),
`.github/agents/`, `.github/skills/`, `.github/copilot-instructions.md`.

The mirror is **generated**. Edit the source, then:

```bash
python scripts/sync_copilot.py
```

CI fails if the mirror has drifted, so the two assistants cannot disagree.

## Development

```bash
pytest                                  # toolkit validation + hook behaviour
python scripts/sync_copilot.py --check  # mirror + catalog drift
claude plugin validate .                # the official manifest check
```

Every script and test is standard-library only — no install step, and they behave the same in
CI as in a fresh clone (CI runs `python -m unittest discover -s tests`, which the same test
files support with zero dependencies). `pytest` is the recommended way to run them locally;
it auto-discovers the same tests and adds `-k` filtering and `--lf`. Python 3.9+ is the only
hard requirement.

Conventions for adding a component, and the rule/skill/command/agent/hook decision table, are
in [CLAUDE.md](CLAUDE.md).

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — how the pieces fit and how distribution works
- [docs/CATALOG.md](docs/CATALOG.md) — every component, what it does, when it triggers
- [docs/COST-MODEL.md](docs/COST-MODEL.md) — where tokens go and the model policy
- [docs/MIGRATION-2.0.md](docs/MIGRATION-2.0.md) — what changed in 2.0 and what to do about it
- [docs/adr/](docs/adr/) — the decisions behind the structure

## License

All rights reserved — see [LICENSE](LICENSE). This repository is published so the toolkit is
visible and reachable from any of the author's own machines; it is not an open-source release.
No permission is granted to use, copy, modify, or install this code, including via the plugin
marketplace, without prior written permission from the copyright holder.
