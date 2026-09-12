---
id: context
title: Słownik domeny — <nazwa produktu>
layer: L1
domain: product
status: active
confidence: decision
owner: <imię>
created: <YYYY-MM-DD>
verified: <YYYY-MM-DD>
review_after: <YYYY-MM-DD>   # zwykle 6 miesięcy
related: [product]
---

<!--
Słownik, nic więcej. Nie specyfikacja, nie notatnik, nie miejsce na decyzje
implementacyjne. Jedno pojęcie = jedna nazwa kanoniczna + lista nazw odrzuconych.

Zgodny z formatem skilla `domain-modeling` (CONTEXT-FORMAT.md) — ten szablon
dodaje wyłącznie front-matter wymagany przez walidator.

Limit: 200 linii miękko, 400 twardo. Powyżej — podziel na konteksty
i załóż CONTEXT-MAP.md w korzeniu.
-->

# Słownik domeny — <nazwa produktu>

<!-- Jedno–dwa zdania: czym jest ta domena i gdzie przebiegają jej granice. -->

## <Grupa pojęć>

<!--
Grupuj, gdy naturalne skupiska się pojawią (np. "Obiekty", "Dane pomiarowe",
"Model produktu", "Regulacje"). Przy kilkunastu pojęciach płaska lista jest
lepsza niż sztuczne grupy.
-->

**<Pojęcie kanoniczne>**
<Jedno–dwa zdania. Definiuj czym to JEST, nie co robi. Bez szczegółów implementacji.>
_Unikać_: <nazwa odrzucona>, <nazwa odrzucona>

**<Pojęcie kanoniczne>**
<Definicja.>
_Unikać_: <nazwa odrzucona>

<!--
Reguły, które decydują o użyteczności słownika:

1. BĄDŹ STANOWCZY. Kilka słów na to samo → wybierasz jedno, reszta trafia
   do _Unikać_. Słownik bez listy odrzuconych nie rozwiązuje niczego —
   właśnie ta lista pozwala agentowi wykryć, że ktoś użył złego słowa.

2. DEFINICJE KRÓTKIE. Jedno–dwa zdania. Dłuższe oznacza, że opisujesz
   działanie zamiast definiować byt.

3. TYLKO POJĘCIA TEJ DOMENY. "Timeout", "retry", "cache" nie należą do
   słownika, nawet jeśli projekt ich intensywnie używa. Pytanie kontrolne:
   czy to pojęcie znaczy tutaj coś innego niż w dowolnym innym projekcie?

4. POJĘCIE DWUZNACZNE — opisz dwuznaczność wprost. Ukrywanie jej nie sprawi,
   że zniknie; sprawi, że każdy rozstrzygnie ją inaczej.

5. NIGDY IMPLEMENTACJI. "Pomiar jest zapisywany w tabeli measurements"
   nie należy do słownika — to kontrakt L2.
-->

## Pojęcia świadomie nieustalone

<!--
Dwuznaczności, których jeszcze nie rozstrzygnąłeś. Zapisane jawnie są
ostrzeżeniem; pominięte są pułapką, w którą wpadnie każdy po kolei.
-->

**<Pojęcie>** — <na czym polega dwuznaczność i co rozstrzyga kontekst zdania>

## Zasady nazewnicze

<!-- Opcjonalne. Wypełnij, gdy zapadły decyzje o języku i formie nazw. -->

- Język kodu: <angielski / polski> · Język dokumentacji: <…>
- <konwencja, np. liczba pojedyncza dla encji, mnoga dla kolekcji>
