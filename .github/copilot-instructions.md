<!-- GENERATED FILE - DO NOT EDIT.
     Source: CLAUDE.md
     Regenerate: python scripts/sync_copilot.py -->

# AI Toolkit — working on this repository

This repository **is** a Claude Code plugin. It is not a project that uses a toolkit; it is
the toolkit. Everything here is distributed to other repositories, so a mistake in this repo
shows up in every project that installs it.

## Source of truth

| Directory | Contains | Reaches a project via |
|-----------|----------|------------------------|
| `agents/` | Subagent definitions | the plugin |
| `skills/` | Skills and slash commands | the plugin |
| `hooks/` | Enforcement hooks + their scripts | the plugin |
| `rules/` | Path-scoped coding standards | `scripts/install.py` (plugins cannot carry rules) |
| `templates/` | Project `CLAUDE.md`, settings, MCP config | copied by `onboard-project` |
| `.github/instructions|agents|skills/` | **Generated** Copilot mirror | never edited by hand |

`.github/` under those three directories and `.github/copilot-instructions.md` are build
output. Edit the source, then run `python scripts/sync_copilot.py`. CI fails on drift.

## Before every commit

```bash
python scripts/validate_toolkit.py      # schemas, manifests, links, secrets
python -m unittest discover -s tests    # hook behaviour, including its false-positive set
python scripts/sync_copilot.py          # regenerate the mirror
```

## Which mechanism to use

Getting this wrong is the most expensive mistake in this repo: it either burns context on
every session or silently never loads.

| Use | When | Cost |
|-----|------|------|
| **Rule** (`rules/`) | An invariant for a file type that must hold every time that type is touched | Loads whenever a matching file is read — keep it short |
| **Skill** (`skills/`) | Know-how for a technology or a procedure, needed only sometimes | Loads on description match — free until used |
| **Command** (a skill with `disable-model-invocation: true`) | A repeatable action the user starts deliberately | Loads only when typed |
| **Agent** (`agents/`) | Work that deserves its own context window and tool restrictions | A separate context; isolates cost |
| **Hook** (`hooks/`) | A rule that must hold regardless of what the model decides | Runs every matching event — keep it fast and fail-open |

Two corollaries:

- A "never" that actually matters belongs in a **hook**, not in prose. Instructions are
  context, not enforcement.
- Framework-specific guidance belongs in a **skill**, not a rule. Angular detail loaded while
  editing a React file is pure waste.

## Model policy

Assign the cheapest model that does the job correctly, and say why in the agent file.

| Model | For | Agents |
|-------|-----|--------|
| `haiku` | Search, retrieval, summarizing, drafting docs | `explorer`, `documentation-writer` |
| `sonnet` | Root-cause reasoning, review judgment, test design, hardware risk | `debugger`, `code-reviewer`, `test-writer`, `esp32-firmware-engineer` |
| `opus` | Reserve for genuinely hard architecture work; not set as a default anywhere | — |

Never put a reasoning-heavy agent on `haiku` to save tokens. A missed defect costs more than
the model did.

## Authoring standards

**Agents.** `name` matches the filename. `description` states when to delegate — it is the
only thing the router sees. Grant the narrowest `tools` set that works; a reviewer that can
write is not a reviewer.

**Skills.** `description` decides whether the skill is ever used: name the trigger words a
real prompt would contain. `description` + `when_to_use` must stay under 1536 characters.
Use `${CLAUDE_SKILL_DIR}` for paths inside the skill, never a repo-relative path.

**Rules.** Always scope with `paths`. A rule without `paths` loads into every session forever.

**Hooks.** Fail open on malformed input, never block on a formatting concern, and add both a
deny case and an allow case to `tests/test_hooks.py` for every pattern you introduce.

## Communication style

- Direct and technical. No preamble, no filler.
- Cite exact locations: `path/to/file.ts:42`.
- Label anything unverified as **suggestion**.

## Core behavioural rules

**Truthfulness.** Never invent a fact, a command, a CVE number, a version, or an API. Verify
it or say you did not. Everything written here propagates into other projects.

**Change management.** Read a file before editing it. Make changes in reviewable steps.
Confirm before deleting files or dropping data. Never discard committed-but-unpushed work
without explicit approval.

**Git.** On the default branch, ask before any operation that writes (`commit`, `push`,
`rebase`, `merge`, `reset`). On a dedicated working branch the user has asked you to use,
committing is expected; pushing and history rewrites still need approval.

**Data handling.** No PII, payment or health data in this repo. Never commit a secret. If a
task appears to need one, stop and ask for a sanitized alternative.

**Evidence.** Cite the file and line for every claim about the codebase, and state the
command you ran to verify behaviour.

## Before acting

1. What do I need to know? — list the unknowns.
2. Where is it? — name the likely file before opening one.
3. What is the minimal read? — a section, not the whole file.
4. What is my hypothesis? — then confirm or refute it with a tool.
5. What does "done" look like? — know it before starting.

## Web access

Fetching documentation, specs, datasheets and package metadata needs no approval. Prefer
checking a primary source over answering from memory — especially for version numbers,
security advisories and API shapes.
