---
paths: ["**/adr/**/*.md", "**/adr-*.md", "**/ADR-*.md"]
description: ADR (Architecture Decision Record) template and process. Auto-loaded when working on any file under an adr/ directory or named adr-*.
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

- File: `NNNN-short-slug.md` (e.g., `0001-use-fastapi.md`)
- Location: `docs/adr/` in the project root — one directory per repo, shared by
  technical and business decisions
- Number sequentially, never reuse numbers

## Template — single source

The canonical ADR template lives in one place:
[`.claude/skills/knowledge-base/templates/adr.template.md`](../skills/knowledge-base/templates/adr.template.md).

Copy it; do not reconstruct an ADR from memory and do not maintain a second
template here. Deciding *whether* a decision deserves an ADR is covered by
[`domain-modeling/ADR-FORMAT.md`](../skills/domain-modeling/ADR-FORMAT.md).

Minimum viable ADR: title, Status, Kontekst, Decyzja, Rozpatrywane alternatywy,
Konsekwencje. The alternatives section is what stops a rejected option from
being re-proposed in six months — never drop it.

## Review Process

1. Author writes ADR with status `Proposed`
2. Team reviews via PR or meeting
3. If accepted: change status to `Accepted`, merge
4. If rejected: document why, close PR
5. If superseded later: update status, link to new ADR
