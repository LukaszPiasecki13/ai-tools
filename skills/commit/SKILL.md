---
name: commit
description: Stage the right files and write a Conventional Commits message from the actual diff.
disable-model-invocation: true
user-invocable: true
argument-hint: "[optional scope or note]"
allowed-tools: Bash(git status:*) Bash(git diff:*) Bash(git log:*) Bash(git add:*) Bash(git commit:*)
---

# Commit

Current state:

!`git status --short`

Staged changes:

!`git diff --cached --stat`

Unstaged changes:

!`git diff --stat`

Recent messages (match their style):

!`git log --oneline -10 2>/dev/null || echo "(no commits yet)"`

## Process

1. **Read the actual diff** — `git diff` and `git diff --cached`. Write the message from what
   the code does, never from the file names alone.

2. **Decide what belongs in this commit.** If the working tree contains two unrelated changes,
   say so and propose splitting into separate commits rather than bundling them. Never stage
   a file the user did not change in this session without pointing it out.

3. **Never stage** `.env`, credentials, key material, local settings (`settings.local.json`),
   build output, or anything matched by `.gitignore`. If `git status` shows one, stop and say so.

4. **Write the message** in Conventional Commits form:

   ```
   <type>(<scope>): <subject in imperative mood, <=72 chars>

   <body: why the change was needed, what it changes, what it deliberately does not>

   <footer: BREAKING CHANGE: ... / refs #123>
   ```

   Types: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `build`, `ci`, `chore`.
   Omit the body only when the subject genuinely says everything.

5. **Show the message and the file list, then ask for approval.** Commit only after the user
   confirms. `$ARGUMENTS`, if given, is the scope or a note to incorporate.

6. **Do not push.** Pushing is a separate, explicit decision.

## Message quality bar

- Subject says what changed, not that something changed: `fix(auth): reject tokens signed with none` beats `fix: bug fix`.
- The body answers "why now", not "what the diff shows" — the diff already shows that.
- No model names, tool names, or session identifiers in the message.
