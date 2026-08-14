---
name: git-workflows
description: Git branching strategies, PR conventions, merge workflows, commit message standards, and conflict resolution patterns. Use when the user asks about git operations, branching, PRs, or version control workflows.
user-invocable: false
---

# Git Workflows Skill

## Branching Strategy

### Branch Naming
```
feature/[ticket-id]-short-description
bugfix/[ticket-id]-short-description
hotfix/[ticket-id]-short-description
release/v[major].[minor].[patch]
```

### Branch Hierarchy
```
main (production)
├── develop (integration)
│   ├── feature/ABC-123-user-auth
│   ├── feature/ABC-124-dashboard
│   └── bugfix/ABC-125-login-fix
└── hotfix/ABC-126-critical-fix
```

## Commit Messages

### Format
```
type(scope): subject

body (optional - explain WHY, not WHAT)

footer (optional - references, breaking changes)
```

### Types
| Type | Use for |
|------|---------|
| feat | New feature |
| fix | Bug fix |
| docs | Documentation only |
| style | Formatting, no logic change |
| refactor | Code change, no feature/fix |
| test | Adding or fixing tests |
| chore | Build, CI, tooling changes |

### Examples
```
feat(auth): add JWT refresh token rotation
fix(api): handle null response from BigQuery
docs(readme): update deployment steps
refactor(dashboard): extract chart component
```

## Pull Request Workflow

### PR Checklist
- [ ] Branch is up-to-date with target branch
- [ ] Tests pass locally
- [ ] No lint errors
- [ ] Commit messages follow convention
- [ ] PR description explains the "why"
- [ ] Self-review completed before requesting others

### PR Description Template
```markdown
## What
Brief description of the change.

## Why
Business context or technical motivation.

## How
Key implementation decisions (if non-obvious).

## Testing
How this was verified.
```

## Common Git Operations

### Rebase workflow (keep history clean)
```bash
git fetch origin
git rebase origin/develop
# resolve conflicts if any
git push --force-with-lease
```

### Squash before merge
```bash
git rebase -i HEAD~N  # N = number of commits to squash
# mark all but first as 'squash'
# write final commit message
```

### Undo last commit (keep changes)
```bash
git reset --soft HEAD~1
```

### Cherry-pick to hotfix
```bash
git checkout hotfix/issue-branch
git cherry-pick <commit-hash>
```

## Conflict Resolution

1. Pull latest from target branch
2. Identify conflicting files
3. For each conflict: understand both sides, choose correct resolution
4. Run tests after resolution
5. Commit with message: `fix: resolve merge conflicts with develop`

## Tags and Releases
```bash
git tag -a v1.2.0 -m "Release v1.2.0: feature X, fix Y"
git push origin v1.2.0
```
