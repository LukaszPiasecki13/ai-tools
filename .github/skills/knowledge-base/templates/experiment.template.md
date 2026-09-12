---
id: exp-<slug>
title: <Hipoteza w formie zdania sprawdzalnego>
layer: L3          # po zakończeniu i zapisaniu wyniku → L4
domain: product
status: draft      # draft → active (trwa) → archived (rozstrzygnięty)
confidence: hypothesis
owner: <imię>
created: <YYYY-MM-DD>
verified: <YYYY-MM-DD>
expires: <YYYY-MM-DD>   # termin rozstrzygnięcia — nie "kiedyś"
related: [product, <id-segmentu>]
---

<!--
Eksperyment produktowy: sprawdzenie założenia, na którym stoi produkt,
zanim zbudujecie na nim kwartał pracy.

W startupie najdroższe błędy nie są techniczne. Są to poprawnie zbudowane
rzeczy, których nikt nie potrzebował. Ten dokument istnieje po to, żeby
założenia były zapisane ZANIM zostaną potwierdzone przez sam fakt, że coś
zbudowaliście.

Reguła bezwzględna: KRYTERIUM ROZSTRZYGNIĘCIA JEST ZAPISANE PRZED STARTEM.
Kryterium ustalane po zobaczeniu wyników zawsze zostanie spełnione.

Cykl życia: draft → active (L3) → archived + wynik przeniesiony do L4
jako research-note. Sam eksperyment nigdy nie staje się normą — normą staje
się ADR podjęty na jego podstawie.
-->

# <Hipoteza>

## 1. Hipoteza

> **Wierzymy, że** <kto> **osiągnie** <jaki efekt> **dzięki** <co>.
> **Będziemy wiedzieć, że to prawda, gdy** <obserwowalny sygnał>.

**Dlaczego to ma znaczenie:** <co zależy od odpowiedzi — jaka decyzja, jaki zakres prac>

**Koszt pomyłki:** <ile stracimy, budując na fałszywym założeniu>

## 2. Kryterium rozstrzygnięcia

<!--
Wypełnione PRZED startem. Trzy progi, bo dwa wymuszają binarny wynik tam,
gdzie rzeczywistość jest ciągła.
-->

| Wynik | Próg | Co robimy |
|---|---|---|
| **Potwierdzone** | <konkretna wartość> | <następny krok> |
| **Nierozstrzygnięte** | <przedział> | <co doprecyzować i powtórzyć> |
| **Obalone** | <konkretna wartość> | <co zmieniamy — zakres, segment, produkt> |

## 3. Metoda

| | |
|---|---|
| **Co robimy** | <najtańsza rzecz dająca sygnał> |
| **Próba** | <ile, kto, jak dobrani> |
| **Czas trwania** | <od–do> |
| **Koszt** | <czas / pieniądze> |

**Największe zagrożenie dla wiarygodności:** <np. dobór próby, efekt uprzejmości, zbyt mała liczebność>

## 4. Wynik

<!-- Wypełniane po zakończeniu. -->

| | |
|---|---|
| **Data zakończenia** | <YYYY-MM-DD> |
| **Zmierzona wartość** | <liczba / obserwacja> |
| **Rozstrzygnięcie** | potwierdzone / nierozstrzygnięte / obalone |

**Co zobaczyliśmy:**

**Czego się nie spodziewaliśmy:**
<!-- Najczęściej najcenniejsza część eksperymentu. -->

**Zastrzeżenia do wyniku:**
<!-- Uczciwie. Wynik z ukrytym zastrzeżeniem jest gorszy niż brak wyniku. -->

## 5. Decyzja

| | |
|---|---|
| **Postanowiliśmy** | <co> |
| **ADR** | [ADR-<NNNN>](<ścieżka>) albo „brak — decyzja odwracalna" |
| **Dowód przeniesiony do L4** | `docs/research/<plik>.md` |
| **Zmiany w kanonie** | <co zaktualizowano w PRODUCT.md / CONTEXT.md> |
