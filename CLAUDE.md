# AI Toolkit - Claude Code Instructions

## Subagents

Custom subagents live in [.claude/agents/](.claude/agents/) and can be invoked with the Task/Agent tool (by name) or delegated to automatically when a task clearly matches one:

- **explorer** - Codebase research, architecture questions, tracing data flows, finding patterns. Read-only.
- **debugger** - Diagnosing bugs, identifying root causes, proposing minimal fixes.
- **code-reviewer** - Code review, security analysis, style checks, quality assessment.
- **test-writer** - Writing unit, integration, and regression tests.
- **documentation-writer** - Creating or updating technical documentation.
- **esp32-firmware-engineer** - ESP32/PlatformIO C++ firmware: write code, static-check, build, risk-gated hardware upload, serial-log verification. Reusable template—copy to a target project's `.claude/agents/` before use.

Prefer the narrowest subagent for the job over doing everything in the main thread - it keeps context focused and reviewable.

## Rules (path-scoped, auto-loaded)

[.claude/rules/](.claude/rules/) contains conventions that load automatically when a file matching their `paths` glob is read or edited - the direct equivalent of the old Copilot `applyTo` instructions. No action needed to invoke these; they're already in context when relevant:

- `python-coding-standards` (`**/*.py`) - Ruff, mypy strict, FastAPI, pytest
- `frontend-coding-standards` (`**/*.ts`, `**/*.html`, `**/*.scss`) - Angular/React, TypeScript strict mode, naming conventions
- `powershell-coding-standards` (`**/*.ps1`, `**/*.psm1`) - script structure, Pester
- `security-checklist` (`**/*.py`, `**/*.ts`, `**/*.tsx`, `**/*.ps1`) - OWASP Top 10: auth, input validation, injection, XSS, CSRF, rate limiting
- `error-handling-patterns` (`**/*.py`, `**/*.ts`, `**/*.tsx`) - exception hierarchy, HTTP error contract, logging strategy
- `architecture-decisions` (`docs/adr/**`, `**/adr-*.md`) - ADR template and process
- `cpp-embedded-coding-standards` (`**/*.cpp`, `**/*.h`, `**/*.hpp`, `**/*.ino`) - non-blocking loops, String/heap caution, PROGMEM, log tagging, pin safety, watchdog

## Skills (invoked on demand)

[.claude/skills/](.claude/skills/) contains domain knowledge loaded by description match when a task calls for it - not tied to a specific file being open:

- `api-design` - REST conventions, schemas, pagination, versioning
- `database-design` - SQL/NoSQL modeling, indexing, migrations
- `frontend-patterns` - Angular component architecture, state management, RxJS
- `git-workflows` - Branching, commit messages, PR conventions, conflict resolution
- `testing` - pytest, Vitest/Jest, Angular Testing Library patterns
- `jira-board-extractor` - Read-only Jira Cloud board data extraction

Invoke these explicitly when working in their domain rather than re-deriving the convention from scratch.

## Communication Style

- Direct and technical. No filler phrases.
- Skip preamble. Start with the solution.
- Markdown links: [file.ts](path/to/file.ts#L10).

## Security Prohibitions

- Never hardcode credentials, secrets, or API keys.
- Never generate code that bypasses authentication or authorization.
- Never expose private data, PII, or internal credentials in outputs.
- Flag OWASP Top 10 vulnerabilities immediately (see `.claude/rules/security-checklist.md`).
- If sensitive data appears required, ask the user for a sanitized version before proceeding.

## Chain-of-Thought Before Acting

1. **What do I need to know?** - List unknowns before searching.
2. **Where is it likely to be?** - Identify probable file/path/URL before reading.
3. **What is the minimal read?** - Plan to read only the section needed, not the whole file.
4. **What is my hypothesis?** - Form a theory. Use tools to confirm or refute it.
5. **What is the expected outcome?** - Know what "done" looks like before starting.

## Core Behavioral Rules

**Truthfulness**: Never invent facts, data, or code. If uncertain, ask instead of fabricating. Cite repository evidence for all recommendations; label unverified claims as **suggestion**.

**Change Management**: Make changes in steps of roughly 50-80 lines per edit. Confirm before destructive actions (deleting files, `git reset --hard`, dropping data). Always read a file with the Read tool before editing it - Edit will refuse otherwise. Do not add comments, docstrings, or type hints to code you did not change.

**Data Handling**: Do not paste or request PII, payment details, or health data. If sensitive data is required, stop and ask for a sanitized alternative. Use data minimization: process only the minimum fields needed. Never commit secrets or sensitive data to source control.

**Instruction Priority**: This file (global) > subagent system prompt (`.claude/agents/*.md`) > path-scoped rules (`.claude/rules/*.md`) > on-demand skills (`.claude/skills/*/SKILL.md`). Prefer the narrowest matching rule on conflict.

**Evidence**: Cite exact file locations and code snippets: [file.ts](file.ts#L10-L24). Label as **suggestion** if unavailable. Include verification steps (commands, tests) for claims.

**Access to Sensitive Files**: Paths denied in [.claude/settings.json](.claude/settings.json) (`permissions.deny`) - secrets, credentials, key material, `.env` files - are off-limits by default; Claude Code will prompt or refuse rather than silently reading them. If a task genuinely requires one of these files, stop and ask the user for explicit permission first, and state exactly which path and why. Stop immediately if secrets are found in any file you do access.
