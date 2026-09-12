---
paths: ["docs/adr/**/*.md", "**/adr-*.md"]
description: ADR (Architecture Decision Record) template and process. Auto-loaded when working in docs/adr/ or on files named adr-*.
---

# Architecture Decision Records (ADR)

Use ADRs for decisions that affect multiple files, teams, or are hard to reverse.

## When to Write an ADR

- Choosing a framework, library, or tool
- Changing authentication or authorization approach
- Altering database schema strategy
- Selecting state management pattern
- Defining API versioning approach
- Any decision you would want to explain to a new team member

## File Naming and Location

- File: `adr-NNN-short-title.md` (e.g., `adr-001-use-fastapi.md`)
- Location: `docs/adr/` in the project root
- Number sequentially, never reuse numbers

## Template

```markdown
# ADR-NNN: [Short Decision Title]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

## Date
YYYY-MM-DD

## Context
What is the problem? What constraints exist?
What options were considered?

## Decision
What did we choose and why?
Reference specific trade-offs that made this the best option.

## Consequences

### Positive
- What becomes easier or better

### Negative
- What becomes harder or what we give up

### Neutral
- Side effects that are neither good nor bad
```

## Review Process

1. Author writes ADR with status `Proposed`
2. Team reviews via PR or meeting
3. If accepted: change status to `Accepted`, merge
4. If rejected: document why, close PR
5. If superseded later: update status, link to new ADR
