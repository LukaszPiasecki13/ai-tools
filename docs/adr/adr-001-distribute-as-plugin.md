# ADR-001: Distribute the toolkit as a Claude Code plugin

## Status
Accepted

## Date
2026-09-12

## Context

The toolkit has to be available in every repository worked on, across several machines, while
being maintained in one place.

Before this decision the working method was to open `ai-tools` alongside the target project in
the IDE. That does not work the way it appears to: the Claude Code documentation states that
with `--add-dir`, "CLAUDE.md files from these directories are not loaded" unless
`CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` is set. Agents and rules from an added
directory are not registered either. The target project — `waterworks-monitoring-platform` —
contained no `.claude/` directory at all, so nothing from the toolkit reached it.

Options considered:

1. **Copy the files into each project.** Immediate, no tooling. Produces divergent copies:
   this repository already demonstrated the failure mode, with the Copilot mirror carrying 6
   skills against the Claude side's 13, and several files differing by a single frontmatter key.
2. **Git submodule or symlinks.** One source, but submodules are awkward in day-to-day work and
   symlinks need administrator rights or Developer Mode on Windows.
3. **A shell script that syncs into each project.** Solves copying, not versioning: nothing
   records which version a project has, and re-running it is a manual step that gets skipped.
4. **A Claude Code plugin with the repository as its own marketplace.** Install and update are
   single commands, the version is explicit in the manifest, and the same repository serves
   every machine over HTTPS.

## Decision

Package the repository as a plugin: `.claude-plugin/plugin.json` plus
`.claude-plugin/marketplace.json` with `source: "./"`, and component directories (`agents/`,
`skills/`, `hooks/`) at the repository root as the plugin layout requires.

Installation becomes:

```
/plugin marketplace add lukaszpiasecki13/ai-tools
/plugin install ai-tools@ai-tools
```

Development uses `claude --plugin-dir /path/to/ai-tools`, which loads the working copy with no
install step.

## Consequences

### Positive
- One command to install, one to update, on any machine.
- The version installed is explicit and visible.
- Skills are namespaced (`/ai-tools:commit`), so they cannot collide with project-local ones.
- Hooks travel with the toolkit, so enforcement applies everywhere it is enabled rather than
  only where someone remembered to configure it.

### Negative
- The component directories had to move from `.claude/` to the repository root, which breaks
  any existing local setup that pointed at the old paths.
- Plugins cannot carry path-scoped rules, so a second distribution channel is required — see
  [ADR-002](adr-002-rules-installed-separately.md).
- Opening the repository as a working directory no longer makes its own agents active; that
  now requires `--plugin-dir`.

### Neutral
- The repository is both a plugin and a marketplace. That is a supported single-plugin layout,
  and it keeps everything in one place at the cost of two small manifests.
