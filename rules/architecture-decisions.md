---
paths: ["docs/**/adr/**/*.md", "**/adr-*.md"]
description: ADR (Architecture Decision Record) template and process. Auto-loaded when working in any docs/**/adr/ directory (e.g. docs/adr/, docs/business/adr/, docs/technical/adr/) or on files named adr-*.
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

- File: `NNNN-short-title.md` (e.g., `0001-mvp-scope-temperature-pressure.md`)
- Location: `docs/business/adr/` for business decisions, `docs/technical/adr/` for technical ones
- Number sequentially per directory, never reuse numbers, pad to 4 digits

## Template

```markdown
# {Tytuł decyzji w formie stwierdzenia, nie pytania}

{1-3 zdania: co zostało zdecydowane i dlaczego — streszczenie dla kogoś, kto nie czyta dalej.}

## Status
Proposed | Accepted | Deprecated | Superseded by ADR-NNNN

## Kontekst
Jaki jest problem? Jakie są ograniczenia? Jakie opcje rozważano?

## Decyzja
Co wybrano i dlaczego. Konkretne kompromisy, które przeważyły.

## Rozpatrywane alternatywy
Co jeszcze było na stole i dlaczego odpadło — konkretny powód, nie ogólnik. ADR bez odrzuconych
alternatyw zapisuje preferencję, nie decyzję.

## Konsekwencje
Co to ułatwia, co utrudnia, co zamyka, co trzeba by zmienić, żeby to cofnąć.

## Notatki
Opcjonalnie: co pozostaje jawnie nierozstrzygnięte (brak decyzji ≠ decyzja), odnośniki do
źródeł/rozdziałów, które ten ADR operacjonalizuje.
```

`Status` i `Notatki` można pominąć, gdy nie wnoszą wartości; `Kontekst`, `Decyzja`,
`Rozpatrywane alternatywy` i `Konsekwencje` są oczekiwane w każdym ADR tego repo.

## Review Process

1. Author writes ADR with status `Proposed`
2. Team reviews via PR or meeting
3. If accepted: change status to `Accepted`, merge — **agent nie przełącza sam na `Accepted`,
   tylko człowiek** (patrz CLAUDE.md)
4. If rejected: document why, close PR
5. If superseded later: update status, link to new ADR
