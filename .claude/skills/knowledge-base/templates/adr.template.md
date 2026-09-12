---
id: adr-<NNNN>-<krotki-slug>
title: <Decyzja w formie zdania oznajmującego>
layer: L1
domain: <backend|frontend|firmware|product|market>
status: draft          # draft → active (= zaakceptowany) → superseded → archived
confidence: decision
owner: <imię>
created: <YYYY-MM-DD>
verified: <YYYY-MM-DD>
review_after: on-change
related: [<id-powiązane>]
supersedes: []
superseded_by: null
---

<!--
ADR zapisuje WYBÓR: co rozważaliśmy, co wybraliśmy, czym za to płacimy.

Piszesz ADR, gdy spełnione są TRZY warunki naraz:
  1. nieodwracalne — zmiana zdania później kosztuje realnie,
  2. nieoczywiste — czytelnik za rok zapyta "dlaczego tak?",
  3. był realny wybór — istniała alternatywa, którą odrzuciliście z powodu.
Brak któregokolwiek → bez ADR. ADR-y pisane "na wszelki wypadek" rozmywają
rejestr i sprawiają, że nikt go nie czyta.

Nazwa pliku: docs/adr/<NNNN>-<krotki-slug>.md — numeracja ciągła w całym repo,
wspólna dla decyzji technicznych i biznesowych. Numer nigdy nie jest ponownie użyty.

Limit: 80 linii miękko, 150 twardo. Dłuższy ADR to zwykle dwie decyzje.

Tytuł w trybie oznajmującym: "Telemetria jest normalizowana do tabeli
measurements", nie "Wybór modelu przechowywania telemetrii".
-->

# <Tytuł — decyzja w formie zdania oznajmującego>

<!-- Jeden akapit streszczenia: co postanowiono i co zostaje otwarte.
     Dla czytelnika, który nie przeczyta reszty. -->

## Status

<!-- draft | active | superseded by ADR-NNNN | archived — zgodnie z front-matter -->

## Kontekst

<!--
Co zmusiło do decyzji. Fakty i ograniczenia, nie uzasadnienie wybranego wariantu.
Liczby i twierdzenia z linkiem do źródła (kod, dowód L4, regulacja).
Czytelnik po tej sekcji powinien rozumieć problem na tyle, by samodzielnie
wymyślić rozważane warianty.
-->

## Decyzja

<!--
Co zostało postanowione. Konkretnie i rozstrzygająco.
"Będziemy używać X" — tak. "Rozważamy X" — to nie jest decyzja, to plan (L3).

Część otwarta jest dopuszczalna, ale nazwana wprost:
  **Otwarte i nierozstrzygnięte przez ten ADR:** <co>
-->

## Rozpatrywane alternatywy

<!--
Bez tej sekcji ADR jest bezwartościowy. To ona chroni przed powrotem do
odrzuconego wariantu za rok. Każdy wariant: na czym polegał + dlaczego odpadł.
Odrzucenie "bo gorszy" nie jest powodem.
-->

**<Wariant A>** — <na czym polegał>. Odrzucony: <konkretny powód>.

**<Wariant B>** — <na czym polegał>. Odrzucony: <konkretny powód>.

## Konsekwencje

<!--
Uczciwie w obie strony. ADR z samymi zaletami jest reklamą, nie decyzją,
i czytelnik przestaje mu ufać.
-->

**Pozytywne**
- <co staje się łatwiejsze>

**Negatywne**
- <co oddajemy, co staje się trudniejsze, jaki dług zaciągamy>

**Neutralne**
- <skutki uboczne bez znaku>

## Wpływ na bazę wiedzy

<!--
Co ta decyzja zmienia w innych dokumentach. Uzupełnij w tym samym commicie,
inaczej decyzja pozostanie widoczna wyłącznie tutaj (antywzorzec A5).
-->

- [ ] `CONTEXT.md` — nowe pojęcia: <…>
- [ ] Kontrakt L2 `<ścieżka>` — aktualizacja + nowe `verified`
- [ ] ADR-y zastąpione: <…> → `status: superseded`, `superseded_by`

## Notatki

<!-- Opcjonalne. Zastrzeżenia, co świadomie pominięto, do czego wrócić. -->
