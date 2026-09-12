---
id: ryzyka
title: Rejestr ryzyk — <nazwa produktu>
layer: L1
domain: product
status: active
confidence: decision
owner: <imię>
created: <YYYY-MM-DD>
verified: <YYYY-MM-DD>
review_after: <YYYY-MM-DD>   # kwartalnie
related: [product]
---

<!--
Jeden dokument na całe repo, nie osobny plik na ryzyko. Wartość rejestru
leży w możliwości przejrzenia wszystkiego naraz.

Rejestr działa tylko wtedy, gdy każde ryzyko ma WŁAŚCICIELA i WYZWALACZ.
Ryzyko bez wyzwalacza to lista zmartwień: nikt nie wie, kiedy zareagować,
więc nikt nie reaguje aż do momentu, w którym jest za późno.

Wyzwalacz to obserwowalne zdarzenie ("trzeci klient z rzędu pyta o sterowanie",
"koszt SIM przekracza X"), nie odczucie ("gdy zrobi się groźnie").
-->

# Rejestr ryzyk

**Ostatni przegląd:** <YYYY-MM-DD> · **Następny:** <YYYY-MM-DD>

## Skala

| Prawdopodobieństwo | Wpływ |
|---|---|
| **W** — wysokie, spodziewamy się w bieżącym etapie | **K** — krytyczny, zatrzymuje projekt |
| **Ś** — średnie, prawdopodobne w ciągu roku | **P** — poważny, wymusza zmianę planu |
| **N** — niskie, możliwe ale mało prawdopodobne | **U** — umiarkowany, kosztuje czas i pieniądze |

## Ryzyka aktywne

<!-- Sortuj po wadze: K przed P, W przed Ś. Ryzyko zamknięte przenieś na dół. -->

### R-<NN> · <Nazwa ryzyka>

| | |
|---|---|
| **Kategoria** | techniczne / biznesowe / regulacyjne / operacyjne / zależność zewnętrzna |
| **Prawdopodobieństwo × wpływ** | <W/Ś/N> × <K/P/U> |
| **Właściciel** | <imię> |
| **Status** | otwarte / mitygowane / zaakceptowane / zamknięte |

**Na czym polega:** <opis — co konkretnie może się stać i jaki będzie skutek>

**Wyzwalacz:** <obserwowalne zdarzenie, po którym uruchamiamy reakcję>

**Mitygacja:** <co robimy TERAZ, żeby zmniejszyć prawdopodobieństwo lub wpływ>

**Plan awaryjny:** <co robimy, GDY się zmaterializuje>

**Powiązania:** [ADR-<NNNN>](<ścieżka>) · [<dowód L4>](<ścieżka>)

---

## Ryzyka zaakceptowane

<!--
Ryzyka, które świadomie przyjmujecie bez mitygacji. To jest decyzja, nie
zaniedbanie — i dlatego musi być zapisana. Bez tej sekcji przy materializacji
ryzyka nie da się odtworzyć, czy ktokolwiek je w ogóle widział.
-->

| # | Ryzyko | Dlaczego akceptujemy | Kto zaakceptował | Data |
|---|---|---|---|---|
| R-<NN> | <nazwa> | <powód> | <imię> | <YYYY-MM-DD> |

## Ryzyka zamknięte

| # | Ryzyko | Jak się zakończyło | Data |
|---|---|---|---|
| R-<NN> | <nazwa> | zmaterializowało się / przestało dotyczyć / zmitygowane | <YYYY-MM-DD> |

<!-- Nie kasuj zamkniętych. "Przestało dotyczyć" bywa przedwczesne
     i ryzyko wraca — wtedy historia oszczędza powtórnej analizy. -->
