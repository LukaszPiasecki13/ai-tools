---
id: runbook-<nazwa>
title: Runbook — <procedura>
layer: L2
domain: <backend|firmware|ops>
status: active
confidence: fact
owner: <imię>
created: <YYYY-MM-DD>
verified: <YYYY-MM-DD>
review_after: <YYYY-MM-DD>
applies_to:
  - <ścieżka/do/kodu/lub/skryptów/**>
sources:
  - <ścieżka/do/skryptu>
related: [<id-komponentu>]
---

<!--
Runbook to procedura wykonywana przez człowieka albo agenta pod presją:
wdrożenie, awaria, provisioning, migracja.

Trzy cechy odróżniające dobry runbook od opisu:
  • każdy krok ma polecenie do wykonania i obserwowalny wynik,
  • każdy krok ma warunek "co, jeśli się nie udało",
  • procedura ma jawne wycofanie.

`verified` w runbooku znaczy: "ktoś to przeszedł od początku do końca w tej
wersji". Runbook niewykonany od pół roku jest hipotezą, nie procedurą.

Limit: 400 linii miękko. Dłuższa procedura to zwykle kilka procedur.
-->

# Runbook: <procedura>

| | |
|---|---|
| **Cel** | <co osiągamy> |
| **Kiedy stosować** | <wyzwalacz> |
| **Czas trwania** | <szacunek> |
| **Ryzyko** | niskie / średnie / wysokie — <na czym polega> |
| **Ostatnio wykonane** | <YYYY-MM-DD> przez <kto> |

## Wymagania wstępne

- [ ] <dostęp / narzędzie / stan systemu>

**Czego NIE robić przed rozpoczęciem:** <typowy błąd, który psuje procedurę>

## Procedura

### Krok 1 — <nazwa>

```bash
<polecenie>
```

**Oczekiwany wynik:** <konkretnie, co zobaczysz>

**Jeśli inaczej:** <diagnoza> → <działanie> → przerwać / kontynuować

### Krok 2 — <nazwa>

<!-- jak wyżej -->

## Weryfikacja powodzenia

<!-- Obserwowalny dowód, że procedura zadziałała. Brak błędów nie jest dowodem. -->

- [ ] <sprawdzalny warunek> — jak sprawdzić: `<polecenie>`

## Wycofanie

<!--
Obowiązkowe dla procedur o ryzyku średnim i wysokim.
Jeśli wycofanie jest niemożliwe, napisz to wprost i wskaż moment bez powrotu.
"Brak wycofania" to informacja krytyczna — jej ukrycie jest niebezpieczne.
-->

**Moment bez powrotu:** <po którym kroku wycofanie przestaje być możliwe>

```bash
<polecenie wycofania>
```

## Typowe problemy

| Objaw | Przyczyna | Działanie |
|---|---|---|
| <co widać> | <dlaczego> | <co zrobić> |

## Ślad

<!-- Co zostaje po wykonaniu: wpis w audycie, log, zmiana statusu.
     Pozwala potwierdzić wykonanie bez pytania wykonawcy. -->

- <gdzie szukać śladu>
