# AI Toolkit - Personal Developer Base

Universal AI agents, skills, and instructions for VS Code Copilot.
Designed as an extensible foundation - modify and expand as needed.

## Structure

```
.ai-toolkit/
├── agents/           # AI agent definitions (.agent.md)
├── docs/             # Coding standards and best practices (single source of truth)
└── skills/           # Domain knowledge modules (SKILL.md)
```

## Agents

| Agent | Purpose |
|-------|---------|
| Code Reviewer | Code review against configurable standards |
| Documentation | Generate and maintain technical documentation |
| Explorer | Research codebase, find patterns, answer questions |
| Debugger | Diagnose and fix bugs systematically |

## Skills

| Skill | Domain |
|-------|--------|
| Git Workflows | Branching, PR strategies, merge conventions |
| API Design | REST, schemas, validation, versioning |
| Database Design | SQL, NoSQL, Firestore, data modeling |
| Frontend Patterns | Angular, component architecture, state management |

## Usage

### Activating in a project

VS Code Copilot reads customizations from specific paths within `.github/`:

```
your-project/
└── .github/
    ├── agents/          # ← agent files go here (.agent.md)
    ├── skills/          # ← skill folders go here (folder/SKILL.md)
    └── copilot-instructions.md
```

Copy the files you need into the target project's `.github/` folder. Example for adding the Code Reviewer:
```powershell
Copy-Item .ai-toolkit\agents\code-reviewer.agent.md target-project\.github\agents\
```

To use coding standards as always-on context, reference the docs in `copilot-instructions.md`:
```markdown
## Standards
See [coding-standards-python](../../.ai-toolkit/docs/coding-standards-python.md) for Python conventions.
See [coding-standards-frontend](../../.ai-toolkit/docs/coding-standards-frontend.md) for Angular/TS conventions.
```

### Quick Reference (Copilot Chat)

| Goal | How to invoke |
|------|--------------|
| Review code | `@Code Reviewer review this file` |
| Write docs | `@Documentation Writer create a README for this module` |
| Explore | `@Explorer how does authentication work here?` |
| Debug | `@Debugger why does this function return null?` |
| Git help | `@workspace #git-workflows what's the commit format?` |
| API design | `@workspace #api-design how should I structure this endpoint?` |

### Customizing per project

- Override a skill by placing a modified `SKILL.md` in the project's `.github/skills/skill-name/`
- Project-specific instructions take precedence over base instructions
- Extend agent checklists by appending project-specific sections

## Extension Plan

- Add new agents as workflows mature
- Refine skills with project-specific knowledge
- Add instructions for new languages/frameworks as needed
