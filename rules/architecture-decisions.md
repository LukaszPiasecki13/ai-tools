---
paths: ["docs/**/adr/**/*.md", "docs/**/bdr/**/*.md", "**/adr-*.md"]
description: ADR (Architecture Decision Record) template and process. Auto-loaded when working in any docs/**/adr/ or docs/**/bdr/ directory (e.g. docs/adr/, docs/business/bdr/, docs/technical/adr/) or on files named adr-*.
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

- Technical decisions: `docs/technical/adr/NNNN-slug.md` (ADR-NNNN)
- Business decisions: `docs/business/bdr/NNNN-slug.md` (BDR-NNNN, Business Decision Record)
- The slug is in the repo's documentation language (e.g., `0027-warstwa-domeny.md`)
- Number sequentially per directory (each directory starts at 0001), never reuse numbers, pad to 4 digits
- In text, always refer to a decision with its prefix: `ADR-0027`, `BDR-0004`
- If the repo already has an ADR directory with a different layout, follow the existing one

## Front-matter

```yaml
---
id: adr-0027-domain-layer   # bdr-NNNN-... for BDR; slug in English
status: Proposed            # Proposed | Accepted
last_reviewed: YYYY-MM-DD
type: decision
scope: backend/domain
---
```

- The agent always writes `Proposed`. Only a human sets `Accepted` after review.
- There is no `Deprecated` or `Superseded` status. To replace a decision, add the note
  "Zastąpiony przez ADR-NNNN" in the old ADR's `## Notatki` (its `status` stays `Accepted`)
  and "Zastępuje ADR-NNNN" in the new one. Never edit an ADR to reverse its own decision.
- There is no `## Status` section in the body: the status lives in the front-matter only
  (see the `knowledge-base` rule).

## Template

```markdown
# {Tytuł decyzji w formie zdania oznajmującego}

{1-3 zdania: co postanowiono i dlaczego, z linkami do powiązanych dokumentów}

## Kontekst
Jaki problem? Jakie fakty i ograniczenia?

## Decyzja
Co wybrano i dlaczego (konkretne kompromisy).

## Rozpatrywane alternatywy
Czemu zostały odrzucone?

## Konsekwencje
Ułatwia, utrudnia, zamyka?

## Notatki
Opcjonalnie: co nierozstrzygnięte, "Powiązane:" z linkami, "Zastępuje/Zastąpiony przez".
```

Required: `Kontekst`, `Decyzja`, `Rozpatrywane alternatywy`, `Konsekwencje`. `Notatki` is optional.
