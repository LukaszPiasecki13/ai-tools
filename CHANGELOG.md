# Changelog

All notable changes to this toolkit. Versions follow the `version` field in
`.claude-plugin/plugin.json`; installed copies update when it is bumped.

## [Unreleased]

### Fixed
- **Breaking:** `.claude-plugin/plugin.json` and `marketplace.json` declared `"license":
  "MIT"` — an explicit grant to use, copy and redistribute this code — with no `LICENSE`
  file in the repository to back it. Added `LICENSE` (all rights reserved, viewing only) and
  changed both manifests to `"SEE LICENSE IN LICENSE"`. The repository stays public; no
  license is now granted for reuse or redistribution.

### Changed
- `scripts/generate_catalog.py` merged into `scripts/sync_copilot.py` — one script now
  produces both the Copilot mirror and `docs/CATALOG.md`, and `--check` covers both. Fewer
  scripts to keep in sync, one less step in CI.
- `scripts/validate_toolkit.py` lost the unused `--strict` flag; nothing invoked it.
- Toolkit validation moved into `tests/test_validate.py`, so `pytest` (or `python -m
  unittest discover -s tests`) alone covers both validation and hook behaviour.
- Local test runner is now `pytest` (added `pytest.ini`, `tests/conftest.py`); CI keeps
  `python -m unittest discover -s tests`, since the same test files support both with zero
  dependencies.
- Pre-commit checklist shortened from three commands to two:
  `pytest` then `python scripts/sync_copilot.py`.

## [2.0.0] — 2026-09-12

Restructured from a loose `.claude/` directory into a versioned Claude Code plugin with
enforced constraints, validation and CI. Full narrative: [docs/MIGRATION-2.0.md](docs/MIGRATION-2.0.md).

### Added
- Plugin packaging: `.claude-plugin/plugin.json` and a single-plugin `marketplace.json`.
- 9 slash commands: `commit`, `pr-description`, `adr`, `security-scan`, `test-focus`,
  `onboard-project`, `fastapi-endpoint`, `react-feature`, `toolkit-validate`.
- 3 enforcement hooks: `guard_bash`, `guard_secrets`, `format_after_edit`, with 45 regression
  cases in `tests/test_hooks.py` covering both denials and false positives.
- `react-patterns` skill: React 19, TanStack Query, react-hook-form + zod, Radix, Tailwind.
- `scripts/validate_toolkit.py`, `sync_copilot.py`, `generate_catalog.py`, `install.py` —
  standard library only.
- `templates/project/`: `CLAUDE.md.template`, `settings.json` with `permissions.deny`,
  `mcp.json.example`.
- Documentation: `README.md`, `docs/ARCHITECTURE.md`, `docs/COST-MODEL.md`,
  generated `docs/CATALOG.md`, and ADRs 001–005.
- CI workflow validating schemas, hooks, mirror drift and catalog freshness.

### Changed
- **Breaking:** `agents/`, `skills/`, `rules/` moved from `.claude/` to the repository root,
  as the plugin layout requires. History preserved via `git mv`.
- **Breaking:** `frontend-coding-standards` → `typescript-coding-standards`, now framework
  agnostic; Angular material moved to `angular-patterns`.
- **Breaking:** `frontend-patterns` → `angular-patterns`.
- `.github/` instructions, agents and skills are now generated output, not hand-maintained.
- Agent models assigned by the cost of an undetected error: `haiku` for `explorer` and
  `documentation-writer`, `sonnet` for `debugger`, `code-reviewer`, `test-writer` and
  `esp32-firmware-engineer`.
- `code-reviewer` lost `Edit`/`Write`; a reviewer that patches its own findings cannot be audited.
- Toolkit `CLAUDE.md` rewritten around working on the toolkit, 41% smaller; project-specific
  rules moved into `templates/project/CLAUDE.md.template`.
- `python-coding-standards` no longer mandates `uv` unconditionally — it follows whatever the
  project already uses, which removes the contradiction with the `.venv` constraint.

### Fixed
- `frontend-coding-standards` glob omitted `**/*.tsx`, so the rule never loaded while editing a
  React component.
- `security-checklist` claimed `python-jose` was unmaintained since 2022; it has 3.4.0 and
  3.5.0 releases. Replaced with the actual advisories (CVE-2024-33663, CVE-2024-33664,
  CVE-2024-29370) and the `>=3.4.0` floor.
- `CLAUDE.md` referenced `permissions.deny` in a `.claude/settings.json` that had been deleted.
- Dead references: `/setup-matt-pocock-skills` in `to-spec`, `.claudeignore` in
  `jira-board-extractor`, `../../CLAUDE.md` and `.claude/rules/*` in every agent.
- `security-checklist` and `error-handling-patterns` globs extended to `.jsx`/`.psm1`.

## [1.x] — before 2026-09

Agents, skills and path-scoped rules maintained as two hand-synchronized copies under
`.claude/` and `.github/`.
