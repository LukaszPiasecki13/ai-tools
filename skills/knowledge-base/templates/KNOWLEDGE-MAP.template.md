---
id: knowledge-map
status: current
type: reference
scope: knowledge-base
last_reviewed: <YYYY-MM-DD>
---

<!--
Jedyny punkt wejścia do bazy wiedzy. Wskaż go wprost z CLAUDE.md:
"Zanim zaczniesz szukać czegokolwiek w docs/, przeczytaj docs/00_KNOWLEDGE-MAP.md."

Dwie części:
  • ręczna   — nawigacja, pakiety kontekstu, "od czego zacząć" (piszesz ty)
  • generowana — tabela między znacznikami KB-INDEX (nadpisuje walidator --write-index)
Nie edytuj ręcznie obszaru między znacznikami.
-->

# Mapa wiedzy — <nazwa produktu>

<!-- Jedno zdanie: czym jest ta baza i kto z niej korzysta. -->

## Jak czytać tę bazę

Wiedza jest podzielona na **warstwy według roli**, nie tematu. Warstwa wyższa
wygrywa przy sprzeczności.

| Warstwa | Co zawiera | Gdzie |
|---|---|---|
| **L0 — Konstytucja** | Reguły zachowania agenta | `CLAUDE.md`, `.claude/rules/` |
| **L1 — Kanon** | Słownik, decyzje, ewentualnie kanon produktu | `CONTEXT.md`, `docs/adr/`, `docs/product/` |
| **L2 — Kontrakty** | Architektura, moduły, interfejsy, runbooki | `docs/technical/` |
| **L3 — Pamięć robocza** | Plany, specyfikacje, briefy | `docs/plans/` |
| **L4 — Dowody** | Badania, analizy, pomiary | `docs/research/` |

**Plan (L3) nie opisuje stanu systemu.** Stan opisuje wyłącznie L2 i kod.

## Od czego zacząć

| Zadanie | Czytaj w tej kolejności |
|---|---|
| Pierwszy kontakt z projektem | `CONTEXT.md` → ADR ze statusem `accepted` |
| Zmiana w backendzie | `CONTEXT.md` → architektura → dokument modułu |
| Zmiana w firmware | mapa sprzętowa → dokument protokołu → runbook |
| Decyzja biznesowa | `CONTEXT.md` → ryzyka → ADR-y `active` |
| Nowe badanie rynku | `CONTEXT.md` → segmenty → istniejące dowody L4 |

## Pakiety kontekstu

<!--
Zestaw dokumentów dla powtarzalnego typu zadania. Agent dostaje nazwę pakietu
zamiast wybierać materiał od nowa. Definiuj dopiero, gdy typ zadania powtórzył
się co najmniej dwa razy — przedwczesne pakiety to wróżenie.
-->

**`<nazwa-pakietu>`** — <kiedy stosować>
1. `<ścieżka>` — <po co>
2. `<ścieżka>` — <po co>

## Czego tu nie ma

<!--
Sekcja niedoceniana, a bardzo wartościowa: chroni przed szukaniem czegoś,
czego nie ma, i przed budowaniem na założeniu, że skoro nie znalazłem,
to pewnie gdzieś jest.
-->

- <obszar> — <dlaczego nie ma; czy planowane>

## Indeks dokumentów

<!-- KB-INDEX:START -->
<!-- Generowane przez: python scripts/kb_validate.py --root . --write-index -->
<!-- KB-INDEX:END -->
