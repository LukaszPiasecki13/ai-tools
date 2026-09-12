---
id: research-<slug>
title: <Pytanie badawcze, na które ten dokument odpowiada>
layer: L4
domain: <market|product|tech|legal>
status: active
confidence: fact        # fact = zebrane dane; hypothesis = wnioski niepotwierdzone
owner: <imię>
created: <YYYY-MM-DD>
verified: <YYYY-MM-DD>
review_after: <YYYY-MM-DD>   # dane cenowe/rynkowe: 3–6 mies.; regulacje: 12 mies.
sources:
  - <URL lub nazwa źródła>
related: [product, <id-adr>]
supersedes: []
superseded_by: null
---

<!--
Dowód: badanie rynku, analiza konkurenta, wywiad, pomiar, analiza regulacji.

Trzy reguły warstwy L4:
  1. APPEND-ONLY — starego badania nie poprawiasz. Powstaje nowy dokument,
     stary dostaje `superseded_by`. Inaczej tracisz informację, JAK zmieniał
     się obraz sytuacji, a to często ważniejsze niż sam obraz.
  2. ZAWSZE Z DATĄ I ŹRÓDŁEM. Dowód bez daty jest bezużyteczny.
  3. NIGDY NORMATYWNY. L4 dostarcza materiału. Obowiązek powstaje dopiero
     w ADR (L1). "Z analizy wynika, że powinniśmy X" nie zobowiązuje nikogo
     do X, dopóki nie ma ADR.

Tytuł jest PYTANIEM, na które dokument odpowiada — nie tematem. "Ilu jest
bezpośrednich konkurentów na rynku polskim?" zamiast "Analiza konkurencji".
-->

# <Pytanie badawcze>

| | |
|---|---|
| **Data zebrania danych** | <YYYY-MM-DD> |
| **Metoda** | <przegląd stron / wywiady / pomiar / analiza dokumentów> |
| **Zakres** | <co objęte, co świadomie pominięte> |
| **Pewność** | wysoka / średnia / niska — <dlaczego> |

## Odpowiedź w skrócie

<!-- 3–5 zdań. Dla czytelnika, który nie przeczyta reszty. Bez rekomendacji —
     te są niżej i są wyraźnie oddzielone od ustaleń. -->

## Ustalenia

<!--
Co udało się ustalić. Każde twierdzenie z przypisem do źródła.
Twierdzenie bez źródła NIE należy do tej sekcji — należy do "Luk i niepewności".
-->

| Ustalenie | Źródło | Data źródła |
|---|---|---|
| <fakt> | <URL / dokument / rozmówca> | <YYYY-MM-DD> |

## Szczegóły

<!-- Dane surowe, tabele porównawcze, cytaty. Rozwinięcie ustaleń. -->

## Luki i niepewności

<!--
Sekcja, którą najłatwiej pominąć i która najbardziej chroni przed zmyśleniami.
Bez niej czytelnik (człowiek i agent) przyjmie, że wszystko poza dokumentem
zostało sprawdzone i nie znaleziono nic.
-->

| Czego nie wiemy | Dlaczego nie ustalono | Jak można ustalić |
|---|---|---|
| <luka> | <powód> | <metoda> |

## Wnioski i rekomendacje

<!--
WYRAŹNIE oddzielone od ustaleń. To interpretacja, nie dane.
Każda rekomendacja ma jawny następny krok, inaczej zawiśnie w próżni
(antywzorzec A11).
-->

**R1.** <rekomendacja>
- Podstawa: <które ustalenia>
- Następny krok: ADR / kolejne badanie / świadome odłożenie do <warunek>
- Status: `otwarte` / `→ ADR-<NNNN>` / `odrzucone (<powód>)`

## Materiał źródłowy

| Źródło | Typ | Data dostępu | Wiarygodność |
|---|---|---|---|
| <URL> | <strona producenta / raport / rozmowa> | <YYYY-MM-DD> | <wysoka/średnia/niska> |

<!-- Materiał marketingowy konkurenta jest źródłem o tym, CO KONKURENT TWIERDZI,
     nie o tym, co potrafi jego produkt. Rozróżniaj to w treści. -->
