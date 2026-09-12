# Architecture

How the toolkit is put together, and why it is put together that way.

## The problem this solves

A personal toolkit is only useful in the repositories where the work happens. Getting it there
is the whole design problem, and it has a constraint that is easy to miss:

> `--add-dir` gives Claude access to another directory, but **CLAUDE.md files from these
> directories are not loaded** unless `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` is set.
> — [Claude Code docs, Memory](https://code.claude.com/docs/en/memory)

So "open the toolkit repository next to the project" does not distribute the toolkit. The
instructions, the rules and the agents stay where they are. Copying files into each project
works but produces divergent copies within weeks — the state this repository was in before
version 2.0, where the Copilot mirror had drifted to 6 skills against the Claude side's 13.

## Two channels, one source

The plugin manifest carries skills, agents, commands, hooks and MCP servers. It has **no
`rules` field** — path-scoped rules are read from `.claude/rules/` in a project or
`~/.claude/rules/` for an account. That single fact forces the shape of the distribution:

```
                     ┌──────────────────────────────────────┐
                     │          ai-tools repository          │
                     │                                       │
   agents/ ──┐       │  single source of truth per component │
   skills/ ──┼──────►│                                       │
   hooks/  ──┘       └───────────┬───────────────┬───────────┘
                                 │               │
                    plugin       │               │   scripts/install.py
                    (versioned,  │               │   (stack-detected subset)
                     one command)│               │
                                 ▼               ▼
                        ┌─────────────┐   ┌──────────────────┐
                        │ any project │   │ .claude/rules/   │
                        │ with the    │   │ or ~/.claude/    │
                        │ plugin on   │   │ rules/           │
                        └─────────────┘   └──────────────────┘

   rules/ ──┐
   agents/ ─┼──► scripts/sync_copilot.py ──► .github/  (generated Copilot mirror)
   skills/ ─┘
   CLAUDE.md
```

Installing the plugin is one command and is versioned. Installing the rules is one command and
is selective. Neither involves copying a file by hand, which is what makes drift possible.

## Component model

Five mechanisms, each with a different loading cost and a different guarantee. Choosing
correctly is the main design decision in this repository.

| Mechanism | Guarantee | Loading | Right for |
|-----------|-----------|---------|-----------|
| Rule | Present in context whenever a matching file is read | Automatic, path-scoped | Invariants tied to a file type |
| Skill | Present when the model judges it relevant | On description match | Technology know-how, procedures |
| Command | Present when the user types it | On invocation | Deliberate, repeatable actions |
| Agent | Separate context and tool set | On delegation | Work that should not pollute the main thread |
| Hook | **Executed** regardless of the model | Every matching event | Rules that must not be negotiable |

The distinction that matters most is the last row. Everything above it is *context* — the
model reads it and usually complies. A hook is *enforcement* — it runs whether the model
agrees or not. The Claude Code documentation is explicit about this:

> Claude treats them as context, not enforced configuration. To block an action regardless of
> what Claude decides, use a PreToolUse hook instead.

That is why the constraints that previously sat in prose ("never `pip install` outside the
virtualenv", "never discard uncommitted work") are now hook patterns with tests, and the prose
is a summary of what the hook does rather than a request.

## Enforcement layers

Three layers, from advisory to absolute:

1. **Instructions** — `CLAUDE.md`, rules, skills. Shape behaviour. Can be reasoned around.
2. **Hooks** — `guard_bash`, `guard_secrets`. Deterministic, ship with the plugin, apply in
   every project that has it enabled. Fail open by design: a guard that crashes must not be
   able to halt all work.
3. **Permissions** — `permissions.deny` in a project's `.claude/settings.json`. Enforced by
   the client itself. Cannot be reached by the model at all.

Secrets are covered by all three, because the failure is unrecoverable: once a credential is
in a transcript it must be rotated. `.gitignore` is not part of this picture — it prevents a
commit and does nothing about a read.

## Generated artifacts

Three files/directories in this repository are output, never input:

| Generated | From | By |
|-----------|------|----|
| `.github/instructions/*.instructions.md` | `rules/*.md` (`paths` → `applyTo`) | `sync_copilot.py` |
| `.github/agents/`, `.github/skills/`, `.github/copilot-instructions.md` | `agents/`, `skills/`, `CLAUDE.md` | `sync_copilot.py` |
| `docs/CATALOG.md` | every component's frontmatter | `generate_catalog.py` |

Each carries a "DO NOT EDIT" banner naming its source, and CI fails when either has drifted.
A generated inventory cannot go stale; a hand-written one always does.

## Verification

The toolkit tests itself, with standard-library Python only so the checks run the same way in
CI and in a fresh clone:

- `scripts/validate_toolkit.py` — frontmatter schemas, name/directory agreement, model
  aliases, glob sanity, manifest consistency, broken links, committed credentials.
- `tests/test_hooks.py` — every guard pattern has a deny case **and** an allow case. The allow
  cases are the important half: a guard with false positives gets disabled, and a disabled
  guard protects nothing.
- `scripts/sync_copilot.py --check` and `generate_catalog.py --check` — drift detection.

## Versioning

`.claude-plugin/plugin.json` carries the version; users receive an update when it is bumped.
The repository is its own single-plugin marketplace (`source: "./"`), so
`/plugin marketplace add lukaszpiasecki13/ai-tools` is enough to find it.

Breaking changes — a renamed rule, a moved directory, a changed command name — get a major
bump and an entry in [MIGRATION-2.0.md](MIGRATION-2.0.md)-style notes, because installed
copies do not migrate themselves.
