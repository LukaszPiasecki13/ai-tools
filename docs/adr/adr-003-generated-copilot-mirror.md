# ADR-003: Generate the Copilot mirror from the Claude Code sources

## Status
Accepted

## Date
2026-09-12

## Context

The toolkit must serve both Claude Code and GitHub Copilot, which read different layouts:
Copilot uses `.github/instructions/*.instructions.md` with an `applyTo` glob string,
`.github/agents/*.agent.md`, and `.github/copilot-instructions.md`.

Both sets were previously maintained by hand, and had already diverged: 13 skills on the Claude
side against 6 mirrored, 7 rules against 6, an `esp32-firmware-engineer` agent that existed in
only one place, and files differing by stray frontmatter keys. Nothing detected any of it.

Options considered:

1. **Keep maintaining both by hand.** The current state is the evidence against it.
2. **Drop Copilot support.** Would work, but discards a tool still in use.
3. **Generate one side from the other**, and fail the build when the generated side is edited
   or falls behind.

## Decision

`rules/`, `agents/`, `skills/` and `CLAUDE.md` are the sources. `scripts/sync_copilot.py`
projects them into the Copilot layout, translating what differs between the two formats:

- `paths: ["**/*.py", "**/*.{ts,tsx}"]` → `applyTo: **/*.py,**/*.{ts,tsx}` (list to
  comma-separated string, brace groups preserved)
- Claude-only agent keys (`color`, `memory`, `permissionMode`, …) are dropped, and the banner
  names which ones were dropped
- Every generated file carries a "DO NOT EDIT" header naming its source

`sync_copilot.py --check` reports drift and is a CI step, so an edit to the mirror or a
forgotten regeneration fails the build rather than going unnoticed for months.

The same approach generates `docs/CATALOG.md` from component frontmatter, for the same reason:
an inventory maintained by hand is wrong within a week.

## Consequences

### Positive
- The two assistants cannot disagree; drift is a build failure, not a discovery.
- Adding a rule or skill is one file, and the mirror follows.
- The `applyTo` translation is done once, correctly, instead of by hand each time. The naive
  version of this conversion splits `**/*.{ts,tsx}` on its comma and silently produces globs
  that match nothing — which is exactly the bug the round-trip test caught.

### Negative
- A generation step to remember. Mitigated by CI, and by `/ai-tools:toolkit-validate`.
- Copilot-specific tuning is not possible in the mirror; it would have to be expressed in the
  generator.

### Neutral
- `.github/instructions`, `.github/agents`, `.github/skills` and `.github/copilot-instructions.md`
  are build artifacts that are committed, because Copilot reads them from the repository.
