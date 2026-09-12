<!-- GENERATED FILE - DO NOT EDIT.
     Regenerate: python scripts/generate_catalog.py -->

# Component catalog

Every component in the toolkit, derived from the component files themselves.

## Agents

Delegated automatically when a task matches the description, or invoked by name.

| Agent | Model | Purpose |
|---|---|---|
| `code-reviewer` | sonnet | Performs systematic code reviews against configurable standards |
| `debugger` | sonnet | Systematic bug diagnosis and fix agent |
| `documentation-writer` | haiku | Generates and maintains technical documentation |
| `esp32-firmware-engineer` | sonnet | Autonomous ESP32/PlatformIO C++ firmware engineer that writes embedded code, runs static checks, builds, uploads to physical hardware under a risk-based confir… |
| `explorer` | haiku | Fast read-only codebase exploration and research agent |
| `test-writer` | sonnet | Generates unit, integration, and regression tests for existing code |


## Commands

Typed deliberately. Hidden from automatic model invocation, so they never fire on their own.

| Command | Arguments | Context | Purpose |
|---|---|---|---|
| `/ai-tools:adr` | `[decision title]` | — | Record an architecture decision as a numbered ADR in docs/adr/. |
| `/ai-tools:commit` | `[optional scope or note]` | — | Stage the right files and write a Conventional Commits message from the actual diff. |
| `/ai-tools:fastapi-endpoint` | `[METHOD /path - what it does]` | — | Scaffold a FastAPI endpoint end to end |
| `/ai-tools:onboard-project` | `[path to project, default: current directory]` | — | Set up a repository for this toolkit |
| `/ai-tools:pr-description` | `[base branch, default: main]` | — | Write a pull request title and body from the branch's actual diff against its base. |
| `/ai-tools:react-feature` | `[feature name - what it does]` | — | Scaffold a React feature slice |
| `/ai-tools:security-scan` | `[optional path or base branch]` | fork | Audit the current changes against the OWASP security checklist in an isolated subagent. |
| `/ai-tools:test-focus` | `[optional path or test name filter]` | — | Run only the tests affected by the current changes, then widen if they pass. |
| `/ai-tools:toolkit-validate` | — | — | Validate this toolkit |


## Skills

Loaded on demand when the description matches the task — free until used.

| Skill | Invocation | Purpose |
|---|---|---|
| `angular-patterns` | model-invoked | Angular architecture - standalone components, signals, RxJS subscription management, state management, folder structure, and component testing |
| `api-design` | model-invoked | REST API design patterns, schema validation, versioning, error handling, and documentation |
| `database-design` | model-invoked | Database modeling patterns for SQL, NoSQL (Firestore), BigQuery |
| `diagnosing-bugs` | model or user | Diagnosis loop for hard bugs and performance regressions |
| `domain-modeling` | model-invoked | Build and sharpen a project's domain model |
| `git-workflows` | model-invoked | Git branching strategies, PR conventions, merge workflows, commit message standards, and conflict resolution patterns |
| `grill-me` | model or user | A relentless interview to sharpen a plan or design. |
| `grill-with-docs` | model or user | A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go. |
| `grilling` | model-invoked | Grill the user relentlessly about a plan, decision, or idea |
| `jira-board-extractor` | model or user | Read-only Jira Cloud board data collection skill for backlog, epics, sprints, board configuration, and issue details |
| `prepare-work` | model or user | Pipeline developerski w wariancie pełnym albo uproszczonym oszczędzającym tokeny |
| `react-patterns` | model-invoked | React 19 architecture - component and hook design, TanStack Query server state, react-hook-form + zod forms, Radix UI primitives, Tailwind styling, and Testing… |
| `testing` | model-invoked | Testing patterns and frameworks for Python (pytest, pytest-asyncio), TypeScript (Vitest, Jest), and Angular (Testing Library) |
| `to-spec` | model or user | Turn the current conversation into a spec and publish it to the project issue tracker |
| `ui-verify` | model or user | Physically click through the running frontend in a real Chrome browser (via the chrome-devtools MCP server) and check each screen/flow against a plan or checkl… |


## Rules

Path-scoped standards. Installed with `scripts/install.py`; they load when a matching file is read.

| Rule | Applies to | Purpose |
|---|---|---|
| `architecture-decisions` | `docs/adr/**/*.md`, `**/adr-*.md` | ADR (Architecture Decision Record) template and process |
| `cpp-embedded-coding-standards` | `**/*.cpp`, `**/*.h`, `**/*.hpp`, `**/*.ino` | Embedded C++/Arduino/ESP32 conventions - non-blocking loops, heap/String caution, PROGMEM, structured log tagging, pin safety, watchdog-safe loops |
| `error-handling-patterns` | `**/*.py`, `**/*.{ts,tsx,js,jsx}` | Error handling patterns for Python backend and TypeScript frontend - exception hierarchy, HTTP contract, logging strategy |
| `powershell-coding-standards` | `**/*.ps1`, `**/*.psm1` | PowerShell 7+ coding standards - script structure, naming, error handling, Pester tests |
| `python-coding-standards` | `**/*.py` | Python 3.12+ coding standards - Ruff, mypy strict, FastAPI patterns, pytest |
| `security-checklist` | `**/*.py`, `**/*.{ts,tsx,js,jsx}`, `**/*.{ps1,psm1}` | OWASP Top 10 security checklist - JWT auth, input validation, SQL injection, XSS, CSRF, rate limiting, secrets management |
| `typescript-coding-standards` | `**/*.{ts,tsx,mts,cts}`, `**/*.{js,jsx,mjs,cjs}`, `**/*.{html,scss,css}` | Framework-agnostic TypeScript/JavaScript standards - strict mode, formatting, complexity limits, naming |


## Hooks

Deterministic enforcement — these run regardless of what the model decides.

| Event | Matcher | Script | Action |
|---|---|---|---|
| `PreToolUse` | `Bash` | `guard_bash.py` | Checking command safety |
| `PreToolUse` | `Read\|Edit\|Write\|NotebookEdit` | `guard_secrets.py` | Checking for credential files |
| `PostToolUse` | `Edit\|Write` | `format_after_edit.py` | Formatting |
