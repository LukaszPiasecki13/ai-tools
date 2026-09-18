---
id: adr-<NNNN>-<krotki-slug>
status: draft          # metadane KB, dla walidatora - patrz METADATA.md. `draft` = dokument
                        # jeszcze piszesz; `current` = gotowy do czytania. NIE to samo, co
                        # sekcja "## Status" niżej (ta ma własne, ustalone w repo słownictwo
                        # decyzji: Proposed/Accepted/... i zmienia się bez dotykania tego pola)
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

Nazwa pliku i lokalizacja: rozstrzyga reguła `architecture-decisions` z TEGO
repo — nie zgaduj z tego szablonu, przeczytaj regułę. Domyślna konwencja to
`docs/adr/NNNN-short-title.md` z numeracją wspólną dla całego repo, ale reguła
może przewidywać podział wg domeny (np. `docs/business/adr/` +
`docs/technical/adr/`, każdy z własną, niezależną numeracją) — oba warianty są
prawidłowe, patrz [ARCHITECTURE.md](../ARCHITECTURE.md). Numer nigdy nie jest
użyty ponownie, niezależnie od wybranego układu.

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

## Status

<!--
Wartości i słowa ustala reguła `architecture-decisions` tego repo (domyślnie:
Proposed | Accepted | Deprecated | Superseded by ADR-NNNN) — to jest INNE
słownictwo niż front-matterowe `status:` wyżej, celowo: to pole czyta człowiek
i wpisuje w nim wynik przeglądu, tamto czyta walidator.

Nowy ADR zaczyna od najsłabszego stanu (Proposed / draft). Przejście na
Accepted / active wpisuje CZŁOWIEK po przeglądzie — agent nigdy nie zmienia
tego pola samodzielnie, choćby decyzja wyglądała na oczywistą.
-->

Proposed

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
- [ ] Kontrakt L2 `<ścieżka>` — aktualizacja + nowe `last_reviewed`
- [ ] ADR-y zastąpione: <…> → w ich treści dopisz „Zastąpione przez ADR-<NNNN>"
      i zaktualizuj ich `## Status` na `Superseded by ADR-<NNNN>`

## Notatki

<!-- Opcjonalne. Zastrzeżenia, co świadomie pominięto, do czego wrócić. -->
