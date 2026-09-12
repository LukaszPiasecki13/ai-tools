---
id: <obszar>-<nazwa-komponentu>
title: <Moduł / komponent> — <jedno zdanie o odpowiedzialności>
layer: L2
domain: <backend|frontend|firmware>
status: active
confidence: fact
owner: <imię>
created: <YYYY-MM-DD>
verified: <YYYY-MM-DD>
review_after: on-change
applies_to:
  - <ścieżka/do/modułu/**>
sources:
  - <ścieżka/do/pliku.py>
related: [<id-architektury>, <id-adr>]
---

<!--
Kontrakt komponentu: co gwarantuje, czego nie gwarantuje, jak się do niego
podłączyć. Nie jest to przepisany kod — jeśli czytelnik równie dobrze mógłby
przeczytać źródło, dokument nie dodaje wartości i będzie gnił.

Wartość dodana dokumentu L2 leży w trzech miejscach, których z kodu nie widać:
  • niezmienniki (co MUSI być prawdą, a kod tego nie wymusza),
  • granice (czego ten komponent NIE robi i dlaczego),
  • uzasadnienia (dlaczego nie zrobiono tego prościej).

`applies_to` jest obowiązkowe — bez niego nie działa ani pobieranie po zakresie,
ani wykrywanie rozjazdu doc↔kod.

Limit: 400 linii miękko, 800 twardo.
-->

# <Nazwa modułu / komponentu>

<!-- Jedno zdanie: za co odpowiada. -->

## 1. Odpowiedzialność

**Robi:**
- <odpowiedzialność>

**Nie robi:**
<!-- Granice są równie ważne jak zakres — to one powstrzymują rozrost
     komponentu i wskazują, gdzie szukać reszty. -->
- <czego nie robi> → robi to: [<komponent>](<ścieżka>)

## 2. Umiejscowienie

| | |
|---|---|
| **Ścieżka** | `<ścieżka>` |
| **Warstwa architektury** | <np. services> |
| **Zależy od** | <komponenty poniżej> |
| **Używany przez** | <komponenty powyżej> |

<!-- Zależności cykliczne wypisz wprost jako dług, jeśli istnieją.
     Ukryte, będą się pogłębiać. -->

## 3. Publiczny interfejs

<!--
Tylko to, co wolno wołać z zewnątrz. Sygnatury z linkiem do kodu.
Reszta jest szczegółem implementacyjnym i nie należy do dokumentu.
-->

| Operacja | Wejście → wyjście | Błędy | Kod |
|---|---|---|---|
| `<nazwa>` | `<typ>` → `<typ>` | `<wyjątki>` | [`plik.py#L<nn>`](<ścieżka>#L<nn>) |

## 4. Niezmienniki

<!--
Najcenniejsza sekcja. Warunki, które MUSZĄ być prawdziwe, a których kod nie
wymusza sam z siebie — czyli dokładnie to, co agent złamie, nie wiedząc o tym.
Każdy niezmiennik: warunek + skutek złamania + gdzie jest pilnowany.
-->

| Niezmiennik | Skutek złamania | Gdzie pilnowany |
|---|---|---|
| <warunek, który musi zachodzić> | <co się zepsuje> | [`plik.py#L<nn>`](<ścieżka>#L<nn>) / test `<nazwa>` |

## 5. Model danych

<!-- Wyłącznie encje należące do tego komponentu. Cudze — linkiem. -->

| Encja | Klucz | Uwagi |
|---|---|---|
| `<nazwa>` | <klucz> | <partycjonowanie, kaskady, indeksy nieoczywiste> |

## 6. Decyzje projektowe

<!--
Dlaczego tak, a nie prościej. Bez tej sekcji ktoś "uprości" rozwiązanie
i przywróci problem, który to rozwiązanie usuwało.
-->

| Rozwiązanie | Powód | Decyzja źródłowa |
|---|---|---|
| <nieoczywisty wybór> | <dlaczego> | [ADR-<NNNN>](<ścieżka>) |

## 7. Testy

| Poziom | Co pokrywa | Gdzie |
|---|---|---|
| jednostkowe | <…> | `<ścieżka>` |
| integracyjne | <…> | `<ścieżka>` |

**Niepokryte świadomie:** <co i dlaczego>

## 8. Znane ograniczenia

<!-- Dług techniczny i braki, znane w chwili `verified`. Pusta sekcja jest
     podejrzana — zwykle znaczy, że nikt nie szukał. -->

- <ograniczenie> — <wpływ> — <warunek naprawy>
