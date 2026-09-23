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

1. **Detect project area** — Analyze changed files to determine if they belong to `backend/`,
   `frontend/`, `firmware/`, or `docs/`. If changes span multiple areas, flag it and suggest
   splitting into separate commits. This prefix will be prepended to the scope.

2. **Read the actual diff** — `git diff` and `git diff --cached`. Write the message from what
   the code does, never from the file names alone.

3. **Decide what belongs in this commit.** If the working tree contains two unrelated changes,
   say so and propose splitting into separate commits rather than bundling them. Never stage
   a file the user did not change in this session without pointing it out.

4. **Never stage** `.env`, credentials, key material, local settings (`settings.local.json`),
   build output, or anything matched by `.gitignore`. If `git status` shows one, stop and say so.

5. **Write the message** in Conventional Commits form with detected prefix:

   ```
   <type>(<prefix>/<scope>): <subject in imperative mood, <=72 chars>

   <body: why the change was needed, what it changes, what it deliberately does not>

   <footer: BREAKING CHANGE: ... / refs #123>
   ```

   **Prefix:** `backend`, `frontend`, `firmware`, or `docs` (auto-detected).
   **Scope:** optional, from `$ARGUMENTS` or inferred (e.g., `security`, `auth`, `ui`).
   **Types:** `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `build`, `ci`, `chore`.
   Omit the body only when the subject genuinely says everything.

   **Example:** `fix(backend/security): remove inline import from validate_password_length`

6. **Show the message and the file list, then ask for approval.** Commit only after the user
   confirms. `$ARGUMENTS`, if given, is an additional scope note or type override (e.g., `auth`
   to narrow the prefix-detected area).

7. **Do not push.** Pushing is a separate, explicit decision.

## Message quality bar

- Subject says what changed, not that something changed: `fix(auth): reject tokens signed with none` beats `fix: bug fix`.
- The body answers "why now", not "what the diff shows" — the diff already shows that.
- No model names, tool names, or session identifiers in the message.
