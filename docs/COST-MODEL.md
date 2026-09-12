# Cost model

Where tokens actually go, and the rules this toolkit follows to keep the bill proportional to
the work. Figures are character counts from the files in this repository, divided by four for
a rough token estimate — good enough to compare options, not a billing statement.

## The four tiers

| Tier | Loaded | Paid | Example |
|------|--------|------|---------|
| Project `CLAUDE.md` | Every session, always | Every session | build commands, project constraints |
| Rules (`paths`) | When a matching file is read | Once per session, per file type touched | `python-coding-standards` |
| Skills | When the description matches the task | Only when used | `react-patterns` |
| Agents | In their own context window | Once per delegation, isolated from the main thread | `code-reviewer` |

The tier decides the price. A paragraph in `CLAUDE.md` is charged on every single session
forever; the same paragraph in a skill is free until the day it is needed. This is why the
mechanism decision in [CLAUDE.md](../CLAUDE.md) matters more than the writing.

## Measured cost of this toolkit

**Rules** — paid only when a file of that type is touched:

| Rule | ~tokens |
|------|--------:|
| `architecture-decisions` | 385 |
| `error-handling-patterns` | 660 |
| `security-checklist` | 682 |
| `powershell-coding-standards` | 910 |
| `typescript-coding-standards` | 927 |
| `python-coding-standards` | 1 845 |
| `cpp-embedded-coding-standards` | 1 984 |

A Python backend session touching `.py` files pays roughly **3 200 tokens** (python + errors +
security). The same session never pays for the TypeScript, PowerShell or embedded rules.

This is exactly why `scripts/install.py` detects the stack and installs a subset: installing
all seven rules everywhere would put ~7 400 tokens of standards in front of every project,
most of it irrelevant.

**Skills** — about 21 000 tokens across all 24 skills, of which a typical session loads one
or none. Moving framework detail out of rules and into skills was the single largest saving in
version 2.0:

| | Before (2.0) | After | Change |
|---|---:|---:|---|
| Frontend standards, always-on when touching TS | 6 660 chars | 3 715 chars | **−44%** |
| Toolkit `CLAUDE.md` | 9 388 chars | 5 520 chars | **−41%** |

Nothing was deleted. The Angular and React material moved into `angular-patterns` and
`react-patterns`, where it loads only when the task is actually about that framework — and
where editing a React component no longer drags in RxJS operator tables.

## Model policy

The cheap model is not the cheap option when it is wrong. A missed defect costs a review
cycle, a debugging session, and sometimes a production incident — all of which are paid in
tokens too, plus your time.

| Model | Assigned to | Why |
|-------|-------------|-----|
| `haiku` | `explorer`, `documentation-writer` | Retrieval, search and drafting: high volume, low judgment. The work is finding the right file, not deciding what it means. |
| `sonnet` | `debugger`, `code-reviewer`, `test-writer`, `esp32-firmware-engineer` | Root-cause reasoning, review judgment, test design, hardware risk. Each of these produces a decision someone will trust without re-checking. |
| `opus` | nothing by default | Reserved for genuinely hard architecture work, chosen deliberately per task. |

Before 2.0 every agent ran on `haiku`, including the reviewer and the debugger. That is not
cost optimization — it is moving the cost to the place where it is hardest to see.

## Context isolation

`/ai-tools:security-scan` declares `context: fork` with `agent: code-reviewer`. The audit runs
in its own window: it reads the whole diff and every boundary it touches, then returns only
the findings. The main conversation pays for the answer, not for the investigation.

Use the same pattern for any task that needs to read a lot and report a little.

## Practical rules

1. **Scope every rule with `paths`.** A rule without them is a permanent tax on every session.
2. **Framework detail belongs in a skill.** Only language- and file-level invariants are
   cheap enough to be always-on.
3. **Keep `CLAUDE.md` under 200 lines.** Past that, cost rises and adherence falls — the
   documentation is explicit that longer files are followed less reliably.
4. **Delegate wide reading to an agent.** Ten file reads in a subagent cost one summary in the
   main thread.
5. **Install selectively.** `install.py` exists so a firmware project never carries React
   standards.
6. **Do not pay twice.** If a rule already states something, a skill should reference it, not
   restate it.
