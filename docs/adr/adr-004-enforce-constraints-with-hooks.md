# ADR-004: Enforce non-negotiable constraints with hooks, not prose

## Status
Accepted

## Date
2026-09-12

## Context

The toolkit's `CLAUDE.md` carried a block of constraints marked **CRITICAL** and "non-negotiable
and enforced without exception": no git operations without approval, no `pip install` outside
the virtual environment, no hand-written Alembic migrations, never discard tracked changes.

They were not enforced by anything. The Claude Code documentation is explicit about what
instruction files are:

> Claude treats them as context, not enforced configuration. To block an action regardless of
> what Claude decides, use a PreToolUse hook instead.

So the strongest wording available in an instruction file still produces a suggestion. Marking
a rule CRITICAL raises its priority in a judgment call; it does not remove the judgment call.

A related gap: `CLAUDE.md` referred to `permissions.deny` in `.claude/settings.json` as the
protection for secrets, but that file had been deleted from the repository in commit
`fa30a25`. The protection it described did not exist.

Options considered:

1. **Stronger wording.** Already at the ceiling.
2. **`permissions.deny` only.** Genuinely enforced by the client, but it lives in each
   project's settings and a plugin cannot ship it — every new repository starts unprotected.
3. **Hooks shipped with the plugin**, backed by `permissions.deny` where a project can add it.

## Decision

Express the constraints that must not be negotiable as `PreToolUse` hooks that ship with the
plugin, and keep the prose as a description of what the hook does.

- `guard_bash` — denies force pushes, `reset --hard`, `clean -f`, wholesale `checkout .` /
  `restore .`, `branch -D`, `--no-verify`, recursive deletes of root/home/wildcard paths,
  `chmod 777`, piping a downloaded script into a shell, `DROP TABLE`, reading `.env` through
  `cat`, and `pip install` outside a virtual environment.
- `guard_secrets` — denies reads of `.env`, private keys, service-account files and credential
  stores, while allowing `.env.example` and friends.
- `format_after_edit` — runs the project's own formatter, and only when that project already
  has it configured.

Three design constraints, each learned from how guards fail in practice:

1. **Fail open.** Malformed input, a missing interpreter, a crash — the action proceeds. A
   guard that can halt all work will be removed, and then it guards nothing.
2. **Deny only the irreversible.** `rm -rf node_modules` stays allowed; `rm -rf ~` does not.
   Every extra pattern buys a false positive somewhere.
3. **Test both directions.** `tests/test_hooks.py` carries 19 commands that must be denied and
   19 that must be allowed, plus the secret-path equivalents. The allow list is the half that
   keeps the guard usable.

`templates/project/settings.json` restores the `permissions.deny` layer for projects, and
`/ai-tools:onboard-project` installs it.

## Consequences

### Positive
- The constraints now hold regardless of what the model concludes.
- They apply in every project with the plugin enabled, including brand-new ones.
- Each denial names the reason and a safe alternative, so the work continues rather than stalling.
- Secrets are covered at three levels: instruction, hook, and client-enforced permission.

### Negative
- A false positive blocks a legitimate command. Mitigated by the allow-case tests and by
  denying only irreversible operations — and the denial message always states the alternative.
- The hooks need Python on `PATH`. The command resolves `python3` or `python` at runtime, and
  a missing interpreter fails open.
- Every new pattern is now a code change with tests, not a line of prose. That is the intended
  trade: slower to add, actually effective.

### Neutral
- Git commits are deliberately **not** blocked. Blocking them would break `/ai-tools:commit`,
  and the approval requirement is a workflow preference rather than an irreversible action.
  Force pushes and history rewrites, which are irreversible, are blocked.
