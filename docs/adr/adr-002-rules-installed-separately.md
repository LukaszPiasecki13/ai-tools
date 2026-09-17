# ADR-002: Install path-scoped rules separately from the plugin

## Status
Accepted

## Date
2026-09-12

## Context

[ADR-001](adr-001-distribute-as-plugin.md) makes the toolkit a plugin. The plugin manifest
supports `skills`, `commands`, `agents`, `hooks`, `mcpServers`, `lspServers`, `outputStyles`,
themes and monitors. It has no field for rules.

Path-scoped rules — markdown files with a `paths` glob that load when a matching file is read —
are discovered only in `.claude/rules/` within a project or `~/.claude/rules/` for the account.
A plugin cannot place them there.

Options considered:

1. **Convert each rule into a skill with a `paths` frontmatter.** Skills support `paths` and
   travel with the plugin, so this would need no second channel. But it changes the guarantee:
   a rule is placed in context whenever a matching file is read, whereas a skill is loaded when
   the model judges it relevant. Coding standards that apply "sometimes, if it seems relevant"
   are not standards.
2. **Ship rules as plain files and let the user copy them.** Back to manual copying and drift,
   which ADR-001 exists to eliminate.
3. **A small installer that places the right rules in the right location.**

## Decision

Keep rules as rules, and distribute them with `scripts/install.py`:

- `--user` installs into `~/.claude/rules/ai-tools/`, applying to every project on the machine.
  The documentation recommends this location for shared rules because it avoids the external-
  import approval dialog that project rules sourced from outside the project trigger.
- `--target <path>` installs into one project's `.claude/rules/ai-tools/`, after detecting the
  stack from `pyproject.toml`, `package.json`, `platformio.ini` and similar markers, and
  selecting only the matching rules.

Installed files go in an `ai-tools/` subdirectory with a manifest recording what was written,
so a re-run can remove rules that are no longer selected without touching anything else.

Path globs make user-scope installation safe: a Python rule scoped to `**/*.py` stays dormant
in a firmware project.

## Consequences

### Positive
- Rules keep the stronger guarantee: present whenever a matching file is touched.
- Selective installation keeps irrelevant standards out of context — all seven rules total
  roughly 7 400 tokens, while a Python backend session needs about 3 200 of them.
- Re-running the installer is idempotent and cleans up its own stale files.

### Negative
- Two installation steps instead of one, which has to be documented clearly or it gets missed.
- Rules updated in the repository do not reach a project until the installer is re-run there.

### Neutral
- GitHub Copilot reads `~/.claude/rules` as one of its user-profile instruction locations, so
  a user-scope install happens to serve both assistants.
