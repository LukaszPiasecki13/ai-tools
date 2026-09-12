---
paths: ["docs/**/*.md", "CONTEXT.md", "PRODUCT.md", "**/CONTEXT.md"]
description: Konwencje bazy wiedzy dla agentów - front-matter, warstwy, limity, reguły edycji dokumentów. Ładowane automatycznie przy pracy na dokumentach w docs/.
---

# Baza wiedzy — konwencje

Minimum egzekwowane przy każdej edycji dokumentu. Uzasadnienia, pełny model
warstwowy, schemat metadanych i gotowe szablony dokumentów są w skillu
`knowledge-base` — wywołaj go, zamiast odtwarzać konwencję z pamięci.

## Warstwa — wybierz jedną

`L0` reguły agenta · `L1` słownik, kanon produktu, decyzje (ADR) ·
`L2` architektura, moduły, kontrakty, runbooki · `L3` plany i specyfikacje ·
`L4` badania i dowody.

Sprzeczność rozstrzyga warstwa wyższa i **jest defektem** — zgłoś ją jako otwarty
punkt, nie wybieraj po cichu. **Plan (L3) nigdy nie opisuje stanu systemu**; stan
opisuje L2 z linkami do kodu.

## Front-matter — obowiązkowy pod `docs/`

```yaml
---
id: <unikalny-slug>          # stabilny, nie zmienia się przy przenoszeniu pliku
title: <zdanie>
layer: L1
domain: <backend|frontend|firmware|product|market>
status: draft|active|superseded|archived
confidence: fact|decision|hypothesis
owner: <imię>
created: YYYY-MM-DD
verified: YYYY-MM-DD         # data sprawdzenia treści wobec rzeczywistości
review_after: YYYY-MM-DD | on-change   # L1, L2
applies_to: [<glob kodu>]              # L2 — obowiązkowe
sources: [<ścieżka|URL>]               # L2, L4
expires: YYYY-MM-DD                    # L3
---
```

Pełna tabela pól i reguł walidacji: skill `knowledge-base`, plik `METADATA.md`.

## Reguły edycji

1. **Jeden fakt — jedno miejsce.** Wszędzie indziej link `plik.md#kotwica`.
2. **Twierdzenie normatywne ma źródło** (kod, ADR, dowód L4). Bez źródła →
   `confidence: hypothesis` + w treści `> **[HIPOTEZA]** … Podstawa: …`.
3. **Decyzja idzie do ADR**, nie do planu. Warunki łącznie: nieodwracalna,
   nieoczywista, był realny wybór. Format ADR ustala reguła
   `architecture-decisions`; gotowy szablon jest w skillu `knowledge-base`.
4. **Nowe pojęcie domenowe → `CONTEXT.md` natychmiast**, z listą `_Unikać_`.
5. **Nic nie kasujesz** — `archived` albo `superseded` + `superseded_by`.
6. **Zmiana nagłówka zrywa kotwice** — napraw linkujące dokumenty w tym commicie.
7. **Nowy dokument → wpis w `docs/00_KNOWLEDGE-MAP.md`** w tym samym commicie.
8. **Zmiana kodu z `applies_to`** → aktualizacja dokumentu i nowe `verified`,
   w tym samym commicie co kod.
9. **`verified` podbija ten, kto sprawdził** — nie ten, kto poprawił literówkę.

## Limity rozmiaru (linie, miękki / twardy)

ADR 80/150 · `CONTEXT.md` 200/400 · L2, L3, L4 400/800.

Ponad twardy limit → rozbicie po **adresowalności** (co jest celem osobnego
pytania), nie po długości. Oryginał zostaje rozdzielaczem z linkami.

## Przed zamknięciem zadania

```bash
python scripts/kb_validate.py --root . --strict
```
