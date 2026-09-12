---
id: product
title: Kanon produktu — <nazwa produktu>
layer: L1
domain: product
status: active
confidence: decision
owner: <imię>
created: <YYYY-MM-DD>
verified: <YYYY-MM-DD>
review_after: <YYYY-MM-DD>   # startup przed PMF: 1 miesiąc; po PMF: 3 miesiące
related: [context, <id-adr>]
---

<!--
PRODUCT.md to najgęstszy dokument w bazie: każdy agent pracujący nad czymkolwiek
zaczyna od niego. Twardy limit 200 linii. Wszystko, co dłuższe, to osobny
dokument L1 albo dowód L4, do którego stąd linkujesz.

Test kontrolny: agent po przeczytaniu tylko tego pliku potrafi odrzucić
propozycję funkcji spoza zakresu i uzasadnić dlaczego. Jeśli nie potrafi,
brakuje sekcji "Czego nie robimy".
-->

# <Nazwa produktu>

<!-- Jedno zdanie. Kto + jaki problem + w jaki sposób. Bez przymiotników. -->

## 1. Problem

<!--
Problem klienta, nie brak naszego rozwiązania. "Gminy nie mają wglądu w stan
przepompowni" to problem. "Brakuje systemu monitoringu" to opis produktu
przebrany za problem.
-->

**Kto ma problem:** <segment>
**Co się dzieje dzisiaj:** <stan bez naszego produktu>
**Koszt tego stanu:** <pieniądze / czas / ryzyko — liczby jeśli są>

> **[HIPOTEZA]** <założenie o problemie, którego jeszcze nie potwierdziłeś>
> Podstawa: <skąd> · Weryfikacja: <jak i kiedy sprawdzisz>

## 2. Klient

| | |
|---|---|
| **Segment podstawowy** | <kto płaci> |
| **Użytkownik** | <kto używa, jeśli to inna osoba niż płacąca> |
| **Kryteria dobrego klienta** | <co odróżnia klienta, który zostanie, od takiego, który odejdzie> |
| **Kogo świadomie nie obsługujemy** | <i dlaczego> |

Rozwinięcie: [`docs/product/segments/`](./docs/product/segments/)

## 3. Propozycja wartości

<!-- Maksymalnie 4 pozycje. Piąta oznacza, że nie wiesz, która jest najważniejsza. -->

| Wartość | Dla kogo | Czym mierzona |
|---|---|---|
| <wartość> | <rola> | <jak sprawdzisz, że dostarczona> |

## 4. Zakres

### W zakresie teraz

- <funkcja / obszar>

### Poza zakresem — świadomie

<!--
Najważniejsza sekcja całego dokumentu dla agenta. To ona pozwala odrzucić
propozycję bez pytania człowieka. Każda pozycja z powodem — sam zakaz bez
powodu zostanie obejściony przy pierwszej okazji.
-->

| Czego nie robimy | Dlaczego | Kiedy wrócić do tematu |
|---|---|---|
| <obszar> | <powód> | <warunek, nie data> |

### Rozważane później

- <obszar> — warunek wejścia: <co musi się wydarzyć>

## 5. Model biznesowy

| | |
|---|---|
| **Źródła przychodu** | <jednorazowe / cykliczne> |
| **Jednostka rozliczeniowa** | <per obiekt / user / urządzenie> |
| **Główny koszt zmienny** | <co rośnie z każdym klientem> |

Decyzja źródłowa: [ADR-<NNNN>](./docs/adr/<NNNN>-<tytul>.md)

<!-- Liczby (ceny, marże, koszty jednostkowe) trzymaj w JEDNYM dokumencie
     docs/product/ i linkuj stąd. Tu nigdy nie kopiuj kwot. -->

## 6. Etapy produktu

| Etap | Zakres | Warunek przejścia dalej |
|---|---|---|
| <etap> | <co obejmuje> | <mierzalny warunek, nie data> |

<!-- Warunek, nie data. Data w kanonie L1 dezaktualizuje się w dwa tygodnie
     i podważa wiarygodność całego dokumentu. -->

## 7. Ograniczenia nadrzędne

<!--
Rzeczy, których nie wolno naruszyć nawet gdy upraszczają pracę.
Bezpieczeństwo, regulacje, obietnice wobec klienta.
Każda pozycja: ograniczenie + skąd wynika.
-->

- **<ograniczenie>** — źródło: <regulacja / ADR / obietnica handlowa>

## 8. Stan i otwarte pytania

| Pytanie | Waga | Kto rozstrzyga | Do kiedy |
|---|---|---|---|
| <pytanie> | blokujące / ważne / poboczne | <kto> | <warunek lub data> |

<!--
Sekcja żywa. Pytanie rozstrzygnięte → ADR, a wpis stąd znika.
Pusta tabela w startupie przed PMF oznacza, że pytania są gdzie indziej
(w czyjejś głowie), nie że ich nie ma.
-->
