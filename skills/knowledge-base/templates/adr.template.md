---
id: adr-<NNNN>-<english-slug>   # bdr-<NNNN>-... dla BDR
status: Proposed       # Proposed | Accepted. Agent pisze Proposed; Accepted ustawia CZŁOWIEK
                       # po przeglądzie. Nie ma osobnej sekcji "## Status" w treści.
type: decision
scope: <np. backend/telemetry>
last_reviewed: <YYYY-MM-DD>
---

<!--
ADR zapisuje WYBÓR: co rozważaliśmy, co wybraliśmy, czym za to płacimy.

Piszesz ADR, gdy spełnione są TRZY warunki naraz:
  1. nieodwracalne — zmiana zdania później kosztuje realnie,
  2. nieoczywiste — czytelnik za rok zapyta "dlaczego tak?",
  3. był realny wybór — istniała alternatywa, którą odrzuciliście z powodu.
Brak któregokolwiek → bez ADR. ADR-y pisane "na wszelki wypadek" rozmywają
rejestr i sprawiają, że nikt go nie czyta.

Nazwa pliku i lokalizacja: rozstrzyga reguła `architecture-decisions` — nie zgaduj
z tego szablonu, przeczytaj regułę. Konwencja: `docs/technical/adr/NNNN-slug.md`
(ADR) i `docs/business/bdr/NNNN-slug.md` (BDR), numeracja niezależna w każdym
katalogu i nigdy nie użyta ponownie, patrz [ARCHITECTURE.md](../ARCHITECTURE.md).

Ten plik dodaje do tej konwencji wyłącznie **front-matter** wymagany przez bazę
wiedzy oraz polskie nagłówki sekcji. Kryteria „czy to w ogóle zasługuje na ADR"
są w skillu `domain-modeling`; procedurę zapisu ma komenda `/adr`.

Limit: 80 linii miękko, 150 twardo. Dłuższy ADR to zwykle dwie decyzje.

Tytuł w trybie oznajmującym: "Telemetria jest normalizowana do tabeli
measurements", nie "Wybór modelu przechowywania telemetrii".
-->

# <Tytuł — decyzja w formie zdania oznajmującego>

<!-- Jeden akapit streszczenia: co postanowiono i co zostaje otwarte.
     Dla czytelnika, który nie przeczyta reszty. -->

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

- <co ułatwia>
- <co oddajemy, co staje się trudniejsze, jaki dług zaciągamy>

## Notatki

<!--
Opcjonalne. Zastrzeżenia, co świadomie pominięto, do czego wrócić.
"Powiązane:" z linkami. "Zastępuje ADR-<NNNN>" w nowym ADR oraz "Zastąpiony
przez ADR-<NNNN>" w starym (jego `status` zostaje Accepted).

Skutki w innych dokumentach uzupełnij w tym samym commicie, inaczej decyzja
pozostanie widoczna wyłącznie tutaj (antywzorzec A5): `CONTEXT.md` (nowe
pojęcia), kontrakty L2 (aktualizacja + nowe `last_reviewed`).
-->
