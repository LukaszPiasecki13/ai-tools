---
id: contract-<nazwa>
title: Kontrakt <nazwa> — <REST API | format wiadomości | schemat zdarzeń>
layer: L2
domain: <backend|firmware|frontend>
status: active
confidence: fact
owner: <imię>
created: <YYYY-MM-DD>
verified: <YYYY-MM-DD>
review_after: on-change
applies_to:
  - <ścieżka/producenta/**>
  - <ścieżka/konsumenta/**>
sources:
  - <ścieżka/do/schematu.py>
related: [<id-komponentu>, <id-adr>]
---

<!--
Kontrakt to obietnica między dwiema stronami, które zmieniają się niezależnie:
backend ↔ frontend, urządzenie ↔ serwer, usługa ↔ usługa.

Różnica wobec dokumentu komponentu: komponent opisuje JEDNĄ stronę, kontrakt
opisuje UMOWĘ. Dlatego `applies_to` obejmuje kod OBU stron — zmiana po jednej
stronie musi unieważnić weryfikację dokumentu.

Najważniejsze sekcje to wersjonowanie i kompatybilność. Reszta jest zwykle
odtwarzalna ze schematu; te dwie nie są, a to one decydują, czy urządzenie
w terenie przestanie działać po deployu.
-->

# Kontrakt: <nazwa>

| | |
|---|---|
| **Wersja** | `<v2>` |
| **Strona nadająca** | <kto> · `<ścieżka>` |
| **Strona odbierająca** | <kto> · `<ścieżka>` |
| **Transport** | <HTTP POST /… \| MQTT topic \| kolejka> |
| **Uwierzytelnienie** | <mechanizm> → [<dokument>](<ścieżka>) |

## 1. Struktura

<!-- Przykład rzeczywisty, nie wymyślony. Najlepiej skopiowany z testu
     albo z logu — wtedy jest sprawdzalny. -->

```json
{
  "<pole>": "<wartość>"
}
```

| Pole | Typ | Wymagane | Znaczenie | Walidacja |
|---|---|---|---|---|
| `<pole>` | `<typ>` | tak/nie | <znaczenie> | <zakres, format, długość> |

## 2. Wersjonowanie i kompatybilność

<!--
Sekcja, której brak kosztuje najwięcej — szczególnie gdy drugą stroną jest
urządzenie w terenie, którego nie da się zaktualizować w tym samym momencie
co serwera.
-->

| | |
|---|---|
| **Sposób wersjonowania** | <pole w payloadzie / ścieżka URL / nagłówek> |
| **Wersje obsługiwane** | <lista> |
| **Data wyłączenia starej wersji** | <data lub warunek> |

**Zmiana kompatybilna wstecz** (bez podbicia wersji):
- dodanie pola opcjonalnego
- rozszerzenie zakresu wartości pola opcjonalnego

**Zmiana niekompatybilna** (wymaga nowej wersji i okresu przejściowego):
- usunięcie pola, zmiana typu, zmiana znaczenia
- zaostrzenie walidacji istniejącego pola
- zmiana jednostki albo skali wartości

<!-- Zmiana jednostki jest klasyczną pułapką: schemat się zgadza, walidacja
     przechodzi, a dane są błędne o trzy rzędy wielkości. -->

## 3. Błędy

| Kod / status | Znaczenie | Reakcja strony odbierającej |
|---|---|---|
| `<kod>` | <kiedy> | <ponów / odrzuć / zbuforuj> |

**Idempotentność:** <czy powtórzone wysłanie tego samego jest bezpieczne i na czym oparta jest deduplikacja>

**Polityka ponowień:** <ile prób, jaki backoff, kiedy rezygnacja>

## 4. Niezmienniki kontraktu

| Niezmiennik | Skutek złamania |
|---|---|
| <np. znacznik czasu zawsze UTC w ISO-8601> | <co się dzieje, gdy nie> |

## 5. Wzajemne zależności

<!-- Co zależy od czego. Np. "wiadomość diagnostyczna musi poprzedzać pierwszą
     pomiarową po restarcie" — wiedza, której nie widać w żadnym schemacie. -->

## 6. Weryfikacja

| Co | Gdzie |
|---|---|
| Test kontraktowy | `<ścieżka>` |
| Schemat / model | `<ścieżka>` |
| Przykład rzeczywisty | `<ścieżka do fixture albo logu>` |
