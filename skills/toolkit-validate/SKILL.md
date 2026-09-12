---
name: toolkit-validate
description: Validate this toolkit - frontmatter, manifests, cross-references and the generated Copilot mirror.
disable-model-invocation: true
user-invocable: true
allowed-tools: Bash(python:*) Bash(python3:*) Bash(git status:*) Bash(git diff:*)
---

# Validate the Toolkit

Run the toolkit's own checks before committing changes to it:

```bash
python scripts/validate_toolkit.py
python scripts/sync_copilot.py --check
```

The first validates structure and content; the second fails if the generated `.github/`
mirror has drifted from the sources in `agents/`, `skills/` and `rules/`.

## On failure

Fix the source file, never the generated mirror — `.github/` is output, and editing it there
is undone by the next sync. Re-run `python scripts/sync_copilot.py` to regenerate.

## What is not covered by the scripts

These need a human or a live session:

- **Does the skill trigger?** A skill with a vague `description` never gets invoked. Test it
  by starting a session and giving the kind of prompt it should match.
- **Does the agent stay in its lane?** Give it a task adjacent to its purpose and see whether
  it declines or drifts.
- **Do the hooks fire?** Trigger the matching event and check the debug log.

Claude Code also ships its own manifest check, which validates the plugin the way the
marketplace does:

```bash
claude plugin validate .
```
