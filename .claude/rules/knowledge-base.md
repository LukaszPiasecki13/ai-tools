---
paths: ["docs/**/*.md", "CONTEXT.md", "PRODUCT.md", "**/CONTEXT.md"]
description: Konwencje bazy wiedzy dla agentów - warstwy, front-matter, linki, aktualizacja. Ładowane automatycznie przy pracy na dokumentach w docs/.
---

# Baza wiedzy — konwencje

Pełny framework: [`.claude/skills/knowledge-base/`](../skills/knowledge-base/SKILL.md).
Ta reguła to zestaw minimalny, wymuszany przy każdej edycji dokumentu.

## Warstwy

| Warstwa | Co | Gdzie |
|---|---|---|
| L0 | reguły zachowania agenta | `CLAUDE.md`, `.claude/rules/` |
| L1 | słownik, kanon produktu, decyzje | `CONTEXT.md`, `PRODUCT.md`, `docs/adr/`, `docs/product/` |
| L2 | architektura, moduły, kontrakty, runbooki | `docs/technical/` |
| L3 | plany, specyfikacje, briefy | `docs/plans/` |
| L4 | badania, analizy, pomiary | `docs/research/` |

Konflikt rozstrzyga warstwa wyższa. **Konflikt jest defektem** — zgłoś go jako
otwarty punkt, nie wybieraj po cichu jednej wersji.

**Plan (L3) nie opisuje stanu systemu.** Stan opisuje wyłącznie L2 z linkami do kodu.

## Front-matter — obowiązkowy w każdym pliku pod `docs/`

```yaml
---
id: <unikalny-slug>
title: <zdanie>
layer: L1
domain: <backend|frontend|firmware|product|market>
status: draft|active|superseded|archived
confidence: fact|decision|hypothesis
owner: <imię>
created: YYYY-MM-DD
verified: YYYY-MM-DD
review_after: YYYY-MM-DD | on-change   # L1, L2
applies_to: [<glob kodu>]              # L2 — obowiązkowe
sources: [<ścieżka|URL>]               # L2, L4
expires: YYYY-MM-DD                    # L3
---
```

`verified` podbija ten, kto **sprawdził treść wobec rzeczywistości** — nie ten,
kto poprawił literówkę.

## Reguły edycji

1. **Jeden fakt — jedno miejsce.** Wszędzie indziej głęboki link `plik.md#kotwica`.
   Nie kopiuj treści między dokumentami.
2. **Twierdzenie normatywne ma źródło** — link do kodu, ADR albo dowodu L4.
   Bez źródła oznacz `confidence: hypothesis` i dodaj w treści:
   `> **[HIPOTEZA]** … Podstawa: … Niezweryfikowane wobec: …`
3. **Decyzja idzie do ADR**, nie do planu ani dokumentu technicznego. Warunki:
   nieodwracalna + nieoczywista + był realny wybór. Wszystkie trzy naraz.
4. **Nowe pojęcie domenowe → `CONTEXT.md` natychmiast**, z listą `_Unikać_`.
5. **Nic nie kasujesz** — `status: archived` albo `superseded` + `superseded_by`.
6. **Zmiana nagłówka zrywa kotwice** — napraw linkujące dokumenty w tym samym commicie.
7. **Nowy dokument → wpis w mapie wiedzy** (`docs/00_KNOWLEDGE-MAP.md`) w tym samym commicie.
8. **Zmiana kodu objętego `applies_to`** → aktualizacja dokumentu i nowe `verified`,
   w tym samym commicie co kod.

## Limity rozmiaru (linie)

| Typ | Miękki | Twardy |
|---|---|---|
| ADR | 80 | 150 |
| `CONTEXT.md` | 200 | 400 |
| L2 / L3 / L4 | 400 | 800 |

Przekroczenie twardego limitu → dokument do rozbicia po **adresowalności**
(jaka sekcja jest celem osobnego pytania), nie po długości. Oryginał zostaje
stroną-rozdzielaczem z linkami do części.

## Zanim uznasz dokument za skończony

```bash
python scripts/kb_validate.py --root . --strict
```

Sprawdza: front-matter, martwe linki i kotwice, zduplikowane `id`, limity
rozmiaru, przeterminowanie, rozjazd doc↔kod.
